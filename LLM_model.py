import os
import time
import json
import warnings # เพิ่มไลบรารีสำหรับจัดการข้อความเตือน
import pandas as pd 
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core import exceptions
from pandas.tseries.offsets import BDay

# ==========================================
# 0. จัดการข้อความเตือน (ปิด FutureWarning ของ GenAI)
# ==========================================
warnings.filterwarnings("ignore", category=FutureWarning)

# ==========================================
# 1. ตั้งค่าพื้นฐานและ API Key
# ==========================================
load_dotenv()
API_KEY = os.getenv("CO1_GEMINI_API") 
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash-lite')
SYMBOLS = ['MSFT']
# SYMBOLS = ["INTC", "MSFT", "NVDA","ORCL"] 
USERTYPE = "personal"
SYMBOL_SLEEP = 72 # พักหลังจบ 1 symbol = 1.00 นาที

def selected_path(symbol, user_type, task):
    read_merged = f"data_merged/merged_{symbol}.csv"
    write_result = f"data_merged/{symbol}_gemini_results.csv"
    
    if task == "read_final": return read_merged
    elif task == "write_result": return write_result

# ==========================================
# 2. ฟังก์ชันส่งข้อมูลให้ Gemini คิดวิเคราะห์
# ==========================================
def ask_gemini_to_predict(row_data):
    # 🎯 แก้ไข Error: int64 is not JSON serializable โดยการแปลง Type (Cast) ให้เป็นของ Python โดยตรง
    context = {
        "Date": str(row_data['Date']),
        "Open": float(row_data['Open']),
        "Close": float(row_data['Close']),
        "Volume": int(row_data['Volume']),           # <--- แก้ไขตรงนี้
        "News_Count": int(row_data['news_count']),   # <--- แก้ไขตรงนี้
        "Net_Sentiment_Score": float(round(row_data['positive_score'] - row_data['negative_score'], 4)) # <--- แก้ไขตรงนี้
    }
    
    context_json = json.dumps(context)
    
    prompt = f"""
    You are an expert quantitative analyst.
    Analyze this daily stock and news sentiment data: {context_json}
    
    Task: Predict the stock's price movement for the NEXT TRADING DAY.
    
    You MUST respond strictly with a valid JSON object in the exact format below. Do not include markdown tags like ```json.
    {{
        "prediction": "up", 
        "confidence": "High", 
        "reasoning": "Explain your logic in 1-2 short sentences based on the sentiment score, news count, and stock data."
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        raw_text = response.text.replace("```json", "").replace("```", "").strip()
        result_dict = json.loads(raw_text)
        result_dict['prediction'] = result_dict['prediction'].lower()
        return result_dict
        
    except exceptions.ResourceExhausted as e:
        raise e
        
    except Exception as e:
        print(f"  [Error] API หรือ JSON มีปัญหา: {e}")
        return {"prediction": "error", "confidence": "none", "reasoning": f"API failed: {e}"}

# ==========================================
# 3. ฟังก์ชันหลักสำหรับดึงข้อมูลมาวนลูปทำนาย
# ==========================================
def start_prediction(symbol):
    print(f"\n{'='*50}\n 🤖 เริ่มต้นให้ Gemini ทำนายทิศทางหุ้น: {symbol} \n{'='*50}")
    
    path = selected_path(symbol, USERTYPE, "read_final")
    df = pd.read_csv(path)
    
    # ดึงข้อมูลมาทดสอบจำนวน 10 วันล่าสุด
    test_df = df.tail(5).copy()
    print(f"ดึงข้อมูลมาทดสอบจำนวน {len(test_df)} วัน\n")
    
    predictions = []
    confidences = []
    reasonings = []
    
    i = 0
    while i < len(test_df):
        row = test_df.iloc[i]
        print(f"[{i+1}/{len(test_df)}] กำลังวิเคราะห์ข้อมูลวันที่ {row['Date']}...", end=" ")
        
        try:
            result = ask_gemini_to_predict(row)
            
            predictions.append(result['prediction'])
            confidences.append(result['confidence'])
            reasonings.append(result['reasoning'])
            
            print(f"👉 ทายว่า: {result['prediction'].upper()} (มั่นใจ: {result['confidence']})")
            
            i += 1
            time.sleep(4)
            
        except exceptions.ResourceExhausted:
            print(f"\n⚠️ ติดลิมิต API (Rate Limit Hit)! ระบบจะหยุดรอ 60 วินาที...")
            time.sleep(72)
            print("🔄 ครบกำหนดพัก 1 นาที กำลังพยายามทำนายแถวเดิมอีกครั้ง...")
            
    test_df['gemini_prediction'] = predictions
    test_df['gemini_confidence'] = confidences
    test_df['gemini_reasoning'] = reasonings
    
    save_path = selected_path(symbol, USERTYPE, "write_result")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    test_df.to_csv(save_path, index=False, encoding='utf-8')
    print(f"\n✅ เสร็จสิ้น! บันทึกผลลัพธ์การทำนายไว้ที่: {save_path}")

# ==========================================
# 2. ฟังก์ชันส่งข้อมูลให้ Gemini ทายพรุ่งนี้ (T+1)
# ==========================================
def predict_tomorrow(row_data):
    context = {
        "Date": str(row_data['Date']),
        "Open": float(row_data['Open']),
        "Close": float(row_data['Close']),
        "Volume": int(row_data['Volume']),
        "News_Count": int(row_data['news_count']),
        "Net_Sentiment_Score": float(round(row_data['positive_score'] - row_data['negative_score'], 4))
    }
    
    context_json = json.dumps(context)
    prompt = f"""
    You are an expert quantitative analyst.
    Analyze this daily stock and news sentiment data from today: {context_json}
    
    Task: Predict the stock's price movement for the NEXT TRADING DAY.
    
    You MUST respond strictly with a valid JSON object in the exact format below. Do not include markdown tags like ```json.
    {{
        "prediction": "up", 
        "confidence": "High", 
        "reasoning": "Explain your logic in 1-2 short sentences based on the sentiment score, news count, and stock data."
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        raw_text = response.text.replace("```json", "").replace("```", "").strip()
        result_dict = json.loads(raw_text)
        return result_dict
    except Exception as e:
        return {"prediction": "error", "confidence": "none", "reasoning": f"API Error: {e}"}

# ==========================================
# 3. โค้ดหลัก: อัปเดตรายวัน (Daily Update)
# ==========================================
def run_daily_update(symbol):
    print(f"\n{'='*60}")
    print(f" 🚀 อัปเดตคำทำนายรายวัน (Daily Prediction): {symbol}")
    print(f"{'='*60}")
    
    merged_path = selected_path(symbol, USERTYPE, "read_final")
    results_path = selected_path(symbol, USERTYPE, "write_result")
    
    try:
        df_merged = pd.read_csv(merged_path)
        latest_row = df_merged.iloc[-1]
        latest_date = latest_row['Date']
        
        # 🌟 จุดที่เพิ่ม: คำนวณวันทำการถัดไป (T+1)
        # BDay(1) จะช่วยข้ามวันเสาร์-อาทิตย์ให้โดยอัตโนมัติ
        target_date = (pd.to_datetime(latest_date) + BDay(1)).strftime('%Y-%m-%d')
        
        if os.path.exists(results_path):
            df_results = pd.read_csv(results_path)
        else:
            df_results = pd.DataFrame()

        # เช็คว่าวันนี้เคยทายไปหรือยัง
        if not df_results.empty and latest_date in df_results['Date'].values:
            print(f"\n⚠️ ข้อมูลวันที่ {latest_date} มีในระบบแล้ว! (ไม่ต้องทายซ้ำ)")
            return 
            
        print(f"\n🔮 กำลังวิเคราะห์ข้อมูลสิ้นสุดวันที่: {latest_date}")
        print(f"🎯 เป้าหมายการทำนาย (Target Date): {target_date}") # แสดงวันที่ T+1 บนหน้าจอ
        
        result = ask_gemini_to_predict(latest_row)
        
        if result['prediction'] != 'error':
            pred_color = "🟢 UP" if result['prediction'].lower() == 'up' else "🔴 DOWN" if result['prediction'].lower() == 'down' else "⚪ STABLE"
            print(f"   👉 ผลทำนายของวันที่ {target_date} คือ: {pred_color}") # บอกวันที่ในอนาคตชัดเจน
            print(f"   🧠 เหตุผล: {result['reasoning']}\n")
            
            # บันทึกข้อมูล
            new_row_df = pd.DataFrame([latest_row])
            new_row_df['gemini_prediction'] = result['prediction'].lower()
            new_row_df['gemini_confidence'] = result['confidence']
            new_row_df['gemini_reasoning'] = result['reasoning']
            
            df_updated = pd.concat([df_results, new_row_df], ignore_index=True)
            df_updated.to_csv(results_path, index=False, encoding='utf-8')
            print(f"✅ บันทึกคำทำนาย T+1 ลงใน {results_path} สำเร็จ!")            
    except Exception as e:
        print(f"❌ ระบบขัดข้องสำหรับ {symbol}: {e}")

if __name__ == "__main__":
    for symbol in SYMBOLS:
        start_prediction(symbol)
        if symbol != SYMBOLS[-1]:
            print(f"⏳ สลับหุ้น: รอ {SYMBOL_SLEEP} วินาทีเพื่อป้องกัน Rate Limit รวม...")
            time.sleep(SYMBOL_SLEEP)

if __name__ == "__main__":
    for symbol in SYMBOLS:
        run_daily_update(symbol)

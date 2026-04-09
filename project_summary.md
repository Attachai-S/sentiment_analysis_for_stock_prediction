# Project Summary: Sentiment Analysis and Stock Trend Prediction using FinBERT and LLM Agent

## 1. Project Overview (ภาพรวมโครงงาน)
โครงงานนี้มุ่งเน้นการพัฒนาระบบทำนายแนวโน้มราคาหุ้น โดยการแปลงข้อมูลเชิงคุณภาพ (พาดหัวข่าวและเนื้อหาข่าว) ให้เป็นข้อมูลเชิงปริมาณ (คะแนนความรู้สึก) ด้วยเทคโนโลยี Natural Language Processing (NLP) ขั้นสูง จากนั้นนำข้อมูลที่ได้ไปบูรณาการร่วมกับข้อมูลราคาหุ้นในอดีต (Historical OHLCV) และใช้ Large Language Model (LLM) ทำหน้าที่เป็น "นักวิเคราะห์เชิงปริมาณ (Quant Analyst)" เพื่อประเมินและทำนายทิศทางของราคาหุ้น (Prediction: Up, Down, Static) 

## 2. Business Problem & Significance (ปัญหาและความสำคัญ)
* **ปัญหา (The Problem):** ตลาดหุ้นผันผวนสูงและขับเคลื่อนด้วยอารมณ์ตลาด (Market Sentiment) ในยุคที่ข้อมูลข่าวสารล้นหลาม นักลงทุนไม่สามารถวิเคราะห์ข่าวทั้งหมดได้ทัน ทำให้ตัดสินใจล่าช้าและมักมีอคติส่วนตัว (Emotional Bias)
* **กลุ่มเป้าหมาย (Target Audience):** นักลงทุนรายย่อย, นักวิเคราะห์เชิงปริมาณ (Quants), และผู้จัดการกองทุน
* **ความสำคัญ (Significance):** โครงงานนี้ช่วยลดอคติในการลงทุน ประหยัดเวลาในการวิเคราะห์ข่าวสาร และสามารถสร้างดัชนีชี้วัดใหม่ (Net Sentiment Score) ที่ช่วยในการตัดสินใจเชิงกลยุทธ์ได้อย่างเป็นระบบ

## 3. Core Concepts (แนวคิดหลัก)
* **Domain-Specific Sentiment Analysis:** ใช้โมเดล NLP ที่ปรับจูนมาสำหรับภาษาทางการเงินโดยเฉพาะ (FinBERT) เพื่อความแม่นยำในการตีความคำศัพท์เฉพาะทาง
* **LLM as a Predictive Agent:** แทนที่จะใช้โมเดล Machine Learning ดั้งเดิม โครงงานนี้ใช้ Google Gemini API ในการอ่านตารางข้อมูล (Data Serialization) เพื่อใช้ตรรกะและเหตุผลประกอบการทำนายทิศทางหุ้น

## 4. Tech Stack (เครื่องมือและเทคโนโลยี)
* **Programming Language:** Python
* **Data Processing:** Pandas, Regular Expressions (Regex)
* **Data Acquisition (APIs):** Finnhub API (สำหรับดึงข่าวและราคาหุ้นรายวัน), python-dotenv (จัดการ API Keys)
* **NLP Framework:** HuggingFace Transformers, PyTorch
* **AI Models:** * `ProsusAI/finbert` (วิเคราะห์ Sentiment)
  * `Google Gemini API` (LLM สำหรับทำนายผลลัพธ์)

## 5. System Architecture & Pipeline (ขั้นตอนการทำงานของระบบ)
ระบบถูกออกแบบเป็น End-to-End Pipeline แบ่งออกเป็น 5 เฟสหลัก ดังนี้:

### Phase 1: Data Collection (การรวบรวมข้อมูลดิบ)
* ดึงข้อมูลพาดหัวข่าว (Headline) และเนื้อหาข่าว (Summary) ของหุ้น 6 ตัว (AAPL, CSCO, INTC, MSFT, NVDA, ORCL) ย้อนหลังตั้งแต่ 1 มกราคม 2025 ผ่าน Finnhub API
* ดึงข้อมูลราคาหุ้นรายวัน (Stock Candles - Resolution 'D') ในช่วงเวลาเดียวกัน

### Phase 2: Data Preprocessing (การทำความสะอาดและเตรียมข้อมูล)
* จัดการ Missing Values (Null)
* ใช้ Regex ลบ Noise เช่น URLs, HTML Tags
* **Encoding Correction:** แก้ปัญหาอักขระประหลาด (Mojibake / Smart Quotes) ที่ติดมาจาก API ต้นทาง โดยแปลงอักขระและบังคับใช้ `encoding='utf-8'` ทั้งระบบ จนได้ข้อความภาษาอังกฤษที่สมบูรณ์ 100%
* นำ Headline และ Summary มารวมกันเป็นคอลัมน์ `model_text`

### Phase 3: Sentiment Scoring (การให้คะแนนความรู้สึก)
* ป้อนข้อความ `model_text` เข้าสู่โมเดล **FinBERT**
* สกัดผลลัพธ์ออกมาเป็นความน่าจะเป็น 3 อารมณ์: `positive_score`, `negative_score`, `neutral_score` และจัดทำป้ายกำกับ (`sentiment_label`)

### Phase 4: Data Merging & Feature Engineering (การประกอบร่างข้อมูล)
* แปลง Timestamp ของข่าวให้เป็น Date Format
* ทำการ Aggregate ข้อมูลโดยหา "ค่าเฉลี่ยคะแนน Sentiment รายวัน"
* สร้าง Feature ใหม่คือ **`net_sentiment`** (positive_score - negative_score)
* ทำ Left Join รวมข้อมูลตารางคะแนนข่าวเข้ากับตารางราคาหุ้น (OHLCV) โดยใช้ `Date` เป็นแกนหลัก ได้ผลลัพธ์เป็น Final ML-Ready Dataset

### Phase 5: LLM Prediction (การทำนายทิศทางหุ้น) *[Current Target]*
* **Data Serialization:** แปลงข้อมูลตารางในแต่ละแถว (Row) ให้เป็นรูปแบบ JSON
* **Prompt Engineering:** ส่ง JSON พร้อมคำสั่ง (System Prompt) ไปยัง **Google Gemini API** เพื่อสวมบทบาทเป็น Quant Analyst
* **Output:** บังคับให้ Gemini คืนค่าคำทำนายทิศทางราคาหุ้นล่วงหน้าเพียง 3 สถานะ คือ **"Up"**, **"Down"**, หรือ **"Static"**

## 6. Current Progress (สถานะปัจจุบัน)
* **Completed:** เฟสที่ 1 ถึงเฟสที่ 4 เสร็จสมบูรณ์ ข้อมูลทั้งหมดถูกทำความสะอาด วิเคราะห์ Sentiment และประกอบร่างเป็น Final Dataset เรียบร้อยแล้ว (PoC Data Pipeline ทำงานได้ 100%)
* **Next Steps:** ดำเนินการในเฟสที่ 5 คือการนำ Final Dataset ไปเชื่อมต่อกับ Google Gemini API เพื่อวัดผลความแม่นยำในการทำนายแนวโน้มตลาดต่อไป
import flet as ft
from backend import *

selected_symbol = None

def main(page: ft.Page):
    
    # def on_stock_click(e, symbol):
    #     print(f"You Click: {symbol}")

    async def go_check(e, symbol):
        global selected_symbol
        selected_symbol = symbol
        await page.push_route("/check")

    def route_change():
        page.views.clear()
        symbols = get_symbols()
        buttons = []
        for sym in symbols:
            buttons.append(
                ft.ElevatedButton(
                    sym,
                    on_click=lambda e, s=sym: page.run_task(go_check, e, s)
                )
            )
        #===== search ui =====

        async def submit_symbol(e):
            global selected_symbol

            symbol = input_field.value.strip().upper()

            if not symbol:
                status_msg.value = "Please enter a symbol"
                page.update()
                return

            status_msg.value = "Checking..."
            page.update()

            if not is_valid_symbol(symbol):
                status_msg.value = "Invalid symbol"
                page.update()
                return

            status_msg.value = "Valid"
            selected_symbol = symbol
            page.update()

            await page.push_route("/check")

        input_field = ft.TextField(
                label="Enter stock symbol (e.g. TSLA)",
                width=300
            )
        status_msg = ft.Text("", color=ft.Colors.RED)
        #===== search ui =====
        page.views.append(
            ft.View(
                route="/",
                controls=[
                    ft.SafeArea(
                        content=ft.Column(
                            controls=[
                                ft.Text("AI Stock Predictor", size=36, weight=ft.FontWeight.BOLD),
                                ft.Text("Select a Stock", size=24),
                                ft.Text(""),
                                ft.Container(content=ft.Row(
                                    controls=buttons,
                                    wrap=True,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=10,
                                    run_spacing=10,
                                ),alignment=ft.Alignment.CENTER, padding=20),
                                ft.Text(""),
                                ft.Text("Or Enter Your Stock Symbol", size=24),
                                # ft.Row([])
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Row(
                                                [
                                                    input_field,
                                                    ft.ElevatedButton(
                                                        "Submit",
                                                        on_click=lambda e: page.run_task(submit_symbol, e)
                                                    )
                                                ],
                                                alignment=ft.MainAxisAlignment.CENTER
                                            ),
                                            status_msg
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                    ),
                                    padding=10
                                )
                            ]
                            ,horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ,expand=True
                        )
                    )
                ],
            )
        )
        if page.route == "/check":
            status_text = ft.Text("Checking...", size=24, color=ft.Colors.YELLOW)
            continue_btn = ft.ElevatedButton(
                    "Continue",
                    disabled=True,
                    bgcolor=ft.Colors.GREY,
                    on_click=lambda e: page.go("/results")
                )
            async def check_and_update(e):
                # 🔹 Checking
                status_text.value = "Checking..."
                status_text.color = ft.Colors.YELLOW
                page.update()
                up_to_date = is_data_up_to_date(selected_symbol)
                async def run_pipeline_async(symbol):
                    import asyncio
                    loop = asyncio.get_running_loop()
                    await loop.run_in_executor(None, run_full_pipeline, symbol)
                    
                    status_text.value = "Ready"
                    status_text.color = ft.Colors.GREEN

                    continue_btn.disabled = False
                    continue_btn.bgcolor = ft.Colors.GREEN

                    page.update()

                # 🔹 If not updated → run pipeline
                if not up_to_date:
                    status_text.value = "Updating..."
                    status_text.color = ft.Colors.ORANGE
                    page.update()
                    try:
                        page.run_task(run_pipeline_async, selected_symbol)
                        # await page.run_task(run_pipeline_async, selected_symbol)
                
                    except Exception as err:
                        status_text.value = f"Error: {err}"
                        status_text.color = ft.Colors.RED
                        page.update()
                        return
                else:
                    status_text.value = "Ready"
                    continue_btn.disabled = False

            page.views.append(
            ft.View(
                route="/check",
                controls=[
                    ft.SafeArea(
                        content=ft.Column(
                            controls=[
                                ft.AppBar(
                                    title=ft.Text(f"Checking: {selected_symbol}"),
                                    leading=ft.IconButton(
                                        icon=ft.Icons.ARROW_BACK,
                                        on_click=lambda e: page.run_task(lambda: page.push_route("/"))
                                    )
                                ),

                                status_text,

                                ft.ElevatedButton(
                                    "Start Checking",
                                    # on_click=lambda e: page.run_task(check_and_update(e))
                                    on_click=lambda e: page.run_task(check_and_update, e)
                                ),

                                continue_btn
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            expand=True
                        )
                    )
                ]
            )
        )
        if page.route == "/results":

            df = load_prediction(selected_symbol)

            if df is None or df.empty:
                page.views.append(
                    ft.View(
                        route="/results",
                        controls=[ft.Text("No data available")]
                    )
                )
                return

            # ===== default row =====
            selected_row = df.iloc[0]

            prediction_text = ft.Text(size=30, weight="bold")
            confidence_text = ft.Text(size=14)
            reasoning_text = ft.Text(size=14)

            # ===== update function =====
            def update_view(row):
                pred = row["gemini_prediction"].upper()

                # 🎯 ใส่ emoji ให้ดูโปร
                if pred == "UP":
                    pred_display = "📈 UP"
                    color = ft.Colors.GREEN
                elif pred == "DOWN":
                    pred_display = "📉 DOWN"
                    color = ft.Colors.RED
                else:
                    pred_display = "➖ STABLE"
                    color = ft.Colors.GREY

                prediction_text.value = f"Prediction (Next Day): {pred_display}"
                prediction_text.color = color

                confidence_text.value = f"Confidence: {row['gemini_confidence']}"
                reasoning_text.value = row["gemini_reasoning"]

                page.update()

            # ===== สร้าง list วันที่ =====
            date_list = []
            for _, row in df.iterrows():
                date_list.append(
                    ft.TextButton(
                        row["Date"],
                        on_click=lambda e, r=row: update_view(r)
                    )
                )

            # set default
            update_view(selected_row)

            page.views.append(
                ft.View(
                    route="/results",
                    controls=[
                        ft.SafeArea(
                            content=ft.Column(
                                controls=[
                                    # 🔹 TOP BAR
                                    ft.Row(
                                        [
                                            ft.TextButton("BACK", on_click=lambda e: page.go("/")),
                                            ft.Text(selected_symbol, size=20, weight="bold")
                                        ]
                                    ),

                                    # 🔹 BODY
                                    ft.Row(
                                        controls=[
                                            # ===== LEFT =====
                                            ft.Container(
                                                content=ft.Column(
                                                    date_list,
                                                    scroll="auto"
                                                ),
                                                width=200,
                                                border=ft.border.all(1),
                                                padding=10
                                            ),

                                            # ===== RIGHT =====
                                            ft.Container(
                                                content=ft.Column(
                                                    [
                                                        prediction_text,
                                                        confidence_text,
                                                        reasoning_text
                                                    ],
                                                    spacing=15
                                                ),
                                                expand=True,
                                                padding=20,
                                                border=ft.border.all(1)
                                            )
                                        ],
                                        expand=True
                                    )
                                ],
                                expand=True
                            )
                        )
                    ]
                )
            )
        page.update()
    async def view_pop(e):
        if e.view is not None:
            print("View pop:", e.view)
            page.views.remove(e.view)
            top_view = page.views[-1]
            await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    route_change()

if __name__ == "__main__":
    ft.run(main)
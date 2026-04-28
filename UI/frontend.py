import flet as ft
from backend import curr_route, get_existing_stocks, app_state, get_paths, check_all_files, run_pipline_step
def main(page: ft.Page):

    async def go_third_page(e):
        await page.push_route("/third")

    existing_symbols = get_existing_stocks()
    stock_buttons = ft.Row(wrap=True, spacing=10, alignment=ft.MainAxisAlignment.CENTER)
    
    async def on_stock_click(e, symbol):
        app_state.selected_symbol = symbol
        await page.push_route("/check")

    if not existing_symbols:
        stock_buttons.controls.append(ft.Text("No stocks found. Please add news files in the news_dataset folder."))
    else:
        for sym in existing_symbols:
            stock_buttons.controls.append(
                ft.Container(
                    content = ft.Row(
                        [ft.Text(sym, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)],
                        alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor=ft.Colors.GREEN_700,
                    padding=20,
                    border_radius=10,
                    on_click=lambda e, s=sym: on_stock_click(s),
                    ink=True,
                    width=100,
                )
            )

    def route_change():
        curr_route(page)
        page.views.clear()
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
                                stock_buttons,
                                ft.Divider(height=40),
                                ft.TextField(label="Or enter a stock symbol:", width=300),
                                ft.ElevatedButton("create new stock", on_click=lambda e: print("Create new stock clicked")),
                            ],horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        )
                    )
                ],
            )
        )
        if page.route == "/check":
            symbol = app_state.selected_symbol
            status = check_all_files(symbol)

            status_column = ft.Column()

            steps = [
                ("news", "News Data"),
                ("stock", "Stock Data"),
                ("processed", "Text Processing"),
                ("sentiment", "Sentiment Scoring"),
                ("merged", "Data Merging"),
                ("llm", "LLM Prediction"),
            ]

            async def run_all_pipeline():
                for key, label in steps:
                    if not status[key]:
                        status_text.value = f"{label} - Preparing..."
                        status_text.color = ft.Colors.ORANGE
                        page.update()

                        run_pipline_step(symbol, key)

                        status[key] = True
                        status_text.value = f"{label} - Done"
                        status_text.color = ft.Colors.GREEN
                        page.update()

                continue_btn.disabled = False
                continue_btn.bgcolor = ft.Colors.GREEN
                page.update()

            for key, label in steps:
                color = ft.Colors.GREEN if status[key] else ft.Colors.ORANGE
                text = "Ready" if status[key] else "Preparing"

                status_text = ft.Text(f"{label}: {text}", color=color)
                status_column.controls.append(status_text)

            continue_btn = ft.ElevatedButton(
                "Continue",
                disabled=True,
                bgcolor=ft.Colors.RED,
                on_click=go_third_page
            )

            page.views.append(
                ft.View(
                    route="/check",
                    controls=[
                        ft.SafeArea(
                            content=ft.Column(
                                controls=[
                                    ft.AppBar(
                                        title=ft.Text(f"Checking: {symbol}"),
                                        leading=ft.IconButton(
                                            icon=ft.Icons.ARROW_BACK,
                                            on_click=lambda e: page.push_route("/")
                                        )
                                    ),
                                    status_column,
                                    ft.ElevatedButton("Run Pipeline", on_click=lambda e: page.run_task(run_all_pipeline)),
                                    continue_btn
                                ]
                            )
                        )
                    ]
                )
            )
        if page.route == "/third":
            page.views.append(
                ft.View(
                    route="/third",
                    controls=[
                        ft.SafeArea(
                            content=ft.Column(
                                controls=[
                                    ft.AppBar(title=ft.Text("Third Page")),
                                    ft.Text("This is the third page!"),
                                ]
                            )
                        )
                    ],
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
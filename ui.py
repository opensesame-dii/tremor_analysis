import flet as ft

def main(page: ft.Page):
    
    page.title = "tremor_analysis"

    page.window_width = 700  # 幅
    page.window_height = ""  # 高さ
    page.window_top = ""  # 位置(TOP)
    page.window_left = ""  # 位置(LEFT)
    page.window_always_on_top = True  # ウィンドウを最前面に固定

    select_file_button = ft.Row([ft.OutlinedButton(text = "フォルダを選択", on_click=""), ft.Container(content = (ft.Text("ディレクトリ名")))])
    scan_button = ft.OutlinedButton(text = "Scan", on_click= "")
    run_button = ft.OutlinedButton(text = "Run", on_click="")
    open_result_button = ft.OutlinedButton(text = "Open Result", on_click="")
    apply_button = ft.OutlinedButton(text = "Apply&Save Settings", on_click="")
    settings = ft.Container(content = ft.Column([
        ft.Row([ft.Text("Row start"), ft.TextField(height = 40,width=50)]),
        ft.Row([ft.Text("Column start"), ft.TextField(height = 40,width=50)]),
        ft.Row([ft.Text("Sensors num"), ft.TextField(height = 40,width=50)]),
        ft.Row([ft.Text("Encoding"), ft.TextField(height = 40, width=100)]),
        ft.Row([ft.Text("Sampling rate"), ft.TextField(height = 40,width=50), ft.Text("Hz")]),
        apply_button
        ]), padding = 25)
    log_outputs = ft.Container(content = (ft.Column([
        ft.Text("Log Outputs"), 
        ft.Container(content = ft.Text("ファイル一覧とか"), border = ft.border.all(1, "black"), height=400, width=300 )])
        ),width="", height="" )
    
    page.add(select_file_button,
            ft.Row([ft.Container(content = (ft.Column([
            settings,
            scan_button,
            run_button,
            open_result_button])
            ), margin = 10,width = 300),
            log_outputs])
    )

    #page.update()

ft.app(target = main)
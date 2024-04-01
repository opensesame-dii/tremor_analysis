import flet as ft
import os
import csv
import subprocess
import platform
from typing import List, Union, Tuple

class MainApp:
    def __init__(self):
        self.target_dir = ft.Text(value = "Not Selected")
        self.log_content = ft.Text()


    #ファイル選択
    def on_folder_picked(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.target_dir.value = e.path
            self.page.update()



    def show_pick_folder(self, _: ft.ControlEvent):
        self.folder_picker.get_directory_path()


    # ディレクトリのscan
    def scan(self,  _:ft.ControlEvent):
        if self.target_dir.value != "Not Selected":
            file_list = []
            self.file_num = 0
            self.pairs_num = 0

            # 再帰的にディレクトリを探索←最大３階層まで
            def recursive_search(directory, depth):
                if depth > 3:
                    return
                csv_files = [f for f in os.listdir(directory) if f.endswith('.csv') and not f.endswith('.tremor.csv')]
                self.file_num += len(csv_files)
                if len(csv_files) == 2:
                    file_list.append(tuple(os.path.join(directory, file) for file in csv_files))
                    self.pairs_num += 1

                elif len(csv_files) == 1:
                    file_list.append((os.path.join(directory, csv_files[0]),))
                else:
                    for item in os.listdir(directory):
                        path = os.path.join(directory, item)
                        if os.path.isdir(path):
                            recursive_search(path, depth + 1)

            recursive_search(self.target_dir.value, 0)

            # log_outputsの中身更新←スクロールバーつけたい
            self.log_content.value  = f"{self.file_num}files\n{self.pairs_num}pairs\nanalysis files\n{file_list}"

        else: # Not Selected なら
            self.log_content.value  = "No folder is selected"

        self.page.update()

    # runボタン
    def run(self, _):
        data = ["result", "num"]
        if self.target_dir:
            self.output_file = os.path.join(self.target_dir.value, "result.tremor.csv")
            with open(self.output_file, "w") as file:
                writer = csv.writer(file)
                writer.writerows(data)
            print("file created")

    # open_result ボタン
    def open_result(self, _):
        if platform.system() == "Windows": # Windows
            subprocess.Popen(["explorer", self.target_dir.value], shell = True)
        elif platform.system() == "Darwin": # Mac
            subprocess.Popen(["open", self.target_dir.value])
        else: # Linux
            subprocess.Popen(["xdg-open", self.target_dir.value])
        return

    def build_ui(self):
        self.folder_picker = ft.FilePicker(on_result = self.on_folder_picked)
        self.page.overlay.append(self.folder_picker)
        select_folder_button = ft.Row([ft.OutlinedButton(text = "Select Folder", on_click= self.show_pick_folder), self.target_dir])
        scan_button = ft.OutlinedButton(text = "Scan", on_click= self.scan)
        run_button = ft.OutlinedButton(text = "Run", on_click=self.run)
        open_result_button = ft.OutlinedButton(text = "Open Result", on_click=self.open_result)
        apply_button = ft.OutlinedButton(text = "Apply&Save Settings", on_click="")
        settings = ft.Container(content = ft.Column([
            ft.Row([ft.Text("Row start"), ft.TextField(height = 40,width=50)]),
            ft.Row([ft.Text("Column start"), ft.TextField(height = 40,width=50)]),
            ft.Row([ft.Text("Sensors num"), ft.TextField(height = 40,width=50)]),
            ft.Row([ft.Text("Encoding"), ft.TextField(height = 40, width=100)]),
            ft.Row([ft.Text("Sampling rate"), ft.TextField(height = 40,width=50), ft.Text("Hz")]),
            ft.Row([ft.Text("max frequency"), ft.TextField(height = 40,width=50), ft.Text("Hz")]),
            ft.Row([ft.Text("min frequency"), ft.TextField(height = 40,width=50), ft.Text("Hz")]),
            apply_button
            ]), padding = 25)
        log_outputs = ft.Container(content = (ft.Column([
            ft.Text("Log Outputs"),
            ft.Container(content = self.log_content, border = ft.border.all(1, "black"), height=500, width=300 )], scroll = ft.ScrollMode.ALWAYS)
            ),width="", height="" )

        self.page.add(select_folder_button,
                ft.Row([ft.Container(content = (ft.Column([
                settings,
                scan_button,
                run_button,
                open_result_button])
                ), margin = 10,width = 300),
                log_outputs])
        )
        return

    def main(self, page: ft.Page):
        self.page = page
        #ページ設定
        self.page.title = "tremor_analysis"
        self.page.window_width = 700  # 幅
        self.page.window_height = ""  # 高さ
        self.page.window_top = ""  # 位置(TOP)
        self.page.window_left = ""  # 位置(LEFT)
        self.page.window_always_on_top = True  # ウィンドウを最前面に固定

        self.build_ui()
        self.page.update()

if __name__ == "__main__":
    app = MainApp()
    ft.app(target = app.main)
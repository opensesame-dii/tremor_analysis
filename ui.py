import flet as ft
import os
import csv
import subprocess
from typing import List, Union, Tuple

def main(page: ft.Page):
    #ページ設定
    page.title = "tremor_analysis"

    page.window_width = 700  # 幅
    page.window_height = ""  # 高さ
    page.window_top = ""  # 位置(TOP)
    page.window_left = ""  # 位置(LEFT)
    page.window_always_on_top = True  # ウィンドウを最前面に固定

 
    class Main_func:
        def __init__(self):
            self.target_dir = ft.Ref[ft.Text]()
            self.target_dir_path = None
            #self.analysis_dir_list = []
            self.total_file_num = 0
            self.pairs_num = 0
            self.output_log_content = ""
            self.folder_picker = ft.FilePicker(on_result= self.on_folder_picked)
            page.overlay.append(self.folder_picker)
    
        #ファイル選択
        def on_folder_picked(self, e: ft.FilePickerResultEvent):
            if e.path:
                self.target_dir.current.value = e.path
                self.target_dir_path = self.target_dir.current.value
                page.update()
                print("target_dir_path:",self.target_dir_path)
            
        def show_pick_folder(self, _: ft.ControlEvent):
            self.folder_picker.get_directory_path()
            page.update()

    # ui_rows = []
    # ui_rows.append(ft.Row(controls=[
    #     ft.ElevatedButton("Select Folder", on_click=show_pick_folder),
    #     ft.Text(ref=target_folder)
    # ]))
    #select_folder_button = ft.Row([ft.OutlinedButton(text = "Select Folder", on_click= show_pick_folder), ft.Container(content = ft.Text(ref = target_dir))])

        # ディレクトリのscan
        def scan(self, _:ft.ControlEvent):
            if self.target_dir_path:
                file_list = []
                self.total_file_num = 0
                self.pairs_num = 0

                # 再帰的にディレクトリを探索←最大３階層まで
                def recursive_search(directory, depth):
                    if depth > 3:
                        return 
                    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv') and not f.endswith('.tremor.csv')]
                    self.total_file_num += len(csv_files)
                    if len(csv_files) == 2:
                        file_list.append(tuple(os.path.join(directory, file) for file in csv_files))
                        self.pairs_num += 1
                        print("ペア数",self.pairs_num)
                    elif len(csv_files) == 1:
                        file_list.append((os.path.join(directory, csv_files[0]),))
                    else:
                        for item in os.listdir(directory):
                            path = os.path.join(directory, item)
                            if os.path.isdir(path):
                                recursive_search(path, depth + 1)
                

                recursive_search(self.target_dir_path, 0)
                print("ファイルリスト", file_list)
            
                # 再帰的にディレクトリを探索
                # def recursive_search(directory):
                #     # if depth > 3:  # 最大3階層まで探索
                #     #     return 
                #     for item in os.listdir(directory):
                #         path = os.path.join(directory, item)
                #         if os.path.isdir(path):
                #             recursive_search(path)
                #         elif item.endswith('.csv') and not item.endswith('.tremor.csv'):
                #             file_list.append(path)
                   
                # self.analysis_dir_list = []
                # #max_depth = 0
            
                # '''
                # # 階層の深さを調べる
                # def calculate_depth(directory, depth):
                #     nonlocal max_depth
                #     if depth > max_depth:
                #         max_depth = depth

                #     if depth < 3:
                #         for item in os.listdir(directory):
                #             path = os.path.join(directory, item)
                #             if os.path.isdir(path):
                #                 calculate_depth(path, depth + 1)

                # #calculate_depth(target_dir_path, 0)
                # '''
                # recursive_search(self.target_dir_path)
                # print("ファイルリスト",file_list,"ここまで")

                # # .csvファイルが1つまたは2つあるディレクトリを選択
                # for file in file_list:
                #     parent_dir = os.path.dirname(file)
                #     csv_files = [f for f in os.listdir(parent_dir) if f.endswith('.csv') and not f.endswith('.tremor.csv')]
                    
                #     # if 1 <= len(csv_files) <= 2:
                #     #     self.analysis_dir_list.append(parent_dir)
                #     if 1 <= len(csv_files) <= 2:
                #         if len(csv_files) == 1:
                #             self.analysis_dir_list.append((file))
                #         elif len(csv_files) == 2:
                #             self.analysis_dir_list.append((os.path.join(parent_dir,os.path.basename(file)), os.path.join(parent_dir,os.path.basename(file))))
                
                # def count_file(l):
                
                #     if isinstance(l, tuple):
                #         for v in l:
                #             self.count += count_file(v)
                #             print("ファイル数", self.count)
                #         return self.count
                #     else:
                #         return 1
                # self.file_num = count_file(file_list)
                
                self.output_log_content = f"{self.total_file_num}files\n{self.pairs_num}pairs\nanalysis files\n{file_list}"
                #print("analysis_dir:",self.analysis_dir_list)
                print("file_num:",self.total_file_num)
                log_outputs.content = ft.Column([
                    ft.Text("Log Outputs"), 
                    ft.Container(content = ft.Text(self.output_log_content), border = ft.border.all(1, "black"), height=400, width=300 )], scroll = ft.ScrollMode.AUTO)
                    
                page.update()

                return  #pair_num #, max_depth
            else:
                print("None")

        # 引数で与えられた文字列を追記する関数
        # def log_output(self, file_num, pairs_num, analysis_dir_list):
        #     self.output_log_content = f"{self.file_num}files\n{self.file_num}pairs\nanalysis files\n{self.analysis_dir_list}"
        #     log_outputs.content = ft.Column([
        #             ft.Text("Log Outputs"), 
        #             ft.Container(content = ft.Text(self.output_log_content), border = ft.border.all(1, "black"), height=400, width=300 )])
        #     return
        
        def run(self, _):
            data = ["result", "num"]
            if self.target_dir_path:
                self.output_file = os.path.join(self.target_dir_path, "result.tremor.csv")
                with open(self.output_file, "w") as file:
                    writer = csv.writer(file)
                    writer.writerows(data)
                print("file created")
        
        def open_result(self, _):
            subprocess.Popen(["explorer", self.target_dir_path], shell = True)
            print("open")
            return

            
            
    

    m = Main_func()
    select_folder_button = ft.Row([ft.OutlinedButton(text = "Select Folder", on_click= m.show_pick_folder), ft.Container(content = (ft.Text(ref=m.target_dir, value = "Not Selected")))])
    scan_button = ft.OutlinedButton(text = "Scan", on_click= m.scan)
    run_button = ft.OutlinedButton(text = "Run", on_click=m.run)
    open_result_button = ft.OutlinedButton(text = "Open Result", on_click=m.open_result)
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
        ft.Container(content = ft.Text(m.output_log_content), border = ft.border.all(1, "black"), height=400, width=300 )], scroll = ft.ScrollMode.ALWAYS)
        ),width="", height="" )
    
    page.add(select_folder_button,
            ft.Row([ft.Container(content = (ft.Column([
            settings,
            scan_button,
            run_button,
            open_result_button])
            ), margin = 10,width = 300),
            log_outputs])
    )
    # ui_controls = ft.Column(controls=ui_rows)
    # page.add(ui_controls)

    #page.update()

ft.app(target = main)
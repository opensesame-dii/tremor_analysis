from cgitb import text
import csv
from logging import root, warning
import os
from io import BytesIO
from re import S
# from shutil import rmtree
import matplotlib.pyplot as plt
from copy import deepcopy
from copy import copy
from sys import exit
from argparse import ArgumentParser
from typing import Any

import datetime

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import flet as ft
from flet import ControlEvent

# from PIL import Image, ImageTk
import numpy as np
from scipy.signal import hamming, detrend, morlet2, cwt, spectrogram, get_window, butter, sosfilt
from matplotlib import use
use('TkAgg')
from matplotlib.mlab import cohere, window_hanning
from matplotlib.pyplot import specgram as pltspectrogram
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import backend_tools as cbook
# import PySimpleGUI as sg
import pandas as pd
from sklearn.decomposition import PCA

class MainApp:
    def __init__(self) -> None:
        self.analysis_methods = [
            Spectrogram_analize(),  # ここで解析手法のクラスをインスタンス化
            # 他の解析手法もここに追加
        ]

    def run(self):
        # ここでscan()も呼ぶべきかも(20240225ミーティングより)
        data = ["result", "num"]
        if self.target_dir:
            self.output_file = os.path.join(self.target_dir.value, "result.tremor.csv")
            with open(self.output_file, "w") as file:
                writer = csv.writer(file)
                writer.writerows(data)
            print("file created")
        for method in self.analysis_methods:
            method.run()  # 全ての解析手法が，runメソッドを持っていることを前提とする

    def on_run_click(self, e: ControlEvent):
        """Buttonのon_clickでは, 引数にControlEventが渡されるが，run()では不要のため, この関数でwrapしている

        Args:
            e (ControlEvent): click event
        """
        self.run()

    def setting_field(self):
        for setting in self.analysis_methods:
            setting.build_result_ui()

    # select folder
    def on_folder_picked(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.target_dir.value = e.path
            self.page.update()
        self.folder_picker = ft.FilePicker(on_result = self.on_folder_picked)

    def show_pick_folder(self, _: ft.ControlEvent):
        self.folder_picker.get_directory_path()


class Spectrogram_analize:
    def __init__(self) :
        self.data = 3
        #self.frame_range = None

    def run(self, data_i) -> dict[str, Any]:
        self.val = 1 + self.data
        self.answer = {"答え": self.val}
        print(self.answer)
        return self.answer
        

    def build_result_ui(self):
        self.text_area = ft.Text("設定項目")
        self.val_area = ft.TextField(hint_text="int")
        return self.text_area, self.val_area

        # Main_appでのrunでこれも呼ぶ？？

    def update_ui(self):
        # 横並びで一塊にして配置したい　https://qiita.com/donraq/items/1ac45ddfe0a803a94e27
        # ここでつくる=>Main_appにUI関係のmake_picみたいなやつを作って並べる
        print("test")

if __name__ == "__main__":
    app = MainApp()
    ft.app(target=app.main)

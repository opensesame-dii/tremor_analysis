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
import yaml


class MainApp:
    def __init__(self) -> None:
        self.analysis_methods = [
            Spectrogram_analize(),  # ここで解析手法のクラスをインスタンス化
            # 他の解析手法もここに追加
        ]

    def run(self):
        # ここでscan()も呼ぶべきかも(20240225ミーティングより)
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
            setting.build_result_ui

    def read_config_file(self, e: ControlEvent):
        with open("config.yaml") as file:
            self.config = yaml.safe_load(file)
        print(self.config)

    def write_config_file(self, e: ControlEvent):
        self.config ["key1"] = "change"
        self.config["add_key"] = "add"
        with open("config.yaml", "w") as file :
            yaml.dump(self.config, file)
        print(self.config)


    def main(self, page: ft.Page):
        run_button = ft.OutlinedButton(text="run", on_click=self.on_run_click)
        read_button = ft.OutlinedButton(text = "read", on_click=self.read_config_file)
        write_button = ft.OutlinedButton(text = "write", on_click=self.write_config_file)
        y = ft.Container(content=ft.Column([run_button, read_button, write_button]))
        page.add(y)
        page.update()


class Spectrogram_analize:
    def __init__(self) :
        self.data = 3

        #self.frame_range = None

    def run(self,) -> dict[str, Any]:
        self.val = 1 + self.data
        self.answer = {"answer": self.val}


    def build_result_ui(self):
        self.text_area = ft.Text("設定項目")
        self.val_area = ft.TextField(hint_text="int")
        x = ft.Container(ft.Row(self.text_area,self.val_area))
        return x

        # Main_appでのrunでこれも呼ぶ？？

    def update_ui(self):
        # 横並びで一塊にして配置したい　https://qiita.com/donraq/items/1ac45ddfe0a803a94e27
        # ここでつくる=>Main_appにUI関係のmake_picみたいなやつを作って並べる
        print("test")



if __name__ == "__main__":
    app = MainApp()
    ft.app(target=app.main)

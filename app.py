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
        for method in self.analysis_methods:
            method.run()  # 全ての解析手法が，runメソッドを持っていることを前提とする

    def on_run_click(self, e: ControlEvent):
        """Buttonのon_clickでは, 引数にControlEventが渡されるが，run()では不要のため, この関数でwrapしている

        Args:
            e (ControlEvent): click event
        """
        self.run()

    def main(self, page: ft.Page):
        t = ft.FilledTonalButton(text="run", on_click=self.on_run_click)
        page.controls.append(t)
        page.update()


class Spectrogram_analize:
    def __init__(self) :
        self.result = None  # 最初はNoneにしておく
        self.python = 54

    def run(self):
        self.result = 123  # ここで結果を格納

    def add(self,x):
        x = 1
        print(x)


if __name__ == "__main__":
    app = MainApp()
    ft.app(target=app.main)

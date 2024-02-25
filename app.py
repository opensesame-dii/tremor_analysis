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
    def main(page: ft.Page):
        t = ft.FilledTonalButton(text="run", on_click="ここどうしたらいいかよくわかんないです")
        page.controls.append(t)
        page.update()    
    ft.app(target=main)
    


class Spectrogram_analize:
    def __init__(self) :
        self.python = 54
    
    def add(self,x):
        x = 1
        print(x)
    
    
   


        





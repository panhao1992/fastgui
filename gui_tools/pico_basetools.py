# -*- coding;utf-8 -*-
"""
File name : pico_basetools.PY
Create file time: 2023/1/3 18:47
File Create By Author : Admin
"""
import json
import os.path
import subprocess
import time
import tkinter
from tinui.TinUI import TinUI
from gui_tools.general_module import *
from gui_tools.item_tkintergui import *
from gui_tools.general_module import go_platform
import numpy as np
from collections import Counter
import pyperclip


def picobasetools_framepage(picobasetools_frame):

    devicebaseframe = ttk.Frame(picobasetools_frame, padding=(10, 10))
    devicebaseframe.pack(fill='x', pady=5, side=TOP)
    ttk.Label(devicebaseframe, text='设备选择').grid(row=0, column=0, padx=10)
    chosecomlist = tkinter.ttk.Combobox(devicebaseframe, state='readonly', width=45)
    chosecomlist.grid(row=0, column=1, columnspan=3, padx=20)

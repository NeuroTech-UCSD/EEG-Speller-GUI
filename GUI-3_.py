##############################################################################
# Notes and Bugs
# 1. There is sort of this lag and idk how to fix it with the highlight going back to the first section
# 2. Maybe make the first section last a little longer due to reaction time
###############################################################################
# Imports
###############################################################################

# Matplotlib + FuncAnimation
import warnings
import math
import random
import pygame  # For sound play
import os
import pickle
from tkinter import ttk
import tkinter as tk
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib

# Text-generation
import sys
import tensorflow as tf

textgen_path = os.path.join(os.getcwd(), "text generation")
sys.path.append(textgen_path)
from textgen import get_one_step_model

# Need to set the backend to enable tkinter functionality with matplotlib
matplotlib.use("TkAgg")

# Tkinter

# Data model save and loading,

# Misc

# Timing and timers
# import time
# from datetime import datetime # For creating timer from a counter

# Suppress warnings
warnings.filterwarnings('ignore')

# Fonts
BOLD_FONT = ("Verdana", 12, 'bold')

# Global variable
TEXT = []


###############################################################################
# Classes for frames
###############################################################################
class FrameContainer(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "EEG Speller GUI Demo")
        tk.Tk.minsize(self, 800, 800)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        frame = StartPage(container, self)
        frame.grid(row=0, column=0, sticky='nsew')
        self.frames[StartPage] = frame

        self.current_frame = None

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        frame.show()
        self.current_frame = frame

    def on_closing(self):
        self.destroy()


class TextFrameContainer(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "EEG Speller Text Demo")
        tk.Tk.minsize(self, 800, 800)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        frame = TextPage(container, self)
        frame.grid(row=0, column=0, sticky='nsew')
        self.frames[TextPage] = frame

        self.current_frame = None

        self.show_frame(TextPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        frame.show()
        self.current_frame = frame

    def on_closing(self):
        self.destroy()


class StartPage(tk.Frame):

    def __init__(self, parent, controller, session=None):
        tk.Frame.__init__(self, parent)
        self.label = tk.Label(self, text="CircleSpell", font=BOLD_FONT)
        self.label.pack()

        self.session = session
        self.controller = controller

        # Create time
        self.time = 0
        self.time2 = 0

        # Create canvas
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill=tk.BOTH, expand=1)

        # Initialize misc constants
        self.BIG_RADIUS = 250
        self.MID_RADIUS = 150
        self.SMALL_RADIUS = 50
        self.LEFT_MI = 0
        self.RIGHT_MI = 1
        self.JAW_EMG = 2
        self.DEFAULT_COLOR = "#FFFFFF"  # white
        self.DEFAULT_TEXT_COLOR = "black"
        self.HIGHLIGHTED_COLOR = "#87CEEB"  # blue
        self.NUM_CIRCLE_SECTIONS = 4
        self.NUM_ARC_SECTIONS = 3
        self.NUM_CHAR = 5
        self.SPACE = 'spc'

        # Initialize layers
        self.FIRST_LAYER = 0  # first layer = 3 circles
        self.SECOND_LAYER = 1  # second layer = 1 circle + sectors
        self.THIRD_LAYER = 2  # third layer = column char selection
        self.curr_layer = self.FIRST_LAYER
        self.curr_section = 0  # 0 is top right, 1 is bot right, 2 is bot left, 3 is top left
        self.curr_arc = 1  # big arc = 0, mid = 1, small = 2
        self.curr_letter = 0  # 0 is left letter, 1 is mid, 2 is right
        self.curr_chart = 0  # 0 is first chart, 1 is second chart
        self.curr_character = 0  # index of character string

        # Initialize the chars for each circle
        self.BIG_CIRCLE_CHAR_L1 = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
                                   "K", "M", "N", "O", "P", "Q", "R", "S", "T", "U"]  # make predictions

        self.MID_CIRCLE_CHAR_L1 = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
                                   "K", "M", "N", "O", "P", "Q", "R", "S", "T", "U"]

        self.SMALL_CIRCLE_CHAR_L1 = []
        self.BIG_CIRCLE_CHAR_L2 = ["0", "1", "N", "O", "P", "Q", "R", "S", "T", "U",
                                   "A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]  # make predictions
        self.MID_CIRCLE_CHAR_L2 = ["0", "1", "N", "O", "P", "Q", "R", "S", "T", "U",
                                   "A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
        self.SMALL_CIRCLE_CHAR_L2 = []  # will be worked on in the future

        self.CHAR_OFFSET = 80

        # labels = [left circle label, mid, right]
        self.LABELS = ["choose quarter", "choose section", "choose words"]
        self.LABEL_OFFSET = 50

        # Initialize coordinates of circles
        self.BIG_CIRCLE = {"x": 400, "y": 375}
        self.MID_CIRCLE = {"x": 400, "y": 375}
        self.SMALL_CIRCLE = {"x": 400, "y": 375}

        # Initialize circle colors
        self.big_arc_color = self.DEFAULT_COLOR
        self.mid_arc_color = self.HIGHLIGHTED_COLOR
        self.small_arc_color = self.DEFAULT_COLOR

        # Initialize arc colors
        self.topleft_arc_color = self.DEFAULT_COLOR
        self.topright_arc_color = self.HIGHLIGHTED_COLOR
        self.botright_arc_color = self.DEFAULT_COLOR
        self.botleft_arc_color = self.DEFAULT_COLOR

        # Initialize letter colors
        self.first_letter_color = self.HIGHLIGHTED_COLOR
        self.second_letter_color = self.DEFAULT_TEXT_COLOR
        self.third_letter_color = self.DEFAULT_TEXT_COLOR
        self.forth_letter_color = self.DEFAULT_TEXT_COLOR
        self.fifth_letter_color = self.DEFAULT_TEXT_COLOR

        # Initialize circle and chars list
        self.CHARS_LIST_L1 = [self.BIG_CIRCLE_CHAR_L1,
                              self.MID_CIRCLE_CHAR_L1, self.SMALL_CIRCLE_CHAR_L1]
        self.CHARS_LIST_L2 = [self.BIG_CIRCLE_CHAR_L2,
                              self.MID_CIRCLE_CHAR_L2, self.SMALL_CIRCLE_CHAR_L2]
        self.CHARS_LIST = [self.CHARS_LIST_L1, self.CHARS_LIST_L2]
        self.CIRCLES_LIST = [self.BIG_CIRCLE,
                             self.MID_CIRCLE, self.SMALL_CIRCLE]
        self.RADIUS_LIST = [self.BIG_RADIUS, self.MID_RADIUS, self.SMALL_RADIUS]

        # initialize textgen model
        self.one_step_model = get_one_step_model()
        self.states = None
        self.next_char = []
        self.next_chars = []

        left_button = ttk.Button(
            self, text="Left", command=lambda: self.send_command(self.LEFT_MI))
        left_button.pack()
        right_button = ttk.Button(
            self, text="Right", command=lambda: self.send_command(self.RIGHT_MI))
        right_button.pack()
        jaw_button = ttk.Button(
            self, text="Jaw", command=lambda: self.send_command(self.JAW_EMG))
        jaw_button.pack()

    def show(self):
        # Begin the update loop
        self.label.after(100, self.update)
        self.canvas.after(100, self.render)

    def render(self):
        self.canvas.delete('all')

        if self.curr_layer == self.FIRST_LAYER:
            self.draw_first_layer()
        elif self.curr_layer == self.SECOND_LAYER:
            self.draw_second_layer()
        elif self.curr_layer == self.THIRD_LAYER:
            self.draw_third_layer()

        self.canvas.after(100, self.render)

    def draw_first_layer(self):
        x = self.BIG_CIRCLE["x"]
        y = self.BIG_CIRCLE["y"]
        self.canvas.create_oval(x - self.BIG_RADIUS, y - self.BIG_RADIUS,
                                x + self.BIG_RADIUS, y + self.BIG_RADIUS, fill=self.DEFAULT_COLOR)
        # topright
        self.canvas.create_arc(x - self.BIG_RADIUS, y - self.BIG_RADIUS,
                               x + self.BIG_RADIUS, y + self.BIG_RADIUS, start=0, extent=90,
                               fill=self.topright_arc_color)
        self.canvas.create_arc(x - self.MID_RADIUS, y - self.MID_RADIUS,
                               x + self.MID_RADIUS, y + self.MID_RADIUS, start=0, extent=90,
                               fill=self.topright_arc_color)
        self.canvas.create_arc(x - self.SMALL_RADIUS, y - self.SMALL_RADIUS,
                               x + self.SMALL_RADIUS, y + self.SMALL_RADIUS, start=0, extent=90,
                               fill=self.topright_arc_color)
        # topleft
        self.canvas.create_arc(x - self.BIG_RADIUS, y - self.BIG_RADIUS,
                               x + self.BIG_RADIUS, y + self.BIG_RADIUS, start=90, extent=90,
                               fill=self.topleft_arc_color)
        self.canvas.create_arc(x - self.MID_RADIUS, y - self.MID_RADIUS,
                               x + self.MID_RADIUS, y + self.MID_RADIUS, start=90, extent=90,
                               fill=self.topleft_arc_color)
        self.canvas.create_arc(x - self.SMALL_RADIUS, y - self.SMALL_RADIUS,
                               x + self.SMALL_RADIUS, y + self.SMALL_RADIUS, start=90, extent=90,
                               fill=self.topleft_arc_color)
        # botleft
        self.canvas.create_arc(x - self.BIG_RADIUS, y - self.BIG_RADIUS,
                               x + self.BIG_RADIUS, y + self.BIG_RADIUS, start=180, extent=90,
                               fill=self.botleft_arc_color)
        self.canvas.create_arc(x - self.MID_RADIUS, y - self.MID_RADIUS,
                               x + self.MID_RADIUS, y + self.MID_RADIUS, start=180, extent=90,
                               fill=self.botleft_arc_color)
        self.canvas.create_arc(x - self.SMALL_RADIUS, y - self.SMALL_RADIUS,
                               x + self.SMALL_RADIUS, y + self.SMALL_RADIUS, start=180, extent=90,
                               fill=self.botleft_arc_color)
        # botright
        self.canvas.create_arc(x - self.BIG_RADIUS, y - self.BIG_RADIUS,
                               x + self.BIG_RADIUS, y + self.BIG_RADIUS, start=270, extent=90,
                               fill=self.botright_arc_color)
        self.canvas.create_arc(x - self.MID_RADIUS, y - self.MID_RADIUS,
                               x + self.MID_RADIUS, y + self.MID_RADIUS, start=270, extent=90,
                               fill=self.botright_arc_color)
        self.canvas.create_arc(x - self.SMALL_RADIUS, y - self.SMALL_RADIUS,
                               x + self.SMALL_RADIUS, y + self.SMALL_RADIUS, start=270, extent=90,
                               fill=self.botright_arc_color)

        # Draw letters on circles
        for i in range(len(self.CHARS_LIST[self.curr_chart])):
            # loop over the chars in each cricle
            for j in range(len(self.CHARS_LIST[self.curr_chart][i])):
                char = self.CHARS_LIST[self.curr_chart][i][j]
                self.draw_letter(
                    char, (360 / len(self.CHARS_LIST[self.curr_chart][i])) * j - self.CHAR_OFFSET,
                          self.RADIUS_LIST[i] - 50,
                    self.CIRCLES_LIST[i]["x"], self.CIRCLES_LIST[i]["y"])
        # Draw labels for circles
        self.canvas.create_text(self.CIRCLES_LIST[0]["x"], self.CIRCLES_LIST[0]["y"] - self.BIG_RADIUS -
                                self.LABEL_OFFSET, text=self.LABELS[1], fill="black", font=("Verdana", 32))

    def draw_second_layer(self):
        x = self.BIG_CIRCLE["x"]
        y = self.BIG_CIRCLE["y"]
        chosen_arc_list = None

        self.canvas.create_oval(x - self.BIG_RADIUS, y - self.BIG_RADIUS,
                                x + self.BIG_RADIUS, y + self.BIG_RADIUS, fill=self.DEFAULT_COLOR)
        self.canvas.create_oval(x - self.MID_RADIUS, y - self.MID_RADIUS,
                                x + self.MID_RADIUS, y + self.MID_RADIUS, fill=self.DEFAULT_COLOR)
        self.canvas.create_oval(x - self.SMALL_RADIUS, y - self.SMALL_RADIUS,
                                x + self.SMALL_RADIUS, y + self.SMALL_RADIUS, fill=self.DEFAULT_COLOR)
        self.canvas.create_line(x - self.BIG_RADIUS, y, x + self.BIG_RADIUS, y)
        self.canvas.create_line(x, y - self.BIG_RADIUS, x, y + self.BIG_RADIUS)

        if self.curr_section == 0:
            # topright
            self.canvas.create_arc(x - self.BIG_RADIUS, y - self.BIG_RADIUS,
                                   x + self.BIG_RADIUS, y + self.BIG_RADIUS, start=0, extent=90,
                                   fill=self.big_arc_color)
            self.canvas.create_arc(x - self.MID_RADIUS, y - self.MID_RADIUS,
                                   x + self.MID_RADIUS, y + self.MID_RADIUS, start=0, extent=90,
                                   fill=self.mid_arc_color)
            self.canvas.create_arc(x - self.SMALL_RADIUS, y - self.SMALL_RADIUS,
                                   x + self.SMALL_RADIUS, y + self.SMALL_RADIUS, start=0, extent=90,
                                   fill=self.small_arc_color)
        elif self.curr_section == 1:
            # botright
            self.canvas.create_arc(x - self.BIG_RADIUS, y - self.BIG_RADIUS,
                                   x + self.BIG_RADIUS, y + self.BIG_RADIUS, start=270, extent=90,
                                   fill=self.big_arc_color)
            self.canvas.create_arc(x - self.MID_RADIUS, y - self.MID_RADIUS,
                                   x + self.MID_RADIUS, y + self.MID_RADIUS, start=270, extent=90,
                                   fill=self.mid_arc_color)
            self.canvas.create_arc(x - self.SMALL_RADIUS, y - self.SMALL_RADIUS,
                                   x + self.SMALL_RADIUS, y + self.SMALL_RADIUS, start=270, extent=90,
                                   fill=self.small_arc_color)
        elif self.curr_section == 2:
            # botleft
            self.canvas.create_arc(x - self.BIG_RADIUS, y - self.BIG_RADIUS,
                                   x + self.BIG_RADIUS, y + self.BIG_RADIUS, start=180, extent=90,
                                   fill=self.big_arc_color)
            self.canvas.create_arc(x - self.MID_RADIUS, y - self.MID_RADIUS,
                                   x + self.MID_RADIUS, y + self.MID_RADIUS, start=180, extent=90,
                                   fill=self.mid_arc_color)
            self.canvas.create_arc(x - self.SMALL_RADIUS, y - self.SMALL_RADIUS,
                                   x + self.SMALL_RADIUS, y + self.SMALL_RADIUS, start=180, extent=90,
                                   fill=self.small_arc_color)
        else:
            # topleft
            self.canvas.create_arc(x - self.BIG_RADIUS, y - self.BIG_RADIUS,
                                   x + self.BIG_RADIUS, y + self.BIG_RADIUS, start=90, extent=90,
                                   fill=self.big_arc_color)
            self.canvas.create_arc(x - self.MID_RADIUS, y - self.MID_RADIUS,
                                   x + self.MID_RADIUS, y + self.MID_RADIUS, start=90, extent=90,
                                   fill=self.mid_arc_color)
            self.canvas.create_arc(x - self.SMALL_RADIUS, y - self.SMALL_RADIUS,
                                   x + self.SMALL_RADIUS, y + self.SMALL_RADIUS, start=90, extent=90,
                                   fill=self.small_arc_color)

        # Draw letters on circles
        for i in range(len(self.CHARS_LIST[self.curr_chart])):
            # loop over the chars in each circle
            for j in range(len(self.CHARS_LIST[self.curr_chart][i])):
                char = self.CHARS_LIST[self.curr_chart][i][j]
                self.draw_letter(
                    char, (360 / len(self.CHARS_LIST[self.curr_chart][i])) * j - self.CHAR_OFFSET,
                          self.RADIUS_LIST[i] - 50,
                    self.CIRCLES_LIST[i]["x"], self.CIRCLES_LIST[i]["y"])
        # Draw labels for circles
        self.canvas.create_text(self.CIRCLES_LIST[0]["x"], self.CIRCLES_LIST[0]["y"] - self.BIG_RADIUS -
                                self.LABEL_OFFSET, text=self.LABELS[1], fill="black", font=("Verdana", 32))

    def draw_third_layer(self):
        x = self.BIG_CIRCLE["x"]
        y = self.BIG_CIRCLE["y"]
        chosen_arc_list = None
        chosen_char_list = None
        x_position = None
        y_position = None
        current_color_letter = None

        self.canvas.create_oval(x - self.BIG_RADIUS, y - self.BIG_RADIUS,
                                x + self.BIG_RADIUS, y + self.BIG_RADIUS, fill=self.DEFAULT_COLOR)
        self.canvas.create_oval(x - self.MID_RADIUS, y - self.MID_RADIUS,
                                x + self.MID_RADIUS, y + self.MID_RADIUS, fill=self.DEFAULT_COLOR)
        self.canvas.create_oval(x - self.SMALL_RADIUS, y - self.SMALL_RADIUS,
                                x + self.SMALL_RADIUS, y + self.SMALL_RADIUS, fill=self.DEFAULT_COLOR)
        self.canvas.create_line(x - self.BIG_RADIUS, y, x + self.BIG_RADIUS, y)
        self.canvas.create_line(x, y - self.BIG_RADIUS, x, y + self.BIG_RADIUS)

        if self.curr_arc == 0:
            chosen_char_list = self.CHARS_LIST[self.curr_chart][0]
        elif self.curr_arc == 1:
            chosen_char_list = self.CHARS_LIST[self.curr_chart][1]
        else:
            chosen_char_list = self.CHARS_LIST[self.curr_chart][2]

        start = self.curr_section * 5
        stop = (self.curr_section + 1) * 5

        # Draw letters on circles
        for i in range(len(self.CHARS_LIST[self.curr_chart])):
            # loop over the chars in each cricle
            for j in range(len(self.CHARS_LIST[self.curr_chart][i])):
                char = self.CHARS_LIST[self.curr_chart][i][j]
                self.draw_letter(
                    char, (360 / len(self.CHARS_LIST[self.curr_chart][i])) * j - self.CHAR_OFFSET,
                          self.RADIUS_LIST[i] - 50,
                    self.CIRCLES_LIST[i]["x"], self.CIRCLES_LIST[i]["y"])

        # Draw highlighted letters
        for k in range(start, stop):
            if self.curr_section == 1:
                if k % 5 == 4:
                    if self.curr_arc == 0:
                        x_position = x + math.cos(math.radians(10 + 90 - 18 * 1)) * 200
                        y_position = y + math.sin(math.radians(10 + 90 - 18 * 1)) * 200
                    elif self.curr_arc == 1:
                        x_position = x + math.cos(math.radians(10 + 90 - 18 * 1)) * 100
                        y_position = y + math.sin(math.radians(10 + 90 - 18 * 1)) * 100
                    current_color_letter = self.first_letter_color
                elif k % 5 == 3:
                    if self.curr_arc == 0:
                        x_position = x + math.cos(math.radians(10 + 90 - 18 * 2)) * 200
                        y_position = y + math.sin(math.radians(10 + 90 - 18 * 2)) * 200
                    elif self.curr_arc == 1:
                        x_position = x + math.cos(math.radians(10 + 90 - 18 * 2)) * 100
                        y_position = y + math.sin(math.radians(10 + 90 - 18 * 2)) * 100
                    current_color_letter = self.second_letter_color
                elif k % 5 == 2:
                    if self.curr_arc == 0:
                        x_position = x + math.cos(math.radians(10 + 90 - 18 * 3)) * 200
                        y_position = y + math.sin(math.radians(10 + 90 - 18 * 3)) * 200
                    elif self.curr_arc == 1:
                        x_position = x + math.cos(math.radians(10 + 90 - 18 * 3)) * 100
                        y_position = y + math.sin(math.radians(10 + 90 - 18 * 3)) * 100
                    current_color_letter = self.third_letter_color
                elif k % 5 == 1:
                    if self.curr_arc == 0:
                        x_position = x + math.cos(math.radians(10 + 90 - 18 * 4)) * 200
                        y_position = y + math.sin(math.radians(10 + 90 - 18 * 4)) * 200
                    elif self.curr_arc == 1:
                        x_position = x + math.cos(math.radians(10 + 90 - 18 * 4)) * 100
                        y_position = y + math.sin(math.radians(10 + 90 - 18 * 4)) * 100
                    current_color_letter = self.forth_letter_color
                elif k % 5 == 0:
                    if self.curr_arc == 0:
                        x_position = x + math.cos(math.radians(10 + 90 - 18 * 5)) * 200
                        y_position = y + math.sin(math.radians(10 + 90 - 18 * 5)) * 200
                    elif self.curr_arc == 1:
                        x_position = x + math.cos(math.radians(10 + 90 - 18 * 5)) * 100
                        y_position = y + math.sin(math.radians(10 + 90 - 18 * 5)) * 100
                    current_color_letter = self.fifth_letter_color
            elif self.curr_section == 0:
                if k % 5 == 4:
                    if self.curr_arc == 0:
                        x_position = x + math.cos(math.radians(10 + 0 - 18 * 1)) * 200
                        y_position = y + math.sin(math.radians(10 + 0 - 18 * 1)) * 200
                    elif self.curr_arc == 1:
                        x_position = x + math.cos(math.radians(10 + 0 - 18 * 1)) * 100
                        y_position = y + math.sin(math.radians(10 + 0 - 18 * 1)) * 100
                    current_color_letter = self.first_letter_color
                elif k % 5 == 3:
                    if self.curr_arc == 0:
                        x_position = x + math.cos(math.radians(10 + 0 - 18 * 2)) * 200
                        y_position = y + math.sin(math.radians(10 + 0 - 18 * 2)) * 200
                    elif self.curr_arc == 1:
                        x_position = x + math.cos(math.radians(10 + 0 - 18 * 2)) * 100
                        y_position = y + math.sin(math.radians(10 + 0 - 18 * 2)) * 100
                    current_color_letter = self.second_letter_color
                elif k % 5 == 2:
                    if self.curr_arc == 0:
                        x_position = x + math.cos(math.radians(10 + 0 - 18 * 3)) * 200
                        y_position = y + math.sin(math.radians(10 + 0 - 18 * 3)) * 200
                    elif self.curr_arc == 1:
                        x_position = x + math.cos(math.radians(10 + 0 - 18 * 3)) * 100
                        y_position = y + math.sin(math.radians(10 + 0 - 18 * 3)) * 100
                    current_color_letter = self.third_letter_color
                elif k % 5 == 1:
                    if self.curr_arc == 0:
                        x_position = x + math.cos(math.radians(10 + 0 - 18 * 4)) * 200
                        y_position = y + math.sin(math.radians(10 + 0 - 18 * 4)) * 200
                    elif self.curr_arc == 1:
                        x_position = x + math.cos(math.radians(10 + 0 - 18 * 4)) * 100
                        y_position = y + math.sin(math.radians(10 + 0 - 18 * 4)) * 100
                    current_color_letter = self.forth_letter_color
                elif k % 5 == 0:
                    if self.curr_arc == 0:
                        x_position = x + math.cos(math.radians(10 + 0 - 18 * 5)) * 200
                        y_position = y + math.sin(math.radians(10 + 0 - 18 * 5)) * 200
                    elif self.curr_arc == 1:
                        x_position = x + math.cos(math.radians(10 + 0 - 18 * 5)) * 100
                        y_position = y + math.sin(math.radians(10 + 0 - 18 * 5)) * 100
                    current_color_letter = self.fifth_letter_color
            elif self.curr_section == 3:
                if k % 5 == 4:
                    if self.curr_arc == 0:
                        x_position = x + math.cos(math.radians(10 + 270 - 18 * 1)) * 200
                        y_position = y + math.sin(math.radians(10 + 270 - 18 * 1)) * 200
                    elif self.curr_arc == 1:
                        x_position = x + math.cos(math.radians(10 + 270 - 18 * 1)) * 100
                        y_position = y + math.sin(math.radians(10 + 270 - 18 * 1)) * 100
                    current_color_letter = self.first_letter_color
                elif k % 5 == 3:
                    if self.curr_arc == 0:
                        x_position = x + math.cos(math.radians(10 + 270 - 18 * 2)) * 200
                        y_position = y + math.sin(math.radians(10 + 270 - 18 * 2)) * 200
                    elif self.curr_arc == 1:
                        x_position = x + math.cos(math.radians(10 + 270 - 18 * 2)) * 100
                        y_position = y + math.sin(math.radians(10 + 270 - 18 * 2)) * 100
                    current_color_letter = self.second_letter_color
                elif k % 5 == 2:
                    if self.curr_arc == 0:
                        x_position = x + math.cos(math.radians(10 + 270 - 18 * 3)) * 200
                        y_position = y + math.sin(math.radians(10 + 270 - 18 * 3)) * 200
                    elif self.curr_arc == 1:
                        x_position = x + math.cos(math.radians(10 + 270 - 18 * 3)) * 100
                        y_position = y + math.sin(math.radians(10 + 270 - 18 * 3)) * 100
                    current_color_letter = self.third_letter_color
                elif k % 5 == 1:
                    if self.curr_arc == 0:
                        x_position = x + math.cos(math.radians(10 + 270 - 18 * 4)) * 200
                        y_position = y + math.sin(math.radians(10 + 270 - 18 * 4)) * 200
                    elif self.curr_arc == 1:
                        x_position = x + math.cos(math.radians(10 + 270 - 18 * 4)) * 100
                        y_position = y + math.sin(math.radians(10 + 270 - 18 * 4)) * 100
                    current_color_letter = self.forth_letter_color
                elif k % 5 == 0:
                    if self.curr_arc == 0:
                        x_position = x + math.cos(math.radians(10 + 270 - 18 * 5)) * 200
                        y_position = y + math.sin(math.radians(10 + 270 - 18 * 5)) * 200
                    elif self.curr_arc == 1:
                        x_position = x + math.cos(math.radians(10 + 270 - 18 * 5)) * 100
                        y_position = y + math.sin(math.radians(10 + 270 - 18 * 5)) * 100
                    current_color_letter = self.fifth_letter_color
            elif self.curr_section == 2:
                if k % 5 == 4:
                    if self.curr_arc == 0:
                        x_position = x + math.cos(math.radians(10 + 180 - 18 * 1)) * 200
                        y_position = y + math.sin(math.radians(10 + 180 - 18 * 1)) * 200
                    elif self.curr_arc == 1:
                        x_position = x + math.cos(math.radians(10 + 180 - 18 * 1)) * 100
                        y_position = y + math.sin(math.radians(10 + 180 - 18 * 1)) * 100
                    current_color_letter = self.first_letter_color
                elif k % 5 == 3:
                    if self.curr_arc == 0:
                        x_position = x + math.cos(math.radians(10 + 180 - 18 * 2)) * 200
                        y_position = y + math.sin(math.radians(10 + 180 - 18 * 2)) * 200
                    elif self.curr_arc == 1:
                        x_position = x + math.cos(math.radians(10 + 180 - 18 * 2)) * 100
                        y_position = y + math.sin(math.radians(10 + 180 - 18 * 2)) * 100
                    current_color_letter = self.second_letter_color
                elif k % 5 == 2:
                    if self.curr_arc == 0:
                        x_position = x + math.cos(math.radians(10 + 180 - 18 * 3)) * 200
                        y_position = y + math.sin(math.radians(10 + 180 - 18 * 3)) * 200
                    elif self.curr_arc == 1:
                        x_position = x + math.cos(math.radians(10 + 180 - 18 * 3)) * 100
                        y_position = y + math.sin(math.radians(10 + 180 - 18 * 3)) * 100
                    current_color_letter = self.third_letter_color
                elif k % 5 == 1:
                    if self.curr_arc == 0:
                        x_position = x + math.cos(math.radians(10 + 180 - 18 * 4)) * 200
                        y_position = y + math.sin(math.radians(10 + 180 - 18 * 4)) * 200
                    elif self.curr_arc == 1:
                        x_position = x + math.cos(math.radians(10 + 180 - 18 * 4)) * 100
                        y_position = y + math.sin(math.radians(10 + 180 - 18 * 4)) * 100
                    current_color_letter = self.forth_letter_color
                elif k % 5 == 0:
                    if self.curr_arc == 0:
                        x_position = x + math.cos(math.radians(10 + 180 - 18 * 5)) * 200
                        y_position = y + math.sin(math.radians(10 + 180 - 18 * 5)) * 200
                    elif self.curr_arc == 1:
                        x_position = x + math.cos(math.radians(10 + 180 - 18 * 5)) * 100
                        y_position = y + math.sin(math.radians(10 + 180 - 18 * 5)) * 100
                    current_color_letter = self.fifth_letter_color

            self.canvas.create_text(x_position, y_position, text=chosen_char_list[k],
                                    font=("Verdana", 25), fill=current_color_letter)
        # Draw labels for circles
        self.canvas.create_text(self.CIRCLES_LIST[0]["x"], self.CIRCLES_LIST[0]["y"] - self.BIG_RADIUS -
                                self.LABEL_OFFSET, text=self.LABELS[2], fill="black", font=("Verdana", 32))

    def draw_letter(self, character, angle, radius, center_x, center_y):
        x = math.cos(math.radians(angle)) * radius + center_x
        y = math.sin(math.radians(angle)) * radius + center_y
        self.canvas.create_text(x, y, text=character,
                                fill="black", font=("Verdana", 25))

    # update the quadrants based on predictions of textgen
    def update_quadrant_textgen(self):
        # arr: quadrant arr to be change
        if self.curr_chart == 0:
            self.BIG_CIRCLE_CHAR_L1[
            self.curr_section * self.NUM_CHAR: (self.curr_section + 1) * self.NUM_CHAR] = self.next_chars
            # if self.curr_section == 0:
            #     self.BIG_CIRCLE_CHAR_L1[0:self.NUM_CHAR] = self.next_chars
            # elif self.curr_section == 1:
            #     self.BIG_CIRCLE_CHAR_L1[self.NUM_CHAR:]
        elif self.curr_chart == 1:
            self.BIG_CIRCLE_CHAR_L2[
            self.curr_section * self.NUM_CHAR: (self.curr_section + 1) * self.NUM_CHAR] = self.next_chars

    # Update loop
    def update(self):
        if self.controller.current_frame == self and self.curr_layer == self.FIRST_LAYER:
            self.time += 50
            cycleTime = 4000
            timeInterval = int(cycleTime / self.NUM_CIRCLE_SECTIONS)
            self.time = self.time % cycleTime
            if self.time >= 0 and self.time < timeInterval:
                self.curr_section = 0
            elif self.time >= timeInterval and self.time < timeInterval * 2:
                self.curr_section = 1
            elif self.time >= timeInterval * 2 and self.time < timeInterval * 3:
                self.curr_section = 2
            else:
                self.curr_section = 3

            self.topright_arc_color = self.HIGHLIGHTED_COLOR if self.curr_section == 0 else self.DEFAULT_COLOR
            self.botright_arc_color = self.HIGHLIGHTED_COLOR if self.curr_section == 1 else self.DEFAULT_COLOR
            self.botleft_arc_color = self.HIGHLIGHTED_COLOR if self.curr_section == 2 else self.DEFAULT_COLOR
            self.topleft_arc_color = self.HIGHLIGHTED_COLOR if self.curr_section == 3 else self.DEFAULT_COLOR
        elif self.controller.current_frame == self and self.curr_layer == self.SECOND_LAYER:
            self.time += 50
            cycleTime = 4000
            timeInterval = int(cycleTime / self.NUM_ARC_SECTIONS)
            self.time = self.time % cycleTime
            if self.time >= 0 and self.time < timeInterval:
                self.curr_arc = 0
            elif self.time >= timeInterval and self.time < timeInterval * 2:
                self.curr_arc = 1
            else:
                self.curr_arc = 2

            self.big_arc_color = self.HIGHLIGHTED_COLOR if self.curr_arc == 0 else self.DEFAULT_COLOR
            self.mid_arc_color = self.HIGHLIGHTED_COLOR if self.curr_arc == 1 else self.DEFAULT_COLOR
            self.small_arc_color = self.HIGHLIGHTED_COLOR if self.curr_arc == 2 else self.DEFAULT_COLOR
        elif self.controller.current_frame == self and self.curr_layer == self.THIRD_LAYER:
            self.time2 += 50
            cycleTime2 = 4000
            timeInterval2 = int(cycleTime2 / 5)
            self.time2 = self.time2 % cycleTime2
            if self.time2 >= 0 and self.time2 < timeInterval2:
                self.curr_letter = 0
            elif self.time2 >= timeInterval2 and self.time2 < timeInterval2 * 2:
                self.curr_letter = 1
            elif self.time2 >= timeInterval2 * 2 and self.time2 < timeInterval2 * 3:
                self.curr_letter = 2
            elif self.time2 >= timeInterval2 * 3 and self.time2 < timeInterval2 * 4:
                self.curr_letter = 3
            else:
                self.curr_letter = 4

            self.first_letter_color = self.HIGHLIGHTED_COLOR if self.curr_letter == 0 else self.DEFAULT_TEXT_COLOR
            self.second_letter_color = self.HIGHLIGHTED_COLOR if self.curr_letter == 1 else self.DEFAULT_TEXT_COLOR
            self.third_letter_color = self.HIGHLIGHTED_COLOR if self.curr_letter == 2 else self.DEFAULT_TEXT_COLOR
            self.forth_letter_color = self.HIGHLIGHTED_COLOR if self.curr_letter == 3 else self.DEFAULT_TEXT_COLOR
            self.fifth_letter_color = self.HIGHLIGHTED_COLOR if self.curr_letter == 4 else self.DEFAULT_TEXT_COLOR

        self.label.after(50, self.update)

    def send_command(self, command):
        if self.curr_layer == self.SECOND_LAYER:
            # Update the current circle
            if command == self.RIGHT_MI:
                self.curr_layer = self.THIRD_LAYER
                self.time = 0
            elif command == self.LEFT_MI:
                self.curr_layer = self.FIRST_LAYER
                self.time2 = 0
            else:
                self.curr_layer = self.SECOND_LAYER
                self.time = 0
        elif self.curr_layer == self.FIRST_LAYER:
            if command == self.RIGHT_MI:
                self.curr_layer = self.SECOND_LAYER
                self.time = 0
            elif command == self.LEFT_MI:
                if self.curr_chart == 0:
                    self.curr_chart = 1
                elif self.curr_chart == 1:
                    self.curr_chart = 0
                self.curr_layer = self.FIRST_LAYER
                self.time = 0
            else:
                self.curr_layer = self.FIRST_LAYER
                self.time = 0
        else:
            # this is where we choose a character
            if command == self.LEFT_MI:
                self.curr_layer = self.SECOND_LAYER
                self.time2 = 0
            elif command == self.RIGHT_MI:
                # save characters
                text_to_append = self.CHARS_LIST[self.curr_chart][self.curr_arc][
                    (self.curr_section + 1) * 5 - self.curr_letter - 1]
                # TODO : FIX THIS FROM MAKING TUPLE + second idea
                # if text_to_append == self.SPACE:
                #   text_to_append = ' '
                text_to_append = text_to_append.replace(self.SPACE, '_')
                TEXT.append(text_to_append)
                # TODO :
                if len(TEXT) % 10 == 0:
                    TEXT.append('\n')
                self.curr_layer = self.SECOND_LAYER
                self.time2 = 0
                # TODO fetch from text and update self.temp and self.BIG_CIRCLE_CHAR_L1
                print()
                self.next_char = [TEXT[-1]]
                print("char selected:", self.next_char)
                self.next_chars, self.states = self.one_step_model.generate_one_step(self.next_char, states=self.states)
                self.next_chars = [x.decode('utf-8') for x in self.next_chars.numpy()]
                self.next_chars = [s.replace(' ', self.SPACE) for s in self.next_chars]
                print("predicted chars:", self.next_chars)
                self.update_quadrant_textgen()
            else:
                self.curr_layer = self.THIRD_LAYER


class TextPage(tk.Frame):

    def __init__(self, parent, controller, session=None):
        tk.Frame.__init__(self, parent)
        self.label = tk.Label(self, text="CircleSpell", font=BOLD_FONT)
        self.label.pack()

        self.session = session
        self.controller = controller

        # Create canvas
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill=tk.BOTH, expand=1)

    # get text
    def draw_text(self):
        self.canvas.create_text(200, 400, text=TEXT, fill="black", font=("Verdana", 32))

    def show(self):
        # Begin the update loop
        self.label.after(100, self.update)
        self.canvas.after(100, self.render)

    def render(self):
        self.canvas.delete('all')
        self.draw_text()
        self.canvas.after(100, self.render)


###############################################################################
# Main
###############################################################################
if __name__ == "__main__":
    app = FrameContainer()
    app = TextFrameContainer()
    app.mainloop()

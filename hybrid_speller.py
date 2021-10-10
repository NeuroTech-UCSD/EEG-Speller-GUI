 #3.8.3 ('base': conda)
from psychopy import visual, event, core, gui, data, logging
from psychopy.visual import textbox  # import c
from numpy import sin, pi
import numpy as np
import time


class Group():
    '''

    '''

    def __init__(self, refresh_rate, win, num_squares, num_stimulations, width, height, edge_width, edge_height,
                 sequence_duration,
                 inter_stimulus_interval, stimulus_interval, top_left_x, top_left_y, flicker_freq, char_dict, char_posX, char_posY):
        self.refresh_rate = refresh_rate
        self.num_squares = num_squares
        self.num_stimulations = num_stimulations
        self.width = width
        self.height = height
        self.sequence_duration = sequence_duration
        self.top_left_x = top_left_x
        self.top_left_y = top_left_y
        self.flicker_freq = flicker_freq
        self.num_frame = int(refresh_rate / flicker_freq)
        self.unit_time = 1000 / refresh_rate
        self.sequence_duration_unit = int(sequence_duration / self.unit_time)
        self.inter_stimulus_interval = inter_stimulus_interval
        self.inter_stimulus_interval_unit = inter_stimulus_interval / self.unit_time
        self.stimulus_interval = stimulus_interval
        self.stimulus_interval_unit = stimulus_interval / self.unit_time
        self.squares = np.empty(
            [num_squares, 2], dtype=object)  # 2 makes a pair
        self.gates = np.zeros(num_squares, dtype=bool)
        self.win = win
        self.sequence_complete = False
        self.opacity = 0
        self.char_dict = char_dict
        self.text_boxes = np.empty(num_squares, dtype=object) #will this work?
        self.char_posX = char_posX
        self.char_posY = char_posY


        assert edge_height * \
            edge_width == num_squares, 'num_squares has to be = edge_height * edge_width!'
        for i in range(edge_height):
            for j in range(edge_width):
                idx = i * edge_width + j
                offset_x = width * j
                offset_y = - height * i
                #currRect = pygame.rect(left=(top_left_x + offset_x), top=(top_left_y + offset_y), width=width, height=height)

                self.squares[idx, 0] = visual.Rect(win, width=width, height=height,
                                                   pos=(top_left_x + offset_x, top_left_y + offset_y),
                                                   fillColor='black')
                #self.squares[idx, 0] = pygame.draw.rect(surface=win, color=(100, 100, 100), rect=currRect)
                self.squares[idx, 1] = visual.Rect(win, width=width, height=height,
                                                   pos=(top_left_x + offset_x, top_left_y + offset_y),
                                                   fillColor='white')
                #self.squares[idx, 1] = pygame.draw.rect(surface=win, color=(255, 255, 255), rect=currRect)

        #MAKE TEXTBOXES
        index = 0
        for i in self.char_dict:
                xShift = index % 3
                yShift = 0
                if 2 < index < 6:
                    yShift = 1
                elif index > 5:
                    yShift = 2

                self.text_boxes[index]=visual.TextBox(window=win,
                         text=i,
                         font_name='Menlo',
                         font_size=40,
                         #black = [-1,-1,-1]; blue = [-1,-1,1]; grey = [0,0,0]
                         font_color=[-1,-1,-1],
                         size=(1.9,.3),
                         pos=(self.char_posX + xShift*0.2, self.char_posY - yShift*0.265),
                         grid_horz_justification='center',
                         units='norm',
                         )
                index += 1 
        



    def update(self, curr_frame, phase):
        '''
        :param curr_frame (int):
        :param phase(str): 'init', 'mid', 'end'
        '''
        self.opacity = int((curr_frame % self.num_frame) >=
                           (self.num_frame / 2))  # 0 or 1
        for i in range(num_squares):
            self.gates[i] = False
        curr = curr_frame % self.sequence_duration_unit
        if phase == 'init':
            for i in range(num_squares):
                if i != num_squares - 1:
                    if self.inter_stimulus_interval_unit * i + self.stimulus_interval_unit * i < curr < self.inter_stimulus_interval_unit * i + self.stimulus_interval_unit * (
                            i + 1):
                        self.gates[i] = True
                # edge case
                elif i == num_squares - 1:
                    if self.inter_stimulus_interval_unit * i + self.stimulus_interval_unit * i < curr < self.inter_stimulus_interval_unit * (
                            i + 1) + self.stimulus_interval_unit * (i + 1):
                        self.gates[i] = True
        elif phase == 'mid':
            for i in range(num_squares):
                if i != num_squares - 1:
                    if self.inter_stimulus_interval_unit * i + self.stimulus_interval_unit * i < curr < self.inter_stimulus_interval_unit * i + self.stimulus_interval_unit * (
                            i + 1):
                        self.gates[i] = True
                # edge case
                elif i == num_squares - 1:
                    if (
                            self.inter_stimulus_interval_unit * i + self.stimulus_interval_unit * i < curr < self.inter_stimulus_interval_unit * (
                            i + 1) + self.stimulus_interval_unit * (i + 1)) \
                            or (0 < curr < - self.inter_stimulus_interval_unit):
                        self.gates[i] = True
        elif phase == 'end':
            if 0 < curr < - self.inter_stimulus_interval_unit:
                self.gates[-1] = True
            if curr == - self.inter_stimulus_interval_unit:
                self.sequence_complete = True

    def flash(self):
        for i in range(num_squares):
            if self.gates[i]:
                if self.opacity == 1:
                    self.squares[i, 0].draw()
                elif self.opacity == 0:
                    self.squares[i, 1].draw()

    def textPrint(self):
        for i in self.text_boxes:
            i.draw()


button_dict = np.array([['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'], 
            ['J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R'], 
            ['S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '#'], 
            ['.', '!', '?', 'D', 'S', '?', '?', '?', '?']])

flicker_freq = [9, 11, 13, 15]  # (top left, top right, bot left, bot right)
refresh_rate = 60
current_frame = 0
max_frame = 10000000  # just some large number

# replace visual.window with display.set
win = visual.Window([1000, 800], color='white', units='pix', monitor='testMonitor', fullscr=False)  # membuat Window # membuat Window
# win = pygame.display.set_mode((700, 800))

# pembuatan stimulus
# top left
width = 100
height = 100
edge_height = 3
edge_width = 3
num_squares = 9
num_stimulations = 3
num_groups = 4

stimulus_interval = 10000  # ms domain: (0, inf)
inter_stimulus_interval = -500  # ms domain: (-inf, 0)

# ms, of a sequence
sequence_duration = (stimulus_interval + inter_stimulus_interval) * num_squares
unit_time = 1000 / refresh_rate
sequence_duration_unit = int(sequence_duration / unit_time)
inter_stimulus_interval_unit = inter_stimulus_interval / unit_time
stimulus_interval_unit = stimulus_interval / unit_time

top_left_xs = [-400, 100, -400, 100]
top_left_ys = [300, 300, -100, -100]
char_posX = [-0.8, 0.2, -0.8, 0.2]
char_posY = [0.7, 0.7, -0.3, -0.3]
groups = np.empty(num_squares, dtype=object)
for i in range(num_groups):
    groups[i] = Group(refresh_rate, win, num_squares, num_stimulations, width, height, edge_width, edge_height,
                      sequence_duration,
                      inter_stimulus_interval, stimulus_interval, top_left_xs[i], top_left_ys[i], flicker_freq[i], button_dict[i], char_posX[i], char_posY[i])

tic = time.time()
curr_frame = 0

while groups[0].sequence_complete is False:
    # update phase
    if curr_frame < sequence_duration_unit * 1:
        phase = 'init'
    elif curr_frame > sequence_duration_unit * num_stimulations:
        phase = 'end'
    else:
        phase = 'mid'
    for j in range(num_groups):
        groups[j].update(curr_frame, phase)
    for j in range(num_groups):
        groups[j].flash()
        groups[j].textPrint()
    curr_frame += 1
    win.flip()
toc = time.time()
print('total time', (toc - tic) * 1000)

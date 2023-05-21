import os
import tkinter as tk
import tkinter.filedialog as tkfiledlg

import trax

DEFAULT_DATA_DIR = os.path.dirname(__file__) + '/../../raw/music/'
os.makedirs(DEFAULT_DATA_DIR, exist_ok=True)

NUM_BEATS_VISIBLE = trax.NUM_BEATS


NUM_COLS    = 1 + trax.NUM_TRACKS
NUM_ROWS    = 1 + NUM_BEATS_VISIBLE

TRACK_COL_START = 1
BEAT_ROW_START  = 1

FONT = ('Fira Code', 11, 'bold')
FONT_SM = ('Fira Code', 9, 'normal')
BGCOL       = '#222222'
SELROWBGCOL = '#083018'
SELCELBGCOL = '#106030'
FGCOL       = '#77e099'
IDCOL       = '#888888'


song = trax.Song()
pattern = song.patterns[0]


curr_beat = -1
curr_trak = 0
last_octave = 3



window = tk.Tk()
window.columnconfigure(NUM_COLS)
window.rowconfigure(NUM_ROWS)
window.rowconfigure(0, minsize=48)
window.title('MKTRAX')
window['bg'] = BGCOL


def load_btn_pressed():
    infilename = tkfiledlg.askopenfilename(defaultextension='trx', filetypes=[('trax file', '*.trx')], parent=window, initialdir=DEFAULT_DATA_DIR)
    print('trying to open', infilename, 'to read from')
    if infilename:
        song.loadFromFile(infilename)
        set_active_pattern(0)

def save_btn_pressed():
    outfilename = tkfiledlg.asksaveasfilename(defaultextension='trx', filetypes=[('trax file', '*.trx')], parent=window, initialdir=DEFAULT_DATA_DIR)
    print('trying to open', outfilename, 'to write to')
    if outfilename:
        song.saveToFile(outfilename)




def get_song_size_fmt():
    return '%0xh B' % song.calc_byte_size()



control_frame = tk.Frame(bg=BGCOL)

load_btn = tk.Button(master=control_frame, text='LOAD', command=load_btn_pressed, foreground=FGCOL, background=BGCOL, font=FONT)
save_btn = tk.Button(master=control_frame, text='SAVE', command=save_btn_pressed, foreground=FGCOL, background=BGCOL, font=FONT)
size_lbl = tk.Label(master=control_frame, text=get_song_size_fmt(), foreground=FGCOL, background=BGCOL, font=FONT_SM, padx=4)

load_btn.pack(side=tk.LEFT, anchor='n')
save_btn.pack(side=tk.LEFT, anchor='n')
size_lbl.pack(side=tk.RIGHT, anchor='ne')
control_frame.grid(row=0, column=0, columnspan=NUM_COLS, sticky='new', padx=4, pady=4)


def init_track_ctrls():
    beat_ctrls = []
    for beat in range(NUM_BEATS_VISIBLE):

        ctrls = []

        e = tk.Label(width=4, font=FONT, background=BGCOL, foreground=IDCOL)
        e.configure(text=f' %02d' % beat)
        e.grid(row=beat+BEAT_ROW_START, column=0)
        ctrls.append(e)

        for track in range(trax.NUM_TRACKS):
            e = tk.Label(width=8, font=FONT, background=BGCOL, foreground=FGCOL, padx=6, text='--- --')
            e.grid(row=beat+BEAT_ROW_START, column=track+TRACK_COL_START)

            onclick = lambda _, track=track, beat=beat: handle_beat_ctrl_clicked(track, beat)
            e.bind('<Button-1>', onclick)

            ctrls.append(e)

        beat_ctrls.append(ctrls)

    return beat_ctrls


beat_ctrls = init_track_ctrls()



def set_active_pattern(patix):
    global pattern
    pattern = song.patterns[patix]
    for beatix in range(pattern.nbeats):
        for trackix in range(len(pattern.tracks)):
            ctrl = beat_ctrls[beatix][trackix+TRACK_COL_START]
            ctrl['text'] = pattern.tracks[trackix][beatix].get_editor_str()


def update_curr_beat(newbeat):
    global curr_beat, curr_trak
    if curr_beat >= 0:
        for ctrl in beat_ctrls[curr_beat]:
            ctrl.configure(background=BGCOL)

    curr_beat = newbeat
    for ix,ctrl in enumerate(beat_ctrls[curr_beat]):
        ctrl.configure(background=SELCELBGCOL if ix==(curr_trak+TRACK_COL_START) else SELROWBGCOL)


def update_note(beat, trak, key):
    global last_octave
    print('handling note update: ' + key)
    ctrl = beat_ctrls[beat][trak+TRACK_COL_START]
    trak_note = pattern.tracks[trak][beat]

    if key in 'abcdefg':
        trak_note.note = key.upper()
        if not trak_note.active:
            trak_note.active = True
            trak_note.octave = last_octave

    elif key == 'numbersign':
        ACCIDENTALS = list('-#b')
        oldaccix = ACCIDENTALS.index(trak_note.accidental)
        newaccix = (oldaccix + 1) % len(ACCIDENTALS)
        trak_note.accidental = ACCIDENTALS[newaccix]

    elif key in '1234567':
        trak_note.octave = int(key)
        last_octave = int(key)

    elif key in 'x-':
        trak_note.active = not trak_note.active
    
    ctrl['text'] = trak_note.get_editor_str()



def handle_keypress(evt):
    global curr_beat, curr_trak

    if evt.keysym == 'Up':
        update_curr_beat((curr_beat + pattern.nbeats - 1) % NUM_BEATS_VISIBLE)

    elif evt.keysym == 'Down':
        update_curr_beat((curr_beat + 1) % NUM_BEATS_VISIBLE)

    elif evt.keysym == 'Left':
        curr_trak = (curr_trak + trax.NUM_TRACKS - 1) % trax.NUM_TRACKS
        update_curr_beat(curr_beat)

    elif evt.keysym == 'Right':
        curr_trak = (curr_trak + 1) % trax.NUM_TRACKS
        update_curr_beat(curr_beat)

    else:
        update_note(curr_beat, curr_trak, evt.keysym)


def handle_beat_ctrl_clicked(trackix, beatix):
    global curr_trak
    curr_trak = trackix
    update_curr_beat(beatix)
    
    

window.bind('<Key>', handle_keypress)

update_curr_beat(0)

window.mainloop()


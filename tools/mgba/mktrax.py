import tkinter as tk

NUM_TRACKS  = 4
NUM_BEATS   = 32

NUM_COLS    = 1 + NUM_TRACKS
NUM_ROWS    = 1 + NUM_BEATS

TRACK_COL_START = 1
BEAT_ROW_START  = 1

FONT = ('Fira Code', 11, 'bold')
BGCOL       = '#222222'
SELROWBGCOL = '#083018'
SELCELBGCOL = '#106030'
FGCOL       = '#77e099'
IDCOL       = '#888888'


curr_beat = -1
curr_trak = 0


def load_btn_pressed():
    print('LOAD pressed')

def save_btn_pressed():
    print('SAVE pressed')



window = tk.Tk()
window.columnconfigure(NUM_COLS)
window.rowconfigure(NUM_ROWS)
window.rowconfigure(0, minsize=48)
window.title('MKTRAX')
window['bg'] = BGCOL


beat_ctrls = []

control_frame = tk.Frame(bg=BGCOL)

load_btn = tk.Button(master=control_frame, text='LOAD', command=load_btn_pressed, foreground=FGCOL, background=BGCOL, font=FONT)
save_btn = tk.Button(master=control_frame, text='SAVE', command=save_btn_pressed, foreground=FGCOL, background=BGCOL, font=FONT)

load_btn.pack(side=tk.LEFT, anchor='n')
save_btn.pack(side=tk.LEFT)
control_frame.grid(row=0, column=0, columnspan=NUM_COLS, sticky='nw', padx=4, pady=4)


for beat in range(NUM_BEATS):

    ctrls = []

    e = tk.Label(width=4, font=FONT, background=BGCOL, foreground=IDCOL)
    e.configure(text=f' %02d' % beat)
    e.grid(row=beat+BEAT_ROW_START, column=0)
    ctrls.append(e)

    for track in range(NUM_TRACKS):
        e = tk.Label(width=8, font=FONT, background=BGCOL, foreground=FGCOL)
        e.configure(text=' --- --')
        e.grid(row=beat+BEAT_ROW_START, column=track+TRACK_COL_START)
        ctrls.append(e)

    beat_ctrls.append(ctrls)


def update_curr_beat(newbeat):
    global curr_beat, curr_trak
    if curr_beat >= 0:
        for ctrl in beat_ctrls[curr_beat]:
            ctrl.configure(background=BGCOL)

    curr_beat = newbeat
    for ix,ctrl in enumerate(beat_ctrls[curr_beat]):
        ctrl.configure(background=SELCELBGCOL if ix==(curr_trak+TRACK_COL_START) else SELROWBGCOL)


def update_note(beat, trak, key):
    print('handling note update: ' + key)
    ctrl = beat_ctrls[beat][trak+TRACK_COL_START]
    oldval = ctrl['text']

    if key in 'abcdefg':
        newval = oldval[:1] + key.upper() + oldval[2:]
        ctrl['text'] = newval
        print(oldval + ' -> ' + newval)

    elif key == 'numbersign':
        newsharp = '#' if oldval[2] != '#' else '-'
        newval = oldval[:2] + newsharp + oldval[3:]
        ctrl['text'] = newval
        print(oldval + ' -> ' + newval)

    elif key in '1234567':
        newval = oldval[:3] + key + oldval[4:]
        ctrl['text'] = newval
        print(oldval + ' -> ' + newval)


def handle_keypress(evt):
    global curr_beat, curr_trak

    if evt.keysym == 'Up':
        update_curr_beat((curr_beat + NUM_BEATS - 1) % NUM_BEATS)

    elif evt.keysym == 'Down':
        update_curr_beat((curr_beat + 1) % NUM_BEATS)

    elif evt.keysym == 'Left':
        curr_trak = (curr_trak + NUM_TRACKS - 1) % NUM_TRACKS
        update_curr_beat(curr_beat)

    elif evt.keysym == 'Right':
        curr_trak = (curr_trak + 1) % NUM_TRACKS
        update_curr_beat(curr_beat)

    else:
        update_note(curr_beat, curr_trak, evt.keysym)
    

window.bind('<Key>', handle_keypress)

update_curr_beat(0)

window.mainloop()


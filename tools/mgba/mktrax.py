import tkinter as tk

NUM_TRACKS=4
NUM_BEATS=32

FONT = ('Fira Code', 11, 'bold')
BGCOL       = '#222222'
SELBGCOL    = '#106030'
FGCOL       = '#77e099'
IDCOL       = '#888888'


curr_beat = -1
curr_trak = 0



window = tk.Tk()
window.columnconfigure(NUM_TRACKS + 1)
window.rowconfigure(NUM_BEATS)
window.title('MKTRAX')

beat_ctrls = []


for beat in range(NUM_BEATS):

    ctrls = []

    e = tk.Entry(width=4, font=FONT, background=BGCOL, foreground=IDCOL)
    e.insert(0, f'  %02d' % beat)
    e.grid(row=beat, column=0)
    ctrls.append(e)

    for track in range(NUM_TRACKS):
        e = tk.Entry(width=8, font=FONT, background=BGCOL, foreground=FGCOL)
        e.insert(0, " --- --")
        e.grid(row=beat, column=track+1)
        ctrls.append(e)

    beat_ctrls.append(ctrls)


def update_curr_beat(newbeat):
    global curr_beat, curr_trak
    if curr_beat >= 0:
        for ctrl in beat_ctrls[curr_beat]:
            ctrl.configure(background=BGCOL)

    curr_beat = newbeat
    for ctrl in beat_ctrls[curr_beat]:
        ctrl.configure(background=SELBGCOL)

    beat_ctrls[curr_beat][curr_trak + 1].focus()


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
    

window.bind('<Key>', handle_keypress)

update_curr_beat(0)

window.mainloop()


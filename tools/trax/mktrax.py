import os, socket
import tkinter as tk
import tkinter.filedialog as tkfiledlg

import trax


class LiveUpdater:
    PORT = 51337
    ADDR_START = 0x02000000

    def __init__(self):
        self.active = False
        self.synced = False
    
    def activate(self, song):
        if self.active:
            print('WARN: trying to activate live update when it\'s already active')
            return
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(('127.0.0.1', LiveUpdater.PORT))
            self.socket.settimeout(1)

            self.active = True
            self.synced = False

            self.sync(song)

            return True

        except:
            return False
        

    def deactivate(self):
        if not self.active:
            print('WARN: trying to deactivate live update when it\'s not active')
            return
        
        self.socket.close()
        self.socket = None
        
        self.active = False

    
    def sync(self, song):
        if not self.active:
            print('WARN: trying to sync when updater is inactive')
            return

        print('\n\n--- START SYNC -----------------')
        bin = trax.compile_song(song)
        for offs in range(0, len(bin), 2):
            cmd = 'POKE %08X %02X%02X\n' % (LiveUpdater.ADDR_START + offs, int(bin[offs+1]), int(bin[offs]))
            print(f'>{cmd}', end=None)
            self.socket.sendall(cmd.encode())
            res = self.socket.recv(1024)
            if not res:
                raise Exception('socket recv timed out');
            print(f'<{res!r}')
        print('--- FINISH SYNC -------------------\n')

        self.synced = True
        self.sync_bin = bin


    def update(self, song):
        if not self.active or not self.synced:
            print('WARN: trying to sync when updater isn\'t active and synced')
            return
        
        oldbin = self.sync_bin
        newbin = trax.compile_song(song)
        for offs in range(0, len(newbin), 2):
            if (oldbin[offs] == newbin[offs]) and (oldbin[offs+1] == newbin[offs+1]):
                continue

            cmd = 'POKE %08X %02X%02X\n' % (LiveUpdater.ADDR_START + offs, int(newbin[offs+1]), int(newbin[offs]))
            print(f'>{cmd}', end=None)
            self.socket.sendall(cmd.encode())
            res = self.socket.recv(1024)
            if not res:
                raise Exception('socket recv timed out');
            print(f'<{res!r}')

        self.sync_bin = newbin
    
        



DEFAULT_DATA_DIR = os.path.dirname(__file__) + '/../../raw/music/'
os.makedirs(DEFAULT_DATA_DIR, exist_ok=True)

NUM_BEATS_VISIBLE = trax.NUM_BEATS


NUM_COLS    = 1 + trax.NUM_TRACKS
NUM_ROWS    = 1 + NUM_BEATS_VISIBLE

TRACK_COL_START = 1
BEAT_ROW_START  = 1

FONT = ('Fira Code', 11, 'normal')
FONT_SM = ('Fira Code', 9, 'normal')
BGCOL       = '#222222'
SELROWBGCOL = '#083018'
SELCELBGCOL = '#106030'
FGCOL       = '#77e099'
IDCOL       = '#888888'
LIVECOL     = '#bb2277'


song = trax.Song()
pattern = song.patterns[0]


curr_beat = -1
curr_trak = 0
last_octave = 3


live_updater = LiveUpdater()



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
        song.load_from_file(infilename)
        songname_txt.set(song.name)
        set_active_pattern(0)

def save_btn_pressed():
    outfilename = tkfiledlg.asksaveasfilename(defaultextension='trx', filetypes=[('trax file', '*.trx')], parent=window, initialdir=DEFAULT_DATA_DIR)
    print('trying to open', outfilename, 'to write to')
    if outfilename:
        song.save_to_file(outfilename)

def live_btn_pressed():
    if not live_updater.active:
        if live_updater.activate(song):
            live_btn.configure(text='!LIVE!', bg=LIVECOL)
    else:
        live_updater.deactivate()
        live_btn.configure(text=' live ', bg=BGCOL)
    




def get_song_size_fmt():
    return '%0xh byt' % song.calc_byte_size()


is_focused_in_control = 0
def handle_focus_in(*args):
    global is_focused_in_control
    is_focused_in_control += 1
def handle_focus_out(*args):
    global is_focused_in_control
    is_focused_in_control -= 1


control_frame = tk.Frame(bg=BGCOL)

load_btn = tk.Button(master=control_frame, text='LOAD', command=load_btn_pressed, foreground=FGCOL, background=BGCOL, font=FONT)
save_btn = tk.Button(master=control_frame, text='SAVE', command=save_btn_pressed, foreground=FGCOL, background=BGCOL, font=FONT)
live_btn = tk.Button(master=control_frame, text=' live ', command=live_btn_pressed, foreground=FGCOL, background=BGCOL, font=FONT)
songname_txt = tk.StringVar()
songname_ent = tk.Entry(master=control_frame, textvariable=songname_txt, foreground=FGCOL, background=BGCOL, font=FONT)
songname_ent.bind('<FocusIn>', handle_focus_in)
songname_ent.bind('<FocusOut>', handle_focus_out)
legend_lbl = tk.Label(master=control_frame, text='['+trax.EDITOR_NOTE_GUIDE+']', foreground=FGCOL, background=BGCOL, font=FONT, padx=4)
size_lbl = tk.Label(master=control_frame, text=get_song_size_fmt(), foreground=FGCOL, background=BGCOL, font=FONT_SM, padx=4)

load_btn.pack(side=tk.LEFT, anchor='n')
save_btn.pack(side=tk.LEFT, anchor='n')
live_btn.pack(side=tk.LEFT, anchor='n')
songname_ent.pack(side=tk.LEFT, padx=4)
size_lbl.pack(side=tk.RIGHT, anchor='e')
legend_lbl.pack(side=tk.RIGHT, anchor='e')
control_frame.grid(row=0, column=0, columnspan=NUM_COLS, sticky='new', padx=4, pady=4)


def init_track_ctrls():
    beat_ctrls = []
    for beat in range(NUM_BEATS_VISIBLE):

        ctrls = []

        e = tk.Label(width=3, font=FONT, background=BGCOL, foreground=IDCOL)
        e.configure(text=f' %02d' % beat)
        e.grid(row=beat+BEAT_ROW_START, column=0)
        ctrls.append(e)

        for track in range(trax.NUM_TRACKS):
            e = tk.Label(width=11, font=FONT, background=BGCOL, foreground=FGCOL, padx=6, text=trax.EMPTY_EDITOR_NOTE, cursor='cross_reverse')
            e.grid(row=beat+BEAT_ROW_START, column=track+TRACK_COL_START)

            onclick = lambda _, track=track, beat=beat: handle_beat_ctrl_clicked(track, beat)
            e.bind('<Button-1>', onclick)

            ctrls.append(e)

        beat_ctrls.append(ctrls)

    return beat_ctrls


beat_ctrls = init_track_ctrls()
songname_txt.set(song.name)
def update_songname(*args): song.name = songname_txt.get()
songname_txt.trace('w', update_songname) 



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

    key = key.lower()   # backspace is BackSpace. not sure how consistently...

    if key in 'abcdefg':
        trak_note.set_note(key.upper())
        if not trak_note.active:
            trak_note.active = True
            trak_note.set_octave(last_octave)

    elif key == 'numbersign':
        ACCIDENTALS = list('-#b')
        oldaccix = ACCIDENTALS.index(trak_note.get_accidental())
        newaccix = (oldaccix + 1) % len(ACCIDENTALS)
        trak_note.set_accidental(ACCIDENTALS[newaccix])

    elif key in '01234567':
        trak_note.set_octave(int(key))
        last_octave = int(key)

    elif key == 'x' or key == 'minus' or key == 'backspace':
        trak_note.active = not trak_note.active
    
    ctrl['text'] = trak_note.get_editor_str()

    if live_updater.active:
        live_updater.update(song)



def handle_keypress(evt):
    global curr_trak

    if is_focused_in_control > 0:
        return

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
    # force a defocus of any focused widget
    window.focus_set()

    global curr_trak
    curr_trak = trackix
    update_curr_beat(beatix)
    
    

window.bind('<Key>', handle_keypress)

update_curr_beat(0)

window.mainloop()


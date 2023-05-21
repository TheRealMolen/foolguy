import math


FLAT_TO_SHARP = { 'ab':'g#', 'bb':'a#', 'cb':'b', 'db':'c#', 'eb':'d#', 'fb':'e', 'gb':'f#' }
NOTE_ORDER = ['c','c#','d','d#','e','f','f#','g','g#','a','a#','b']
C2_HZ = 65.41


def calc_valid_notes():
    notes = list('abcdefg') + list(FLAT_TO_SHARP.keys()) + list(FLAT_TO_SHARP.values())
    return set(notes)


VALID_NOTES = calc_valid_notes()


def clamp(v, lo, hi):
    return min(max(v, lo), hi)


def note_to_hz(note, octave):
    octave = clamp(octave, 2, 8)

    note = note.lower()
    if note in FLAT_TO_SHARP.keys():
        if note == 'cb':
            octave -= 1
        note = FLAT_TO_SHARP[note]
    
    n = NOTE_ORDER.index(note)
    semis = n + ((octave-2) * 12)

    hz = math.pow(2.0, semis / 12) * C2_HZ

    return hz
    

def note_to_gba_freq(note, octave):
    hz = note_to_hz(note, octave)
    counter = (2048.0 - ((1<<17) / (hz)))
    return clamp(int(counter), 0, 2047)


###############################################################################################################

# note, accidental, octave   |   velocity, envelope, length     |    extension data per sound type
# nao vell xx
# C#4 F700 D3

EMPTY_EDITOR_NOTE = '--- ---- --'
EDITOR_NOTE_GUIDE = 'nao vell xx'

class GbaNote:
    def __init__(self):
        self.active = False
        self._note = 'x'
        self._accidental = '-'
        self._octave = 0
        self.velocity = 0xf
        self.decay = 2
        self.reverse = False
        self.length = 0        # if >0, the duration of the note in 256ths of a sec
        
    
    def set_note(self, note):
        self._note = note

    def set_accidental(self, acc):
        self._accidental = acc

    def set_octave(self, octave):
        self._octave = octave

    def get_note_name(self):
        if self._accidental != '-':
            return self._note + self._accidental
        return self._note

    def get_gba_freq(self):
        "return the value to write into REG_SOUNDnCNT_X(64h/6Ch/74h) for this note"
        if not self.active:
            return 0
        
        word = note_to_gba_freq(self.get_note_name(), self._octave)

        if self.length > 0:
            word = word | 0x4000

        word = word | 0x8000    # trigger envelope/length
        return word
    
    def parse(self, tokens, trackix):
        self.active = False
        if len(tokens) == 1 and tokens[0] == '-':
            return
        
        self._parse_note(tokens[0])
        self.active = True

        for token in tokens[1:]:
            if not self._parse_token(token):
                print(f'WARNING: failed to parse note param "{token}" for track {trackix}')

    def get_editor_str(self) -> str:
        if not self.active:
            return EMPTY_EDITOR_NOTE
        
        note_str = self._note + self._accidental + str(self._octave)
        env_str = '%0X' % clamp(self.velocity, 0, 15)
        env_str += self._get_env_str()
        if self.length > 0:
            env_str += '%02X' % clamp(self.length, 0, 255)
        else:
            env_str += '--'

        ext_str = self.get_editor_ext_str()
        return note_str + ' ' + env_str + ' ' + ext_str

    def get_editor_ext_str(self):
        return '--'
        

    def _get_env_str(self) -> str:
        if not self.reverse:
            return '%0X' % clamp(self.decay, 1, 7)
        
        return '%0X' % clamp(((-self.decay) & 0xf), 8, 0xf)
        


    def _parse_note(self, token):
        self._note = token[0]
        if self._note.lower() not in 'abcdefg':
            raise Exception(f'"{self._note}" aint a valid note')
        
        self._accidental = token[1]
        if self._accidental not in '-#b':
            raise Exception(f'"{self._note}{self._accidental}" aint a valid note')
        
        self._octave = int(token[2])
    
    def _parse_token(self, token):
        if token[0] == 'l':
            self.length = int(token[1:])
            return True
        
        if token[0] == 'd':
            self.decay = int(token[1:])
            if self.decay < 0:
                self.reverse = True
                self.decay = -self.decay
            return True
        
        if token[0] == 'v':
            self.velocity = int(token[1:], 16)
            return True
        
        return False
    

    def __repr__(self):
        return self.get_editor_str()

    

class SquareNote(GbaNote):
    DUTIES = { 12.5:0, 25:1, 50:2, 75:3 }
    DUTIES_BY_ENCODING = {v:k for k,v in DUTIES.items()}
    
    def __init__(self):
        GbaNote.__init__(self)
        self.duty = 50

    def _parse_token(self, token):                
        if token[0] == 'c':
            self.duty = self.DUTIES_BY_ENCODING[int(token[1:])]
            return True
        
        return super()._parse_token(token)    

    def get_gba_ctrl(self):
        "return the value to write into REG_SOUNDxCNT_H(62h/68h) for this note"
        if not self.active:
            return 0
        
        word = 0

        if self.length >= 0:
            word = word | clamp(self.length, 0, 63)
        
        word = word | (self.DUTIES[self.duty] << 6)

        word = word | (clamp(self.decay, 0, 7) << 8)

        if self.reverse:
            word = word | 0x0800

        word = word | (clamp(self.velocity, 0, 15) << 12)

        return word


class WaveTblNote(GbaNote):
    VEL_TO_VOL = [0,3,3,3, 3,3,2,2, 2,2,4,4, 4,4,1,1]   # roughly maps 0-f velocity to snd3 volumes

    def __init__(self):
        GbaNote.__init__(self)

        self.instrument = 0     # 32 bit instrument index, packed into unused bits in reg 72h

    def _parse_token(self, token):                
        if token[0] == 'i':
            self.instrument = int(token[1:])
            return True
        
        return super()._parse_token(token)  

    def get_gba_ctrl(self):
        "return the value to write into REG_SOUND3CNT_H(72h) for this note"
        if not self.active:
            return 0
        
        word = clamp(self.length, 0, 255)

        # pack the instrument id into bits 8-C as the hw ignores them
        word = word | (self.instrument & 31) << 8
        
        word = word | (self.VEL_TO_VOL[self.velocity] << 0xD)

        return word


class NoiseNote(GbaNote):
    def __init__(self):
        GbaNote.__init__(self)

        # NB. clockdiv packed in octave; 7-0 for 8.2Mhz, 4.1, 4/2, 4/3, 4/4, 4/5, 4/6, 4/7 freq into the scale
        self._octave = 6
        
        # NB. clocklog packed in ((note << 1) | accidental); # and b both count as 1; notes are in reverse order to make A# lower pitch than B
        self._note = 'c'

        self.shortseq = False   # if True, drops to only using a 7 stage rng, repeating after 63 clocks
        
        self.decay = 2          # decay rate, higher is slower, 1-7
        self.reverse = False    # if True, the envelope is reversed
        
    
    def get_clockdiv(self):
        if not self.active:
            return 0
        return 7 - clamp(self._octave, 0, 7)
    
    def get_clocklog(self):
        if not self.active:
            return 0
        
        noteix = 'gfedcba'.index(self._note.lower())
        if noteix < 0:
            raise Exception(f'Noise: can\'t pack invalid note {self._note}')
        accbit = 0 if self._accidental != '-' else 1
        return (noteix << 1) | accbit



    def get_gba_ctrl(self):
        "return the value to write into REG_SOUND4CNT_L(78h) for this note"
        if not self.active:
            return 0
        
        word = 0

        if self.length >= 0:
            word = word | clamp(self.length, 0, 63)

        word = word | (clamp(self.decay, 0, 7) << 8)

        if self.reverse:
            word = word | 0x0800

        word = word | 0x8000    # trigger envelope/length
        return word
    
    def get_gba_freq(self):
        "return the value to write into REG_SOUND4CNT_H(7Ch) for this note"
        if not self.active:
            return 0
        
        word = 0

        word = word | (self.get_clockdiv() & 7)
        if self.shortseq:
            word = word | 0x08

        word = word | ((self.get_clocklog() & 0xf) << 4)

        if self.length >= 0:
            word = word | 0x4000

        word = word | 0x8000    # trigger envelope/length
        return word
        


###############################################################################################################

NUM_TRACKS  = 4
NUM_BEATS   = 32


class Pattern():
    def __init__(self, nbeats=NUM_BEATS):
        self.nbeats = nbeats
        self.tracks = [[SquareNote() for _ in range(self.nbeats)],
                       [SquareNote() for _ in range(self.nbeats)],
                       [WaveTblNote() for _ in range(self.nbeats)],
                       [NoiseNote() for _ in range(self.nbeats)]]
        
    def calc_byte_size(self):
        bytes_per_note = 4
        bytes = 0
        for track in self.tracks:
            bytes += len(track) * bytes_per_note
        
        return bytes
    
    @staticmethod
    def load(header, itline):
        hdr_toks = header.split(' ')
        hdr = dict(tok.split('=',1) for tok in hdr_toks[1:])
        nbeats = int(hdr['beats'])

        pattern = Pattern(nbeats)
        for beatix in range(nbeats):
            event_line = next(itline)
            if event_line == '':
                raise Exception(f'invalid beat def "{event_line}"')
            
            for trackix,note in enumerate(event_line.split('\t')):
                note_toks = [tok.strip() for tok in note.strip().split()]
                pattern.tracks[trackix][beatix].parse(note_toks, trackix)
        
        return pattern




class Song:
    def __init__(self):
        self.patterns = [Pattern()]
        self.name = 'unnamed'

    def calc_byte_size(self):
        bytes = 0 # header bytes
        for pattern in self.patterns:
            bytes += pattern.calc_byte_size()

        return bytes
    
    def loadFromFile(self, infilename):
        old_patterns = self.patterns
        self.patterns = []

        with open(infilename, 'rt') as infile:
            lines = [line.strip() for line in infile.readlines()]
            itline = iter(lines)

            try:
                self._chk_magic(next(itline))

                # parse header data
                while True:
                    line = next(itline)
                    if line == '':
                        break

                # parse song data
                while True:
                    block_hdr = self._get_next_line(itline)
                    if block_hdr.startswith('!Pattern'):
                        new_pattern = Pattern.load(block_hdr, itline)
                        self.patterns.append(new_pattern)
                    else:
                        raise Exception(f'unrecognised block header "{block_hdr}"')

            except StopIteration:
                pass


    def saveFromFile(self, outfilename):
        print('TODO: saving')


    @staticmethod
    def _chk_magic(line):
        tokens = line.split(' ')
        if len(tokens) != 2 or tokens[0] != 'TRAX':
            raise Exception('invalid/corrupt trax file')
        if tokens[1] != '0.1':
            raise Exception('unsupported file version')
       
    @staticmethod 
    def _get_next_line(iter):
        "keeps reading from a lines iterator until it finds a non-blank line, or raises StopIteration"
        while True:
            line = next(iter)
            if not line == '':
                return line




if __name__ == '__main__':
    song = Song()
    infilename = 'raw/music/theme.trx'
    song.loadFromFile(infilename)
    print(f'loaded song with {len(song.patterns)} patterns from {infilename}')


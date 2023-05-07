import argparse, re, os


class Font(object):
    def __init__(self, firstChar, lastChar, missingTile):
        self.firstChar = firstChar
        self.lastChar = lastChar
        self.missingTile = missingTile
        self.glyphMap = [missingTile] * (lastChar - firstChar + 1)


    def _setCharGlyph(self, char, tileIndex):
        o = ord(char)
        if o < self.firstChar or o > self.lastChar:
            raise Exception(f'out of range glyph encountered: "{c}" ({o})')
        if tileIndex >= 256:
            raise Exception(f'tile index has exceeded 256 (for character "{c}" ({o})')
        
        self.glyphMap[o - self.firstChar] = tileIndex


    def parse(self, filename):
        # these can be overridden in the file with directives
        tileOffset = 0      # the tile index of the next glyph in the font
        allCaps = False     # if true, emit a lowercase glyph for each uppercase char encountered
        
        comment_re = r"\s*#.*$"

        with open(filename, "rt") as infile:
            for rawline in infile.readlines():
                line = re.sub(comment_re, '', rawline, 0).rstrip()  # note: don't strip leading whitespace in case it's an intentional space character
                if line == '':
                    continue

                # is this line a directive?
                if line.startswith('.offset'):
                    tileOffset = int(line.split(' ')[1])
                
                elif line.startswith('.allcaps'):
                    allCaps = True

                else:
                    for c in line:
                        self._setCharGlyph(c, tileOffset)
                        
                        if allCaps and c.isalpha():
                            self._setCharGlyph(c.lower(), tileOffset)

                        tileOffset += 1



def get_default_symname(fntfile):
    basename = os.path.basename(fntfile)
    symname = basename.replace('.fnt', '').replace(r"[^a-zA-Z0-9]", '_')      
    return symname.upper()

def parse_args():
    parser = argparse.ArgumentParser(description='loads a font def (.fnt) file and emits a simple character lookup as an asm (.s) and c header')
    parser.add_argument('fntfile')
    parser.add_argument('-o', '--outfilestem', help='the output will be written to OUTFILESTEM.s and OUTFILESTEM.h')
    parser.add_argument('-s', '--symbol', help='the stem of the c symbol names; defaults to sanitised fntfile name')
    parser.add_argument('-f', '--firstcharix', type=int, default=ord(" "), help='the ascii value of the first char to be emitted')
    parser.add_argument('-l', '--lastcharix', type=int, default=ord("~"), help='the ascii value of the last char to be emitted')
    parser.add_argument('-m', '--missingtile', type=int, default=0, help='the tile number to emit for missing chars')

    return parser.parse_args()


def write_font_header(font, outfilename, symbolstem, infilename):
    lines = []

    lines.append(f'// GBA font exported from {infilename}')
    lines.append(f'//\n')
    lines.append('#pragma once\n')

    lines.append(f'static const unsigned char {symbolstem}_firstchar = {font.firstChar};')
    lines.append(f'static const unsigned char {symbolstem}_lastchar = {font.lastChar};')
    lines.append(f'extern const unsigned char {symbolstem}_glyphtiles[];')

    lines.append('\n\n')

    with open(outfilename, 'wt') as f:
        f.write('\n'.join(lines))


def write_font_asm(font, outfilename, symbolstem, infilename):
    lines = []
    lines.append('''\
@
@	GBA font exported from {infilename}
@

	.section .rodata
	.align	1
	.global {symbolstem}_glyphtiles
	.hidden {symbolstem}_glyphtiles

{symbolstem}_glyphtiles:\
'''.format(symbolstem=symbolstem, infilename=infilename))

    o = font.firstChar
    for tileix in font.glyphMap:
        lines.append(f'\t.byte\t{tileix}\t@ {chr(o)}')
        o += 1

    lines.append('\n')

    with open(outfilename, 'wt') as f:
        f.write('\n'.join(lines))


def main():
    args = parse_args()

    font = Font(args.firstcharix, args.lastcharix, args.missingtile)
    font.parse(args.fntfile)

    symname = args.symbol if args.symbol else get_default_symname(args.fntfile)
    outfilename = args.outfilestem if args.outfilestem else args.fntfile
    outfilestem = os.path.splitext(outfilename)[0]

    write_font_header(font, outfilestem+'.h', symname, args.fntfile)
    write_font_asm(font, outfilestem+'.s', symname, args.fntfile)


if __name__ == '__main__':
    main()
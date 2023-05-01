import argparse, re, os


def parse_gpl(filename):
    "loads a gimp palette file and returns an array of colour entries"
    palette = []
    comment_re = r"\s*#.*$"
    entry_re = r"\s*(\d+)\s*(\d+)\s*(\d+)\s*(\S+)?\s?$"

    with open(filename, "rt") as infile:
        lines = infile.readlines()
        if lines[0].strip() != 'GIMP Palette':
            raise Exception(f'{filename} doesn\'t seem to be in GIMP Palette format')
        
        for rawline in lines[1:]:
            line = re.sub(comment_re, '', rawline, 0, re.MULTILINE).strip()
            if line == '':
                continue

            m = re.match(entry_re, line)
            if not m:
                raise Exception(f'{rawline} seems invalid')
            
            entry = dict(r=int(m[1]), g=int(m[2]), b=int(m[3]), desc=m[4])
            palette.append(entry)

    return palette


def get_default_symname(gplfile):
    basename = os.path.basename(gplfile)
    symname = basename.replace('.gpl', '').replace(r"[^a-zA-Z0-9]", '_')      
    return symname.upper()

def parse_args():
    parser = argparse.ArgumentParser(description='loads a GIMP Palette (.gpl) file and emits a gba-compatible palette as .h & .c files')
    parser.add_argument('gplfile')
    parser.add_argument('-o', '--outfilestem', help='the output will be written to OUTFILESTEM.c and OUTFILESTEM.h')
    parser.add_argument('-s', '--symbol', help='the stem of the c symbol names; defaults to sanitised gplfile name')

    return parser.parse_args()

def clamp(v, lo, hi):
    if v <= lo:
        return lo
    if v >= hi:
        return hi
    return v

def entry_to_hex(entry):
    r = clamp(entry['r'] >> 3, 0, 31)
    g = clamp(entry['g'] >> 3, 0, 31)
    b = clamp(entry['b'] >> 3, 0, 31)
    u16 = r | (g << 5) | (b << 10)
    return '%#04x' % u16


def write_pal_header(palette, outfilename, symbolstem, infilename):

    lines = []
    lines.append(f'// GBA palette exported from {infilename}')
    lines.append(f'//\n')
    lines.append('#pragma once\n')

    lines.append(f'extern const unsigned short {symbolstem}_paldata[];')
    lines.append(f'static const unsigned short {symbolstem}_palcount = {len(palette)};')

    lines.append('\n\n')

    with open(outfilename, 'wt') as f:
        f.write('\n'.join(lines))

def write_pal_c(palette, outfilename, symbolstem, infilename):

    lines = []
    lines.append(f'// GBA palette exported from {infilename}')
    lines.append(f'//\n')

    lines.append(f'const unsigned short {symbolstem}_paldata[] = ')
    lines.append('{')
    for entry in palette:
        lines.append(f'\t{entry_to_hex(entry)},\t// {entry["desc"]}')
    lines.append('};\n\n')

    with open(outfilename, 'wt') as f:
        f.write('\n'.join(lines))


def main():
    args = parse_args()

    palette = parse_gpl(args.gplfile)

    symname = args.symbol if args.symbol else get_default_symname(args.gplfile)
    outfilename = args.outfilestem if args.outfilestem else args.gplfile
    outfilestem = os.path.splitext(outfilename)[0]

    write_pal_header(palette, outfilestem+'.h', symname, args.gplfile)
    write_pal_c(palette, outfilestem+'.c', symname, args.gplfile)



if __name__ == '__main__':
    main()
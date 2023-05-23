import argparse
import trax


def parse_args():
    parser = argparse.ArgumentParser(description='loads a TRAX file and emits gba-native data as a .bin file')
    parser.add_argument('trxfile')
    parser.add_argument('-o', '--outfilename', help='the output will be written this file')

    return parser.parse_args()



def main():
    args = parse_args()

    song = trax.Song()
    song.load_from_file(args.trxfile)

    bin = trax.compile_song(song)

    with open(args.outfilename, 'wb') as outfile:
        outfile.write(bin)



if __name__ == '__main__':
    main()


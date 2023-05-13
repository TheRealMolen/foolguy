import argparse, os, re, sys



def parse_args():
    parser = argparse.ArgumentParser(description='expands variables in a template with values specified on the command line')
    parser.add_argument('templatefile')
    parser.add_argument('-o', '--outfile', help='the output will be written to OUTFILE')
    parser.add_argument('-D', '--define', action='append')

    return parser.parse_args()

def read_defs(raw_defs):
    defs = dict()

    for raw_def in raw_defs:
        key,val = raw_def.split('=', 1)
        defs[key] = val

    return defs


def replace_defs(infile, outfile, defs):
    template_re = re.compile(r'\{([a-zA-Z_][a-zA-Z_0-9]*)\}')

    linenum = 0
    for line in infile.readlines():
        linenum += 1
        m = template_re.search(line)
        while m:
            defname = m[1]
            if defname not in defs:
                raise Exception(f'failed to find a definition for "{defname}" on line {linenum}')
            
            line = line[:m.start()] + defs[defname] + line[m.end():]
            
            m = template_re.search(line)

        outfile.write(line)


def main():
    args = parse_args()
    defs = read_defs(args.define)

    with open(args.templatefile, "rt") as infile:

        if args.outfile:
            with open(args.outfile, "wt") as outfile:
                replace_defs(infile, outfile, defs)

        else:
            replace_defs(infile, sys.stdout, defs)



if __name__ == '__main__':
    main()
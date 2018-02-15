import argparse, os.path, re

parser = argparse.ArgumentParser(
    description='compare checksums in 2 files'
    )
parser.add_argument("A", help="path to file A")
parser.add_argument("B", help="path to file B")
parser.add_argument("--ext", help="only look at these extension(s), comma seperated. empty for everything")
args = parser.parse_args();

assert os.path.isfile(args.A)
assert os.path.isfile(args.B)

if args.ext:
    exts = args.ext.strip().lower().split(',')
else:
    exts = []

def read_checksum(path_to_checksum_file, exts):
    f = open(path_to_checksum_file, 'r', encoding='utf-8')
    chksums = []
    paths = []
    out = []
    r = re.compile('^([0-9a-f]+)\s+(\S.*\S)\s*$')
    for line in f:
        hit = r.match(line)
        assert hit
        chksum_hex, path = hit.groups(0)
        if exts:
            line_ext = os.path.splitext(line)[1].strip().lower()
            if not line_ext:
                continue # skip for no extension
            if line_ext[1:] not in exts:
                continue
        chksum = int(chksum_hex, 16)
        out.append((chksum, path.strip()))
    f.close()
    return out

A = read_checksum(args.A, exts)
B = read_checksum(args.B, exts)

A_chksum = [i[0] for i in A]
B_chksum = [i[0] for i in B]

# todo: sort checksum and use binary search
# todo: find duplicates
# todo: check for collisions

f = open('A_not_in_B.txt', 'w', encoding='utf-8');
f.write('# in "%s" but not in "%s"\n' % (args.A, args.B))
for chksum, path in A:
    if chksum not in B_chksum:
        if '/@' not in path:
            f.write( '%s\n' % (path) )
f.close()

f = open('B_not_in_A.txt', 'w', encoding='utf-8');
f.write('# in "%s" but not in "%s"\n' % (args.B, args.A))
for chksum, path in B:
    if chksum not in A_chksum:
        if '/@' not in path:
            f.write( '%s\n' % (path) )
f.close()








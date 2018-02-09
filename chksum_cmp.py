import argparse, os.path, re

parser = argparse.ArgumentParser(
    description='compare checksums in 2 files'
    )
parser.add_argument("A", help="path to file A")
parser.add_argument("B", help="path to file B")
args = parser.parse_args();

assert os.path.isfile(args.A)
assert os.path.isfile(args.B)

def read_checksum(path_to_checksum_file):
    f = open(path_to_checksum_file, 'r')
    chksums = []
    paths = []
    out = []
    r = re.compile('^([0-9a-f]+)\s+(\S.*)$')
    for line in f:
        hit = r.match(line)
        assert hit
        chksum_hex, path = hit.groups(0)
        chksum = int(chksum_hex, 16)
        #chksums.append(chksum)
        #paths.append(path.strip())
        out.append((chksum, path.strip()))
    f.close()
    #return (chksums, path)
    return out

A = read_checksum(args.A)
B = read_checksum(args.B)

A_chksum = [i[0] for i in A]
B_chksum = [i[0] for i in B]

f = open('A_not_in_B.txt', 'w');
f.write('# in "%s" but not in "%s"\n' % (args.A, args.B))
for chksum, path in A:
    if chksum not in B_chksum:
        if '/@' not in path:
            f.write( '%s\n' % (path) )
f.close()

f = open('B_not_in_A.txt', 'w');
f.write('# in "%s" but not in "%s"\n' % (args.B, args.A))
for chksum, path in B:
    if chksum not in A_chksum:
        if '/@' not in path:
            f.write( '%s\n' % (path) )
f.close()








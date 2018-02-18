#! /usr/bin/env python3
import platform, argparse, os
parser = argparse.ArgumentParser("delete a list of files")
parser.add_argument('file_list');
args = parser.parse_args()
file_list = args.file_list.strip()
assert os.path.isfile(file_list)
with open(file_list,'r', encoding='utf-8') as f:
    for line in f:
        path = line.partition('#')[0].strip()
        if path:
            if os.path.isfile(path):
                # print('delete this file: "%s"' % path)
                os.remove(path)
            else:
                print('this file does not exist: "%s"' % path)





#! /usr/bin/env python3
import exifread, os, argparse

parser = argparse.ArgumentParser(
    description='find JPEGs whose certain EXIF tag contains certain words'
);
parser.add_argument('--root', 
    help='root directory for the search', 
    default=os.getcwd() 
)
parser.add_argument('--ext', 
    help='file extensions, comma seperated, case insensitive',
    default='jpg,jpeg'
)
parser.add_argument('--tag', 
    help='exif tag to look at, case sensitive',
    default='Image Model'
)
parser.add_argument('--val',
    help='expected values for the tag, comma seperated, OR''ed, case insensitive',
    default='canon,olympus,nikon,sony'
)

args = parser.parse_args();

root_to_walk = args.root.strip()
assert os.path.isdir(root_to_walk), root_to_walk

exts_to_see = args.ext.strip().lower().split(',')

target_tag = args.tag.strip()
assert target_tag, target_tag

target_vals = args.val.strip().lower().split(',')
assert target_vals, target_vals

files_to_process = []

with open('file_list.txt', 'w', encoding='utf-8') as log:
    for root, dirs, files in os.walk(root_to_walk):
        for f in files:
            if (os.path.splitext(f)[1].lower()[1:] in exts_to_see) or (not exts_to_see):
                full_path = os.path.join(root, f)
                files_to_process.append( full_path )
                log.write( full_path + '\n')

def process_files(file_list, tar_tag, tar_vals):
    file_hits = []
    file_notag = []
    candidates = []
    for path in file_list:
        with open(path, 'rb') as f:
            tags = exifread.process_file(
                f, 
                details=False, 
                stop_tag=tar_tag
                );
            if tar_tag in tags.keys():
                val = str(tags[tar_tag]).lower().strip()
                if val not in candidates:
                    candidates.append(val)
                for tar_val in tar_vals:
                    if tar_val in val:
                        file_hits.append(path)
                        break
            else:
                file_notag.append(path)
    with open('candidates.txt', 'w', encoding='utf-8') as f:
        for line in candidates:
            f.write(line + '\n')
    return (file_hits, file_notag)

hits, notags = process_files(files_to_process, target_tag, target_vals)

with open('hits.txt','w', encoding='utf-8') as f:
    f.write(
        '# these files are "%s" in "%s" with at least one of "%s" in its exif tag "%s" \n' % 
        (exts_to_see, root_to_walk, target_vals, target_tag) 
    )
    for path in hits:
        f.write(path)
        f.write('\n')

with open('notags.txt','w', encoding='utf-8') as f:
    f.write(
        '# these files are "%s" in "%s" with no exif tag "%s" \n' % 
        (exts_to_see, root_to_walk, target_tag) 
    )
    for path in notags:
        f.write(path)
        f.write('\n')



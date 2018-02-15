import argparse, subprocess, os, platform

parser = argparse.ArgumentParser(
    description='generate '
    )
parser.add_argument("file_list", help="list of files to be adb-pushed")
parser.add_argument("--target_path", help="path on android device",
    default="/sdcard/pics_to_upload")
args = parser.parse_args();

assert os.path.isfile(args.file_list)

cwd = os.getcwd()

with open(args.file_list) as f:
    for line in f:
        if not line.startswith('#'):
            line = line.strip()
            if platform.system() is 'Windows':
                line_host = line.replace('/', '\\')
            else:
                line_host = line
            if os.path.isfile(line):
                cmd = 'adb push "%s" "%s"' % (
                    os.path.join(cwd, line_host), 
                    os.path.join(args.target_path, line).replace('\\','/'))
                subprocess.call(cmd)
            else:
                print('this line does not point to a file %s' % line)
            
        
    

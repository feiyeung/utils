#!/usr/bin/env python
# Feiyang Xue
# example: echo "hello world" | python my_email.py

import sys, datetime, argparse, re, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from_addr = 'your_email@drexel.edu' # sender's email
to_addr = 'your_email@drexel.edu' # recipient's email
subject = 'Whatever Subject You Like %s' % datetime.datetime.now()

parser = argparse.ArgumentParser()
parser.add_argument('--addrfrom', type=str,
        help='email address of both sender and receiver')
parser.add_argument('--addrto', type=str,
        help='email address of both sender and receiver')
parser.add_argument('--subj', type=str,
        help='email subject')
args = parser.parse_args()

if args.addrfrom:
    from_addr = args.addrfrom
if args.addrto:
    to_addr = args.addrto
if args.subj:
    subject = args.subj

re_email = re.compile('^[^@]+@[\S\.]+\.[a-zA-Z]+$')
assert re_email.match(from_addr), from_addr
assert re_email.match(to_addr), to_addr

# prepare HTML parts
html_header = """
<html>
<body>
<pre style="font: monospace">
<span class="inner-pre" style="font-size: 12px">
"""
html_footer = """
</span>
</pre>
</body>
</html>
"""
html_msg = ''
html_msg += html_header
for line in sys.stdin:
    html_msg += line 
html_msg += html_footer

# assemble the message
msg = MIMEMultipart('alternative')
msg['Subject'] = subject
msg['From'] = from_addr
msg['To'] = to_addr
msg.attach(MIMEText(html_msg, 'html'))
print('*************\nthis message: \n%s\n*************\n' % msg.as_string())

# send it out
mySMTP = smtplib.SMTP('smtp.mail.drexel.edu')
# mySMTP.set_debuglevel(1)
mySMTP.sendmail(from_addr, to_addr, msg.as_string())
mySMTP.quit()

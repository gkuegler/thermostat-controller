"""
Install 'arping'
Install 'arp-scan'

#!/usr/bin/env python
import subprocess

sudo_password = 'mysecretpass'
command = 'apach2ctl restart'
command = command.split()

cmd1 = subprocess.Popen(['echo',sudo_password], stdout=subprocess.PIPE)
cmd2 = subprocess.Popen(['sudo','-S'] + command, stdin=cmd1.stdout, stdout=subprocess.PIPE)

output = cmd2.stdout.read().decode() 

Possible Solution:
sudo arp-scan -l -r 3 | grep {Phone Static Assigned IP} 

Other Solution:
proc = Popen("sudo -S apach2ctl restart".split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
# Popen only accepts byte-arrays so you must encode the string
proc.communicate(password.encode())

RESULT:
I think it's best if I wrap my sudo commands in a different service?
Write out data to a file (with seq record #'s to idenify stale data)
and consume from non-sudo processes.
"""

import subprocess
import regex

p = subprocess.run(["sudo", "arp-scan", "-l", "-r", "4"],
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE)

if "10.0.0.188" in p.stdout.decode():
    print("Device Connected!")
else:
    print("Disconnected")

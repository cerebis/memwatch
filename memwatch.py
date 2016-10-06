#!/bin/env python
"""
MIT License

Copyright (c) 2016 Matthew DeMaere

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import time
import psutil
import argparse

parser = argparse.ArgumentParser(description='Monitor process resident memory')
parser.add_argument('-s', '--size', choices=['k', 'm', 'g', 'K', 'M', 'G'], default='m', help='Reported units (kB, MB, GB) [m]')
parser.add_argument('-w', '--wait', type=int, default=3, help='Wait time in seconds [3]')
parser.add_argument('PID', type=int, help='Process ID')

args = parser.parse_args()

proc = psutil.Process(args.PID)

if args.size.lower() == 'k':
    blsz = 1024
    unit = 'kB'
elif args.size.lower() == 'm':
    blsz = 1024**2
    unit = 'MB'
elif args.size.lower() == 'g':
    blsz = 1024**3
    unit = 'GB'

def get_rss(proc):
    return proc.memory_info().rss

peak = {}
rss = {}
while True:
    rss[proc.pid] = get_rss(proc)
    if rss[proc.pid] > peak.setdefault(proc.pid, 0):
        peak[proc.pid] = rss[proc.pid]
        
    for cp in proc.children():
        rss[cp.pid] = get_rss(cp)
        if rss[cp.pid] > peak.setdefault(cp.pid, 0):
            peak[cp.pid] = rss[cp.pid]

    pid_srt = sorted(rss.keys())
    print ', '.join('pid:{0} rss:{1} peak:{2} {3}'.format(pi, rss[pi] // blsz, peak[pi] // blsz, unit)  for pi in pid_srt)

    time.sleep(args.wait)

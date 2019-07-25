#!/usr/bin/env python3

import glob
import os
import subprocess
import time

def find_dirs_to_reduce():
  return [f for f in glob.glob("repro-*")]

while True:
  dirs = find_dirs_to_reduce()
  print("Found folders to reduce: " + str(dirs))
  for d in dirs:
    os.system("bash " + d + "/creduce.sh")
    os.rename(d, "reduced-" + d)
  time.sleep(10)

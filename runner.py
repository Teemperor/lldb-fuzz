#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys
import time
import random

import itertools
spinner = itertools.cycle(['-', '/', '|', '\\'])

clang_res = subprocess.run(["clang++", "-g", "-std=c++11", "test.cpp", "-o", "tt"])

if clang_res.returncode != 0:
  print("Error: Clang failed")
  exit(1)

lldb = sys.argv[1]

def make_repro(seed, time):
  print("Crashed, creating reproducer...")
  repro_folder = "repro-" + hex(seed)[2:] + "/"
  os.makedirs(repro_folder)
  shutil.copyfile("test.cpp", repro_folder + "test.cpp")
  pp_res = subprocess.run(["clang++", "-g", "-std=c++11", "test.cpp",
                           "-E", "-o", repro_folder + "test_pp.cpp"])
  shutil.copyfile("fuzz.py", repro_folder + "fuzz.py")

  repro_script = """
#!/bin/bash
set -e
clang++ -g -std=c++11 test.cpp -o tt
$1 ./tt -o "command script import fuzz.py" -o "fuzz """ + str(seed) + """"
"""
  with open(repro_folder + "repro.sh", "w") as f:
    f.write(repro_script)

  test_script = ("""#!/bin/bash
set -e
clang++ -g -std=c++11 test_pp.cpp -o tt
rm -f err.log
set +e
{ lldb ./tt -o "command script import fuzz.py" -o "fuzz """ + str(seed) +
"""" ; } 2>err.log >/dev/null
grep -Fxq "Assertion failed:" err.log
""")
  with open(repro_folder + "test.sh", "w") as f:
    f.write(test_script)

  git_res = subprocess.run(["git", "-C", repro_folder, "init"])
  if git_res.returncode != 0:
    return
  git_res = subprocess.run(["git", "-C", repro_folder, "add",
                            "test.cpp", "test.sh", "repro.sh", "fuzz.py",
                            "test_pp.cpp"])
  if git_res.returncode != 0:
    return

  git_res = subprocess.run(["git", "-C", repro_folder, "commit", "-m", "Init"])
  if git_res.returncode != 0:
    return
  print("Created reproducer")



while True:
  seed = random.randint(0, 9999999999)
  timed_out = False
  start = time.time()
  try:
    lldb_res = subprocess.run([lldb, "./tt", "-o",
                               "command script import fuzz.py", "-o",
                               "fuzz " + str(seed), "-b"],
                               stdout=subprocess.DEVNULL, timeout=30)
  except subprocess.TimeoutExpired:
    print("Seed caused timeout: " + str(seed))
    timed_out = True
  end = time.time()

  sys.stdout.write('\b')            # erase the last written char
  sys.stdout.write(next(spinner))  # write the next character
  sys.stdout.flush()                # flush stdout buffer (actual character display)

  if lldb_res.returncode < 0 or timed_out:
    print("")
    make_repro(seed, str(int(end - start)))

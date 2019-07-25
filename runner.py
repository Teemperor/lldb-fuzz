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
  repro_folder = "repro-" + hex(seed)[2:] + "/"
  print("Creating reproducer: " + repro_folder)
  os.makedirs(repro_folder)
  shutil.copyfile("test.cpp", repro_folder + "test.cpp")
  pp_res = subprocess.run(["clang++", "-g", "-std=c++11", "test.cpp",
                           "-E", "-o", repro_folder + "test_pp.cpp"])
  shutil.copyfile("fuzz.py", repro_folder + "fuzz.py")

  repro_folder_full_path = os.path.abspath(repro_folder)

  repro_script = """
#!/bin/bash
set -e
clang++ -g -std=c++11 test_pp.cpp -o tt
$1 ./tt -o "command script import fuzz.py" -o "fuzz """ + str(seed) + """"
"""
  with open(repro_folder + "repro.sh", "w") as f:
    f.write(repro_script)

  creduce_script = """
#!/bin/bash
set -e
cd "$(dirname "$0")"
chmod +x test.sh
creduce ./test.sh test_pp.cpp --n 1 --timeout 30
"""
  with open(repro_folder + "creduce.sh", "w") as f:
    f.write(creduce_script)

  test_script = ("""#!/bin/bash
set -e
clang++ -g -std=c++11 test_pp.cpp -o tt
set +e
rm -f err.log
{ export LLDB_UNDER_CREDUCE=1 ; """ + lldb + """ ./tt -o "command script import """ + repro_folder_full_path + """/fuzz.py" -o "fuzz """ + str(seed) +
"""" ; } 2>err.log >std.log
grep -Fq "Assertion failed:" err.log
""")
  with open(repro_folder + "test.sh", "w") as f:
    f.write(test_script)

  print("Creating git repo")
  git_res = subprocess.run(["git", "-C", repro_folder, "init"], stdout=subprocess.DEVNULL)
  if git_res.returncode != 0:
    return
  git_res = subprocess.run(["git", "-C", repro_folder, "add",
                            "test.cpp", "test.sh", "repro.sh", "fuzz.py",
                            "test_pp.cpp"], stdout=subprocess.DEVNULL)
  if git_res.returncode != 0:
    return

  git_res = subprocess.run(["git", "-C", repro_folder, "commit", "-m", "Init"], stdout=subprocess.DEVNULL)
  if git_res.returncode != 0:
    return
  print("Created reproducer")

  if False: #Disable automatically running creduce for now.
    git_res = subprocess.run(["bash", repro_folder + "creduce.sh"])
    if git_res.returncode != 0:
      return

run_env = os.environ.copy()
run_env["LLDB_UNDER_CREDUCE"] = "1"


while True:
  seed = random.randint(0, 9999999999)
  timed_out = False
  start = time.time()

  try:
    lldb_res = subprocess.run([lldb, "./tt", "-o",
                               "command script import fuzz.py", "-o",
                               "fuzz " + str(seed), "-b"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               timeout=30, env=run_env)
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

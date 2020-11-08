import lldb
import random

fuzz_rand = random.Random()

def add_suffix(s, suffix):
  parts = s.split(" ")
  if suffix.startswith(parts[-1]):
    cut_off = -len(parts[-1])
    if cut_off == 0:
      return s + suffix

    return s[:cut_off] + suffix
  return s + suffix

class StepAndPrint:
    def __init__(self, debugger, unused):
        return

    def __call__(self, debugger, command, exe_ctx, result):
        # Set the command to synchronous so the step will complete
        # before we try to run the frame variable.
        old_async = debugger.GetAsync()
        debugger.SetAsync(False)

        if len(command):
          seed = int(command)
          print("Using seed: " + str(seed))
          fuzz_rand = random.Random(seed)

        debugger.HandleCommand("b main")
        debugger.HandleCommand("run")

        debugger.HandleCommand("settings set target.process.thread.step-avoid-regexp \"\"")


        for i in range(0, fuzz_rand.randrange(300) + 5):
          debugger.HandleCommand("s")


        if fuzz_rand.randrange(10) <= 1:
          res = lldb.SBCommandReturnObject()
          interp.HandleCommand("bt", res)

        cmd = "expr "
        for k in range(3, fuzz_rand.randrange(10)):
          interp = debugger.GetCommandInterpreter()
          match_strings = lldb.SBStringList()
          desc_strings = lldb.SBStringList()
          num_matches = interp.HandleCompletionWithDescriptions(cmd, len(cmd), 0, -1, match_strings, desc_strings)

          if num_matches == 0:
            cmd += fuzz_rand.choice(["+", "-", "*", " = ", "/", ";"])
            continue

          selected = 0
          while len(desc_strings.GetStringAtIndex(selected)) == 0:
            selected = fuzz_rand.randrange(num_matches)
            if fuzz_rand.uniform(0.0, 1.0) < 0.01:
              break

          new_end = match_strings.GetStringAtIndex(selected)

          if len(new_end) != 0:
            if new_end.endswith("("):
              new_end += fuzz_rand.choice([").", ")->", " "])
            else:
              new_end += fuzz_rand.choice(["->", ".", " "])

          cmd = add_suffix(cmd, new_end)
          print("Adding: '" + new_end + "'")
          print("Command: '" + cmd + "'")

        debugger.SetAsync(old_async)

    def get_short_help(self):
        return "Fuzzed lldb expr completion"

def __lldb_init_module(debugger, unused):
    debugger.HandleCommand("command script add -c fuzz.StepAndPrint fuzz")

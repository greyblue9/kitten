#!/usr/bin/env python3

import pprint
from pathlib import Path
import sys
sys.path.insert(0, (Path.cwd()/"alice").as_posix())
import aiml.AimlParser
  
def main():
  k = aiml.Kernel()
  k.bootstrap(None, list(map(Path.as_posix, Path("./").glob("**/*.aiml"))));
  while ln := input("> "):
    print(f"\nyou: {ln}\n   >> {k.respond(ln)}")

if __name__ == "__main__":
  main()

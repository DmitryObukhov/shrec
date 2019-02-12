#!/usr/bin/env python3

import os
from swissknife import Shell as sh
from swissknife import Text as tx

def ab_merge():
    flist = sh.find_files('*.mp3')
    tx.print(flist,'    ','-------- Files -----------')
#---


def main():
    """ main function """
    import argparse
    parser = argparse.ArgumentParser(description="Shell Receipe", formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--debug", action="store_true", default=False, help="Debug execution mode")
    parser.add_argument("--quiet", action="store_true", default=False, help="Quiet execution mode")
    args = parser.parse_args()
    ab_merge()
#---

if __name__ == "__main__":
    main()
#---

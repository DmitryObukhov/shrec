#!/usr/bin/python
""" SHell RECipe: """
from __future__ import print_function
import argparse
from shellwrapper import ShellWrapper
__author__ = "29250"

def main():
    """ main function """
    parser = argparse.ArgumentParser(description="Shell Receipe", formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--debug", action="store_true", default=False, help="Debug execution mode")
    parser.add_argument("--quiet", action="store_true", default=False, help="Quiet execution mode")
    args = parser.parse_args()

    # Create shell wrapper and perform necessary commands
    batch = ShellWrapper(args.debug, args.quiet, "auto")
    # put your code here. For example, batch.run("ping 127.0.0.1")
    flist = batch.find_files('*.*')
    batch.prntxt(flist,'    ','-------- Files -----------')
    batch.exit(0) # batch.exit terminates the script
#---

if __name__ == "__main__":
    main()
#---


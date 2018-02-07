#!/usr/bin/env python
""" SHell RECipe: """
from __future__ import print_function
import argparse
import getpass
from shellwrapper import ShellWrapper
__author__ = "29250"

def main():
    """ main function """
    parser = argparse.ArgumentParser(description="Shell Receipe", formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--debug", action="store_true", default=False, help="Debug execution mode")
    parser.add_argument("--quiet", action="store_true", default=False, help="Quiet execution mode")
    parser.add_argument("script", action="store", default='', nargs='?', help="Template file")
    args = parser.parse_args()

    # Create shell wrapper and perform necessary commands
    batch = ShellWrapper(args.debug, args.quiet, "auto")

    template_script = [ \
            "#!/usr/bin/env python", \
            '""" SHell RECipe: """', \
            'from __future__ import print_function', \
            'import argparse', \
            "from shellwrapper import ShellWrapper", \
            '__author__ = "%s"' % getpass.getuser(), \
            '', \
            'def main():', \
            '    """ main function """', \
            '    parser = argparse.ArgumentParser(description="Shell Receipe", formatter_class=argparse.RawDescriptionHelpFormatter)', \
            '    parser.add_argument("--debug", action="store_true", default=False, help="Debug execution mode")', \
            '    parser.add_argument("--quiet", action="store_true", default=False, help="Quiet execution mode")', \
            '    args = parser.parse_args()', \
            '', \
            '    # Create shell wrapper and perform necessary commands', \
            '    batch = ShellWrapper(args.debug, args.quiet, "auto")', \
            '    # put your code here. For example, batch.run("ping 127.0.0.1")', \
            '    batch.exit(0) # batch.exit terminates the script', \
            '#---', \
            '', \
            'if __name__ == "__main__":', \
            '    main()', \
            '#---', \
            "" \
        ]
    #---
    if args.script == '':
        batch.prntxt(template_script)
    else:
        batch.save(template_script, args.script)
    #---
    batch.exit(0) # batch.exit terminates the script
#---

if __name__ == "__main__":
    main()
#---


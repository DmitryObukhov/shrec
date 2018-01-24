#!/usr/bin/python
""" SHell RECipes module """
from __future__ import print_function

import os
#import re
import argparse

#from shrec import TextProcessor
#from shrec import BatchProcessor
from textprocessor import TextProcessor
from batchprocessor import BatchProcessor
from shrecunittest import TextProcessorUnitTest
from recipes import ShellRecipes
#from shrecunittest import BatchProcessorUnitTest

__author__ = 'dmitry.obukhov'


def main():
    """ main function to parse arguments """
    exit_code = -1
    parser = argparse.ArgumentParser(description="Shell Receipes Engine", \
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    # Global arguments
    parser.add_argument('--debug', action='store_true', default=False, help='Debug execution mode')
    parser.add_argument('--quiet', action='store_true', default=False, help='Quiet execution mode')

    subparsers = parser.add_subparsers(help='Supported commands', dest='command')

    setup_parser = subparsers.add_parser('setup', help='Setup Python module')
    install_parser = subparsers.add_parser('install', help='Install shrec as system utility')
    utest_parser = subparsers.add_parser('unittest', help='Unit test the module')
    debug_parser = subparsers.add_parser('debug', help='Debug new code')
    recipe_parser = subparsers.add_parser('recipe', help='System configuration recipes')

    recipe_subparser = recipe_parser.add_subparsers(help='Recipes', dest='recipe')

    r001d = recipe_subparser.add_parser('enablerootssh',    help='Enable root ssh')
    r001n = recipe_subparser.add_parser('disablerootssh',   help='Disable root ssh')
    r002d = recipe_subparser.add_parser('enablepm',         help='Enable power management')
    r002n = recipe_subparser.add_parser('disablepm',        help='Disable power management')
    r003d = recipe_subparser.add_parser('enableip6',        help='Enable support of IP v.6')
    r003n = recipe_subparser.add_parser('disableip6',       help='Disable support of IP v.6')
    r004d = recipe_subparser.add_parser('enabletcg',        help='Enable support of TCG storage')
    r004n = recipe_subparser.add_parser('disabletcg',       help='Disable support of TCG storage')

    r005  = recipe_subparser.add_parser('sethostname',      help='Set hostname from MAC or Random')
    r005.add_argument('--naming', action='store', default='mac', help='Naming: {mac,rnd}')

    args = parser.parse_args()

    if args.command == 'setup':
        batch = BatchProcessor(args.debug, args.quiet, "auto")
        setup_script = [ \
                "#!/usr/bin/env python", \
                "from distutils.core import setup", \
                "setup(name='shrec',version='0.2',", \
                "      description='Script Helper',", \
                "      py_modules=['shrec'])", \
                "" \
            ]
        #---
        TextProcessor.save(setup_script, 'temp_setup.py')
        batch.run('python temp_setup.py install')
        os.remove('temp_setup.py')
        TextProcessor.Print(batch.cout, '', '-- installation log --')
        batch.exit(0)
    #--

    if args.command == 'unittest':
        exit(TextProcessorUnitTest())
    #--

    if args.command == 'recipe':
        shr = ShellRecipes(args.debug, args.quiet)

        if args.recipe == 'enablerootssh':
            exit(shr.enable_root_ssh())
        #---

        if args.recipe == 'disablerootssh':
            exit(shr.disable_root_ssh())
        #---

        if args.recipe == 'sethostname':
            exit(shr.set_hostname())
        #---
    #--

    print ("Unhandled command %s" % args.command)
    exit(0)
#---


if __name__ == "__main__":
    main()
#---

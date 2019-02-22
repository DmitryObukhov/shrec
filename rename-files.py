#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    Universal code module
"""
import os
import re
from swissknife import Text  as tx
from swissknife import Shell as sh

def translit_folder(args):
    for dir in args['dir']:
        sh.transliterate_folder(dir)
    #---
#---

def norm_folder(args):
    for dir in args['dir']:
        sh.normalize_names(args['mask'],dir)
    #---
#---


def flat_folder(args):
    for dir in args['dir']:
        sh.flat_folder(dir,separator=args['separator'])
    #---
#---

def detrack_folder(args):
    flist = sh.find_files('*.*', args['dir'])
    for name in flist:
        (p,n,e) = sh.fname_split(name, ret_tuple=True)
        nn = re.sub('^[\d\.\s\-]+','',n)
        if n != nn:
            newname = p + '/' + nn + e
            os.rename(name,newname)
        #---
    #---

    # for dir in args['dir']:
    #     sh.detrack_folder('*.*', dir)
    # #---
#---



def main():
    """ main function """
    import argparse
    parser = argparse.ArgumentParser(description="Mass rename files")
    parser.add_argument("--debug", action="store_true", default=False, help="Debug execution mode")
    parser.add_argument("--quiet", action="store_true", default=False, help="Quiet execution mode")

    subparsers = parser.add_subparsers(help='Operations', dest='operation')

    t_parser = subparsers.add_parser("translit")
    t_parser.add_argument('dir', default='.', nargs='*')

    f_parser = subparsers.add_parser("flat")
    f_parser.add_argument('--separator', default='__', help="Default separator" )
    f_parser.add_argument('dir', default='.', nargs='*')

    n_parser = subparsers.add_parser("norm")
    n_parser.add_argument('--mask', default='*.*', help="Search mask, default is *.*" )
    n_parser.add_argument('dir', default='.', nargs='*')

    a_parser = subparsers.add_parser("all")
    a_parser.add_argument('--separator', default='__', help="Default separator" )
    a_parser.add_argument('--mask', default='*.*', help="Search mask, default is *.*" )
    a_parser.add_argument('dir', default='.', nargs='*')

    d_parser = subparsers.add_parser("detrack")
    d_parser.add_argument('dir', default=os.getcwd(), nargs='*')


    args = vars(parser.parse_args())
    if args['debug']:
        tx.print(args)
    #---

    """
        {
            "debug": false,
            "quiet": false,
            "operation": "flat",
            "delimiter": null,
            "dir": "."
        }
    """
    if args['operation'] == 'flat':
        return flat_folder(args)
    #---
    if args['operation'] == 'norm':
        return norm_folder(args)
    #---
    if args['operation'] == 'translit':
        return translit_folder(args)
    #---
    if args['operation'] == 'detrack':
        return detrack_folder(args)
    #---

    if args['operation'] == 'all':
        flat_folder(args)
        translit_folder(args)
        norm_folder(args)
    #---

#---

if __name__ == "__main__":
    main()
#---

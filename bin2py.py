#!/usr/bin/env python
""" SHell RECipe: """
#from __future__ import print_function
import argparse
import zlib
import hashlib
import base64

from shellwrapper import ShellWrapper

def fold(long_str, width=80):
    """  longStr --> [str1,str2,str3] """
    ret_val = []
    tmp = long_str
    while tmp != '':
        cur = ''
        if len(tmp) > width:
            cur = tmp[0:width]
            tmp = tmp[width:]
        else:
            cur = tmp
            tmp = ''
        #---
        ret_val.append(cur)
    #---
    return ret_val
#---


def gen_pybin(export_data, obj_name, default_file_name):
    """ Generate script to restore binary file """
    script_file = open(obj_name+'.py', 'wt')
    script_file.write("#!/usr/bin/python\n")
    script_file.write('""" This is automatically generated script to create file %s. Do not edit! """\n' % default_file_name)
    script_file.write("__all__ = ['Extract']\n")
    script_file.write("\n")
    script_file.write("# Usage:\n")
    script_file.write("#     import %s\n" % obj_name)
    script_file.write("#     %s.Extract()\n" % obj_name)
    script_file.write("# or in command line\n")
    script_file.write("#     python %s [fileName]\n" % obj_name)
    script_file.write("\n")
    script_file.write("import zlib\n")
    script_file.write("import binascii\n")
    script_file.write("import hashlib\n")
    script_file.write("import base64\n")
    script_file.write("import sys\n")
    script_file.write("\n")
    script_file.write("def Extract(fileName='%s'):\n" % default_file_name)
    script_file.write("    binObject=''\n")

    data_array = fold(export_data, 100)

    for blk in data_array:
        script_file.write("    binObject+='%s'\n" % blk)
    #---

    script_file.write("    decoded = base64.b64decode(binObject)\n")
    script_file.write("    decompressed = zlib.decompress(decoded)\n")
    script_file.write("    f = open(fileName, 'wb')\n")
    script_file.write("    f.write(decompressed)\n")
    script_file.write("    f.flush()\n")
    script_file.write("    f.close()\n")
    script_file.write("#---\n")
    script_file.write("\n")
    script_file.write("if __name__ == '__main__':\n")
    script_file.write("    import argparse\n")
    script_file.write("    parser = argparse.ArgumentParser()\n")
    script_file.write("    parser.add_argument('--file',\n")
    script_file.write("                        action='store',\n")
    script_file.write("                        default='%s',\n" % default_file_name)
    script_file.write("                        help='Export file name')\n")
    script_file.write("    args = parser.parse_args()\n")
    script_file.write("    Extract(args.file)\n")
    script_file.write("#---\n")
    script_file.write("\n")
#---



def bin2py(bin_file_name, py_object_name):
    """ Generate Python script to restore binary file """
    try:
        original_data = open(bin_file_name, 'rb').read()
        compressed = zlib.compress(original_data)
        encoded = base64.b64encode(compressed).decode('utf-8')
        gen_pybin(encoded, py_object_name, bin_file_name)
        return 0
    except IOError:
        print("Error: IOError")
    except OSError:
        print("Error: OSError")
    #---
    return -1
#---




if __name__ == "__main__":
    """ main function """
    parser = argparse.ArgumentParser(description="Shell Receipe", formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--debug", action="store_true", default=False, help="Debug execution mode")
    parser.add_argument("--quiet", action="store_true", default=False, help="Quiet execution mode")
    parser.add_argument("bin",     action="store",                     help="Input file")
    parser.add_argument("py",      action="store",                     help="Output script")
    args = parser.parse_args()

    exit(bin2py(args.bin, args.py))
#---

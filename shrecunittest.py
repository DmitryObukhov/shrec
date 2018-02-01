#!/usr/bin/python
""" SHell RECipes unit test module """
from __future__ import print_function
from shellwrapper import ShellWrapper

def main():
    errorCount = 0
    shw = ShellWrapper(True, False, 'auto')
    print_template = "%s, %d, %s"

    tested_function = 'quoted_string'
    test_case = 1
    expected_result = '"abc"'
    actual_result = shw.quoted_string('abc')
    if actual_result == expected_result:
        print (print_template % (tested_function, test_case, 'PASS'))
    else:
        print (print_template % (tested_function, test_case, 'FAIL'))
        errorCount += 1
    #---

    return -1 * errorCount
#---

if __name__ == "__main__":
    exit(main())
#---

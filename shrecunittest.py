#!/usr/bin/python
""" SHell RECipes unit test module """
from __future__ import print_function
import re
import hashlib
from shellwrapper import ShellWrapper

def TestCompareByPattern(wrapper, function_name, test_case_num, expected_pattern, actual_result ):
    ret_val = 0
    print_template = "%s: %03d, %s"
    actual_result_str = "%s" % actual_result
    if re.match(expected_pattern, actual_result_str):
        print (print_template % ('PASS', test_case_num, function_name))
    else:
        print (print_template % ('FAIL', test_case_num, function_name))
        print ("    %s != %s" % (actual_result, expected_pattern))
        ret_val += 1
    #---
    return ret_val
#---


def TestStringConversion(wrapper, function_name, test_case_num, expected_result, test_input ):
    ret_val = 0
    print_template = "%s: %03d, %s"
    method_to_call = getattr(ShellWrapper, function_name)
    actual_result = method_to_call(test_input)
    if actual_result == expected_result:
        print (print_template % ('PASS', test_case_num, function_name))
    else:
        print (print_template % ('FAIL', test_case_num, function_name))
        print ("    %s --> %s, expected %s" % (test_input, actual_result, expected_result))
        ret_val += 1
    #---
    return ret_val
#---

def TestTextConversion(wrapper, function_name, test_case_num, expected_text, test_input ):
    ret_val = 0
    print_template = "%s: %03d, %s"
    method_to_call = getattr(ShellWrapper, function_name)
    actual_result = method_to_call(test_input)

    delta = set(actual_result) ^ set(expected_text)

    if delta != None and len(delta)>0:
        print (print_template % ('FAIL', test_case_num, function_name))
        print ("    %s --> %s, expected %s" % (test_input, actual_result, expected_text))
        ret_val += 1
    else:
        print (print_template % ('PASS', test_case_num, function_name))
    #---
    return ret_val
#---

def CompareTextLists(wrapper, function_name, test_case_num, expected_text, actual_text ):
    ret_val = 0
    print_template = "%s: %03d, %s"

    delta = set(actual_text) ^ set(expected_text)

    if delta != None and len(delta)>0:
        print (print_template % ('FAIL', test_case_num, function_name))
        print ("    %s != %s" % (actual_text, expected_text))
        ret_val += 1
    else:
        print (print_template % ('PASS', test_case_num, function_name))
    #---
    return ret_val
#---



def TestFileOperations(wrapper, function_name, test_case_num, file_name, expected_hash ):
    hasher = hashlib.md5()
    ret_val = 0
    print_template = "%s: %03d, %s"
    with open(file_name, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    #--
    actual_hash = hasher.hexdigest()
    if  actual_hash == expected_hash:
        print (print_template % ('PASS', test_case_num, function_name))
    else:
        print (print_template % ('FAIL', test_case_num, function_name))
        print ("    %s --> %s" % (file_name, actual_hash))
        ret_val += 1
    #---
    return ret_val
#---

def dummy(x):
    return "%s" % (x * 2)
#---

def stack_depth_plus_2(shw):
    return shw._call_stack_depth()
#---

def stack_depth_plus_1(shw):
    cur1 = shw._call_stack_depth()
    cur2 = stack_depth_plus_2(shw)
    return (cur1,cur2)
#---



def main():
    err_count = 0
    shw = ShellWrapper(False, False, 'auto')
    err_count += TestStringConversion(shw,  'quoted_string',        1, '"abc"', 'abc')
    err_count += TestStringConversion(shw,  'quoted_string',        2, '""abc""', '"abc"')
    err_count += TestStringConversion(shw,  'one_dir_up',           1, 'a/b/c', 'a/b/c/d.e')
    err_count += TestStringConversion(shw,  'one_dir_up',           1, 'a/b', 'a/b/c')

    err_count += TestStringConversion(shw,  'fname_path',           1, 'a/b/c', 'a/b/c/d.e')
    err_count += TestStringConversion(shw,  'fname_name',           1, 'd', 'a/b/c/d.e')
    err_count += TestStringConversion(shw,  'fname_ext',            1, 'e', 'a/b/c/d.e')

    


    err_count += TestCompareByPattern(shw,  'timestamp',            1, '\d\d\d\d_\d\d_\d\d_\d\d\d\d\d\d', shw.timestamp())
    err_count += TestCompareByPattern(shw,  'random_string',        1, '....', shw.random_string(4))
    err_count += TestCompareByPattern(shw,  'random_string',        2, '\d\d\d\d', shw.random_string(4,'0123456789'))
    err_count += TestTextConversion(shw,    'rstrip_all',           1, ['a','b','c'], ['a  ','b\n\n','c\r'])
    err_count += TestTextConversion(shw,    'remove_empty_lines',   1, ['a ',' ','c'], ['a ',' ','','c'])

    err_count += TestCompareByPattern(shw,  'unify_length',        1, 'abcde',  shw.unify_length('abcde'))
    err_count += TestCompareByPattern(shw,  'unify_length',        2, 'abcde',  shw.unify_length('abcde',-1,-1,' '))
    err_count += TestCompareByPattern(shw,  'unify_length',        3, 'abc',    shw.unify_length('abcde',3))
    err_count += TestCompareByPattern(shw,  'unify_length',        4, 'abc   ', shw.unify_length('abcde',3,6))
    err_count += TestCompareByPattern(shw,  'unify_length',        5, 'abc---', shw.unify_length('abcde',3,6,'-'))


    f_name = 'res.tmp'
    text = ['1', '2', '3']
    shw.save(text, f_name)
    err_count += TestFileOperations(shw, 'save', 1, f_name, 'b0778a411c26f7b9b9ef5db8ed99566e')

    extratext = ['4', '', '5']
    shw.append(extratext, 'res.tmp')
    err_count += TestFileOperations(shw, 'append', 1, f_name, '86f74b3e9ca9fbfbf0e37da6021c7ac7')

    content = []
    content.extend(text)
    content.extend(extratext)
    actual_text = shw.read(f_name)
    expected_text = ['1', '2', '3', '4', '5']
    discrepancies = set(actual_text) ^ set(expected_text)
    if (discrepancies != None) and (len(discrepancies)>0):
        err_count += 1
        print("FAIL: 001, read")
        print('    Expected text: %s' % expected_text)
        print('    Actual text: %s' % actual_text)
    else:
        print("PASS: 001, read")
    #---

    actual_text = shw.read(f_name, clean=False)
    expected_text = ['1\n', '2\n', '3\n', '4\n', '\n', '5\n']
    discrepancies = set(actual_text) ^ set(expected_text)
    if (discrepancies != None) and (len(discrepancies)>0):
        err_count += 1
        print("FAIL: 002, read")
        print('    Expected text: %s' % expected_text)
        print('    Actual text: %s' % actual_text)
    else:
        print("PASS: 002, read")
    #---


    err_count += CompareTextLists(shw, 'fold',      1, ['a'*80, 'b'*80, 'c'*80],       shw.fold('a'*80 + 'b'*80 + 'c'*80))
    err_count += CompareTextLists(shw, 'fold',      2, ['aaa', 'bbb', 'ccc'],          shw.fold('aaabbbccc', 3))

    err_count += CompareTextLists(shw, 'replace_all', 1, ['a','ddd','c'],       shw.replace_all(['a','b','c'],'b','ddd'))
    err_count += CompareTextLists(shw, 'replace_all', 2, ['ddd','ddd','ddd'],   shw.replace_all(['a','b','c'],'.','ddd'))
    err_count += CompareTextLists(shw, 'replace_all', 3, ['ddd','ddd','ddd'],   shw.replace_all(['a','b','c'],r'\w','ddd'))

    err_count += CompareTextLists(shw, 'remove_duplicates', 1, ['a','b','c'],   shw.remove_duplicates(['a','b','c','b','a']))

    err_count += CompareTextLists(shw, 'each_line', 1, ['aa','bb','cc'],   shw.each_line(['a','b','c'], dummy))

    err_count += TestCompareByPattern(shw,  'maxlen',        1, '3', shw.maxlen(['a','bbb','c']))
    err_count += TestCompareByPattern(shw,  'maxlen',        2, '3', shw.maxlen(['a','b','ccc']))
    err_count += TestCompareByPattern(shw,  'maxlen',        3, '3', shw.maxlen(['aaa','b','c']))

    err_count += TestCompareByPattern(shw,  'longest_line',        1, 'bbb', shw.longest_line(['a','bbb','c']))
    err_count += TestCompareByPattern(shw,  'longest_line',        2, 'ccc', shw.longest_line(['a','b','ccc']))
    err_count += TestCompareByPattern(shw,  'longest_line',        3, 'aaa', shw.longest_line(['aaa','b','c']))

    err_count += TestCompareByPattern(shw,  'debug_info',        1, '\d\d\.\d\d\.\d\d\.\d\d\d\d\d\d\s\:\s', shw.debug_info('aaa'))


    err_count += TestCompareByPattern(shw,  'minlen',        1, '1', shw.minlen(['a','bbb','c']))
    err_count += TestCompareByPattern(shw,  'minlen',        2, '1', shw.minlen(['a','b','ccc']))
    err_count += TestCompareByPattern(shw,  'minlen',        3, '1', shw.minlen(['aaa','bbbb','c']))

    err_count += TestCompareByPattern(shw,  'shortest_line',        1, 'b', shw.shortest_line(['aaa','b','ccc']))
    err_count += TestCompareByPattern(shw,  'shortest_line',        2, 'c', shw.shortest_line(['aaa','bbb','c']))
    err_count += TestCompareByPattern(shw,  'shortest_line',        3, 'a', shw.shortest_line(['a','bbb','ccc']))

    err_count += CompareTextLists(shw,      'filter', 1,  ['a1','c1'],       shw.filter(['a1','bb','c1'],r'\d'))
    err_count += CompareTextLists(shw,      'filter_not', 1, ['aa','cc'],   shw.filter_not(['aa','b1','cc'],r'\d'))


    err_count += TestCompareByPattern(shw,  'search_forward',        1, '1', shw.search_forward(['a','bbb','ccc'],'bb'))
    err_count += TestCompareByPattern(shw,  'search_forward',        2, '-1', shw.search_forward(['aa','bbb','ccc'],'aa',1))
    err_count += TestCompareByPattern(shw,  'search_forward',        3, '3', shw.search_forward(['aa','bbb','ccc','aa'],'aa',1))

    err_count += TestCompareByPattern(shw,  'search_backward',        1, '1', shw.search_backward(['a','bbb','ccc'],'bb'))
    err_count += TestCompareByPattern(shw,  'search_backward',        2, '0', shw.search_backward(['aa','bbb','ccc'],'aa',1))
    err_count += TestCompareByPattern(shw,  'search_backward',        3, '-1', shw.search_backward(['aa','bbb','ccc','aa'],'cc',1))

    err_count += TestCompareByPattern(shw,  'count_matches',        1, '2', shw.count_matches(['aa','bbb','ccc','aa'],'aa'))
    err_count += TestCompareByPattern(shw,  'count_matches',        2, '0', shw.count_matches(['aa','bbb','ccc','aa'],'xx'))
    err_count += TestCompareByPattern(shw,  'count_matches',        3, '4', shw.count_matches(['aa','bbb','ccc','aa'],'\w'))

    err_count += TestCompareByPattern(shw,  'to_string',        1, 'a b c', shw.to_string(['a','b','c']))
    err_count += TestCompareByPattern(shw,  'to_string',        2, 'a#b#c', shw.to_string(['a','b','c'],'#'))

    err_count += CompareTextLists(shw, 'get_fragment', 1, ['bb','cc'],   shw.get_fragment(['aa','bb','cc','dd'],1,3))
    err_count += CompareTextLists(shw, 'get_fragment', 2, ['cc','dd'],   shw.get_fragment(['aa','bb','cc','dd'],2,100))
    err_count += CompareTextLists(shw, 'get_fragment', 3, ['aa','bb'],   shw.get_fragment(['aa','bb','cc','dd'],-2,2))

    err_count += CompareTextLists(shw, 'cut_fragment', 1, ['aa','dd'],   shw.cut_fragment(['aa','bb','cc','dd'],1,3))
    err_count += CompareTextLists(shw, 'cut_fragment', 2, ['aa','bb'],   shw.cut_fragment(['aa','bb','cc','dd'],2,100))
    err_count += CompareTextLists(shw, 'cut_fragment', 3, ['cc','dd'],   shw.cut_fragment(['aa','bb','cc','dd'],-2,2))

    err_count += CompareTextLists(shw, 'insert_fragment', 1, ['aa','bb','cc','dd'],   shw.insert_fragment(['aa','dd'],1,['bb','cc']))

    err_count += CompareTextLists(shw, 'indent', 1, ['    aa','    bb'],   shw.indent(['aa','bb']))
    err_count += CompareTextLists(shw, 'indent', 2, ['--aa','--bb'],   shw.indent(['aa','bb'],'--'))

    err_count += CompareTextLists(shw, 'trail', 1, ['aa--','bb--'],   shw.trail(['aa','bb'],'--'))

    err_count += CompareTextLists(shw, 'get_vertical', 1, ['ab','12'],   shw.get_vertical(['abcd','1234'],0,2))
    err_count += CompareTextLists(shw, 'get_vertical', 2, ['bc','23'],   shw.get_vertical(['abcd','1234'],1,3))
    err_count += CompareTextLists(shw, 'get_vertical', 3, ['','56'],   shw.get_vertical(['abcd','123456'],4,6))
    err_count += CompareTextLists(shw, 'get_vertical', 4, ['abcd','123456'],   shw.get_vertical(['abcd','123456'],-1,6))

    err_count += CompareTextLists(shw, 'cut_vertical', 1, ['cd','34'],   shw.cut_vertical(['abcd','1234'],0,2))
    err_count += CompareTextLists(shw, 'cut_vertical', 2, ['ad','14'],   shw.cut_vertical(['abcd','1234'],1,3))
    err_count += CompareTextLists(shw, 'cut_vertical', 3, ['ab','12'],   shw.cut_vertical(['abcd','1234'],2,6))


    testv = ['aaa','bbb','ccc']
    err_count += CompareTextLists(shw, 'fmttxt', 1, ['aaa','bbb','ccc'],   shw.fmttxt(testv))
    err_count += CompareTextLists(shw, 'fmttxt', 2, ['--aaa','--bbb','--ccc'],   shw.fmttxt(testv, '--'))
    err_count += CompareTextLists(shw, 'fmttxt', 3, ['--*hdr','--aaa','--bbb','--ccc'],   shw.fmttxt(testv, '--', '*hdr'))
    err_count += CompareTextLists(shw, 'fmttxt', 4, ['--*hdr','--aaa','--bbb','--ccc','--*ftr'],   shw.fmttxt(testv, '--', '*hdr','*ftr'))
    err_count += CompareTextLists(shw, 'fmttxt', 5, ['--*','--a','--b','--c','--*'],   shw.fmttxt(testv, '--', '*hdr','*ftr',3))
    err_count += CompareTextLists(shw, 'fmttxt', 6, ['--*  ','--a  ','--b  ','--c  ','--*  '],   shw.fmttxt(testv, '--', '*hdr','*ftr',3,5))
    err_count += CompareTextLists(shw, 'fmttxt', 7, ['--*hdr   ', '--10: aaa', '--11: bbb', '--12: ccc', '--*ftr   '],   shw.fmttxt(testv, '--', '*hdr','*ftr',9,9,10))

    err_count += CompareTextLists(shw, 'parse_shell_output', 1, ['a', 'b', 'c'],   shw.parse_shell_output('a\nb\nc\n'))
    err_count += CompareTextLists(shw, 'parse_shell_output', 2, ['a', 'b', 'c'],   shw.parse_shell_output('a\n\nb\n\nc\n\n'))
    err_count += CompareTextLists(shw, 'parse_shell_output', 3, ['a', 'b', 'c'],   shw.parse_shell_output('a \nb \nc \n'))

    cur0 = shw._call_stack_depth()
    (cur1,cur2) = stack_depth_plus_1(shw)
    print(cur0,cur1,cur2)

    print("\nDetected %d errors\n\n"  % err_count)
    return -1 * err_count
#---

if __name__ == "__main__":
    exit(main())
#---

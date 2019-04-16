#!/usr/bin/python
#from __future__ import print_function
import inspect
import sys
import unittest
import os

from swissknife import Debug
from swissknife import Strings
from swissknife import Text
from swissknife import Shell
from swissknife import NumberBag

class Testing(unittest.TestCase):
    verbose = False

    def test_debug_lineno(self):
        self.assertEqual(Debug.lineno(), 18)
    #---



    def test_strings_enquote(self):
        expected    = '"abc"'
        actual      =  Strings.enquote('abc')
        self.assertEqual(expected, actual)

        expected    = "'abc'"
        actual      =  Strings.enquote('abc',"'")
        self.assertEqual(expected, actual)

        expected    = '#abc#'
        actual      =  Strings.enquote('abc','#')
        self.assertEqual(expected, actual)

    #---

    def test_strings_lorem(self):
        expected    = 'Lorem ipsum dolor sit amet'
        actual      = Strings.lorem(26)
        self.assertEqual(expected, actual)

        expected    = 'Lorem ipsum dolor sit'
        actual      = Strings.lorem(21)
        self.assertEqual(expected, actual)

    #---


    def test_strings_timestamp(self):
        actual      = Strings.timestamp()
        self.assertRegex(actual, r'^\d\d\d\d_\d\d_\d\d_\d+$')

        actual      = Strings.timestamp('%Y_%m_%d')
        self.assertRegex(actual, r'^\d\d\d\d_\d\d_\d\d$')
    #---


    def test_strings_randomstr(self):
        actual      = Strings.randomstr(4)
        self.assertRegex(actual, r'^....$')

        actual      = Strings.randomstr(4,'0123456789')
        self.assertRegex(actual, r'^\d\d\d\d$')
    #---


    def test_strings_is_url(self):
        self.assertTrue(Strings.is_url('http://www.xome.com'))
        self.assertTrue(Strings.is_url('https://www.xome.nz'))
        self.assertTrue(Strings.is_url('ftp://www.xome.en'))
        self.assertTrue(Strings.is_url('ftp://www'))
        self.assertTrue(Strings.is_url('ssh://www'))
        self.assertTrue(Strings.is_url('blahblah://www'))
        self.assertTrue(Strings.is_url('http://1.2.3.4:56/www'))

        self.assertFalse(Strings.is_url('www.something.com'))
    #---

    def test_strings_is_email(self):
        self.assertTrue(Strings.is_email('user@server.com'))
        self.assertTrue(Strings.is_email('user.user@server.com'))
        self.assertTrue(Strings.is_email('a.b.c.d.e@zzz.zz.tt.xx'))

        self.assertFalse(Strings.is_email('www.something.com'))
        self.assertFalse(Strings.is_email('user@www'))
        self.assertFalse(Strings.is_email('http://www'))
    #---

    def test_strings_extract_email(self):
        val         = 'sidjhgf kjdghfkjsda kjgfkasdghf test@server.com kuahfkjasdf aksjhfkjasrfha sdakjfhasjfh'
        expected    = 'test@server.com'
        actual      = Strings.extract_email(val)
        self.assertEqual(expected, actual)

        val         = 'sidjhgf kjdghfkjsda kjgfkasdghf kuahfkjasdf aksjhfkjasrfha sdakjfhasjfh'
        expected    = ''
        actual      = Strings.extract_email(val)
        self.assertEqual(expected, actual)

    #---

    def test_strings_unify(self):
        exp = '12345'
        act = Strings.unify_length('12345')
        self.assertEqual(exp, act)

        exp = '123'
        act = Strings.unify_length('12345', 3)
        self.assertEqual(exp, act)

        exp = '123__'
        act = Strings.unify_length('123', 5, 5, '_')
        self.assertEqual(exp, act)

    #---




    def test_text_save_read_append(self):
        txt = ['aaa', 'bbb', 'ccc']
        Text.save(txt, 'tmp.tmp')

        nxt = Text.read('missing.tmp')
        self.assertIsNone(nxt)

        nxt = Text.read('tmp.tmp')
        self.assertEqual(txt, nxt)

        appendix = ['ddd','eee']
        Text.append(appendix,'tmp.tmp')
        txt.extend(appendix)
        nxt = Text.read('tmp.tmp')
        self.assertEqual(txt, nxt)
        os.remove("tmp.tmp")
    #---

    def test_text_decode(self):
        txt = ['aaa', 'bbb', 'ccc']
        nxt = Text.decode(txt)
        self.assertEqual(txt, nxt)
    #---

    def test_text_clean(self):
        txt = ['aaa', 'bbb', 'ccc']
        exp = ['aaa', 'bbb', 'ccc']
        act = Text.clean(txt)
        self.assertEqual(exp, act)

        txt = ['aaa', 'bbb', '', 'ccc']
        exp = ['aaa', 'bbb', 'ccc']
        act = Text.clean(txt)
        self.assertEqual(exp, act)

        txt = [1, 2, '', 3]
        exp = ['1', '2', '3']
        act = Text.clean(txt)
        self.assertEqual(exp, act)

    #---

    def test_text_fold(self):
        exp = ['aaa', 'bbb', 'ccc']
        act = Text.fold('aaabbbccc',3)
        self.assertEqual(exp, act)
    #---


    def test_text_replace(self):
        txt = ['aaa', 'bbb', 'ccc']
        exp = ['aaa', 'xxx', 'ccc']
        act = Text.replace(txt,r'b','x')
        self.assertEqual(exp, act)
        act = Text.replace(txt,r'.','x')
        exp = ['xxx', 'xxx', 'xxx']
        self.assertEqual(exp, act)
    #---


    def test_text_remove_duplicates(self):
        txt = ['aaa', 'bbb', 'bbb', 'ccc']
        exp = ['aaa', 'bbb', 'ccc']
        act = Text.remove_duplicates(txt)
        self.assertEqual(exp, act)
    #---

    def test_text_longest_shortest(self):
        txt = ['aaa', 'bbbb', 'ccc', 'dd', 'eee']
        self.assertEqual(Text.longest(txt), 1)
        self.assertEqual(Text.shortest(txt), 3)
    #---

    def test_text_filter(self):
        txt = ['aaa1', 'bbb', 'ccc2', 'ddd', 'eee3']
        exp = ['aaa1', 'ccc2', 'eee3']
        act = Text.filter(txt,r'\d')
        self.assertEqual(exp, act)

        exp = ['bbb', 'ddd']
        act = Text.filter_not(txt,r'\d')
        self.assertEqual(exp, act)

    #---


    def test_text_search_find(self):
        txt = ['aaa1', 'bbb', 'ccc2', 'ddd', 'eee3']
        self.assertEqual(Text.search_forward(txt,'\d'), 0)
        self.assertEqual(Text.search_forward(txt,'\d',1), 2)
        self.assertEqual(Text.search_forward(txt,'x',1), -1)

        self.assertEqual(Text.search_backward(txt,'\d'), 4)
        self.assertEqual(Text.search_backward(txt,'\d',3), 2)
        self.assertEqual(Text.search_backward(txt,'x'), -1)

        self.assertEqual(Text.find(txt,'\d'), [0,2,4])
        self.assertEqual(Text.find(txt,'.'), [0,1,2,3,4])

        self.assertEqual(Text.find_not(txt,'\d'), [1,3])
        self.assertEqual(Text.find_not(txt,'.'), [])

    #---


    def test_text_fragment(self):
        txt = ['a', 'b', 'c', 'd', 'e']
        self.assertEqual(Text.get_fragment(txt, 2,3), ['c','d'])
        self.assertEqual(Text.get_fragment(txt, -4,1), ['a','b'])
        self.assertEqual(Text.get_fragment(txt, 3,18), ['d','e'])

        self.assertEqual(Text.cut_fragment(txt, 1,3), ['a','e'])
        self.assertEqual(Text.cut_fragment(txt, -1,3), ['e'])
        self.assertEqual(Text.cut_fragment(txt, 2,13), ['a','b'])

        txt = ['a', 'b', 'c']
        exp = ['a', '1', '2', 'b', 'c']
        self.assertEqual(Text.insert_fragment(txt, 1, ['1','2']), exp)

        exp = ['a', 'b', 'c', '1', '2']
        self.assertEqual(Text.insert_fragment(txt, 10, ['1','2']), exp)

        exp = ['1', '2', 'a', 'b', 'c']
        self.assertEqual(Text.insert_fragment(txt, -4, ['1','2']), exp)

    #---


    def test_text_indent(self):
        txt = ['a', 'b', 'c']
        exp = ['-a', '-b', '-c']
        act = Text.indent(txt,'-')
        self.assertEqual(exp, act)

        act = Text.dedent(act,1)
        self.assertEqual(txt, act)


        exp = ['    a', '    b', '    c']
        act = Text.indent(txt)
        self.assertEqual(exp, act)

        exp = ['a-', 'b-', 'c-']
        act = Text.trail(txt,'-')
        self.assertEqual(exp, act)
    #---


    def test_text_vertical(self):
        txt = ['abc', 'def', '123']
        exp = ['ac', 'df', '13']
        act = Text.cut_vertical(txt,1,2)
        self.assertEqual(exp, act)

        exp = ['c', 'f', '3']
        act = Text.cut_vertical(txt,-1,2)
        self.assertEqual(exp, act)

        exp = ['a', 'd', '1']
        act = Text.cut_vertical(txt,1,12)
        self.assertEqual(exp, act)

        exp = ['', '', '']
        act = Text.cut_vertical(txt,-1,12)
        self.assertEqual(exp, act)

        exp = ['b', 'e', '2']
        act = Text.get_vertical(txt,1,2)
        self.assertEqual(exp, act)

        exp = ['ab', 'de', '12']
        act = Text.get_vertical(txt,-1,2)
        self.assertEqual(exp, act)

        exp = ['', '', '']
        act = Text.get_vertical(txt,8,12)
        self.assertEqual(exp, act)

        exp = ['c', 'f', '3']
        act = Text.get_vertical(txt,2,12)
        self.assertEqual(exp, act)

    #---


    def test_text_format(self):
        txt = ['abc', 'def', '123']
        exp = ['offset-header', 'offset-abc', 'offset-def', 'offset-123', 'offset-footer']
        act = Text.format(txt,'offset-','header', 'footer')
        self.assertEqual(exp, act)

        exp = ['__head', '__1: a', '__2: d', '__3: 1', '__foot']
        act = Text.format(txt,'__','header', 'footer', 6, 6, 1)
        self.assertEqual(exp, act)

        exp = ['__head', '__10: ', '__11: ', '__12: ', '__foot']
        act = Text.format(txt,'__','header', 'footer', 6, 6, 10)
        self.assertEqual(exp, act)

    #---


    def test_text_fromstruct(self):
        import datetime
        test_struct = {'fld':'val','arr':[1,2]}
        exp = [ 'header',
                '{',
                '    "fld": "val",',
                '    "arr": [',
                '        1,',
                '        2',
                '    ]',
                '}',
                'footer']

        act = Text.from_struct(test_struct,'header', 'footer')
        self.assertEqual(exp, act)


        test_struct = {'fld':'val','arr':[1,2],'dt':datetime.datetime(2020, 5, 17)}
        exp = [ 'header',
                "{   'arr': [   1,",
                '               2],',
                "    'dt': datetime.datetime(2020, 5, 17, 0, 0),",
                "    'fld': 'val'}",
                'footer']
        act = Text.from_struct(test_struct,'header', 'footer')
        self.assertEqual(exp, act)


    #---




    def test_shell_run(self):
        res = Shell.run('dir')
        self.assertEqual(res['status'], 0)

        res = Shell.run('dir', '..')
        self.assertEqual(res['status'], 0)

        res = Shell.run('dir', '..', silent=True)
        self.assertEqual(res['status'], 0)

        res = Shell.run('', '..', silent=True)
        self.assertEqual(res['status'], 0)

        #              tag      cmd      dir     break    silent    description
        cmd_list = [('tag_a',   'dir',   '..',   True,    True,     'description'),
                    ('tag_b',   'dir',   '..',   True,    True,     'description'),
                    ('tag_c',   'dir',   '..',   True,    True,     'description')
        ]
        res = Shell.batch(cmd_list)
        self.assertEqual(res['status'], 0)

    #---

    def test_shell_filenames(self):
        fname = 'path/name.ext'
        self.assertEqual(Shell.fname_ext(fname), 'ext')
        self.assertEqual(Shell.fname_name(fname), 'name')
        self.assertEqual(Shell.fname_path(fname), 'path')
    #---

    def test_shell_findfiles(self):
        self.assertEqual(len(Shell.find_files('swissknife.py')), 1)
        self.assertEqual(len(Shell.find_files('swissknife.py',recursive=False)), 1)
    #---

    def test_shell_dir_make_remove(self):
        tname = 'temp'
        Shell.makedir(tname)
        self.assertTrue(os.path.isdir(tname))

        Shell.remove(tname)
        self.assertFalse(os.path.isdir(tname))

        tname = 'temp.tmp'
        Shell.touch(tname)
        self.assertTrue(os.path.exists(tname))
        self.assertFalse(os.path.isdir(tname))

        Shell.remove(tname)
        self.assertFalse(os.path.exists(tname))
        self.assertFalse(os.path.isdir(tname))

    #---


    def test_numberbag_fifo(self):
        nb = NumberBag('wrong')
        x = nb.get()
        self.assertIsNone(x)
        nb.put('xxx')
        x = nb.get()
        self.assertIsNone(x)


        nb = NumberBag('fifo')
        x = nb.get()
        self.assertIsNone(x)


        nb.put(1)
        nb.put(2)
        nb.put(3)

        exp = [1,2,3]
        act = []
        while nb.count():
            act.append(nb.get())
        #---
        self.assertEqual(exp, act)

    #---

    def test_numberbag_lifo(self):
        nb = NumberBag('lifo')
        nb.put(1)
        nb.put(2)
        nb.put(3)

        exp = [3,2,1]
        act = []
        while nb.count():
            act.append(nb.get())
        #---
        self.assertEqual(exp, act)

    #---

    def test_numberbag_random(self):
        nb = NumberBag('rand')
        for i in range(0,20):
            nb.put(i)
        #---
        act1 = []
        while nb.count():
            act1.append(nb.get())
        #---

        for i in range(0,20):
            nb.put(i)
        #---
        act2 = []
        while nb.count():
            act2.append(nb.get())
        #---

        self.assertNotEqual(act1, act2)

    #---




#---

if __name__ == '__main__':
    unittest.main()
#---

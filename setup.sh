#!/bin/bash

echo > temp_setup.py
echo "from distutils.core import setup"                     >> temp_setup.py
echo "setup(name='shrec',version='0.3',"                    >> temp_setup.py
echo "      author='Dmitry Obukhov',"                       >> temp_setup.py
echo "      author_email='Dmitry.Obukhov@gmail.com',"       >> temp_setup.py
echo "      py_modules=['shrec'])"                          >> temp_setup.py
python  temp_setup.py install
python2 temp_setup.py install
python3 temp_setup.py install
rm -f temp_setup.py

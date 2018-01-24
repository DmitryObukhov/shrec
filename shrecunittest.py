#!/usr/bin/python
""" SHell RECipes unit test module """
from __future__ import print_function
from textprocessor import TextProcessor
from batchprocessor import BatchProcessor

__all__ = ['TextProcessorUnitTest','BatchProcessorUnitTest']


def TextProcessorUnitTest():
    errorCount = 0

    actual_result = TextProcessor.quoted_string('abc')
    if actual_result != '"abc"':
        print ("FAIL -- QuotedString")
        errorCount += 1
    #---

    actual_result_1 = TextProcessor.time_stamp()
    actual_result_2 = TextProcessor.time_stamp()
    if actual_result_1 == actual_result_2:
        print ("FAIL -- TimeStamp %s VS %s" % (actual_result_1,actual_result_2))
        errorCount += 1
    #---

    actual_result = TextProcessor.random_string(3,'a')
    if actual_result != 'aaa':
        print ("FAIL -- random_string charset limitation")
        errorCount += 1
    #---

    actual_result_1 = TextProcessor.random_string(16,'0123456789')
    actual_result_2 = TextProcessor.random_string(16,'0123456789')
    if actual_result_1 == actual_result_2:
        print ("FAIL -- random_string, not really random")
        errorCount += 1
    #---


    return errorCount
#---

def BatchProcessorUnitTest():
    pass
#---

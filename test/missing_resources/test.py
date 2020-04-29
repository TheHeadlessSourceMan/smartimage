#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Run unit tests

See:
    http://pyunit.sourceforge.net/pyunit.html
"""
import unittest
import os
from smartimage import *


__HERE__=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep
class Test(unittest.TestCase):
    """
    Run unit test
    
    This is to test that we successfully throw errors when 
    resources go missing!
    """

    def setUp(self):
        self.dut=SmartImage()
        
    def tearDown(self):
        pass
        
    def testName(self):
        try:
            self.dut.load(__HERE__)
            self.dut.save(__HERE__+'actualOutput.png')
            assert(False) # we shouldn't have been able to get here!
        except SmartimageError as e:
            print(e)
            print(dir(e))
            assert(e.line==3)
            assert(e.xml.tag=='image')

        
def testSuite():
    """
    Combine unit tests into an entire suite
    """
    testSuite = unittest.TestSuite()
    testSuite.addTest(Test("testName"))
    return testSuite
        
        
if __name__ == '__main__':
    """
    Run all the test suites in the standard way.
    """
    unittest.main()
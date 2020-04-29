#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Run unit tests

See:
    http://pyunit.sourceforge.net/pyunit.html
"""
import unittest
import os
import sys
import smartimage


__HERE__=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep
class Test(unittest.TestCase):
    """
    Run unit test
    
    Check the command line help for each module
    """
    
    def __init__(self,testName):
        unittest.TestCase.__init__(self,testName)
        self.cmd=None
        

    def setUp(self):
        pass
        
    def tearDown(self):
        pass
        
    def testName(self):
        basedir=os.path.abspath(smartimage.__file__).rsplit(os.sep,1)[0]+os.sep
        for filename in os.listdir(basedir):
            if not filename.endswith('.py'):
                continue
            if filename in ['bounds.py','setup.py','__init__.py']:
                continue
            filename=basedir+filename
            if not os.path.isfile(filename):
                continue
            self.runScript(filename,'--help')
    
    def runScript(self,filename,*args):
        from importlib.util import spec_from_loader, module_from_spec
        from importlib.machinery import SourceFileLoader
        path=filename.rsplit(os.sep,1)
        module=path[-1].rsplit('.py',1)[0]
        path=path[0]
        spec = spec_from_loader(module, SourceFileLoader(module,filename))
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        if 'cmdline' in dir(module):
            print('RUN: '+filename+' '+(' '.join(args)))
            module.cmdline(args)
        else:
            print('SKIP: '+filename+' '+(' '.join(args)))
            #print(dir(module))
    
    def runScriptOld(self,filename,*args):
        """
        This works 100% fine, but does not add to the code coverage metrics
        """
        bak=sys.argv
        sys.argv=[filename]
        sys.argv.extend(args)
        print('RUN: '+(' '.join(sys.argv)))
        globalz=globals()
        #print(globalz)
        globalz['__package__']='smartimage'
        globalz['__name__']='__main__'
        try:
            code=open(filename).read()
            if code.find('__main__')>=0:
                exec(code,globalz)
        finally:
            sys.argv=bak
        
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
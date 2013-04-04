#
# Tests for the grammar parser.
#

import unittest
import random
import sys
from xpath2.grammar import qName, step, literal, nameTest
from xpath2 import parsetree
from pyparsing import ParseException

class TestQName(unittest.TestCase):
    def test_noNS(self):
        result = qName.parseString('nodeA')
        self.assertEqual(result[0].name, 'nodeA')
        self.assertEqual(result[0].ns, None)
    
    def test_invalidName(self):
        self.assertRaises(ParseException, qName.parseString, '1node')
        
    def test_emptyName(self):
        self.assertRaises(ParseException, qName.parseString, '')
    
    def test_nsAndName(self):
        result = qName.parseString('an:node')
        self.assertEqual(result[0].name, 'node')
        self.assertEqual(result[0].ns, 'an')
        
    def test_annonymousNS(self):
        self.assertRaises(ParseException, qName.parseString, ':node')

    def test_invalidNS(self):
        self.assertRaises(ParseException, qName.parseString, '1:node')

class TestLiteral(unittest.TestCase):
    def setUp(self):
        self.integers = [1, sys.maxsize, 0] + random.sample(range(sys.maxsize), 50)
    
    def test_numbers(self):
        result = literal.parseString('.12')
        print (result)
        result = literal.parseString('1.1')
        print (result)
        result = literal.parseString('0.1')
        print (result)
        result = literal.parseString('1e2')
        print (result)
        result = literal.parseString('1.0E+4')
        print(result)

    def test_integer(self):
        testIntegerStrings = map(str, self.integers)
        
        for valueStr in testIntegerStrings:
            result = literal.parseString(valueStr)
            self.assertIsInstance(result[0], parsetree.IntegerLiteral)
            self.assertEquals(result[0].value(), int(valueStr))
            
        self.assertRaises(ParseException, literal.parseString, '')
        self.assertRaises(ParseException, literal.parseString, '-1')
        
    def test_decimal(self):
        pass
        
    def test_double(self):
        pass

class TestStep(unittest.TestCase):
    def setUp(self):
        self.axis = ['parent', 'ancestor', 'preceding-sibling',  'preceding', 'ancestor-or-self', 'child', 'descendant', 'attribute', 'self', 'descendant-or-self', 'following-sibling', 'following', 'namespace']
        self.names = ['Node', 'ns:Node', '*:Node', 'ns:*', '*']
        self.axisPlusName = [(axis,name) for axis in self.axis for name in self.names]
        
    def test_fullsteps(self):
        for (axis,name) in self.axisPlusName:
            str = axis + '::' + name
            #print ("Testing '%s'" % str) 
            result = step.parseString(str)
            #print (result)
            nameTestResult = nameTest.parseString(name)
            
            self.assertEqual(result[0].axis, axis)
            #self.assertEqual(result[0].nodeTest, nameTestResult[0])
        

if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestQName)
    suite2 = unittest.TestLoader().loadTestsFromTestCase(TestStep)
    suite3 = unittest.TestLoader().loadTestsFromTestCase(TestLiteral)
    alltests = unittest.TestSuite([suite1, suite2, suite3])
    unittest.TextTestRunner(verbosity=2).run(alltests)
#
# Tests for the grammar parser.
#

import unittest
import random
import sys
from xpath2.grammar import qName, step, literal, nameTest
from xpath2 import parsetree
from pyparsing import ParseException
from decimal import Decimal

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
        self.decimals = [(Decimal('0.1'),'0.1'), (Decimal('1.0'),'1.0'), (Decimal('0.1'),'.1')]
        self.doubles = [(0.1, '0.1e0'), (1.1, '1.1e0'), (1000.1, '1.0001e3'), (0.0001, '1e-4')]
        self.strings = [('a', '"a"'), ('a', "'a'"), ('\'a\'', "'''a'''"), ('"a"', '"""a"""'), \
            ('"a" \'b', '\'"a" \'\'b\'')]
        self.fails = ['', '-1', '-1.0', '-.1', '"a', 'a"', "'a", "a'"]

    def test_integer(self):
        testIntegerStrings = map(str, self.integers)
        
        for valueStr in testIntegerStrings:
            result = literal.parseString(valueStr)
            self.assertIsInstance(result[0], parsetree.IntegerLiteral)
            self.assertEquals(result[0].getValue(), int(valueStr))
        
    def test_decimal(self):
        for (value, valueStr) in self.decimals:
            result = literal.parseString(valueStr)
            self.assertIsInstance(result[0], parsetree.DecimalLiteral)
            self.assertEquals(result[0].getValue(), value)
        
    def test_double(self):
        for (value, valueStr) in self.doubles:
            result = literal.parseString(valueStr)
            self.assertIsInstance(result[0], parsetree.DoubleLiteral)
            self.assertEquals(result[0].getValue(), value)
            
    def test_string(self):
        for (value, valueStr) in self.strings:
            result = literal.parseString(valueStr)
            self.assertIsInstance(result[0], parsetree.StringLiteral)
            self.assertEquals(result[0].getValue(), value)
            
    def test_fails(self):
        for value in self.fails:
            self.assertRaises(ParseException, literal.parseString, value)

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
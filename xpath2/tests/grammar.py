#
# Tests for the grammar parser.
#

import unittest
from xpath2.grammar import qName, step, nameTest
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

class TestStep(unittest.TestCase):
    def setUp(self):
        self.axis = ['parent', 'ancestor', 'preceding-sibling',  'preceding', 'ancestor-or-self', 'child', 'descendant', 'attribute', 'self', 'descendant-or-self', 'following-sibling', 'following', 'namespace']
        self.names = ['Node', 'ns:Node', '*:Node', 'ns:*', '*']
        self.axisPlusName = [(axis,name) for axis in self.axis for name in self.names]
        
    def test_fullsteps(self):
        for (axis,name) in self.axisPlusName:
            str = axis + '::' + name
            print ("Testing '%s'" % str) 
            result = step.parseString(str)
            print (result)
            nameTestResult = nameTest.parseString(name)
            
            self.assertEqual(result[0].axis, axis)
            #self.assertEqual(result[0].nodeTest, nameTestResult[0])
        

if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestQName)
    suite2 = unittest.TestLoader().loadTestsFromTestCase(TestStep)
    alltests = unittest.TestSuite([suite1, suite2])
    unittest.TextTestRunner(verbosity=2).run(alltests)
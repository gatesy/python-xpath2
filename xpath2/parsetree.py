'''
Created on 8 Jul 2012

Classes for representing nodes in the parse tree of an XPath2 expression

@author: James
'''

class QName(object):
    def __init__(self, tokens):
        if len(tokens) is 3:
            self.ns = tokens[0]
            self.name= tokens[2]
        else:
            self.ns = None
            self.name = tokens[0]
        
    def __repr__(self):
        s = 'QName('
        if not(self.ns is None):
            s += self.ns + ':'
        s += self.name + ')'
        return s

    def match(self, element):
        if self.name == element.tag:
            return element
        else:
            return None
    
class Wildcard(object):
    def __init__(self, tokens):
        self.tokens = tokens
        
    def __repr__(self):
        return 'Wildcard(' + str(self.tokens) + ')'

class KindTest(object):
    pass

class AnyKindTest(KindTest):
    pass

class TextTest(KindTest):
    pass

class CommentTest(KindTest):
    pass

class Step(object):
    def __init__(self, tokens):
        self.axis = tokens[0]
        self.nodeTest = tokens[2]
        
    def match(self, element):
        if self.axis == 'child':
            return self.nodeTest.match(element)
        
    def __repr__(self):
        return 'Step(axis=' + repr(self.axis) + '; nodeTest=' + repr(self.nodeTest) + ')'

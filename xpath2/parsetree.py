'''
Created on 8 Jul 2012

Classes for representing nodes in the parse tree of an XPath2 expression

@author: James
'''

class QName(object):
    def __init__(self, ns, name):
        self.ns = ns
        self.name = name
        
    def __str__(self):
        s = ''
        if not(self.ns is None):
            s += self.ns + ':'
        s += self.name
        return s
    
    
'''
Created on 8 Jul 2012

Functions for evaluating an XPath2 expression over a element tree structure

@author: James
'''

from xml.etree import ElementTree as ET
from xpath2.grammar import Grammar
from xpath2.context import Context

'''
Compile the given XPath string into a list of parsetree objects
'''
def compile(xpathExpr):
    return Grammar.parseString(xpathExpr)

'''
Given an element and a list of parsetree nodes, evaluate each node and return 
the list of matching elements.
'''
def evaluate(element, parsetree):
    print(parsetree)
    context = Context(parsetree, element)
    print(context)
    return context.process()
    
'''
Compile and evaluate the XPath string on the element
'''
def parse(element, xpathExpr):
    parsetree = compile(xpathExpr)
    return evaluate(element, parsetree)
        
xml1 = """
<root>
  <A value="a"></A>
  <B><C></C></B>
</root>
"""

if __name__ == '__main__':
    rootEl = ET.XML(xml1)
    ET.dump(rootEl)
    aEl = rootEl.findall("A")
    print(aEl)
    parentEl = aEl[0].findall("./..")
    print(parentEl)
    #ET.dump(parentEl)
    
    print(parse(rootEl, "root/B"))    

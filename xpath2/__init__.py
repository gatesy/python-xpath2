from xpath2.grammar import Grammar

def parse(string):
    return Grammar.parseString(string)[0]

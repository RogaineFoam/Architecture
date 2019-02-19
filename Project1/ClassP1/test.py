# Project 1, Disassembler
# Sam Pugh, William Fallin
import sys
from collections import Counter
import inspect


def autodict(*args):
    get_rid_of = ['autodict(', ',', ')', '\n']
    calling_code = inspect.getouterframes(inspect.currentframe())[1][4][0]
    calling_code = calling_code[calling_code.index('autodict'):]
    for garbage in get_rid_of:
        calling_code = calling_code.replace(garbage, '')
    var_names, var_values = calling_code.split(), args
    dyn_dict = {var_name: var_value for var_name, var_value in
                zip(var_names, var_values)}
    return dyn_dict


op = 'opcode'
arg1 = 1
arg2 = 2
arg3 = 3

array = {op, arg1, arg2, arg3}

fuck = autodict(array)
print fuck
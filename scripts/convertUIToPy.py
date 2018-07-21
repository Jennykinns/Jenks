import sys, pprint
from pysideuic import compileUi
pyfile = open("[path to output python file]/.py", 'w')
compileUi("[path to input ui file]/.ui", pyfile, False, 4,False)
pyfile.close()
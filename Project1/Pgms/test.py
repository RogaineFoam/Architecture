#Project 1, Disassembler
# Sam Pugh, William Fallin
# Alex, We Need A 2's Complememnt Method
import sys                                             # module to handle command line interface.

fileName=sys.argv[1]
fileRead=open(fileName,"r")                            # Open the binary file in read mode.
count=18                                               # total number of binary lines being inputted into the file: Needs cleaned Up
i=0

rList=[1104, 1112, 1360, 1624, 1690, 1691]
iList=[1160, 1161, 1672, 1673]
while i < count:
    inst=fileRead.readline()                           # Read 1 encoded instruction from memoryself.
    subStr=inst[0:11]                                  # split off a substring
    value=int(subStr, 2)                               # convert the bitstring into an int

    # R-Type Instruction Encoding
    for j in rList:
        if j == value:
            print "R-Type Instruction", "Value:", value

    # Immediate Instruction Encoding
    for j in iList:
        if j == value:
            print "Immediate Instruction", "Value: ", value

    # Values to check to determine the operation.
    if value > 159 and value < 192:
        print "Unconditional Branch", "Value", value

    # Conditional Branches
    if (value > 1439 and value < 1448) or (value > 1447 and value < 1456):
        print "Conditional Branch", "Value", value

    if value > 1647 and value < 1688:
        print "MOVZ"

    if value > 1939 and value < 1944:
        print "MOVK"

    # Load Store Instructions
    if (value == 1984) or (value == 1986):
        print "Load/Store Instructions", "Value:", value

    i+=1                                # increment counter

fileRead.close()                        # close the file after reading an processing is complete

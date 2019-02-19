#Project 1, Disassembler
# Sam Pugh, William Fallin
# Alex, We Need A 2's Complememnt Method
import sys                                             # module to handle command line interface.

test = ['11001011010101010101010100101010',96, 'INST', 'R3', 'R2', 'R1', 400]             # METHOD IS VERIFIED FUNCTIONAL

def evaluateInstruction(type, inst, j):         # Passes type of instruction, instruction string, and index where it was found in the array
  if type == 'immediate':
      a=0
  return

#Output Strings:
rType= '%s %d   %s   %s, %s, %s' % (test[0], test[1], test[2], test[3], test[4], test[5])
iType= '%s %d   %s   %s, %s, #%d' % (test[0], test[1], test[2], test[4], test[6])

print '%s %d   %s   %s, %s, %s' % (test[0], test[1], test[2], test[3], test[4], test[5])
print '%d   %s   %s, %s, #%d' % (test[0], test[1], test[2], test[3], test[5])

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

    if (value > 1647 and value < 1688) or (value > 1939 and value < 1944):
        print "Wide Immediate Instruction", "Value", value

    # Load Store Instructions
    if (value == 1984) or (value == 1986):
        print "Load/Store Instructions", "Value:", value

    if(value == 2038):
        print "Break Instruction", "Value", value

    print "   ",value,
    i+=1                                # increment counter

fileRead.close()                        # close the file after reading an processing is complete

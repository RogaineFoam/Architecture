# Project 1, Disassembler
# Sam Pugh, William Fallin
import sys


# Opcode key Value Pairs for Dicerning Operation
opCodeDict = {10001011000: 'ADD', 11001011000: 'SUB', 11010011011: 'LSL',
              11010011010: 'LSR', 10001010000: 'AND', 10101010000: 'ORR',
              11101010000: 'EOR', 1001000100: 'ADDI', 1101000100: 'SUBI',
              111100101: 'MOVK', 110100101: 'MOVZ', 11111000010: 'LDUR',
              11111000000: 'STUR', 10110100: 'CBZ', 10110101: 'CBNZ',
              101: 'B', 11010011100: 'RSA'}

# 1. ADD, SUB, LSL, LSR, AND, ORR, EOR
def decodeRType(binToDecode, memIndex):
    op = str(opCodeDict[int(str(binToDecode)[0:11])]+'\t')

    rm = 'R'+str(int(str(binToDecode)[11:16], 2))
    shamt = '#'+str(int(str(binToDecode)[16:22], 2))
    rn = 'R'+str(int(str(binToDecode)[22:27], 2))+', '
    rd = 'R'+str(int(str(binToDecode)[27:32], 2))+', '

    binToDecode = formatBin(binToDecode)

    # if it is not a shift instruction
    if op[0:1] != 'L' and op[0:1] != 'R':
        outString = str(binToDecode) + '\t' + \
            str(memIndex) + '\t' + \
            op + rd + rn + rm + '\n'

    # else it is a shift instruction
    else:
        outString = str(binToDecode) + '\t' + \
            str(memIndex) + '\t' + \
            op + rd + rn + shamt + '\n'

    return outString


# 1. ADDI, SUBI
def decodeIType(binToDecode, memIndex):

    op = str(opCodeDict[int(str(binToDecode)[0:10])] + '\t')


    immBin = str(binToDecode)[10:22]
    if immBin[0] == '1':
        immVal = '#' + str(binToSignedInt(immBin))
    else:
        immVal = '#' + str(int(immBin, 2))

    rn = 'R' + str(int(str(binToDecode)[22:27], 2)) + ', '
    rd = 'R' + str(int(str(binToDecode)[27:32], 2)) + ', '


    binToDecode = formatBin(binToDecode)

    outString = str(binToDecode) + '\t' + \
                str(memIndex) + '\t' + \
                op + rd + rn + immVal + '\n'

    return outString


# 1. MOVK, MOVZ
def decodeIWType(binToDecode, memIndex):

    op = str(opCodeDict[int(str(binToDecode)[0:9])] + '\t')
    lslNum = 'LSL ' + str(int(str(binToDecode)[9:11], 2)*16)

    immVal =  str(int(str(binToDecode)[11:27], 2)) + ', '

    rd = 'R' + str(int(str(binToDecode)[27:32], 2)) + ', '

    binToDecode = formatBin(binToDecode)

    outString = str(binToDecode) + '\t' + \
                str(memIndex) + '\t' + \
                op + rd + immVal + lslNum + '\n'

    return outString


# 1. LDUR, STUR
def decodeDType(binToDecode, memIndex):

    op = str(opCodeDict[int(str(binToDecode)[0:11])] + '\t')

    offsetBin = str(binToDecode)[11:20]
    if offsetBin[0] == '1':
        offsetVal = '#' + str(binToSignedInt(offsetBin)) + '] '
    else:
        offsetVal = '#' + str(int(offsetBin, 2)) + '] '

    rn = '[R' + str(int(str(binToDecode)[22:27], 2))+ ', '
    rt = 'R' + str(int(str(binToDecode)[27:32], 2)) + ', '

    binToDecode = formatBin(binToDecode)

    outString = str(binToDecode) + '\t' + \
                str(memIndex) + '\t' + \
                op + rt + rn + offsetVal + '\n'

    return outString


# 1. CBZ, CBNZ
def decodeCBType(binToDecode, memIndex):

    op = str(opCodeDict[int(str(binToDecode)[0:8])] + '\t')

    offsetBin = str(binToDecode)[8:27]
    if offsetBin[0] == '1':
        offsetVal = '#' + str(binToSignedInt(offsetBin))
    else:
        offsetVal = '#' + str(int(offsetBin, 2))

    rt = 'R' + str(int(str(binToDecode)[27:32], 2)) + ', '

    binToDecode = formatBin(binToDecode)

    outString = str(binToDecode) + '\t' + \
                str(memIndex) + '\t' + \
                op + rt + offsetVal + '\n'

    return outString


# 1. B
def decodeBType(binToDecode, memIndex):

    op = str(opCodeDict[int(str(binToDecode)[0:6])] + '\t')

    offsetBin = str(binToDecode)[6:32]
    if offsetBin[0] == '1':
        offsetVal = '#' + str(binToSignedInt(offsetBin))
    else:
        offsetVal = '#' + str(int(offsetBin, 2))

    binToDecode = formatBin(binToDecode)

    outString = str(binToDecode) + '\t' + \
                str(memIndex) + '\t' + \
                op + offsetVal + '\n'
    return outString

def decodeNop(memIndex):

    return formatBin(0) + '\t' + str(memIndex) + '\t' + 'NOP' + '\n'

def decodeBreak(binToDecode, memIndex):

    return formatBin(binToDecode) + '\t' + str(memIndex) + '\t' + 'BREAK' + '\n'


def binToSignedInt(binToConv):

    convertedInt = int(str(binToConv), 2)
    convertedInt -= 2**(len(str(binToConv)))

    return convertedInt


def formatBin(origBin):
    origBin = str(origBin).zfill(32)
    newBin = str(origBin)[0:8] + ' '
    newBin += str(origBin)[8:11] + ' '
    newBin += str(origBin)[11:16] + ' '
    newBin += str(origBin)[16:21] + ' '
    newBin += str(origBin)[21:26] + ' '
    newBin += str(origBin)[26:32]

    return newBin


# file I/O
for i in range(len(sys.argv)):
    if(sys.argv[i]=='-i' and i<(len(sys.argv)-1)):
        inFile=sys.argv[i+1]
    elif(sys.argv[i]=='-o' and i<(len(sys.argv)-1)):
        outFile=sys.argv[i+1]

fileRead=open(inFile,'r')
fileWrite=open(outFile,'w')
rList=[1104, 1112, 1360, 1624, 1690, 1691, 1692, 1872]
iList=[1160, 1161, 1672, 1673]
inst=fileRead.readline()
memLoc = 96
while inst != "":
    subStr=inst[0:11]
    value=int(subStr, 2)

    # R-Type Instruction Encoding
    if value in rList:
        fileWrite.write(decodeRType(inst, memLoc))

    # Immediate Instruction Encoding
    elif value in iList:
        fileWrite.write(decodeIType(inst, memLoc))

    # Unconditional Branches
    elif value > 159 and value < 192:
        fileWrite.write(decodeBType(inst, memLoc))

    # Conditional Branches
    elif (value > 1439 and value < 1456):
        fileWrite.write(decodeCBType(inst, memLoc))

    # Decode Wide Instruction Type
    elif (value > 1683 and value < 1688) or (value > 1939 and value < 1944):
        fileWrite.write(decodeIWType(inst, memLoc))

    # Load Store Instructions
    elif (value == 1984) or (value == 1986):
        fileWrite.write(decodeDType(inst, memLoc))

    # Break Statement
    elif(value == 2038):
        fileWrite.write(decodeBreak(inst, memLoc))

    # NoOp Instruction
    elif(value == 0):
        fileWrite.write(decodeNop(memLoc))

    # Else 2's Complement
    else:
        fileWrite.write(inst.rstrip() + '\t' + str(memLoc) + '\t' + str(binToSignedInt(int(inst))) + '\n')

    memLoc += 4
    inst=fileRead.readline()

fileRead.close()
fileWrite.close()

opCodeDict = {10001011000: 'ADD', 11001011000: 'SUB', 11010011011: 'LSL',
              11010011010: 'LSR', 10001010000: 'AND', 10101010000: 'ORR',
              11001010000: 'EOR', 1001000100: 'ADDI', 1101000100: 'SUBI',
              111100101: 'MOVK', 110100101: 'MOVZ', 11111000010: 'LDUR',
              11111000000: 'STUR', 10110100: 'CBZ', 10110101: 'CBNZ',
              101: 'B'}

# CNBZ CBZ have some notes in the ppt
# Ask Sam about the SHIFTS in the ppt, they're unsigned I think

# 1. ADD
# 2. SUB
# 3. LSL
# 4. LSR
# 5. AND
# 6. ORR
# 7. EOR
def decodeRType(binToDecode, memIndex):
    # First 11 are opcode for R-Type instructions
    op = str(opCodeDict[int(str(binToDecode)[0:11])]+'\t')
    # Next 5 are rm, need case for XZR
    rm = 'R'+str(int(str(binToDecode)[11:16], 2))
    shamt = '#'+str(int(str(binToDecode)[16:22], 2))
    rn = 'R'+str(int(str(binToDecode)[22:27], 2))+', '
    rd = 'R'+str(int(str(binToDecode)[27:32], 2))+', '

    # Formatting binToDecode for printing:
    binToDecode = formatBin(binToDecode)


    # Non-shift case:
    if op[0:1] != 'L':
        outString = str(binToDecode) + "\t" + \
            str(memIndex) + "\t" + \
            op + rd + rn + rm
    # Shift case:
    else:
        outString = str(binToDecode) + "\t" + \
            str(memIndex) + "\t" + \
            op + rd + rn + shamt

    return outString


# 1. ADDI
# 2. SUBI
def decodeIType(binToDecode, memIndex):
    # First 10 are opcode for I-Type instructions
    op = str(opCodeDict[int(str(binToDecode)[0:10])] + '\t')

    # Handling for signed ints
    immBin = str(binToDecode)[10:22]
    if immBin[0] == '1':
        immVal = '#' + str(binToSignedInt(immBin))
    else:
        immVal = '#' + str(int(immBin, 2))

    rn = 'R' + str(int(str(binToDecode)[22:27], 2)) + ', '
    rd = 'R' + str(int(str(binToDecode)[27:32], 2)) + ', '

    # Format binary for output
    binToDecode = formatBin(binToDecode)

    outString = str(binToDecode) + "\t" + \
                str(memIndex) + "\t" + \
                op + rd + rn + immVal

    return outString


# 1. MOVK
# 2. MOVZ
def decodeIWType(binToDecode, memIndex):
    # First 9 are opcode for IW-Type instructions
    op = str(opCodeDict[int(str(binToDecode)[0:9])] + '\t')
    lslNum = 'LSL ' + str(int(str(binToDecode)[9:11], 2))

    immVal =  str(int(str(binToDecode)[11:27], 2)) + ', '

    rd = 'R' + str(int(str(binToDecode)[27:32], 2)) + ', '

    binToDecode = formatBin(binToDecode)

    outString = str(binToDecode) + "\t" + \
                str(memIndex) + "\t" + \
                op + rd + immVal + lslNum

    return outString


# 1. LDUR
# 2. STUR
def decodeDType(binToDecode, memIndex):
    # First 11 are opcode for D-Type instructions
    op = str(opCodeDict[int(str(binToDecode)[0:11])] + '\t')

    # Handling signed imm values
    offsetBin = str(binToDecode)[11:20]
    if offsetBin[0] == '1':
        offsetVal = '#' + str(binToSignedInt(offsetBin)) + '] '
    else:
        offsetVal = '#' + str(int(offsetBin, 2)) + '] '

    # I don't seem to need the value stored in op2?
    op2 = str(binToDecode)[20:22]
    rn = '[R' + str(int(str(binToDecode)[22:27], 2))+ ', '
    rt = 'R' + str(int(str(binToDecode)[27:32], 2)) + ', '

    binToDecode = formatBin(binToDecode)

    outString = str(binToDecode) + "\t" + \
                str(memIndex) + "\t" + \
                op + rt + rn + offsetVal

    return outString


# 1. CBZ
# 2. CBNZ
def decodeCBType(binToDecode, memIndex):
    # First 8 are opcode for CB-Type instructions
    op = str(opCodeDict[int(str(binToDecode)[0:8])] + '\t')

    # For this version of the instruction, the stuff in between
    # is the offset for the instruction as per ppt guidelines
    # Handling signed imm values
    offsetBin = str(binToDecode)[11:27]
    if offsetBin[0] == '1':
        offsetVal = '#' + str(binToSignedInt(offsetBin)) + ', '
    else:
        offsetVal = '#' + str(int(offsetBin, 2)) + ', '

    rt = 'R' + str(int(str(binToDecode)[27:32], 2)) + ', '

    binToDecode = formatBin(binToDecode)

    outString = str(binToDecode) + "\t" + \
                str(memIndex) + "\t" + \
                op + rt + offsetVal

    return outString


# 1. B
def decodeBType(binToDecode, memIndex):
    # First 6 are opcode for B-Type instructions but leading zeroes are stripped
    op = str(opCodeDict[int(str(binToDecode)[0:6])] + '\t')

    # For this version of the instruction, the stuff in between
    # is the offset for the instruction as per ppt guidelines
    # Handling signed imm values
    offsetBin = str(binToDecode)[6:32]
    if offsetBin[0] == '1':
        offsetVal = '#' + str(binToSignedInt(offsetBin))
    else:
        offsetVal = '#' + str(int(offsetBin, 2))

    binToDecode = formatBin(binToDecode)

    outString = str(binToDecode) + "\t" + \
                str(memIndex) + "\t" + \
                op + offsetVal
    return outString

def decodeNop(memIndex):

    return formatBin(0) + "\t" + str(memIndex) + "\t" + 'NOP'

def decodeBreak(binToDecode, memIndex):

    return formatBin(binToDecode) + "\t" + str(memIndex) + "\t" + 'BREAK'


# Must be passed 2's C bitstring, having issues with leading zeroes being striped by dumb-ass python
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

print decodeRType("10001011000000100000000000100011", 96)
print decodeRType("11001011000000100000000000100011", 100)
print decodeRType("10001010000000100000000000100011", 104)
print decodeRType("10101010000000100000000000100011", 108)
print decodeBType("00010100000000000010011100010000", 112)
print decodeIType("10010001001001100100000001000001", 116)
print decodeIType("11010001000001100100000001000001", 120)
print decodeDType("11111000010001100100000001000001", 124)
print decodeDType("11111000000001100100000001000001", 128)
print decodeCBType("10110100000000000000000001110011", 132)
print decodeCBType("10110101000000000000000001110011", 136)
print decodeIWType("11010010100000000001111111100001", 140)
print decodeIWType("11110010111111111110000000000010", 144)
print decodeRType("11010011010000000001000000100000", 148)
print decodeRType("11010011011000000001000000100000", 152)
print decodeBreak("11111110110111101111111111100111", 156)
print decodeNop(160)
# print decodeRType("11111111111111111111111111111111", 164)
# print decodeRType("11111111111111111111111111111110", 168)
# print decodeRType("11111111111111111111111111111101", 172)
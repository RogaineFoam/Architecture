# Project 1, Disassembler
# Sam Pugh, William Fallin
import sys


class Disassembler:
    # initialize the opcodeDictionary in constructor
    def __init__(self):
        self.opCodeDict = {10001011000: 'ADD', 11001011000: 'SUB', 11010011011: 'LSL',
                           11010011010: 'LSR', 10001010000: 'AND', 10101010000: 'ORR',
                           11101010000: 'EOR', 1001000100: 'ADDI', 1101000100: 'SUBI',
                           111100101: 'MOVK', 110100101: 'MOVZ', 11111000010: 'LDUR',
                           11111000000: 'STUR', 10110100: 'CBZ', 10110101: 'CBNZ',
                           101: 'B', 11010011100: 'RSA'}

    # 1. ADD, SUB, LSL, LSR, AND, ORR, EOR
    def decodeRType(self, binToDecode, memIndex):
        op = str(self.opCodeDict[int(str(binToDecode)[0:11])] + '\t')

        rm = 'R' + str(int(str(binToDecode)[11:16], 2))
        shamt = '#' + str(int(str(binToDecode)[16:22], 2))
        rn = 'R' + str(int(str(binToDecode)[22:27], 2)) + ', '
        rd = 'R' + str(int(str(binToDecode)[27:32], 2)) + ', '

        binToDecode = self.formatBin(binToDecode)

        # if it is not a shift instruction
        if op[0:1] != 'L' and op[0:1] != 'R':
            outString = str(binToDecode) + '\t' + \
                        str(memIndex) + '\t' + \
                        op + rd + rn + rm + '\n'
            # Stripping the unnecessary characters that were used to format it in the past
            outInst = Instruction(binToDecode.replace(' ', ''), op,
                                  rd[1:-2], rn[1:-2], rm[1:], outString)

        # else it is a shift instruction
        else:
            outString = str(binToDecode) + '\t' + \
                        str(memIndex) + '\t' + \
                        op + rd + rn + shamt + '\n'

            outInst = Instruction(binToDecode.replace(' ', ''), op,
                                  rd[1:-2], rn[1:-2], shamt[1:], outString)

        return outInst

    # 1. ADDI, SUBI
    def decodeIType(self, binToDecode, memIndex):

        op = str(self.opCodeDict[int(str(binToDecode)[0:10])] + '\t')

        immBin = str(binToDecode)[10:22]
        if immBin[0] == '1':
            immVal = '#' + str(self.binToSignedInt(immBin))
        else:
            immVal = '#' + str(int(immBin, 2))

        rn = 'R' + str(int(str(binToDecode)[22:27], 2)) + ', '
        rd = 'R' + str(int(str(binToDecode)[27:32], 2)) + ', '

        binToDecode = self.formatBin(binToDecode)

        outString = str(binToDecode) + '\t' + \
                    str(memIndex) + '\t' + \
                    op + rd + rn + immVal + '\n'

        outInst = Instruction(binToDecode.replace(' ', ''), op,
                              rd[1:-2], rn[1:-2], immVal[1:], outString)

        return outInst

    # 1. MOVK, MOVZ
    def decodeIWType(self, binToDecode, memIndex):

        op = str(self.opCodeDict[int(str(binToDecode)[0:9])] + '\t')
        lslNum = 'LSL ' + str(int(str(binToDecode)[9:11], 2) * 16)

        immVal = str(int(str(binToDecode)[11:27], 2)) + ', '

        rd = 'R' + str(int(str(binToDecode)[27:32], 2)) + ', '

        binToDecode = self.formatBin(binToDecode)

        outString = str(binToDecode) + '\t' + \
                    str(memIndex) + '\t' + \
                    op + rd + immVal + lslNum + '\n'

        outInst = Instruction(binToDecode.replace(' ', ''), op,
                              rd[1:-2], immVal[:-2], lslNum[4:], outString)

        return outInst

    # 1. LDUR, STUR
    def decodeDType(self, binToDecode, memIndex):

        op = str(self.opCodeDict[int(str(binToDecode)[0:11])] + '\t')

        offsetBin = str(binToDecode)[11:20]
        if offsetBin[0] == '1':
            offsetVal = '#' + str(self.binToSignedInt(offsetBin)) + '] '
        else:
            offsetVal = '#' + str(int(offsetBin, 2)) + '] '

        rn = '[R' + str(int(str(binToDecode)[22:27], 2)) + ', '
        rt = 'R' + str(int(str(binToDecode)[27:32], 2)) + ', '

        binToDecode = self.formatBin(binToDecode)

        outString = str(binToDecode) + '\t' + \
                    str(memIndex) + '\t' + \
                    op + rt + rn + offsetVal + '\n'

        outInst = Instruction(binToDecode.replace(' ', ''), op,
                              rt[1:-2], rn[2:-2], offsetVal[1:-2], outString)

        return outInst

    # 1. CBZ, CBNZ
    def decodeCBType(self, binToDecode, memIndex):

        op = str(self.opCodeDict[int(str(binToDecode)[0:8])] + '\t')

        offsetBin = str(binToDecode)[8:27]
        if offsetBin[0] == '1':
            offsetVal = '#' + str(self.binToSignedInt(offsetBin))
        else:
            offsetVal = '#' + str(int(offsetBin, 2))

        rt = 'R' + str(int(str(binToDecode)[27:32], 2)) + ', '

        binToDecode = self.formatBin(binToDecode)

        outString = str(binToDecode) + '\t' + \
                    str(memIndex) + '\t' + \
                    op + rt + offsetVal + '\n'

        outInst = Instruction(binToDecode.replace(' ', ''), op,
                              rt[1:-2], offsetVal[1:], '', outString)

        return outInst

    # 1. B
    def decodeBType(self, binToDecode, memIndex):

        op = str(self.opCodeDict[int(str(binToDecode)[0:6])] + '\t')

        offsetBin = str(binToDecode)[6:32]
        if offsetBin[0] == '1':
            offsetVal = '#' + str(self.binToSignedInt(offsetBin))
        else:
            offsetVal = '#' + str(int(offsetBin, 2))

        binToDecode = self.formatBin(binToDecode)

        outString = str(binToDecode) + '\t' + \
                    str(memIndex) + '\t' + \
                    op + offsetVal + '\n'

        outInst = Instruction(binToDecode.replace(' ', ''), op,
                              offsetVal[1:], '', '', outString)

        return outInst

    def decodeNop(self, memIndex):

        outInst = Instruction(self.formatBin(0).replace(' ', ''), 'NOP',
                              '', '', '', self.formatBin(0) + '\t' + str(memIndex) + '\t' + 'NOP' + '\n')
        return outInst

    def decodeBreak(self, binToDecode, memIndex):

        outInst = Instruction(binToDecode, 'BREAK',
                              '', '', '', self.formatBin(binToDecode) + '\t' + str(memIndex) + '\t' + 'BREAK' + '\n')

        return outInst

    def binToSignedInt(self, binToConv):

        convertedInt = int(str(binToConv), 2)
        convertedInt -= 2 ** (len(str(binToConv)))

        return convertedInt

    def formatBin(self, origBin):
        origBin = str(origBin).zfill(32)
        newBin = str(origBin)[0:8] + ' '
        newBin += str(origBin)[8:11] + ' '
        newBin += str(origBin)[11:16] + ' '
        newBin += str(origBin)[16:21] + ' '
        newBin += str(origBin)[21:26] + ' '
        newBin += str(origBin)[26:32]

        return newBin

    def run(self):
        for i in range(len(sys.argv)):
            if (sys.argv[i] == '-i' and i < (len(sys.argv) - 1)):
                inFile = sys.argv[i + 1]
            elif (sys.argv[i] == '-o' and i < (len(sys.argv) - 1)):
                outFile = sys.argv[i + 1]

        fileRead = open(inFile, 'r')
        fileWrite = open(outFile, 'w')
        rList = [1104, 1112, 1360, 1624, 1690, 1691, 1692, 1872]
        iList = [1160, 1161, 1672, 1673]
        inst = fileRead.readline()
        memLoc = 96
        instList = []
        memoryMap={}
        while inst != "":
            subStr = inst[0:11]
            value = int(subStr, 2)
            i = 0
            # R-Type Instruction Encoding
            if value in rList:
                # fileWrite.write(self.decodeRType(inst, memLoc))
                instList.append(self.decodeRType(inst, memLoc))

                # Immediate Instruction Encoding
            elif value in iList:
                # fileWrite.write(self.decodeIType(inst, memLoc))
                instList.append(self.decodeIType(inst, memLoc))

                # Unconditional Branches
            elif value > 159 and value < 192:
                # fileWrite.write(self.decodeBType(inst, memLoc))
                instList.append(self.decodeBType(inst, memLoc))

                # Conditional Branches
            elif (value > 1439 and value < 1456):
                # fileWrite.write(self.decodeCBType(inst, memLoc))
                instList.append(self.decodeCBType(inst, memLoc))

                # Decode Wide Instruction Type
            elif (value > 1683 and value < 1688) or (value > 1939 and value < 1944):
                # fileWrite.write(self.decodeIWType(inst, memLoc))
                instList.append(self.decodeIWType(inst, memLoc))

                # Load Store Instructions
            elif (value == 1984) or (value == 1986):
                # fileWrite.write(self.decodeDType(inst, memLoc))
                instList.append(self.decodeDType(inst, memLoc))

                # Break Statement
            elif (value == 2038):
                # fileWrite.write(self.decodeBreak(inst, memLoc))
                instList.append(self.decodeBreak(inst, memLoc))

                # NoOp Instruction
            elif (value == 0):
                # fileWrite.write(self.decodeNop(memLoc))
                instList.append(self.decodeNop(memLoc))

                # Else 2's Complement
            else:
                # fileWrite.write(inst.rstrip() + '\t' + str(memLoc) + '\t' + str(self.binToSignedInt(int(inst))) + '\n')
                instList.append(Instruction(inst, '', '', '', '',
                                            inst.rstrip() + '\t' + str(memLoc) + '\t' + str(
                                                self.binToSignedInt(int(inst))) + '\n'))

            memLoc += 4
            inst = fileRead.readline()

        # Iterates through all the instructions and prints them
        for i in range(len(instList)):
            instList[i].printInstruction(fileWrite)
            memoryMap.update({(96 + (4 * i)): instList[i]})

        fileRead.close()
        fileWrite.close()

        # Returns a map of the memory with addresses in decimal. Also returns the first available address
        return memoryMap, (len(instList) * 4 + 96)


################################################################################
# Class Disassembler Ends Here                                                 #
################################################################################

class Instruction:
    # Define all local variables on construction
    def __init__(self, machineCode='', textOp='', argument1='', argument2='', argument3='', stringToPrint=''):
        self.binInstr = machineCode
        self.operation = textOp
        self.argOne = argument1
        self.argTwo = argument2
        self.argThree = argument3
        self.formattedString = stringToPrint

    # printInstruction, prints the formattedString to the file supplied by the argument writeFile
    def printInstruction(self, writeFile):
        writeFile.write(self.formattedString)

    # getNonNullInfo, returns an array of all relevant fields operation is always included, even if null
    def getNonNullInfo(self):
        operationArray = []
        operationArray.append(self.operation)

        if (self.argOne == ''):
            return operationArray
        operationArray.append(self.argOne)

        if (self.argTwo == ''):
            return operationArray
        operationArray.append(self.argTwo)

        if (self.argThree == ''):
            return operationArray
        operationArray.append(self.argThree)

        return operationArray


################################################################################
# Class Instruction Ends Here                                                  #
################################################################################

d = Disassembler()
d.run()

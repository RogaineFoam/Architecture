# Project 2, Simulator
# Sam Pugh, William Fallin
import sys


# class that will hold all of the needed elements for Instructions
class Instruction:
    # Define all local variables on construction
    def __init__(self, machineCode='', textOp='', argument1='33', argument2='33', argument3='33', stringToPrint='',
                 memLoc='96'):
        self.binInstr = machineCode
        self.operation = textOp
        self.memLoc = int(memLoc)  # memory location for this to be stored in
        self.argOne = int(argument1)  # this holds 2's comp value
        self.argTwo = int(argument2)
        self.argThree = int(argument3)
        self.formattedString = stringToPrint

    # printInstruction, prints the formattedString to the file supplied by the argument writeFile
    def printInstruction(self, writeFile):
        writeFile.write(self.formattedString)


################################################################################
# Instruction Class Ends Here                                                  #
################################################################################

class State:
    # state takes not parameters
    def __init__(self, memMap, endIAddr, outFile):
        # set up the output file and fix formatting
        self.outFile = outFile + "_sim.txt"

        # open the file in write mode
        self.simWrite = open(self.outFile, 'w')

        # Generate an array of 32 registers and initialize them to 0
        self.registers = [0] * 32

        # Current PC location in program
        self.pcAddr = 96

        # Current cycle count
        self.cycleCount = 0

        # Dictionary to hold location in memory and index of instruction
        self.memoryMap = memMap

        # End of data memory
        self.endOfData = 0

        # Last instruction address, iterates backwards through the memory map until it finds the last instruction
        # While it does this, it is replacing data items with their plain int counterparts
        # I.E. Turns and instruction that contains the two's complement number -32 with just the number -32 ect.
        self.endOfData = endIAddr
        while self.memoryMap[endIAddr].operation == '':
            self.memoryMap.update({endIAddr: int(self.memoryMap[endIAddr].argOne)})
            endIAddr -= 4

        self.endIAddr = endIAddr

    def outputState(self):
        # ensure extra end line for next phase of output
        self.simWrite.write("=====================\n")
        self.simWrite.write(
            "cycle:%d\t%s\n" % (
                self.cycleCount, self.memoryMap[self.pcAddr].formattedString[38:]))
        self.simWrite.write("registers:\n")
        self.simWrite.write(
            "r00:\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n" % (self.registers[0], self.registers[1],
                                                        self.registers[2], self.registers[3],
                                                        self.registers[4], self.registers[5],
                                                        self.registers[6], self.registers[7]))

        self.simWrite.write(
            "r08:\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n" % (self.registers[8], self.registers[9],
                                                        self.registers[10], self.registers[11],
                                                        self.registers[12], self.registers[13],
                                                        self.registers[14], self.registers[15]))

        self.simWrite.write(
            "r16:\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n" % (self.registers[16], self.registers[17],
                                                        self.registers[18], self.registers[19],
                                                        self.registers[20], self.registers[21],
                                                        self.registers[22], self.registers[23]))

        self.simWrite.write(
            "r24:\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n\n" % (self.registers[24], self.registers[25],
                                                          self.registers[26], self.registers[27],
                                                          self.registers[28], self.registers[29],
                                                          self.registers[30], self.registers[31]))
        self.simWrite.write("data:\n")

        # print memMap
        addrIndex = self.endIAddr + 4
        # These work now
        # print self.endOfData
        # print self.endIAddr
        # counter for now to make functional, must think of something cooler...

        while (addrIndex <= self.endOfData):
            self.simWrite.write(str(addrIndex) + ':\t')

            # loop will force 8 writes even if the index is
            for i in range(8):
                if int(addrIndex) in self.memoryMap:
                    self.simWrite.write(str(self.memoryMap[int(addrIndex)]) + "\t")
                else:
                    self.simWrite.write('0\t')

                addrIndex += 4

            self.simWrite.write("\n")

        self.simWrite.write("\n")


################################################################################
# State Class Ends Here                                                        #
################################################################################

class Simulator:

    def __init__(self, simState):
        self.state = simState

    # 'Graceful crash' w/ some debug code
    def CRASH(self, errorMSG='Fatal Error'):
        print errorMSG
        print self.state.memoryMap[self.state.pcAddr].formattedString[38:]
        sys.exit()

    # accessMemory, takes a memory location and what should be done to it and checks it for validity, crashes otherwise
    # Writes the data if the action was a write and the address is valid, returns the read data if its a read.
    def accessMemory(self, address, readOrWrite, dataToWrite=''):
        # If it's greater than it is trying to read or write from an address that's not restricted
        if address > self.state.endIAddr:
            # If we are trying to read from an address that is just junk memory
            if readOrWrite == 'r':
                try:
                    return self.state.memoryMap[int(address)]
                except KeyError:
                    self.CRASH('You tried to read from memory that was not written to by you')
            else:
                self.state.endOfData = int(address)
                self.state.memoryMap.update({int(address): dataToWrite})

        else:
            self.CRASH('You attempted to read or write to reserved memory, IE: system memory, instruction memory, ect.')

    # Does the branch validation and branches the PC
    def branch(self, bOffset):
        # Compute target address PC + (Offset * 4)
        targetAddr = self.state.pcAddr + (bOffset * 4)

        # Determine if this is legal jump, for error message before crash
        if targetAddr > self.state.endIAddr or targetAddr < 96:
            self.CRASH('You tried to branch out of instruction memory, ya dingus!')
        # Set PC to this instruction
        else:
            # One of two special cases where we miss the end of the sim while loop
            self.state.cycleCount += 1
            self.state.outputState()
            self.state.pcAddr = targetAddr

    # running the simulator after all data has been inputted into the data structures
    # from the disassembler.
    # pass state object to run function.
    def run(self):

        while self.state.pcAddr <= self.state.endIAddr:
            test = self.state.memoryMap[self.state.pcAddr].operation
            # both functions assume immediate operand will be located in the r2 register.
            if test == "ADD":
                self.state.registers[int(self.state.memoryMap[self.state.pcAddr].argOne)] = self.state.registers[int(
                    self.state.memoryMap[self.state.pcAddr].argTwo)] + self.state.registers[int(
                    self.state.memoryMap[self.state.pcAddr].argThree)]

            elif test == "ADDI":
                self.state.registers[int(self.state.memoryMap[self.state.pcAddr].argOne)] = self.state.registers[int(
                    self.state.memoryMap[self.state.pcAddr].argTwo)] + int(
                    self.state.memoryMap[self.state.pcAddr].argThree)

            # both functions assume immediate operand will be located in the r2 register.
            elif test == "SUB":
                self.state.registers[int(self.state.memoryMap[self.state.pcAddr].argOne)] = self.state.registers[int(
                    self.state.memoryMap[self.state.pcAddr].argTwo)] - self.state.registers[int(
                    self.state.memoryMap[self.state.pcAddr].argThree)]

            elif test == "SUBI":
                self.state.registers[int(self.state.memoryMap[self.state.pcAddr].argOne)] = self.state.registers[int(
                    self.state.memoryMap[self.state.pcAddr].argTwo)] - int(
                    self.state.memoryMap[self.state.pcAddr].argThree)

            elif test == "AND":
                self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] = self.state.registers[int(
                    self.state.memoryMap[self.state.pcAddr].argTwo)] & self.state.registers[int(
                    self.state.memoryMap[self.state.pcAddr].argThree)]

            elif test == "ORR":
                self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] = self.state.registers[int(
                    self.state.memoryMap[self.state.pcAddr].argTwo)] | self.state.registers[int(
                    self.state.memoryMap[self.state.pcAddr].argThree)]

            elif test == "EOR":
                self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] = self.state.registers[int(
                    self.state.memoryMap[self.state.pcAddr].argTwo)] ^ self.state.registers[int(
                    self.state.memoryMap[self.state.pcAddr].argThree)]

            elif test == "LSL":
                self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] = self.state.registers[int(
                    self.state.memoryMap[self.state.pcAddr].argTwo)] << int(
                    self.state.memoryMap[self.state.pcAddr].argThree)

            elif test == "LSR":
                shamt = 2**int(self.state.memoryMap[self.state.pcAddr].argThree)
                val = int(self.state.registers[int(self.state.memoryMap[self.state.pcAddr].argTwo)])//shamt
                if val < 0 and shamt != 1:
                    val *= -1
                self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] = val

            elif test == "ASR":
                self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] = self.state.registers[int(
                    self.state.memoryMap[self.state.pcAddr].argTwo)] >> int(self.state.memoryMap[self.state.pcAddr].argThree)

            elif test == "LDUR":
                self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] = self.accessMemory(
                    self.state.registers[self.state.memoryMap[self.state.pcAddr].argTwo] + (4 *
                                                                                            self.state.memoryMap[
                                                                                                self.state.pcAddr].argThree),
                    'r')

            elif test == "STUR":
                self.accessMemory(self.state.registers[self.state.memoryMap[self.state.pcAddr].argTwo] + (
                        4 * self.state.memoryMap[self.state.pcAddr].argThree), 'w',
                                  self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne])

            elif test == "MOVK":
                mask = 0xFFFF << self.state.memoryMap[self.state.pcAddr].argThree
                self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] = self.state.registers[
                                                                                           self.state.memoryMap[
                                                                                               self.state.pcAddr].argOne] & ~mask
                self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] = self.state.registers[
                                                                                           self.state.memoryMap[
                                                                                               self.state.pcAddr].argOne] | (
                                                                                               self.state.memoryMap[
                                                                                                   self.state.pcAddr].argTwo <<
                                                                                               self.state.memoryMap[
                                                                                                   self.state.pcAddr].argThree)

            elif test == 'MOVZ':
                self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] = self.state.memoryMap[
                                                                                           self.state.pcAddr].argTwo << \
                                                                                       self.state.memoryMap[
                                                                                           self.state.pcAddr].argThree

            elif test == "B":
                self.branch(self.state.memoryMap[self.state.pcAddr].argOne)
                # Continue the loop instruction to miss the bottom PC +4 increment
                continue

            elif test == "CBZ":
                if self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] == 0:
                    self.branch(self.state.memoryMap[self.state.pcAddr].argTwo)
                    continue


            elif test == "CBNZ":
                if self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] != 0:
                    self.branch(self.state.memoryMap[self.state.pcAddr].argTwo)
                    continue

            elif test == "BREAK":
                # The second of two special cases where we miss the end of the loop
                self.state.cycleCount += 1
                self.state.outputState()
                break
                # Looks like he just wants us to use break to signal the end of the program

            # NOP instruction if it is not one of the other instructions. It does nothing and does not need a check
            self.state.cycleCount += 1
            self.state.outputState()
            self.state.pcAddr += 4


class Disassembler:
    # initialize the opcodeDictionary in constructor
    def __init__(self):
        self.opCodeDict = {10001011000: 'ADD', 11001011000: 'SUB', 11010011011: 'LSL',
                           11010011010: 'LSR', 10001010000: 'AND', 10101010000: 'ORR',
                           11101010000: 'EOR', 1001000100: 'ADDI', 1101000100: 'SUBI',
                           111100101: 'MOVK', 110100101: 'MOVZ', 11111000010: 'LDUR',
                           11111000000: 'STUR', 10110100: 'CBZ', 10110101: 'CBNZ',
                           101: 'B', 11010011100: 'ASR'}
        self.didBreak = False

    # 1. ADD, SUB, LSL, LSR, AND, ORR, EOR
    def decodeRType(self, binToDecode, memIndex):
        op = str(self.opCodeDict[int(str(binToDecode)[0:11])] + '\t')

        rm = 'R' + str(int(str(binToDecode)[11:16], 2))
        shamt = '#' + str(int(str(binToDecode)[16:22], 2))
        rn = 'R' + str(int(str(binToDecode)[22:27], 2)) + ', '
        rd = 'R' + str(int(str(binToDecode)[27:32], 2)) + ', '

        # Formatting binary string to output specs
        binToDecode = self.formatBin(binToDecode)

        # if it is not a shift instruction
        if op[1:2] != 'S':
            outString = str(binToDecode) + '\t' + \
                        str(memIndex) + '\t' + \
                        op + rd + rn + rm + '\n'

            # Constructing the instruction that gets passed into the dictionary
            # Stripping the unnecessary characters that were used to format it in the past

            outInst = Instruction(binToDecode.replace(' ', ''), op.strip(),
                                  int(rd[1:-2]), int(rn[1:-2]), int(rm[1:]), outString, 0)

        # else it is a shift instruction
        else:
            outString = str(binToDecode) + '\t' + \
                        str(memIndex) + '\t' + \
                        op + rd + rn + shamt + '\n'

            # Construction the instruction
            outInst = Instruction(binToDecode.replace(' ', ''), op.strip(),
                                  int(rd[1:-2]), int(rn[1:-2]), int(shamt[1:]), outString, 0)

        return outInst

    # 1. ADDI, SUBI
    def decodeIType(self, binToDecode, memIndex):

        op = str(self.opCodeDict[int(str(binToDecode)[0:10])] + '\t')

        # immediate binary value
        immBin = str(binToDecode)[10:22]
        if immBin[0] == '1':
            immVal = '#' + str(self.binToSignedInt(immBin))
        else:
            immVal = '#' + str(int(immBin, 2))

        rn = 'R' + str(int(str(binToDecode)[22:27], 2)) + ', '
        rd = 'R' + str(int(str(binToDecode)[27:32], 2)) + ', '

        # format binary
        binToDecode = self.formatBin(binToDecode)

        outString = str(binToDecode) + '\t' + \
                    str(memIndex) + '\t' + \
                    op + rd + rn + immVal + '\n'

        # construct the instruction to be passed into the dictionary.
        outInst = Instruction(binToDecode.replace(' ', ''), op.strip(),
                              int(rd[1:-2]), int(rn[1:-2]), int(immVal[1:]), outString, 0)

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

        outInst = Instruction(binToDecode.replace(' ', ''), op.strip(),
                              rd[1:-2], immVal[:-2], lslNum[4:], outString, 0)

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

        outInst = Instruction(binToDecode.replace(' ', ''), op.strip(),
                              rt[1:-2], rn[2:-2], offsetVal[1:-2], outString, 0)

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

        outInst = Instruction(binToDecode.replace(' ', ''), op.strip(),
                              rt[1:-2], offsetVal[1:], '33', outString, 0)

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

        outInst = Instruction(binToDecode.replace(' ', ''), op.strip(),
                              offsetVal[1:], '33', '33', outString, 0)

        return outInst

    def decodeNop(self, memIndex):

        outInst = Instruction(self.formatBin(0).replace(' ', ''), 'NOP',
                              '33', '33', '33', self.formatBin(0) + '\t' + str(memIndex) + '\t' + 'NOP' + '\n', 0)
        return outInst

    def decodeBreak(self, binToDecode, memIndex):

        outInst = Instruction(binToDecode, 'BREAK',
                              '33', '33', '33',
                              self.formatBin(binToDecode) + '\t' + str(memIndex) + '\t' + 'BREAK' + '\n', 0)

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
        fileWrite = open(outFile + "_dis.txt", 'w')
        rList = [1104, 1112, 1360, 1624, 1690, 1691, 1692, 1872]
        iList = [1160, 1161, 1672, 1673]
        inst = fileRead.readline()
        memLoc = 96
        instList = []
        memoryMap = {}
        while inst != "":
            subStr = inst[0:11]
            value = int(subStr, 2)
            i = 0
            # R-Type Instruction Encoding
            if value in rList and not self.didBreak:
                # fileWrite.write(self.decodeRType(inst, memLoc))
                instList.append(self.decodeRType(inst, memLoc))

                # Immediate Instruction Encoding
            elif value in iList and not self.didBreak:
                # fileWrite.write(self.decodeIType(inst, memLoc))
                instList.append(self.decodeIType(inst, memLoc))

                # Unconditional Branches
            elif value > 159 and value < 192 and not self.didBreak:
                # fileWrite.write(self.decodeBType(inst, memLoc))
                instList.append(self.decodeBType(inst, memLoc))

                # Conditional Branches
            elif value > 1439 and value < 1456 and not self.didBreak:
                # fileWrite.write(self.decodeCBType(inst, memLoc))
                instList.append(self.decodeCBType(inst, memLoc))

                # Decode Wide Instruction Type
            elif ((value > 1683 and value < 1688) or (value > 1939 and value < 1944)) and not self.didBreak:
                # fileWrite.write(self.decodeIWType(inst, memLoc))
                instList.append(self.decodeIWType(inst, memLoc))

                # Load Store Instructions
            elif (value == 1984 or value == 1986) and not self.didBreak:
                # fileWrite.write(self.decodeDType(inst, memLoc))
                instList.append(self.decodeDType(inst, memLoc))

                # Break Statement
            elif value == 2038 and not self.didBreak:
                # fileWrite.write(self.decodeBreak(inst, memLoc))
                instList.append(self.decodeBreak(inst, memLoc))
                self.didBreak = True

                # NoOp Instruction
            elif int(inst) == 0 and not self.didBreak:
                # fileWrite.write(self.decodeNop(memLoc))
                instList.append(self.decodeNop(memLoc))

                # Else value to be loaded into memory
            else:
                # fileWrite.write(inst.rstrip() + '\t' + str(memLoc) + '\t' + str(self.binToSignedInt(int(inst))) + '\n')
                if inst[0] == '1':
                    number = str(self.binToSignedInt(int(inst)))
                else:
                    number = str(int(inst, 2))

                instList.append(Instruction(inst, '', number, '33', '33', (inst.rstrip() + '\t' + str(memLoc) + '\t' + number + '\n'), memLoc))

            memLoc += 4
            inst = fileRead.readline()

        # Iterates through all the instructions and prints them
        for i in range(len(instList)):
            instList[i].printInstruction(fileWrite)
            memoryMap.update({(96 + (4 * i)): instList[i]})

        fileRead.close()
        fileWrite.close()

        # Returns a map of the memory with addresses in decimal. Also returns the first available address
        # InstList is a misnomer, LaKomski wants us to collect any data after the break for our simulator
        return State(memoryMap, (len(instList) * 4 + 92), outFile)


################################################################################
# Class Disassembler Ends Here                                                 #
################################################################################
simCity = Simulator(Disassembler().run()).run()

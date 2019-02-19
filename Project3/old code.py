# # Resetting the pipe register to make sure we're starting fresh every time
# self.cpuState.IFID.regReset()
# if self.cpuState.pcAddr <= self.cpuState.endIAddr:
#     self.cpuState.IFID.IFIDInstr = self.cpuState.memoryMap[self.cpuState.pcAddr]
#     self.setControlSigs()
#     self.cpuState.pcAddr += 4
# print'IF Stage for PC: ' + str(self.cpuState.pcAddr)
# self.cpuState.IFID.printPipeReg()
#
#
# def setControlSigs(self):
#     # EX Control Signals
#     ALUSrcList = {'ADDI', 'SUBI', 'LSR', 'LSL', 'MOVK', 'MOVZ', 'LDUR', 'STUR', 'CBZ', 'CBNZ', 'ASR'}
#     if self.cpuState.IFID.IFIDInstr.operation in ALUSrcList:
#         self.cpuState.IFID.ALUSrc = 1
#     self.cpuState.IFID.ALUOp = self.cpuState.IFID.IFIDInstr.operation
#
#     # MEM Control Signals
#     if self.cpuState.IFID.IFIDInstr.operation == 'STUR':
#         self.cpuState.IFID.MemWrite = 1
#     elif self.cpuState.IFID.IFIDInstr.operation == 'LDUR':
#         self.cpuState.IFID.MemRead = 1
#     if self.cpuState.IFID.IFIDInstr.operation == 'B':
#         self.cpuState.IFID.PCSrc = 1
#
#     # WB Control Signals
#     WBInstList = {'ADD', 'SUB', 'ADDI', 'SUBI', 'LSL', 'LSR', 'ASR', 'AND', 'ORR', 'EOR', 'MOVK', 'MOVZ', 'LDUR'}
#     if self.cpuState.IFID.IFIDInstr.operation in WBInstList:
#         self.cpuState.IFID.MemToReg = 1
#         self.cpuState.IFID.RegWrite = 1

# class InstructionDecodeUnit:
#
#     def __init__(self, state):
#         self.cpuState = state
#
#     def instDecode(self):
#         if self.cpuState.IFID.ALUOp in {'NOP', 0, 'BREAK'}:
#             self.cpuState.IDEX = copy(self.cpuState.IFID)
#             return
#
#         readData1 = 0xDEADBEEF
#         readData2 = 0xDEADBEEF
#         immediate = self.cpuState.IFID.IFIDInstr.argThree
#         writeReg = self.cpuState.IFID.IFIDInstr.argOne
#
#         # Read Data 1
#         # Special MOV Case
#         if self.cpuState.IFID.IFIDInstr.operation[:-1] == 'MOV':
#             readData1 = self.cpuState.IFID.IFIDInstr.argTwo
#
#         elif int(self.cpuState.IFID.IFIDInstr.argTwo) < 32:
#             readData1 = int(self.cpuState.registers[int(self.cpuState.IFID.IFIDInstr.argTwo)])
#
#         # Read Data 2
#         # Store case, read data 2 is the write data
#         if self.cpuState.IFID.IFIDInstr.operation == 'STUR':
#             print "Arg1: ", self.cpuState.IFID.IFIDInstr.argOne, "RegisterValue: ", self.cpuState.registers[
#                 self.cpuState.IFID.IFIDInstr.argOne]
#             readData2 = int(self.cpuState.registers[self.cpuState.IFID.IFIDInstr.argOne])
#
#         elif int(self.cpuState.IFID.IFIDInstr.argThree) < 32:
#             readData2 = int(self.cpuState.registers[int(self.cpuState.IFID.IFIDInstr.argThree)])
#
#         # Immediate logic
#         if self.cpuState.IFID.IFIDInstr.operation == 'B':
#             immediate = self.cpuState.IFID.IFIDInstr.argOne
#
#         elif self.cpuState.IFID.IFIDInstr.operation in {'CBZ', 'CBNZ'}:
#             immediate = self.cpuState.IFID.IFIDInstr.argTwo
#
#         self.cpuState.IFID.IDEXReadData1 = readData1
#         self.cpuState.IFID.IDEXReadData2 = readData2
#         self.cpuState.IFID.IDEXImmValue = immediate
#         self.cpuState.IFID.IDEXWriteReg = writeReg
#
#         self.cpuState.IDEX = copy(self.cpuState.IFID)
#
#         # Debugging Below:
#         print self.cpuState.IFID.printPipeReg()

# if self.cpuState.IDEX.ALUOp in {'NOP', 0, 'BREAK'}:
#     self.cpuState.EXMEM = copy(self.cpuState.IDEX)
#     return
#
# # Importing values from pipeline register
# ALUOp = self.cpuState.IDEX.ALUOp
# ALUSrc = self.cpuState.IDEX.ALUSrc
# readData1 = self.cpuState.IDEX.IDEXReadData1
# readData2 = self.cpuState.IDEX.IDEXReadData2
# immediate = self.cpuState.IDEX.IDEXImmValue
#
# # Opcode dictionary to simplify syntax for simple operations
# simpOps = {'ADD': operator.add, 'SUB': operator.sub, 'LSL': operator.lshift, 'ASR': operator.rshift,
#            'AND': operator.and_, 'ORR': operator.or_, 'EOR': operator.xor}
#
# # Local holders for outgoing variables
# ALUResult = 0
#
# # TODO: CBZ, CBNZ in IF module I believe
# if ALUSrc:
#     if ALUOp in simpOps:
#         ALUResult = simpOps[ALUOp](readData1, immediate)
#
#     elif ALUOp[:-1] in simpOps:
#         ALUResult = simpOps[ALUOp[:-1]](readData1, immediate)
#
#     elif ALUOp == 'LSR':
#         LSRResult = readData1 // 2 ** immediate
#         if LSRResult < 0 and 2 ** immediate != 1:
#             LSRResult *= -1
#         ALUResult = LSRResult
#
#     elif ALUOp in {'LDUR', 'STUR'}:
#         ALUResult = readData1 + (4 * immediate)
#
#     elif ALUOp == 'MOVK':
#         mask = 0xFFFF << immediate
#         ALUResult = ALUResult & ~mask
#         ALUResult = ALUResult | (readData1 << immediate)
#
#     # Else MOVZ
#     else:
#         ALUResult = readData1 << immediate
#
# # Not immediate operation
# else:
#     ALUResult = simpOps[ALUOp](readData1, readData2)
#
# # Moving the register further down the pipeline
# self.cpuState.IDEX.EXMEMALUResult = ALUResult
# # Writing values through from one pipe register to the next, these are untouched by EX
# self.cpuState.IDEX.EXMEMMemWriteData = self.cpuState.IDEX.IDEXReadData2
# self.cpuState.IDEX.EXMEMWriteReg = self.cpuState.IDEX.IDEXWriteReg
#
# self.cpuState.EXMEM = copy(self.cpuState.IDEX)

#
#
#     if self.cpuState.EXMEM.ALUOp in {'NOP', 0, 'BREAK'}:
#         self.cpuState.MEMWB = copy(self.cpuState.EXMEM)
#         return
#
#     if self.cpuState.EXMEM.MemWrite:
#         self.accessMemory(self.cpuState.EXMEM.EXMEMALUResult, self.cpuState.EXMEM.MemRead,
#                           self.cpuState.EXMEM.EXMEMMemWriteData)
#
#     elif self.cpuState.EXMEM.MemRead:
#         self.cpuState.EXMEM.MEMWBData2Write = self.accessMemory(self.cpuState.EXMEM.EXMEMALUResult,
#                                                                 self.cpuState.EXMEM.MemRead,
#                                                                 self.cpuState.EXMEM.EXMEMMemWriteData)
#
#     if not self.cpuState.EXMEM.MemRead:
#         self.cpuState.EXMEM.MEMWBData2Write = self.cpuState.EXMEM.EXMEMALUResult
#     self.cpuState.EXMEM.MEMWBWriteReg = self.cpuState.EXMEM.EXMEMWriteReg
#     self.cpuState.MEMWB = copy(self.cpuState.EXMEM)
#
# # accessMemory, takes a memory location and what should be done to it and checks it for validity, crashes otherwise
# # Writes the data if the action was a write and the address is valid, returns the read data if its a read.
# def accessMemory(self, address, isRead, dataToWrite=''):
#     # If it's greater than it is trying to read or write from an address that's not restricted
#     if address > self.cpuState.endIAddr:
#         # If we are trying to read from an address that is just junk memory
#         if isRead == 1:
#             if (int(address) in self.cpuState.memoryMap):
#                 return self.cpuState.memoryMap[int(address)]
#             else:
#                 sys.exit('You tried to read from memory that was not written to by you')
#
#         else:
#             self.cpuState.endOfData = int(address)
#             self.cpuState.memoryMap.update({int(address): dataToWrite})
#
#     else:
#         sys.exit('You attempted to read or write to reserved memory, IE: system memory, instruction memory, ect.')
def outputState(self):
    #     # ensure extra end line for next phase of output
    #     self.simWrite.write("=====================\n")
    #     self.simWrite.write(
    #         "cycle:%d\t%s\n" % (
    #             self.cycleCount, self.memoryMap[self.pcAddr].formattedString[38:]))
    #     self.simWrite.write("registers:\n")
    #     self.simWrite.write(
    #         "r00:\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n" % (self.registers[0], self.registers[1],
    #                                                     self.registers[2], self.registers[3],
    #                                                     self.registers[4], self.registers[5],
    #                                                     self.registers[6], self.registers[7]))
    #
    #     self.simWrite.write(
    #         "r08:\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n" % (self.registers[8], self.registers[9],
    #                                                     self.registers[10], self.registers[11],
    #                                                     self.registers[12], self.registers[13],
    #                                                     self.registers[14], self.registers[15]))
    #
    #     self.simWrite.write(
    #         "r16:\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n" % (self.registers[16], self.registers[17],
    #                                                     self.registers[18], self.registers[19],
    #                                                     self.registers[20], self.registers[21],
    #                                                     self.registers[22], self.registers[23]))
    #
    #     self.simWrite.write(
    #         "r24:\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n\n" % (self.registers[24], self.registers[25],
    #                                                       self.registers[26], self.registers[27],
    #                                                       self.registers[28], self.registers[29],
    #                                                       self.registers[30], self.registers[31]))
    #     self.simWrite.write("data:\n")
    #
    #     # print memMap
    #     addrIndex = self.endIAddr + 4
    #     # These work now
    #     # print self.endOfData
    #     # print self.endIAddr
    #     # counter for now to make functional, must think of something cooler...
    #
    #     while (addrIndex <= self.endOfData):
    #         self.simWrite.write(str(addrIndex) + ':\t')
    #
    #         # loop will force 8 writes even if the index is
    #         for i in range(8):
    #             if int(addrIndex) in self.memoryMap:
    #                 self.simWrite.write(str(self.memoryMap[int(addrIndex)]) + "\t")
    #             else:
    #                 self.simWrite.write('0\t')
    #
    #             addrIndex += 4
    #
    #         self.simWrite.write("\n")
    #
    #     self.simWrite.write("\n")


# class Simulator:
#
#     def __init__(self, simState):
#         self.state = simState
#
#     # 'Graceful crash' w/ some debug code
#     def CRASH(self, errorMSG='Fatal Error'):
#         print errorMSG
#         print self.state.memoryMap[self.state.pcAddr].formattedString[38:]
#         sys.exit()
#
#     # accessMemory, takes a memory location and what should be done to it and checks it for validity, crashes otherwise
#     # Writes the data if the action was a write and the address is valid, returns the read data if its a read.
#     def accessMemory(self, address, readOrWrite, dataToWrite=''):
#         # If it's greater than it is trying to read or write from an address that's not restricted
#         if address > self.state.endIAddr:
#             # If we are trying to read from an address that is just junk memory
#             if readOrWrite == 'r':
#                 try:
#                     return self.state.memoryMap[int(address)]
#                 except KeyError:
#                     self.CRASH('You tried to read from memory that was not written to by you')
#             else:
#                 self.state.endOfData = int(address)
#                 self.state.memoryMap.update({int(address): dataToWrite})
#
#         else:
#             self.CRASH('You attempted to read or write to reserved memory, IE: system memory, instruction memory, ect.')
#
#     # Does the branch validation and branches the PC
#     def branch(self, bOffset):
#         # Compute target address PC + (Offset * 4)
#         targetAddr = self.state.pcAddr + (bOffset * 4)
#
#         # Determine if this is legal jump, for error message before crash
#         if targetAddr > self.state.endIAddr or targetAddr < 96:
#             self.CRASH('You tried to branch out of instruction memory, ya dingus!')
#         # Set PC to this instruction
#         else:
#             # One of two special cases where we miss the end of the sim while loop
#             self.state.cycleCount += 1
#             self.state.outputState()
#             self.state.pcAddr = targetAddr
#
#     # running the simulator after all data has been inputted into the data structures
#     # from the disassembler.
#     # pass state object to run function.
#     def run(self):
#
#         while self.state.pcAddr <= self.state.endIAddr:
#             test = self.state.memoryMap[self.state.pcAddr].operation
#             # both functions assume immediate operand will be located in the r2 register.
#             if test == "ADD":
#                 self.state.registers[int(self.state.memoryMap[self.state.pcAddr].argOne)] = self.state.registers[int(
#                     self.state.memoryMap[self.state.pcAddr].argTwo)] + self.state.registers[int(
#                     self.state.memoryMap[self.state.pcAddr].argThree)]
#
#             elif test == "ADDI":
#                 self.state.registers[int(self.state.memoryMap[self.state.pcAddr].argOne)] = self.state.registers[int(
#                     self.state.memoryMap[self.state.pcAddr].argTwo)] + int(
#                     self.state.memoryMap[self.state.pcAddr].argThree)
#
#             # both functions assume immediate operand will be located in the r2 register.
#             elif test == "SUB":
#                 self.state.registers[int(self.state.memoryMap[self.state.pcAddr].argOne)] = self.state.registers[int(
#                     self.state.memoryMap[self.state.pcAddr].argTwo)] - self.state.registers[int(
#                     self.state.memoryMap[self.state.pcAddr].argThree)]
#
#             elif test == "SUBI":
#                 self.state.registers[int(self.state.memoryMap[self.state.pcAddr].argOne)] = self.state.registers[int(
#                     self.state.memoryMap[self.state.pcAddr].argTwo)] - int(
#                     self.state.memoryMap[self.state.pcAddr].argThree)
#
#             elif test == "AND":
#                 self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] = self.state.registers[int(
#                     self.state.memoryMap[self.state.pcAddr].argTwo)] & self.state.registers[int(
#                     self.state.memoryMap[self.state.pcAddr].argThree)]
#
#             elif test == "ORR":
#                 self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] = self.state.registers[int(
#                     self.state.memoryMap[self.state.pcAddr].argTwo)] | self.state.registers[int(
#                     self.state.memoryMap[self.state.pcAddr].argThree)]
#
#             elif test == "EOR":
#                 self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] = self.state.registers[int(
#                     self.state.memoryMap[self.state.pcAddr].argTwo)] ^ self.state.registers[int(
#                     self.state.memoryMap[self.state.pcAddr].argThree)]
#
#             elif test == "LSL":
#                 self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] = self.state.registers[int(
#                     self.state.memoryMap[self.state.pcAddr].argTwo)] << int(
#                     self.state.memoryMap[self.state.pcAddr].argThree)
#
#             elif test == "LSR":
#                 shamt = 2 ** int(self.state.memoryMap[self.state.pcAddr].argThree)
#                 val = int(self.state.registers[int(self.state.memoryMap[self.state.pcAddr].argTwo)]) // shamt
#                 if val < 0 and shamt != 1:
#                     val *= -1
#                 self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] = val
#
#             elif test == "ASR":
#                 self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] = self.state.registers[int(
#                     self.state.memoryMap[self.state.pcAddr].argTwo)] >> int(
#                     self.state.memoryMap[self.state.pcAddr].argThree)
#
#             elif test == "LDUR":
#                 self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] = self.accessMemory(
#                     self.state.registers[self.state.memoryMap[self.state.pcAddr].argTwo] + (4 *
#                                                                                             self.state.memoryMap[
#                                                                                                 self.state.pcAddr].argThree),
#                     'r')
#
#             elif test == "STUR":
#                 self.accessMemory(self.state.registers[self.state.memoryMap[self.state.pcAddr].argTwo] + (
#                         4 * self.state.memoryMap[self.state.pcAddr].argThree), 'w',
#                                   self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne])
#
#             elif test == "MOVK":
#                 mask = 0xFFFF << self.state.memoryMap[self.state.pcAddr].argThree
#                 self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] = self.state.registers[
#                                                                                            self.state.memoryMap[
#                                                                                                self.state.pcAddr].argOne] & ~mask
#                 self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] = self.state.registers[
#                                                                                            self.state.memoryMap[
#                                                                                                self.state.pcAddr].argOne] | (
#                                                                                                self.state.memoryMap[
#                                                                                                    self.state.pcAddr].argTwo <<
#                                                                                                self.state.memoryMap[
#                                                                                                    self.state.pcAddr].argThree)
#
#             elif test == 'MOVZ':
#                 self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] = self.state.memoryMap[
#                                                                                            self.state.pcAddr].argTwo << \
#                                                                                        self.state.memoryMap[
#                                                                                            self.state.pcAddr].argThree
#
#             elif test == "B":
#                 self.branch(self.state.memoryMap[self.state.pcAddr].argOne)
#                 # Continue the loop instruction to miss the bottom PC +4 increment
#                 continue
#
#             elif test == "CBZ":
#                 if self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] == 0:
#                     self.branch(self.state.memoryMap[self.state.pcAddr].argTwo)
#                     continue
#
#
#             elif test == "CBNZ":
#                 if self.state.registers[self.state.memoryMap[self.state.pcAddr].argOne] != 0:
#                     self.branch(self.state.memoryMap[self.state.pcAddr].argTwo)
#                     continue
#
#             elif test == "BREAK":
#                 # The second of two special cases where we miss the end of the loop
#                 self.state.cycleCount += 1
#                 self.state.outputState()
#                 break
#                 # Looks like he just wants us to use break to signal the end of the program
#
#             # NOP instruction if it is not one of the other instructions. It does nothing and does not need a check
#             self.state.cycleCount += 1
#             self.state.outputState()
#             self.state.pcAddr += 4
#
#     class PipeReg(object):
#         def __init__(self):
#             # Pipeline registers
#             self.PCSrc = 0
#             self.RegWrite = 0
#             self.ALUSrc = 0
#             self.ALUOp = 0
#             self.MemWrite = 0
#             self.MemRead = 0
#             self.MemToReg = 0
#
#             self.IFIDInstr = 'h'
#
#             self.IDEXReadData1 = 'i'
#             self.IDEXReadData2 = 'j'
#             self.IDEXImmValue = 'k'
#             self.IDEXWriteReg = 'l'
#
#             self.EXMEMBranchAddr = 'm'
#             self.EXMEMALUResult = 'n'
#             self.EXMEMMemWriteData = 'o'
#             self.EXMEMWriteReg = 'p'
#
#             self.MEMWBData2Write = 'q'
#             self.MEMWBWriteReg = 'r'
#
#         def regReset(self):
#             self.__init__()
#             self.ALUOp = 'NOP'
#
#         def printPipeReg(self):
#             pprint(self.__dict__, indent=2)
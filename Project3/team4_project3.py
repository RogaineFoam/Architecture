# Project 3, Pepeline Simulator
# Sam Pugh, William Fallin
import sys
import operator
from pprint import pprint

class Cache:

    def __init__(self, state):
        self.cpuState = state
        self.sets = [CacheSet(), CacheSet(), CacheSet(), CacheSet()]
        self.missedList = []

    # isRead = flag for determining whether is read or write.
    def accessMem(self, address, isRead, dataToWrite):
        tagMask = 4294967264  # -> 11111111111111111111111111100000
        setMask = 24  # -> 0000000000000000000000000011000
        address1 = 0xDEADBEEF
        address2 = 0xDEADBEEF
        data1 = 0
        data2 = 0

        # dataWordNum, reflects which of the two words in a block we'll write to
        dataWordNum = 0

        # If given address is aligned on 96
        if address % 8 == 0:
            address1 = address
            address2 = address + 4
        elif address % 8 != 0:
            address1 = address - 4
            address2 = address
            dataWordNum = 1

        # You can write to addresses that aren't in the map, this 'if' avoids a key error
        if isRead:
            data1 = self.cpuState.memoryMap[address1]
            data2 = self.cpuState.memoryMap[address2]

        if not isRead:
            if address <= self.cpuState.endIAddr:
                sys.exit('you tried to write to instruction memory, ya dingus')
            else:
                if address1 == address:
                    data1 = dataToWrite
                else:
                    data2 = dataToWrite

        setNum = (address1 & setMask) >> 3
        tag = (address1 & tagMask) >> 5
        isHit = -1

        # If block 0 in the sets we masked is valid and it has a matching tag
        if self.sets[setNum].block[0].valid == 1 and self.sets[setNum].block[0].tag == tag:
            isHit = 0  # Block 0 is a hit!

        elif self.sets[setNum].block[1].valid == 1 and self.sets[setNum].block[1].tag == tag:
            isHit = 1  # Block 1 is a hit!

        # If we hit
        if isHit != -1:
            # if it is a write
            if not isRead:
                # Setting LRU to the block that was not a hit
                self.sets[setNum].lru = int(not isHit)

                # Setting the block to dirty
                self.sets[setNum].block[isHit].dirty = 1

                # Writing data into the block at word dataWordNum
                self.sets[setNum].block[isHit].data[dataWordNum] = dataToWrite

            else:
                # If its a read we just sets LRU
                self.sets[setNum].lru = int(not isHit)

            # Now we're going to return the data that was read, I think we return either way r/w
            return [True, self.sets[setNum].block[isHit].data[dataWordNum]]

        # Now we're in miss territory BOIIIIIIII
        # Remember, address1 is the address for the whole 2 word block that's why we only check the list for address1
        # If it's in the list, then that means this is the second cycle that we've had a miss on this address
        if address1 in self.missedList:
            # If it's there then were gonna remove it bc we're about to stick it in cache
            # This is list comprehension that removes every instance of address1, just in case we have more than one
            self.missedList = [listItem for listItem in self.missedList if listItem != address1]

            # Create new block and stick it in cache
            tempBlock = self.sets[setNum].block[self.sets[setNum].lru]

            # Dirty block, must write to mem
            if tempBlock.dirty == 1:
                self.writeBackBlock(tempBlock, setNum)
                self.writeBackBlock(self.sets[setNum].block[int(not self.sets[setNum].lru)], setNum)

            self.sets[setNum].block[self.sets[setNum].lru] = Block([data1, data2], 1, 0, tag)

            # Now we must update the flags
            if not isRead:
                # If we just wrote to the block it must be sets to dirty
                self.sets[setNum].block[self.sets[setNum].lru].dirty = 1

            # Finally LRU is switched to reflect that we just used current LRU
            self.sets[setNum].lru = int(not self.sets[setNum].lru)

            # Returning the requested word
            return [True, self.sets[setNum].block[int(not self.sets[setNum].lru)].data[dataWordNum]]

        # This is the case where there is a full miss, not in missed list or anything
        else:
            self.missedList.append(address1)
            return [False, 0]

    # Does as the function suggests, writes back the whole cache
    def writeBackWholeCache(self):
        for setNum in range(4):
            self.writeBackBlock(self.sets[setNum].block[0], setNum)
            self.writeBackBlock(self.sets[setNum].block[1], setNum)

    # writeBackBlock, writes back a single block to memory after making sure that it has valid addresses
    def writeBackBlock(self, block, setNum):
        if block.dirty == 1:
            # Getting the tag, which we must manipulate to make it the address
            wbAddr = block.tag
            wbAddr = (wbAddr << 5) + (setNum << 3)

            if wbAddr > self.cpuState.endIAddr:
                self.cpuState.memoryMap.update({int(wbAddr): block.data[0]})
            if wbAddr + 4 > self.cpuState.endIAddr:
                self.cpuState.memoryMap.update({int(wbAddr + 4): block.data[1]})

            block.dirty = 0

        else:
            return


class CacheSet:

    def __init__(self):
        self.block = [Block(), Block()]
        self.lru = 0


class Block:

    def __init__(self, data=[0, 0], valid=0, dirty=0, tag=0):
        self.data = data
        self.valid = valid
        self.dirty = dirty
        self.tag = tag


class Pipeline:

    # State object As Param
    def __init__(self, state):
        self.state = state
        self.IF = InstructionFetchUnit(state)
        self.ID = IssueUnit(state)
        self.EX = AritmeticLogicUnit(state)
        self.MEM = MemoryUnit(state)
        self.WB = WriteBackUnit(state)

    def run(self):
        isBreak = 0
        while (not isBreak):
            self.WB.writeBack()
            self.MEM.memOperations()
            self.EX.crystalMath()
            self.ID.issueInst()
            isBreak = self.IF.instFetch()

            self.state.cycleCount += 1

            if isBreak:
                self.state.cache.writeBackWholeCache()
            self.state.outputPipeline()


class InstructionFetchUnit:

    def __init__(self, state):
        self.cpuState = state
        self.hitBreak = False

    def instFetch(self):
        if self.hitBreak:
            allDests = [inst.argOne for inst in self.cpuState.preIssBuff if inst != -1]
            allDests.extend([inst.argOne for inst in self.cpuState.preMemBuff if inst != -1])
            allDests.extend([inst.argOne for inst in self.cpuState.preALUBuff if inst != -1])
            allDests.extend([inst.argOne for inst in self.cpuState.postMemBuff if inst != -1])
            allDests.extend([inst.argOne for inst in self.cpuState.postALUBuff if inst != -1])

            if len(allDests) == 0:
                return True
            else:
                return False
        else:
            if self.cpuState.pcAddr <= self.cpuState.endIAddr:
                numInstInPreIss = self.cpuState.preIssBuff.count(-1)
                if numInstInPreIss > 1:
                    firstInst = self.cpuState.cache.accessMem(self.cpuState.pcAddr, 1, 0)
                    if firstInst[0]:
                        secondInst = self.cpuState.cache.accessMem(self.cpuState.pcAddr + 4, 1, 0)
                    else:
                        secondInst = [False, 0]

                elif numInstInPreIss == 1:
                    firstInst = self.cpuState.cache.accessMem(self.cpuState.pcAddr, 1, 0)
                    secondInst = [False, 0]

                else:  # numInstInPreIss < 1
                    return False

                if firstInst[0] and firstInst[1].operation in {'B', 'CBZ', 'CBNZ'}:
                    if firstInst[1].operation == 'B':
                        self.cpuState.pcAddr = (firstInst[1].argOne * 4)
                        return False
                    else:
                        allDests = [inst.argOne for inst in self.cpuState.preIssBuff if inst != -1]
                        allDests.extend([inst.argOne for inst in self.cpuState.preMemBuff if inst != -1])
                        allDests.extend([inst.argOne for inst in self.cpuState.preALUBuff if inst != -1])
                        allDests.extend([inst.argOne for inst in self.cpuState.postMemBuff if inst != -1])
                        allDests.extend([inst.argOne for inst in self.cpuState.postALUBuff if inst != -1])

                        if firstInst[1].argOne not in allDests:
                            if firstInst[1].operation == 'CBZ':
                                if self.cpuState.registers[firstInst[1].argOne] == 0:
                                    self.cpuState.pcAddr = firstInst[1].argTwo * 4
                                    return False
                                else:
                                    self.cpuState.pcAddr += 4
                                    return False
                            else:  # is CBNZ
                                if self.cpuState.registers[firstInst[1].argOne] != 0:
                                    self.cpuState.pcAddr = firstInst[1].argTwo * 4
                                    return False
                                else:
                                    self.cpuState.pcAddr += 4
                                    return False
                        else:
                            return False

                elif firstInst[0] and (firstInst[1].operation in {'BREAK', 'NOP'}):
                    if firstInst[1].operation == 'BREAK':
                        self.hitBreak = True
                    self.cpuState.pcAddr += 4
                    return False

                elif firstInst[0] and secondInst[0]:
                    self.issueThisInst(firstInst[1])

                    if secondInst[1].operation in {'BREAK', 'NOP'}:
                        if secondInst[1].operation == 'BREAK':
                            self.hitBreak = True
                        self.cpuState.pcAddr += 8  # May need to be four
                        return False

                    elif secondInst[1].operation in {'B', 'CBZ', 'CBNZ'}:
                        if secondInst[1].operation == 'B':
                            self.cpuState.pcAddr = (secondInst[1].argOne * 4)
                            return False
                        else:
                            allDests = [inst.argOne for inst in self.cpuState.preIssBuff if inst != -1]
                            allDests.extend([inst.argOne for inst in self.cpuState.preMemBuff if inst != -1])
                            allDests.extend([inst.argOne for inst in self.cpuState.preALUBuff if inst != -1])
                            allDests.extend([inst.argOne for inst in self.cpuState.postMemBuff if inst != -1])
                            allDests.extend([inst.argOne for inst in self.cpuState.postALUBuff if inst != -1])

                            if secondInst[1].argOne not in allDests:
                                if secondInst[1].operation == 'CBZ':
                                    if self.cpuState.registers[secondInst[1].argOne] == 0:
                                        self.cpuState.pcAddr = secondInst[1].argTwo * 4
                                        return False
                                    else:
                                        self.cpuState.pcAddr += 8
                                        return False
                                else:  # is CBNZ
                                    if self.cpuState.registers[secondInst[1].argOne] != 0:
                                        self.cpuState.pcAddr = secondInst[1].argTwo * 4
                                        return False
                                    else:
                                        self.cpuState.pcAddr += 8
                                        return False
                            else:
                                return False
                    else:
                        self.issueThisInst(secondInst[1])
                        self.cpuState.pcAddr += 8
                #
                # elif firstInst[0] and not secondInst[1]:
                #     self.issueThisInst(firstInst[1])
                #     self.cpuState.pcAddr += 4

                elif firstInst[0] and (not secondInst[0] or not secondInst[1]):
                    self.issueThisInst(firstInst[1])
                    self.cpuState.pcAddr += 4

    # Sticks intsruction into the lowest open slot in the preissue buffer
    def issueThisInst(self, inst):
        for i in range(4):
            if self.cpuState.preIssBuff[i] == -1:
                self.cpuState.preIssBuff[i] = inst
                return
        sys.exit("error, issueThisInst couldn't find an open slot")


class IssueUnit:

    # Gets state as param like usual
    def __init__(self, state):
        self.cpuState = state

    def issueInst(self):
        curr = 0
        numIssued = 0
        numInPreIssueBuff = 4 - self.cpuState.preIssBuff.count(-1)
        # Register argument postion lists
        firstRegList = {'ADDI', 'SUBI', 'ASR', 'LSL', 'LSR', 'LDUR', 'STUR'}
        bothRegList = {'ADD', 'SUB', 'AND', 'ORR', 'EOR'}
        noRegArgList = {'CBZ', 'CBNZ'}

        while numIssued < 2 and numInPreIssueBuff > 0 and curr < 4:
            issueMe = True
            # get an instruction from preissueBuff starting with element 0
            index = self.cpuState.preIssBuff[curr]
            # make sure there is an instruction to execute
            if index == -1:
                break

            # see if there is room in the following buffers: structural hazard
            # if instruction is a memory instruction and pre mem buff has both positions with -1 in them
            # don't issue the memmory instruction. Should be -1 in position 1 almost always.
            if index.operation in {'LDUR', 'STUR'} and not -1 in self.cpuState.preMemBuff:
                issueMe = False
                # break
            # if another instruction type same for preALUbuff
            if not index.operation in {'LDUR', 'STUR'} and not -1 in self.cpuState.preALUBuff:
                issueMe = False
                # break

            # Getting arguments to check against in the other buffers
            if index.operation in firstRegList:
                argOne = index.argTwo
                argTwo = -1
            elif index.operation in bothRegList:
                argOne = index.argTwo
                argTwo = index.argThree
            # This'll be the case for MOVK and MOVZ, they have little hazard potential
            else:
                argOne = -1
                argTwo = -1
            # IndexDest used for WAW checks
            indexDest = index.argOne

            # RAW PREISSUE
            reverseIndex = curr - 1
            while reverseIndex >= 0:
                unIssDest = self.cpuState.preIssBuff[reverseIndex].argOne
                if unIssDest in {argOne, argTwo}:
                    issueMe = False
                    break
                reverseIndex -= 1

            # RAW PREMEM
            preMemDest = [inst.argOne for inst in self.cpuState.preMemBuff if inst != -1]
            for dest in preMemDest:
                if dest in {argOne, argTwo}:
                    issueMe = False
                    break

            # RAW PREALU
            preALUDest = [inst.argOne for inst in self.cpuState.preALUBuff if inst != -1]
            for dest in preALUDest:
                if dest in {argOne, argTwo}:
                    issueMe = False
                    break

            # RAW POSTMEM AND POSTALU
            postMemANDPostALUDest = [inst.argOne for inst in self.cpuState.postMemBuff if inst != -1]
            postMemANDPostALUDest.extend([inst.argOne for inst in self.cpuState.postALUBuff if inst != -1])
            for dest in postMemANDPostALUDest:
                if dest in {argOne, argTwo}:
                    issueMe = False
                    break

            # WAW
            reverseIndex = curr - 1
            while reverseIndex >= 0:
                unIssDest = self.cpuState.preIssBuff[reverseIndex].argOne
                if unIssDest == indexDest:
                    issueMe = False
                    break
                reverseIndex -= 1

            allDestList = preMemDest
            allDestList.extend(preALUDest)
            allDestList.extend(postMemANDPostALUDest)
            if indexDest in allDestList:
                issueMe = False

            # After it passes all checks
            if issueMe:
                numIssued += 1
                # copy the instruction to the appropriate buffer
                # the assumption here is that we will have a -1 in the right spot! Think we will.
                if index.operation in {'LDUR', 'STUR'}:
                    for i in range(2):
                        if self.cpuState.preMemBuff[i] == -1:
                            self.cpuState.preMemBuff[i] = index
                            break
                    # self.cpuState.preMemBuff.append(index)  # [self.cpuState.preMemBuff.index(-1)] = index
                else:
                    for i in range(2):
                        if self.cpuState.preALUBuff[i] == -1:
                            self.cpuState.preALUBuff[i] = index
                            break
                    # self.cpuState.preALUBuff.append(index)  # [self.cpuState.preALUBuff.index(-1)] = index

                # move the instrs in the preissue buff down one level
                self.cpuState.preIssBuff[0:curr] = self.cpuState.preIssBuff[0:curr]
                self.cpuState.preIssBuff[curr:3] = self.cpuState.preIssBuff[
                                                   curr + 1:]  # dropped 4, think will go to end always
                self.cpuState.preIssBuff[3] = -1
                numInPreIssueBuff -= 1
            else:
                curr += 1


class AritmeticLogicUnit:

    def __init__(self, state):
        self.cpuState = state

    def crystalMath(self):
        if self.cpuState.postALUBuff[0] != -1:
            return
        else:
            # Opcode dictionary to simplify syntax for simple operations
            immOps = {'ADDI', 'SUBI', 'LSL', 'LSR', 'ASR', 'MOVZ', 'MOVK'}
            simpOps = {'ADD': operator.add, 'SUB': operator.sub, 'LSL': operator.lshift, 'ASR': operator.rshift,
                       'AND': operator.and_, 'ORR': operator.or_, 'EOR': operator.xor}
            inst = self.cpuState.preALUBuff[0]
            
            # Is a valid instruction
            if inst != -1:
                ALUOp = inst.operation
                # Temp holder variable
                ALUResult = 0
                
                if ALUOp in immOps:
                    if ALUOp in simpOps:
                        ALUResult = simpOps[ALUOp](self.cpuState.registers[inst.argTwo], inst.argThree)

                    elif ALUOp[:-1] in simpOps:
                        ALUResult = simpOps[ALUOp[:-1]](self.cpuState.registers[inst.argTwo], inst.argThree)

                    elif ALUOp == 'LSR':
                        LSRResult = self.cpuState.registers[inst.argTwo] // 2 ** inst.argThree
                        if LSRResult < 0 and 2 ** inst.argThree != 1:
                            LSRResult *= -1
                        ALUResult = LSRResult

                    elif ALUOp == 'MOVK':
                        mask = 0xFFFF << inst.argThree
                        ALUResult = ALUResult & ~mask
                        ALUResult = ALUResult | (inst.argTwo << inst.argThree)

                    # Else MOVZ
                    else:
                        ALUResult = inst.argTwo << inst.argThree
                        # Not immediate operation
                else:
                    ALUResult = simpOps[ALUOp](self.cpuState.registers[inst.argTwo], self.cpuState.registers[inst.argThree])

                inst.argTwo = ALUResult

                self.cpuState.postALUBuff[0] = inst

                self.cpuState.preALUBuff[0] = self.cpuState.preALUBuff[1]
                self.cpuState.preALUBuff[1] = -1
            else:
                return

class MemoryUnit:

    def __init__(self, state):
        self.cpuState = state

    def memOperations(self):
        if self.cpuState.postMemBuff[0] != -1:
            return
        else:
            inst = self.cpuState.preMemBuff[0]
            if inst != -1:
                if inst.operation == 'LDUR':
                    addr = self.cpuState.registers[inst.argTwo] + (4 * inst.argThree)
                    success = self.cpuState.cache.accessMem(addr, 1, 0)

                    if success[0]:
                        inst.argTwo = success[1]

                        self.cpuState.postMemBuff[0] = inst

                        self.cpuState.preMemBuff[0] = self.cpuState.preMemBuff[1]
                        self.cpuState.preMemBuff[1] = -1

                    else:
                        return

                else:  # inst.operation == 'STUR'
                    addr = self.cpuState.registers[inst.argTwo] + (4 * inst.argThree)
                    success = self.cpuState.cache.accessMem(addr, 0, self.cpuState.registers[inst.argOne])

                    if success[0]:
                        self.cpuState.preMemBuff[0] = self.cpuState.preMemBuff[1]
                        self.cpuState.preMemBuff[1] = -1

                    else:
                        return
            else:
                    return


class WriteBackUnit:

    def __init__(self, state):
        self.cpuState = state

    def writeBack(self):
        writeBack1 = self.cpuState.postALUBuff[0]
        writeBack2 = self.cpuState.postMemBuff[0]

        if writeBack1 != -1:
            self.cpuState.registers[writeBack1.argOne] = writeBack1.argTwo
            self.cpuState.postALUBuff[0] = -1
        if writeBack2 != -1:
            self.cpuState.registers[writeBack2.argOne] = writeBack2.argTwo
            self.cpuState.postMemBuff[0] = -1


# class that will hold all of the needed elements for Instructions
class Instruction:
    # Define all local variables on construction
    def __init__(self, machineCode='', textOp='', argument1='33', argument2='33', argument3='33', stringToPrint='',
                 memLoc='96'):
        self.binInstr = machineCode.strip('\n')
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
        # sets up the output file and fix formatting
        self.outFile = outFile + "_pipeline.txt"

        # open the file in write mode
        self.simWrite = open(self.outFile, 'w')

        # Generate an array of 32 registers and initialize them to 0
        self.registers = [0] * 32

        # Different buffers that are req
        self.preIssBuff = [-1, -1, -1, -1]  # Maxsize = 4
        self.preALUBuff = [-1, -1]
        self.postALUBuff = [-1]  # Maxsize = 1
        self.preMemBuff = [-1, -1]
        self.postMemBuff = [-1]  # Maxsize = 1

        # Current PC location in program
        self.pcAddr = 96

        # Current cycle count
        self.cycleCount = 0

        # Dictionary to hold location in memory and index of instruction
        self.memoryMap = memMap

        # Cache that manages the memory
        self.cache = Cache(self)

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

    def trimInst(self, instStr):
        index = 0
        for i in range(len(instStr)):
            if instStr[i] in {'A', 'S', 'L', 'O', 'E', 'C', 'M', 'B', 'N'}:
                return instStr[i:].rstrip()

        
    def outputPipeline(self):

        # Here is where we need to output the issue buffers
        # Hard Coded for now
        self.simWrite.write("--------------------\n")
        self.simWrite.write("Cycle:%d\n\n" % self.cycleCount)
        self.simWrite.write("Pre-Issue Buffer:\n")
        self.simWrite.write("\tEntry 0: [" + (self.trimInst(self.preIssBuff[0].formattedString[38:-1]) if self.preIssBuff[0] != -1 else ' ') + "]\n")
        self.simWrite.write("\tEntry 1: [" + (self.trimInst(self.preIssBuff[1].formattedString[38:-1]) if self.preIssBuff[1] != -1 else ' ') + "]\n")
        self.simWrite.write("\tEntry 2: [" + (self.trimInst(self.preIssBuff[2].formattedString[38:-1]) if self.preIssBuff[2] != -1 else ' ') + "]\n")
        self.simWrite.write("\tEntry 3: [" + (self.trimInst(self.preIssBuff[3].formattedString[38:-1]) if self.preIssBuff[3] != -1 else ' ') + "]\n")
        self.simWrite.write("Pre_ALU Queue:\n")
        self.simWrite.write("\tEntry 0: [" + (self.trimInst(self.preALUBuff[0].formattedString[38:-1]) if self.preALUBuff[0] != -1 else ' ') + "]\n")
        self.simWrite.write("\tEntry 1: [" + (self.trimInst(self.preALUBuff[1].formattedString[38:-1]) if self.preALUBuff[1] != -1 else ' ') + "]\n")
        self.simWrite.write("Post_ALU Queue:\n")
        self.simWrite.write("\tEntry 0: [" + (self.trimInst(self.postALUBuff[0].formattedString[38:-1]) if self.postALUBuff[0] != -1 else ' ') + "]\n")
        self.simWrite.write("Pre_MEM Queue:\n")
        self.simWrite.write("\tEntry0: [" + (self.trimInst(self.preMemBuff[0].formattedString[38:-1]) if self.preMemBuff[0] != -1 else ' ') + "]\n")
        self.simWrite.write("\tEntry1: [" + (self.trimInst(self.preMemBuff[1].formattedString[38:-1]) if self.preMemBuff[1] != -1 else ' ') + "]\n")
        self.simWrite.write("Post_MEM Queue\n")
        self.simWrite.write("\tEntry 0: [" + (self.trimInst(self.postMemBuff[0].formattedString[38:-1]) if self.postMemBuff[0] != -1 else ' ') + "]\n\n")

        # Register Output Starts Here
        self.simWrite.write("Registers\n")
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

        # Here is Where we are going to output the State of the Cache
        i=0
        self.simWrite.write("Cache\n")
        for i in range(4):
            self.simWrite.write("sets %d: LRU=%d\n" % (i, self.cache.sets[i].lru))
            self.simWrite.write("\tEntry 0: [(%d,%d,%d)<%s,%s>]\n" % (self.cache.sets[i].block[0].valid,
                                                                 self.cache.sets[i].block[0].dirty,
                                                                 self.cache.sets[i].block[0].tag,
                                                                 str(self.cache.sets[i].block[0].data[0].binInstr if isinstance(self.cache.sets[i].block[0].data[0], Instruction) else self.cache.sets[i].block[0].data[0]),
                                                                 str(self.cache.sets[i].block[0].data[1].binInstr if isinstance(self.cache.sets[i].block[0].data[1], Instruction) else self.cache.sets[i].block[0].data[1])))

            self.simWrite.write("\tEntry 1: [(%d,%d,%d)<%s,%s>]\n" % (self.cache.sets[i].block[1].valid,
                                                                 self.cache.sets[i].block[1].dirty,
                                                                 self.cache.sets[i].block[1].tag,
                                                                 str(self.cache.sets[i].block[1].data[0].binInstr if isinstance(self.cache.sets[i].block[1].data[0], Instruction) else self.cache.sets[i].block[1].data[0]),
                                                                 str(self.cache.sets[i].block[1].data[1].binInstr if isinstance(self.cache.sets[i].block[1].data[1], Instruction) else self.cache.sets[i].block[1].data[1])))

        self.simWrite.write("\nData:\n")
        addrIndex = self.endIAddr + 4
        while (addrIndex <= self.endOfData):
            self.simWrite.write(str(addrIndex) + ':')

            # loop will force 8 writes even if the index is
            for i in range(8):
                if int(addrIndex) in self.memoryMap:
                    self.simWrite.write(str(self.memoryMap[int(addrIndex)]) + "\t")
                else:
                    self.simWrite.write('0\t')

                addrIndex += 4

            self.simWrite.write("\n")

################################################################################
# State Class Ends Here                                                        #
################################################################################

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
                if inst[0] == '1':
                    number = str(self.binToSignedInt(int(inst)))
                else:
                    number = str(int(inst, 2))

                instList.append(Instruction(inst, '', number, '33', '33',
                                            (inst.rstrip() + '\t' + str(memLoc) + '\t' + number + '\n'), memLoc))

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

pipeLine = Pipeline(Disassembler().run()).run()

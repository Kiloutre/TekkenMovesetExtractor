# Python 3.6.5

from Addresses import GameAddresses, GameClass
from Requirements import getRequirement, getTag2Requirement
import sys
import os

T = GameClass("TekkenGame-Win64-Shipping.exe" )
    
def bToInt(data, offset, length, ed='little'):
    return int.from_bytes(data[offset:offset + length], ed)

def readInt(addr, len, endian='little'):
    return T.readInt(addr, len, endian=endian)
    
def readBytes(addr, len):
    return T.readBytes(addr, len)
    
def readString(addr):
    offset = 0
    while readInt(addr + offset, 1) != 0:
        offset += 1
    return readBytes(addr, offset).decode("ascii")
    
def readStringPtr(addr):
    return readString(readInt(addr, 8))
    
def getDirectionFromFlag(flag):
    return {
        (0): "",
        (1 << 0): "(??0)",
        (1 << 1): "D/B",
        (1 << 2): "D",
        (1 << 3): "D/F",
        (1 << 4): "B",
        (1 << 5): "(??5 - Neutral?)",
        (1 << 6): "F",
        (1 << 7): "U/B",
        (1 << 8): "U",
        (1 << 9): "U/F",
        (1 << 15): "[AUTO]",
    }.get(flag, "?? (0x%x)" % (flag))
    
def getMoveStr(move):
    inputs = ""
    direction = ""
    
    inputflags = move >> 32
    directionflags = move & 0xffffffff

    for i in range(1, 5):
        if inputflags & (1 << (i - 1)):
            inputs += "+%d" % (i)

    direction = getDirectionFromFlag(directionflags)
        
    if direction == "" and inputs == "":
        return None
    if direction == "" and inputs != "":
        return inputs[1:]
    return direction + inputs
    
def getMoveName(id, movelist):
    if id >= len(movelist):
        return {
            32771: 'Death',
            32769: 'Standing',
            32770: 'Crouching',
            32774: 'Downed',
            32775: 'Downed',
            32777: 'Downed face down',
            32778: 'Downed face down',
        }.get(id, 'UNKNOWN-MOVE')
    return movelist[id].name
    
def getRequirementList(requirement_ptr):
    requirement_list = []
    requirement = Requirement(requirement_ptr)
    while requirement.req != 881 and requirement.req != 0:
        requirement_list.append(requirement)
        requirement_ptr += 8
        requirement = Requirement(requirement_ptr)
    return requirement_list
    
class Requirement:
    requirement_size = 0x8
    
    def __init__(self, addr):
        data = readBytes(addr, 0x8)
        self.req = bToInt(data, 0, 4)
        self.param = bToInt(data, 4, 4)
       
    def print(self):
        reqData = getRequirement(self.req)
        reqName = '' if reqData == None else ("(%s) " % (reqData['description']))
        print("R: %d %s| P: %d" % (self.req, reqName, self.param))
        
class ReactionScenario:
    def __init__(self, addr):
        data = readBytes(addr, 0x18)
        self.addr = addr
        
        self.requirements = getRequirementList(bToInt(data, 0x0, 8))
        self.attack_dmg = bToInt(data, 0x8, 4)
        reaction_addr = bToInt(data, 0x10, 8)
        
        reaction_data = readBytes(reaction_addr + 0x50, 24)
        self.moveid_list = [bToInt(reaction_data, (offset * 2), 2) for offset in range (14)]
        
    def print(self):
        print("%d damage" % (self.attack_dmg))
        for req in self.requirements:
            req.print()
        print("0x%x" % (self.addr))
        print(self.moveid_list)
    
class Cancel:
    def __init__(self, addr):
        self.addr = addr
        data = readBytes(addr, 0x28)
        
        self.command = bToInt(data, 0x0, 8)
        self.frame_window_start = bToInt(data, 0x18, 4)
        self.frame_window_end = bToInt(data, 0x1C, 4)
        self.starting_frame = bToInt(data, 0x20, 4)
        self.move_id = bToInt(data, 0x24, 2)
        
        self.requirements = getRequirementList(bToInt(data, 0x8, 8))

    def print(self, movelist=None, printOnlyIfRequirements=False):
        if printOnlyIfRequirements and len(self.requirements) == 0:
            return
        moveName = getMoveName(self.move_id, movelist) if movelist != None else ''
        print("Move: %d [%s]" % (self.move_id, moveName))
        print("Command: %s | %d->%d:%d" % (getMoveStr(self.command), self.frame_window_start, self.frame_window_end, self.starting_frame))
        for req in self.requirements:
            req.print()
        print('')

class Move:
    def __init__(self, addr, id=0):
        self.id = id
        self.addr = addr + (id * 0xB0)
        
        moveBytes = readBytes(self.addr, 0xB0)
        self.name = readString(bToInt(moveBytes, 0, 8))
        self.hitlevel = bToInt(moveBytes, 0x1c, 4)
        self.cancel_ptr = bToInt(moveBytes, 0x20, 8)
        self.reaction_ptr = bToInt(moveBytes, 0x60, 8)
        
        self.u12 = bToInt(moveBytes, 0x74, 4)
        self.u15 = bToInt(moveBytes, 0x98, 4)
        
        self.cancels = []
        self.reactionScenarios = []
        
        if id == 0:
            self.loadCancels()
            if self.hitlevel != 0:
                self.loadReactions()
                
    def __eq__(self, other):
        return self.name == other
                
    def loadReactions(self):
        reaction_ptr = self.reaction_ptr
        reaction = ReactionScenario(reaction_ptr)
        self.reaction_list = [reaction]
        while len(reaction.requirements) != 0:
            reaction_ptr += 0x18
            reaction = ReactionScenario(reaction_ptr)
            self.reaction_list.append(reaction)
            
    def loadCancels(self):
        cancel_ptr = self.cancel_ptr
        cancel = Cancel(cancel_ptr)
        self.cancels = [cancel]
        while cancel.command != 0x8000:
            cancel_ptr += 0x28
            cancel = Cancel(cancel_ptr)
            self.cancels.append(cancel)
            
    def printAttackReactions(self):
        if self.hitlevel == 0:
            print("Not an attack.")
            return
        print("- Reactions: -")
        for reaction in self.reaction_list:
            reaction.print()
            print("\n")
        print("- Reaction END -")
            
    def printCancels(self, movelist, printOnlyIfRequirements=False):
        print("- Cancel list: -")
        for cancel in self.cancels:
            cancel.print(movelist, printOnlyIfRequirements)
        print("- %d cancels. -" % (len(self.cancels)))
        
class Player:
    def __init__(self, addr, id=None):
        self.addr = addr
        self.id = id
    
        motbin_ptr = readInt(addr + 0x14a0, 8)
        
        self.movelist_head = readInt(motbin_ptr + 0x210, 8)
        self.movelist_size = readInt(motbin_ptr + 0x218, 4)
        self.movelist = [Move(self.movelist_head, i) for i in range(self.movelist_size)]
        self.movelist2 = []
        
        self.curr_move = 0
        self.curr_move_ptr = 0
        self.curr_move_name = ''
        self.using_second_movelist = False
        
    def setSecondMovelist(self, movelist):
        self.movelist2 = movelist
        
    def getMovelist(self):
        return self.movelist2 if self.using_second_movelist else self.movelist
        
    def getMoveName(self, id):
        return getMoveName(id, self.getMovelist())
        
    def isUsingSecondMovelist(self):
        return readInt(self.addr + 0x14a0, 8) != readInt(self.addr + 0x14a8, 8)
        
    def getCurrmoveData(self):
        self.using_second_movelist = self.isUsingSecondMovelist()
        self.curr_move = readInt(self.addr + 0x344, 4)
        self.curr_move_name = self.getMoveName(self.curr_move)
        self.curr_move_ptr = readInt(self.addr + 0x220, 8)
        self.curr_move_class = Move(self.curr_move_ptr, 0)
        
    def printCancels(self, printOnlyIfRequirements=True):
        self.getCurrmoveData()
        self.curr_move_class.printCancels(self.getMovelist(), printOnlyIfRequirements)
        
    def printAttackReactions(self):
        self.getCurrmoveData()
        self.curr_move_class.printAttackReactions()
        
    def printId(self):
        if self.id != None:
            print("--- Player %s: ---" % (self.id))
        else:
            print("--- Unknown player ---")
        
    def printBasicData(self):
        self.getCurrmoveData()
        self.printId()
        extraMoveInfo = '(Second movelist)' if self.using_second_movelist else ''
        print("Current move: %d [%s]" % (self.curr_move, self.curr_move_name), extraMoveInfo)
        print("\n")
            
if __name__ == "__main__":
    P1 = Player(GameAddresses.a['p1_ptr'], '1')
    P2 = Player(GameAddresses.a['p2_ptr'], '2')

    P1.setSecondMovelist(P2.movelist)
    P2.setSecondMovelist(P1.movelist)
    
    if len(sys.argv) == 1:
        print("Usage: ListRequirements.py [p1] [p2] (p2 optional)")
        print("Example: ./ListRequirements.py cancels reactions")
        print("Show the list of cancels for p1 and the list of reactions for p2")
        os._exit(1)
    
    p1Show = sys.argv[1]
    p2Show = 'none' if len(sys.argv) == 2 else sys.argv[2]
    
    dict1 = {}
    
    for move in P1.movelist:
        if move in P2.movelist:
            move2 = P2.movelist[P2.movelist.index(move)]
            if move.u15 == move2.u15:
                continue
            dict1[move2.u15] = move.u15
            #print("{ 'id': %d, 'tag2_id': %d }," % (move2.u15, move.u15))
    for key in dict1.keys():
        print("{ 'id': %d, 'tag2_id': %d }," % (key, dict1[key]))
    os._exit(0)
    
    if p1Show != None and p1Show.lower() != "none":
        P1.printBasicData()
        if p1Show.lower().startswith("cancel"):
            P1.printCancels(False)
        elif p1Show.lower().startswith("reaction"):
            P1.printAttackReactions()
        else:
            print("Unrecognized argument: [%s]. Try [cancels/reactions]" % (p1Show))
    
    if p2Show != None and p2Show.lower() != "none":
        P2.printBasicData()
        if p2Show.lower().startswith("cancel"):
            P2.printCancels()
        elif p2Show.lower().startswith("reaction"):
            P2.printAttackReactions()
        else:
            print("Unrecognized argument: [%s]. Try [cancels/reactions]" % (p2Show))
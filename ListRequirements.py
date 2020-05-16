# Python 3.6.5
# This file is used only for debugging purpose and is is not used by the moveset importer/exporter
# Dumping info about movelists and comparing them will be necessary to build reliable alias lists

from Addresses import GameAddresses, GameClass
from Aliases import getRequirement, getTag2Requirement, getProperty
import sys
import os
import json

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
        reqName = '' if reqData == None else ("(%s) " % (reqData['desc']))
        print("R: %d %s| P: %d" % (self.req, reqName, self.param))
        
    def __eq__(self, other):
        return self.param == other.param
        
class ReactionScenario:
    def __init__(self, addr):
        data = readBytes(addr, 0x18)
        self.addr = addr
        
        self.requirements = getRequirementList(bToInt(data, 0x0, 8))
        self.attack_dmg = bToInt(data, 0x8, 4)
        reaction_addr = bToInt(data, 0x10, 8)
        
        reaction_data = readBytes(reaction_addr + 0x50, 24)
        self.moveid_list = [bToInt(reaction_data, (offset * 2), 2) for offset in range (15)]
        self.names = [''] * 15
        
        
    def loadNames(self, movelist):
        for i, n in enumerate(self.names):
            if n == '':
                self.names[i] = getMoveName(self.moveid_list[i], movelist)
                
    def __eq__(self, other):
        if len(self.requirements) !=  len(other.requirements):
            return False
        for r, r2 in zip(self.requirements, other.requirements):
            if r.param != r2.param:
                return False
        return True
        
    def print(self, printReqs=True):
        print("%d damage" % (self.attack_dmg))
        if printReqs:
            for req in self.requirements:
                req.print()
        #print("0x%x" % (self.addr))
        print(self.moveid_list)
        print(self.names)
        
class ExtraProperty:
    def __init__(self, addr):
        data = readBytes(addr, 4 * 3)
        
        self.addr = addr
        self.type = bToInt(data, 0, 4)
        self.id = bToInt(data, 4, 4)
        self.value= bToInt(data, 8, 4)
        
    def dict(self):
        return {
            'type': self.type,
            'id': self.id,
            'value': self.value
        }
        
    def print(self, printAddress=False):
        if printAddress:
            print("%x - " % (self.addr), end='')
        propertyDetails = getProperty(self.id)
        desc = '' if propertyDetails == None else ('| ' + propertyDetails['desc'])
        print("Type: %x | ID: %x | value: %x" % (self.type, self.id, self.value), desc)
        
    def __eq__(self, other):
        return self.type == other.type and self.value == other.value
    
class Cancel:
    def __init__(self, addr):
        self.addr = addr
        data = readBytes(addr, 0x28)
        
        self.command = bToInt(data, 0x0, 8)
        self.frame_window_start = bToInt(data, 0x18, 4)
        self.frame_window_end = bToInt(data, 0x1C, 4)
        self.starting_frame = bToInt(data, 0x20, 4)
        self.move_id = bToInt(data, 0x24, 2)
        self.unknown = bToInt(data, 0x26, 2)
        
        self.name = ''
        
        self.requirements = getRequirementList(bToInt(data, 0x8, 8))
        
    def getName(self, movelist):
        if self.name == '':
            self.name = getMoveName(self.move_id, movelist)
        return self.name
        
    def __eq__(self, other):
        if self.frame_window_start == other.frame_window_start \
            and self.frame_window_end == other.frame_window_end \
            and self.starting_frame == other.starting_frame \
            and self.command == other.command \
            and self.unknown == other.unknown \
            and self.name == other.name:
                return True
        return False

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
        self.extra_property_ptr = bToInt(moveBytes, 0x80, 8)
        
        self.u12 = bToInt(moveBytes, 0x74, 4)
        self.u15 = bToInt(moveBytes, 0x98, 4)
        self.u15_a = bToInt(moveBytes, 0x98, 2)
        self.u15_b = bToInt(moveBytes, 0x9a, 2)
        self.u15_list = [bToInt(moveBytes, 0x98 + x, 1) for x in range(4)]
        
        self.cancels = []
        self.reactionScenarios = []
        self.property_list = []
        self.reaction_list = []
        
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
                
    def loadExtraProperties(self):
        extra_property_ptr = self.extra_property_ptr
        if extra_property_ptr == 0:
            #print("extra_property_ptr = 0")
            return []
        property = ExtraProperty(extra_property_ptr)
        self.property_list = []
        while property.type != 0:
            self.property_list.append(property)
            extra_property_ptr += 12
            property = ExtraProperty(extra_property_ptr)
        return self.property_list
            
    def loadCancels(self):
        cancel_ptr = self.cancel_ptr
        cancel = Cancel(cancel_ptr)
        self.cancels = [cancel]
        while cancel.command != 0x8000:
            cancel_ptr += 0x28
            cancel = Cancel(cancel_ptr)
            self.cancels.append(cancel)
        return self.cancels
        
    def loadCancelNames(self, movelist):
        for cancel in self.cancels:
            cancel.getName(movelist)
        
    def loadReactionNames(self, movelist):
        for reaction in self.reaction_list:
            reaction.loadNames(movelist)
            
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
        
    def printProperties(self):
        self.loadExtraProperties()
        for property in self.property_list:
            property.print()
        
class Player:
    def __init__(self, addr, id=None):
        self.addr = addr
        self.id = id
    
        motbin_ptr = readInt(addr + 0x14a0, 8)
        
        self.name = readStringPtr(motbin_ptr + 8)
        self.uname = self.name.upper()
        
        if self.name[0] == '[':
            self.uname = self.uname[1:-1]
        
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
        
    def getCurrmoveName(self):
        self.getCurrmoveData()
        return self.curr_move_name
        
    def printCancels(self, printOnlyIfRequirements=True):
        self.getCurrmoveData()
        self.curr_move_class.printCancels(self.getMovelist(), printOnlyIfRequirements)
        
    def printProperties(self):
        self.getCurrmoveData()
        self.curr_move_class.printProperties()
        
    def printAttackReactions(self):
        self.getCurrmoveData()
        self.curr_move_class.printAttackReactions()
        
    def getCurrmoveId(self):
        return readInt(self.addr + 0x344, 4)
        
    def getMoveProperties(self, id):
        self.movelist[id].loadExtraProperties()
        return self.movelist[id].property_list
        
    def getCurrmoveProperties(self):
        self.getCurrmoveData()
        self.curr_move_class.loadExtraProperties()
        return self.curr_move_class.property_list
        
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
        
def getSharedMoves(P1, P2):
    return [(move, P2.movelist[P2.movelist.index(move)]) for move in P1.movelist if move in P2.movelist]
    
        
class ExtraProperty2:
    def __init__(self, object):
        self.type = object.type
        self.id = object.id
        self.value = object.value
        
    def __eq__(self, other):
        return self.type == other.type and self.value == other.value and self.id != other.id
        
    
def addTestMapping(key, value):
    global testmapping
    if key not in testmapping.keys():
        testmapping[key] = { value: 1 }
    else:
        if value not in testmapping[key].keys():
            testmapping[key][value] = 1
        else:
            testmapping[key][value] += 1
            
def addUniqueAlias(alias2):
    global extra_move_properties2
    
    for e in extra_move_properties2:
        if e['tag2_id'] == alias2['tag2_id']:
            return False
        
    extra_move_properties2.append(alias2)
        
def isPropAliasUniq(alias):
    global extra_move_properties2
    
    for e in extra_move_properties2:
        if e['tag2_id'] == alias['tag2_id'] and (e['t7_id'] != alias['t7_id']):
            return False
    return True
    
def isPropKeyReliable(key):
    global testmapping
    if key in testmapping:
        if len(testmapping[key].keys()) > 1:
            return False
    return True
        
def saveExtraProperties():
    global extra_move_properties2
    global testmapping
    
    P1 = Player(GameAddresses.a['p1_ptr'], '1')
    P2 = Player(GameAddresses.a['p2_ptr'], '2')
    
    print("Comparing %s to %s..." % (P1.name, P2.name))
    
    if P1.name.upper() != P2.name.upper():
        print("Unmatching movelist names, exiting")
        return
    
    sharedMoves = getSharedMoves(P1, P2)
    aliasedList = []
    fileContent = []
    
    aliasList = []
    
    for tag2_move, t7_move in sharedMoves:
        proplist1 = [ExtraProperty2(t) for t in tag2_move.loadExtraProperties()]
        proplist2 = [ExtraProperty2(t) for t in t7_move.loadExtraProperties()]
        
        for prop in proplist1:
            t7Props = [p for p in proplist2 if p == prop]
            if len(t7Props) != 1:
                continue
            propAlias = {
                'type': prop.type,
                't7_id': t7Props[0].id,
                'tag2_id': prop.id,
                'desc': "(%s) %s" % (P1.uname, tag2_move.name)
            }
            aliasList.append(propAlias)
    
    oldLen = len(extra_move_properties2)
    for alias in aliasList:
        addTestMapping(alias['tag2_id'], alias['t7_id'])
        addUniqueAlias(alias)
        
    new_extra_move_properties = [alias for alias in extra_move_properties2 if isPropAliasUniq(alias) and isPropKeyReliable(alias['tag2_id'])]
    print("%d new aliases." % (len(new_extra_move_properties) - oldLen))
    
    with open("./test.py", "w") as f:
        f.write("extra_move_properties2 = [\n")
        for item in new_extra_move_properties:
            text = "   { 't7_id': 0x%x, 'tag2_id': 0x%x, 'desc': '%s' }," % (item['t7_id'], item['tag2_id'], item['desc'])
            f.write(text + "\n")
        f.write("]\n\n")
        
        f.write("testmapping = " + str(testmapping))
        
    print("File saved.")
    os._exit(0)
    
def addKeyMapping(key, value):
    if key not in requirements_mapping.keys():
        requirements_mapping[key] = { value: 1 }
    else:
        if value not in requirements_mapping[key].keys():
            requirements_mapping[key][value] = 1
        else:
            requirements_mapping[key][value] += 1
    
def isKeyReliable(key):
    if key in requirements_mapping:
        if len(requirements_mapping[key].keys()) > 1:
            return False
    return True
    
def getKeyValue(key):
    threshold = 1.25
    if key in testmapping:
        alias = testmapping[key]
        key_list = [k for k in alias]
        if len(key_list) == 1:
            return key_list[0]
        
        biggest = key_list[0]
        second_biggest = key_list[0]
        
        for k in key_list:
            if alias[k] > alias[biggest]:
                biggest = k
            elif alias[k] > alias[second_biggest] or biggest == second_biggest:
                second_biggest = k
                
        if alias[biggest] > (alias[second_biggest] * threshold):
            #print(alias[biggest], alias[second_biggest])
            return biggest
        #print("ERR-", biggest, alias[biggest], alias[second_biggest])
    return None
        
                    
def saveAliasRequirements():
    P1 = Player(GameAddresses.a['p1_ptr'], '1')
    P2 = Player(GameAddresses.a['p2_ptr'], '2')
    
    print("Comparing %s to %s..." % (P1.name, P2.name))
    
    if P1.name.upper() != P2.name.upper() and (len(sys.argv) < 3 or sys.argv[2] != "--force"):
        print("Unmatching movelist names, exiting")
        return

    print("Getting movelists...")
    P1.setSecondMovelist(P2.movelist)
    P2.setSecondMovelist(P1.movelist)
    

    sharedMoves = getSharedMoves(P1, P2)    
    globalAliases = {}
    targetMove = ''
    
    for tag2_move, t7_move in sharedMoves:
        if targetMove != '' and targetMove != tag2_move:
            continue
        tag2_move.loadCancels()
        tag2_move.loadReactions()
        tag2_move.loadReactionNames(P1.movelist)
        tag2_move.loadCancelNames(P1.movelist)
        t7_move.loadCancels()
        t7_move.loadReactions()
        t7_move.loadReactionNames(P1.movelist)
        t7_move.loadCancelNames(P2.movelist)
        
        currentMoveAliases = {}
        forbiddenReqs = []
       
        """
        for t2_reaction in tag2_move.reaction_list:
            t7_reaction = [r for r in t7_move.reaction_list if r == t2_reaction and len(r.requirements) > 0]
            
            if len(t7_reaction) != 1:
                continue
                
            t7_reaction = t7_reaction[0]
            for t2_req, t7_req in zip(t2_reaction.requirements, t7_reaction.requirements):
                if t2_req.req == t7_req.req:
                    continue
                addKeyMapping(t2_req.req, t7_req.req)
                if t2_req.req not in currentMoveAliases:
                    currentMoveAliases[t2_req.req] = {
                        't7_id': t7_req.req,
                        'desc': '(%s) %s R' % (P1.uname, t7_move.name)
                    }
                elif currentMoveAliases[t2_req.req] != t7_req.req:
                    forbiddenReqs += [t2_req.req]
        
        for t2_cancel in tag2_move.cancels:
            t7_cancel = [c for c in t7_move.cancels if c == t2_cancel and c.requirements == t2_cancel.requirements]
            
            if len(t7_cancel) != 1:
                continue
            t7_cancel = t7_cancel[0]

            for t2_req, t7_req in zip(t2_cancel.requirements, t7_cancel.requirements):
                if t2_req.req == t7_req.req:
                    continue
                addKeyMapping(t2_req.req, t7_req.req)
                if t2_req.req not in currentMoveAliases:
                    currentMoveAliases[t2_req.req] = {
                        't7_id': t7_req.req,
                        'desc': '(%s) %s -> %s' % (P1.uname, t7_move.name, t7_cancel.name)
                    }
                elif currentMoveAliases[t2_req.req] != t7_req.req:
                    forbiddenReqs += [t2_req.req]
        """
                
        currmove_keys = [key for key in currentMoveAliases.keys() if key not in forbiddenReqs and key not in globalAliases]
        for key in currmove_keys:
            globalAliases[key] = currentMoveAliases[key]
                
    alias_keys = [key for key in globalAliases.keys() if key not in tag2_requirements2]
    for key in alias_keys:
        tag2_requirements2[key] = globalAliases[key]
        print(key, globalAliases[key])
        
    reliable_key_list = [key for key in tag2_requirements2.keys() if isKeyReliable(key)]
    final_requirements = {key:tag2_requirements2[key] for key in reliable_key_list}
    
    with open("./test.py", "w") as f:
        f.write("tag2_requirements2 = {\n")
        for key in final_requirements.keys():
            alias = final_requirements[key]
            text = "    %d: { 't7_id': %d, 'desc': '%s' }," % (key, alias['t7_id'], alias['desc'])
            f.write(text + "\n")
        f.write("}\n\n")
        
        f.write("requirements_mapping = " + str(requirements_mapping))
        
    print("\nSaved.")
    os._exit(0)
    
def getDesc(key):
    for k in extra_move_properties2:
        if k['tag2_id'] == key:
            return k['desc']
    return 'AUTO'
    
def printMoveProperty(movelist, name):
    for m in movelist:
        if m.name == name:
            #propertyList = m.loadExtraProperties()
            print("%s properties:\n" % (name))
            #m.printProperties()
            
            print()
            return True
    print("Move %s not found." %(name))
    
if __name__ == "__main__":
    #saveExtraProperties()
    #saveAliasRequirements()
   
    """
    new_testmapping = {}
    for key in [k for k in sorted(testmapping.keys())]:
        key_value = getKeyValue(key)
        if key_value!= None:
            desc = getDesc(key)
            new_testmapping[key] = {
                't7_id': key_value,
                'desc': desc
            }
            text = "    0x%x: { 't7_id': 0x%x, 'desc': '%s' }," % (key, key_value, desc)
            print(text)
    print("%d keys" % (len(new_testmapping.keys())))
    os._exit(0)
    """
    
    
    
    P1 = Player(GameAddresses.a['p1_ptr'], '1')
    P2 = Player(GameAddresses.a['p2_ptr'], '2')
    
    for move in P1.movelist:
        move.loadCancels()
        for cancel in move.cancels:
            if cancel.move_id == 489:
                cancel.print()
            
    #printMoveProperty(P2.movelist, "wDm_AirF_Up")
    os._exit(0)

    P1.setSecondMovelist(P2.movelist)
    P2.setSecondMovelist(P1.movelist)
    
    if len(sys.argv) == 1:
        print("Usage: ListRequirements.py [p1] [p2] (p2 optional)")
        print("Example: ./ListRequirements.py cancels reactions")
        print("Show the list of cancels for p1 and the list of reactions for p2")
        os._exit(1)
    
    p1Show = sys.argv[1]
    p2Show = 'none' if len(sys.argv) == 2 else sys.argv[2]
    

    sharedMoves = getSharedMoves(P1, P2)

    if p1Show != None and p1Show.lower() != "none":
        P1.printBasicData()
        if p1Show.lower().startswith("properties"):
            P1.printProperties()
        elif p1Show.lower().startswith("cancel"):
            P1.printCancels(True)
        elif p1Show.lower().startswith("reaction"):
            P1.printAttackReactions()
        else:
            print("Unrecognized argument: [%s]. Try [cancels/reactions]" % (p1Show))
    
    if p2Show != None and p2Show.lower() != "none":
        P2.printBasicData()
        if p2Show.lower().startswith("properties"):
            P2.printProperties()
        elif p2Show.lower().startswith("cancel"):
            P2.printCancels(True)
        elif p2Show.lower().startswith("reaction"):
            P2.printAttackReactions()
        else:
            print("Unrecognized argument: [%s]. Try [cancels/reactions]" % (p2Show))
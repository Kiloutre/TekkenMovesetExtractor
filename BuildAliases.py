
import os
import json
    
endVals = {
    'Tekken7': 881,
    'Tag2': 690,
    'Revolution': 697,
    'Tekken6': 397,
    'Tekken3D': 397,
    'Tekken5': 327,
}


targetComp = 't5_'
charactersPath = "./extracted_chars/"

class ExtraProperty:
    def __init__(self, data):
        self.starting_frame = data['type']
        self.value = data['value']
        self.id = data['id']
    
    def __eq__(self, other):
        return self.starting_frame == other.starting_frame and self.value == other.value
        # or (self.value != other.value and self.starting_frame == other.starting_frame and self.starting_frame != 0x8001
    
def loadMovelist(path):
    jsonFilename = next(file for file in os.listdir(path) if file.endswith(".json"))
    with open('%s/%s' % (path, jsonFilename)) as f:
        return json.load(f)
        
def getExtrapropList(extrapropId, moveset):
    propList = []
    
    while True:
        prop = ExtraProperty(moveset['extra_move_properties'][extrapropId])
        if prop.starting_frame == 0:
            break
        propList.append(prop)
        extrapropId += 1
    
    return propList
 
def getRequirementList(reqId, moveset):
    reqList = []
    endVal = endVals[moveset['version']]
    
    while True:
        req = Requirement(moveset['requirements'][reqId])
        if req.req == endVal:
            break
        reqList.append(req)
        reqId += 1
    
    return reqList
        
class Requirement:
    def __init__(self, data):
        self.req = data['req']
        self.param = data['param']
        
    def __eq__(self, other):
        return self.param == other.param
        
class Move:
    def __init__(self, data):
        for key in data:
            setattr(self, key, data[key])
        
    def __eq__(self, other):
        return other != None and (self.name == other.name or self.anim_name == other.anim_name)
        
    def isSimilar(self, other):
        return self.vuln == other.vuln \
               and self.hitlevel == other.hitlevel \
               and self.transition == other.transition \
               and self.anim_max_len == other.anim_max_len \
               and self.first_active_frame == other.first_active_frame \
               and self.last_active_frame == other.last_active_frame
               
def getSimilarMove(movelist, comp):
    similarMove = None
    
    for move in movelist:
        if move.isSimilar(comp):
            if similarMove != None:
                return None
            similarMove = move
    
    return similarMove
        
class Cancel:
    def __init__(self, data, moveset):
        self.command = data['command']
        self.frame_window_start = data['frame_window_start']
        self.frame_window_end = data['frame_window_end']
        self.starting_frame = data['starting_frame']
        self.unknown = data['cancel_option']
        self.move = getMoveName(data['move_id'], moveset)
        self.requirements = getRequirementList(data['requirement_idx'], moveset)
       
    def __eq__(self, other):
        return self.command == other.command and \
               self.frame_window_start == other.frame_window_start and \
               self.frame_window_end == other.frame_window_end and \
               self.starting_frame == other.starting_frame and \
               self.unknown == other.unknown and \
               self.move == other.move
        
def getMoveName(moveId, moveset):
    if moveId >= 0x8000:
        return str(moveId)
    try:
        return moveset['moves'][moveId]['name']
    except:
        return '!+_' + str(moveId)
 
def getCancelList(moveName, moveset):
    moveId = next((i for i, m in enumerate(moveset['moves']) if m['name'] == moveName))
    cancelId = moveset['moves'][moveId]['cancel_idx']
    cancelList = []
    
    while True:
        cancel = Cancel(moveset['cancels'][cancelId], moveset)
        cancelList.append(cancel)
        if cancel.command == 0x8000:
            break
        cancelId += 1
    
    return cancelList

charList = [folder for folder in os.listdir(charactersPath) if os.path.isdir(charactersPath + folder)]

t7Chars = [c[2:] for c in charList if c.startswith('7_')]
revChars = [c[len(targetComp):] for c in charList if c.startswith(targetComp) if c[len(targetComp):] in t7Chars]

requirements_mapping = {}
requirements_desc_mapping = {}

extraprop_mapping = {}
extraprop_desc_mapping = {}

    
def addKeyMapping(key, value, string):
    if key not in requirements_mapping.keys():
        requirements_mapping[key] = { value: 1 }
        requirements_desc_mapping[key] = string
    else:
        if value not in requirements_mapping[key].keys():
            requirements_mapping[key][value] = 1
        else:
            requirements_mapping[key][value] += 1
    
def addPropMapping(key, value, string):
    if key not in extraprop_mapping.keys():
        extraprop_mapping[key] = { value: 1 }
        extraprop_desc_mapping[key] = string
    else:
        if value not in extraprop_mapping[key].keys():
            extraprop_mapping[key][value] = 1
        else:
            extraprop_mapping[key][value] += 1

print("Building aliases for", targetComp)
for i, char in enumerate(revChars):
    print("%d/%d - %s" % (i + 1, len(revChars), char))
    t7_char = '7_' + char
    rev_char = targetComp + char
    uname = char.upper()
    
    t7 = loadMovelist('%s/%s' % (charactersPath, t7_char))
    rev = loadMovelist('%s/%s' % (charactersPath, rev_char))
    
    t7_moves = [Move(m) for m in t7['moves']]
    rev_moves = [Move(m) for m in rev['moves']]
    
    for rev_move in rev_moves:
        move = [m for m in t7_moves if m == rev_move ]
        if len(move) == 0:
            move = [m for m in t7_moves if m.isSimilar(rev_move)]
        if len(move) != 1:
            continue
        t7_move = move[0]
    
        t7_cancels = getCancelList(t7_move.name, t7)
        rev_cancels = getCancelList(rev_move.name, rev)
        t7_proplist = getExtrapropList(t7_move.extra_properties_idx, t7)
        rev_proplist = getExtrapropList(rev_move.extra_properties_idx, rev)
        
        for prop in rev_proplist:
            t7Prop = [p for p in t7_proplist if p == prop]
            
            if len(t7Prop) != 1:
                continue
            t7Prop = t7Prop[0]
            string = '(%s-%s) %s' % (uname, rev_move.name, t7_move.name)
            addPropMapping(prop.id, t7Prop.id, string)
            
        
        rev_cancels = [c for c in rev_cancels if len(c.requirements) > 0] #filtering-out useless cancels
        for rev_cancel in rev_cancels:
            similarCancel = [c for c in t7_cancels if c == rev_cancel and c.requirements == rev_cancel.requirements]
            
            if len(similarCancel) != 1:
                continue
            similarCancel = similarCancel[0]
            
            for t7_req, rev_req in zip(similarCancel.requirements, rev_cancel.requirements):
                if t7_req.req == rev_req.req:
                    continue
                string = '(%s) %s -> %s' % (uname, t7_move.name, similarCancel.move)
                addKeyMapping(rev_req.req, t7_req.req, string)
    
def getHighest(dictionnary):
    keys = list(dictionnary.keys())
    highest = keys[0]
    for k in keys:
        if dictionnary[k] > dictionnary[highest]:
            dictionnary[highest] = dictionnary[k]
    return highest
    
keylist = sorted(requirements_mapping.keys())
print("_requirements = {")
for key in keylist:
    desc = requirements_desc_mapping[key]
    highest = getHighest(requirements_mapping[key])
    t7_val = highest
    orig_val = key
    
    print("    %d: { 't7_id': %d, 'desc': '%s' }," % (key, t7_val, desc))
print('}')

keylist = sorted(extraprop_mapping.keys())
print("_extra_properties = {")
for key in keylist:
    desc = extraprop_desc_mapping[key]
    highest = getHighest(extraprop_mapping[key])
    t7_val = highest
    orig_val = key
    
    print("    0x%x: { 't7_id': 0x%x, 'desc': '%s' }," % (key, t7_val, desc))
print('}')

from Tag2Aliases import tag2_requirements, tag2_extra_move_properties, tag2_character_fixes, getTag2CharIDAliases, tag2_odd_hitbox_aliases, tag2_even_hitbox_aliases
from RevAliases import rev_requirements

versionAliases = {
    'Tag2': {
        'requirements': tag2_requirements,
        'extra_move_properties': tag2_extra_move_properties,
        'chara_fixes': tag2_character_fixes,
        'hitbox_1': tag2_odd_hitbox_aliases,
        'hitbox_2': tag2_even_hitbox_aliases,
        'char_id_func':  getTag2CharIDAliases
    },
    'Revolution': {
        'requirements': rev_requirements
    },
    'Tekken7': {}
}

globalRequirementsReplace = {
    218: 'copy_nearest', #Character ID
    219: 'copy_nearest', #Character ID
    220: 'copy_nearest', #Character ID
    221: 'copy_nearest', #Character ID
    222: 'copy_nearest', #Character ID
    223: 'copy_nearest', #Character ID
    224: 'copy_nearest', #Character ID
    9999: 'copy_nearest', #Disable
}

def getHitboxAliases(version, hitbox):
    if 'hitbox_1' in versionAliases[version] and 'hitbox_2' in versionAliases[version]:
    
        oddHitboxBytesAliases = versionAliases[version]['hitbox_1']
        evenHitboxBytesAliases = versionAliases[version]['hitbox_2']
        
        byteList = [int(b) for b in hitbox.to_bytes(4, 'big')]
        for i, b in enumerate(byteList):
            if i % 2 != 0: #only affects 2nd and 4th byte
                byteList[i] = oddHitboxBytesAliases.get(b, b)
            else:
                byteList[i] = evenHitboxBytesAliases.get(b, b)
        return int.from_bytes(byteList, 'big')
        
    return hitbox

def getCharacteridAlias(version, charId):
    if 'char_id_func' in versionAliases[version]:
        return versionAliases[version]['char_id_func'](charId)
    return charId

def getRequirementAlias(version, req, param):
    if 'requirements' in versionAliases[version]:
        alias = versionAliases[version]['requirements'].get(req, None)
        if alias != None:
            req = alias['t7_id']
            if 'param_alias' in alias:
                param = alias['param_alias'].get(param, param)
    return req, param

def getMoveExtrapropAlias(version, type, id, value):
    if 'extra_move_properties' in versionAliases[version]:
        alias = versionAliases[version]['extra_move_properties'].get(id, None)
        if alias != None:
            id = alias['t7_id']
            if 'force_type' in alias:
                type = alias['force_type']
            if 'force_value' in alias:
                value = alias['value']
    return type, id, value

class ExtraPropertyFix:
    def __init__(self, alias):
        self.alias = alias
        
    def matchProperty(self, property):
        for key in ['type', 'id', 'value']:
            if key in self.alias and self.alias[key] != property[key]:
                return False
        return True
    
    def searchPropertyByMatch(self, property_list, starting_index):
    
        if starting_index > 0 and property_list[starting_index - 1]['type'] != 0:
            return property_list[starting_index - 1]
                
        index = starting_index + 1
        while index < len(property_list) and property_list[index]['type'] != 0:
            if not self.matchProperty(property_list[index]):
                return property_list[index]
            index += 1
            
        return { 'type': 0, 'id': 0, 'value': 0, }
        
    def applyFix(self, property_list, index):
        if not self.matchProperty(property_list[index]):
            return False
    
        if 'force_type' in self.alias:
            property_list[index]['type'] = self.alias['force_type']
        if 'value_alias' in self.alias:
            value = property_list[index]['value']
            property_list[index]['value'] = self.alias['value_alias'].get(value, value)
        
        if 'copy_nearest' in self.alias:
            matching_property = self.searchPropertyByMatch(property_list, index) 
            property_list[index] = matching_property
        return True

def ApplyCharacterFixes(m):
    character_name = m['tekken_character_name']
    version = m['version']
    if 'chara_fixes' not in versionAliases[version]:
        return
    characterFixes = versionAliases[version]['chara_fixes']
    if character_name not in characterFixes:
        return
        
    propertyFixList = [ExtraPropertyFix(alias) for alias in characterFixes[character_name]['extraproperty']]
    for i in range(len(m['extra_move_properties'])):
        for propertyFix in propertyFixList:
            if propertyFix.applyFix(m['extra_move_properties'], i):
                break
                
    if 'moves' in characterFixes[character_name]:
        for i, move in enumerate(m['moves']):
            for moveFix in characterFixes[character_name]['moves']:
                if moveFix['name'] == move['name']:
                    for key in moveFix:
                        move[key] = moveFix[key]
            
            
class GlobalRequirementFix:
    def __init__(self, req):
        self.req = req
        self.value = globalRequirementsReplace[req]
    
    def searchReq(self, requirement_list, starting_index):
        if starting_index > 0 and requirement_list[starting_index - 1]['req'] != 881:
            return requirement_list[starting_index - 1]
                
        index = starting_index
        while index < len(requirement_list):
            if requirement_list[index]['req'] != self.req:
                return requirement_list[index]
            index += 1
            
        return { 'req': 881, 'param': 0 }
        
    def applyFix(self, requirement_list, index):
        if requirement_list[index]['req'] != self.req:
            return False
            
        if self.value == 'copy_nearest':
            matching_requirement = self.searchReq(requirement_list, index) 
            requirement_list[index] = matching_requirement
    
        return True
        
def applyGlobalRequirementAliases(requirement_list):
    requirementAliasList = [GlobalRequirementFix(key) for key in globalRequirementsReplace]
    
    for i in range(len(requirement_list)):
        for requirementAlias in requirementAliasList:
            if requirementAlias.applyFix(requirement_list, i):
                break

def fillDict(dictionnary):
    keylist = sorted(dictionnary)
    generatedKeys = 0
    
    if 0xFFFF in dictionnary:
        return dictionnary
    
    for i in range(len(keylist) - 1):
        key = keylist[i]
        nextkey = keylist[i + 1]
        key_diff = nextkey - (key + 1)
        
        if 'nofill' in dictionnary[key] or 'nofill' in dictionnary[nextkey]:
            continue
        
        alias_offset = dictionnary[key]['t7_id'] - key
        alias_offset2 = dictionnary[nextkey]['t7_id'] - nextkey
        
        if alias_offset == alias_offset2 and key_diff > 0:
            for i in range(1, key_diff + 1):
                dictionnary[key + i] = {
                    't7_id': dictionnary[key]['t7_id'] + i,
                    'desc': '%d:FILLED' % (key + i)
                }
                generatedKeys += 1
                
    dictionnary[0xFFFF] = 'FILLED_DICT'
    print("Generated %d keys" % (generatedKeys))
    return dictionnary
                
def fillAliasesDictonnaries(version):
    if 'requirements' in versionAliases[version]:
        fillDict(versionAliases[version]['requirements'])
        
    if 'extra_move_properties' in versionAliases[version]:
        fillDict(versionAliases[version]['extra_move_properties'])

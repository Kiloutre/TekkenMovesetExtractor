# --- Ton-Chan's Motbin export --- #
# Python 3.6.5

from Addresses import GameAddresses, GameClass
from ByteSwap import SwapAnimBytes
from datetime import datetime, timezone
import json
import os
import sys
   
TekkenVersion = 7

if len(sys.argv) > 1 and sys.argv[1].lower() == "tag2":
    TekkenVersion = 2

T = GameClass("TekkenGame-Win64-Shipping.exe" if TekkenVersion == 7 else "Cemu.exe")
ptr_size = 8 if TekkenVersion == 7 else 4
base = 0x0 if TekkenVersion == 7 else 0x1F8D5110000 #Cemu base ptr
endian = 'little' if TekkenVersion == 7 else 'big'
tag2_p1_base = 0x10885C90
cemu_motbin_base = (base + tag2_p1_base - 0x98)

def readInt(addr, len):
    return T.readInt(addr, len, endian=endian)
    
def readBytes(addr, len):
    return T.readBytes(addr, len)
    
def readString(addr):
    offset = 0
    while readInt(addr + offset, 1) != 0:
        offset += 1
    return readBytes(addr, offset).decode("ascii")
    
def readStringPtr(addr):
    return readString(base + readInt(addr, ptr_size))
    
def bToInt(data, offset, length, ed=None):
    return int.from_bytes(data[offset:offset + length], ed if ed != None else endian)
    
def GetTT2Pos(data):
    return [
        data[1:].find(b'\x00\x64\x00\x17\x00'),
        data[1:].find(b'\x00\x64\x00\x1B\x00'),
        data[1:].find(b'\x00\xC8\x00\x17')
    ]
    
def GetT7Pos(data):
    return [
        data[1:].find(b'\x64\x00\x17\x00'),
        data[1:].find(b'\x64\x00\x1B\x00'),
        data[1:].find(b'\xC8\x00\x17')
    ]
    
def CropAnim(data):
    pos = GetT7Pos(data) if TekkenVersion == 7 else GetTT2Pos(data)
    pos = [p+1 for p in pos if p != -1]
    x = pos
    if len(pos) == 0:
        return data
    return data[:min(pos)]
    
class AnimData:
    def __init__(self, name, data_addr):
        self.name = name
        self.data = None    
        self.addr = data_addr
                
    def getData(self):
        if self.data == None:
            read_size = 2000000
            while self.data == None and read_size > 100:
                try:
                    self.data = CropAnim(readBytes(self.addr, read_size))
                except Exception as e:
                    read_size = int(read_size * 0.75)
            
            if TekkenVersion != 7:
                try:
                    self.data = SwapAnimBytes(self.data)
                except:
                    pass
        return self.data
        
    def __eq__(self, other):
        return self.name == other.name
        
class Pushback:
    pushback_size = 0x10 if TekkenVersion == 7 else 0xC
    
    def __init__(self, addr):
        data = readBytes(base + addr, Pushback.pushback_size)
        
        self.val1 = bToInt(data, 0, 2)
        self.val2 = bToInt(data, 2, 2)
        self.val3 = bToInt(data, 4, 4)
        self.extra_index = -1
        self.extra_addr = bToInt(data, 8, ptr_size)
        
    def dict(self):
        return {
            'val1': self.val1,
            'val2': self.val2,
            'val3': self.val3,
            'extra_index': self.extra_index
        }
        
    def setExtraIndex(self, idx):
        self.extra_index = idx
        
class PushbackExtradata:
    size = 0x2 if TekkenVersion == 7 else 0x2
    
    def __init__(self, addr):
        data = readBytes(base + addr, Pushback.pushback_size)
        
        self.value = bToInt(data, 0, 2)
        
    def dict(self):
        return self.value
        
class Requirement:
    requirement_size = 0x8 if TekkenVersion == 7 else 0x8
    
    def __init__(self, addr):
        self.addr = addr
        
        data = readBytes(base + addr, 0x8)
        self.req = bToInt(data, 0, 4)
        self.param = bToInt(data, 4, 4)
        self.id = -1
        
    def dict(self):
        return {
            'id': self.id,
            'req': self.req,
            'param': self.param
        }
        
    def setId(self, id):
        self.id = id
        
class Cancel:
    cancel_size = 0x28 if TekkenVersion == 7 else 0x20
    
    def __init__(self, addr):
        self.addr = addr
        data = readBytes(base + addr, Cancel.cancel_size)
        
        
        after_ptr_offset = 0x18 if TekkenVersion == 7 else 0x10
        
        self.command = bToInt(data, 0x0, 8)
        self.requirement_addr = bToInt(data, 0x8, ptr_size)
        extra_data_addr = bToInt(data, 0x8 + ptr_size, ptr_size) + base
        self.extra_data = readInt(extra_data_addr, 4)
        self.frame_window_start = bToInt(data, after_ptr_offset, 4)
        self.frame_window_end = bToInt(data, after_ptr_offset + 4, 4)
        self.starting_frame = bToInt(data,after_ptr_offset + 8, 4)
        self.move_id = bToInt(data, after_ptr_offset + 12, 2)
        self.unknown = bToInt(data, after_ptr_offset + 14, 2)
        
        if TekkenVersion != 7:
            t = bToInt(data, 0, 4)
            t2 = bToInt(data, 0x4, 4) 
            self.command = (t2 << 32) | t
        
        self.id = -1
        
    def dict(self):
        return {
            'id': self.id,
            'command': self.command,
            'extra_data': self.extra_data,
            'requirement': self.requirement_idx,
            'frame_window_start': self.frame_window_start,
            'frame_window_end': self.frame_window_end,
            'starting_frame': self.starting_frame,
            'move_id': self.move_id,
            'unknown': self.unknown
        }
    
    def setRequirementId(self, requirement_idx):
        self.requirement_idx = requirement_idx
        
    def setId(self, id):
        self.id = id
        
class ReactionList:
    reaction_list_size = 0x70 if TekkenVersion == 7 else 0x50
    
    def __init__(self, addr):
        data = readBytes(base + addr, ReactionList.reaction_list_size)
        
        self.ptr_list = [bToInt(data, i * ptr_size, ptr_size) for i in range(7)]
        self.pushback_indexes = [-1] * 7
        
        list_starting_offset = 0x50 if TekkenVersion == 7 else 0x34
        self.reaction_list = [bToInt(data, list_starting_offset + (offset * 2), 2) for offset in range(0, 14)]
        
        self.standing = bToInt(data, list_starting_offset + 0x0, 2)
        self.crouch = bToInt(data, list_starting_offset + 0x2, 2)
        self.ch = bToInt(data, list_starting_offset + 0x4, 2)
        self.crouch_ch = bToInt(data, list_starting_offset + 0x6, 2)
        self.left_side = bToInt(data, list_starting_offset + 0x8, 2)
        self.left_side_crouch = bToInt(data, list_starting_offset + 0xA, 2)
        self.right_side = bToInt(data, list_starting_offset + 0xC, 2)
        self.right_side_crouch = bToInt(data, list_starting_offset + 0xE, 2)
        self.back = bToInt(data, list_starting_offset + 0x10, 2)
        self.back_crouch = bToInt(data, list_starting_offset + 0x12, 2)
        self.block = bToInt(data, list_starting_offset + 0x14, 2)
        self.crouch_block = bToInt(data, list_starting_offset + 0x16, 2)
        self.wallslump = bToInt(data, list_starting_offset + 0x18, 2)
        self.downed = bToInt(data, list_starting_offset + 0x1A, 2)
        
    def setIndexes(self, pushback_ptr, pushback_size):
        for i, ptr in enumerate(self.ptr_list):
            self.pushback_indexes[i] = (ptr - pushback_ptr) // pushback_size
        
    def dict(self):
        return {
            'pushback_indexes': self.pushback_indexes,
            'standing': self.standing,
            'ch': self.ch,
            'crouch': self.crouch,
            'crouch_ch': self.crouch_ch,
            'left_side': self.left_side,
            'left_side_crouch': self.left_side_crouch,
            'right_side': self.right_side,
            'right_side_crouch': self.right_side_crouch,
            'back': self.back,
            'back_crouch': self.back_crouch,
            'block': self.block,
            'crouch_block': self.crouch_block,
            'wallslump': self.wallslump,
            'downed': self.downed,
        }
    
class HitCondition:
    hit_condition_size = 0x18 if TekkenVersion == 7 else 0xC
    
    def __init__(self, addr):
        data = readBytes(base + addr, HitCondition.hit_condition_size)
        
        self.reaction_list_idx = -1
        self.requirement_idx = -1
        
        self.requirement_addr = bToInt(data, 0x0, ptr_size)
        self.damage = bToInt(data, ptr_size, 4)
        self.reaction_list_addr = bToInt(data, (ptr_size + 8) if TekkenVersion == 7 else (ptr_size + 4), ptr_size)
        
    def dict(self):
        return {
            'requirement': self.requirement_idx,
            'damage': self.damage,
            'reaction_list': self.reaction_list_idx
        }

    def setRequirementId(self, id):
        self.requirement_idx = id

    def setReactionListId(self, id):
        self.reaction_list_idx = id
    
class Move:
    move_size = 0xB0 if TekkenVersion == 7 else 0x70
    
    def __init__(self, addr):
        move_bytes = readBytes(base + addr, Move.move_size)
        
        if TekkenVersion == 7:
            move_name_addr = bToInt(move_bytes, 0x0, ptr_size)
            anim_name_addr = bToInt(move_bytes, 0x8, ptr_size)
            anim_data_addr = bToInt(move_bytes, 0x10, ptr_size)
            vuln = bToInt(move_bytes, 0x18, 4)
            hit_level = bToInt(move_bytes, 0x1c, 4)
            cancel_ptr = bToInt(move_bytes, 0x20, ptr_size)
            
            u1 = bToInt(move_bytes, 0x28, ptr_size)
            u2 = bToInt(move_bytes, 0x30, ptr_size)
            u3 = bToInt(move_bytes, 0x38, ptr_size)
            u4 = bToInt(move_bytes, 0x40, ptr_size)
            u5 = bToInt(move_bytes, 0x48, ptr_size)
            u6 = bToInt(move_bytes, 0x50, 4)
            
            transition = bToInt(move_bytes, 0x54, 2)
            
            u7 = bToInt(move_bytes, 0x56, 2)
            u8 = bToInt(move_bytes, 0x58, 4)
            u9 = bToInt(move_bytes, 0x5C, 4)
            
            on_hit_ptr = bToInt(move_bytes, 0x60, ptr_size)
            anim_max_length = bToInt(move_bytes, 0x68, 4)
            
            u10 = bToInt(move_bytes, 0x6c, 4)
            u11 = bToInt(move_bytes, 0x70, 4)
            u12 = bToInt(move_bytes, 0x74, 4)
            
            if u12 != 0:
                print(readString(base + move_name_addr), "\t", u12)
            
            extra_properties_ptr = bToInt(move_bytes, 0x78, ptr_size) #can_be_null
            particles_ptr = bToInt(move_bytes, 0x80, ptr_size) #can_be_null
            
            u13 = bToInt(move_bytes, 0x88, 8)
            u14 = bToInt(move_bytes, 0x90, 8)
            u15 = bToInt(move_bytes, 0x98, 4)
            
            hitbox_location = bToInt(move_bytes, 0x9c, 4)
            attack_startup = bToInt(move_bytes, 0xa0, 4)
            attack_recovery = bToInt(move_bytes, 0xa4, 4)
            
            u16 = bToInt(move_bytes, 0xa8, 8)
        else:
            move_name_addr = bToInt(move_bytes, 0x0, ptr_size)
            anim_name_addr = bToInt(move_bytes, 0x4, ptr_size)
            anim_data_addr = bToInt(move_bytes, 0x8, ptr_size)
            vuln = bToInt(move_bytes, 0xC, 4)
            hit_level = bToInt(move_bytes, 0x10, 4)
            cancel_ptr = bToInt(move_bytes, 0x14, ptr_size)
            
            u1 = bToInt(move_bytes, 0x18, ptr_size)
            u2 = bToInt(move_bytes, 0x1c, ptr_size)
            u3 = bToInt(move_bytes, 0x20, ptr_size)
            u4 = bToInt(move_bytes, 0x24, ptr_size)
            u5 = bToInt(move_bytes, 0x28, ptr_size)
            u6 = bToInt(move_bytes, 0x2c, 4)
            
            transition = bToInt(move_bytes, 0x30, 2)
            
            u7 = bToInt(move_bytes, 0x32, 2)
            u8 = bToInt(move_bytes, 0x34, 2)
            u9 = bToInt(move_bytes, 0x36, 2)
            
            on_hit_ptr = bToInt(move_bytes, 0x38, ptr_size)
            anim_max_length = bToInt(move_bytes, 0x3c, 4)
            
            u10 = bToInt(move_bytes, 0x40, 4)
            u11 = bToInt(move_bytes, 0x44, 4)
            u12 = 0#bToInt(move_bytes, 0x48, 4) #break hits airborne
            
            extra_properties_ptr = bToInt(move_bytes, 0x4c, ptr_size) #can_be_null
            particles_ptr = bToInt(move_bytes, 0x50, ptr_size) #can_be_null
            
            u13 = bToInt(move_bytes, 0x54, 4)
            u14 = bToInt(move_bytes, 0x58, 4)
            u15 = 0#bToInt(move_bytes, 0x5c, 4) #breaks hits airborne toos
            
            hitbox_location = bToInt(move_bytes, 0x60, 4, ed='little')
            attack_startup = bToInt(move_bytes, 0x64, 4)
            attack_recovery = bToInt(move_bytes, 0x68, 4)
            
            u16 = bToInt(move_bytes, 0x6c, 4)
        
        self.name = readString(base + move_name_addr)
        self.anim_name = readString(base + anim_name_addr)
        self.anim_addr = anim_data_addr
        self.vuln = vuln
        self.hitlevel = hit_level
        self.cancel_addr = cancel_ptr
        self.transition = transition
        self.anim_max_len = anim_max_length
        self.startup = attack_startup
        self.recovery = attack_recovery
        self.hitbox_location = hitbox_location
        self.hit_condition_addr = on_hit_ptr
        
        self.u1 = u1
        self.u2 = u2
        self.u3 = u3
        self.u4 = u4
        self.u5 = u5
        self.u6 = u6
        self.u7 = u7
        self.u8 = u8
        self.u9 = u9
        self.u10 = u10
        self.u11 = u11
        self.u12 = u12
        self.u13 = u13
        self.u14 = u14
        self.u15 = u15
        self.u16 = u16
        
        self.anim = AnimData(self.anim_name, base + self.anim_addr)
        self.cancel_idx = -1
        self.hit_condition_idx = -1
        
        self.id = -1
    
    def dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'anim_name': self.anim_name,
            'vuln': self.vuln,
            'hitlevel': self.hitlevel,
            'cancel': self.cancel_idx,
            'transition': self.transition,
            'anim_max_len': self.anim_max_len,
            'hit_condition': self.hit_condition_idx,
            'hitbox_location': self.hitbox_location,
            'startup': self.startup,
            'recovery': self.recovery,
            
            'u1': self.u1,
            'u2': self.u2,
            'u3': self.u3,
            'u4': self.u4,
            'u5': self.u5,
            'u6': self.u6,
            'u7': self.u7,
            'u8': self.u8,
            'u9': self.u9,
            'u10': self.u10,
            'u11': self.u11,
            'u12': self.u12,
            'u13': self.u13,
            'u14': self.u14,
            'u15': self.u15,
            'u16': self.u16
        }
        
    def setCancelIdx(self, cancel_idx):
        self.cancel_idx = cancel_idx
        
    def setHitConditionIdx(self, id):
        self.hit_condition_idx = id
        
    def setId(self, id):
        self.id = id
    
class Motbin:
    def __init__(self, addr):
        self.addr = addr
        
        self.version = "Tekken7" if TekkenVersion == 7 else "Tag2"
        self.extraction_date = datetime.now(timezone.utc).__str__()
    
        character_name_addr = 0x8
        creator_name_addr = character_name_addr + ptr_size
        date_addr = creator_name_addr + ptr_size
        fulldate_addr = date_addr + ptr_size
        
        self.character_name = readStringPtr(addr + character_name_addr)
        self.name = self.character_name[1:-1]
        self.creator_name = readStringPtr(addr + creator_name_addr)
        self.date = readStringPtr(addr + date_addr)
        self.fulldate = readStringPtr(addr + fulldate_addr)

        reaction_list_ptr = 0x150 if TekkenVersion == 7 else 0x140
        reaction_list_size = reaction_list_ptr + ptr_size
        self.reaction_list_ptr = readInt(addr + reaction_list_ptr, ptr_size)
        self.reaction_list_size = readInt(addr + reaction_list_size, 4)
        
        requirements_ptr = 0x160 if TekkenVersion == 7 else 0x148
        requirement_count = requirements_ptr + ptr_size
        self.requirements_ptr = readInt(addr + requirements_ptr, ptr_size)
        self.requirement_count = readInt(addr + requirement_count, 4)
        
        hit_conditions_ptr = 0x170 if TekkenVersion == 7 else 0x150
        hit_conditions_size = hit_conditions_ptr + ptr_size
        self.hit_conditions_ptr = readInt(addr + hit_conditions_ptr, ptr_size)
        self.hit_conditions_size = readInt(addr + hit_conditions_size, 4)
        
        pushback_ptr = 0x190 if TekkenVersion == 7 else 0x160
        pushback_list_size = pushback_ptr + ptr_size
        self.pushback_ptr = readInt(addr + pushback_ptr, ptr_size)
        self.pushback_list_size = readInt(addr + pushback_list_size, 4)

        pushback_extradata_ptr = 0x1A0 if TekkenVersion == 7 else 0x168
        pushback_extradata_size = pushback_extradata_ptr + ptr_size
        self.pushback_extradata_ptr = readInt(addr + pushback_extradata_ptr, ptr_size)
        self.pushback_extradata_size = readInt(addr + pushback_extradata_size, 4)

        cancel_head_ptr = 0x1b0 if TekkenVersion == 7 else 0x170
        cancel_list_size = cancel_head_ptr + ptr_size
        self.cancel_head_ptr = readInt(addr + cancel_head_ptr, ptr_size)
        self.cancel_list_size = readInt(addr + cancel_list_size, 4)

        group_cancel_head_ptr = 0x1c0 if TekkenVersion == 7 else 0x178
        group_cancel_list_size = group_cancel_head_ptr + ptr_size
        self.group_cancel_head_ptr = readInt(addr + group_cancel_head_ptr, ptr_size)
        self.group_cancel_list_size = readInt(addr + group_cancel_list_size, 4)

        cancel_extradata_head_ptr = 0x1d0 if TekkenVersion == 7 else 0x180
        cancel_extradata_list_size = cancel_extradata_head_ptr + ptr_size
        self.cancel_extradata_head_ptr = readInt(addr + cancel_extradata_head_ptr, ptr_size)
        self.cancel_extradata_list_size = readInt(addr + cancel_extradata_list_size, 4)

        movelist_head_ptr = 0x210 if TekkenVersion == 7 else 0x1a0
        movelist_size = movelist_head_ptr + ptr_size
        self.movelist_head_ptr = readInt(addr + movelist_head_ptr, ptr_size)
        self.movelist_size = readInt(addr + movelist_size, 4)
        
        aliasCopySize = 0x2a
        aliasOffset = 0x98 if TekkenVersion == 7 else 0x88
    
        self.aliases = [readInt(addr + aliasOffset + offset, 2) for offset in range(0, 42, 2)]
        
        self.requirements = []
        self.cancels = []
        self.moves = []
        self.anims = []
        self.group_cancels = []
        self.reaction_list = []
        self.hit_conditions = []
        self.pushbacks = []
        self.pushback_extras = []
        
    def printBasicData(self):
        print("Character: %s" % (self.character_name))
        print("Creator: %s" % (self.creator_name))
        print("Date: %s %s\n" % (self.date, self.fulldate))
        
    def dict(self):
        anim_names = [anim.name for anim in self.anims]
        
        return {
            'version': self.version,
            'extraction_date': self.extraction_date,
            'character_name': self.character_name,
            'creator_name': self.creator_name,
            'date': self.date,
            'fulldate': self.fulldate,
            'aliases': self.aliases,
            'requirements': self.requirements,
            'cancels': self.cancels,
            'group_cancels': self.group_cancels,
            'anims': anim_names,
            'moves': self.moves,
            'reaction_list': self.reaction_list,    
            'hit_conditions': self.hit_conditions,
            'pushbacks': self.pushbacks,
            'pushback_extras': self.pushback_extras
        }
        
    def save(self):
        print("Saving data...")
        path = "./%d_%s" % (TekkenVersion, self.name)
        anim_path = "%s/anim" % (path)
        
        if not os.path.isdir(path):
            os.mkdir(path)
        if not os.path.isdir(anim_path):
            os.mkdir(anim_path)
            
        with open("%s/%s.json" % (path, self.name), "w") as f:
            json.dump(self.dict(), f, indent=4)
            
        print("Saving animations...")
        for anim in self.anims:
            with open ("%s/%s.bin" % (anim_path, anim.name), "wb") as f:
                f.write(anim.getData())
            
        print("Saved at path %s/%s" % (os.getcwd(), path[2:]))

if __name__ == "__main__":
    motbin_ptr_addr = (GameAddresses.a['p1_ptr'] + 0x14a0) if TekkenVersion == 7 else cemu_motbin_base
    motbin_ptr = readInt(motbin_ptr_addr, ptr_size)
    
    m = Motbin(motbin_ptr if TekkenVersion == 7 else motbin_ptr + base)
    m.printBasicData()
    
    print("Reading requirements...")
    for i in range(m.requirement_count):
        condition = Requirement(m.requirements_ptr + (i * Requirement.requirement_size))
        condition.setId(i)
        m.requirements.append(condition.dict())
    
    print("Reading cancels...")
    for i in range(m.cancel_list_size):
        cancel = Cancel(m.cancel_head_ptr + (i * Cancel.cancel_size))
        cancel.setRequirementId((cancel.requirement_addr - m.requirements_ptr) // Requirement.requirement_size)
        cancel.setId(i)
        m.cancels.append(cancel.dict())
    
    print("Reading grouped cancels...")
    for i in range(m.group_cancel_list_size):
        cancel = Cancel(m.group_cancel_head_ptr + (i * Cancel.cancel_size))
        cancel.setRequirementId((cancel.requirement_addr - m.requirements_ptr) // Requirement.requirement_size)
        cancel.setId(i)
        m.group_cancels.append(cancel.dict())
    
    print("Reading pushbacks extradatas...")
    for i in range(m.pushback_extradata_size):
        pushback_extra = PushbackExtradata(m.pushback_extradata_ptr + (i * PushbackExtradata.size))
        m.pushback_extras.append(pushback_extra.dict())

    print("Reading pushbacks...")
    for i in range(m.pushback_list_size):
        pushback = Pushback(m.pushback_ptr + (i * Pushback.pushback_size))
        pushback.setExtraIndex((pushback.extra_addr - m.pushback_extradata_ptr) // PushbackExtradata.size)
        m.pushbacks.append(pushback.dict())
    
    print("Reading reaction lists...")
    for i in range(m.reaction_list_size):
        reaction_list = ReactionList(m.reaction_list_ptr + (i * ReactionList.reaction_list_size))
        reaction_list.setIndexes(m.pushback_ptr, Pushback.pushback_size)
        m.reaction_list.append(reaction_list.dict())
    
    print("Reading on-hit condition lists...")
    for i in range(m.hit_conditions_size):
        hit_conditions = HitCondition(m.hit_conditions_ptr + (i * HitCondition.hit_condition_size))
        hit_conditions.setRequirementId((hit_conditions.requirement_addr - m.requirements_ptr) // Requirement.requirement_size)
        hit_conditions.setReactionListId((hit_conditions.reaction_list_addr - m.reaction_list_ptr) // ReactionList.reaction_list_size)
        m.hit_conditions.append(hit_conditions.dict())
    
    print("Reading movelist...")
    for i in range(m.movelist_size):
        move = Move(m.movelist_head_ptr + (i * Move.move_size))
        cancel_id = (move.cancel_addr - m.cancel_head_ptr) // Cancel.cancel_size
        move.setCancelIdx(cancel_id)
        move.setHitConditionIdx((move.hit_condition_addr - m.hit_conditions_ptr) // HitCondition.hit_condition_size)
        move.setId(i)
        m.moves.append(move.dict())
        
        if move.anim not in m.anims:
            m.anims.append(move.anim)
    
    m.save()
    
    
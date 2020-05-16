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

exportVersion = "0.2.2"
T = GameClass("TekkenGame-Win64-Shipping.exe" if TekkenVersion == 7 else "Cemu.exe")
ptr_size = 8 if TekkenVersion == 7 else 4
base = 0x0 if TekkenVersion == 7 else GameAddresses.a['cemu_base']
endian = 'little' if TekkenVersion == 7 else 'big'

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
        data[1:].find(b'\x00\xC8\x00\x17'),
        data[1:].find(b'motOrigin'),
        data[1:].find(bytes([0] * 100))
    ]
    
def GetT7Pos(data):
    return [
        data[1:].find(b'\x64\x00\x17\x00'),
        data[1:].find(b'\x64\x00\x1B\x00'),
        data[1:].find(b'\xC8\x00\x17'),
        data[1:].find(b'motOrigin'),
        data[1:].find(bytes([0] * 100))
    ]
    
def getEndPos(data):
    pos = GetT7Pos(data) if TekkenVersion == 7 else GetTT2Pos(data)
    pos = [p+1 for p in pos if p != -1]
    return -1 if len(pos) == 0 else min(pos)
    
class AnimData:
    def __init__(self, name, data_addr):
        self.name = name
        self.data = None    
        self.addr = data_addr
        return None
                
    def getData(self):
        if self.data == None:
            read_size = 8192
            offset = 0
            prev_bytes = None
            maxSize = 50000000 
            
            while read_size >= 16:
                try:
                    curr_bytes = readBytes(self.addr + offset, read_size)
                except Exception as e:
                    read_size //= 2
                else:
                    tmp = curr_bytes
                    if prev_bytes != None:
                        curr_bytes = prev_bytes + curr_bytes
                    
                    endPos = getEndPos(curr_bytes)
                    if endPos != -1:
                        offset += endPos
                        break
                    
                    prev_bytes = tmp
                    if offset + read_size > maxSize:
                        break
                    offset += read_size
                    
            self.data = None if offset == 0 else readBytes(self.addr, offset)
            if TekkenVersion != 7:
                self.data = SwapAnimBytes(self.data)
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
    size = 0x2
    
    def __init__(self, addr):
        data = readBytes(base + addr, Pushback.pushback_size)
        
        self.value = bToInt(data, 0, 2)
        
    def dict(self):
        return self.value
        
class Requirement:
    size = 0x8
    
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
    size = 0x28 if TekkenVersion == 7 else 0x20
    
    def __init__(self, addr):
        self.addr = addr
        data = readBytes(base + addr, Cancel.size)
        
        
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
        
        self.u1list = [bToInt(data, (ptr_size * 7) + i * 2, 2) for i in range(4)]
        
        list_starting_offset = 0x50 if TekkenVersion == 7 else 0x34
        self.reaction_list = [bToInt(data, list_starting_offset + (offset * 2), 2) for offset in range(0, 14)]
        
        
        self.vertical_pushback = bToInt(data, list_starting_offset - 4, 2)
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
            'u1list': self.u1list,
            'vertical_pushback': self.vertical_pushback,
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
    size = 0x18 if TekkenVersion == 7 else 0xC
    
    def __init__(self, addr):
        data = readBytes(base + addr, HitCondition.size)
        
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
    
class ExtraMoveProperties:
    size = 0xC
    
    def __init__(self, addr):
        self.addr = addr
        data = readBytes(base + addr, ExtraMoveProperties.size)
        
        self.type = bToInt(data, 0, 4)
        self.id = bToInt(data, 4, 4)
        self.value = bToInt(data, 8, 4)
            
    def dict(self):
        return {
            'type': self.type,
            'id': self.id,
            'value': self.value
        }
    
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
            
            u1 = 0#bToInt(move_bytes, 0x28, ptr_size) #pointer!!!
            u2 = bToInt(move_bytes, 0x30, ptr_size) #NOT pointer
            u3 = bToInt(move_bytes, 0x38, ptr_size)
            u4 = bToInt(move_bytes, 0x40, ptr_size)
            u5 = 0#bToInt(move_bytes, 0x48, ptr_size)  #pointer!!!
            u6 = bToInt(move_bytes, 0x50, 4)
            
            transition = bToInt(move_bytes, 0x54, 2)
            
            u7 = bToInt(move_bytes, 0x56, 2)
            u8 = bToInt(move_bytes, 0x58, 2)
            u8_2 = bToInt(move_bytes, 0x5A, 2)
            u9 = bToInt(move_bytes, 0x5C, 4)
            
            on_hit_ptr = bToInt(move_bytes, 0x60, ptr_size)
            anim_max_length = bToInt(move_bytes, 0x68, 4)
            
            u10 = bToInt(move_bytes, 0x6c, 4)
            u11 = bToInt(move_bytes, 0x70, 4)
            u12 = bToInt(move_bytes, 0x74, 4)
            
            voiceclip_ptr = bToInt(move_bytes, 0x78, ptr_size) #can_be_null
            extra_properties_ptr = bToInt(move_bytes, 0x80, ptr_size) #can_be_null
            
            u13 = 0#bToInt(move_bytes, 0x88, 8) #pointer!!!
            u14 = 0#bToInt(move_bytes, 0x90, 8) #pointer!!!
            u15 = bToInt(move_bytes, 0x98, 4)
            
            hitbox_location = bToInt(move_bytes, 0x9c, 4)
            attack_startup = bToInt(move_bytes, 0xa0, 4)
            attack_recovery = bToInt(move_bytes, 0xa4, 4)
            
            u16 = bToInt(move_bytes, 0xa8, 2)
            u17 = bToInt(move_bytes, 0xaa, 2)
            u18 = bToInt(move_bytes, 0xac, 4)
        else:
            move_name_addr = bToInt(move_bytes, 0x0, ptr_size)
            anim_name_addr = bToInt(move_bytes, 0x4, ptr_size)
            anim_data_addr = bToInt(move_bytes, 0x8, ptr_size)
            vuln = bToInt(move_bytes, 0xC, 4)
            hit_level = bToInt(move_bytes, 0x10, 4)
            cancel_ptr = bToInt(move_bytes, 0x14, ptr_size)
            
            u1 = 0#bToInt(move_bytes, 0x18, ptr_size) #pointer!!!
            u2 = bToInt(move_bytes, 0x1c, ptr_size) #NOT pointer
            u3 = bToInt(move_bytes, 0x20, ptr_size)
            u4 = bToInt(move_bytes, 0x24, ptr_size)
            u5 = 0#bToInt(move_bytes, 0x28, ptr_size) #pointer!!!
            u6 = bToInt(move_bytes, 0x2c, 4)
            
            transition = bToInt(move_bytes, 0x30, 2)
            
            u7 = bToInt(move_bytes, 0x32, 2) 
            u8 = bToInt(move_bytes, 0x36, 2)
            u8_2 = bToInt(move_bytes, 0x34, 2) #inverted offsets for 0x36 & 0x34
            u9 = 0 
            
            on_hit_ptr = bToInt(move_bytes, 0x38, ptr_size)
            anim_max_length = bToInt(move_bytes, 0x3c, 4)
            
            u10 = bToInt(move_bytes, 0x40, 4)
            u11 = bToInt(move_bytes, 0x44, 4)
            u12 = bToInt(move_bytes, 0x48, 4)
            
            voiceclip_ptr = bToInt(move_bytes, 0x4c, ptr_size) #can_be_null
            extra_properties_ptr = bToInt(move_bytes, 0x50, ptr_size) #can_be_null
            
            u13 = 0#bToInt(move_bytes, 0x54, 4) #pointer!!!
            u14 = 0#bToInt(move_bytes, 0x58, 4) #pointer!!!
            u15 = bToInt(move_bytes, 0x5c, 4)
            
            hitbox_location = bToInt(move_bytes, 0x60, 4, ed='little')
            attack_startup = bToInt(move_bytes, 0x64, 4)
            attack_recovery = bToInt(move_bytes, 0x68, 4)
            
            u16 = bToInt(move_bytes, 0x6c, 2) 
            u17 = bToInt(move_bytes, 0x6e, 2) 
            u18 = 0
            
        
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
        self.extra_properties_ptr = extra_properties_ptr
        self.voiceclip_ptr = voiceclip_ptr
        
        self.u1 = u1
        self.u2 = u2
        self.u3 = u3
        self.u4 = u4
        self.u5 = u5
        self.u6 = u6
        self.u7 = u7
        self.u8 = u8
        self.u8_2 = u8_2
        self.u9 = u9
        self.u10 = u10
        self.u11 = u11
        self.u12 = u12
        self.u13 = u13
        self.u14 = u14
        self.u15 = u15
        self.u16 = u16
        self.u17 = u17
        self.u18 = u18
        
        self.anim = AnimData(self.anim_name, base + self.anim_addr)
        self.cancel_idx = -1
        self.hit_condition_idx = -1
        self.extra_properties_idx = -1
        self.voiceclip_idx = -1
        
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
            'voiceclip': self.voiceclip_idx,
            'extra_properties_id': self.extra_properties_idx,
            'hitbox_location': self.hitbox_location,
            'startup': self.startup,
            'recovery': self.recovery,
            
            #'u1': self.u1,
            'u2': self.u2,
            'u3': self.u3,
            'u4': self.u4,
            #'u5': self.u5,
            'u6': self.u6,
            'u7': self.u7,
            'u8': self.u8,
            'u8_2': self.u8_2,
            'u9': self.u9,
            'u10': self.u10,
            'u11': self.u11,
            'u12': self.u12,
            #'u13': self.u13,
            #'u14': self.u14,
            'u15': self.u15,
            'u16': self.u16,
            'u18': self.u18,
            'u17': self.u17
        }
        
    def setCancelIdx(self, cancel_idx):
        self.cancel_idx = cancel_idx
        
    def setHitConditionIdx(self, id):
        self.hit_condition_idx = id
        
    def setExtraPropertiesIdx(self, id):
        self.extra_properties_idx = id
        
    def setVoiceclipId(self, id):
        self.voiceclip_idx = id

    def setId(self, id):
        self.id = id
    
class Voiceclip:
    size = 4
    
    def __init__(self, addr):
        self.addr = addr
        
        self.id = readInt(base + addr, 4)

    def dict(self):
        return self.id
        
class InputExtradata:
    size = 8
    
    def __init__(self, addr):
        self.addr = addr
        data = readBytes(base + addr, InputExtradata.size)
        
        self.u1 = bToInt(data, 0, 4)
        self.u2 = bToInt(data, 4, 4)
        
    def dict(self):
        return {
            'u1': self.u1,
            'u2': self.u2
        }
        
class InputSequence:
    size = 0x10 if TekkenVersion == 7 else 0x8
    
    def __init__(self, addr):
        self.addr = addr
        data = readBytes(base + addr, InputSequence.size)
        
        if TekkenVersion == 7:
            self.u1 = bToInt(data, 0, 2)
            self.u2 = bToInt(data, 2, 2)
            self.u3 = bToInt(data, 4, 4)
            self.extradata_addr = bToInt(data, 8, ptr_size)
        else:
            self.u1 = bToInt(data, 1, 1)
            self.u2 = bToInt(data, 2, 2)
            self.u3 = bToInt(data, 0, 1)
            self.extradata_addr = bToInt(data, 4, ptr_size)
        
        self.extradata_idx = -1
        
    def setExtradataId(self, idx):
        self.extradata_idx = idx
        
    def dict(self):
        return {
            'u1': self.u1,
            'u2': self.u2,
            'u3': self.u3,
            'extradata_id': self.extradata_idx
        }
        
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

        extra_move_properties_ptr = 0x1e0 if TekkenVersion == 7 else 0x188
        extra_move_properties_size = extra_move_properties_ptr + ptr_size
        self.extra_move_properties_ptr = readInt(addr + extra_move_properties_ptr, ptr_size)
        self.extra_move_properties_size = readInt(addr + extra_move_properties_size, 4)

        movelist_head_ptr = 0x210 if TekkenVersion == 7 else 0x1a0
        movelist_size = movelist_head_ptr + ptr_size
        self.movelist_head_ptr = readInt(addr + movelist_head_ptr, ptr_size)
        self.movelist_size = readInt(addr + movelist_size, ptr_size)

        voiceclip_list_ptr = 0x220 if TekkenVersion == 7 else 0x1a8
        voiceclip_list_size = voiceclip_list_ptr + ptr_size
        self.voiceclip_list_ptr = readInt(addr + voiceclip_list_ptr, ptr_size)
        self.voiceclip_list_size = readInt(addr + voiceclip_list_size, ptr_size)

        input_sequence_ptr = 0x230 if TekkenVersion == 7 else 0x1b0
        input_sequence_size = input_sequence_ptr + ptr_size
        self.input_sequence_ptr = readInt(addr + input_sequence_ptr, ptr_size)
        self.input_sequence_size = readInt(addr + input_sequence_size, ptr_size)

        input_extradata_ptr = 0x240 if TekkenVersion == 7 else 0x1b8
        input_extradata_size = input_extradata_ptr + ptr_size
        self.input_extradata_ptr = readInt(addr + input_extradata_ptr, ptr_size)
        self.input_extradata_size = readInt(addr + input_extradata_size, ptr_size)

        test_ptr = 0x250 if TekkenVersion == 7 else 0x1c0
        test_size = test_ptr + ptr_size
        self.test_ptr = readInt(addr + test_ptr, ptr_size)
        self.test_size = readInt(addr + test_size, ptr_size)
        
        
        aliasCopySize = 0x2a
        aliasOffset = 0x98 if TekkenVersion == 7 else 0x88
        aliasCount = 148
    
        self.aliases = [readInt(addr + aliasOffset + (offset * 2), 2) for offset in range(0, aliasCount)]
        
        self.requirements = []
        self.cancels = []
        self.moves = []
        self.anims = []
        self.group_cancels = []
        self.reaction_list = []
        self.hit_conditions = []
        self.pushbacks = []
        self.pushback_extras = []
        self.extra_move_properties = []
        self.voiceclips = []
        self.input_sequences = []
        self.input_extradata = []
        
    def printBasicData(self):
        print("Character: %s" % (self.character_name))
        print("Creator: %s" % (self.creator_name))
        print("Date: %s %s\n" % (self.date, self.fulldate))
        
    def dict(self):
        anim_names = [anim.name for anim in self.anims]
        
        return {
            'export_version': exportVersion,
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
            'pushback_extras': self.pushback_extras,
            'extra_move_properties': self.extra_move_properties,
            'voiceclips': self.voiceclips,
            'input_sequences': self.input_sequences,
            'input_extradata': self.input_extradata
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
            
        print("Saved at path %s/%s\n" % (os.getcwd(), path[2:]))
        
    def extractMoveset(self):
        self.printBasicData()
        
        print("Reading input extradata...")
        for i in range(self.input_extradata_size + 1):
            input_extradata = InputExtradata(self.input_extradata_ptr + (i * InputExtradata.size))
            self.input_extradata.append(input_extradata.dict())
        
        print("Reading input sequences...")
        for i in range(self.input_sequence_size):
            input_sequence = InputSequence(self.input_sequence_ptr + (i * InputSequence.size))
            input_sequence.setExtradataId((input_sequence.extradata_addr - self.input_extradata_ptr) // InputExtradata.size)
            self.input_sequences.append(input_sequence.dict())

        print("Reading requirements...")
        for i in range(self.requirement_count):
            condition = Requirement(self.requirements_ptr + (i * Requirement.size))
            condition.setId(i)
            self.requirements.append(condition.dict())
        
        print("Reading cancels...")
        for i in range(self.cancel_list_size):
            cancel = Cancel(self.cancel_head_ptr + (i * Cancel.size))
            cancel.setRequirementId((cancel.requirement_addr - self.requirements_ptr) // Requirement.size)
            cancel.setId(i)
            self.cancels.append(cancel.dict())
        
        print("Reading grouped cancels...")
        for i in range(self.group_cancel_list_size):
            cancel = Cancel(self.group_cancel_head_ptr + (i * Cancel.size))
            cancel.setRequirementId((cancel.requirement_addr - self.requirements_ptr) // Requirement.size)
            cancel.setId(i)
            self.group_cancels.append(cancel.dict())
        
        print("Reading pushbacks extradatas...")
        for i in range(self.pushback_extradata_size):
            pushback_extra = PushbackExtradata(self.pushback_extradata_ptr + (i * PushbackExtradata.size))
            self.pushback_extras.append(pushback_extra.dict())

        print("Reading pushbacks...")
        for i in range(self.pushback_list_size):
            pushback = Pushback(self.pushback_ptr + (i * Pushback.pushback_size))
            pushback.setExtraIndex((pushback.extra_addr - self.pushback_extradata_ptr) // PushbackExtradata.size)
            self.pushbacks.append(pushback.dict())
        
        print("Reading reaction lists...")
        for i in range(self.reaction_list_size):
            reaction_list = ReactionList(self.reaction_list_ptr + (i * ReactionList.reaction_list_size))
            reaction_list.setIndexes(self.pushback_ptr, Pushback.pushback_size)
            self.reaction_list.append(reaction_list.dict())
        
        print("Reading on-hit condition lists...")
        for i in range(self.hit_conditions_size):
            hit_conditions = HitCondition(self.hit_conditions_ptr + (i * HitCondition.size))
            hit_conditions.setRequirementId((hit_conditions.requirement_addr - self.requirements_ptr) // Requirement.size)
            hit_conditions.setReactionListId((hit_conditions.reaction_list_addr - self.reaction_list_ptr) // ReactionList.reaction_list_size)
            self.hit_conditions.append(hit_conditions.dict())
        
        print("Reading extra move properties...")
        for i in range(self.extra_move_properties_size):
            extra_move_property = ExtraMoveProperties(self.extra_move_properties_ptr + (i * ExtraMoveProperties.size))
            self.extra_move_properties.append(extra_move_property.dict())
        
        print("Reading voiceclips...")
        for i in range(self.voiceclip_list_size):
            voiceclip = Voiceclip(self.voiceclip_list_ptr + (i * Voiceclip.size))
            self.voiceclips.append(voiceclip.dict())
        
        print("Reading movelist...")
        for i in range(self.movelist_size):
            move = Move(self.movelist_head_ptr + (i * Move.move_size))
            move.setCancelIdx((move.cancel_addr - self.cancel_head_ptr) // Cancel.size)
            move.setHitConditionIdx((move.hit_condition_addr - self.hit_conditions_ptr) // HitCondition.size)
            if move.extra_properties_ptr != 0:
                move.setExtraPropertiesIdx((move.extra_properties_ptr - self.extra_move_properties_ptr) // ExtraMoveProperties.size)
            if move.voiceclip_ptr != 0:
                move.setVoiceclipId((move.voiceclip_ptr - self.voiceclip_list_ptr) // Voiceclip.size)
            move.setId(i)
            self.moves.append(move.dict())
            
            if move.anim not in self.anims:
                self.anims.append(move.anim)
        
        self.save()
        
if __name__ == "__main__":
    cemu_motbin_base = (base + GameAddresses.a['cemu_p1_base'] - 0x98)
    motbin_ptr_addr = (GameAddresses.a['p1_ptr'] + 0x14a0) if TekkenVersion == 7 else cemu_motbin_base
    motbin_ptr = readInt(motbin_ptr_addr, ptr_size)
    
    m = Motbin(base + motbin_ptr)
    m.extractMoveset()
    
    cemu_motbin_base = (base + GameAddresses.a['cemu_p2_base'] - 0x98)
    motbin_ptr_addr = (GameAddresses.a['p2_ptr'] + 0x14a0) if TekkenVersion == 7 else cemu_motbin_base
    motbin_ptr = readInt(motbin_ptr_addr, ptr_size)
    
    m2 = Motbin(base + motbin_ptr)
    if m.name != m2.name:
        m2.extractMoveset()
    
    
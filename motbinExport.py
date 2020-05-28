# --- Ton-Chan's Motbin export --- #
# Python 3.6.5

from Addresses import game_addresses, GameClass
from ByteSwap import SwapAnimBytes
from datetime import datetime, timezone
import json
import os
import sys
import re
from zlib import crc32

exportVersion = "0.9.0"

def getMovesetName(TekkenVersion, character_name):
    if character_name.startswith('['):
        character_name = character_name[1:-1]
    return '%d_%s' % (TekkenVersion, character_name.upper())

def initTekkenStructure(self, parent, addr=0, size=0):
    self.addr = addr
    self.T = parent.T
    self.TekkenVersion = parent.TekkenVersion
    self.ptr_size = parent.ptr_size
    self.base = parent.base
    self.endian = parent.endian
    
    self.readInt = parent.readInt
    self.readBytes = parent.readBytes
    self.readString = parent.readString
    self.readStringPtr = parent.readStringPtr
    self.bToInt = parent.bToInt
    
    if addr != 0 and size != 0:
        self.data = self.readBytes(self.base + addr, size)
    else:
        self.data = None
    return self.data
        
def setStructureSizes(self):
    self.Pushback_size = 0x10 if self.TekkenVersion == 7 else 0xC
    self.PushbackExtradata_size = 0x2
    self.Requirement_size = 0x8
    self.CancelExtradata_size = 0x4
    self.Cancel_size = 0x28 if self.TekkenVersion == 7 else 0x20
    self.ReactionList_size = 0x70 if self.TekkenVersion == 7 else 0x50
    self.HitCondition_size = 0x18 if self.TekkenVersion == 7 else 0xC
    self.ExtraMoveProperty_size = 0xC
    self.Move_size = 0xB0 if self.TekkenVersion == 7 else 0x70
    self.Voiceclip_size = 0x4
    self.InputExtradata_size = 8
    self.InputSequence_size = 0x10 if self.TekkenVersion == 7 else 0x8
    self.Projectile_size = 0xa8 if self.TekkenVersion == 7 else 0x88
    self.ThrowExtra_size = 0xC
    self.Throw_size = 0x10 if self.TekkenVersion == 7 else 0x8
            
class Exporter:
    def __init__(self, TekkenVersion, folder_destination='./extracted_chars/'):
        game_addresses.reloadValues()

        self.T = GameClass("TekkenGame-Win64-Shipping.exe" if TekkenVersion == 7 else "Cemu.exe")
        self.TekkenVersion = TekkenVersion
        self.ptr_size = 8 if TekkenVersion == 7 else 4
        self.base = 0x0 if TekkenVersion == 7 else game_addresses.addr['cemu_base']
        self.endian = 'little' if TekkenVersion == 7 else 'big'
        self.folder_destination = folder_destination
            
        if self.base == 0x9999999999999999:
            raise Exception("Cemu base address has not been modified yet, please insert the correct cemu_base address in game_address.txt")
        
        
        if not os.path.isdir(folder_destination):
            os.mkdir(folder_destination)
        
    def getCemuP1Addr(self):
        windowTitle = self.T.getWindowTitle()
        p = re.compile("TitleId: ([0-9a-fA-F]{8}\-[0-9a-fA-F]{8})")
        match = p.search(windowTitle)
        if match == None:
            return None
        key = match.group(1) + '_p1_addr'
        return None if key not in game_addresses.addr else game_addresses.addr[key]
        
    def readInt(self, addr, len):
        return self.T.readInt(addr, len, endian=self.endian)
        
    def readBytes(self, addr, len):
        return self.T.readBytes(addr, len)
        
    def readString(self, addr):
        offset = 0
        while self.readInt(addr + offset, 1) != 0:
            offset += 1
        return self.readBytes(addr, offset).decode("ascii")
        
    def readStringPtr(self, addr):
        return self.readString(self.base + self.readInt(addr, self.ptr_size))
        
    def bToInt(self, data, offset, length, ed=None):
        return int.from_bytes(data[offset:offset + length], ed if ed != None else self.endian)
        
    def getMotbinPtr(self, playerAddress):
        motbin_ptr_addr = (playerAddress + game_addresses.addr['motbin_offset']) if self.TekkenVersion == 7 else playerAddress - 0x98
        return self.readInt(motbin_ptr_addr, self.ptr_size)
            
    def getPlayerMovesetName(self, playerAddress):
        motbin_ptr = self.getMotbinPtr(self.base + playerAddress)
        return self.readStringPtr(self.base + motbin_ptr + 8)
            
    def exportMoveset(self, playerAddress, name=''):
        motbin_ptr = self.getMotbinPtr(self.base + playerAddress)
        
        m = Motbin(self.base + motbin_ptr, self, name)
        m.getCharacterId(playerAddress)
        m.extractMoveset()
        return m
        
def GetTT2AnimEndPos(data, searchStart):
    return [
        data[searchStart:].find(b'\x00\x64\x00\x17\x00'),
        data[searchStart:].find(b'\x00\x64\x00\x1B\x00'),
        data[searchStart:].find(b'\x00\xC8\x00\x17'),
        data[searchStart:].find(b'motOrigin'),
        data[searchStart:].find(bytes([0] * 100))
    ]
    
def GetT7AnimEndPos(data, searchStart):
    return [
        data[searchStart:].find(b'\x64\x00\x17\x00'),
        data[searchStart:].find(b'\x64\x00\x1B\x00'),
        data[searchStart:].find(b'\xC8\x00\x17'),
        data[searchStart:].find(b'motOrigin'),
        data[searchStart:].find(bytes([0] * 100))
    ]
    
def getAnimEndPos(TekkenVersion, data):
    minSize = 1000
    if len(data) < minSize:
        return -1
    searchStart = minSize - 100
    pos = GetT7AnimEndPos(data, searchStart) if TekkenVersion == 7 else GetTT2AnimEndPos(data, searchStart)
    pos = [p+searchStart for p in pos if p != -1]
    return -1 if len(pos) == 0 else min(pos)
    
class AnimData:
    def __init__(self, name, data_addr, parent):
        initTekkenStructure(self, parent, data_addr, 0)
        self.name = name
        self.data = None
                
    def getData(self):
        if self.data == None:
            read_size = 8192
            offset = 0
            prev_bytes = None
            maxSize = 50000000 
            
            while read_size >= 16:
                try:
                    curr_bytes = self.readBytes(self.addr + offset, read_size)
                except Exception as e:
                    read_size //= 2
                else:
                    tmp = curr_bytes
                    if prev_bytes != None:
                        curr_bytes = prev_bytes + curr_bytes
                    
                    endPos = getAnimEndPos(self.TekkenVersion, curr_bytes)
                    if endPos != -1:
                        offset += endPos
                        break
                    
                    prev_bytes = tmp
                    if offset + read_size > maxSize:
                        break
                    offset += read_size
                    
            try:
                self.data = None if offset == 0 else self.readBytes(self.addr, offset)
            except:
                print("Error extracting animation " + self.name + ", game might crash with this moveset.", file=sys.stderr)
                return None
                
            oldData = self.data
            if self.TekkenVersion != 7:
                try:
                    self.data = SwapAnimBytes(self.data)
                except:
                    self.data = oldData
                    print("Error byteswapping animation " + self.name + ", game might crash with this moveset.", file=sys.stderr)
        return self.data
        
    def __eq__(self, other):
        return self.name == other.name
        
class Pushback:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.Pushback_size)
        
        self.val1 = self.bToInt(data, 0, 2)
        self.val2 = self.bToInt(data, 2, 2)
        self.val3 = self.bToInt(data, 4, 4)
        self.extra_index = -1
        self.extra_addr = self.bToInt(data, 8, self.ptr_size)
        
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
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.PushbackExtradata_size)
        
        self.value = self.bToInt(data, 0, 2)
        
    def dict(self):
        return self.value
        
class Requirement:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.Requirement_size)
        
        data = self.readBytes(self.base + addr, 0x8)
        self.req = self.bToInt(data, 0, 4)
        self.param = self.bToInt(data, 4, 4)
        self.id = -1
        
    def dict(self):
        return {
            'id': self.id,
            'req': self.req,
            'param': self.param
        }
        
    def setId(self, id):
        self.id = id
        
class CancelExtradata:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.CancelExtradata_size)
        
        self.value = self.bToInt(data, 0x0, parent.CancelExtradata_size)
        
    def dict(self):
        return self.value
        
        
class Cancel:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.Cancel_size)
        
        
        after_ptr_offset = 0x18 if self.TekkenVersion == 7 else 0x10
        
        self.command = self.bToInt(data, 0x0, 8)
        self.requirement_addr = self.bToInt(data, 0x8, self.ptr_size)
        self.extradata_addr = self.bToInt(data, 0x8 + self.ptr_size, self.ptr_size)
        self.frame_window_start = self.bToInt(data, after_ptr_offset, 4)
        self.frame_window_end = self.bToInt(data, after_ptr_offset + 4, 4)
        self.starting_frame = self.bToInt(data,after_ptr_offset + 8, 4)
        self.move_id = self.bToInt(data, after_ptr_offset + 12, 2)
        self.cancel_option = self.bToInt(data, after_ptr_offset + 14, 2)
        
        if self.TekkenVersion != 7: #swapping first two ints
            t = self.bToInt(data, 0, 4)
            t2 = self.bToInt(data, 0x4, 4) 
            self.command = (t2 << 32) | t
        
        self.id = -1
        self.extradata_id = -1
        
    def dict(self):
        return {
            'id': self.id,
            'command': self.command,
            'extradata': self.extradata_id,
            'requirement': self.requirement_idx,
            'frame_window_start': self.frame_window_start,
            'frame_window_end': self.frame_window_end,
            'starting_frame': self.starting_frame,
            'move_id': self.move_id,
            'cancel_option': self.cancel_option
        }
    
    def setRequirementId(self, requirement_idx):
        self.requirement_idx = requirement_idx
    
    def setExtradataId(self, extradata_id):
        self.extradata_id = extradata_id
        
    def setId(self, id):
        self.id = id
        
class ReactionList:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.ReactionList_size)
        
        self.ptr_list = [self.bToInt(data, i * self.ptr_size, self.ptr_size) for i in range(7)]
        self.pushback_indexes = [-1] * 7
        
        self.u1list = [self.bToInt(data, (self.ptr_size * 7) + i * 2, 2) for i in range(6)]
        
        list_starting_offset = 0x50 if self.TekkenVersion == 7 else 0x34
        self.reaction_list = [self.bToInt(data, list_starting_offset + (offset * 2), 2) for offset in range(0, 14)]
        
        
        self.vertical_pushback = self.bToInt(data, list_starting_offset - 4, 2)
        self.standing = self.bToInt(data, list_starting_offset + 0x0, 2)
        self.crouch = self.bToInt(data, list_starting_offset + 0x2, 2)
        self.ch = self.bToInt(data, list_starting_offset + 0x4, 2)
        self.crouch_ch = self.bToInt(data, list_starting_offset + 0x6, 2)
        self.left_side = self.bToInt(data, list_starting_offset + 0x8, 2)
        self.left_side_crouch = self.bToInt(data, list_starting_offset + 0xA, 2)
        self.right_side = self.bToInt(data, list_starting_offset + 0xC, 2)
        self.right_side_crouch = self.bToInt(data, list_starting_offset + 0xE, 2)
        self.back = self.bToInt(data, list_starting_offset + 0x10, 2)
        self.back_crouch = self.bToInt(data, list_starting_offset + 0x12, 2)
        self.block = self.bToInt(data, list_starting_offset + 0x14, 2)
        self.crouch_block = self.bToInt(data, list_starting_offset + 0x16, 2)
        self.wallslump = self.bToInt(data, list_starting_offset + 0x18, 2)
        self.downed = self.bToInt(data, list_starting_offset + 0x1A, 2)
        
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
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.HitCondition_size)
        
        self.reaction_list_idx = -1
        self.requirement_idx = -1
        
        self.requirement_addr = self.bToInt(data, 0x0, self.ptr_size)
        self.damage = self.bToInt(data, self.ptr_size, 4)
        self.reaction_list_addr = self.bToInt(data, self.ptr_size * 2, self.ptr_size)
        
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
    
class ExtraMoveProperty:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.ExtraMoveProperty_size)
        
        self.type = self.bToInt(data, 0, 4)
        self.id = self.bToInt(data, 4, 4)
        self.value = self.bToInt(data, 8, 4)
            
    def dict(self):
        return {
            'type': self.type,
            'id': self.id,
            'value': self.value
        }
    
class Move:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.Move_size)
        
        if self.TekkenVersion == 7:
            move_name_addr = self.bToInt(data, 0x0, self.ptr_size)
            anim_name_addr = self.bToInt(data, 0x8, self.ptr_size)
            anim_data_addr = self.bToInt(data, 0x10, self.ptr_size)
            vuln = self.bToInt(data, 0x18, 4)
            hit_level = self.bToInt(data, 0x1c, 4)
            cancel_ptr = self.bToInt(data, 0x20, self.ptr_size)
            
            u1 = 0#bToInt(data, 0x28, self.ptr_size) #pointer!!!
            u2 = self.bToInt(data, 0x30, self.ptr_size) #NOT pointer
            u3 = self.bToInt(data, 0x38, self.ptr_size)
            u4 = self.bToInt(data, 0x40, self.ptr_size)
            u5 = 0#bToInt(data, 0x48, self.ptr_size)  #pointer!!!
            u6 = self.bToInt(data, 0x50, 4)
            
            transition = self.bToInt(data, 0x54, 2)
            
            u7 = self.bToInt(data, 0x56, 2)
            u8 = self.bToInt(data, 0x58, 2)
            u8_2 = self.bToInt(data, 0x5A, 2)
            u9 = self.bToInt(data, 0x5C, 4)
            
            on_hit_ptr = self.bToInt(data, 0x60, self.ptr_size)
            anim_max_length = self.bToInt(data, 0x68, 4)
            
            u10 = self.bToInt(data, 0x6c, 4)
            u11 = self.bToInt(data, 0x70, 4)
            u12 = self.bToInt(data, 0x74, 4)
            
            voiceclip_ptr = self.bToInt(data, 0x78, self.ptr_size) #can_be_null
            extra_properties_ptr = self.bToInt(data, 0x80, self.ptr_size) #can_be_null
            
            u13 = 0#bToInt(data, 0x88, 8) #pointer!!!
            u14 = 0#bToInt(data, 0x90, 8) #pointer!!!
            u15 = self.bToInt(data, 0x98, 4)
            
            hitbox_location = self.bToInt(data, 0x9c, 4)
            attack_startup = self.bToInt(data, 0xa0, 4)
            attack_recovery = self.bToInt(data, 0xa4, 4)
            
            u16 = self.bToInt(data, 0xa8, 2)
            u17 = self.bToInt(data, 0xaa, 2)
            u18 = self.bToInt(data, 0xac, 4)
        else:
            move_name_addr = self.bToInt(data, 0x0, self.ptr_size)
            anim_name_addr = self.bToInt(data, 0x4, self.ptr_size)
            anim_data_addr = self.bToInt(data, 0x8, self.ptr_size)
            vuln = self.bToInt(data, 0xC, 4)
            hit_level = self.bToInt(data, 0x10, 4)
            cancel_ptr = self.bToInt(data, 0x14, self.ptr_size)
            
            u1 = 0#bToInt(data, 0x18, self.ptr_size) #pointer!!!
            u2 = self.bToInt(data, 0x1c, self.ptr_size) #NOT pointer
            u3 = self.bToInt(data, 0x20, self.ptr_size)
            u4 = self.bToInt(data, 0x24, self.ptr_size)
            u5 = 0#bToInt(data, 0x28, self.ptr_size) #pointer!!!
            u6 = self.bToInt(data, 0x2c, 4)
            
            transition = self.bToInt(data, 0x30, 2)
            
            u7 = self.bToInt(data, 0x32, 2) 
            u8 = self.bToInt(data, 0x36, 2)
            u8_2 = self.bToInt(data, 0x34, 2) #inverted offsets for 0x36 & 0x34
            u9 = 0 
            
            on_hit_ptr = self.bToInt(data, 0x38, self.ptr_size)
            anim_max_length = self.bToInt(data, 0x3c, 4)
            
            u10 = self.bToInt(data, 0x40, 4)
            u11 = self.bToInt(data, 0x44, 4)
            u12 = self.bToInt(data, 0x48, 4)
            
            voiceclip_ptr = self.bToInt(data, 0x4c, self.ptr_size) #can_be_null
            extra_properties_ptr = self.bToInt(data, 0x50, self.ptr_size) #can_be_null
            
            u13 = 0#bToInt(data, 0x54, 4) #pointer!!!
            u14 = 0#bToInt(data, 0x58, 4) #pointer!!!
            u15 = self.bToInt(data, 0x5c, 4)
            
            hitbox_location = self.bToInt(data, 0x60, 4, ed='little')
            attack_startup = self.bToInt(data, 0x64, 4)
            attack_recovery = self.bToInt(data, 0x68, 4)
            
            u16 = self.bToInt(data, 0x6c, 2) 
            u17 = self.bToInt(data, 0x6e, 2) 
            u18 = 0
            
        
        self.name = self.readString(self.base + move_name_addr)
        self.anim_name = self.readString(self.base + anim_name_addr)
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
        
        self.anim = AnimData(self.anim_name, self.base + self.anim_addr, self)
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
            
            #'u1': self.u1, #pointer
            'u2': self.u2,
            'u3': self.u3,
            'u4': self.u4,
            #'u5': self.u5, #pointer
            'u6': self.u6,
            'u7': self.u7,
            'u8': self.u8,
            'u8_2': self.u8_2,
            'u9': self.u9,
            'u10': self.u10,
            'u11': self.u11,
            'u12': self.u12,
            #'u13': self.u13, #pointer
            #'u14': self.u14, #pointer
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
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.Voiceclip_size)
        
        self.value = self.bToInt(data, 0, 4)

    def dict(self):
        return self.value
        
class InputExtradata:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.InputExtradata_size)
        
        self.u1 = self.bToInt(data, 0, 4)
        self.u2 = self.bToInt(data, 4, 4)
        
    def dict(self):
        return {
            'u1': self.u1,
            'u2': self.u2
        }
        
class InputSequence:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.InputSequence_size)
        
        if self.TekkenVersion == 7:
            self.u1 = self.bToInt(data, 0, 2)
            self.u2 = self.bToInt(data, 2, 2)
            self.u3 = self.bToInt(data, 4, 4)
            self.extradata_addr = self.bToInt(data, 8, self.ptr_size)
        else:
            self.u1 = self.bToInt(data, 1, 1)
            self.u2 = self.bToInt(data, 2, 2)
            self.u3 = self.bToInt(data, 0, 1)
            self.extradata_addr = self.bToInt(data, 4, self.ptr_size)
        
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
        
class Projectile:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.Projectile_size)
        
        if self.TekkenVersion == 7:
            self.u1 = [self.bToInt(data, offset * 2, 2) for offset in range(48)]
            
            self.hit_condition_addr = self.bToInt(data, 0x60, self.ptr_size)
            self.cancel_addr = self.bToInt(data, 0x68, self.ptr_size)
            
            self.u2 = [self.bToInt(data, 0x70 + (offset * 2), 2) for offset in range(28)]
        else:
            self.u1 = [0] * 48
            
            self.hit_condition_addr = 0#bToInt(data, 0x60, self.ptr_size)
            self.cancel_addr = 0#bToInt(data, 0x68, self.ptr_size)
            
            self.u2 = [0] * 28
        
        self.hit_condition = -1
        self.cancel_idx = -1
        
    def dict(self):
        return {
            'u1': self.u1,
            'u2': self.u2,
            'hit_condition': self.hit_condition,
            'cancel': self.cancel_idx
        }
        
    def setHitConditionIdx(self, idx):
        self.hit_condition = idx
        
    def setCancelIdx(self, cancel_idx):
        self.cancel_idx = cancel_idx
        
class ThrowExtra:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.ThrowExtra_size)
        
        self.u1 = self.bToInt(data, 0x0, 4)
        self.u2 = [self.bToInt(data, 4 + offset * 2, 2) for offset in range(4)]

    def dict(self):
        return {
            'u1': self.u1,
            'u2': self.u2
        }
        
class Throw:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.Throw_size)
        
        self.u1 = self.bToInt(data, 0, self.ptr_size)
        self.unknown_addr = self.bToInt(data, self.ptr_size, self.ptr_size)
        
        self.unknown_idx = -1
        
    def dict(self):
        return {
            'u1': self.u1,
            'unknown_idx': self.unknown_idx
        }
        
    def setUnknownIdx(self, idx):
        self.unknown_idx = idx
        
class Motbin:
    def __init__(self, addr, exporterObject, name=''):
        initTekkenStructure(self, exporterObject, addr, size=0)
        setStructureSizes(self)
        self.folder_destination= exporterObject.folder_destination
    
        self.name = ''
        self.version = "Tekken7" if self.TekkenVersion == 7 else "Tag2"
        self.extraction_date = datetime.now(timezone.utc).__str__()
        self.extraction_path = ''
    
        character_name_addr = 0x8
        creator_name_addr = character_name_addr + self.ptr_size
        date_addr = creator_name_addr + self.ptr_size
        fulldate_addr = date_addr + self.ptr_size

        try:
            self.character_name = self.readStringPtr(addr + character_name_addr)
            self.creator_name = self.readStringPtr(addr + creator_name_addr)
            self.date = self.readStringPtr(addr + date_addr)
            self.fulldate = self.readStringPtr(addr + fulldate_addr)
        
            reaction_list_ptr = 0x150 if self.TekkenVersion == 7 else 0x140
            reaction_list_size = reaction_list_ptr + self.ptr_size
            self.reaction_list_ptr = self.readInt(addr + reaction_list_ptr, self.ptr_size)
            self.reaction_list_size = self.readInt(addr + reaction_list_size, self.ptr_size)
            
            requirements_ptr = 0x160 if self.TekkenVersion == 7 else 0x148
            requirement_count = requirements_ptr + self.ptr_size
            self.requirements_ptr = self.readInt(addr + requirements_ptr, self.ptr_size)
            self.requirement_count = self.readInt(addr + requirement_count, self.ptr_size)
            
            hit_conditions_ptr = 0x170 if self.TekkenVersion == 7 else 0x150
            hit_conditions_size = hit_conditions_ptr + self.ptr_size
            self.hit_conditions_ptr = self.readInt(addr + hit_conditions_ptr, self.ptr_size)
            self.hit_conditions_size = self.readInt(addr + hit_conditions_size, self.ptr_size)
            
            projectile_ptr = 0x180 if self.TekkenVersion == 7 else 0x158
            projectile_size = projectile_ptr + self.ptr_size
            self.projectile_ptr = self.readInt(addr + projectile_ptr, self.ptr_size)
            self.projectile_size = self.readInt(addr + projectile_size, self.ptr_size)
            
            pushback_ptr = 0x190 if self.TekkenVersion == 7 else 0x160
            pushback_list_size = pushback_ptr + self.ptr_size
            self.pushback_ptr = self.readInt(addr + pushback_ptr, self.ptr_size)
            self.pushback_list_size = self.readInt(addr + pushback_list_size, self.ptr_size)

            pushback_extradata_ptr = 0x1A0 if self.TekkenVersion == 7 else 0x168
            pushback_extradata_size = pushback_extradata_ptr + self.ptr_size
            self.pushback_extradata_ptr = self.readInt(addr + pushback_extradata_ptr, self.ptr_size)
            self.pushback_extradata_size = self.readInt(addr + pushback_extradata_size, self.ptr_size)

            cancel_head_ptr = 0x1b0 if self.TekkenVersion == 7 else 0x170
            cancel_list_size = cancel_head_ptr + self.ptr_size
            self.cancel_head_ptr = self.readInt(addr + cancel_head_ptr, self.ptr_size)
            self.cancel_list_size = self.readInt(addr + cancel_list_size, self.ptr_size)

            group_cancel_head_ptr = 0x1c0 if self.TekkenVersion == 7 else 0x178
            group_cancel_list_size = group_cancel_head_ptr + self.ptr_size
            self.group_cancel_head_ptr = self.readInt(addr + group_cancel_head_ptr, self.ptr_size)
            self.group_cancel_list_size = self.readInt(addr + group_cancel_list_size, self.ptr_size)

            cancel_extradata_head_ptr = 0x1d0 if self.TekkenVersion == 7 else 0x180
            cancel_extradata_list_size = cancel_extradata_head_ptr + self.ptr_size
            self.cancel_extradata_head_ptr = self.readInt(addr + cancel_extradata_head_ptr, self.ptr_size)
            self.cancel_extradata_list_size = self.readInt(addr + cancel_extradata_list_size, self.ptr_size)

            extra_move_properties_ptr = 0x1e0 if self.TekkenVersion == 7 else 0x188
            extra_move_properties_size = extra_move_properties_ptr + self.ptr_size
            self.extra_move_properties_ptr = self.readInt(addr + extra_move_properties_ptr, self.ptr_size)
            self.extra_move_properties_size = self.readInt(addr + extra_move_properties_size, self.ptr_size)

            movelist_head_ptr = 0x210 if self.TekkenVersion == 7 else 0x1a0
            movelist_size = movelist_head_ptr + self.ptr_size
            self.movelist_head_ptr = self.readInt(addr + movelist_head_ptr, self.ptr_size)
            self.movelist_size = self.readInt(addr + movelist_size, self.ptr_size)

            voiceclip_list_ptr = 0x220 if self.TekkenVersion == 7 else 0x1a8
            voiceclip_list_size = voiceclip_list_ptr + self.ptr_size
            self.voiceclip_list_ptr = self.readInt(addr + voiceclip_list_ptr, self.ptr_size)
            self.voiceclip_list_size = self.readInt(addr + voiceclip_list_size, self.ptr_size)

            input_sequence_ptr = 0x230 if self.TekkenVersion == 7 else 0x1b0
            input_sequence_size = input_sequence_ptr + self.ptr_size
            self.input_sequence_ptr = self.readInt(addr + input_sequence_ptr, self.ptr_size)
            self.input_sequence_size = self.readInt(addr + input_sequence_size, self.ptr_size)

            input_extradata_ptr = 0x240 if self.TekkenVersion == 7 else 0x1b8
            input_extradata_size = input_extradata_ptr + self.ptr_size
            self.input_extradata_ptr = self.readInt(addr + input_extradata_ptr, self.ptr_size)
            self.input_extradata_size = self.readInt(addr + input_extradata_size, self.ptr_size)

            throw_extras_ptr = 0x260 if self.TekkenVersion == 7 else 0x1c8
            throw_extras_size = throw_extras_ptr + self.ptr_size
            self.throw_extras_ptr = self.readInt(addr + throw_extras_ptr, self.ptr_size)
            self.throw_extras_size = self.readInt(addr + throw_extras_size, self.ptr_size)

            throws_ptr = 0x270 if self.TekkenVersion == 7 else 0x1d0
            throws_size = throws_ptr + self.ptr_size
            self.throws_ptr = self.readInt(addr + throws_ptr, self.ptr_size)
            self.throws_size = self.readInt(addr + throws_size, self.ptr_size)
            
            aliasCopySize = 0x2a
            aliasOffset = fulldate_addr + self.ptr_size
            aliasCount = 148
        
            self.aliases = [self.readInt(addr + aliasOffset + (offset * 2), 2) for offset in range(0, aliasCount)]
            
            self.name = getMovesetName(self.TekkenVersion, self.character_name) if name == '' else name
            self.export_folder = self.name
            
        except Exception as e:
            print("Invalid character or moveset.")
            raise e
        
        self.chara_id = -1
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
        self.cancel_extradata = []
        self.projectiles = []
        self.throw_extras = []
        self.throws = []
        
    def __eq__(self, other):
        return self.character_name == other.character_name \
            and self.creator_name == other.creator_name \
            and self.date == other.date \
            and self.fulldate == other.fulldate
        
    def getCharacterId(self, playerAddress):
        key = 'chara_id_offset' if self.TekkenVersion == 7 else 'cemu_chara_id_offset'
        self.chara_id = (self.readInt(self.base + playerAddress + game_addresses.addr[key], 4))
        
    def printBasicData(self):
        if self.chara_id == -1:
            print("Character: %s" % (self.character_name))
        else:
            print("Character: %s (ID %d)" % (self.character_name, self.chara_id))
        print("Creator: %s" % (self.creator_name))
        print("Date: %s %s\n" % (self.date, self.fulldate))
        
    def dict(self):
        anim_names = [anim.name for anim in self.anims]
        
        return {
            'original_hash': '',
            'export_version': exportVersion,
            'version': self.version,
            'character_id': self.chara_id,
            'extraction_date': self.extraction_date,
            'character_name': self.name,
            'tekken_character_name': self.character_name,
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
            'input_extradata': self.input_extradata,
            'cancel_extradata': self.cancel_extradata,
            'projectiles': self.projectiles,
            'throw_extras': self.throw_extras,
            'throws': self.throws
        }
        
    def calculateHash(self, selfData):
        exclude_keys =  [
            'original_hash',
            'export_version',
            'character_name',
            'extraction_date',
            'character_name',
            'tekken_character_name',
            'creator_name',
            'date',
            'fulldate'
        ]    
        
        data = ""
        
        for k in (key for key in selfData.keys() if key not in exclude_keys):
           data += str(selfData[k])
        
        data = bytes(str.encode(data))
        
        return "%x" % (crc32(data))
        
    def save(self):
        print("Saving data...")
        
        path = self.folder_destination + self.export_folder
        self.extraction_path = path
        anim_path = "%s/anim" % (path)
        
        if not os.path.isdir(path):
            os.mkdir(path)
        if not os.path.isdir(anim_path):
            os.mkdir(anim_path)
            
        with open("%s/%s.json" % (path, self.name), "w") as f:
            selfData = self.dict()
            selfData['original_hash'] = self.calculateHash(selfData)
            json.dump(selfData, f, indent=4)
            
        print("Saving animations...")
        for anim in self.anims:
            try:
                with open ("%s/%s.bin" % (anim_path, anim.name), "wb") as f:
                    animdata = anim.getData()
                    f.write(animdata if animdata != None else bytes([0]))
                    if animdata == None:
                        raise
            except:
                print("Error extracting animation %s, file will not be created" % (anim.name), file=sys.stderr)
            
        print("Saved at path %s.\nHash: %s" % (path.replace("\\", "/"), selfData['original_hash']))
        
    def extractMoveset(self):
        self.printBasicData()
        
        print("Reading input extradata...")
        for i in range(self.input_extradata_size + 1):
            input_extradata = InputExtradata(self.input_extradata_ptr + (i * self.InputExtradata_size), self)
            self.input_extradata.append(input_extradata.dict())
        
        print("Reading input sequences...")
        for i in range(self.input_sequence_size):
            input_sequence = InputSequence(self.input_sequence_ptr + (i * self.InputSequence_size), self)
            input_sequence.setExtradataId((input_sequence.extradata_addr - self.input_extradata_ptr) // self.InputExtradata_size)
            self.input_sequences.append(input_sequence.dict())
            
        print("Reading requirements...")
        for i in range(self.requirement_count):
            condition = Requirement(self.requirements_ptr + (i * self.Requirement_size), self)
            condition.setId(i)
            self.requirements.append(condition.dict())
            
        print("Reading cancels extradatas...")
        for i in range(self.cancel_extradata_list_size):
            extradata = CancelExtradata(self.cancel_extradata_head_ptr + (i * self.CancelExtradata_size), self)
            self.cancel_extradata.append(extradata.dict())
        
        print("Reading cancels...")
        for i in range(self.cancel_list_size):
            cancel = Cancel(self.cancel_head_ptr + (i * self.Cancel_size), self)
            cancel.setRequirementId((cancel.requirement_addr - self.requirements_ptr) // self.Requirement_size)
            cancel.setExtradataId((cancel.extradata_addr - self.cancel_extradata_head_ptr) // self.CancelExtradata_size)
            cancel.setId(i)
            self.cancels.append(cancel.dict())
        
        print("Reading grouped cancels...")
        for i in range(self.group_cancel_list_size):
            cancel = Cancel(self.group_cancel_head_ptr + (i * self.Cancel_size), self)
            cancel.setRequirementId((cancel.requirement_addr - self.requirements_ptr) // self.Requirement_size)
            cancel.setExtradataId((cancel.extradata_addr - self.cancel_extradata_head_ptr) // self.CancelExtradata_size)
            cancel.setId(i)
            self.group_cancels.append(cancel.dict())
        
        print("Reading pushbacks extradatas...")
        for i in range(self.pushback_extradata_size):
            pushback_extra = PushbackExtradata(self.pushback_extradata_ptr + (i * self.PushbackExtradata_size), self)
            self.pushback_extras.append(pushback_extra.dict())

        print("Reading pushbacks...")
        for i in range(self.pushback_list_size):
            pushback = Pushback(self.pushback_ptr + (i * self.Pushback_size), self)
            pushback.setExtraIndex((pushback.extra_addr - self.pushback_extradata_ptr) // self.PushbackExtradata_size)
            self.pushbacks.append(pushback.dict())
        
        print("Reading reaction lists...")
        for i in range(self.reaction_list_size):
            reaction_list = ReactionList(self.reaction_list_ptr + (i * self.ReactionList_size), self)
            reaction_list.setIndexes(self.pushback_ptr, self.Pushback_size)
            self.reaction_list.append(reaction_list.dict())
        
        print("Reading on-hit condition lists...")
        for i in range(self.hit_conditions_size):
            hit_conditions = HitCondition(self.hit_conditions_ptr + (i * self.HitCondition_size), self)
            hit_conditions.setRequirementId((hit_conditions.requirement_addr - self.requirements_ptr) // self.Requirement_size)
            hit_conditions.setReactionListId((hit_conditions.reaction_list_addr - self.reaction_list_ptr) // self.ReactionList_size)
            self.hit_conditions.append(hit_conditions.dict())
        
        print("Reading extra move properties...")
        for i in range(self.extra_move_properties_size):
            extra_move_property = ExtraMoveProperty(self.extra_move_properties_ptr + (i * self.ExtraMoveProperty_size), self)
            self.extra_move_properties.append(extra_move_property.dict())
        
        print("Reading voiceclips...")
        for i in range(self.voiceclip_list_size):
            voiceclip = Voiceclip(self.voiceclip_list_ptr + (i * self.Voiceclip_size), self)
            self.voiceclips.append(voiceclip.dict())
            
        print("Reading projectiles...")
        for i in range(self.projectile_size):
            projectile = Projectile(self.projectile_ptr + (i * self.Projectile_size), self)
            if projectile.cancel_addr != 0:
                projectile.setCancelIdx((projectile.cancel_addr - self.cancel_head_ptr) // self.Cancel_size)
            if projectile.hit_condition_addr != 0:
                projectile.setHitConditionIdx((projectile.hit_condition_addr - self.hit_conditions_ptr) // self.HitCondition_size)
            self.projectiles.append(projectile.dict())
            
        print("Reading throw extras...")
        for i in range(self.throw_extras_size):
            throw_extra = ThrowExtra(self.throw_extras_ptr + (i * self.ThrowExtra_size), self)
            self.throw_extras.append(throw_extra.dict())
            
        print("Reading throws...")
        for i in range(self.throws_size):
            throw = Throw(self.throws_ptr + (i * self.Throw_size), self)
            throw.setUnknownIdx((throw.unknown_addr - self.throw_extras_ptr) // self.ThrowExtra_size)
            self.throws.append(throw.dict())
        
        print("Reading movelist...")
        for i in range(self.movelist_size):
            move = Move(self.movelist_head_ptr + (i * self.Move_size), self)
            move.setCancelIdx((move.cancel_addr - self.cancel_head_ptr) // self.Cancel_size)
            move.setHitConditionIdx((move.hit_condition_addr - self.hit_conditions_ptr) // self.HitCondition_size)
            if move.extra_properties_ptr != 0:
                move.setExtraPropertiesIdx((move.extra_properties_ptr - self.extra_move_properties_ptr) // self.ExtraMoveProperty_size)
            if move.voiceclip_ptr != 0:
                move.setVoiceclipId((move.voiceclip_ptr - self.voiceclip_list_ptr) // self.Voiceclip_size)
            move.setId(i)
            self.moves.append(move.dict())
            
            if move.anim not in self.anims:
                self.anims.append(move.anim)

        self.save()
        
if __name__ == "__main__":
    
    TekkenVersion = 2 if (len(sys.argv) > 1 and sys.argv[1].lower() == "tag2") else 7
    try:
        TekkenExporter = Exporter(TekkenVersion)
    except Exception as e:
        print(e)
        os._exit(0)
    
    extractedMovesetNames = []
    extractedMovesets = []
    
    if TekkenVersion == 7:
        playerAddr = game_addresses.addr["p1_addr"] 
        playerOffset = game_addresses.addr["playerstruct_size"]
    else:
        playerAddr = TekkenExporter.getCemuP1Addr()
        playerOffset = game_addresses.addr["cemu_playerstruct_size"]
    
    for i in range(2 if TekkenVersion == 7 else 4):
        try:
            player_name = TekkenExporter.getPlayerMovesetName(playerAddr)
        except Exception as e:
            print(e)
            print("%x: Invalid character or moveset." % (playerAddr))
            break
        
        if player_name in extractedMovesetNames:
            print("%x: Character %s already just extracted, not extracting twice." % (playerAddr, player_name))
            playerAddr += playerOffset
            continue
            
        moveset = TekkenExporter.exportMoveset(playerAddr)
        extractedMovesetNames.append(player_name)
        extractedMovesets.append(moveset)
        playerAddr += playerOffset
    
    if len(extractedMovesets) > 0:
        print("\nSuccessfully extracted:")
        for moveset in extractedMovesets:
            print(moveset.name, "at", moveset.extraction_path)
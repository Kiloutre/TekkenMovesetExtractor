# --- Ton-Chan's Motbin export --- #
# Python 3.6.5

from Addresses import game_addresses, GameClass
from ByteSwap import SwapAnimBytes, SwapMotaBytes
from datetime import datetime, timezone
import json
import os
import sys
import re
import string
from zlib import crc32

exportVersion = "1.0.0"       
        
def GetBigEndianAnimEnd(data, searchStart):
    return [
        data[searchStart:].find(b'\x00\x64\x00\x17\x00'),
        data[searchStart:].find(b'\x00\x64\x00\x1B\x00'),
        data[searchStart:].find(b'\x00\xC8\x00\x17\x00'),
        data[searchStart:].find(b'motOrigin'),
        data[searchStart:].find(bytes([0] * 100))
    ]
    
def GetLittleEndianAnimEnd(data, searchStart):
    return [
        data[searchStart:].find(b'\x64\x00\x17\x00'),
        data[searchStart:].find(b'\x64\x00\x1B\x00'),
        data[searchStart:].find(b'\xC8\x00\x17\x00'),
        data[searchStart:].find(b'motOrigin'),
        data[searchStart:].find(bytes([0] * 100))
    ]

ptrSizes = {
    't7': 8,
    'tag2': 4,
    'rpcs3_tag2': 4,
    'rev': 4,
    't6': 4,
    '3d': 4,
    't5': 4,
    't5dr': 4,
    't4': 4,
}

endians = {
    't7': 'little',
    'tag2': 'big',
    'rpcs3_tag2': 'big',
    'rev': 'big',
    't6': 'big',
    't5': 'little',
    't5dr': 'big',
    '3d': 'little',
    't4': 'little',
}

swapGameAnimBytes = {
    't7': False,
    'tag2': True,
    'rpcs3_tag2': True,
    'rev': True,
    't6': True,
    't5': False,
    't5dr': True,
    't4': False,
    '3d': False
}

charaIdSize = {
    't5': 2
}

animEndPosFunc = {
    't7': GetBigEndianAnimEnd,
    'tag2': GetLittleEndianAnimEnd,
    'rpcs3_tag2': GetLittleEndianAnimEnd,
    'rev': GetLittleEndianAnimEnd,
    't6': GetLittleEndianAnimEnd,
    't5dr': GetBigEndianAnimEnd,
    't5': GetLittleEndianAnimEnd,
    't4': GetBigEndianAnimEnd,
    '3d': GetBigEndianAnimEnd,
}

versionLabels = {
    't7': 'Tekken7',
    'tag2': 'Tag2',
    'rpcs3_tag2': 'Tag2',
    'rev': 'Revolution',
    't6': 'Tekken6',
    't5': 'Tekken5',
    't5dr': 'Tekken5DR',
    't4': 'Tekken4',
    '3d': 'Tekken3D',
}

tag2StructSizes = {
    'Pushback_size': 0xC,
    'PushbackExtradata_size': 0x2,
    'Requirement_size': 0x8,
    'CancelExtradata_size': 0x4,
    'Cancel_size': 0x20,
    'ReactionList_size': 0x50,
    'HitCondition_size': 0xC,
    'ExtraMoveProperty_size': 0xC,
    'Move_size': 0x70,
    'Voiceclip_size': 0x4,
    'InputExtradata_size': 0x8,
    'InputSequence_size': 0x8,
    'Projectile_size': 0x88,
    'ThrowExtra_size': 0xC,
    'Throw_size': 0x8,
    'UnknownParryRelated_size': 0x4
}

t6StructSizes = {
    'Pushback_size': 0xC,
    'PushbackExtradata_size': 0x2,
    'Requirement_size': 0x8,
    'CancelExtradata_size': 0x4,
    'Cancel_size': 0x20,
    'ReactionList_size': 0x50,
    'HitCondition_size': 0xC,
    'ExtraMoveProperty_size': 0xC,
    'Move_size': 0x58,
    'Voiceclip_size': 0x4,
    'InputExtradata_size': 0x8,
    'InputSequence_size': 0x8,
    'Projectile_size': 0x88,
    'ThrowExtra_size': 0xC,
    'Throw_size': 0x8,
    'UnknownParryRelated_size': 0x4
}

t5StructSizes = {
    'Pushback_size': 0xC,
    'PushbackExtradata_size': 0x2,
    'Requirement_size': 0x4,
    'CancelExtradata_size': 0x4,
    'Cancel_size': 0x18,
    'ReactionList_size': 0x50,
    'HitCondition_size': 0xC,
    'ExtraMoveProperty_size': 0x8,
    'Move_size': 0x4c,
    'Voiceclip_size': 0x2,
    'InputExtradata_size': 0x4,
    'InputSequence_size': 0x8,
    'Projectile_size': 0x88,
    'ThrowExtra_size': 0xC,
    'Throw_size': 0x8,
    'UnknownParryRelated_size': 0x4
}

structSizes = {
    't7': {
        'Pushback_size': 0x10,
        'PushbackExtradata_size': 0x2,
        'Requirement_size': 0x8,
        'CancelExtradata_size': 0x4,
        'Cancel_size': 0x28,
        'ReactionList_size': 0x70,
        'HitCondition_size': 0x18,
        'ExtraMoveProperty_size': 0xC,
        'Move_size': 0xB0,
        'Voiceclip_size': 0x4,
        'InputExtradata_size': 0x8,
        'InputSequence_size': 0x10,
        'Projectile_size': 0xa8,
        'ThrowExtra_size': 0xC,
        'Throw_size': 0x10,
        'UnknownParryRelated_size': 0x4
    },
    'tag2': tag2StructSizes,
    'rpcs3_tag2': tag2StructSizes,
    'rev': tag2StructSizes,
    't6': t6StructSizes,
    '3d': t6StructSizes,
    't5': t5StructSizes,
    't5dr': t5StructSizes,
    't4': {
        'Pushback_size': 0xC,
        'PushbackExtradata_size': 0x2,
        'Requirement_size': 0x4,
        'CancelExtradata_size': 0x4,
        'Cancel_size': 0x14,
        'ReactionList_size': 0x50,
        'HitCondition_size': 0xC,
        'ExtraMoveProperty_size': 0x8,
        'Move_size': 0x34,
        'Voiceclip_size': 0x4,
        'InputExtradata_size': 0x4,
        'InputSequence_size': 0x8,
        'Projectile_size': 0x88,
        'ThrowExtra_size': 0xC,
        'Throw_size': 0x8,
        'UnknownParryRelated_size': 0x4
    },
}

t7_offsetTable = {
    'character_name': { 'offset': 0x8, 'size': 'stringPtr'},
    'creator_name': { 'offset': 0x10, 'size': 'stringPtr' },
    'date': { 'offset': 0x18, 'size': 'stringPtr' },
    'fulldate': { 'offset': 0x20, 'size': 'stringPtr' },
    
    'reaction_list_ptr': { 'offset': 0x150, 'size': 8 },
    'reaction_list_size': { 'offset': 0x158, 'size': 8 },
    'requirements_ptr': { 'offset': 0x160, 'size': 8 },
    'requirement_count': { 'offset': 0x168, 'size': 8 },
    'hit_conditions_ptr': { 'offset': 0x170, 'size': 8 },
    'hit_conditions_size': { 'offset': 0x178, 'size': 8 },
    'projectile_ptr': { 'offset': 0x180, 'size': 8 },
    'projectile_size': { 'offset': 0x188, 'size': 8 },
    'pushback_ptr': { 'offset': 0x190, 'size': 8 },
    'pushback_list_size': { 'offset': 0x198, 'size': 8 },
    'pushback_extradata_ptr': { 'offset': 0x1a0, 'size': 8 },
    'pushback_extradata_size': { 'offset': 0x1a8, 'size': 8 },
    'cancel_head_ptr': { 'offset': 0x1b0, 'size': 8 },
    'cancel_list_size': { 'offset': 0x1b8, 'size': 8 },
    'group_cancel_head_ptr': { 'offset': 0x1c0, 'size': 8 },
    'group_cancel_list_size': { 'offset': 0x1c8, 'size': 8 },
    'cancel_extradata_head_ptr': { 'offset': 0x1d0, 'size': 8 },
    'cancel_extradata_list_size': { 'offset': 0x1d8, 'size': 8 },
    'extra_move_properties_ptr': { 'offset': 0x1e0, 'size': 8 },
    'extra_move_properties_size': { 'offset': 0x1e8, 'size': 8 },
    'movelist_head_ptr': { 'offset': 0x210, 'size': 8 },
    'movelist_size': { 'offset': 0x218, 'size': 8 },
    'voiceclip_list_ptr': { 'offset': 0x220, 'size': 8 },
    'voiceclip_list_size': { 'offset': 0x228, 'size': 8 },
    'input_sequence_ptr': { 'offset': 0x230, 'size': 8 },
    'input_sequence_size': { 'offset': 0x238, 'size': 8 },
    'input_extradata_ptr': { 'offset': 0x240, 'size': 8 },
    'input_extradata_size': { 'offset': 0x248, 'size': 8 },
    'unknown_parryrelated_list_ptr': { 'offset': 0x250, 'size': 8 },
    'unknown_parryrelated_list_size': { 'offset': 0x258, 'size': 8 },
    'throw_extras_ptr': { 'offset': 0x260, 'size': 8 },
    'throw_extras_size': { 'offset': 0x268, 'size': 8 },
    'throws_ptr': { 'offset': 0x270, 'size': 8 },
    'throws_size': { 'offset': 0x278, 'size': 8 },
    
    'mota_start': { 'offset': 0x280, 'size': None },
    'aliases': { 'offset': 0x28, 'size': (148, 2) }, # 112 aliases + 36 ??? of 2 bytes
    'aliases2': { 'offset': 0x108, 'size': (36, 2) }, # 112 aliases + 36 ??? of 2 bytes
    
    'pushback:val1': { 'offset': 0x0, 'size': 2 },
    'pushback:val2': { 'offset': 0x2, 'size': 2 },
    'pushback:val3': { 'offset': 0x4, 'size': 2 },
    'pushback:extra_addr': { 'offset': 0x8, 'size': 8 },
    
    'pushbackextradata:value': { 'offset': 0x0, 'size': 2 },
    
    'requirement:req': { 'offset': 0x0, 'size': 4 },
    'requirement:param': { 'offset': 0x4, 'size': 4 },
    
    'cancelextradata:value': { 'offset': 0x0, 'size': 4 },
    
    'cancel:command': { 'offset': 0x0, 'size': 8 },
    'cancel:requirement_addr': { 'offset': 0x8, 'size': 8 },
    'cancel:extradata_addr': { 'offset': 0x10, 'size': 8 },
    'cancel:frame_window_start': { 'offset': 0x18, 'size': 4 },
    'cancel:frame_window_end': { 'offset': 0x1c, 'size': 4 },
    'cancel:starting_frame': { 'offset': 0x20, 'size': 4 },
    'cancel:move_id': { 'offset': 0x24, 'size': 2 },
    'cancel:cancel_option': { 'offset': 0x26, 'size': 2 },
    
    'reactionlist:ptr_list': { 'offset': 0x0, 'size': (7, 8) }, #array of 7 variables, each 8 bytes long
    'reactionlist:u1list': { 'offset': 0x38, 'size': (6, 2) },  #array of 6 variables, each 2 bytes long
    'reactionlist:vertical_pushback': { 'offset': 0x4C, 'size': 2 },
    'reactionlist:standing': { 'offset': 0x50, 'size': 2 },
    'reactionlist:crouch': { 'offset': 0x52, 'size': 2 },
    'reactionlist:ch': { 'offset': 0x54, 'size': 2 },
    'reactionlist:crouch_ch': { 'offset': 0x56, 'size': 2 },
    'reactionlist:left_side': { 'offset': 0x58, 'size': 2 },
    'reactionlist:left_side_crouch': { 'offset': 0x5a, 'size': 2 },
    'reactionlist:right_side': { 'offset': 0x5c, 'size': 2 },
    'reactionlist:right_side_crouch': { 'offset': 0x5e, 'size': 2 },
    'reactionlist:back': { 'offset': 0x60, 'size': 2 },
    'reactionlist:back_crouch': { 'offset': 0x62, 'size': 2 },
    'reactionlist:block': { 'offset': 0x64, 'size': 2 },
    'reactionlist:crouch_block': { 'offset': 0x66, 'size': 2 },
    'reactionlist:wallslump': { 'offset': 0x68, 'size': 2 },
    'reactionlist:downed': { 'offset': 0x6a, 'size': 2 },
    
    'hitcondition:requirement_addr': { 'offset': 0x0, 'size': 8 },
    'hitcondition:damage': { 'offset': 0x8, 'size': 4 },
    'hitcondition:reaction_list_addr': { 'offset': 0x10, 'size': 8 },
    
    'extramoveprop:type': { 'offset': 0x0, 'size': 4 },
    'extramoveprop:id': { 'offset': 0x4, 'size': 4 },
    'extramoveprop:value': { 'offset': 0x8, 'size': 4 },    
    
    'move:name': { 'offset': 0x0, 'size': 'stringPtr' },
    'move:anim_name': { 'offset': 0x8, 'size': 'stringPtr' },
    'move:anim_addr': { 'offset': 0x10, 'size': 8 },
    'move:vuln': { 'offset': 0x18, 'size': 4 },
    'move:hitlevel': { 'offset': 0x1c, 'size': 4 },
    'move:cancel_addr': { 'offset': 0x20, 'size': 8 },
    'move:transition': { 'offset': 0x54, 'size': 2 },
    'move:anim_max_len': { 'offset': 0x68, 'size': 4 },
    'move:startup': { 'offset': 0xa0, 'size': 4 },
    'move:recovery': { 'offset': 0xa4, 'size': 4 },
    'move:hitbox_location': { 'offset': 0x9c, 'size': 4 },
    'move:hit_condition_addr': { 'offset': 0x60, 'size': 8 },
    'move:extra_properties_ptr': { 'offset': 0x80, 'size': 8 },
    'move:voiceclip_ptr': { 'offset': 0x78, 'size': 8 },
    #'move:u1': { 'offset': 0x10, 'size': 8 },
    'move:u2': { 'offset': 0x30, 'size': 8 },
    'move:u3': { 'offset': 0x38, 'size': 8 },
    'move:u4': { 'offset': 0x40, 'size': 8 },
    #'move:u5': { 'offset': 0x10, 'size': 8 },
    'move:u6': { 'offset': 0x50, 'size': 4 },
    'move:u7': { 'offset': 0x56, 'size': 2 },
    'move:u8': { 'offset': 0x58, 'size': 2 },
    'move:u8_2': { 'offset': 0x5a, 'size': 2 },
    'move:u9': { 'offset': 0x5c, 'size': 2 },
    'move:u10': { 'offset': 0x6c, 'size': 4 },
    'move:u11': { 'offset': 0x70, 'size': 4 },
    'move:u12': { 'offset': 0x74, 'size': 4 },
    #'move:u13': { 'offset': 0x10, 'size': 8 },
    #'move:u14': { 'offset': 0x10, 'size': 8 },
    'move:u15': { 'offset': 0x98, 'size': 4 },
    'move:u16': { 'offset': 0xa8, 'size': 2 },
    'move:u17': { 'offset': 0xaa, 'size': 2 },
    'move:u18': { 'offset': 0xac, 'size': 4 },
    
    'voiceclip:value': { 'offset': 0x0, 'size': 4 },
    
    'inputextradata:u1': { 'offset': 0x0, 'size': 4 },
    'inputextradata:u2': { 'offset': 0x4, 'size': 4 },
    
    'inputsequence:u1': { 'offset': 0x0, 'size': 2 },
    'inputsequence:u2': { 'offset': 0x2, 'size': 2 },
    'inputsequence:u3': { 'offset': 0x4, 'size': 4 },
    'inputsequence:extradata_addr': { 'offset': 0x8, 'size': 8 },
    
    
    'throw:u1': { 'offset': 0x0, 'size': 8 },
    'throw:throwextra_addr': { 'offset': 0x8, 'size': 8 },
    
    'unknownparryrelated:value': { 'offset': 0x0, 'size': 4 },
    
    'projectile:u1': { 'offset': 0x0, 'size': (48, 2) },
    'projectile:hit_condition_addr': { 'offset': 0x60, 'size': 8 },
    'projectile:cancel_addr': { 'offset': 0x68, 'size': 8 },
    'projectile:u2': { 'offset': 0x70, 'size': (28, 2) },
    
    'throwextra:u1': { 'offset': 0x0, 'size': 4 },
    'throwextra:u2': { 'offset': 4, 'size': (4, 2) },
}

tag2_offsetTable = {
    'character_name': { 'offset': 0x8, 'size': 'stringPtr'},
    'creator_name': { 'offset': 0xc, 'size': 'stringPtr' },
    'date': { 'offset': 0x10, 'size': 'stringPtr' },
    'fulldate': { 'offset': 0x14, 'size': 'stringPtr' },
    
    'reaction_list_ptr': { 'offset': 0x140, 'size': 4 },
    'reaction_list_size': { 'offset': 0x144, 'size': 4 },
    'requirements_ptr': { 'offset': 0x148, 'size': 4 },
    'requirement_count': { 'offset': 0x14c, 'size': 4 },
    'hit_conditions_ptr': { 'offset': 0x150, 'size': 4 },
    'hit_conditions_size': { 'offset': 0x154, 'size': 4 },
    'projectile_ptr': { 'offset': 0x158, 'size': 4 },
    'projectile_size': { 'offset': 0x15c, 'size': 4 },
    'pushback_ptr': { 'offset': 0x160, 'size': 4 },
    'pushback_list_size': { 'offset': 0x164, 'size': 4 },
    'pushback_extradata_ptr': { 'offset': 0x168, 'size': 4 },
    'pushback_extradata_size': { 'offset': 0x16c, 'size': 4 },
    'cancel_head_ptr': { 'offset': 0x170, 'size': 4 },
    'cancel_list_size': { 'offset': 0x174, 'size': 4 },
    'group_cancel_head_ptr': { 'offset': 0x178, 'size': 4 },
    'group_cancel_list_size': { 'offset': 0x17c, 'size': 4 },
    'cancel_extradata_head_ptr': { 'offset': 0x180, 'size': 4 },
    'cancel_extradata_list_size': { 'offset': 0x184, 'size': 4 },
    'extra_move_properties_ptr': { 'offset': 0x188, 'size': 4 },
    'extra_move_properties_size': { 'offset': 0x18c, 'size': 4 },
    'movelist_head_ptr': { 'offset': 0x1a0, 'size': 4 },
    'movelist_size': { 'offset': 0x1a4, 'size': 4 },
    'voiceclip_list_ptr': { 'offset': 0x1a8, 'size': 4 },
    'voiceclip_list_size': { 'offset': 0x1ac, 'size': 4 },
    'input_sequence_ptr': { 'offset': 0x1b0, 'size': 4 },
    'input_sequence_size': { 'offset': 0x1b4, 'size': 4 },
    'input_extradata_ptr': { 'offset': 0x1b8, 'size': 4 },
    'input_extradata_size': { 'offset': 0x1bc, 'size': 4 },
    'unknown_parryrelated_list_ptr': { 'offset': 0x1c0, 'size': 4 },
    'unknown_parryrelated_list_size': { 'offset': 0x1c4, 'size': 4 },
    'throw_extras_ptr': { 'offset': 0x1c8, 'size': 4 },
    'throw_extras_size': { 'offset': 0x1cc, 'size': 4 },
    'throws_ptr': { 'offset': 0x1d0, 'size': 4 },
    'throws_size': { 'offset': 0x1d4, 'size': 4 },
    
    'mota_start': { 'offset': 0x1d8, 'size': None },
    'aliases': { 'offset': 0x18, 'size': (148, 2) }, # 112 aliases + 36 ??? of 2 bytes
    'aliases2': { 'offset': 0xF8, 'size': (36, 2) }, # 36 ??? of 2 bytes
    
    'pushback:val1': { 'offset': 0x0, 'size': 2 },
    'pushback:val2': { 'offset': 0x2, 'size': 2 },
    'pushback:val3': { 'offset': 0x4, 'size': 4 },
    'pushback:extra_addr': { 'offset': 0x8, 'size': 4 },
    
    'pushbackextradata:value': { 'offset': 0x0, 'size': 2 },
    
    'requirement:req': { 'offset': 0x0, 'size': 4 },
    'requirement:param': { 'offset': 0x4, 'size': 4 },
    
    'cancelextradata:value': { 'offset': 0x0, 'size': 4 },
    
    'cancel:command': { 'offset': 0x0, 'size': 8 },
    'cancel:requirement_addr': { 'offset': 0x8, 'size': 4 },
    'cancel:extradata_addr': { 'offset': 0xc, 'size': 4 },
    'cancel:frame_window_start': { 'offset': 0x10, 'size': 4 },
    'cancel:frame_window_end': { 'offset': 0x14, 'size': 4 },
    'cancel:starting_frame': { 'offset': 0x18, 'size': 4 },
    'cancel:move_id': { 'offset': 0x1c, 'size': 2 },
    'cancel:cancel_option': { 'offset': 0x1e, 'size': 2 },
    
    'reactionlist:ptr_list': { 'offset': 0x0, 'size': (7, 4) }, #array of 7 variables, each 8 bytes long
    'reactionlist:u1list': { 'offset': 0x1c, 'size': (6, 2) },  #array of 6 variables, each 2 bytes long
    'reactionlist:vertical_pushback': { 'offset': 0x30, 'size': 2 },
    'reactionlist:standing': { 'offset': 0x34, 'size': 2 },
    'reactionlist:crouch': { 'offset': 0x36, 'size': 2 },
    'reactionlist:ch': { 'offset': 0x38, 'size': 2 },
    'reactionlist:crouch_ch': { 'offset': 0x3a, 'size': 2 },
    'reactionlist:left_side': { 'offset': 0x3c, 'size': 2 },
    'reactionlist:left_side_crouch': { 'offset': 0x3e, 'size': 2 },
    'reactionlist:right_side': { 'offset': 0x40, 'size': 2 },
    'reactionlist:right_side_crouch': { 'offset': 0x42, 'size': 2 },
    'reactionlist:back': { 'offset': 0x44, 'size': 2 },
    'reactionlist:back_crouch': { 'offset': 0x46, 'size': 2 },
    'reactionlist:block': { 'offset': 0x48, 'size': 2 },
    'reactionlist:crouch_block': { 'offset': 0x4a, 'size': 2 },
    'reactionlist:wallslump': { 'offset': 0x4c, 'size': 2 },
    'reactionlist:downed': { 'offset': 0x4e, 'size': 2 },
    
    'hitcondition:requirement_addr': { 'offset': 0x0, 'size': 4 },
    'hitcondition:damage': { 'offset': 0x4, 'size': 4 },
    'hitcondition:reaction_list_addr': { 'offset': 0x8, 'size': 4 },
    
    'extramoveprop:type': { 'offset': 0x0, 'size': 4 },
    'extramoveprop:id': { 'offset': 0x4, 'size': 4 },
    'extramoveprop:value': { 'offset': 0x8, 'size': 4 },    
    
    'move:name': { 'offset': 0x0, 'size': 'stringPtr' },
    'move:anim_name': { 'offset': 0x4, 'size': 'stringPtr' },
    'move:anim_addr': { 'offset': 0x8, 'size': 4 },
    'move:vuln': { 'offset': 0xc, 'size': 4 },
    'move:hitlevel': { 'offset': 0x10, 'size': 4 },
    'move:cancel_addr': { 'offset': 0x14, 'size': 4 },
    'move:transition': { 'offset': 0x30, 'size': 2 },
    'move:anim_max_len': { 'offset': 0x3c, 'size': 4 },
    'move:startup': { 'offset': 0x64, 'size': 4 },
    'move:recovery': { 'offset': 0x68, 'size': 4 },
    'move:hitbox_location': { 'offset': 0x60, 'size': 4, 'endian': 'little' },
    'move:hit_condition_addr': { 'offset': 0x38, 'size': 4 },
    'move:extra_properties_ptr': { 'offset': 0x50, 'size': 4 },
    'move:voiceclip_ptr': { 'offset': 0x4c, 'size': 4 },
    #'move:u1': { 'offset': 0x18, 'size': 4 },
    'move:u2': { 'offset': 0x1c, 'size': 4 },
    'move:u3': { 'offset': 0x20, 'size': 4 },
    'move:u4': { 'offset': 0x24, 'size': 4 },
    #'move:u5': { 'offset': 0x28, 'size': 4 },
    'move:u6': { 'offset': 0x2c, 'size': 4 },
    'move:u7': { 'offset': 0x32, 'size': 2 },
    'move:u8': { 'offset': 0x36, 'size': 2 },
    'move:u8_2': { 'offset': 0x34, 'size': 2 },
    'move:u9': { 'offset': None, 'size': 2 },
    'move:u10': { 'offset': 0x40, 'size': 4 },
    'move:u11': { 'offset': 0x44, 'size': 4 },
    'move:u12': { 'offset': 0x48, 'size': 4 },
    #'move:u13': { 'offset': 0x54 'size': 4 },
    #'move:u14': { 'offset': 0x58, 'size': 4 },
    'move:u15': { 'offset': 0x5c, 'size': 4 },
    'move:u16': { 'offset': 0x6c, 'size': 2 },
    'move:u17': { 'offset': 0x6e, 'size': 2 },
    'move:u18': { 'offset': None, 'size': 4 },
    
    'voiceclip:value': { 'offset': 0x0, 'size': 4 },
    
    'inputextradata:u1': { 'offset': 0x0, 'size': 4 },
    'inputextradata:u2': { 'offset': 0x4, 'size': 4 },
    
    'inputsequence:u1': { 'offset': 0x1, 'size': 1 },
    'inputsequence:u2': { 'offset': 0x2, 'size': 2 },
    'inputsequence:u3': { 'offset': 0x0, 'size': 1 },
    'inputsequence:extradata_addr': { 'offset': 4, 'size': 4 },
    
    'throw:u1': { 'offset': 0x0, 'size': 4 },
    'throw:throwextra_addr': { 'offset': 0x4, 'size': 4 },
    
    'unknownparryrelated:value': { 'offset': 0x0, 'size': 4 },
    
    'projectile:u1': { 'offset': 0x0, 'size': (48, None) }, # 48 * [0]
    'projectile:hit_condition_addr': { 'offset': None, 'size': 4 }, #0
    'projectile:cancel_addr': { 'offset': None, 'size': 4 }, #0
    'projectile:u2': { 'offset': 0x70, 'size': (28, None) }, # 28 * [0]
    
    'throwextra:u1': { 'offset': 0x0, 'size': 4 },
    'throwextra:u2': { 'offset': 4, 'size': (4, 2) },
}

t6_offsetTable = {
    'character_name': { 'offset': 0x8, 'size': 'stringPtr'},
    'creator_name': { 'offset': 0xc, 'size': 'stringPtr' },
    'date': { 'offset': 0x10, 'size': 'stringPtr' },
    'fulldate': { 'offset': 0x14, 'size': 'stringPtr' },
    
    'reaction_list_ptr': { 'offset': 0x174, 'size': 4 },
    'reaction_list_size': { 'offset': 0x178, 'size': 4 },
    'requirements_ptr': { 'offset': 0x17c, 'size': 4 },
    'requirement_count': { 'offset': 0x180, 'size': 4 },
    'hit_conditions_ptr': { 'offset': 0x184, 'size': 4 },
    'hit_conditions_size': { 'offset': 0x188, 'size': 4 },
    'projectile_ptr': { 'offset': None, 'size': 4 }, #unknown
    'projectile_size': { 'offset': None, 'size': 4 }, #unknown
    'pushback_ptr': { 'offset': 0x18c, 'size': 4 },
    'pushback_list_size': { 'offset': 0x190, 'size': 4 },
    'pushback_extradata_ptr': { 'offset': 0x194, 'size': 4 },
    'pushback_extradata_size': { 'offset': 0x198, 'size': 4 },
    'cancel_head_ptr': { 'offset': 0x19c, 'size': 4 },
    'cancel_list_size': { 'offset': 0x1a0, 'size': 4 },
    'group_cancel_head_ptr': { 'offset': 0x1a4, 'size': 4 },
    'group_cancel_list_size': { 'offset': 0x1a8, 'size': 4 },
    'cancel_extradata_head_ptr': { 'offset': 0x1ac, 'size': 4 }, 
    'cancel_extradata_list_size': { 'offset': 0x1b0, 'size': 4 }, 
    'extra_move_properties_ptr': { 'offset': 0x1b4, 'size': 4 },
    'extra_move_properties_size': { 'offset': 0x1b8, 'size': 4 },
    'movelist_head_ptr': { 'offset': 0x1cc, 'size': 4 },
    'movelist_size': { 'offset': 0x1d0, 'size': 4 },
    'voiceclip_list_ptr': { 'offset': 0x1d4, 'size': 4 },
    'voiceclip_list_size': { 'offset': 0x1d8, 'size': 4 },
    'input_sequence_ptr': { 'offset': None, 'size': 4 }, #unknown
    'input_sequence_size': { 'offset': None, 'size': 4 }, #unknown
    'input_extradata_ptr': { 'offset': None, 'size': 4 }, #unknown
    'input_extradata_size': { 'offset': None, 'size': 4 }, #unknown
    'unknown_parryrelated_list_ptr': { 'offset': None, 'size': 4 }, #unknown
    'unknown_parryrelated_list_size': { 'offset': None, 'size': 4 }, #unknown
    'throw_extras_ptr': { 'offset': 0x22c, 'size': 4 },
    'throw_extras_size': { 'offset': 0x230, 'size': 4 },
    'throws_ptr': { 'offset': None, 'size': 4 }, #unknown, prob 0x224
    'throws_size': { 'offset': None, 'size': 4 }, #unknown, prob 0x228
    
    'mota_start': { 'offset': 0x234, 'size': None },
    'aliases': { 'offset': 0x18, 'size': (148, 2) }, #148 aliases of 2 bytes
    'aliases2': { 'offset': 0xF8, 'size': (36, 2) }, # 36 ??? of 2 bytes
    
    'pushback:val1': { 'offset': 0x0, 'size': 2 },
    'pushback:val2': { 'offset': 0x2, 'size': 2 },
    'pushback:val3': { 'offset': 0x4, 'size': 4 },
    'pushback:extra_addr': { 'offset': 0x8, 'size': 4 },
    
    'pushbackextradata:value': { 'offset': 0x0, 'size': 2 },
    
    'requirement:req': { 'offset': 0x0, 'size': 4 },
    'requirement:param': { 'offset': 0x4, 'size': 4 },
    
    'cancelextradata:value': { 'offset': 0x0, 'size': 4 },
    
    'cancel:command': { 'offset': 0x0, 'size': 8 },
    'cancel:requirement_addr': { 'offset': 0x8, 'size': 4 },
    'cancel:extradata_addr': { 'offset': 0xc, 'size': 4 },
    'cancel:frame_window_start': { 'offset': 0x10, 'size': 4 },
    'cancel:frame_window_end': { 'offset': 0x14, 'size': 4 },
    'cancel:starting_frame': { 'offset': 0x18, 'size': 4 },
    'cancel:move_id': { 'offset': 0x1c, 'size': 2 },
    'cancel:cancel_option': { 'offset': 0x1e, 'size': 2 },
    
    'reactionlist:ptr_list': { 'offset': 0x0, 'size': (7, 4) }, #array of 7 variables, each 8 bytes long
    'reactionlist:u1list': { 'offset': 0x1c, 'size': (6, 2) },  #array of 6 variables, each 2 bytes long
    'reactionlist:vertical_pushback': { 'offset': 0x30, 'size': 2 },
    'reactionlist:standing': { 'offset': 0x34, 'size': 2 },
    'reactionlist:crouch': { 'offset': 0x36, 'size': 2 },
    'reactionlist:ch': { 'offset': 0x38, 'size': 2 },
    'reactionlist:crouch_ch': { 'offset': 0x3a, 'size': 2 },
    'reactionlist:left_side': { 'offset': 0x3c, 'size': 2 },
    'reactionlist:left_side_crouch': { 'offset': 0x3e, 'size': 2 },
    'reactionlist:right_side': { 'offset': 0x40, 'size': 2 },
    'reactionlist:right_side_crouch': { 'offset': 0x42, 'size': 2 },
    'reactionlist:back': { 'offset': 0x44, 'size': 2 },
    'reactionlist:back_crouch': { 'offset': 0x46, 'size': 2 },
    'reactionlist:block': { 'offset': 0x48, 'size': 2 },
    'reactionlist:crouch_block': { 'offset': 0x4a, 'size': 2 },
    'reactionlist:wallslump': { 'offset': 0x4c, 'size': 2 },
    'reactionlist:downed': { 'offset': 0x4e, 'size': 2 },
    
    'hitcondition:requirement_addr': { 'offset': 0x0, 'size': 4 },
    'hitcondition:damage': { 'offset': 0x4, 'size': 4 },
    'hitcondition:reaction_list_addr': { 'offset': 0x8, 'size': 4 },
    
    'extramoveprop:type': { 'offset': 0x0, 'size': 4 },
    'extramoveprop:id': { 'offset': 0x4, 'size': 4 },
    'extramoveprop:value': { 'offset': 0x8, 'size': 4 },    
    
    'move:name': { 'offset': None, 'size': 'stringPtr' }, #unknown
    'move:anim_name': { 'offset': None, 'size': 'stringPtr' }, #unknown
    'move:anim_addr': { 'offset': 0x8, 'size': 4 },
    'move:vuln': { 'offset': 0xc, 'size': 4 },
    'move:hitlevel': { 'offset': 0x10, 'size': 4 },
    'move:cancel_addr': { 'offset': 0x14, 'size': 4 },
    'move:transition': { 'offset': 0x18, 'size': 2 },
    'move:anim_max_len': { 'offset': 0x24, 'size': 4 },
    'move:startup': { 'offset': 0x4c, 'size': 4 },
    'move:recovery': { 'offset': 0x50, 'size': 4 },
    'move:hit_condition_addr': { 'offset': 0x20, 'size': 4 },
    'move:voiceclip_ptr': { 'offset': 0x34, 'size': 4 },
    'move:extra_properties_ptr': { 'offset': 0x38, 'size': 4 },
    'move:hitbox_location': { 'offset': 0x48, 'size': 4, 'endian': 'little' },
    #'move:u1': { 'offset': 0x18, 'size': 4 },
    'move:u2': { 'offset': None, 'size': 4 },
    'move:u3': { 'offset': None, 'size': 4 },
    'move:u4': { 'offset': None, 'size': 4 },
    #'move:u5': { 'offset': 0x28, 'size': 4 },
    'move:u6': { 'offset': None, 'size': 4 },
    'move:u7': { 'offset': None, 'size': 2 },
    'move:u8': { 'offset': None, 'size': 2 },
    'move:u8_2': { 'offset': None, 'size': 2 },
    'move:u9': { 'offset': None, 'size': 2 },
    'move:u10': { 'offset': 0x28, 'size': 4 },
    'move:u11': { 'offset': 0x2c, 'size': 4 },
    'move:u12': { 'offset': 0x30, 'size': 4 },
    #'move:u13': { 'offset': 0x54 'size': 4 },
    #'move:u14': { 'offset': 0x58, 'size': 4 },
    'move:u15': { 'offset': 0x44, 'size': 4 },
    'move:u16': { 'offset': 0x54, 'size': 2 },
    'move:u17': { 'offset': 0x56, 'size': 2 },
    'move:u18': { 'offset': None, 'size': 4 },
    
    'voiceclip:value': { 'offset': 0x0, 'size': 4 },
    
    'inputextradata:u1': { 'offset': 0x0, 'size': 4 },
    'inputextradata:u2': { 'offset': 0x4, 'size': 4 },
    
    'inputsequence:u1': { 'offset': 0x1, 'size': 1 },
    'inputsequence:u2': { 'offset': 0x2, 'size': 2 },
    'inputsequence:u3': { 'offset': 0x0, 'size': 1 },
    'inputsequence:extradata_addr': { 'offset': 4, 'size': 4 },
    
    'throw:u1': { 'offset': None, 'size': 4 },
    'throw:throwextra_addr': { 'offset': None, 'size': 4 },
    
    'unknownparryrelated:value': { 'offset': None, 'size': 4 },
    
    'projectile:u1': { 'offset': 0x0, 'size': (48, None) }, # 48 * [0]
    'projectile:hit_condition_addr': { 'offset': None, 'size': 4 }, #0
    'projectile:cancel_addr': { 'offset': None, 'size': 4 }, #0
    'projectile:u2': { 'offset': 0x70, 'size': (28, None) }, # 28 * [0]
    
    'throwextra:u1': { 'offset': 0x0, 'size': 4 },
    'throwextra:u2': { 'offset': 4, 'size': (4, 2) },
}

t5_offsetTable = {
    'character_name': { 'offset': 0x8, 'size': 'invalidStringPtr'},
    'creator_name': { 'offset': 0xc, 'size': 'invalidStringPtr' },
    'date': { 'offset': 0x10, 'size': 'stringPtr' },
    'fulldate': { 'offset': 0x14, 'size': 'stringPtr' },
    
    'reaction_list_ptr': { 'offset': 0x180, 'size': 4 },
    'reaction_list_size': { 'offset': 0x184, 'size': 4 },
    'requirements_ptr': { 'offset': 0x188, 'size': 4 },
    'requirement_count': { 'offset': 0x18c, 'size': 4 },
    'hit_conditions_ptr': { 'offset': 0x190, 'size': 4 },
    'hit_conditions_size': { 'offset': 0x194, 'size': 4 },
    'projectile_ptr': { 'offset': None, 'size': 4 },
    'projectile_size': { 'offset': None, 'size': 4 },
    'pushback_ptr': { 'offset': 0x198, 'size': 4 },
    'pushback_list_size': { 'offset': 0x19c, 'size': 4 },
    'pushback_extradata_ptr': { 'offset': 0x1a0, 'size': 4 },
    'pushback_extradata_size': { 'offset': 0x1a4, 'size': 4 },
    'cancel_head_ptr': { 'offset': 0x1a8, 'size': 4 },
    'cancel_list_size': { 'offset': 0x1ac, 'size': 4 },
    'group_cancel_head_ptr': { 'offset': 0x1b0, 'size': 4 },
    'group_cancel_list_size': { 'offset': 0x1b4, 'size': 4 },
    'cancel_extradata_head_ptr': { 'offset': 0x1b8, 'size': 4 },
    'cancel_extradata_list_size': { 'offset': 0x1bc, 'size': 4 },
    'extra_move_properties_ptr': { 'offset': 0x1c0, 'size': 4 },
    'extra_move_properties_size': { 'offset': 0x1c4, 'size': 4 },
    'movelist_head_ptr': { 'offset': 0x1d8, 'size': 4 },
    'movelist_size': { 'offset': 0x1dc, 'size': 4 },
    'voiceclip_list_ptr': { 'offset': 0x1e0, 'size': 4 },
    'voiceclip_list_size': { 'offset': 0x1e4, 'size': 4 },
    'input_sequence_ptr': { 'offset': 0x1e8, 'size': 4 },
    'input_sequence_size': { 'offset': 0x1ec, 'size': 4 },
    'input_extradata_ptr': { 'offset': 0x1f0, 'size': 4 },
    'input_extradata_size': { 'offset': 0x1f4, 'size': 4 },
    'unknown_parryrelated_list_ptr': { 'offset': None, 'size': 4 },
    'unknown_parryrelated_list_size': { 'offset': None, 'size': 4 },
    'throw_extras_ptr': { 'offset': None, 'size': 4 },
    'throw_extras_size': { 'offset': None, 'size': 4 },
    'throws_ptr': { 'offset': None, 'size': 4 },
    'throws_size': { 'offset': None, 'size': 4 },
    
    'mota_start': { 'offset': 0x230, 'size': None },
    'aliases': { 'offset': 0x18, 'size': (36, 4) },
    'aliases2': { 'offset': 0x13e, 'size': (33, 2) },
    
    'pushback:val1': { 'offset': 0x0, 'size': 2 },
    'pushback:val2': { 'offset': 0x2, 'size': 2 },
    'pushback:val3': { 'offset': 0x4, 'size': 2 },
    'pushback:extra_addr': { 'offset': 0x8, 'size': 4 },
    
    'pushbackextradata:value': { 'offset': 0x0, 'size': 2 },
    
    'requirement:req': { 'offset': 0x0, 'size': 2 },
    'requirement:param': { 'offset': 0x2, 'size': 2 },
    
    'cancelextradata:value': { 'offset': 0x0, 'size': 4 },
    
    'cancel:command': { 'offset': 0x0, 'size': 4 },
    'cancel:requirement_addr': { 'offset': 0x4, 'size': 4 },
    'cancel:extradata_addr': { 'offset': 0xc, 'size': 4 },
    'cancel:frame_window_start': { 'offset': 0x10, 'size': 2 },
    'cancel:frame_window_end': { 'offset': 0x12, 'size': 2 },
    'cancel:starting_frame': { 'offset': 0x14, 'size': 2 },
    'cancel:move_id': { 'offset': 0x8, 'size': 2 },
    'cancel:cancel_option': { 'offset': 0x16, 'size': 2 },
    
    'reactionlist:ptr_list': { 'offset': 0x0, 'size': (7, 4) }, #array of 7 variables, each 8 bytes long
    'reactionlist:u1list': { 'offset': 0x1c, 'size': (6, 2) },  #array of 6 variables, each 2 bytes long
    'reactionlist:vertical_pushback': { 'offset': 0x30, 'size': 2 },
    'reactionlist:standing': { 'offset': 0x34, 'size': 2 },
    'reactionlist:crouch': { 'offset': 0x36, 'size': 2 },
    'reactionlist:ch': { 'offset': 0x38, 'size': 2 },
    'reactionlist:crouch_ch': { 'offset': 0x3a, 'size': 2 },
    'reactionlist:left_side': { 'offset': 0x3c, 'size': 2 },
    'reactionlist:left_side_crouch': { 'offset': 0x3e, 'size': 2 },
    'reactionlist:right_side': { 'offset': 0x40, 'size': 2 },
    'reactionlist:right_side_crouch': { 'offset': 0x42, 'size': 2 },
    'reactionlist:back': { 'offset': 0x44, 'size': 2 },
    'reactionlist:back_crouch': { 'offset': 0x46, 'size': 2 },
    'reactionlist:block': { 'offset': 0x48, 'size': 2 },
    'reactionlist:crouch_block': { 'offset': 0x4a, 'size': 2 },
    'reactionlist:wallslump': { 'offset': 0x4c, 'size': 2 },
    'reactionlist:downed': { 'offset': 0x4e, 'size': 2 },
    
    'hitcondition:requirement_addr': { 'offset': 0x0, 'size': 4 },
    'hitcondition:damage': { 'offset': 0x4, 'size': 2 },
    'hitcondition:reaction_list_addr': { 'offset': 0x8, 'size': 4 },
    
    'extramoveprop:type': { 'offset': 0x0, 'size': 2 },
    'extramoveprop:id': { 'offset': 0x2, 'size': 2 },
    'extramoveprop:value': { 'offset': 0x4, 'size': 4 },    
    
    'move:name': { 'offset': 0x0, 'size': 'stringPtr' },
    'move:anim_name': { 'offset': 0x4, 'size': 'stringPtr' },
    'move:anim_addr': { 'offset': 0x8, 'size': 4 },
    'move:vuln': { 'offset': 0xc, 'size': 4 },
    'move:hitlevel': { 'offset': 0x10, 'size': 4 },
    'move:cancel_addr': { 'offset': 0x14, 'size': 4 },
    'move:transition': { 'offset': 0x18, 'size': 2 },
    'move:anim_max_len': { 'offset': 0x24, 'size': 2 },
    'move:startup': { 'offset': 0x44, 'size': 2 },
    'move:recovery': { 'offset': 0x46, 'size': 2 },
    'move:hit_condition_addr': { 'offset': 0x20, 'size': 4 },
    'move:voiceclip_ptr': { 'offset': 0x2c, 'size': 4 },
    'move:extra_properties_ptr': { 'offset': 0x30, 'size': 4 },
    'move:hitbox_location': { 'offset': 0x40, 'size': 4, 'endian': 'little' },
    #'move:u1': { 'offset': 0x18, 'size': 4 },
    'move:u2': { 'offset': None, 'size': 4 },
    'move:u3': { 'offset': None, 'size': 4 },
    'move:u4': { 'offset': None, 'size': 4 },
    #'move:u5': { 'offset': 0x28, 'size': 4 },
    'move:u6': { 'offset': None, 'size': 4 },
    'move:u7': { 'offset': None, 'size': 2 },
    'move:u8': { 'offset': None, 'size': 2 },
    'move:u8_2': { 'offset': None, 'size': 2 },
    'move:u9': { 'offset': None, 'size': 2 },
    'move:u10': { 'offset': None, 'size': 4 },
    'move:u11': { 'offset': None, 'size': 4 },
    'move:u12': { 'offset': None, 'size': 4 },
    #'move:u13': { 'offset': 0x54 'size': 4 },
    #'move:u14': { 'offset': 0x58, 'size': 4 },
    'move:u15': { 'offset': None, 'size': 4 },
    'move:u16': { 'offset': None, 'size': 2 },
    'move:u17': { 'offset': None, 'size': 2 },
    'move:u18': { 'offset': None, 'size': 4 },
    
    'voiceclip:value': { 'offset': 0x0, 'size': 2 },
    
    'inputextradata:u1': { 'offset': 0x0, 'size': 2 },
    'inputextradata:u2': { 'offset': 0x2, 'size': 2 },
    
    'inputsequence:u1': { 'offset': 0x0, 'size': 2 },
    'inputsequence:u2': { 'offset': 0x2, 'size': 2 },
    'inputsequence:u3': { 'offset': 0x0, 'size': 1 },
    'inputsequence:extradata_addr': { 'offset': 4, 'size': 4 },
    
    'throw:u1': { 'offset': 0x0, 'size': 4 },
    'throw:throwextra_addr': { 'offset': 0x4, 'size': 4 },
    
    'unknownparryrelated:value': { 'offset': 0x0, 'size': 4 },
    
    'projectile:u1': { 'offset': 0x0, 'size': (48, None) }, # 48 * [0]
    'projectile:hit_condition_addr': { 'offset': None, 'size': 4 }, #0
    'projectile:cancel_addr': { 'offset': None, 'size': 4 }, #0
    'projectile:u2': { 'offset': 0x70, 'size': (28, None) }, # 28 * [0]
    
    'throwextra:u1': { 'offset': 0x0, 'size': 4 },
    'throwextra:u2': { 'offset': 4, 'size': (4, 2) },
}

t5dr_offsetTable = {
    'character_name': { 'offset': 0x8, 'size': 'invalidStringPtr'},
    'creator_name': { 'offset': 0xc, 'size': 'invalidStringPtr' },
    'date': { 'offset': 0x10, 'size': 'stringPtr' },
    'fulldate': { 'offset': 0x14, 'size': 'stringPtr' },
    
    'reaction_list_ptr': { 'offset': 0x188, 'size': 4 },
    'reaction_list_size': { 'offset': 0x18c, 'size': 4 },
    'requirements_ptr': { 'offset': 0x190, 'size': 4 },
    'requirement_count': { 'offset': 0x194, 'size': 4 },
    'hit_conditions_ptr': { 'offset': 0x198, 'size': 4 },
    'hit_conditions_size': { 'offset': 0x19c, 'size': 4 },
    'projectile_ptr': { 'offset': None, 'size': 4 }, #unknown
    'projectile_size': { 'offset': None, 'size': 4 }, #unknown
    'pushback_ptr': { 'offset': 0x1a0, 'size': 4 },
    'pushback_list_size': { 'offset': 0x1a4, 'size': 4 },
    'pushback_extradata_ptr': { 'offset': 0x1a8, 'size': 4 },
    'pushback_extradata_size': { 'offset': 0x1ac, 'size': 4 },
    'cancel_head_ptr': { 'offset': 0x1b0, 'size': 4 },
    'cancel_list_size': { 'offset': 0x1b4, 'size': 4 },
    'group_cancel_head_ptr': { 'offset': 0x1b8, 'size': 4 },
    'group_cancel_list_size': { 'offset': 0x1bc, 'size': 4 },
    'cancel_extradata_head_ptr': { 'offset': 0x1c0, 'size': 4 },
    'cancel_extradata_list_size': { 'offset': 0x1c4, 'size': 4 },
    'extra_move_properties_ptr': { 'offset': 0x1c8, 'size': 4 },
    'extra_move_properties_size': { 'offset': 0x1cc, 'size': 4 },
    'movelist_head_ptr': { 'offset': 0x1e0, 'size': 4 },
    'movelist_size': { 'offset': 0x1e4, 'size': 4 },
    'voiceclip_list_ptr': { 'offset': 0x1e8, 'size': 4 },
    'voiceclip_list_size': { 'offset': 0x1ec, 'size': 4 },
    'input_sequence_ptr': { 'offset': 0x1f0, 'size': 4 }, #unknown
    'input_sequence_size': { 'offset': 0x1f4, 'size': 4 }, #unknown
    'input_extradata_ptr': { 'offset': 0x1f8, 'size': 4 }, #unknown
    'input_extradata_size': { 'offset': 0x1fc, 'size': 4 }, #unknown
    'unknown_parryrelated_list_ptr': { 'offset': None, 'size': 4 }, #unknown
    'unknown_parryrelated_list_size': { 'offset': None, 'size': 4 }, #unknown
    'throw_extras_ptr': { 'offset': None, 'size': 4 }, #unknown
    'throw_extras_size': { 'offset': None, 'size': 4 }, #unknown
    'throws_ptr': { 'offset': None, 'size': 4 }, #unknown
    'throws_size': { 'offset': None, 'size': 4 }, #unknown
    
    'mota_start': { 'offset': 0x230, 'size': None },
    'aliases': { 'offset': 0x18, 'size': (36, 4) },
    'aliases2': { 'offset': 0x13e, 'size': (33, 2) },
    
    'pushback:val1': { 'offset': 0x0, 'size': 2 },
    'pushback:val2': { 'offset': 0x2, 'size': 2 },
    'pushback:val3': { 'offset': 0x4, 'size': 2 },
    'pushback:extra_addr': { 'offset': 0x8, 'size': 4 },
    
    'pushbackextradata:value': { 'offset': 0x0, 'size': 2 },
    
    'requirement:req': { 'offset': 0x0, 'size': 2 },
    'requirement:param': { 'offset': 0x2, 'size': 2 },
    
    'cancelextradata:value': { 'offset': 0x0, 'size': 4 },
    
    'cancel:command': { 'offset': 0x0, 'size': 4 },
    'cancel:requirement_addr': { 'offset': 0x4, 'size': 4 },
    'cancel:extradata_addr': { 'offset': 0xc, 'size': 4 },
    'cancel:frame_window_start': { 'offset': 0x10, 'size': 2 },
    'cancel:frame_window_end': { 'offset': 0x12, 'size': 2 },
    'cancel:starting_frame': { 'offset': 0x14, 'size': 2 },
    'cancel:move_id': { 'offset': 0x8, 'size': 2 },
    'cancel:cancel_option': { 'offset': 0x16, 'size': 2 },
    
    'reactionlist:ptr_list': { 'offset': 0x0, 'size': (7, 4) }, #array of 7 variables, each 8 bytes long
    'reactionlist:u1list': { 'offset': 0x1c, 'size': (6, 2) },  #array of 6 variables, each 2 bytes long
    'reactionlist:vertical_pushback': { 'offset': 0x30, 'size': 2 },
    'reactionlist:standing': { 'offset': 0x34, 'size': 2 },
    'reactionlist:crouch': { 'offset': 0x36, 'size': 2 },
    'reactionlist:ch': { 'offset': 0x38, 'size': 2 },
    'reactionlist:crouch_ch': { 'offset': 0x3a, 'size': 2 },
    'reactionlist:left_side': { 'offset': 0x3c, 'size': 2 },
    'reactionlist:left_side_crouch': { 'offset': 0x3e, 'size': 2 },
    'reactionlist:right_side': { 'offset': 0x40, 'size': 2 },
    'reactionlist:right_side_crouch': { 'offset': 0x42, 'size': 2 },
    'reactionlist:back': { 'offset': 0x44, 'size': 2 },
    'reactionlist:back_crouch': { 'offset': 0x46, 'size': 2 },
    'reactionlist:block': { 'offset': 0x48, 'size': 2 },
    'reactionlist:crouch_block': { 'offset': 0x4a, 'size': 2 },
    'reactionlist:wallslump': { 'offset': 0x4c, 'size': 2 },
    'reactionlist:downed': { 'offset': 0x4e, 'size': 2 },
    
    'hitcondition:requirement_addr': { 'offset': 0x0, 'size': 4 },
    'hitcondition:damage': { 'offset': 0x4, 'size': 2 },
    'hitcondition:reaction_list_addr': { 'offset': 0x8, 'size': 4 },
    
    'extramoveprop:type': { 'offset': 0x0, 'size': 2 },
    'extramoveprop:id': { 'offset': 0x2, 'size': 2 },
    'extramoveprop:value': { 'offset': 0x4, 'size': 4 },    
    
    'move:name': { 'offset': 0x0, 'size': 'stringPtr' },
    'move:anim_name': { 'offset': 0x4, 'size': 'stringPtr' },
    'move:anim_addr': { 'offset': 0x8, 'size': 4 },
    'move:vuln': { 'offset': 0xc, 'size': 4 },
    'move:hitlevel': { 'offset': 0x10, 'size': 4 },
    'move:cancel_addr': { 'offset': 0x14, 'size': 4 },
    'move:transition': { 'offset': 0x18, 'size': 2 },
    'move:anim_max_len': { 'offset': 0x24, 'size': 2 },
    'move:startup': { 'offset': 0x44, 'size': 2 },
    'move:recovery': { 'offset': 0x46, 'size': 2 },
    'move:hit_condition_addr': { 'offset': 0x20, 'size': 4 },
    'move:voiceclip_ptr': { 'offset': 0x2c, 'size': 4 },
    'move:extra_properties_ptr': { 'offset': 0x30, 'size': 4 },
    'move:hitbox_location': { 'offset': 0x40, 'size': 4, 'endian': 'little' },
    #'move:u1': { 'offset': 0x18, 'size': 4 },
    'move:u2': { 'offset': None, 'size': 4 },
    'move:u3': { 'offset': None, 'size': 4 },
    'move:u4': { 'offset': None, 'size': 4 },
    #'move:u5': { 'offset': 0x28, 'size': 4 },
    'move:u6': { 'offset': None, 'size': 4 },
    'move:u7': { 'offset': None, 'size': 2 },
    'move:u8': { 'offset': None, 'size': 2 },
    'move:u8_2': { 'offset': None, 'size': 2 },
    'move:u9': { 'offset': None, 'size': 2 },
    'move:u10': { 'offset': None, 'size': 4 },
    'move:u11': { 'offset': None, 'size': 4 },
    'move:u12': { 'offset': None, 'size': 4 },
    #'move:u13': { 'offset': 0x54 'size': 4 },
    #'move:u14': { 'offset': 0x58, 'size': 4 },
    'move:u15': { 'offset': None, 'size': 4 },
    'move:u16': { 'offset': None, 'size': 2 },
    'move:u17': { 'offset': None, 'size': 2 },
    'move:u18': { 'offset': None, 'size': 4 },
    
    'voiceclip:value': { 'offset': 0x0, 'size': 2 },
    
    'inputextradata:u1': { 'offset': 0x0, 'size': 2 },
    'inputextradata:u2': { 'offset': 0x2, 'size': 2 },
    
    'inputsequence:u1': { 'offset': 0x0, 'size': 2 },
    'inputsequence:u2': { 'offset': 0x2, 'size': 2 },
    'inputsequence:u3': { 'offset': 0x0, 'size': 1 },
    'inputsequence:extradata_addr': { 'offset': 4, 'size': 4 },
    
    'throw:u1': { 'offset': 0x0, 'size': 4 },
    'throw:throwextra_addr': { 'offset': 0x4, 'size': 4 },
    
    'unknownparryrelated:value': { 'offset': 0x0, 'size': 4 },
    
    'projectile:u1': { 'offset': 0x0, 'size': (48, None) }, # 48 * [0]
    'projectile:hit_condition_addr': { 'offset': None, 'size': 4 }, #0
    'projectile:cancel_addr': { 'offset': None, 'size': 4 }, #0
    'projectile:u2': { 'offset': 0x70, 'size': (28, None) }, # 28 * [0]
    
    'throwextra:u1': { 'offset': 0x0, 'size': 4 },
    'throwextra:u2': { 'offset': 4, 'size': (4, 2) },
}

t4_offsetTable = {
    'character_name': { 'offset': 0x4, 'size': 'invalidStringPtr'},
    'creator_name': { 'offset': 0x8, 'size': 'invalidStringPtr' },
    'date': { 'offset': 0xc, 'size': 'stringPtr' },
    'fulldate': { 'offset': 0x10, 'size': 'stringPtr' },
    
    'reaction_list_ptr': { 'offset': 0xdc, 'size': 4 },
    'reaction_list_size': { 'offset': 0xe0, 'size': 4 },
    'requirements_ptr': { 'offset': 0xe4, 'size': 4 },
    'requirement_count': { 'offset': 0xe8, 'size': 4 },
    'hit_conditions_ptr': { 'offset': 0xec, 'size': 4 },
    'hit_conditions_size': { 'offset': 0xf0, 'size': 4 },
    'projectile_ptr': { 'offset': None, 'size': 4 }, #unknown
    'projectile_size': { 'offset': None, 'size': 4 }, #unknown
    'pushback_ptr': { 'offset': 0xf4, 'size': 4 },
    'pushback_list_size': { 'offset': 0xf8, 'size': 4 },
    'pushback_extradata_ptr': { 'offset': 0xfc, 'size': 4 },
    'pushback_extradata_size': { 'offset': 0x100, 'size': 4 },
    'cancel_head_ptr': { 'offset': 0x104, 'size': 4 },  
    'cancel_list_size': { 'offset': 0x108, 'size': 4 },
    'group_cancel_head_ptr': { 'offset': 0x10c, 'size': 4 }, 
    'group_cancel_list_size': { 'offset': 0x110, 'size': 4 }, 
    'cancel_extradata_head_ptr': { 'offset': None, 'size': 4 }, 
    'cancel_extradata_list_size': { 'offset': None, 'size': 4 }, 
    'extra_move_properties_ptr': { 'offset': 0x114, 'size': 4 }, #unknown
    'extra_move_properties_size': { 'offset': 0x118, 'size': 4 }, #unknown
    'movelist_head_ptr': { 'offset': 0x11c, 'size': 4 },
    'movelist_size': { 'offset': 0x120, 'size': 4 },
    'voiceclip_list_ptr': { 'offset': 0x124, 'size': 4 }, #unknown
    'voiceclip_list_size': { 'offset': 0x128, 'size': 4 }, #unknown
    'input_sequence_ptr': { 'offset': None, 'size': 4 }, #unknown
    'input_sequence_size': { 'offset': None, 'size': 4 }, #unknown
    'input_extradata_ptr': { 'offset': None, 'size': 4 }, #unknown
    'input_extradata_size': { 'offset': None, 'size': 4 }, #unknown
    'unknown_parryrelated_list_ptr': { 'offset': None, 'size': 4 }, #unknown
    'unknown_parryrelated_list_size': { 'offset': None, 'size': 4 }, #unknown
    'throw_extras_ptr': { 'offset': None, 'size': 4 }, #unknown
    'throw_extras_size': { 'offset': None, 'size': 4 }, #unknown
    'throws_ptr': { 'offset': None, 'size': 4 }, #unknown
    'throws_size': { 'offset': None, 'size': 4 }, #unknown
    
    'mota_start': { 'offset': None, 'size': None },
    'aliases': { 'offset': 0x14, 'size': (32, 4) },
    'aliases2': { 'offset': 0x98, 'size': (37, 2) },
    
    'pushback:val1': { 'offset': 0x0, 'size': 2 },
    'pushback:val2': { 'offset': 0x2, 'size': 2 },
    'pushback:val3': { 'offset': 0x4, 'size': 2 },
    'pushback:extra_addr': { 'offset': 0x8, 'size': 4 },
    
    'pushbackextradata:value': { 'offset': 0x0, 'size': 2 },
    
    'requirement:req': { 'offset': 0x0, 'size': 2 },
    'requirement:param': { 'offset': 0x2, 'size': 2 },
    
    'cancelextradata:value': { 'offset': 0x0, 'size': 4 },
    
    'cancel:command': { 'offset': 0x0, 'size': 4 },
    'cancel:requirement_addr': { 'offset': 0x4, 'size': 4 },
    'cancel:extradata_addr': { 'offset': 0xc, 'size': 4 },
    'cancel:frame_window_start': { 'offset': 0x10, 'size': 2 },
    'cancel:frame_window_end': { 'offset': 0x12, 'size': 2 },
    'cancel:starting_frame': { 'offset': 0x14, 'size': 2 },
    'cancel:move_id': { 'offset': 0x8, 'size': 2 },
    'cancel:cancel_option': { 'offset': 0x16, 'size': 2 },
    
    'reactionlist:ptr_list': { 'offset': 0x0, 'size': (7, 4) }, #array of 7 variables, each 8 bytes long
    'reactionlist:u1list': { 'offset': 0x1c, 'size': (6, 2) },  #array of 6 variables, each 2 bytes long
    'reactionlist:vertical_pushback': { 'offset': 0x30, 'size': 2 },
    'reactionlist:standing': { 'offset': 0x34, 'size': 2 },
    'reactionlist:crouch': { 'offset': 0x36, 'size': 2 },
    'reactionlist:ch': { 'offset': 0x38, 'size': 2 },
    'reactionlist:crouch_ch': { 'offset': 0x3a, 'size': 2 },
    'reactionlist:left_side': { 'offset': 0x3c, 'size': 2 },
    'reactionlist:left_side_crouch': { 'offset': 0x3e, 'size': 2 },
    'reactionlist:right_side': { 'offset': 0x40, 'size': 2 },
    'reactionlist:right_side_crouch': { 'offset': 0x42, 'size': 2 },
    'reactionlist:back': { 'offset': 0x44, 'size': 2 },
    'reactionlist:back_crouch': { 'offset': 0x46, 'size': 2 },
    'reactionlist:block': { 'offset': 0x48, 'size': 2 },
    'reactionlist:crouch_block': { 'offset': 0x4a, 'size': 2 },
    'reactionlist:wallslump': { 'offset': 0x4c, 'size': 2 },
    'reactionlist:downed': { 'offset': 0x4e, 'size': 2 },
    
    'hitcondition:requirement_addr': { 'offset': 0x0, 'size': 4 },
    'hitcondition:damage': { 'offset': 0x4, 'size': 2 },
    'hitcondition:reaction_list_addr': { 'offset': 0x8, 'size': 4 },
    
    'extramoveprop:type': { 'offset': 0x0, 'size': 2 },
    'extramoveprop:id': { 'offset': 0x2, 'size': 2 },
    'extramoveprop:value': { 'offset': 0x4, 'size': 4 },    
    
    'move:name': { 'offset': None, 'size': 'stringPtr' },
    'move:anim_name': { 'offset': None, 'size': 'stringPtr' },
    'move:anim_addr': { 'offset': 0x0, 'size': 4 },
    'move:vuln': { 'offset': 0x4, 'size': 4 },
    'move:hitlevel': { 'offset': 0x8, 'size': 4 },
    'move:cancel_addr': { 'offset': 0xc, 'size': 4 },
    'move:transition': { 'offset': 0x10, 'size': 2 },
    'move:anim_max_len': { 'offset': 0x1c, 'size': 2 },
    'move:startup': { 'offset': 0x30, 'size': 2 },
    'move:recovery': { 'offset': 0x31, 'size': 2 }, #unknown
    'move:hit_condition_addr': { 'offset': 0x18, 'size': 4 },
    'move:voiceclip_ptr': { 'offset': 0x20, 'size': 4 },
    'move:extra_properties_ptr': { 'offset': 0x24, 'size': 4 },
    'move:hitbox_location': { 'offset': 0x28, 'size': 4, 'endian': 'little' },
    #'move:u1': { 'offset': 0x18, 'size': 4 },
    'move:u2': { 'offset': None, 'size': 4 },
    'move:u3': { 'offset': None, 'size': 4 },
    'move:u4': { 'offset': None, 'size': 4 },
    #'move:u5': { 'offset': 0x28, 'size': 4 },
    'move:u6': { 'offset': None, 'size': 4 },
    'move:u7': { 'offset': None, 'size': 2 },
    'move:u8': { 'offset': None, 'size': 2 },
    'move:u8_2': { 'offset': None, 'size': 2 },
    'move:u9': { 'offset': None, 'size': 2 },
    'move:u10': { 'offset': None, 'size': 4 },
    'move:u11': { 'offset': None, 'size': 4 },
    'move:u12': { 'offset': None, 'size': 4 },
    #'move:u13': { 'offset': 0x54 'size': 4 },
    #'move:u14': { 'offset': 0x58, 'size': 4 },
    'move:u15': { 'offset': None, 'size': 4 },
    'move:u16': { 'offset': None, 'size': 2 },
    'move:u17': { 'offset': None, 'size': 2 },
    'move:u18': { 'offset': None, 'size': 4 },
    
    'voiceclip:value': { 'offset': 0x0, 'size': 4 },
    
    'inputextradata:u1': { 'offset': 0x0, 'size': 2 },
    'inputextradata:u2': { 'offset': 0x2, 'size': 2 },
    
    'inputsequence:u1': { 'offset': 0x1, 'size': 1 },
    'inputsequence:u2': { 'offset': 0x2, 'size': 2 },
    'inputsequence:u3': { 'offset': 0x0, 'size': 1 },
    'inputsequence:extradata_addr': { 'offset': 4, 'size': 4 },
    
    'throw:u1': { 'offset': 0x0, 'size': 4 },
    'throw:throwextra_addr': { 'offset': 0x4, 'size': 4 },
    
    'unknownparryrelated:value': { 'offset': 0x0, 'size': 4 },
    
    'projectile:u1': { 'offset': 0x0, 'size': (48, None) }, # 48 * [0]
    'projectile:hit_condition_addr': { 'offset': None, 'size': 4 }, #0
    'projectile:cancel_addr': { 'offset': None, 'size': 4 }, #0
    'projectile:u2': { 'offset': 0x70, 'size': (28, None) }, # 28 * [0]
    
    'throwextra:u1': { 'offset': 0x0, 'size': 4 },
    'throwextra:u2': { 'offset': 4, 'size': (4, 2) },
}

offsetTables = {
    't7': t7_offsetTable,
    'tag2': tag2_offsetTable,
    'rpcs3_tag2': tag2_offsetTable,
    'rev': tag2_offsetTable,
    't6': t6_offsetTable,
    't5': t5_offsetTable,
    't5dr': t5dr_offsetTable,
    't4': t4_offsetTable,
    '3d': t6_offsetTable,
}

animHeaders = {
    't5dr': b'\x00\x64\x00\x17\x00\x0B\x00\x0B\x00\x05\x00\x07\x00\x07\x00\x07\x00\x0B\x00\x07\x00\x07\x00\x07\x00\x07\x00\x06\x00\x07\x00\x07\x00\x07\x00\x06\x00\x07\x00\x07\x00\x06\x00\x07\x00\x07\x00\x06\x00\x07',
    't5':   b'\x64\x00\x17\x00\x0B\x00\x0B\x00\x05\x00\x07\x00\x07\x00\x07\x00\x0B\x00\x07\x00\x07\x00\x07\x00\x07\x00\x06\x00\x07\x00\x07\x00\x07\x00\x06\x00\x07\x00\x07\x00\x06\x00\x07\x00\x07\x00\x06\x00\x07\x00',
}

t5_character_name_mappping = {
    b'\x95\x97\x8a\xd4 \x90m': '[JIN]',
    b'BAEK DOO SAN': '[BAEK_DOO_SAN]',
    b'[\x83G\x83f\x83B\x81E\x83S\x83\x8b\x83h\x81[]': '[EDDY]',
    b'[DEVIL JIN]': '[DEVIL_JIN]',
    b'[\x8d\x95\x90l\x94E\x8e\xd2]': '[RAVEN]',
    b'[ \x94\xf2\x92\xb9 ]': '[ASUKA]',
    b'[\x91\xbe\x8b\xc9\x8c\x9d]' : '[FENG]',
    b'[\x8c\xb5\x97\xb3]': '[GANRYU]',
    b'[ \x89\xa4 \x96\xb8\x97\x8b ]': '[WANG]',
    b'[\x83A\x83}\x83L\x83\x93]': '[ARMOR_KING]',
    b'[\x93S\x8c\x9d5\x83{\x83X]': '[JINPACHI]',
    b'[ VALE-TUDO ]': '[MARDUK]',
    b'[ANNA]': '[ANNA]',
    b'[ \x83\x8d\x83E ]': '[LAW]',
    b'[\x89\xd4\x98Y]': '[HWOARANG]',
    b'[\x83L\x83\x93\x83O]': '[KING]',
    b'[EMILIE]': '[EMILIE]',
    b'[\x90V\x83L\x83\x83\x83\x89(\x91\xe5\x8d\xb2)]': '[DRAGUNOV]',
    b'\x8eO\x93\x87 \x95\xbd\x94\xaa': '[HEIHACHI]',
    b'[\x83N\x83\x8a\x83X\x83e\x83B]': '[CHRISTIE]',
    b'[\x83|\x81[\x83\x8b]': '[PAUL]',
    b'[\x83W\x83\x83\x83b\x83N\x82T]': '[JACK]',
    b'\x83u\x83\x8b\x81[\x83X': '[BRUCE]',
    b'[\x83\x8d\x83W\x83\x83\x81[]': '[ROGER]',
    b'[ \x97\x8b \x95\x90\x97\xb4 ]': '[LEI_WULONG]',
    b'[\x83j\x81[\x83i]': '[NINA]',
    b'\x83{\x83N\x83T\x81[': '[STEVE_FOX]',
    b'[ \x8eO\x93\x87 \x88\xea\x94\xaa ]': '[KAZUYA]',
    b'\x97\xbd \x8b\xc5\x89J': '[LIN_XIAOYU]',
    b'[ \x97\x9b \x92\xb4\x98T ]': '[LEE]',
    b'[ \x83W\x83\x85\x83\x8a\x83A ]': '[JULIA]',
    b'\x8bg\x8c\xf5': '[YOSHIMITSU]',
    b'\x83u\x83\x89\x83C\x83A\x83\x93': '[BRYAN]',
    b'[\x83N\x83}]': '[PANDA]'
}

characterNameMapping = {
    't5': t5_character_name_mappping,
    't5dr': t5_character_name_mappping,
    't4': {
        b'\x95\x97\x8a\xd4 \x90m': '[JIN]',
        b'[\x83G\x83f\x83B\x81E\x83S\x83\x8b\x83h\x81[]': '[EDDY]',
        b'[ VALE-TUDO ]': '[MARDUK]',
        b'[ \x83\x8d\x83E ]': '[LAW]',
        b'[\x89\xd4\x98Y]': '[HWOARANG]',
        b'[\x83L\x83\x93\x83O]': '[KING]',
        b'\x8eO\x93\x87 \x95\xbd\x94\xaa': '[HEIHACHI]',
        b'[\x83N\x83\x8a\x83X\x83e\x83B]': '[CHRISTIE]',
        b'[\x83|\x81[\x83\x8b]': '[PAUL]',
        b'[ \x97\x8b \x95\x90\x97\xb4 ]': '[LEI_WULONG]',
        b'[\x83j\x81[\x83i]': '[NINA]',
        b'\x83{\x83N\x83T\x81[': '[STEVE_FOX]',
        b'[ \x8eO\x93\x87 \x88\xea\x94\xaa ]': '[KAZUYA]',
        b'\x97\xbd \x8b\xc5\x89J': '[LIN_XIAOYU]',
        b'[ \x97\x9b \x92\xb4\x98T ]': '[LEE]',
        b'[ \x83W\x83\x85\x83\x8a\x83A ]': '[JULIA]',
        b'\x8bg\x8c\xf5': '[YOSHIMITSU]',
        b'\x83u\x83\x89\x83C\x83A\x83\x93': '[BRYAN]',
        b'[\x83N\x83}]': '[PANDA]'
    },
}
 
def readOffsetTable(self, key=''):
    if key == '':
        keyPrefix = ''
        keylist = [k for k in self.offsetTable if k.find(':') == -1]
    else:
        keyPrefix = key + ':'
        splitLen = len(keyPrefix)
        keylist = [k[splitLen:] for k in self.offsetTable if k.startswith(keyPrefix)]
    
    for label in keylist:
        key = keyPrefix + label
        offset, size = self.offsetTable[key]['offset'], self.offsetTable[key]['size']
        endian = self.endian if 'endian' not in self.offsetTable[key] else self.offsetTable[key]['endian']
        
        if size == None:
            continue
            
        if offset == None:
            value = 0
        elif size == 'stringPtr' or size == 'invalidStringPtr':
            if self.data == None:
                value = self.readInt(self.addr + offset, self.ptr_size)
            else:
                value = self.bToInt(self.data, offset, self.ptr_size)
            value = self.readString(self.base + value) if size == 'stringPtr' else self.readBytesUntilZero(self.base + value)
        elif type(size) is tuple:
            value = []
            varCount, varSize = size
            
            for i in range(varCount):
                if varSize == None:
                    varVal = 0
                elif self.data == None:
                    varVal = self.readInt(self.addr + offset + (i * varSize), varSize)
                else:
                    varVal = self.bToInt(self.data, offset + (i * varSize), varSize)
                value.append(varVal)
        else:
            if self.data == None:
                value = self.readInt(self.addr + offset, size)
            else:
                value = self.bToInt(self.data, offset, size, ed=endian)
    
        setattr(self, label, value)

def getMovesetName(TekkenVersion, character_name):
    if character_name.startswith(TekkenVersion):
        return character_name
    if character_name.startswith('['):
        if character_name.endswith(']'):
            character_name = character_name[1:-1]
        else:
            character_name = character_name.replace('[', '__')
            character_name = character_name.replace(']', '__')
    return '%s_%s' % (TekkenVersion, character_name.upper())

def initTekkenStructure(self, parent, addr=0, size=0):
    self.addr = addr
    self.T = parent.T
    self.TekkenVersion = parent.TekkenVersion
    self.ptr_size = parent.ptr_size
    self.base = parent.base
    self.endian = parent.endian
    self.offsetTable = parent.offsetTable
    
    self.readInt = parent.readInt
    self.readBytes = parent.readBytes
    self.readString = parent.readString
    self.readBytesUntilZero = parent.readBytesUntilZero
    self.readStringPtr = parent.readStringPtr
    self.bToInt = parent.bToInt
    
    if addr != 0 and size != 0:
        self.data = self.readBytes(self.base + addr, size)
    else:
        self.data = None
    return self.data
        
def setStructureSizes(self):
    for key in structSizes[self.TekkenVersion]:
        setattr(self, key, structSizes[self.TekkenVersion][key])
            
class Exporter:
    def __init__(self, TekkenVersion, folder_destination='./extracted_chars/'):
        game_addresses.reloadValues()

        self.T = GameClass(game_addresses[TekkenVersion + '_process_name'])
        self.T.applyModuleAddress(game_addresses)
        self.TekkenVersion = TekkenVersion
        self.ptr_size = ptrSizes[TekkenVersion]
        self.base =  game_addresses[TekkenVersion + '_base']

        self.endian = endians[TekkenVersion]
        self.folder_destination = folder_destination
        self.offsetTable = offsetTables[TekkenVersion]
        
        if not os.path.isdir(folder_destination):
            os.mkdir(folder_destination)
        
    def getP1Addr(self):
        if (self.TekkenVersion + '_p1_addr') in game_addresses.addr:
            return game_addresses[self.TekkenVersion + '_p1_addr']
        matchKeys = [key for key in game_addresses.addr if key.startswith(self.TekkenVersion + '_p1_addr_')]
        regex = game_addresses[self.TekkenVersion + '_window_title_regex']
        
        windowTitle = self.T.getWindowTitle()
        p = re.compile(regex)
        match = p.search(windowTitle)
        if match == None:
            raise Exception('Player address not found')
        key = self.TekkenVersion + '_p1_addr_' + match.group(1)
        return None if key not in game_addresses.addr else game_addresses[key]
        
    def readInt(self, addr, len):
        return self.T.readInt(addr, len, endian=self.endian)
        
    def readBytes(self, addr, len):
        return self.T.readBytes(addr, len)
        
    def readString(self, addr):
        offset = 0
        while self.readInt(addr + offset, 1) != 0:
            offset += 1
        return self.readBytes(addr, offset).decode("ascii")
        
    def readBytesUntilZero(self, addr):
        offset = 0
        while self.readInt(addr + offset, 1) != 0:
            offset += 1
        return self.readBytes(addr, offset)
        
    def readStringPtr(self, addr):
        return self.readString(self.base + self.readInt(addr, self.ptr_size))
        
    def readInvalidStrPtr(self, addr):
        return self.readBytesUntilZero(self.base + self.readInt(addr, self.ptr_size))
        
    def bToInt(self, data, offset, length, ed=None):
        return int.from_bytes(data[offset:offset + length], ed if ed != None else self.endian)
        
    def getMotbinPtr(self, playerAddress):
        key = self.TekkenVersion + '_motbin_offset'
        motbin_ptr_addr = (playerAddress + game_addresses[key])
        return self.readInt(motbin_ptr_addr, self.ptr_size)

    def getPlayerMovesetName(self, playerAddress):
        offset = self.offsetTable['character_name']['offset']
        motbin_ptr = self.getMotbinPtr(self.base + playerAddress)
        try:
            return self.readStringPtr(self.base + motbin_ptr + offset)
        except:
            if self.TekkenVersion not in characterNameMapping:
                return 'UNKNOWN'
            val = self.readInvalidStrPtr(self.base + motbin_ptr + offset)
            for name in characterNameMapping[self.TekkenVersion]:
                try: # Try seeing if we know the first part of the name (So that things like [LAW]_STORY_ may work)
                    if val.index(name) == 0:
                        nameSuffix = val[len(name):]
                        printable = set(string.printable)
                        nameSuffix = ''.join([chr(b) for b in nameSuffix if chr(b) in printable])
                        nameSuffix = re.sub(' |\\|\]|\[', '_', nameSuffix)
                        
                        return characterNameMapping[self.TekkenVersion][name] + nameSuffix
                except Exception as e:
                    pass
            return characterNameMapping[self.TekkenVersion].get(val, 'UNKNOWN')
            
    def exportMoveset(self, playerAddress, name=''):
        motbin_ptr = self.getMotbinPtr(self.base + playerAddress)
        
        m = Motbin(self.base + motbin_ptr, self, name)
        m.getCharacterId(playerAddress)
        m.extractMoveset()
        return m 
    
def getAnimEndPos(TekkenVersion, data):
    minSize = 1000
    if len(data) < minSize:
        return -1
    searchStart = minSize - 100
    pos = animEndPosFunc[TekkenVersion](data, searchStart)
    pos = [p+searchStart for p in pos if p != -1]
    return -1 if len(pos) == 0 else min(pos)
    
AnimC8OffsetTable = {
    0x17: 0x64,
    0x19: 0x6C,
    0x1B: 0x74,
    0x1d: 0x7c,
    0x1f: 0x80,
    0x21: 0x8c,
    0x23: 0x94,
    0x31: 0xcc 
}
    
class AnimData:
    def __init__(self, name, data_addr, parent):
        initTekkenStructure(self, parent, data_addr, 0)
        self.name = name
        self.data = None
        self.type = None
        self.length = 0
        
    def getLength(self):
        if self.type == 0xC8:
            return self.readInt(self.addr + 4, 4)
        else:
            return 0
    
    def getC8EndPos(self): #t7
        type = self.readInt(self.addr + (2 if self.endian == 'little' else 3), 1)
        framesize = type * 0xC
        return (framesize * self.length) + AnimC8OffsetTable[type]
        
    def findEndingPos(self, maxLen=None):
        read_size = 8192
        offset = 0
        prev_bytes = None
        defaultMaxLen = 50000000
        maxLen = defaultMaxLen if (maxLen == None or maxLen > defaultMaxLen) else maxLen
        
        while read_size >= 8:
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
                if offset + read_size > maxLen:
                    return maxLen
                offset += read_size
        return offset
        
    def getType(self):
        return self.readInt(self.addr + (0 if self.endian == 'little' else 1), 1)
                
    def getData(self, boundaries):
        if self.data == None:
            self.type = self.getType()
            self.length = self.getLength()
        
            boundaryAddr = None
            for i, addr in enumerate(boundaries):
                if self.addr >= boundaries[i] and (len(boundaries) != i + 1 and self.addr < boundaries[i + 1]):
                    boundaryAddr = boundaries[i + 1]
                    
                  
            maxLen = boundaryAddr - self.addr if boundaryAddr != None else None
                  
            if self.type == 0xc8:
                endPos = self.getC8EndPos()
            else:
                endPos = self.findEndingPos(maxLen)
            
            self.data = None
            
            if endPos > 0:
                successfulyRead = False
                while True:
                    try:
                        origEndPos = endPos
                        endPos = int(endPos * 0.9) #Failsafe in case the animation reaches the end of the allocated area
                        if endPos == 0: break
                        self.data = self.readBytes(self.addr, origEndPos)
                        successfulyRead = True
                        break
                    except:
                        pass
                if not successfulyRead:
                    print("Error extracting animation " + self.name + ", game might crash with this moveset.", file=sys.stderr)
                    return None
                
            if self.TekkenVersion in animHeaders:
                self.data = animHeaders[self.TekkenVersion] + self.data

            oldData = self.data
            if swapGameAnimBytes[self.TekkenVersion]:
                try:
                    self.data = SwapAnimBytes(self.data)
                except Exception as e:
                    print(e)
                    self.data = oldData
                    print("Error byteswapping animation " + self.name + ", game might crash with this moveset.", file=sys.stderr)

        return self.data
        
    def __eq__(self, other):
        return self.name == other.name
        
class Pushback:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.Pushback_size)
        
        readOffsetTable(self, 'pushback')
        self.extra_index = -1
        
    def dict(self):
        return {
            'val1': self.val1,
            'val2': self.val2,
            'val3': self.val3,
            'pushbackextra_idx': self.extra_index
        }
        
    def setExtraIndex(self, idx):
        self.extra_index = idx
        
class PushbackExtradata:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.PushbackExtradata_size)
        
        readOffsetTable(self, 'pushbackextradata')
        
    def dict(self):
        return self.value
        
class Requirement:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.Requirement_size)
        
        readOffsetTable(self, 'requirement')
        
    def dict(self):
        return {
            'req': self.req,
            'param': self.param
        }
        
class CancelExtradata:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.CancelExtradata_size)
        
        readOffsetTable(self, 'cancelextradata')
        
    def dict(self):
        return self.value
        
        
class Cancel:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.Cancel_size)
        
        readOffsetTable(self, 'cancel')
        
        if self.endian == 'big' and self.TekkenVersion != 't5dr': #swapping first two ints
            t = self.bToInt(data, 0, 4)
            t2 = self.bToInt(data, 0x4, 4) 
            self.command = (t2 << 32) | t
        elif self.TekkenVersion == 't5dr':
            t = (self.command & 0xFFFF0000) >> 16
            t |= (self.command & 0xFF) << 32
            t |= (self.command & 0xFF00) << 49
            self.command = t

            if self.command == 0x8005:
                self.command = 0x800b
            elif self.command == 0x8006:
                self.command = 0x800c
            # Adjusting input sequences. Looks like they start from 0x8013 instead of 0x800d
            elif self.command >= 0x8013 and self.command <= 0x81FF:
                self.command += 6
        elif self.TekkenVersion == 't5':
            t = (self.command & 0x00FF0000) << 16
            t |= (self.command & 0xFF000000) << 33
            t |= (self.command & 0x0000FFFF)
            self.command = t

            if self.command == 0x8005:
                self.command = 0x800b
            elif self.command == 0x8006:
                self.command = 0x800c
            # Adjusting input sequences. Looks like they start from 0x8013 instead of 0x800d
            elif self.command >= 0x8013 and self.command <= 0x81FF:
                self.command += 6
        
        self.extradata_id = -1
        self.requirement_idx =- -1
        
    def dict(self):
        return {
            'command': self.command,
            'extradata_idx': self.extradata_id,
            'requirement_idx': self.requirement_idx,
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
        
class ReactionList:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.ReactionList_size)
        
        readOffsetTable(self, 'reactionlist')
        self.pushback_indexes = [-1] * 7
        
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
        
        readOffsetTable(self, 'hitcondition')
        
    def dict(self):
        return {
            'requirement_idx': self.requirement_idx,
            'damage': self.damage,
            'reaction_list_idx': self.reaction_list_idx
        }

    def setRequirementId(self, id):
        self.requirement_idx = id

    def setReactionListId(self, id):
        self.reaction_list_idx = id
    
class ExtraMoveProperty:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.ExtraMoveProperty_size)
        
        readOffsetTable(self, 'extramoveprop')
            
    def dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'value': self.value
        }
    
class Move:
    def __init__(self, addr, parent, moveId=None):
        data = initTekkenStructure(self, parent, addr, parent.Move_size)
        
        readOffsetTable(self, 'move')
        
        if self.name == 0:
            self.name = str(addr) if moveId == None else str(moveId)
            self.anim_name = self.name
        
        self.anim = AnimData(self.anim_name, self.base + self.anim_addr, self)
        self.cancel_idx = -1
        self.hit_condition_idx = -1
        self.extra_properties_idx = -1
        self.voiceclip_idx = -1
    
    def dict(self):
        return {
            'name': self.name,
            'anim_name': self.anim_name,
            'vuln': self.vuln,
            'hitlevel': self.hitlevel,
            'cancel_idx': self.cancel_idx,
            'transition': self.transition,
            'anim_max_len': self.anim_max_len,
            'hit_condition_idx': self.hit_condition_idx,
            'voiceclip_idx': self.voiceclip_idx,
            'extra_properties_idx': self.extra_properties_idx,
            'hitbox_location': self.hitbox_location,
            'first_active_frame': self.startup,
            'last_active_frame': self.recovery,
            
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
    
class Voiceclip:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.Voiceclip_size)
        
        readOffsetTable(self, 'voiceclip')
        
        # Assuming DR uses same voiceclip scheme as vanilla T5
        # Converts 2 byte value into 4 byte equivalent
        if self.TekkenVersion == "t5" or self.TekkenVersion == "t5dr":
            if self.value == 0xFFFF:
                self.value = 0xFFFFFFFF
            elif 0x0F00 <= self.value < 0x1000:  # If in range of 0x0F00
                self.value = (self.value << 16) & 0xFF000000 | (
                    self.value & 0x000000FF)
            else: # E.g; 0x2006 -> 0x0200006
                self.value = (self.value << 12) & 0xFF000000 | (
                    self.value & 0x000000FF)

    def dict(self):
        return self.value
        
class InputExtradata:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.InputExtradata_size)
        
        readOffsetTable(self, 'inputextradata')
        
        if self.TekkenVersion == "t5":
            command = self.u2 << 16 | self.u1
            t = (command & 0x00FF0000) << 16
            t |= (command & 0xFF000000) << 33
            t |= (command & 0x0000FFFF)
            self.u1 = t & 0xffffffff
            self.u2 = t >> 32
        
    def dict(self):
        return {
            'u1': self.u1,
            'u2': self.u2
        }
        
class InputSequence:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.InputSequence_size)
        
        readOffsetTable(self, 'inputsequence')
        
        self.extradata_idx = -1
        
    def setExtradataId(self, idx):
        self.extradata_idx = idx
        
    def dict(self):
        return {
            'u1': self.u1,
            'u2': self.u2,
            'u3': self.u3,
            'extradata_idx': self.extradata_idx
        }
        
class Projectile:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.Projectile_size)
        
        readOffsetTable(self, 'projectile')
        
        self.hit_condition = -1
        self.cancel_idx = -1
        
    def dict(self):
        return {
            'u1': self.u1,
            'u2': self.u2,
            'hit_condition_idx': self.hit_condition,
            'cancel_idx': self.cancel_idx
        }
        
    def setHitConditionIdx(self, idx):
        self.hit_condition = idx
        
    def setCancelIdx(self, cancel_idx):
        self.cancel_idx = cancel_idx
        
class ThrowExtra:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.ThrowExtra_size)
        
        readOffsetTable(self, 'throwextra')

    def dict(self):
        return {
            'u1': self.u1,
            'u2': self.u2
        }
        
class Throw:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.Throw_size)
        
        readOffsetTable(self, 'throw')
        
        self.throwextra_idx = -1
        
    def dict(self):
        return {
            'u1': self.u1,
            'throwextra_idx': self.throwextra_idx
        }
        
    def setThrowExtraIdx(self, idx):
        self.throwextra_idx = idx
        
class UnknownParryRelated:
    def __init__(self, addr, parent):
        data = initTekkenStructure(self, parent, addr, parent.UnknownParryRelated_size)
        
        readOffsetTable(self, 'unknownparryrelated')
        
    def dict(self):
        return self.value
        
class Motbin:
    def __init__(self, addr, exporterObject, name=''):
        initTekkenStructure(self, exporterObject, addr, size=0)
        setStructureSizes(self)
        self.folder_destination= exporterObject.folder_destination
    
        self.name = ''
        self.version = versionLabels[self.TekkenVersion]
        self.extraction_date = datetime.now(timezone.utc).__str__()
        self.extraction_path = ''
        
        try:
            readOffsetTable(self, '')
            
            mota_start = self.offsetTable['mota_start']['offset']
            self.mota_list = []
            
            if mota_start != None:
                for i in range(12):
                    mota_addr = self.readInt(addr + mota_start + (i * self.ptr_size), self.ptr_size)
                    mota_end_addr = self.readInt(addr + mota_start + ((i + 2) * self.ptr_size), self.ptr_size) if i < 10 else mota_addr + 20
                    self.mota_list.append((mota_addr, mota_end_addr - mota_addr))
                
            
            if isinstance(self.character_name, bytes):
                self.getCharacterNameFromBytes()
            if isinstance(self.creator_name, bytes):
                try:
                    self.creator_name = self.creator_name.decode('ascii')
                except:
                    self.creator_name = 'UNKNOWN'
                
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
        self.parry_related = []
        
    def getCharacterNameFromBytes(self):
        oldCharName = self.character_name
        if self.TekkenVersion in characterNameMapping:
            for name in characterNameMapping[self.TekkenVersion]:
                try: # Try seeing if we know the first part of the name (So that things like [LAW]_STORY_ may work)
                    if self.character_name.index(name) == 0:
                        nameSuffix = self.character_name[len(name):]
                        printable = set(string.printable)
                        nameSuffix = ''.join([chr(b) for b in nameSuffix if chr(b) in printable])
                        nameSuffix = re.sub(' |\\|\]|\[', '_', nameSuffix)
                        
                        self.character_name = characterNameMapping[self.TekkenVersion][name] + nameSuffix
                        return
                except Exception as e:
                    pass
            self.character_name = characterNameMapping[self.TekkenVersion].get(self.character_name, 'UNKNOWN')
        else:
            self.character_name = 'UNKNOWN'
        if self.character_name == 'UNKNOWN':
            print('Unknown character:', oldCharName)
        
    def __eq__(self, other):
        return self.character_name == other.character_name \
            and self.creator_name == other.creator_name \
            and self.date == other.date \
            and self.fulldate == other.fulldate
        
    def getCharacterId(self, playerAddress):
        key = self.TekkenVersion + '_chara_id_offset'
        if key in game_addresses.addr:
            self.chara_id = self.readInt(self.base + playerAddress + game_addresses[key], charaIdSize.get(self.TekkenVersion, 4))
        else:
            key = self.TekkenVersion + '_chara_id_addr'
            if key not in game_addresses.addr:
                self.chara_id = 0
            else:
                self.chara_id = (self.readInt(self.base  + game_addresses[key], 2))
        
    def printBasicData(self):
        if self.chara_id == -1:
            print("Character: %s" % (self.character_name))
        else:
            print("Character: %s (ID %d)" % (self.character_name, self.chara_id))
        print("Creator: %s" % (self.creator_name))
        print("Date: %s %s\n" % (self.date, self.fulldate))
        
    def dict(self):
        return {
            'original_hash': '',
            'last_calculated_hash': '',
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
            'aliases2': self.aliases2,
            'requirements': self.requirements,
            'cancels': self.cancels,
            'group_cancels': self.group_cancels,
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
            'throws': self.throws,
            'parry_related': self.parry_related
        }
        
    def calculateHash(self, movesetData):
        exclude_keys =  [
            'original_hash',
            'last_calculated_hash',
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
        for k in (key for key in movesetData.keys() if key not in exclude_keys):
           data += str(movesetData[k])
        
        data = bytes(str.encode(data))
        return "%x" % (crc32(data))
        
    def save(self):
        print("Saving data...")
        
        path = self.folder_destination + self.export_folder
        self.extraction_path = path
        anim_path = "%s/anim" % (path)
            
        jsonPath = "%s/%s.json" % (path, self.name)
        
        if not os.path.isdir(path):
            os.mkdir(path)
        if not os.path.isdir(anim_path):
            os.mkdir(anim_path)
            
        if os.path.exists(jsonPath):
            os.remove(jsonPath)
            
        with open(jsonPath, "w") as f:
            movesetData = self.dict()
            movesetData['original_hash'] = self.calculateHash(movesetData)
            movesetData['last_calculated_hash'] = movesetData['original_hash']
            json.dump(movesetData, f, indent=4)
            
        print("Saving animations...")
        animBoundaries = sorted([anim.addr for anim in self.anims])
        existingAnim = 0
        for anim in self.anims:
            try:
                filePath = "%s/%s.bin" % (anim_path, anim.name)
                if os.path.exists(filePath):
                    existingAnim += 1
                else:
                    with open (filePath, "wb") as f:
                        animdata = anim.getData(animBoundaries)
                        if animdata == None:
                            raise 
                        f.write(animdata)
            except Exception as e:
                print("Error extracting animation %s, file will not be created" % (anim.name), file=sys.stderr)
        if existingAnim != 0:
            animLen = len(self.anims)
            print("%d/%d anims missing and imported." % (animLen - existingAnim, animLen))
                        
        print("Saving MOTA animations...")
        for i, mota in enumerate(self.mota_list):
            mota_addr, mota_size = mota
            filePath = "%s/mota_%d.bin" % (path, i)
            if not os.path.exists(filePath):
                try:
                    mota_data = self.readBytes(self.base + mota_addr, mota_size)
                except:
                    print("Error getting MOTA %d, file will not be created." % (i))
                    continue
                    
                try:
                    if self.readInt(self.base+mota_addr+4, 4) == 256: # if 2nd byte is 256, convert this into little endian
                        mota_data = SwapMotaBytes(mota_data)
                except:
                    print("Error byteswapping MOTA %d, file will not be byteswapped." % (i))
                with open(filePath, "wb") as f:
                    f.write(mota_data)
            
        print("Saved at path %s.\nHash: %s" % (path.replace("\\", "/"), movesetData['original_hash']))
        
    def extractMoveset(self):
        self.printBasicData()
        
        print("Reading parry-related...")
        for i in range(self.unknown_parryrelated_list_size):
            unknown = UnknownParryRelated(self.unknown_parryrelated_list_ptr + (i * self.UnknownParryRelated_size), self)
            self.parry_related.append(unknown.dict())
            
        if self.input_extradata_size != 0:
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
            self.cancels.append(cancel.dict())
        
        print("Reading grouped cancels...")
        for i in range(self.group_cancel_list_size):
            cancel = Cancel(self.group_cancel_head_ptr + (i * self.Cancel_size), self)
            cancel.setRequirementId((cancel.requirement_addr - self.requirements_ptr) // self.Requirement_size)
            cancel.setExtradataId((cancel.extradata_addr - self.cancel_extradata_head_ptr) // self.CancelExtradata_size)
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
            throw.setThrowExtraIdx((throw.throwextra_addr - self.throw_extras_ptr) // self.ThrowExtra_size)
            self.throws.append(throw.dict())
        
        print("Reading movelist...")
        for i in range(self.movelist_size):
            move = Move(self.movelist_head_ptr + (i * self.Move_size), self, i)
            move.setCancelIdx((move.cancel_addr - self.cancel_head_ptr) // self.Cancel_size)
            move.setHitConditionIdx((move.hit_condition_addr - self.hit_conditions_ptr) // self.HitCondition_size)
            if move.extra_properties_ptr != 0:
                move.setExtraPropertiesIdx((move.extra_properties_ptr - self.extra_move_properties_ptr) // self.ExtraMoveProperty_size)
            if move.voiceclip_ptr != 0:
                move.setVoiceclipId((move.voiceclip_ptr - self.voiceclip_list_ptr) // self.Voiceclip_size)
            self.moves.append(move.dict())
            
            if move.anim not in self.anims:
                self.anims.append(move.anim)

        self.save()
        
if __name__ == "__main__":

    if len(sys.argv) <= 1:
        print("Usage: ./motbinExport [t7/tag2/rev/t6/3d/t5/t5dr]")
        os._exit(1)
        
    TekkenVersion = sys.argv[1]
    if (TekkenVersion + '_process_name') not in game_addresses.addr:
        print("Unknown version '%s'" % (TekkenVersion))
        os._exit(1)
    
    try:
        TekkenExporter = Exporter(TekkenVersion)
    except Exception as e:
        print(e)
        os._exit(0)
    
    extractedMovesetNames = []
    extractedMovesets = []
    
    playerAddr = TekkenExporter.getP1Addr()
    playerOffset = game_addresses[TekkenVersion + "_playerstruct_size"]
    
    playerCount = 4 if TekkenVersion == 'tag2' else 2
    if len(sys.argv) > 2:
        playerCount = int(sys.argv[2])
    
    for i in range(playerCount):
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

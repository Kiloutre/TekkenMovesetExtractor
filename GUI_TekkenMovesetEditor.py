# Python 3.6.5

from tkinter import Tk, Frame, Listbox, Label, Scrollbar, StringVar, Toplevel, Menu, messagebox, Text, simpledialog
from tkinter.ttk import Button, Entry, Style
from Addresses import game_addresses, GameClass
import shutil
import copy
import motbinImport as importLib
import json
import os
import re
import ctypes
from zlib import crc32

charactersPath = "./extracted_chars/"
editorVersion = "0.32-BETA"

requirementLabels = {}
propertyLabels = {}
commandLabels = {}

for i in range(0x83c4, 0x83c4 + 112):
    propertyLabels[i] = 'Set %d alias' % (i)

def getDetails(itemId, key):
    tekkenAliasesList = {
        'requirements': requirementLabels,
        'extra_move_properties': propertyLabels
    }
    
    return tekkenAliasesList[key].get(itemId)

reqListEndval = {
    'Tekken7': 881,
    'Tag2': 690,
    'Revolution': 697,
    'Tekken6': 397,
    'Tekken5DR': 327,
    'Tekken5': 321,
    'Tekken4': 263,
}

itemNames = {
    'moves': 'move',
    'cancels': 'cancel',
    'group_cancels': 'group cancel',
    'requirements': 'requirement',
    'extra_move_properties': 'move property',
    'hit_conditions': 'hit condition',
    'reaction_list': 'reaction list',
    'pushbacks': 'pushback',
    'pushback_extras': 'pushback-extra',
    'cancel_extradata': 'cancel-extra',
    'voiceclips': 'voiceclip',
}

fieldLabels = {
    'u10': 'airborne_start',
    'u11': 'airborne_end',
    'u16': 'collision? (u16)',
    'u17': 'distance (u17)',
    'anim_max_len': 'anim_len',
    'standing': 'default',
    'type': 'starting_frame',
}

moveFields = {
    'name': 'text',
    'anim_name': 'text',
    'vuln': 'int',
    'hitlevel': 'int',
    'cancel_idx': 'positive_index',
    'transition': 'short',
    'anim_max_len': 'int',
    'hit_condition_idx': 'positive_index',
    'voiceclip_idx': 'index',
    'extra_properties_idx': 'index',
    'hitbox_location': 'hex',
    'first_active_frame': 'int',
    'last_active_frame': 'int',
    'u2': 'long',
    'u3': 'long',
    'u4': 'long',
    'u6': 'int',
    'u7': 'short',
    'u8': 'short',
    'u8_2': 'short',
    'u9': 'int',
    'u10': 'int',
    'u11': 'int',
    'u12': 'int',
    'u15': 'int',
    'u16': 'short',
    'u18': 'short',
    'u17': 'int'
}

cancelFields = {
    'command': '8b_hex',
    'extradata_idx': 'positive_index',
    'requirement_idx': 'positive_index',
    'frame_window_start': 'int',
    'frame_window_end': 'int',
    'starting_frame': 'int',
    'move_id': 'short',
    'cancel_option': 'short'
}

requirementFields = {
    'req': 'int',
    'param': 'int'
}

extrapropFields = {
    'type': 'int',
    'id': 'hex',
    'value': 'int'
}

hitConditionFields = {
    'requirement_idx': 'positive_index',
    'damage': 'int',
    'reaction_list_idx': 'positive_index'
}

reactionlistExtraPushbackFields = [
    'front_pushback',
    'back_pushback',
    'left_side_pushback',
    'right_side_pushback',
    'front_ch_pushback',
    'downed_pushback',
    'block_pushback'
]

reactionlistExtraLaunchFields = [
    'front_direction',
    'back_direction',
    'left_side_direction',
    'right_side_direction',
    'front_ch_direction',
    'downed_direction'
]

reactionlistFields = {
    'vertical_pushback': 'int',
    'standing': 'short',
    'ch': 'short',
    'crouch': 'short',
    'crouch_ch': 'short',
    'left_side': 'short',
    'left_side_crouch': 'short',
    'right_side': 'short',
    'right_side_crouch': 'short',
    'back': 'short',
    'back_crouch': 'short',
    'block': 'short',
    'crouch_block': 'short',
    'wallslump': 'short',
    'downed': 'short',
    'front_pushback': 'positive_index',
    'back_pushback': 'positive_index',
    'left_side_pushback': 'positive_index',
    'right_side_pushback': 'positive_index',
    'front_ch_pushback': 'positive_index',
    'downed_pushback': 'positive_index',
    'block_pushback': 'positive_index',
    'front_direction': 'short',
    'back_direction': 'short',
    'left_side_direction': 'short',
    'right_side_direction': 'short',
    'front_ch_direction': 'short',
    'downed_direction': 'short'
}

pushbackFields = {
    'val1': 'short',
    'val2': 'short',
    'val3': 'int',
    'pushbackextra_idx': 'positive_index'
}

pushbackExtradataFields = {
    'value': 'short',
}

cancelExtradataFields = {
    'value': 'int',
}

voiceclipFields = {
    'value': 'int',
}

fieldsTypes = {
    'moves': moveFields,
    'cancels': cancelFields,
    'group_cancels': cancelFields,
    'requirements': requirementFields,
    'extra_move_properties': extrapropFields,
    'hit_conditions': hitConditionFields,
    'reaction_list': reactionlistFields,
    'pushbacks': pushbackFields,
    'pushback_extras': pushbackExtradataFields,
    'cancel_extradata': cancelExtradataFields,
    'voiceclips': voiceclipFields,
}

folderNameOrder = [
    't7',
    '7',
    'tag2',
    '2',
    'rev',
    't6',
    't5',
    't5dr',
    't4'
]

def groupByPrefix(strings):
    stringsByPrefix = {}
    for string in strings:
        if '_' in string:
            prefix, suffix = map(str.strip, string.split("_", 1))
        else:
            prefix, suffix = '', string
        group = stringsByPrefix.setdefault(prefix, [])
        group.append(string)
    return stringsByPrefix
    
def getCharacterList():
    if not os.path.isdir(charactersPath):
        return []
    folders = [folder for folder in os.listdir(charactersPath) if os.path.isdir(charactersPath + folder)]
    folders = sorted(folders)
    
    sortedStringList = []
    
    groupedStrings = groupByPrefix(folders)
    keyList = sorted(groupedStrings.keys(), reverse=True)
    
    for key in folderNameOrder:
        if key in groupedStrings:
            for string in groupedStrings[key]: sortedStringList.append(string)
            del groupedStrings[key]
    
    for key in groupedStrings:
        for string in groupedStrings[key]: sortedStringList.append(string)
    
    return sortedStringList
    
def getMovelist(path):
    jsonFilename = next(file for file in os.listdir(path) if file.endswith(".json"))
    with open('%s/%s' % (path, jsonFilename)) as f:
        return json.load(f), jsonFilename
        
def sortKeys(keys):
    keyList = [key for key in keys if not re.match("^u[0-9_]+$", key)]
    unknownKeys = [key for key in keys if re.match("^u[0-9_]+$", key)]
    return keyList + unknownKeys
        
def validateField(type, value):
    if type == 'short' or type == 'int' or type == 'long' or type == 'positive_index':
        return re.match("^[0-9]+$", value)
    if type == 'index':
        return value == '-1' or re.match("^[0-9]+$", value)
    if type == 'hex' or type == '8b_hex':
        return re.match("^0(x|X)[0-9A-Fa-f]+$", value)
    if type == 'text':
        return re.match("^[a-zA-Z0-9_\-\(\)]+$", value)
    raise Exception("Unknown type '%s'" % (type))
    
def getFieldValue(type, value):
    if type == 'short':
        return ctypes.c_ushort(int(value)).value
    if type == 'int':
        return ctypes.c_uint(int(value)).value
    if type == 'long':
        return ctypes.c_ulong(int(value)).value
    if type == 'hex':
        return ctypes.c_uint(int(value, 16)).value
    if type == '8b_hex':
        return ctypes.c_ulonglong(int(value, 16)).value
    if type == 'index' or type == 'positive_index':
        return int(value)
    if type == 'text':
        return str(value)
    raise Exception("Unknown type '%s'" % (type))
    
def formatFieldValue(type, value):
    if type == 'short' or type == 'int' or type == 'long':
        return str(value)
    if type == 'hex' or type == '8b_hex':
        return "0x%x" % (value)
    if type == 'text' or type == 'index' or type == 'positive_index':
        return str(value)
    raise Exception("Unknown type '%s'" % (type))

def calculateHash(movesetData):
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
    
def getCommandStr(commandBytes):
    inputs = ""
    direction = ""
    
    inputBits = commandBytes >> 32
    directionBits = commandBytes & 0xffffffff

    for i in range(1, 5):
        if inputBits & (1 << (i - 1)):
            inputs += "+%d" % (i)
    
    
    if directionBits in commandLabels:
        direction = '(%s)' % commandLabels[directionBits]
    elif 32781 <= directionBits <= 36863:
        direction = " input_sequence[%d]" % (directionBits - 32781)
    else:
        direction = {
            (0): "",
            (1 << 1): "D/B",
            (1 << 2): "D",
            (1 << 3): "D/F",
            (1 << 4): "B",
            (1 << 6): "F",
            (1 << 7): "U/B",
            (1 << 8): "U",
            (1 << 9): "U/F",
            (1 << 15): "[AUTO]",
            (32769): " Double tap F",
            (32770): " Double tap B",
            (32771): " Double tap U",
            (32772): " Double tap D",
        }.get(directionBits, "UNKNOWN")
    
        
    if direction == "" and inputs != "":
        return inputs[1:]
    return direction + inputs

def getMoveColor(moveId, move, aliases):            
    if moveId in aliases:
        return '#b5caff'
    if move['hitlevel'] == 4195602:
        return 'violet'
    if move['hitlevel'] and move['hitbox_location'] and move['first_active_frame'] and move['last_active_frame']:
        return '#ffbdbd'
    if move['hitlevel'] or move['hitbox_location'] or move['first_active_frame'] or move['last_active_frame']:
        return '#ffe7e6'
    return None
        
class CharalistSelector:
    def __init__(self, root, rootFrame):
        self.root = root
        charalistFrame = Frame(rootFrame)
        charalistFrame.pack(side='left', fill='y')
        
        charaSelect = Listbox(charalistFrame)
        charaSelect.bind('<<ListboxSelect>>', self.onCharaSelectionChange)
        charaSelect.pack(fill='both', expand=1)
        
        buttons = [
            ("Select Moveset", self.selectMoveset)
        ]
        
        for label, callback in buttons:
            newButton = Button(charalistFrame, text=label, command=callback)
            newButton.pack(fill='x')
        
        self.charaSelect = charaSelect
        self.frame = charalistFrame
        
        self.characterList = []
        self.selection = None
        self.filename = None
        self.selectionIndex = -1
        self.last_selection = None
        self.movelist_path = None
        self.visible = True
        
    def toggleVisibility(self):
        if self.visible:
            self.hide()
        else:
            self.show()
       
    def hide(self):
        self.frame.pack_forget()
        self.visible = False
       
    def show(self):
        self.root.MoveSelector.hide()
        self.frame.pack(side='left', fill='y')
        self.root.MoveSelector.show()
        self.visible = True
        
    def colorCharacterList(self):
        colors = [
            ["#fff", "#eee"], #TTT2
            ["#eee", "#ddd"]  #T7
        ]
        for i, character in enumerate(self.characterList):
            color = colors[character.startswith("7_")][i & 1]
            self.charaSelect.itemconfig(i, {'bg': color, 'fg': 'black'})
    
        
    def updateCharacterlist(self):
        self.selection = None
        self.charaSelect.delete(0, 'end')
        
        characterList = getCharacterList()
        if len(characterList) == 0:
            self.charaSelect.insert(0, "No moveset...")
        else:
            for character in characterList: self.charaSelect.insert('end', character)
        self.characterList = characterList
        self.colorCharacterList()

    def onCharaSelectionChange(self, event):
        if len(self.characterList) == 0:
            return
        w = event.widget
        try:
            index = int(w.curselection()[0])
            self.selection = w.get(index)
            self.selectionIndex = int(index)
        except:
            self.selection = None
            self.selectionIndex = -1
        
    def loadToPlayer(self, playerId):
        if self.movelist_path == None:
            return
        playerAddr = game_addresses.addr['t7_p1_addr'] + (playerId * game_addresses.addr['t7_playerstruct_size'])
        TekkenImporter = importLib.Importer()
        TekkenImporter.importMoveset(playerAddr, self.movelist_path, moveset=self.root.movelist, charactersPath=charactersPath)
        
    def selectMoveset(self, selection=None):
        selection = self.selection if selection == None else selection
        
        if selection == None:
            selection = self.last_selection
            if selection == None:
                return
        else:
            self.colorCharacterList()
            self.charaSelect.itemconfig(self.selectionIndex, {'bg': '#a126c7', 'fg': 'white'})
            
        self.movelist_path = charactersPath + selection
        movelist, filename = getMovelist(self.movelist_path)
        self.filename = filename
        self.last_selection = selection
        
        self.root.MoveSelector.setMoves(movelist['moves'], movelist['aliases'])
        self.root.MoveSelector.setCharacter(movelist['character_name'])
        self.root.movelist = movelist
        self.root.resetForms()
        
        self.hide()
        if movelist['version'] != 'Tekken7':
            messagebox.showwarning('Warning', 'Modifying non-Tekken 7 movesets works, but is not recommended.\nLoad the moveset in Tekken 7 and export it to convert it to the Tekken7 format.\nRequirement and extra-move property will be differents otherwise.')
        
class MoveSelector:
    def __init__(self, root, rootFrame):
        self.root = root
        movelistFrame = Frame(rootFrame)
        movelistFrame.pack(side='left', fill='y')
        
        bottomButtons = [
            ('Save to file', self.root.save),
            ('Go to 2P move ID', lambda self=self: self.goToCurrentMove(1)),
            ('Go to 1P move ID', self.goToCurrentMove)
        ]
        
        for label, callback in bottomButtons:
            newButton = Button(movelistFrame, text=label, command=callback)
            newButton.pack(side='bottom', fill='x')
        
        selectedChar = Label(movelistFrame, text="No character selected", bg='#bbb')
        selectedChar.pack(side='bottom', fill='x')
        
        
        playMoveFrame = Frame(movelistFrame)
        playMoveFrame.pack(side='bottom', fill='x')
        
            
        sv = StringVar()
        sv.trace("w", lambda name, index, mode, sv=sv: self.onMoveidChange(sv))
        playMoveField = Entry(playMoveFrame, textvariable=sv)
        playMoveField.pack(side='left')
        
        playMoveButton = Button(playMoveFrame, text="Play move (1P)", command=self.playMove, state="disabled")
        playMoveButton.pack(side='right')
        
        
        movelistSelect = Listbox(movelistFrame, width=30)
        movelistSelect.bind('<<ListboxSelect>>', self.onMoveSelection)
        movelistSelect.pack(side='left', fill='both')
        
        scrollbar = Scrollbar(movelistFrame, command=movelistSelect.yview)
        scrollbar.pack(side='right', fill='y')
        
        movelistSelect.config(yscrollcommand=scrollbar.set)
        
        self.playMoveId = 0
        self.frame = movelistFrame
        self.selectedChar = selectedChar
        self.movelistSelect = movelistSelect
        
        self.playMoveSv = sv
        self.playMoveButton = playMoveButton
        self.playMovePid = 0
        
    def onMoveidChange(self, value):
        if self.root.movelist == None:
            return
            
        value = value.get()
        if re.match("[0-9]+", value):
            moveId = int(value)
            
            if moveId >= 0 and moveId < len(self.root.movelist['moves']):
                self.playMoveId = moveId
                self.playMoveButton.configure(state="enabled")
                return
        
        self.playMoveButton.configure(state="disabled")
        
    def playMove(self):
        if self.root.movelist == None:
            return
        T = importLib.Importer()
        
        playerAddr = game_addresses.addr['t7_p1_addr'] + (self.playMovePid * game_addresses.addr['t7_playerstruct_size'])
        motbinOffset = game_addresses.addr['t7_motbin_offset']
        curr_frame_timer_offset = game_addresses.addr['curr_frame_timer_offset']
        next_move_offset = game_addresses.addr['next_move_offset']
        
        moveset = T.readInt(playerAddr + motbinOffset, 8)
        movelist = T.readInt(moveset + 0x210, 8)
        
        moveAddr = movelist + (self.playMoveId * 0xB0)
        T.writeInt(playerAddr + curr_frame_timer_offset, 99999, 4)
        T.writeInt(playerAddr + next_move_offset, moveAddr, 8)
            
       
    def hide(self):
        self.frame.pack_forget()
       
    def show(self):
        self.frame.pack(side='left', fill='y')
        
    def onMoveSelection(self, event):
        w = event.widget
        moveId = -1
        try:
            moveId = int(w.curselection()[0])
        except:
            pass
        finally:
            self.playMoveSv.set(str(moveId))
            self.root.setMove(moveId)
            
    def goToCurrentMove(self, playerId = 0):
        if self.root.movelist == None:
            return
            
        self.playMovePid = playerId
        self.playMoveButton['text'] = "Play move (%dP)" % (playerId + 1)
        playerAddress = game_addresses.addr['t7_p1_addr'] + (playerId * game_addresses.addr['t7_playerstruct_size'])
        offset = game_addresses.addr['player_curr_move_offset']
        TekkenGame = GameClass("TekkenGame-Win64-Shipping.exe")
        
        currMoveId = TekkenGame.readInt(playerAddress + offset, 4)
        currMoveId = self.root.getMoveId(currMoveId)
        
        if currMoveId >= len(self.root.movelist['moves']):
            return
        
        self.root.setMove(currMoveId)
        
    def setCharacter(self, char):
        self.selectedChar['text'] = 'Current character: ' + char
        self.root.setTitle(char)
        
    def setMoves(self, moves, aliases):
        moves = [(i, move) for i, move in enumerate(moves)]
        self.movelistSelect.delete(0,'end')
        for moveId, move in moves:
            text = "%d   %s" % (moveId, move['name'])
            bg = getMoveColor(moveId, move, aliases)
            
            if moveId in aliases:
                text += "   (%d)" % (32768 + aliases.index(moveId))
                
            self.movelistSelect.insert('end', text)
            if bg != None:
                self.movelistSelect.itemconfig(moveId, {'bg': bg})
                
class FormEditor:
    def __init__(self, root, rootFrame, key, col, row):
        self.key = key
        self.fieldTypes = fieldsTypes[key]
        self.root = root
        self.rootFrame = rootFrame
        self.id = None
        self.editMode = None
        self.fieldVar = {}
        self.fieldInput = {}
        self.fieldLabel = {}
        self.fieldValue = {}
        self.container = None
        self.lastValidLabel = None
        self.listSaveFunction = None
        self.navigatorLabel = None
        self.details = None
        
        self.initEditor(col, row)
        
    def initEditor(self, col, row):
        container = Frame(self.rootFrame)
        container.grid(row=row, column=col, sticky="nsew")
        container.pack_propagate(False)
        
        label = Label(container, bg='#ddd')
        label.pack(side='top', fill='x')
        
        content = Frame(container)
        content.pack(side='top', fill='both', expand=True)
        
        saveButton = Button(container, text="Apply", command=self.save)
        saveButton.pack(side='bottom', fill='x')
        
        self.container = content
        self.label = label
        self.saveButton = saveButton
        
    def setLabel(self, text, saveLabel=True):
        self.label['text'] = text
        if saveLabel:
            self.lastValidLabel = text
           
    def enableSaveButton(self):
        self.saveButton['style'] = 'Bold.TButton'
        self.saveButton.config(state='enabled')
           
    def disableSaveButton(self):
        self.saveButton['style'] = 'TButton'
        self.saveButton.config(state='disabled')
    
    def onchange(self, field, sv):
        if self.editMode == None:
            return
        self.enableSaveButton()
        value = sv.get()
        valueType = self.fieldTypes[field]
        
        if validateField(valueType, value):
            self.fieldValue[field] =  getFieldValue(valueType, value)
            self.setLabel(self.lastValidLabel, False)
        else:
            self.setLabel("Invalid field: " + field, False)
            self.disableSaveButton()
        
        self.setField(field, value)
        
    def setListOnsaveFunction(self, function):
        self.listSaveFunction = function
        
    def save(self):
        if self.editMode == None:
            return False
            
        for field in self.fieldVar:
            valueType = self.fieldTypes[field]
            value = self.fieldVar[field].get()
            if validateField(valueType, value):
                fieldValue = getFieldValue(valueType, value)
                self.root.saveField(self.key, self.id, field, fieldValue)
                self.setField(field, fieldValue, setFieldValue=True)
            else:
                print("Invalid field value for '%s'" % (field))
                
        if self.listSaveFunction != None:
            index = self.listIndex
            self.listSaveFunction(self.baseId)
            self.setItem(index)
            
        self.disableSaveButton()
            
        return True
        
    def setField(self, field, value, setFieldValue=False):
        self.editMode = None
        
        if field not in self.fieldValue or setFieldValue:
            valueType = self.fieldTypes[field]
            self.fieldVar[field].set(formatFieldValue(valueType, value))
            self.fieldValue[field] = value
        else:
            self.fieldVar[field].set(value)
            
        self.editMode = True
        
    def resetForm(self):
        self.disableSaveButton()
        self.editMode = None
        self.id = None
        itemName = itemNames[self.key]
        self.setLabel("No %s selected" % (itemName))
        self.fieldValue = {}
        for field in self.fieldTypes.keys():
            if field in self.fieldVar:
                self.fieldVar[field].set('')
                self.fieldInput[field].config(state='disabled')
                
        if self.navigatorLabel != None:
            self.navigatorLabel['text'] = ""
        if self.details != None:
            self.details['text'] = ''
        
    def setItemList(self, itemList, itemId):
        self.id = itemId
        self.baseId = itemId
        self.itemList = itemList
        self.listIndex = 0
        
        self.setItem(0)
        self.disableSaveButton()
        
    def navigateToItem(self, offset):
        if self.editMode == None:
            return
        if offset == -1:
            offset = len(self.itemList) + offset
        if offset < 0 or offset >= len(self.itemList):
            return
        self.disableSaveButton()
        self.setItem(offset)
        
    def navigateFromItem(self, offset):
        if self.editMode != None and (self.listIndex + offset) >= 0:
            self.navigateToItem(self.listIndex + offset)
        
    def enableNavigator(self, itemLabel):
        navigatorFrame = Frame(self.container)
        navigatorFrame.pack(side='bottom', fill='x', expand=False)
       
        navigatorLabel = Label(navigatorFrame)
        navigatorLabel.pack(side='top')
        
        buttonsFrame = Frame(navigatorFrame)
        buttonsFrame.pack(side='bottom', fill='x', expand=False)

        buttonsFrame.grid_rowconfigure(0, weight=1)
        for i in range(4):
            buttonsFrame.grid_columnconfigure(i, weight=1)
        
        prevButton = Button(buttonsFrame, text="< Prev", command=lambda : self.navigateFromItem(-1))
        prevButton.grid(row=0, column=0)
        
        nextButton = Button(buttonsFrame, text="Next >", command=lambda : self.navigateFromItem(1))
        nextButton.grid(row=0, column=1)
        
        firstButton = Button(buttonsFrame, text="First", command=lambda : self.navigateToItem(0))
        firstButton.grid(row=0, column=2)
        
        lastButton = Button(buttonsFrame, text="Last", command=lambda : self.navigateToItem(-1))
        lastButton.grid(row=0, column=3)
        
        self.navigatorLabel = navigatorLabel
        
    def initFields(self):
        fields = sortKeys(self.fieldTypes.keys())
        
        for field in fields:
            container = Frame(self.container)
            container.pack(side='top', anchor='n', fill='both')

            fieldLabel = Label(container, text=fieldLabels.get(field, field), width=15)
            fieldLabel.grid(row=0, column=0, pady=2, sticky='w')
            
            sv = StringVar()
            sv.trace("w", lambda name, index, mode, field=field, sv=sv: self.onchange(field, sv))

            fieldInput = Entry(container, textvariable=sv)
            fieldInput.grid(row=0, column=1, sticky='ew')
            
            self.fieldVar[field] = sv
            self.fieldInput[field] = fieldInput
            self.fieldLabel[field] = fieldLabel
            
    def registerFieldButtons(self, items):
        for field, function in items:
            self.fieldLabel[field].config(cursor='hand2', bg='#cce3e1')
            self.fieldLabel[field].bind("<Button-1>", lambda _, self=self, field=field, function=function : function(self.fieldValue[field]) if self.editMode != None else 0 )
            
    def enableDetailsArea(self):
        details = Label(self.container)
        details.pack(side='bottom', fill='x', padx=0, pady=0)
        self.details = details
            
class HitConditionEditor(FormEditor):
    def __init__(self, root, rootFrame, col, row):
        FormEditor.__init__(self, root, rootFrame, 'hit_conditions', col, row)
        self.setListOnsaveFunction(self.root.setConditionList)
        self.enableNavigator(itemLabel='Condition')
        
        self.initFields()
        
        self.registerFieldButtons([
            ('requirement_idx', self.root.setRequirementList),
            ('reaction_list_idx', self.root.setReactionList),
        ])
            
    def setItem(self, index):
        hitconditionData = self.itemList[index]
        self.listIndex = index
        self.id = self.baseId + index
        
        hitConditionCount = len(self.itemList)
        
        propCount = " %d conditions" % (hitConditionCount) if hitConditionCount > 1 else "1 condition" 
        self.setLabel("Hit conditions list %d: %s" % (self.baseId, propCount))
        
        self.navigatorLabel['text'] = "Condition %d/%d" % (index + 1, hitConditionCount)
        
        self.editMode = None
        for field in hitconditionData:
            if field in hitConditionFields:
                self.setField(field, hitconditionData[field], True)
                self.fieldInput[field].config(state='enabled')
        self.editMode = True
        
        reactionlistId = self.fieldValue['reaction_list_idx']
        self.disableSaveButton()
            
class VoiceclipEditor(FormEditor):
    def __init__(self, root, rootFrame, col, row):
        FormEditor.__init__(self, root, rootFrame, 'voiceclips', col, row)
        
        self.initFields()
            
    def setItem(self, itemData, itemId):
        self.id = itemId
        self.setLabel("Voiceclip %d" % (itemId))
        
        self.editMode = None
        self.fieldInput['value'].config(state='enabled')
        self.setField('value', itemData, True)
        self.editMode = True
        self.disableSaveButton()
        
    def save(self):
        if self.editMode == True and validateField('int', self.fieldVar['value'].get()):
            self.root.saveField(self.key, self.id, None, getFieldValue('int', self.fieldVar['value'].get()))
            self.disableSaveButton()
            
class CancelExtraEditor(FormEditor):
    def __init__(self, root, rootFrame, col, row):
        FormEditor.__init__(self, root, rootFrame, 'cancel_extradata', col, row)
        
        self.initFields()
            
    def setItem(self, itemData, itemId):
        self.id = itemId
        self.setLabel("Cancel-extradata %d" % (itemId))
        
        self.editMode = None
        self.fieldInput['value'].config(state='enabled')
        self.setField('value', itemData, True)
        self.editMode = True
        self.disableSaveButton()
        
    def save(self):
        if self.editMode == True and validateField('int', self.fieldVar['value'].get()):
            self.root.saveField(self.key, self.id, None, getFieldValue('int', self.fieldVar['value'].get()))
            self.disableSaveButton()
            
class PushbackExtraEditor(FormEditor):
    def __init__(self, root, rootFrame, col, row):
        FormEditor.__init__(self, root, rootFrame, 'pushback_extras', col, row)
        
        self.initFields()
            
    def setItem(self, itemData, itemId):
        self.id = itemId
        self.setLabel("Pushback-extradata %d" % (itemId))
        
        self.editMode = None
        self.fieldInput['value'].config(state='enabled')
        self.setField('value', itemData, True)
        self.editMode = True
        self.disableSaveButton()
        
    def save(self):
        if self.editMode == True and validateField('short', self.fieldVar['value'].get()):
            self.root.saveField(self.key, self.id, None, getFieldValue('short', self.fieldVar['value'].get()))
            self.disableSaveButton()
            
class PushbackEditor(FormEditor):
    def __init__(self, root, rootFrame, col, row):
        FormEditor.__init__(self, root, rootFrame, 'pushbacks', col, row)
        
        self.initFields()
        
        self.registerFieldButtons([
            ('pushbackextra_idx', self.root.setPushbackExtra),
        ])
            
    def setItem(self, itemData, itemId):
        self.id = itemId
        self.setLabel("Pushback %d" % (itemId))
        
        self.editMode = None
        for field in pushbackFields:
            self.fieldInput[field].config(state='enabled')
            if field in itemData:
                self.setField(field, itemData[field], True)
            
        self.editMode = True
        self.disableSaveButton()
            
class ReactionListEditor(FormEditor):
    def __init__(self, root, rootFrame, col, row):
        FormEditor.__init__(self, root, rootFrame, 'reaction_list', col, row)
        
        self.westernFrame = Frame(self.container)
        self.westernFrame.pack(side='left', fill='both', expand=True)
        
        self.easternFrame = Frame(self.container)
        self.easternFrame.pack(side='right', fill='both', expand=True)
        
        
        self.initFields()
        
        self.registerFieldButtons([
            *[(f, self.root.setPushback) for f in self.fieldTypes if f in reactionlistExtraPushbackFields]
        ])
        
    def save(self):
        if super().save():
            pushbackFields = reactionlistExtraPushbackFields
            invalidFields = [f for f in pushbackFields if not validateField('index', self.fieldVar[f].get())]

            if len(invalidFields) == 0:
                pushbackFields = [getFieldValue('index', self.fieldVar[f].get()) for f in pushbackFields]
                self.root.saveField(self.key, self.id, 'pushback_indexes', pushbackFields)
            
            launchFields = reactionlistExtraLaunchFields
            invalidFields = [f for f in launchFields if not validateField('short', self.fieldVar[f].get())]

            if len(invalidFields) == 0:
                launchFields = [getFieldValue('short', self.fieldVar[f].get()) for f in launchFields]
                self.root.saveField(self.key, self.id, 'u1list', launchFields)
            
    def setItem(self, itemData, itemId):
        self.id = itemId
        self.setLabel("Reaction list %d: Pushback & Move IDs" % (itemId))
        
        self.editMode = None
        for field in reactionlistFields:
            self.fieldInput[field].config(state='enabled')
            if field in itemData:
                self.setField(field, itemData[field], True)
                
        for i, val in enumerate(itemData['pushback_indexes']):
            self.setField(reactionlistExtraPushbackFields[i], val, True)
        for i, val in enumerate(itemData['u1list']):
            self.setField(reactionlistExtraLaunchFields[i], val, True)
            
        self.editMode = True
        self.disableSaveButton()

    def initFields(self):
        fields = sortKeys(reactionlistFields.keys())
        sideBreakpoint = len(fields) / 2
        
        for i, field in enumerate(fields):
            container = Frame(self.westernFrame if i < sideBreakpoint else self.easternFrame)
            container.pack(side='top', anchor='n', fill='both')

            fieldLabel = Label(container, text=fieldLabels.get(field, field), width=15)
            fieldLabel.grid(row=0, column=0, sticky='w')
            
            sv = StringVar()
            sv.trace("w", lambda name, index, mode, field=field, sv=sv: self.onchange(field, sv))

            fieldInput = Entry(container, textvariable=sv)
            fieldInput.grid(row=0, column=1, sticky='ew')
                
            
            self.fieldVar[field] = sv
            self.fieldInput[field] = fieldInput
            self.fieldLabel[field] = fieldLabel
            
class ExtrapropEditor(FormEditor):
    def __init__(self, root, rootFrame, col, row):
        FormEditor.__init__(self, root, rootFrame, 'extra_move_properties', col, row)
        self.setListOnsaveFunction(self.root.setExtrapropList)
        self.enableNavigator(itemLabel='Prop')
        self.enableDetailsArea()
        
        self.initFields()
        
    def onchange(self, field, sv):
        if self.editMode == None:
            return
        super().onchange(field, sv)
        self.setDetails()
        
    def setDetails(self):
        if self.root.movelist['version'] != 'Tekken7':
            return

        reqId = self.fieldValue['id']
        description = getDetails(reqId, 'extra_move_properties')
        
        text = '(INSTANT) ' if self.fieldValue['type'] == 32769 else ''
        
        if description != None:
            text += '%x: %s' % (reqId, description)

        self.details['text'] = text
            
    def setItem(self, index):
        propertyData = self.itemList[index]
        self.listIndex = index
        self.id = self.baseId + index
        
        propertyCount = len(self.itemList)
        
        propCount = " %d properties" % (propertyCount) if propertyCount > 1 else "1 property" 
        self.setLabel("Move property list %d: %s" % (self.baseId, propCount))
        
        self.navigatorLabel['text'] = "Property %d/%d" % (index + 1, propertyCount)
        
        self.editMode = None
        for field in propertyData:
            if field in extrapropFields:
                self.setField(field, propertyData[field], True)
                self.fieldInput[field].config(state='enabled')
        self.editMode = True
        
        self.setDetails()
        self.disableSaveButton()
            
class RequirementEditor(FormEditor):
    def __init__(self, root, rootFrame, col, row):
        FormEditor.__init__(self, root, rootFrame, 'requirements', col, row)
        self.setListOnsaveFunction(self.root.setRequirementList)
        self.enableNavigator(itemLabel='Req')
        self.enableDetailsArea()
        
        self.initFields()
        
    def setDetails(self):
        if self.root.movelist['version'] != 'Tekken7':
            return

        reqId = self.fieldValue['req']
        prefix = '%d' % (reqId)
        key = 'requirements'
        
        if reqId >= 0x8000: #extraprop
            key = 'extra_move_properties'
            prefix = '%d (prop %x)' % (reqId, reqId)
            
        description = getDetails(reqId, key)
        
        if description != None:
            text = prefix + ': ' + description
        else:
            text = '' if key == 'requirements' else prefix
            
        self.details['text'] = text
            
    def setItem(self, index):
        requirementData = self.itemList[index]
        self.listIndex = index
        self.id = self.baseId + index
        
        requirementsLen = len(self.itemList)
        
        reqCount = " %d requirements" % (requirementsLen) if requirementsLen > 1 else "1 requirement" 
        self.setLabel("Requirement list %d: %s" % (self.baseId, reqCount))
        
        self.navigatorLabel['text'] = "Requirement %d/%d" % (index + 1, requirementsLen)
        
        self.editMode = None
        for field in requirementData:
            if field in requirementFields:
                self.setField(field, requirementData[field], True)
                self.fieldInput[field].config(state='enabled')
        self.editMode = True
        
        self.setDetails()
        self.disableSaveButton()
            
class GroupCancelEditor(FormEditor):
    def __init__(self, root, rootFrame, col, row):
        FormEditor.__init__(self, root, rootFrame, 'group_cancels', col, row)
        self.setListOnsaveFunction(self.root.openGroupCancel)
        self.enableNavigator(itemLabel='Cancel')
        self.enableDetailsArea()
        
        self.initFields()
        
        self.registerFieldButtons([
            ('move_id', self.root.setMove),
            ('requirement_idx', self.root.setRequirementList),
            ('extradata_idx', self.root.setCancelExtra),
        ])
        
    def onchange(self, field, sv):
        if self.editMode == None:
            return
        super().onchange(field, sv)
        self.setMoveIdLabel()
        
    def setMoveIdLabel(self):
        command = self.fieldValue['command']
        moveId = self.fieldValue['move_id']
        
        moveName = self.root.getMoveName(moveId)
        if moveName != None:
            text =  "Command: " + getCommandStr(command) + "\nMove: " + moveName
            self.details['text'] = text
        else:
            self.details['text'] = 'Invalid move'
            
    def setItem(self, index):
        cancelData = self.itemList[index]
        self.listIndex = index
        self.id = self.baseId + index
        
        cancelLen = len(self.itemList)
        
        cancelCount = " %d cancels" % (cancelLen) if cancelLen > 1 else "1 cancel" 
        self.setLabel("Group Cancel-list %d: %s" % (self.baseId, cancelCount))
        
        self.navigatorLabel['text'] = "Cancel %d/%d" % (index + 1, cancelLen)
        
        self.editMode = None
        for field in cancelData:
            if field in cancelFields:
                self.setField(field, cancelData[field], True)
                self.fieldInput[field].config(state='enabled')
        self.editMode = True
        
        self.setMoveIdLabel()
        self.disableSaveButton()
            
class CancelEditor(FormEditor):
    def __init__(self, root, rootFrame, col, row):
        FormEditor.__init__(self, root, rootFrame, 'cancels', col, row)
        self.setListOnsaveFunction(self.root.setCancelList)
        self.enableNavigator(itemLabel='Cancel')
        self.enableDetailsArea()
        
        self.initFields()
        
        self.registerFieldButtons([
            ('move_id', self.onMoveClick),
            ('requirement_idx', self.root.setRequirementList),
            ('extradata_idx', self.root.setCancelExtra),
        ])
        
        self.setTitleFunction = None
        
    def onMoveClick(self, id):
        if self.fieldValue['command'] == 0x800b:
            self.root.openGroupCancel(id)
        else:
            self.root.setMove(id)
        
    def onchange(self, field, sv):
        if self.editMode == None:
            return
        super().onchange(field, sv)
        self.setMoveIdLabel()
        
    def setMoveIdLabel(self):
        command = self.fieldValue['command']
        moveId = self.fieldValue['move_id']
        
        if command == 0x800b:
            self.details['text'] = '(move_id) group_cancel ' + str(moveId)
        else:
            moveName = self.root.getMoveName(moveId)
            if moveName != None:
                text =  "Command: " + getCommandStr(command) + "\nMove: " + moveName
                self.details['text'] = text
            else:
                self.details['text'] = 'Invalid move'
            
    def setItem(self, index):
        cancelData = self.itemList[index]
        self.listIndex = index
        self.id = self.baseId + index
        
        cancelLen = len(self.itemList)
        
        cancelCount = " %d cancels" % (cancelLen) if cancelLen > 1 else "1 cancel" 
        self.setLabel("Cancel-list %d: %s" % (self.baseId, cancelCount))
        
        self.navigatorLabel['text'] = "Cancel %d/%d" % (index + 1, cancelLen)
        
        self.editMode = None
        for field in cancelData:
            if field in cancelFields:
                self.setField(field, cancelData[field], True)
                self.fieldInput[field].config(state='enabled')
        self.editMode = True
        
        self.setMoveIdLabel()
        self.disableSaveButton()
    
class MoveEditor(FormEditor):
    def __init__(self, root, rootFrame, col, row):
        FormEditor.__init__(self, root, rootFrame, 'moves', col, row)
        
        self.westernFrame = Frame(self.container)
        self.westernFrame.pack(side='left', fill='both', expand=True)
        
        self.easternFrame = Frame(self.container)
        self.easternFrame.pack(side='right', fill='both', expand=True)
        
        self.initFields()
        
        self.registerFieldButtons([
            ('cancel_idx', self.root.setCancelList),
            ('extra_properties_idx', self.root.setExtrapropList),
            ('voiceclip_idx', self.root.setVoiceclip),
            ('hit_condition_idx', self.root.setConditionList),
        ])
        

    def initFields(self):
        fields = sortKeys(moveFields.keys())
        sideBreakpoint = len(fields) / 2
        
        for i, field in enumerate(fields):
            container = Frame(self.westernFrame if i < sideBreakpoint else self.easternFrame)
            container.pack(side='top', anchor='n', fill='both')

            fieldLabel = Label(container, text=fieldLabels.get(field, field), width=15)
            fieldLabel.grid(row=0, column=0, sticky='w')
            
            sv = StringVar()
            sv.trace("w", lambda name, index, mode, field=field, sv=sv: self.onchange(field, sv))

            fieldInput = Entry(container, textvariable=sv)
            fieldInput.grid(row=0, column=1, sticky='ew')
                
            
            self.fieldVar[field] = sv
            self.fieldInput[field] = fieldInput
            self.fieldLabel[field] = fieldLabel
        
    def setMove(self, moveData, moveId):
        if moveId in self.root.movelist['aliases']:
            aliasValue = 32768 + self.root.movelist['aliases'].index(moveId)
            self.setLabel("Move %d: %s   (Aliased to: %d)" % (moveId, moveData['name'], aliasValue))
        else:
            self.setLabel("Move %d: %s" % (moveId, moveData['name']))
        self.id = moveId
            
        self.editMode = None
        for field in moveData:
            if field in moveFields:
                self.setField(field, moveData[field], True)
                self.fieldInput[field].config(state='enabled')
        self.editMode = True
        self.disableSaveButton()
        
    def selectCancel(self, event):
        if self.editMode == None:
            return
        self.root.setCancelList(self.fieldValue['cancel_idx'])
        
    def selectExtraprop(self, event):
        if self.editMode == None:
            return
        self.root.setExtrapropList(self.fieldValue['extra_properties_idx'])
        
def createGrid(root, split, bg=None):
    rowCount = 1 + (split == 'horizontal')
    colCount = 1 + (split == 'vertical')
    newFrame = Frame(root, bg=bg)
    
    for i in range(rowCount):
        newFrame.grid_rowconfigure(i, weight=1, uniform='group1' )
    for i in range(colCount):
        newFrame.grid_columnconfigure(i, weight=1, uniform='group1' )
    return newFrame
    
def splitFrame(root, split):
    rowCount = 1 + (split == 'horizontal')
    colCount = 1 + (split == 'vertical')
    
    for i in range(rowCount):
        root.grid_rowconfigure(i, weight=1, uniform='group1' )
    for i in range(colCount):
        root.grid_columnconfigure(i, weight=1, uniform='group1' )
        
    Frame1 = Frame(root)
    Frame1.grid(column=0, row=0, sticky='nsew')
    
    col, row = int(split == 'vertical'), int(split == 'horizontal')
    Frame2 = Frame(root)
    Frame2.grid(column=col, row=row, sticky='nsew')
    
    return Frame1, Frame2
    
def getCancelList(movelist, cancelId):
    id = cancelId
    while movelist['cancels'][id]['command'] != 0x8000:
        id += 1
    cancelList = [cancel for cancel in movelist['cancels'][cancelId:id + 1]]
    return cancelList
    
def getGroupCancelList(movelist, cancelId):
    id = cancelId
    while movelist['group_cancels'][id]['command'] != 0x800c:
        id += 1
    cancelList = [cancel for cancel in movelist['group_cancels'][cancelId:id + 1]]
    return cancelList
    
def getRequirementList(movelist, requirementId):
    id = requirementId
    endValue = reqListEndval[movelist['version']]
    while movelist['requirements'][id]['req'] != endValue:
        id += 1
    return [req for req in movelist['requirements'][requirementId:id + 1]]
    
def getExtrapropList(movelist, baseId):
    id = baseId
    while movelist['extra_move_properties'][id]['type'] != 0:
        id += 1
    return [prop for prop in movelist['extra_move_properties'][baseId:id + 1]]
    
def getHitConditionList(movelist, baseId):
    id = baseId
    endValue = reqListEndval[movelist['version']]
    while True:
        reqIdx = movelist['hit_conditions'][id]['requirement_idx'] 
        if movelist['requirements'][reqIdx]['req'] == endValue:
            break
        id += 1
    return  [item for item in movelist['hit_conditions'][baseId:id + 1]]
    
class MoveCopyingWindow:
    def __init__(self, root):
        window = Toplevel()
        self.window = window
        self.root = root
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        mainFrame = Frame(window)
        mainFrame.pack(fill='both', expand=1)
        for i in range(2):
            mainFrame.grid_columnconfigure(i, weight=1, uniform="group1")
        mainFrame.grid_rowconfigure(0, weight=1, uniform="group1")
        
        leftFrame, rightFrame = splitFrame(mainFrame, 'vertical')
        
        characterListFrame, movelistFrame = splitFrame(leftFrame, 'vertical')
        
        window.iconbitmap('InterfaceData/renge.ico')
        window.geometry("640x720")
        window.minsize(240, 340)
        self.setTitle("Copy move from movelist")
        
        selectCharacter = Button(characterListFrame, text='Select moveset')
        selectCharacter['command'] = self.loadCharacterMovelist
        selectCharacter.pack(side='bottom', fill='x')
        
        charaSelect = Listbox(characterListFrame)
        charaSelect.bind('<<ListboxSelect>>', self.onCharaSelectionChange)
        charaSelect.pack(side='left', expand=1, fill='both')
        
        scrollbar = Scrollbar(characterListFrame, command=charaSelect.yview)
        scrollbar.pack(side='right', fill='y')
        
        charaSelect.config(yscrollcommand=scrollbar.set)
        
        
        selectedChar = Label(movelistFrame, text="No character selected", bg='#bbb')
        selectedChar.pack(side='bottom', fill='x')
        
        movelistSelect = Listbox(movelistFrame)
        movelistSelect.bind('<<ListboxSelect>>', self.onMoveSelectionChange)
        movelistSelect.pack(side='left', expand=1, fill='both')
        
        scrollbar = Scrollbar(movelistFrame, command=movelistSelect.yview)
        scrollbar.pack(side='right', fill='y')
        
        movelistSelect.config(yscrollcommand=scrollbar.set)
        
        
        moveInfo = Label(rightFrame)
        moveInfo.pack()
        
        importMoveButton = Button(rightFrame, text="Import move", state="disabled")
        importMoveButton['command'] = self.importMove
        importMoveButton.pack()
        
        self.movelistSelect = movelistSelect
        self.charaSelect = charaSelect
        self.moveInfo = moveInfo
        self.importMoveButton = importMoveButton
        
        self.selectedChar = selectedChar
        self.characterList = []
        self.selection = None
        self.selectionIndex = -1
        self.last_selection = None
        self.movelist = None
        self.filename = ""
        self.selectedMoveIndex = -1
        
        self.updateCharacterlist()
        
    def loadCharacterMovelist(self):
        selection = self.selection
        if selection == None:
            if self.last_selection == None:
                return
            selection = self.last_selection
        else:
            self.charaSelect.itemconfig(self.selectionIndex, {'bg': '#a126c7', 'fg': 'white'})
            
        self.selectedChar['text'] = selection
        self.movelist_path = charactersPath + selection
        
        movelist, filename = getMovelist(self.movelist_path)
        self.last_selection = selection
        self.movelist = movelist
        self.filename = filename
        
        self.setMoves(movelist['moves'], movelist['aliases'])

    def setMoves(self, moves, aliases):
        moves = [(i, move) for i, move in enumerate(moves)]
        self.movelistSelect.delete(0,'end')
        
        for moveId, move in moves:
            text = "%d   %s" % (moveId, move['name'])
            
            if moveId in aliases:
                text += "   (%d)" % (32768 + aliases.index(moveId))
                
            self.movelistSelect.insert('end', text)
            moveColor = getMoveColor(moveId, move, aliases)
            if moveColor != None:
                self.movelistSelect.itemconfig(moveId, {'bg': moveColor})
                
    def setMove(self, moveId):
        self.importMoveButton['state'] = 'enabled'
        move = self.movelist['moves'][moveId]
        
        self.moveInfo['text'] = "Loading move %d..." % (moveId)
        
        moveText = "Move ID: %d" % (moveId)
        if moveId in self.movelist['aliases']:
            moveText += "  (%d)" % (self.movelist['aliases'].index(moveId) + 32768)
            
        moveText += "\nName: %s" % (move['name'])
        moveText += "\nAnimation: %s" % (move['anim_name'])
        
        print("Getting dependencies...")
        dependencies = self.getMoveDependencies(moveId)
        print("got dependencies...")
        
        moveText += "\n\nDependencies:"
        for category in dependencies:
            moveText += "\n%s: %d items." % (category, len(dependencies[category].keys()))
        
        self.moveInfo['text'] = moveText
        
    def getRequirements(self, requirementId, dependencies):
        if requirementId in dependencies['requirements']:
            return
        reqList = [c.copy() for c in getRequirementList(self.movelist, requirementId)]
        dependencies['requirements'][requirementId] = reqList
        
    def getExtraproperties(self, extraId, dependencies):
        if extraId == -1 or extraId in dependencies['extra_move_properties']:
            return
        dependencies['extra_move_properties'][extraId] = getExtrapropList(self.movelist, extraId)
        
    def getCancelExtra(self, extraId, dependencies):
        if extraId in dependencies['cancel_extradata']:
            return
        dependencies['cancel_extradata'][extraId] = self.movelist['cancel_extradata'][extraId]
        
    def getVoiceclip(self, id, dependencies):
        if id in dependencies['voiceclips']:
            return
        dependencies['voiceclips'][id] = self.movelist['voiceclips'][id]
        
    def getPushbackExtra(self, extraId, dependencies):
        if extraId in dependencies['pushback_extras']:
            return
        dependencies['pushback_extras'][extraId] = self.movelist['pushback_extras'][extraId]
        
    def getPushback(self, id, dependencies):
        if id in dependencies['pushbacks']:
            return
        dependencies['pushbacks'][id] = self.movelist['pushbacks'][id].copy()
        self.getPushbackExtra(dependencies['pushbacks'][id]['pushbackextra_idx'], dependencies)
        
    def getReactionList(self, id, dependencies):
        if id in dependencies['reaction_list']:
            return
        reactionList = self.movelist['reaction_list'][id].copy()
        dependencies['reaction_list'][id] = reactionList
        
        for pushback in reactionList['pushback_indexes']:
            self.getPushback(pushback, dependencies)
            
        moveKeys = (k for k in reactionList if k != 'vertical_pushback' and k != 'u1list' and k != 'pushback_indexes')
        for key in moveKeys:
            if reactionList[key] != 0:
                self.getMove(reactionList[key], dependencies)
            
    def getHitConditions(self, id, dependencies):
        if id in dependencies['hit_conditions']:
            return
        hitConditionList = [c.copy() for c in getHitConditionList(self.movelist, id)]
        dependencies['hit_conditions'][id] = hitConditionList
        
        for hitCondition in hitConditionList:
            self.getRequirements(hitCondition['requirement_idx'], dependencies)
            self.getReactionList(hitCondition['reaction_list_idx'], dependencies)
        
    def getGroupCancels(self, cancelId, dependencies, recursiveLevel):
        if cancelId in dependencies['group_cancels']:
            return
        cancelList = [c.copy() for c in getGroupCancelList(self.movelist, cancelId)]
        dependencies['group_cancels'][cancelId] = cancelList
        print("getGroupCancels", cancelId, recursiveLevel)
        
        for cancel in cancelList:
            self.getRequirements(cancel['requirement_idx'], dependencies)
            self.getCancelExtra(cancel['extradata_idx'], dependencies)
            if cancel['move_id'] < 0x8000:
                self.getMove(cancel['move_id'], dependencies, recursiveLevel + 1)
            
        print("getGroupCancelsEND")
        
    def getCancels(self, cancelId, dependencies, recursiveLevel):
        if cancelId in dependencies['cancels']:
            return
        print("getCancels", cancelId, recursiveLevel)
        
        cancelList = [c.copy() for c in getCancelList(self.movelist, cancelId)]
        dependencies['cancels'][cancelId] = cancelList
        
        for cancel in cancelList:
            print("cancelmove:", cancel['move_id'])
            self.getRequirements(cancel['requirement_idx'], dependencies)
            print("getRequirements")
            self.getCancelExtra(cancel['extradata_idx'], dependencies)
            print("getCancelExtra")
            if cancel['command'] == 0x800b:
                print("Getting group cancel")
                self.getGroupCancels(cancel['move_id'], dependencies, recursiveLevel + 1)
                print("Got group cancel")
            elif cancel['move_id'] < 0x8000:
                print("Getting move cancel")
                self.getMove(cancel['move_id'], dependencies, recursiveLevel + 1)
            print("Next item")
            
        print("getCancelsEND")
        
    def getMove(self, moveId, dependencies, recursiveLevel=0):
        if moveId in dependencies['moves']:
            return
            
        print("getMove", moveId, recursiveLevel)
        
        move = self.movelist['moves'][moveId].copy()
        dependencies['moves'][moveId] = move
        self.getExtraproperties(move['extra_properties_idx'], dependencies)
        self.getVoiceclip(move['voiceclip_idx'], dependencies)
        self.getCancels(move['cancel_idx'], dependencies, recursiveLevel)
        self.getHitConditions(move['hit_condition_idx'], dependencies)
        print("getMoveEND")
        
    def getMoveDependencies(self, moveId):
        dependencies = {
            'moves': {},
            'cancels': {},
            'group_cancels': {},
            'requirements': {},
            'extra_move_properties': {},
            'cancel_extradata': {},
            'hit_conditions': {},
            'reaction_list': {},
            'pushbacks': {},
            'pushback_extras': {},
            'voiceclips': {},
        }
        self.getMove(moveId, dependencies)
        return dependencies
        
    def importMove(self):
        dependencies = self.getMoveDependencies(self.selectedMoveIndex)
        idAliases = {
            'moves': {},
            'cancels': {},
            'group_cancels': {},
            'requirements': {},
            'extra_move_properties': {},
            'cancel_extradata': {},
            'hit_conditions': {},
            'reaction_list': {},
            'pushbacks': {},
            'pushback_extras': {},
            'voiceclips': {},
        }
        
        targetMovelist = self.root.movelist
        moveInsertionIndex = len(targetMovelist['moves'])
        
        for category in dependencies:
            for item in dependencies[category]:
                itemData = dependencies[category][item]
                insertionIndex = len(targetMovelist[category])
                
                idAliases[category][item] = insertionIndex
                
                if isinstance(itemData, list):
                    for newItem in itemData: targetMovelist[category].append(newItem)
                else:
                    targetMovelist[category].append(itemData)
                
        for moveId in dependencies['moves']:
            move = dependencies['moves'][moveId]
            move['cancel_idx'] = idAliases['cancels'].get(move['cancel_idx'], -1)
            move['extra_properties_idx'] = idAliases['extra_move_properties'].get(move['extra_properties_idx'], -1)
            move['voiceclip_idx'] = idAliases['voiceclips'].get(move['voiceclip_idx'], -1)
            move['hit_condition_idx'] = idAliases['hit_conditions'].get(move['hit_condition_idx'], -1)
            
            anim = move['anim_name']
            sourcePath = "%s/anim/%s.bin" % (self.movelist_path, anim)
            targetPath = "%s/anim/%s.bin" % (self.root.Charalist.movelist_path, anim)

            if not os.path.exists(targetPath):
                shutil.copyfile(sourcePath, targetPath)
                
        for cancelId in dependencies['cancels']:
            for cancel in dependencies['cancels'][cancelId]:
                cancel['requirement_idx'] = idAliases['requirements'].get(cancel['requirement_idx'], -1)
                cancel['extradata_idx'] = idAliases['cancel_extradata'].get(cancel['extradata_idx'], -1)
                if cancel['command'] != 0x800b:
                    cancel['move_id'] = idAliases['group_cancels'].get(cancel['move_id'], -1)
                elif cancel['move_id'] < 0x8000:
                    cancel['move_id'] = idAliases['moves'].get(cancel['move_id'], -1)
                
        for cancelId in dependencies['group_cancels']:
            for cancel in dependencies['group_cancels'][cancelId]:
                cancel['requirement_idx'] = idAliases['requirements'].get(cancel['requirement_idx'], -1)
                cancel['extradata_idx'] = idAliases['cancel_extradata'].get(cancel['extradata_idx'], -1)
                if cancel['move_id'] < 0x8000:
                    cancel['move_id'] = idAliases['moves'].get(cancel['move_id'], -1)
        
        for hitConditionId in dependencies['hit_conditions']:
            for hitCondition in dependencies['hit_conditions'][hitConditionId]:
                hitCondition['requirement_idx'] = idAliases['requirements'].get(hitCondition['requirement_idx'], -1)
                hitCondition['reaction_list_idx'] = idAliases['reaction_list'].get(hitCondition['reaction_list_idx'], -1)
        
        for reactionListId in dependencies['reaction_list']:
            reactionList = dependencies['reaction_list'][reactionListId]
            for i, pushback in enumerate(reactionList['pushback_indexes']):
                reactionList['pushback_indexes'][i] = idAliases['pushbacks'].get(pushback, -1)        
            moveKeys = (k for k in reactionList if k != 'vertical_pushback' and k != 'u1list' and k != 'pushback_indexes')
            for k in moveKeys:
                reactionList[k] = idAliases['moves'].get(reactionList[k], 0)
                
        for pushbackId in dependencies['pushbacks']:
            pushback = dependencies['pushbacks'][pushbackId]
            pushback['pushbackextra_idx'] = idAliases['pushback_extras'].get(pushback['pushbackextra_idx'], -1)    
        
        messagebox.showinfo('Imported', 'Data successfully imported')
        self.root.MoveSelector.setMoves(targetMovelist['moves'], self.root.movelist['aliases'])
        self.root.setMove(moveInsertionIndex)
        
    def onMoveSelectionChange(self, event):
        if self.movelist == None:
            return
        w = event.widget
        try:
            index = int(w.curselection()[0])
            self.selectedMoveIndex = int(index)
            self.setMove(self.selectedMoveIndex)
        except:
            self.selectedMoveIndex = -1
        
    def onCharaSelectionChange(self, event):
        if len(self.characterList) == 0:
            return
        w = event.widget
        try:
            index = int(w.curselection()[0])
            self.selection = w.get(index)
            self.selectionIndex = int(index)
        except:
            self.selection = None
            self.selectionIndex = -1
        
    def updateCharacterlist(self):
        self.charaSelect.delete(0, 'end')
        characterList = getCharacterList()
        if len(characterList) == 0:
            self.charaSelect.insert(0, "No moveset...")
        else:
            for character in characterList: self.charaSelect.insert('end', character)
            
        self.characterList = characterList
        self.colorCharacterList()
        
    def colorCharacterList(self):
        colors = [
            ["#fff", "#eee"], #TTT2
            ["#ddd", "#ddd"]  #T7
        ]
        
        colorPool = 0
        
        for i, character in enumerate(self.characterList):
            color = colors[colorPool][i & 1]
            self.charaSelect.itemconfig(i, {'bg': color, 'fg': 'black'})
            
    def setTitle(self, title):
        self.window.wm_title(title) 
        
    def on_close(self):
        self.root.MoveCopyingWindow = None
        self.window.destroy()
        self.window.update()
    
class MoveReferenceWindow:
    def __init__(self, root, moveName, moveId, referenceList):
        window = Toplevel()
        self.window = window
        self.root = root
        
        window.iconbitmap('InterfaceData/renge.ico')
        window.geometry("500x500")
        window.minsize(800, 600)
        
        self.setTitle("Reference Finder: Move %s (%d) (%d entries)" % (moveName, moveId, len(referenceList)))
        self.printReferenceList(moveName, moveId, referenceList)
            
    def printReferenceList(self, moveName, moveId, referenceList):
        TextArea = Text(self.window, wrap="word")
        
        scrollbar = Scrollbar(self.window, command=TextArea.yview)
        scrollbar.pack(side='right', fill='y')
        
        TextArea.config(yscrollcommand=scrollbar.set)
        
        
        if len(referenceList) == 0:
            TextArea.insert("end", "No reference found for move %s (%d)" % (moveName, moveId))
        else:
            TextArea.insert("end", "%d entries for move %s (%d):\n\n" % (len(referenceList), moveName, moveId))
        
            for reference in referenceList:
                referenceText = "Type: %s" % (reference['origin'])
            
                if len(reference['references']) != 0:
                    referenceText = '\n' + referenceText
                
                if 'list_id' in reference:
                    referenceText += " | List ID: %d" % (reference['list_id'])
                    referenceText += " | Item ID: %d (list idx %d)" % (reference['item_id'], reference['item_id'] - reference['list_id'])
                else:
                    referenceText += " | Item ID: %d" % (reference['item_id'])
                    
                for ref in reference['references']:
                    referenceText += "\n- Referenced by: " + ref
                    
                if len(reference['references']) != 0:
                    referenceText += '\n'
                
                TextArea.insert("end", referenceText + "\n")
            TextArea.insert("end", "--- %d entries for move %s (%d) ---" % (len(referenceList), moveName, moveId))
        
        TextArea.configure(state="disabled")
        TextArea.pack(padx=10, pady=5, side='left', fill='both', expand=1)
            
    def setTitle(self, title):
        self.window.wm_title(title) 
    
class GroupCancelWindow:
    def __init__(self, root, id):
        window = Toplevel()
        self.window = window
        self.root = root
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        editorFrame = Frame(window)
        editorFrame.pack(fill='both', expand=1)
        editorFrame.grid_columnconfigure(0, weight=1, uniform="group1")
        editorFrame.grid_rowconfigure(0, weight=1, uniform="group1")
        
        window.iconbitmap('InterfaceData/renge.ico')
        window.geometry("240x340")
        window.minsize(240, 340)
        
        self.CancelEditor = GroupCancelEditor(root, editorFrame, col=0, row=0)
        self.CancelEditor.resetForm()
        
        creationMenu = [
            ("Insert new group-cancel to current list", self.root.insertNewGroupCancel),
            ("Create group-cancel list", self.root.createGroupCancelList),
            ("", "separator" ),
            ("Duplicate current group-cancel", lambda self=self: self.root.insertNewGroupCancel(copyCurrent=True) ),
            ("Duplicate current group-cancel list", self.root.copyGroupCancelList),
        ]
        
        deletionMenu = [
            ("Current group-cancel list", self.root.deleteCurrentGroupCancelList),
            ("Current group-cancel", self.root.deleteCurrentGroupCancel),
        ]
        
        menuActions = [
            ("New", creationMenu),
            ("Delete", deletionMenu)
        ]
        
        menu = createMenu(window, menuActions, validationFunc=self.root.canEditMoveset)
        window.config(menu=menu)
        
        self.setCancelList(id)
            
    def setTitle(self, title):
        self.window.wm_title(title) 
        
    def on_close(self):
        self.root.GroupCancelEditor = None
        self.window.destroy()
        self.window.update()
        
    def setCancelList(self, cancelId):
        if cancelId < 0 or cancelId >= len(self.root.movelist['group_cancels']):
            return
        cancelList = []
        id = cancelId
        while self.root.movelist['group_cancels'][id]['command'] != 0x800c:
            id += 1
        cancelList = [cancel for cancel in self.root.movelist['group_cancels'][cancelId:id + 1]]
        self.CancelEditor.setItemList(cancelList, cancelId)
        self.setTitle('Group %d' % (cancelId))
        
def createMenu(root, menuActions, validationFunc=None, rootMenu=True):
    newMenu = Menu(root, tearoff=0)
    for label, command in menuActions:
        if isinstance(command, list):
            subMenu = createMenu(newMenu, command, validationFunc=validationFunc, rootMenu=False)
            newMenu.add_cascade(label=label, menu=subMenu)
        elif command == "separator":
            if rootMenu:
                newMenu.add_command(label='|', state='disabled')
            else:
                newMenu.add_separator()
        elif command == None:
            newMenu.add_command(label=label, state="disabled")
        else:
            wrappedFunction = lambda validationFunc=validationFunc, command=command : command() if (validationFunc and validationFunc()) else None
            newMenu.add_command(label=label, command=wrappedFunction)
    return newMenu
        
class GUI_TekkenMovesetEditor():
    def __init__(self, mainWindow=True, showCharacterSelector=True):
        window = Tk() if mainWindow else Toplevel()
        self.window = window

        boldButtonStyle = Style()
        boldButtonStyle.configure("Bold.TButton", font = ('Sans','10','bold'))
        
        self.setTitle()
        window.iconbitmap('InterfaceData/renge.ico')
        window.minsize(960, 540)
        window.geometry("1280x770")
        
        self.Charalist = CharalistSelector(self, window)
        self.MoveSelector = MoveSelector(self, window)
        
        editorFrame = Frame(window)
        editorFrame.pack(side='right', fill='both', expand=1)
        for i in range(2):
            editorFrame.grid_columnconfigure(i, weight=1, uniform="group1")
            editorFrame.grid_rowconfigure(i, weight=1, uniform="group1")
            
        topRightFrame = createGrid(editorFrame, 'vertical')
        topRightFrame.grid(row=0, column=1, sticky="nsew")
            
        reqAndPropsFrame = createGrid(topRightFrame, split='horizontal')
        reqAndPropsFrame.grid(row=0, column=1, sticky="nsew")
        
        bottomLeftFrame = createGrid(editorFrame, 'vertical')
        bottomLeftFrame.grid(row=1, column=0, sticky="nsew")
        
        bottomLeftToprow = createGrid(bottomLeftFrame, 'horizontal')
        bottomLeftToprow.grid(row=0, column=0, sticky="nsew")
        
        bottomLeftToprow2 = createGrid(bottomLeftFrame, 'horizontal')
        bottomLeftToprow2.grid(row=0, column=1, sticky="nsew")
        
        bottomLeftToprow3 = createGrid(bottomLeftToprow, 'horizontal')
        bottomLeftToprow3.grid(row=1, column=0, sticky="nsew")
        
        
        self.MoveEditor = MoveEditor(self, editorFrame, col=0, row=0)
        self.CancelEditor = CancelEditor(self, topRightFrame, col=0, row=0)
        self.RequirementEditor = RequirementEditor(self, reqAndPropsFrame, col=0, row=0)
        self.ExtrapropEditor = ExtrapropEditor(self, reqAndPropsFrame, col=0, row=1)
        
        self.HitConditionEditor = HitConditionEditor(self, bottomLeftToprow2, col=0, row=0)
        self.PushbackExtraEditor = PushbackExtraEditor(self, bottomLeftToprow2, col=0, row=1)
        self.PushbackEditor = PushbackEditor(self, bottomLeftToprow, col=0, row=0)
        self.VoiceclipEditor = VoiceclipEditor(self, bottomLeftToprow3, col=0, row=1)
        self.CancelExtraEditor = CancelExtraEditor(self, bottomLeftToprow3, col=0, row=0)
        
        self.ReactionListEditor = ReactionListEditor(self, editorFrame, col=1, row=1)
        
        self.GroupCancelEditor = None
        self.MoveCopyingWindow = None
        
        moveCreationMenu = [
            ("Create new empty move", self.createMove ),
            ("Copy current move", lambda self=self: self.createMove(True)),
            ("Copy move from another moveset (BETA!!!)", self.openMoveCopyWindow ),
        ]
        
        extrapropCreationMenu = [
            ("Insert new extra move-prop to current list", self.insertNewExtraprop ),
            ("Create new extra move-prop list", self.createExtrapropList ),
            ("", "separator" ),
            ("Duplicate current extra move-prop", lambda self=self: self.insertNewExtraprop(copyCurrent=True) ),
            ("Duplicate current extra move-prop list", self.copyExtrapropList ),
        ]
        
        requirementCreationMenu = [
            ("Insert new requirement to current list", self.insertNewRequirement ),
            ("Create new requirement list", self.createRequirementList ),
            ("", "separator" ),
            ("Duplicate current requirement list", self.copyRequirementList ),
        ]
        
        cancelCreationMenu = [
            ("Insert new cancel to current list", self.insertNewCancel ),
            ("Create new cancel-list", self.createCancelList ),
            ("", "separator" ),
            ("Duplicate current cancel", lambda self=self: self.insertNewCancel(copyCurrent=True) ),
            ("Duplicate current cancel-list", self.copyCancelList ),
        ]
        
        hitconditionCreationMenu = [
            ("Insert new hit-condition to current list", self.insertNewHitCondition ),
            ("Create new hit-condition list", lambda self=self: self.copyHitconditionList(0) ),
            ("", "separator" ),
            ("Duplicate current hit-condition", lambda self=self: self.insertNewHitCondition(copyCurrent=True) ),
            ("Duplicate current hit-condition list", self.copyHitconditionList ),
        ]
        
        reactionListCreationMenu = [
            ("Create new reaction-list", self.createNewReactionlist),
            ("Duplicate current reaction-list", lambda self=self: self.createNewReactionlist(copyCurrent=True)  ),
        ]
        
        pushbackCreationMenu = [
            ("Create new pushback", self.createNewPushback),
            ("Duplicate current pushback", lambda self=self: self.createNewPushback(copyCurrent=True)  ),
        ]
        
        creationMenu = [
            ("Cancel", cancelCreationMenu),
            ("Hit-condition", hitconditionCreationMenu),
            ("Move", moveCreationMenu),
            ("Extra move-property", extrapropCreationMenu),
            ("Requirement", requirementCreationMenu),
            ("Reaction-list", reactionListCreationMenu),
            ("Pushback", pushbackCreationMenu),
        ]

        deletionMenu = [
            ("Current cancel", self.deleteCurrentCancel),
            ("Current cancel-list", self.deleteCurrentCancelList),
            ("", "separator"),
            ("Current hit-condition", self.deleteCurrentHitcondition),
            ("Current hit-condition list", self.deleteCurrentHitconditionList),
            ("", "separator"),
            ("Current move", self.deleteMove),
            ("", "separator"),
            ("Current extra move-prop", self.deleteCurrentExtraprop),
            ("Current extra move-prop list", self.deleteCurrentExtraproplist),
            ("", "separator"),
            ("Current requirement", self.deleteCurrentRequirement),
            ("Current requirement list", self.deleteCurrentRequirementList),
            ("", "separator"),
            ("Current reaction list", self.deleteReactionList),
            ("", "separator"),
            ("Current pushback", self.deletePushback)
        ]
        
        toolsMenu = [
            ("What cancels into this move", self.listCancelsForMove),
            ("What reactions use this move", self.listReactionsForMove)
        ]
        
        gotoMenu = [
            ("Cancel", self.goToCancel),
            ("Group cancel", self.goToGroupCancel),
            ("Reaction list", self.goToReactionList),
            ("Hit-condition list", self.goToHitConditionList),
        ]
        
        menuActions = [
            ('Toggle character selector', self.Charalist.toggleVisibility),
            ("", "separator"),
            ("Load to P1", lambda self=self : self.Charalist.loadToPlayer(0) ),
            ("Load to P2", lambda self=self : self.Charalist.loadToPlayer(1) ),
            ("", "separator"),
            ("New", creationMenu ),
            ("Delete", deletionMenu ),
            ("Tools", toolsMenu ),
            ("Go to", gotoMenu ),
        ]
        
        menu = createMenu(window, menuActions, validationFunc=self.canEditMoveset)
        window.config(menu=menu)
        
        
        self.movelist = None
        
        if showCharacterSelector:
            self.updateCharacterlist()
        else:
            self.Charalist.toggleVisibility()
            
        self.loadLabels()
        self.resetForms()
        
    def loadLabels(self):
        global requirementLabels, propertyLabels, commandLabels
        try:
            with open("InterfaceData/editorRequirements.txt", "r") as f:
                for line in f:
                    commaPos = line.find(',')
                    val, label = line[:commaPos], line[commaPos + 1:].strip()
                    requirementLabels[int(val)] = label
        except:
            pass
        try:
            with open("InterfaceData/editorProperties.txt", "r") as f:
                for line in f:
                    commaPos = line.find(',')
                    val, label = line[:commaPos], line[commaPos + 1:].strip()
                    propertyLabels[int(val, 16)] = label
        except:
            pass
        try:
            with open("InterfaceData/editorCommands.txt", "r") as f:
                for line in f:
                    commaPos = line.find(',')
                    val, label = line[:commaPos], line[commaPos + 1:].strip()
                    commandLabels[int(val, 16)] = label
        except:
            pass
            
    def setTitle(self, label = ""):
        title = "TekkenMovesetEditor %s" % (editorVersion)
        if label != "":
            title += " - " + label
        self.window.wm_title(title) 

    def save(self):
        if self.Charalist.filename == None or self.Charalist.movelist_path == None:
            return
        jsonPath = "%s/%s" % (self.Charalist.movelist_path, self.Charalist.filename)
        
        if os.path.exists(jsonPath):
            os.remove(jsonPath)
            
        with open(jsonPath, "w") as f:
            self.movelist['last_calculated_hash'] = calculateHash(self.movelist)
            json.dump(self.movelist, f, indent=4)
            
        print("Editor: saved at " + jsonPath)
        
    def updateCharacterlist(self):
        self.Charalist.updateCharacterlist()
        
    def resetForms(self):
        self.MoveEditor.resetForm()
        self.CancelEditor.resetForm()
        self.RequirementEditor.resetForm()
        self.ExtrapropEditor.resetForm()
        self.HitConditionEditor.resetForm()
        self.ReactionListEditor.resetForm()
        self.PushbackEditor.resetForm()
        self.PushbackExtraEditor.resetForm()
        self.CancelExtraEditor.resetForm()
        self.VoiceclipEditor.resetForm()
        if self.GroupCancelEditor:
            self.GroupCancelEditor.on_close()
            
    def goToCancel(self):
        maxvalue = len(self.movelist['cancels']) - 1
        cancelId = simpledialog.askinteger("Go to Cancel", "Input cancel list id (0 - %d)" % (maxvalue), minvalue=0, maxvalue=maxvalue)
        if cancelId != None:
            self.setCancelList(cancelId)
            
    def goToGroupCancel(self):
        maxvalue = len(self.movelist['group_cancels']) - 1
        cancelId = simpledialog.askinteger("Go to Group-Cancel", "Input group-cancel list id (0 - %d)" % (maxvalue), minvalue=0, maxvalue=maxvalue)
        if cancelId != None:
            self.openGroupCancel(cancelId)
            
    def goToReactionList(self):
        maxvalue = len(self.movelist['reaction_list']) - 1
        reactionListId = simpledialog.askinteger("Go to Reaction-list", "Input reaction-list id (0 - %d)" % (maxvalue), minvalue=0, maxvalue=maxvalue)
        if reactionListId != None:
            self.setReactionList(reactionListId)
            
    def goToHitConditionList(self):
        maxvalue = len(self.movelist['hit_conditions']) - 1
        conditionId = simpledialog.askinteger("Go to Hit-Condition list", "Input hit-condition list id (0 - %d)" % (maxvalue), minvalue=0, maxvalue=maxvalue)
        if conditionId != None:
            self.setConditionList(conditionId)
            
    def listMovesUsingCancel(self, cancelListId, cancelId):
        for move_id, move in enumerate(self.movelist['moves']):
            if cancelListId <= move['cancel_idx'] <= cancelId:
                yield (move_id, move['name'])
            
    def listCancelsUsingGroupCancel(self, cancelListId, cancelId):
        listId = 0
        for cancel_id, cancel in enumerate(self.movelist['cancels']):
            if cancel['command'] == 0x800b and cancelListId <= cancel['move_id'] <= cancelId:
                yield listId, cancel_id
            elif cancel['command'] == 0x8000:
                listId = cancel_id + 1

    def listCancelsForMove(self):
        if self.MoveEditor.editMode == None:
            return
            
        refList = []
                
        listId = 0
        for cancel_id, cancel in enumerate(self.movelist['group_cancels']):
            if cancel['move_id'] == self.MoveEditor.id:
                moveReferences = []
                
                for cancelListId, cancelId in self.listCancelsUsingGroupCancel(listId, cancel_id):
                    moveList = [move for move in self.listMovesUsingCancel(cancelListId, cancelId)]
                    
                    if len(moveList) != 0:
                        for move_id, move_name in self.listMovesUsingCancel(cancelListId, cancelId):
                            moveReferences.append('Move %s (%d) -> Cancel list %d (item %d, idx %d)' % (move_name, move_id, cancelListId, cancelId, cancelId - cancelListId))
                    else:
                        moveReferences.append('Cancel list %d (item %d, idx %d)' % (cancelListId, cancelId, cancelId - cancelListId))
                    
                refList.append({
                    'origin': 'group_cancels',
                    'item_id': cancel_id,
                    'list_id': listId,
                    'references': moveReferences
                })
            if cancel['command'] == 0x800c:
                listId = cancel_id + 1
        
        listId = 0
        for cancel_id, cancel in enumerate(self.movelist['cancels']):
            if cancel['command'] != 0x800b and cancel['move_id'] == self.MoveEditor.id:
                references = ['Move %s (%d)' % (ref[1], ref[0]) for ref in self.listMovesUsingCancel(listId, cancel_id)]
                refList.append({
                    'origin': 'cancels',
                    'item_id': cancel_id,
                    'list_id': listId,
                    'references': references
                })
            if cancel['command'] == 0x8000:
                listId = cancel_id + 1
        
        app = MoveReferenceWindow(self, self.movelist['moves'][self.MoveEditor.id]['name'], self.MoveEditor.id, refList)
        app.window.mainloop()

    def listReactionsForMove(self):
        if self.MoveEditor.editMode == None:
            return
        refList = []
        
        for reactionlistId, reactionList in enumerate(self.movelist['reaction_list']):
            referencesMove = False
            
            for field in [f for f in reactionList if f != 'pushback_indexes' and f != 'u1list' and f != 'vertical_pushback']:
                if reactionList[field] == self.MoveEditor.id:
                    referencesMove = True
                    break
            
            if referencesMove:
                references = []
                refList.append({
                    'origin': 'reaction_list',
                    'item_id': reactionlistId,
                    'references': references
                })
        
        app = MoveReferenceWindow(self, self.movelist['moves'][self.MoveEditor.id]['name'], self.MoveEditor.id, refList)
        app.window.mainloop()
        
    def openGroupCancel(self, id):
        if self.GroupCancelEditor == None:
            app = GroupCancelWindow(self, id)
            self.GroupCancelEditor = app
            app.window.mainloop()
        else:
            self.GroupCancelEditor.setCancelList(id)
        
    def openMoveCopyWindow(self):
        if self.MoveCopyingWindow == None:
            messagebox.showinfo('Warning', 'This feature is in BETA, save your moveset before using it!!!')
            app = MoveCopyingWindow(self)
            self.MoveCopyingWindow = app
            app.window.mainloop()      
            
    def getMoveId(self, moveId):
        if moveId >= 0x8000 and moveId - 0x8000 < len(self.movelist['aliases']):
            return self.movelist['aliases'][moveId - 0x8000] 
        return moveId
        
    def getMoveName(self, moveId):
        moveId = self.getMoveId(moveId)
        if moveId == None or moveId >= len(self.movelist['moves']):
            return None
        return self.movelist['moves'][moveId]['name']
        
    def setMove(self, moveId):
        moveId = self.getMoveId(moveId)
        if moveId < 0 or moveId >= len(self.movelist['moves']):
            return
        moveData = self.movelist['moves'][moveId]
        self.MoveEditor.setMove(moveData, moveId)
        self.MoveSelector.movelistSelect.select_set(moveId)
        self.MoveSelector.movelistSelect.see(moveId)
        
    def setReactionList(self, itemId):
        if itemId < 0 or itemId >= len(self.movelist['reaction_list']):
            return
        itemData = self.movelist['reaction_list'][itemId]
        self.ReactionListEditor.setItem(itemData, itemId)
        
    def setVoiceclip(self, itemId):
        if itemId < 0 or itemId >= len(self.movelist['voiceclips']):
            return
        itemData = self.movelist['voiceclips'][itemId]
        self.VoiceclipEditor.setItem(itemData, itemId)
        
    def setCancelExtra(self, itemId):
        if itemId < 0 or itemId >= len(self.movelist['cancel_extradata']):
            return
        itemData = self.movelist['cancel_extradata'][itemId]
        self.CancelExtraEditor.setItem(itemData, itemId)
        
    def setPushbackExtra(self, itemId):
        if itemId < 0 or itemId >= len(self.movelist['pushback_extras']):
            return
        itemData = self.movelist['pushback_extras'][itemId]
        self.PushbackExtraEditor.setItem(itemData, itemId)
        
    def setPushback(self, itemId):
        if itemId < 0 or itemId >= len(self.movelist['pushbacks']):
            return
        itemData = self.movelist['pushbacks'][itemId]
        self.PushbackEditor.setItem(itemData, itemId)
        
    def setCancelList(self, cancelId):
        if cancelId < 0 or cancelId >= len(self.movelist['cancels']):
            return
        id = cancelId
        while self.movelist['cancels'][id]['command'] != 0x8000:
            id += 1
        cancelList = [cancel for cancel in self.movelist['cancels'][cancelId:id + 1]]
        self.CancelEditor.setItemList(cancelList, cancelId)
        
    def setRequirementList(self, requirementId):
        if requirementId < 0 or requirementId >= len(self.movelist['requirements']):
            return
        id = requirementId
        endValue = reqListEndval[self.movelist['version']]
        while self.movelist['requirements'][id]['req'] != endValue:
            id += 1
        reqList = [req for req in self.movelist['requirements'][requirementId:id + 1]]
        self.RequirementEditor.setItemList(reqList, requirementId)
        
    def setExtrapropList(self, propId):
        if propId < 0 or propId >= len(self.movelist['extra_move_properties']):
            return
        id = propId
        while self.movelist['extra_move_properties'][id]['type'] != 0:
            id += 1
        propList = [prop for prop in self.movelist['extra_move_properties'][propId:id + 1]]
        self.ExtrapropEditor.setItemList(propList, propId)
        
    def setConditionList(self, itemId):
        if itemId < 0 or itemId >= len(self.movelist['hit_conditions']):
            return
        id = itemId
        endValue = reqListEndval[self.movelist['version']]
        while True:
            reqIdx = self.movelist['hit_conditions'][id]['requirement_idx'] 
            if self.movelist['requirements'][reqIdx]['req'] == endValue:
                break
            id += 1
        itemList = [item for item in self.movelist['hit_conditions'][itemId:id + 1]]
        self.HitConditionEditor.setItemList(itemList, itemId)
        
    def canEditMoveset(self):
        return self.movelist != None
        
    def createCancelList(self):
        newCancel = {f:0 for f in cancelFields}
        newCancel['command'] = 0x8000
        
        self.movelist['cancels'].append(newCancel)
        self.setCancelList(len(self.movelist['cancels']) - 1)
        
    def copyCancelList(self):
        if self.CancelEditor.editMode == None:
            return
            
        cancelId = self.CancelEditor.baseId
        id = cancelId
        while self.movelist['cancels'][id]['command'] != 0x8000:
            id += 1
        cancelList = [cancel.copy() for cancel in self.movelist['cancels'][cancelId:id + 1]]
        
        listIndex = len(self.movelist['cancels'])
        self.movelist['cancels'] += cancelList
        self.setCancelList(listIndex)
        
    def deleteCurrentCancelList(self):
        if self.CancelEditor.editMode == None:
            return
        startingId = self.CancelEditor.baseId
        listLen = len(self.CancelEditor.itemList)
        
        title = 'Delete cancel-list %d' % (startingId)
        message = 'Are you sure you want to delete the cancel-list %d (%d cancels)?\nCancel IDs will be properly shifted down.' % (startingId, listLen)
        result = messagebox.askquestion(title, message, icon='warning')
        
        if result == 'yes':
            self.movelist['cancels'] = self.movelist['cancels'][:startingId] + self.movelist['cancels'][startingId + listLen:]
        
            for move in self.movelist['moves']:
                if move['cancel_idx'] > startingId:
                    move['cancel_idx'] -= listLen
                
            for projectile in self.movelist['projectiles']:
                if projectile['cancel_idx'] > startingId:
                    projectile['cancel_idx'] -= listLen
            
            messagebox.showinfo('Return', 'Cancel-list successfully deleted.')
            self.CancelEditor.resetForm()
        
    def deleteCurrentCancel(self):
        if self.CancelEditor.editMode == None:
            return
        
        listIndex = self.CancelEditor.listIndex
        index = self.CancelEditor.id
        resetForm = (self.movelist['cancels'][index]['command'] == 0x8000)
        self.movelist['cancels'].pop(index)
        
        for move in self.movelist['moves']:
            if move['cancel_idx'] > index:
                move['cancel_idx'] -= 1
                
        for projectile in self.movelist['projectiles']:
            if projectile['cancel_idx'] > index:
                projectile['cancel_idx'] -= 1
        
        if not resetForm:
            self.setCancelList(self.CancelEditor.baseId)
            self.CancelEditor.setItem(listIndex)
        else:
            self.CancelEditor.resetForm()
        
    def insertNewCancel(self, copyCurrent=False):
        if self.CancelEditor.editMode == None:
            return
        
        index = self.CancelEditor.listIndex
        insertPoint = self.CancelEditor.id
        
        if not copyCurrent:
            newCancel = {f:0 for f in cancelFields}
        else:
            newCancel = self.movelist['cancels'][insertPoint].copy()
        
        self.movelist['cancels'].insert(insertPoint, newCancel)
        
        for move in self.movelist['moves']:
            if move['cancel_idx'] > insertPoint:
                move['cancel_idx'] += 1
                
        for projectile in self.movelist['projectiles']:
            if projectile['cancel_idx'] > insertPoint:
                projectile['cancel_idx'] += 1
        
        self.setCancelList(self.CancelEditor.baseId)
        self.CancelEditor.setItem(index)
        
    def createExtrapropList(self):
        newProp = {f:0 for f in extrapropFields}
        
        self.movelist['extra_move_properties'].append(newProp)
        self.setExtrapropList(len(self.movelist['extra_move_properties']) - 1)
        
    def copyExtrapropList(self):
        if self.ExtrapropEditor.editMode == None:
            return
            
        baseId = self.ExtrapropEditor.baseId
        id = baseId
        while self.movelist['extra_move_properties'][id]['type'] != 0:
            id += 1
        propList = [prop.copy() for prop in self.movelist['extra_move_properties'][baseId:id + 1]]
        
        listIndex = len(self.movelist['extra_move_properties'])
        self.movelist['extra_move_properties'] += propList
        self.setExtrapropList(listIndex)
        
    def deleteCurrentExtraproplist(self):
        if self.ExtrapropEditor.editMode == None:
            return
        startingId = self.ExtrapropEditor.baseId
        listLen = len(self.ExtrapropEditor.itemList)
        
        title = 'Delete extra-prop list %d' % (startingId)
        message = 'Are you sure you want to delete the extra-prop list %d (%d properties)?\nIDs will be properly shifted down.' % (startingId, listLen)
        result = messagebox.askquestion(title, message, icon='warning')
        
        if result == 'yes':
            self.movelist['extra_move_properties'] = self.movelist['extra_move_properties'][:startingId] + self.movelist['extra_move_properties'][startingId + listLen:]
        
            for move in self.movelist['moves']:
                if move['extra_properties_idx'] > startingId:
                    move['extra_properties_idx'] -= listLen
            
            messagebox.showinfo('Return', 'Extra-prop list successfully deleted.')
            self.ExtrapropEditor.resetForm()
        
    def deleteCurrentExtraprop(self):
        if self.ExtrapropEditor.editMode == None:
            return
        
        listIndex = self.ExtrapropEditor.listIndex
        index = self.ExtrapropEditor.id
        resetForm = (self.movelist['extra_move_properties'][index]['type'] == 0)
        self.movelist['extra_move_properties'].pop(index)
        
        for move in self.movelist['moves']:
            if move['extra_properties_idx'] > index:
                move['extra_properties_idx'] -= 1
        
        if not resetForm:
            self.setExtrapropList(self.ExtrapropEditor.baseId)
            self.ExtrapropEditor.setItem(listIndex)
        else:
            self.ExtrapropEditor.resetForm()
        
    def insertNewExtraprop(self, copyCurrent=False):
        if self.ExtrapropEditor.editMode == None:
            return
        
        index = self.ExtrapropEditor.listIndex
        insertPoint = self.ExtrapropEditor.id
        
        if not copyCurrent:
            newProp = {f:0 for f in extrapropFields}
            newProp['type'] = 0x8001
        else:
            newProp = self.movelist['extra_move_properties'][insertPoint].copy()
        
        self.movelist['extra_move_properties'].insert(insertPoint, newProp)
        
        for move in self.movelist['moves']:
            if move['extra_properties_idx'] > insertPoint:
                move['extra_properties_idx'] += 1
        
        self.setExtrapropList(self.ExtrapropEditor.baseId)
        self.ExtrapropEditor.setItem(index)
        
    def createRequirementList(self):
        newProp = {f:0 for f in requirementFields}
        newProp['req'] = reqListEndval[self.movelist['version']]
        
        self.movelist['requirements'].append(newProp)
        self.setRequirementList(len(self.movelist['requirements']) - 1)
        
    def copyRequirementList(self):
        if self.RequirementEditor.editMode == None:
            return
            
        baseId = self.RequirementEditor.baseId
        id = baseId
        endval = reqListEndval[self.movelist['version']]
        while self.movelist['requirements'][id]['req'] != endval:
            id += 1
        reqList = [req.copy() for req in self.movelist['requirements'][baseId:id + 1]]
        
        listIndex = len(self.movelist['requirements'])
        self.movelist['requirements'] += reqList
        self.setRequirementList(listIndex)
        
    def deleteCurrentRequirementList(self):
        if self.RequirementEditor.editMode == None:
            return
        startingId = self.RequirementEditor.baseId
        listLen = len(self.RequirementEditor.itemList)
        
        title = 'Delete requirement list %d' % (startingId)
        message = 'Are you sure you want to delete the requirement list %d (%d conditions)?\nIDs will be properly shifted down.' % (startingId, listLen)
        result = messagebox.askquestion(title, message, icon='warning')
        
        if result == 'yes':
            self.movelist['requirements'] = self.movelist['requirements'][:startingId] + self.movelist['requirements'][startingId + listLen:]
        
            for cancel in self.movelist['cancels']:
                if cancel['requirement_idx'] > startingId:
                    cancel['requirement_idx'] -= listLen
                    
            for cancel in self.movelist['group_cancels']:
                if cancel['requirement_idx'] > startingId:
                    cancel['requirement_idx'] -= listLen
                    
            for hitCondition in self.movelist['hit_conditions']:
                if hitCondition['requirement_idx'] > startingId:
                    hitCondition['requirement_idx'] -= listLen
            
            messagebox.showinfo('Return', 'Requirement list list successfully deleted.')
            self.RequirementEditor.resetForm()
        
    def deleteCurrentRequirement(self):
        if self.RequirementEditor.editMode == None:
            return
        
        listIndex = self.RequirementEditor.listIndex
        index = self.RequirementEditor.id
        endval = reqListEndval[self.movelist['version']]
        resetForm = (self.movelist['requirements'][index]['req'] == endval)
        self.movelist['requirements'].pop(index)
        
        for cancel in self.movelist['cancels']:
            if cancel['requirement_idx'] > index:
                cancel['requirement_idx'] -= 1
                
        for cancel in self.movelist['group_cancels']:
            if cancel['requirement_idx'] > index:
                cancel['requirement_idx'] -= 1
                
        for hitCondition in self.movelist['hit_conditions']:
            if hitCondition['requirement_idx'] > index:
                hitCondition['requirement_idx'] -= 1
        
        if not resetForm:
            self.setRequirementList(self.RequirementEditor.baseId)
            self.RequirementEditor.setItem(listIndex)
        else:
            self.RequirementEditor.resetForm()
        
    def insertNewRequirement(self, copyCurrent=False):
        if self.RequirementEditor.editMode == None:
            return
        
        index = self.RequirementEditor.listIndex if copyCurrent else 0
        insertPoint = self.RequirementEditor.id
        
        if not copyCurrent:
            newProp = {f:0 for f in requirementFields}
        else:
            newProp = self.movelist['requirements'][insertPoint].copy()
        
        self.movelist['requirements'].insert(insertPoint, newProp)
        
        for cancel in self.movelist['cancels']:
            if cancel['requirement_idx'] > insertPoint:
                cancel['requirement_idx'] += 1
                
        for cancel in self.movelist['group_cancels']:
            if cancel['requirement_idx'] > insertPoint:
                cancel['requirement_idx'] += 1
                
        for hitCondition in self.movelist['hit_conditions']:
            if hitCondition['requirement_idx'] > insertPoint:
                hitCondition['requirement_idx'] += 1
        
        self.setRequirementList(self.RequirementEditor.baseId)
        self.RequirementEditor.setItem(index)
        
    def createGroupCancelList(self):
        newCancel = {f:0 for f in cancelFields}
        newCancel['command'] = 0x800c
        
        self.movelist['group_cancels'].append(newCancel)
        self.openGroupCancel(len(self.movelist['group_cancels']) - 1)
        
    def copyGroupCancelList(self):
        if self.GroupCancelEditor == None:
            return
            
        cancelId = self.GroupCancelEditor.CancelEditor.baseId
        id = cancelId
        while self.movelist['group_cancels'][id]['command'] != 0x800c:
            id += 1
        cancelList = [cancel.copy() for cancel in self.movelist['group_cancels'][cancelId:id + 1]]
        
        listIndex = len(self.movelist['group_cancels'])
        self.movelist['group_cancels'] += cancelList
        self.openGroupCancel(listIndex)
        
    def deleteCurrentGroupCancelList(self):
        if self.GroupCancelEditor == None:
            return
            
        startingId = self.GroupCancelEditor.CancelEditor.baseId
        listLen = len(self.GroupCancelEditor.CancelEditor.itemList)
        
        title = 'Delete group cancel-list %d' % (startingId)
        message = 'Are you sure you want to delete the group cancel-list %d (%d cancels)?' % (startingId, listLen)
        result = messagebox.askquestion(title, message, icon='warning')
        
        if result == 'yes':
            self.movelist['group_cancels'] = self.movelist['group_cancels'][:startingId] + self.movelist['group_cancels'][startingId + listLen:]
        
            for cancel in self.movelist['cancels']:
                if cancel['command'] == 0x800b and cancel['move_id'] > startingId:
                    cancel['move_id'] -= listLen
            
            messagebox.showinfo('Return', 'Group cancel-list successfully deleted.')
            self.GroupCancelEditor.on_close()
        
    def deleteCurrentGroupCancel(self):
        if self.GroupCancelEditor == None:
            return
        
        listIndex = self.GroupCancelEditor.CancelEditor.listIndex
        index = self.GroupCancelEditor.CancelEditor.id
        resetForm = (self.movelist['group_cancels'][index]['command'] == 0x800c)
        self.movelist['group_cancels'].pop(index)
        
        for cancel in self.movelist['cancels']:
            if cancel['command'] == 0x800b and cancel['move_id'] > index:
                cancel['move_id'] -= 1
        
        if not resetForm:
            self.openGroupCancel(self.GroupCancelEditor.CancelEditor.baseId)
            self.GroupCancelEditor.CancelEditor.setItem(listIndex)
        else:
            self.GroupCancelEditor.CancelEditor.resetForm()
        
    def insertNewGroupCancel(self, copyCurrent=False):
        if copyCurrent and self.GroupCancelEditor == None:
            return
        
        index = self.GroupCancelEditor.CancelEditor.listIndex
        insertPoint = self.GroupCancelEditor.CancelEditor.id
        
        if not copyCurrent:
            newCancel = {f:0 for f in cancelFields}
        else:
            newCancel = self.movelist['group_cancels'][insertPoint].copy()
        
        self.movelist['group_cancels'].insert(insertPoint, newCancel)
        
        for cancel in self.movelist['cancels']:
            if cancel['command'] == 0x800b and cancel['move_id'] > insertPoint:
                cancel['move_id'] += 1
        
        self.openGroupCancel(self.GroupCancelEditor.CancelEditor.baseId)
        self.GroupCancelEditor.CancelEditor.setItem(index)
        
    def insertNewHitCondition(self, copyCurrent=False):
        if self.HitConditionEditor.editMode == None:
            return
        
        index = self.HitConditionEditor.listIndex if copyCurrent == True else 0
        insertPoint = self.HitConditionEditor.id
        
        if not copyCurrent:
            newHitCondition = {f:0 for f in hitConditionFields}
        else:
            newHitCondition = self.movelist['hit_conditions'][insertPoint].copy()
        
        self.movelist['hit_conditions'].insert(insertPoint, newHitCondition)
        
        for move in self.movelist['moves']:
            if move['hit_condition_idx'] > insertPoint:
                move['hit_condition_idx'] += 1
                
        for projectile in self.movelist['projectiles']:
            if projectile['hit_condition_idx'] > insertPoint:
                projectile['hit_condition_idx'] += 1
        
        self.setConditionList(self.HitConditionEditor.baseId)
        self.HitConditionEditor.setItem(index)
        
    def copyHitconditionList(self, forceId=None):
        if forceId == None and self.HitConditionEditor.editMode == None:
            return
            
        itemId = self.HitConditionEditor.baseId if forceId == None else forceId
        id = itemId
        endValue = reqListEndval[self.movelist['version']]
        while True:
            reqIdx = self.movelist['hit_conditions'][id]['requirement_idx'] 
            if self.movelist['requirements'][reqIdx]['req'] == endValue:
                break
            id += 1
        itemList = [item.copy() for item in self.movelist['hit_conditions'][itemId:id + 1]]
        
        listIndex = len(self.movelist['hit_conditions'])
        self.movelist['hit_conditions'] += itemList
        self.setConditionList(listIndex)
        
    def deleteCurrentHitcondition(self):
        if self.HitConditionEditor.editMode == None:
            return
        
        listIndex = self.HitConditionEditor.listIndex
        index = self.HitConditionEditor.id
        endValue = reqListEndval[self.movelist['version']]
        reqIdx = self.movelist['hit_conditions'][index]['requirement_idx']
        resetForm = self.movelist['requirements'][reqIdx]['req'] == endValue
        
        self.movelist['hit_conditions'].pop(index)
        
        for move in self.movelist['moves']:
            if move['hit_condition_idx'] > index:
                move['hit_condition_idx'] -= 1
                
        for projectile in self.movelist['projectiles']:
            if projectile['hit_condition_idx'] > index:
                projectile['hit_condition_idx'] -= 1
        
        if not resetForm:
            self.setConditionList(self.HitConditionEditor.baseId)
            self.HitConditionEditor.setItem(listIndex)
        else:
            self.HitConditionEditor.resetForm()
        
    def deleteCurrentHitconditionList(self):
        if self.HitConditionEditor.editMode == None:
            return
        startingId = self.HitConditionEditor.baseId
        listLen = len(self.HitConditionEditor.itemList)
        
        title = 'Delete hit-condition list %d' % (startingId)
        message = 'Are you sure you want to delete the hit-condition list %d (%d items)?\nIDs will be properly shifted down.' % (startingId, listLen)
        result = messagebox.askquestion(title, message, icon='warning')
        
        if result == 'yes':
            self.movelist['hit_conditions'] = self.movelist['hit_conditions'][:startingId] + self.movelist['hit_conditions'][startingId + listLen:]
        
            for move in self.movelist['moves']:
                if move['hit_condition_idx'] > startingId:
                    move['hit_condition_idx'] -= listLen
                
            for projectile in self.movelist['projectiles']:
                if projectile['hit_condition_idx'] > startingId:
                    projectile['hit_condition_idx'] -= listLen
            
            messagebox.showinfo('Return', 'Hit-condition list successfully deleted.')
            self.HitConditionEditor.resetForm()
        
    def createNewReactionlist(self, copyCurrent=False):
        if copyCurrent and self.ReactionListEditor.editMode == None:
            return
            
        if not copyCurrent:
            newReactionlist = self.movelist['reaction_list'][0].copy()
        else:
            newReactionlist = self.movelist['reaction_list'][self.ReactionListEditor.id].copy()
        
        itemIndex = len(self.movelist['reaction_list'])
        self.movelist['reaction_list'].append(newReactionlist)
        self.setReactionList(itemIndex)
        
    def deleteReactionList(self):
        if self.ReactionListEditor.editMode == None:
            return
        
        index = self.ReactionListEditor.id
        self.movelist['reaction_list'].pop(index)
        
        for hitCondition in self.movelist['hit_conditions']:
            if hitCondition['reaction_list_idx'] > index:
                hitCondition['reaction_list_idx'] -= 1

        self.ReactionListEditor.resetForm()
        
    def createNewPushback(self, copyCurrent=False):
        if copyCurrent and self.PushbackEditor.editMode == None:
            return
            
        if not copyCurrent:
            newPushback = {f:0 for f in pushbackFields}
        else:
            newPushback = self.movelist['pushbacks'][self.PushbackEditor.id].copy()
        
        itemIndex = len(self.movelist['pushbacks'])
        self.movelist['pushbacks'].append(newPushback)
        self.setPushback(itemIndex)
        
    def deletePushback(self):
        if self.PushbackEditor.editMode == None:
            return
        
        index = self.PushbackEditor.id
        self.movelist['pushbacks'].pop(index)
        
        for reactionList in self.movelist['reaction_list']:
            for i, p in enumerate(reactionList['pushback_indexes']):
                if p > index:
                    reactionList['pushback_indexes'][i] -= 1

        self.PushbackEditor.resetForm()
        
    def deleteMove(self):
        if self.MoveEditor.editMode == None:
            return
            
        moveId = self.MoveEditor.id
        self.movelist['moves'].pop(moveId)
        
        for cancel in self.movelist['cancels']:
            if cancel['move_id'] > moveId and cancel['command'] != 0x800b and cancel['move_id'] < 0x8000:
                cancel['move_id'] -= 1
        
        for cancel in self.movelist['group_cancels']:
            if cancel['move_id'] > moveId and cancel['move_id'] < 0x8000:
                cancel['move_id'] -= 1
                
        for reactionList in self.movelist['reaction_list']:
            keyList = [key for key in reactionList if key != 'pushback_indexes' and key != 'u1list' and key != 'vertical_pushback']
            for key in keyList: 
                if reactionList[key] > moveId:
                    reactionList[key] -= 1
                    
        self.MoveEditor.resetForm()
        self.MoveSelector.setMoves(self.movelist['moves'], self.movelist['aliases'])
        
        
    def createMove(self, copyCurrent=False):
        if copyCurrent and self.MoveEditor.editMode == None:
            return
        
        moveId = len(self.movelist['moves'])
        if copyCurrent:
            newMove = self.movelist['moves'][self.MoveEditor.id].copy()
            newMove['name'] = 'COPY_' + newMove['name']
        else:
            newMove = {f:(0 if moveFields[f] != 'text' else '') for f in moveFields}
            newMove['name'] = 'NEW_MOVE_%d' % (moveId)
            newMove['voiceclip_idx'] = -1
            newMove['extra_properties_idx'] = -1
        
        self.movelist['moves'].append(newMove)
        self.MoveSelector.setMoves(self.movelist['moves'], self.movelist['aliases'])
        self.setMove(moveId)
        
    def saveField(self, key, id, field, value):
        if field != None:
            self.movelist[key][id][field] = value
        else:
            self.movelist[key][id] = value
        

if __name__ == "__main__":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('kilo.TekkenMovesetEditor')
    app = GUI_TekkenMovesetEditor()
    app.window.mainloop()

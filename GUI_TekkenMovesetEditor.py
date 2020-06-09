# Python 3.6.5

from tkinter import Tk, Frame, Listbox, Label, Scrollbar, StringVar, Toplevel, Menu
from tkinter.ttk import Button, Entry
from Addresses import game_addresses, GameClass
from Aliases import getRequirement, getTag2Requirement, getProperty, getTag2ExtraMoveProperty
import motbinImport as importLib
import json
import os
import re
from zlib import crc32

charactersPath = "./extracted_chars/"

itemNames = {
    'moves': 'move',
    'cancels': 'cancel',
    'requirements': 'requirement',
    'extra_move_properties': 'move property',
    'hit_conditions': 'hit condition',
    'reaction_list': 'reaction list'
}

fieldLabels = {
    'u17': 'distance (u17)',
    'anim_max_len': 'anim_len',
    'standing': 'default'
}

moveFields = {
    'name': 'text',
    'anim_name': 'text',
    'vuln': 'number',
    'hitlevel': 'number',
    'cancel_idx': 'number',
    'transition': 'number',
    'anim_max_len': 'number',
    'hit_condition_idx': 'number',
    'voiceclip_idx': 'number',
    'extra_properties_idx': 'number',
    'hitbox_location': 'hex',
    'first_active_frame': 'number',
    'last_active_frame': 'number',
    'u2': 'number',
    'u3': 'number',
    'u4': 'number',
    'u6': 'number',
    'u7': 'number',
    'u8': 'number',
    'u8_2': 'number',
    'u9': 'number',
    'u10': 'number',
    'u11': 'number',
    'u12': 'number',
    'u15': 'number',
    'u16': 'number',
    'u18': 'number',
    'u17': 'number'
}

cancelFields = {
    'command': 'hex',
    'extradata_idx': 'number',
    'requirement_idx': 'number',
    'frame_window_start': 'number',
    'frame_window_end': 'number',
    'starting_frame': 'number',
    'move_id': 'number',
    'cancel_option': 'number'
}

requirementFields = {
    'req': 'number',
    'param': 'number'
}

extrapropFields = {
    'type': 'hex',
    'id': 'hex',
    'value': 'number'
}

hitConditionFields = {
    'requirement_idx': 'number',
    'damage': 'number',
    'reaction_list_idx': 'number'
}

reactionlistFields = {
    'vertical_pushback': 'number',
    'standing': 'number',
    'ch': 'number',
    'crouch': 'number',
    'crouch_ch': 'number',
    'left_side': 'number',
    'left_side_crouch': 'number',
    'right_side': 'number',
    'right_side_crouch': 'number',
    'back': 'number',
    'back_crouch': 'number',
    'block': 'number',
    'crouch_block': 'number',
    'wallslump': 'number',
    'downed': 'number'
}

fieldsTypes = {
    'moves': moveFields,
    'cancels': cancelFields,
    'requirements': requirementFields,
    'extra_move_properties': extrapropFields,
    'hit_conditions': hitConditionFields,
    'reaction_list': reactionlistFields
}
    
def getCharacterList():
    if not os.path.isdir(charactersPath):
        return []
    folders = [folder for folder in os.listdir(charactersPath) if os.path.isdir(charactersPath + folder)]
    tag2_chars = sorted(folders)
    
    return t7_chars + tag2_chars
    
def getMovelist(path):
    jsonFilename = next(file for file in os.listdir(path) if file.endswith(".json"))
    with open('%s/%s' % (path, jsonFilename)) as f:
        return json.load(f), jsonFilename
        
def sortKeys(keys):
    keyList = [key for key in keys if not re.match("^u[0-9_]+$", key)]
    unknownKeys = [key for key in keys if re.match("^u[0-9_]+$", key)]
    return keyList + unknownKeys
        
def validateField(type, value):
    if type == 'number':
        return re.match("^-?[0-9]+$", value)
    if type == 'hex' or type == '8hex':
        return re.match("^(0(x|X))?[0-9A-Za-z]+$", value)
    if type == 'text':
        return re.match("^[a-zA-Z0-9_\-\(\)]+$", value)
    raise Exception("Unknown type '%s'" % (type))
    
def getFieldValue(type, value):
    if type == 'number':
        return int(value)
    if type == 'hex':
        return int(value, 16)
    if type == 'text':
        return str(value)
    raise Exception("Unknown type '%s'" % (type))
    
def formatFieldValue(type, value):
    if type == 'number':
        return str(value)
    if type == 'hex':
        return "0x%x" % (value)
    if type == 'text':
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

    direction =  {
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
        self.root.MovelistSelector.hide()
        self.frame.pack(side='left', fill='y')
        self.root.MovelistSelector.show()
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
            colors = [
                ["#fff", "#eee"], #TTT2
                ["#eee", "#ddd"]  #T7
            ]
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
        TekkenImporter.importMoveset(playerAddr, self.movelist_path, moveset=self.root.movelist)
        
    def selectMoveset(self, selection=None):
        selection = self.selection if selection == None else selection
        
        if selection == None:
            selection = self.last_selection
            if selection == None:
                return
        else:
            self.colorCharacterList()
            self.charaSelect.itemconfig(self.selectionIndex, {'bg': '#a126c7', 'fg': 'white'})
            
        self.movelist_path = "extracted_chars/" + selection
        movelist, filename = getMovelist(self.movelist_path)
        self.filename = filename
        self.last_selection = selection
        
        self.root.MovelistSelector.setMoves(movelist['moves'], movelist['aliases'])
        self.root.MovelistSelector.setCharacter(movelist['character_name'])
        self.root.movelist = movelist
        self.root.resetForms()
        
        self.hide()
        
class MovelistSelector:
    def __init__(self, root, rootFrame):
        self.root = root
        movelistFrame = Frame(rootFrame)
        movelistFrame.pack(side='left', fill='y')
        
        bottomButtons = [
            ('Save to file', self.root.save),
            ('Go to current move ID', self.goToCurrentMove)
        ]
        
        for label, callback in bottomButtons:
            newButton = Button(movelistFrame, text=label, command=callback)
            newButton.pack(side='bottom', fill='x')
        
        selectedChar = Label(movelistFrame, text="No character selected", bg='#bbb')
        selectedChar.pack(side='bottom', fill='x')
        
        movelistSelect = Listbox(movelistFrame, width=30)
        movelistSelect.bind('<<ListboxSelect>>', self.onMoveSelection)
        movelistSelect.pack(side='left', fill='both')
        
        scrollbar = Scrollbar(movelistFrame, command=movelistSelect.yview)
        scrollbar.pack(side='right', fill='y')
        
        movelistSelect.config(yscrollcommand=scrollbar.set)
        
        self.frame = movelistFrame
        self.selectedChar = selectedChar
        self.movelistSelect = movelistSelect
       
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
            self.root.setMove(moveId)
            
    def goToCurrentMove(self):
        if self.root.movelist == None:
            return
        playerAddress = game_addresses.addr['t7_p1_addr']
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
        
    def setLabel(self, text, saveLabel=True):
        self.label['text'] = text
        if saveLabel:
            self.lastValidLabel = text
    
    def onchange(self, field, sv):
        if self.editMode == None:
            return
        value = sv.get()
        valueType = self.fieldTypes[field]
        
        if validateField(valueType, value):
            self.fieldValue[field] =  getFieldValue(valueType, value)
            self.setLabel(self.lastValidLabel, False)
        else:
            self.setLabel(self.lastValidLabel + " - Invalid field: " + field, False)
        
        self.setField(field, value)
        
    def setListOnsaveFunction(self, function):
        self.listSaveFunction = function
        
    def save(self):
        if self.editMode == None:
            return
        for field in self.fieldVar:
            valueType = self.fieldTypes[field]
            value = self.fieldVar[field].get()
            if validateField(valueType, value):
                self.root.saveField(self.key, self.id, field, getFieldValue(valueType, value))
                
        if self.listSaveFunction != None:
            index = self.listIndex
            self.listSaveFunction(self.baseId)
            self.setItem(index)
        
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
        
    def navigateToItem(self, offset):
        if self.editMode == None or (self.listIndex + offset) < 0 or (self.listIndex + offset) >= len(self.itemList):
            return
        self.setItem(self.listIndex + offset)
        
    def enableNavigator(self, itemLabel):
        navigatorFrame = Frame(self.container)
        navigatorFrame.pack(side='bottom', fill='x')
       
        navigatorLabel = Label(navigatorFrame)
        navigatorLabel.pack(side='top')
        
        prevButton = Button(navigatorFrame, text="<< Previous %s" % (itemLabel), command=lambda : self.navigateToItem(-1))
        prevButton.pack(fill='x', side='left', expand=True)
        
        nextButton = Button(navigatorFrame, text="Next %s >>" % (itemLabel), command=lambda : self.navigateToItem(1))
        nextButton.pack(fill='x', side='right', expand=True)
        
        self.navigatorLabel = navigatorLabel
        
    def initFields(self):
        fields = sortKeys(self.fieldTypes.keys())
        
        for field in fields:
            container = Frame(self.container)
            container.pack(side='top', anchor='n', fill='both')

            fieldLabel = Label(container, text=field, width=15)
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
        details.pack(side='bottom', fill='x')
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
        self.root.setReactionList(reactionlistId)
            
class ReactionListEditor(FormEditor):
    def __init__(self, root, rootFrame, col, row):
        FormEditor.__init__(self, root, rootFrame, 'reaction_list', col, row)
        
        self.westernFrame = Frame(self.container)
        self.westernFrame.pack(side='left', fill='both', expand=True)
        
        self.easternFrame = Frame(self.container)
        self.easternFrame.pack(side='right', fill='both', expand=True)
        
        self.initFields()
            
    def setItem(self, itemData, itemId):
        self.id = itemId
        self.setLabel("Reaction list %d: Pushback & Move IDs" % (itemId))
        
        self.editMode = None
        for field in itemData:
            if field in reactionlistFields:
                self.setField(field, itemData[field], True)
                self.fieldInput[field].config(state='enabled')
        self.editMode = True

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
        #self.enableDetailsArea()
        
        self.initFields()
        
    def setDetails(self):
        return
        
        """
        propId = self.fieldValue['id']
        getDetails = getProperty if self.root.movelist['version'] == 'Tekken7' else getTag2ExtraMoveProperty
        
        details = getDetails(propId)
        
        if details != None and details['desc'] != 'MAPPING' and not details['desc'].startswith('('):
            text = details['desc']
        else:
            text = ''
        self.details['text'] = text
        """
            
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
            
class RequirementEditor(FormEditor):
    def __init__(self, root, rootFrame, col, row):
        FormEditor.__init__(self, root, rootFrame, 'requirements', col, row)
        self.setListOnsaveFunction(self.root.setRequirementList)
        self.enableNavigator(itemLabel='Req')
        self.enableDetailsArea()
        
        self.initFields()
        
    def setDetails(self):
        reqId = self.fieldValue['req']
        getDetails = getRequirement if self.root.movelist['version'] == 'Tekken7' else getTag2Requirement
        
        details = getDetails(reqId)
        
        if details != None and details['desc'] != 'MAPPING' and not details['desc'].startswith('('):
            text = '%d: %s' % (reqId, details['desc'])
        else:
            text = ''
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
            
class CancelEditor(FormEditor):
    def __init__(self, root, rootFrame, col, row):
        FormEditor.__init__(self, root, rootFrame, 'cancels', col, row)
        self.setListOnsaveFunction(self.root.setCancelList)
        self.enableNavigator(itemLabel='Cancel')
        self.enableDetailsArea()
        
        self.initFields()
        
        self.registerFieldButtons([
            ('move_id', self.root.setMove),
            ('requirement_idx', self.root.setRequirementList),
        ])
        
    def onchange(self, field, sv):
        if self.editMode == None:
            return
        super().onchange(field, sv)
        self.setCommandLabel()
        
    def setCommandLabel(self):
        command = self.fieldValue['command']
        moveId = self.fieldValue['move_id']
        moveName = self.root.getMoveName(moveId)
        
        text =  "Command: " + getCommandStr(command) + "\nMove: " + moveName
        self.details['text'] = text
            
    def setItem(self, index):
        cancelData = self.itemList[index]
        self.listIndex = index
        self.id = self.baseId + index
        
        cancelLen = len(self.itemList)
        
        cancelCount = " %d cancels" % (cancelLen) if cancelLen > 1 else "1 cancel" 
        self.setLabel("Cancel list %d: %s" % (self.baseId, cancelCount))
        
        self.navigatorLabel['text'] = "Cancel %d/%d" % (index + 1, cancelLen)
        
        self.editMode = None
        for field in cancelData:
            if field in cancelFields:
                self.setField(field, cancelData[field], True)
                self.fieldInput[field].config(state='enabled')
        self.editMode = True
        
        self.setCommandLabel()
    
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
        
    def selectCancel(self, event):
        if self.editMode == None:
            return
        self.root.setCancelList(self.fieldValue['cancel_idx'])
        
    def selectExtraprop(self, event):
        if self.editMode == None:
            return
        self.root.setExtrapropList(self.fieldValue['extra_properties_idx'])
        
def splitFrame(root, split, bg=None):
    rowCount = 1 + (split == 'horizontal')
    colCount = 1 + (split == 'vertical')
    newFrame = Frame(root, bg=bg)
    
    for i in range(rowCount):
        newFrame.grid_rowconfigure(i, weight=1, uniform='group1' )
    for i in range(colCount):
        newFrame.grid_columnconfigure(i, weight=1, uniform='group1' )
    return newFrame

class GUI_TekkenMovesetEditor():
    def __init__(self, showCharacterSelector=True, mainWindow=True):
        window = Tk() if mainWindow else Toplevel()
        self.window = window
        
        self.setTitle()
        window.iconbitmap('InterfaceData/renge.ico')
        window.minsize(960, 540)
        window.geometry("1280x720")
        
        self.Charalist = CharalistSelector(self, window)
        self.MovelistSelector = MovelistSelector(self, window)
        
        editorFrame = Frame(window)
        editorFrame.pack(side='right', fill='both', expand=1)
        for i in range(2):
            editorFrame.grid_columnconfigure(i, weight=1, uniform="group1")
            editorFrame.grid_rowconfigure(i, weight=1, uniform="group1")
            
        topRightFrame = splitFrame(editorFrame, 'vertical')
        topRightFrame.grid(row=0, column=1, sticky="nsew")
            
        reqAndPropsFrame = splitFrame(topRightFrame, split='horizontal')
        reqAndPropsFrame.grid(row=0, column=1, sticky="nsew")
        
        bottomLeftFrame = splitFrame(editorFrame, 'vertical')
        bottomLeftFrame.grid(row=1, column=0, sticky="nsew")
        
        
        self.MoveEditor = MoveEditor(self, editorFrame, col=0, row=0)
        self.CancelEditor = CancelEditor(self, topRightFrame, col=0, row=0)
        self.RequirementEditor = RequirementEditor(self, reqAndPropsFrame, col=0, row=0)
        self.ExtrapropEditor = ExtrapropEditor(self, reqAndPropsFrame, col=0, row=1)
        self.HitConditionEditor = HitConditionEditor(self, bottomLeftFrame, col=1, row=0)
        self.ReactionListEditor = ReactionListEditor(self, editorFrame, col=1, row=1)
        
        
        #moveFrame2 = Frame(editorFrame, bg='#999')
        #moveFrame2.grid(row=1, column=1, sticky="nsew")
        
        
        menuActions = [
            ('Toggle character selector', self.Charalist.toggleVisibility),
            ("Load to P1", lambda self=self : self.Charalist.loadToPlayer(0) ),
            ("Load to P2", lambda self=self : self.Charalist.loadToPlayer(1) )
        ]
        
        
        menubar = Menu(window)
        for label, command in menuActions:
            menubar.add_command(label=label, command=command)
        window.config(menu=menubar)
        
        self.movelist = None
        
        if showCharacterSelector:
            self.updateCharacterlist()
        else:
            self.setCharaFrame.toggleVisibility()
            
        self.resetForms()
            
    def setTitle(self, label = ""):
        title = "TekkenMovesetEditor 0.8-BETA"
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
        
    def getMoveId(self, moveId):
        return self.movelist['aliases'][moveId - 0x8000] if moveId >= 0x8000 else moveId
        
    def setMove(self, moveId):
        moveId = self.getMoveId(moveId)
        if moveId < 0 or moveId >= len(self.movelist['moves']):
            return
        moveData = self.movelist['moves'][moveId]
        self.MoveEditor.setMove(moveData, moveId)
        self.MovelistSelector.movelistSelect.select_set(moveId)
        self.MovelistSelector.movelistSelect.see(moveId)
        
    def setReactionList(self, itemId):
        if itemId < 0 or itemId >= len(self.movelist['reaction_list']):
            return
        itemData = self.movelist['reaction_list'][itemId]
        self.ReactionListEditor.setItem(itemData, itemId)
        
    def getMoveName(self, moveId):
        moveId = self.getMoveId(moveId)
        return self.movelist['moves'][moveId]['name']
        
    def setCancelList(self, cancelId):
        if cancelId < 0 or cancelId >= len(self.movelist['cancels']):
            return
        cancelList = []
        id = cancelId
        while self.movelist['cancels'][id]['command'] != 0x8000:
            id += 1
        cancelList = [cancel for cancel in self.movelist['cancels'][cancelId:id + 1]]
        self.CancelEditor.setItemList(cancelList, cancelId)
        
    def setRequirementList(self, requirementId):
        if requirementId < 0 or requirementId >= len(self.movelist['requirements']):
            return
        reqList = []
        id = requirementId
        endValue = 881 if self.movelist['version'] == 'Tekken7' else 690
        while self.movelist['requirements'][id]['req'] != endValue:
            id += 1
        reqList = [req for req in self.movelist['requirements'][requirementId:id + 1]]
        self.RequirementEditor.setItemList(reqList, requirementId)
        
    def setExtrapropList(self, propId):
        if propId < 0 or propId >= len(self.movelist['extra_move_properties']):
            return
        propList = []
        id = propId
        while self.movelist['extra_move_properties'][id]['type'] != 0:
            id += 1
        propList = [prop for prop in self.movelist['extra_move_properties'][propId:id + 1]]
        self.ExtrapropEditor.setItemList(propList, propId)
        
    def setConditionList(self, itemId):
        if itemId < 0 or itemId >= len(self.movelist['hit_conditions']):
            return
        itemList = []
        id = itemId
        reqEndValue = 881 if self.movelist['version'] == 'Tekken7' else 690
        while True:
            reqIdx = self.movelist['hit_conditions'][id]['requirement_idx'] 
            if self.movelist['requirements'][reqIdx]['req'] == reqEndValue:
                break
            id += 1
        itemList = [item for item in self.movelist['hit_conditions'][itemId:id + 1]]
        self.HitConditionEditor.setItemList(itemList, itemId)
        
    def saveField(self, key, id, field, value):
        self.movelist[key][id][field] = value
        

if __name__ == "__main__":
    app = GUI_TekkenMovesetEditor()
    app.window.mainloop()
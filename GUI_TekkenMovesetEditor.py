# Python 3.6.5

from tkinter import Tk, Frame, Listbox, Label, Scrollbar, StringVar, Toplevel
from tkinter.ttk import Button, Entry
from Addresses import game_addresses, GameClass
import motbinImport as importLib
import json
import os
import re
from zlib import crc32

charactersPath = "./extracted_chars/"

fieldLabels = {
    'name': 'Name',
    'anim_name': 'Anim',
    'vuln': 'Vuln',
    'hitlevel': 'Hitlevel',
    'cancel_idx': 'Cancel idx',
    'transition': 'Transition',
    'anim_max_len': 'Anim len',
    'u17': 'Distance'
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

fieldsTypes = {
    'moves': moveFields,
    'cancels': cancelFields
}
    
def getCharacterList():
    if not os.path.isdir(charactersPath):
        return []
    folders = [folder for folder in os.listdir(charactersPath) if os.path.isdir(charactersPath + folder)]
    
    return sorted(folders)
    
def getMovelist(path):
    jsonFilename = next(file for file in os.listdir(path) if file.endswith(".json"))
    with open('%s/%s' % (path, jsonFilename)) as f:
        return json.load(f), jsonFilename
        
def sortKeys(keys):
    keyList = [key for key in keys if not re.match("^u[0-9_]+$", key) and key != "id"]
    unknownKeys = [key for key in keys if re.match("^u[0-9_]+$", key)]
    return keyList + unknownKeys
        
def validateField(type, value):
    if type == 'number':
        return re.match("^-?[0-9]+$", value)
    if type == 'hex' or type == '8hex':
        return re.match("^0x[0-9A-Za-z]+$", value)
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
            ("Select Moveset", self.selectMoveset),
            ("Load to P1", lambda self=self : self.loadToPlayer(0) ),
            ("Load to P2", lambda self=self : self.loadToPlayer(1) )
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
       
    def hide(self):
        self.frame.pack_forget()
        
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
            self.charaSelect.insert(0, "No moveset extracted yet...")
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
        playerAddr = game_addresses.addr['p1_addr'] + (playerId * game_addresses.addr['playerstruct_size'])
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
        
class MovelistSelector:
    def __init__(self, root, rootFrame):
        self.root = root
        movelistFrame = Frame(rootFrame)
        movelistFrame.pack(side='left', fill='y')
        
        newButton = Button(movelistFrame, text='Save', command=self.root.save)
        newButton.pack(side='bottom', fill='x')
        
        selectedChar = Label(movelistFrame, text="No character selected", bg='#bbb')
        selectedChar.pack(side='bottom', fill='x')
        
        movelistSelect = Listbox(movelistFrame, width=30)
        movelistSelect.bind('<<ListboxSelect>>', self.onMoveSelection)
        movelistSelect.pack(side='left', fill='both')
        
        scrollbar = Scrollbar(movelistFrame, command=movelistSelect.yview)
        scrollbar.pack(side='right', fill='y')
        
        movelistSelect.config(yscrollcommand=scrollbar.set)
        
        self.selectedChar = selectedChar
        self.movelistSelect = movelistSelect
        
    def onMoveSelection(self, event):
        w = event.widget
        moveId = -1
        try:
            moveId = int(w.curselection()[0])
        except:
            pass
        finally:
            self.root.setMove(moveId)
        
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
        
        self.initEditor(col, row)
        
    def initEditor(self, col, row):
        container = Frame(self.rootFrame, bg='pink')
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
        
    def save(self):
        if self.editMode == None:
            return
        for field in self.fieldVar:
            valueType = self.fieldTypes[field]
            value = self.fieldVar[field].get()
            if validateField(valueType, value):
                self.root.movelist[self.key][self.id][field] = getFieldValue(valueType, value)
        
    def setField(self, field, value):
        self.editMode = None
        self.fieldVar[field].set(value)
        
        if field not in self.fieldValue:
            self.fieldValue[field] = value
            
        self.editMode = True
        
    def resetForm(self):
        self.editMode = None
        self.id = None
        self.setLabel("No item selected")
        self.fieldValue = {}
        for field in self.fieldTypes.keys():
            if field in self.fieldVar:
                self.fieldVar[field].set('')
                self.fieldInput[field].config(state='disabled')
            
class CancelEditor(FormEditor):
    def __init__(self, root, rootFrame, col, row):
        FormEditor.__init__(self, root, rootFrame, 'cancels', col, row)
        
        navigatorFrame = Frame(self.container)
        navigatorFrame.pack(side='bottom', fill='x')
       
        navigatorLabel = Label(navigatorFrame)
        navigatorLabel.pack(side='top')
        
        prevCancelButton = Button(navigatorFrame, text="<< Previous Cancel", command=lambda : self.navigateToCancel(-1))
        prevCancelButton.pack(fill='x', side='left', expand=True)
        
        nextCancelButton = Button(navigatorFrame, text="Next Cancel >>", command=lambda : self.navigateToCancel(1))
        nextCancelButton.pack(fill='x', side='right', expand=True)
        
        commandLabel = Label(self.container)
        commandLabel.pack(side='bottom', fill='x')
        
        self.initFields()
        self.navigatorLabel = navigatorLabel
        self.commandLabel = commandLabel
        
        self.fieldLabel['move_id'].bind("<Button-1>", self.selectMove)
        
    def onchange(self, field, sv):
        if self.editMode == None:
            return
        super().onchange(field, sv)
        self.setCommandLabel()
        
    def selectMove(self, event):
        if self.editMode == None:
            return
        self.root.setMove(self.fieldValue['move_id'])
        
    def setCommandLabel(self):
        command = self.fieldValue['command']
        moveId = self.fieldValue['move_id']
        moveName = self.root.getMoveName(moveId)
        
        text =  "Command: " + getCommandStr(command) + "\nMove: " + moveName
        self.commandLabel['text'] = text
        
    def resetForm(self):
        self.navigatorLabel['text'] = "No cancel selected"
        self.commandLabel['text'] = ''
        super().resetForm()
        
    def save(self):
        if self.editMode == None:
            return
        super().save()
        index = self.listIndex
        self.root.setCancelList(self.baseId)
        self.setCancel(index)
        
    def navigateToCancel(self, offset):
        if self.editMode == None or (self.listIndex + offset) < 0 or (self.listIndex + offset) >= len(self.cancelList):
            return
        self.setCancel(self.listIndex + offset)
        
    def initFields(self):
        fields = sortKeys(cancelFields.keys())
        
        for field in fields:
            container = Frame(self.container)
            container.pack(side='top', anchor='n', fill='both')

            fieldLabel = Label(container, text=field, width=15)
            fieldLabel.grid(row=0, column=0, pady=2, sticky='w')
        
            if field.endswith("_idx") or field.endswith("_indexes") or field.endswith('_id'):
                fieldLabel.config(cursor='hand2', bg='#cce3e1')
            
            sv = StringVar()
            sv.trace("w", lambda name, index, mode, field=field, sv=sv: self.onchange(field, sv))

            fieldInput = Entry(container, textvariable=sv)
            fieldInput.grid(row=0, column=1, sticky='ew')
            
            self.fieldVar[field] = sv
            self.fieldInput[field] = fieldInput
            self.fieldLabel[field] = fieldLabel
            
    def setCancel(self, index):
        cancelData = self.cancelList[index]
        self.listIndex = index
        self.id = self.baseId + index
        
        self.navigatorLabel['text'] = "Cancel %d/%d" % (index + 1, len(self.cancelList))
        
        self.editMode = None
        for field in cancelData:
            if field in cancelFields:
                self.setField(field, cancelData[field])
                self.fieldInput[field].config(state='enabled')
        self.editMode = True
        
        self.setCommandLabel()
        
    def setCancelList(self, cancelList, cancelId):
        cancelCount = " %d cancels" % (len(cancelList)) if (len(cancelList) > 1) else "1 cancel" 
        self.setLabel("Cancel list %d: %s" % (cancelId, cancelCount))
        self.id = cancelId
        self.baseId = cancelId
        self.cancelList = cancelList
        self.listIndex = 0
        
        self.setCancel(0)
    
class MoveEditor(FormEditor):
    def __init__(self, root, rootFrame, col, row):
        FormEditor.__init__(self, root, rootFrame, 'moves', col, row)
        
        self.westernFrame = Frame(self.container)
        self.westernFrame.pack(side='left', fill='both', expand=True)
        
        self.easternFrame = Frame(self.container)
        self.easternFrame.pack(side='right', fill='both', expand=True)
        
        self.initFields()
        
        self.fieldLabel['cancel_idx'].bind("<Button-1>", self.selectCancel)
        
    def initFields(self):
        fields = sortKeys(moveFields.keys())
        sideBreakpoint = len(fields) / 2
        for i, field in enumerate(fields):
            container = Frame(self.westernFrame if i < sideBreakpoint else self.easternFrame)
            container.pack(side='top', anchor='n', fill='both')

            fieldLabel = Label(container, text=fieldLabels.get(field, field), width=15)
            fieldLabel.grid(row=0, column=0, sticky='w')
            
            if field.endswith("_idx") or field.endswith("_indexes") or field.endswith('_id'):
                fieldLabel.config(cursor='hand2', bg='#cce3e1')
            
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
                self.setField(field, moveData[field])
                self.fieldInput[field].config(state='enabled')
        self.editMode = True
        
    def selectCancel(self, event):
        if self.editMode == None:
            return
        self.root.setCancelList(self.fieldValue['cancel_idx'])

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
            editorFrame.grid_rowconfigure(i, weight=1)
            
        northEastFrame = Frame(editorFrame, bg='red')
        northEastFrame.grid(row=0, column=1, sticky="nsew")
        northEastFrame.grid_columnconfigure(0, weight=1, uniform="group1")
        northEastFrame.grid_columnconfigure(1, weight=1, uniform="group1")
        northEastFrame.grid_rowconfigure(0, weight=1)
        
        self.MoveEditor = MoveEditor(self, editorFrame, col=0, row=0)
        self.CancelEditor = CancelEditor(self, northEastFrame, col=0, row=0)
        
        
        moveFrame2 = Frame(editorFrame, bg='pink')
        moveFrame2.grid(row=1, column=0, sticky="nsew")
        moveFrame2 = Frame(editorFrame, bg='violet')
        moveFrame2.grid(row=1, column=1, sticky="nsew")
        
        self.movelist = None
        
        if showCharacterSelector:
            self.updateCharacterlist()
        else:
            self.hideCharaFrame()
            
        self.resetForms()
            
    def setTitle(self, label = ""):
        title = "TekkenMovesetEditor 0.1"
        if label != "":
            title += " - " + label
        self.window.wm_title(title) 

    def save(self):
        if self.Charalist.filename == None:
            return
        jsonPath = "%s/%s" % (self.Charalist.movelist_path, self.Charalist.filename)
        
        if os.path.exists(jsonPath):
            os.remove(jsonPath)
            
        with open(jsonPath, "w") as f:
            self.movelist['last_calculated_hash'] = calculateHash(self.movelist)
            json.dump(self.movelist, f, indent=4)
            
        print("Saved " + jsonPath)
        
    def hideCharaFrame(self):
        self.Charalist.hide()
        
    def updateCharacterlist(self):
        self.Charalist.updateCharacterlist()
        
    def resetForms(self):
        self.MoveEditor.resetForm()
        self.CancelEditor.resetForm()
        
    def getMoveId(self, moveId):
        return self.movelist['aliases'][moveId - 0x8000] if moveId >= 0x8000 else moveId
        
    def setMove(self, moveId):
        moveId = self.getMoveId(moveId)
        if moveId < 0 or moveId >= len(self.movelist['moves']):
            return
        moveData = self.movelist['moves'][moveId]
        self.MoveEditor.setMove(moveData, moveId)
        
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
        self.CancelEditor.setCancelList(cancelList, cancelId)
        

if __name__ == "__main__":
    app = GUI_TekkenMovesetEditor()
    app.window.mainloop()
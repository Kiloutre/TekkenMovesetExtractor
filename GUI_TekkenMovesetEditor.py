# Python 3.6.5

from tkinter import *
from tkinter.ttk import Button, Entry
from Addresses import game_addresses, GameClass
import motbinImport as importLib
import json
import os
from zlib import crc32

charactersPath = "extracted_chars/"

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
        return json.load(f)
        
def sortKeys(keys):
    keyList = [key for key in keys if not re.match("^u[0-9_]+$", key) and key != "id"]
    unknownKeys = [key for key in keys if re.match("^u[0-9_]+$", key)]
    return keyList + unknownKeys
        
def validateField(type, value):
    if type == 'number':
        return re.match("^-?[0-9]+$", value)
    if type == 'hex':
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

def calculateMovesetHash(movesetData):
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
        
class CharalistSelector:
    def __init__(self, root):
        self.root = root
        charalistFrame = Frame(root)
        charalistFrame.pack(side='left', fill=Y)
        
        charaSelect = Listbox(charalistFrame)
        charaSelect.bind('<<ListboxSelect>>', self.onCharaSelectionChange)
        charaSelect.pack(fill=BOTH, expand=1)
        
        buttons = [
            ("Select Moveset", self.selectMoveset),
            ("Load to P1", self.loadToPlayer),
            ("Load to P2", self.loadToPlayer)
        ]
        
        for label, callback in buttons:
            newButton = Button(charalistFrame, text=label, command=callback)
            newButton.pack(fill=X)
        
        self.charaSelect = charaSelect
        self.frame = charalistFrame
        
        self.characterList = []
        self.selection = None
       
    def hide(self):
        self.frame.pack_forget()
        
    def updateCharacterlist(self):
        self.selection = None
        self.charaSelect.delete(0,'end')
        
        characterList = getCharacterList()
        if len(characterList) == 0:
            self.charaSelect.insert(0, "No moveset extracted yet...")
        else:
            colors = [
                ["#fff", "#eee"], #TTT2
                ["#eee", "#ddd"]  #T7
            ]
            for i, character in enumerate(characterList):
                self.charaSelect.insert(END, character)
                color = colors[character.startswith("7_")][i & 1]
                self.charaSelect.itemconfig(i, {'bg': color })
        self.characterList = characterList

    def onCharaSelectionChange(self, event):
        if len(self.characterList) == 0:
            return
        w = event.widget
        try:
            index = int(w.curselection()[0])
            self.selection = w.get(index)
        except:
            self.selection = None
        
    def loadToPlayer(self):
        playerAddr = game_addresses.addr['p1_addr']
        TekkenImporter = importLib.Importer()
        TekkenImporter.importMoveset(playerAddr, self.movelist_path, moveset=self.root.movelist)
        
    def selectMoveset(self, selection=None):
        if selection == None and self.selection == None:
            return
        self.movelist_path = "extracted_chars/" + (self.selection if selection == None else selection)
        
        movelist = getMovelist(self.movelist_path)
        
        self.root.MovelistSelector.setMoves(movelist['moves'], movelist['aliases'])
        self.root.MovelistSelector.setCharacter(movelist['character_name'])
        self.root.movelist = movelist
        self.root.resetForms()
        
class MovelistSelector:
    def __init__(self, root):
        self.root = root
        movelistFrame = Frame(root)
        movelistFrame.pack(side='left', fill=Y)
        
        selectedChar = Label(movelistFrame, text="No character selected", bg='#bbb')
        selectedChar.pack(side=BOTTOM, fill=X)
        
        movelistSelect = Listbox(movelistFrame, width=30)
        movelistSelect.bind('<<ListboxSelect>>', root.onMoveSelection)
        movelistSelect.pack(side=LEFT, fill=BOTH)
        
        scrollbar = Scrollbar(movelistFrame)
        scrollbar.pack(side=RIGHT, fill=Y)
        scrollbar.config(command=movelistSelect.yview)
        
        movelistSelect.config(yscrollcommand=scrollbar.set)
        
        self.selectedChar = selectedChar
        self.movelistSelect = movelistSelect
        
    def setCharacter(self, char):
        self.selectedChar['text'] = 'Current character: ' + char
        
    def setMoves(self, moves, aliases):
        moves = [(i, move['hitlevel'] and move['first_active_frame'] and move['last_active_frame'] and move['hitbox_location'], move['name']) for i, move in enumerate(moves)]
        self.movelistSelect.delete(0,'end')
        for moveId, isAttack, moveName in moves:
            text = "%d   %s" % (moveId, moveName)
            bg = None
            
            if moveId in aliases:
                bg = '#b5caff'
                text += "   (%d)" % (32768 + aliases.index(moveId))
            elif isAttack:
                bg = '#ffbdbd'
                
            self.movelistSelect.insert(END, text)
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
        self.fields = {}
        self.fieldsInputs = {}
        self.fieldValues = {}
        self.container = None
        
        self.initEditor(col, row)
        
    def initEditor(self, col, row):
        container = Frame(self.rootFrame, bg='pink')
        container.grid(row=row, column=col, sticky="nsew")
        container.pack_propagate(False)
        
        label = Label(container, bg='#ddd')
        label.pack(side='top', fill=X)
        
        saveButton = Button(container, text="Apply", command=self.save)
        saveButton.pack(side='bottom', fill=X)
        
        self.container = container
        self.label = label
        
    def setLabel(self, text):
        self.label['text'] = text
    
    def onchange(self, field, sv):
        if self.editMode == None:
            return
        value = sv.get()
        valueType = self.fieldTypes[field]
        if not validateField(valueType, value):
            self.setField(field, self.fieldValues[field])
        else:
            self.setField(field, getFieldValue(valueType, value))
        
    def save(self):
        if self.editMode == None:
            return
        for field in self.fields:
            valueType = self.fieldTypes[field]
            value = self.fields[field].get()
            if validateField(valueType, value):
                self.root.movelist[self.key][self.id][field] = getFieldValue(valueType, value)
        
    def setField(self, field, value):
        self.editMode = None
        self.fieldValues[field] = value
        
        valueType = self.fieldTypes[field]
        value = formatFieldValue(valueType, value)
        self.fields[field].set(value)
        
        self.editMode = True
        
    def resetForm(self):
        self.editMode = None
        self.id = None
        self.setLabel("No item selected")
        for field in self.fieldTypes.keys():
            self.fields[field].set('')
            
class CancelEditor(FormEditor):
    def __init__(self, root, rootFrame, col, row):
        FormEditor.__init__(self, root, rootFrame, 'cancels', col, row)
        
        navigatorFrame = Frame(self.container)
        navigatorFrame.pack(side='bottom', fill=X)
        
        prevCancelButton = Button(navigatorFrame, text="<< Previous Cancel", command=lambda : self.navigateToCancel(-1))
        prevCancelButton.pack(fill=X, side='left', expand=True)
        
        nextCancelButton = Button(navigatorFrame, text="Next Cancel >>", command=lambda : self.navigateToCancel(1))
        nextCancelButton.pack(fill=X, side='right', expand=True)
        
        
        self.initFields()
        
    def navigateToCancel(self, offset):
        if self.editMode == None:
            return
        self.root.setCancelList(self.id + offset)
        
    def initFields(self):
        fields = sortKeys(cancelFields.keys())
        for field in fields:
            container = Frame(self.container)
            container.pack(side='top', anchor=N, fill=BOTH)

            fieldLabel = Label(container, text=field, width=15)
            fieldLabel.grid(row=0, column=0, pady=2, sticky='w')
            
            if field.endswith("_idx") or field.endswith("_indexes") or field.endswith('_id'):
                fieldLabel['bg'] = '#cce3e1'
            
            sv = StringVar()
            sv.trace("w", lambda name, index, mode, field=field, sv=sv: self.onchange(field, sv))
            self.fields[field] = sv

            fieldInput = Entry(container, textvariable=sv)
            fieldInput.grid(row=0, column=1, sticky='ew')
            self.fieldsInputs[field] = fieldInput
        
    def setCancel(self, cancelData, cancelId):
        cancelCount = " %d cancels" % (len(cancelData)) if (len(cancelData) > 1) else "1 cancel" 
        self.setLabel("Cancel list %d: %s" % (cancelId, cancelCount))
        self.id = cancelId
        cancelData = [0]
            
        self.editMode = None
        for field in cancelData:
            if field in cancelFields:
                self.setField(field, cancelData[field])
        self.editMode = True
    
class MoveEditor(FormEditor):
    def __init__(self, root, rootFrame, col, row):
        FormEditor.__init__(self, root, rootFrame, 'moves', col, row)
        
        self.westernFrame = Frame(self.container)
        self.westernFrame.pack(side='left', fill=BOTH, expand=True)
        
        self.easternFrame = Frame(self.container)
        self.easternFrame.pack(side='right', fill=BOTH, expand=True)
        
        self.initFields()
        
        self.fieldsInputs['cancel_idx'].bind("<Button-1>", self.selectCancel)
        
    def initFields(self):
        fields = sortKeys(moveFields.keys())
        sideBreakpoint = len(fields) / 2
        for i, field in enumerate(fields):
            container = Frame(self.westernFrame if i < sideBreakpoint else self.easternFrame)
            container.pack(side='top', anchor=N, fill=BOTH)

            fieldLabel = Label(container, text=field, width=15)
            fieldLabel.grid(row=0, column=0, sticky='w')
            
            if field.endswith("_idx") or field.endswith("_indexes") or field.endswith('_id'):
                fieldLabel['bg'] = '#cce3e1'
            
            sv = StringVar()
            sv.trace("w", lambda name, index, mode, field=field, sv=sv: self.onchange(field, sv))
            self.fields[field] = sv

            fieldInput = Entry(container, textvariable=sv)
            fieldInput.grid(row=0, column=1, sticky='ew')
            self.fieldsInputs[field] = fieldInput
        
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
        self.editMode = True
        
    def selectCancel(self, event):
        if self.editMode == None:
            return
        self.root.setCancelList(self.fieldValues['cancel_idx'])


class GUI_TekkenMovesetExtractor(Tk):
    def __init__(self):
        Tk.__init__(self)
        
        self.wm_title("TekkenMovesetEditor 0.1") 
        self.iconbitmap('InterfaceData/renge.ico')
        self.minsize(960, 540)
        self.geometry("1280x720")
        
        self.Charalist = CharalistSelector(self)
        self.MovelistSelector = MovelistSelector(self)
        
        editorFrame = Frame(self)
        editorFrame.pack(side='right', fill=BOTH, expand=1)
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
        
        self.updateCharacterlist()
        self.Charalist.selectMoveset("7_JIN")
        #self.hideCharaFrame()
        
    def hideCharaFrame(self):
        self.Charalist.hide()
        
    def updateCharacterlist(self):
        self.Charalist.updateCharacterlist()
        
    def onMoveSelection(self, event):
        w = event.widget
        moveId = -1
        try:
            moveId = int(w.curselection()[0])
        except:
            pass
        finally:
            self.setMove(moveId)
        
    def resetForms(self):
        self.MoveEditor.resetForm()
        self.CancelEditor.resetForm()
        
    def setMove(self, moveId):
        if moveId < 0 or moveId >= len(self.movelist['moves']):
            return
        moveData = self.movelist['moves'][moveId]
        self.MoveEditor.setMove(moveData, moveId)
        
    def setCancelList(self, cancelId):
        if cancelId < 0 or cancelId >= len(self.movelist['cancels']):
            return
        cancelList = []
        id = cancelId + 1
        while self.movelist['cancels'][id]['command'] != 0x8000:
            id += 1
        cancelList = [cancel for cancel in self.movelist['cancels'][cancelId:id + 1]]
        self.CancelEditor.setCancel(cancelList, cancelId)
        

if __name__ == "__main__":
    app = GUI_TekkenMovesetExtractor()
    app.mainloop()
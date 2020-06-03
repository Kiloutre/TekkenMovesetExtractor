# Python 3.6.5

from tkinter import *
from tkinter.ttk import Button, Entry
from Addresses import game_addresses, GameClass
import motbinImport as importLib
import json
import os

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
    'hitbox_location': 'number',
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
            newButton = Button(charalistFrame)
            newButton["text"] = label
            newButton["command"] = callback
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
            self.charaSelect.insert(0, *characterList)
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
        TekkenImporter.importMoveset(playerAddr, self.movelist_path, moveset=self.movelist)
        
    def selectMoveset(self, selection=None):
        if selection == None and self.selection == None:
            return
        self.movelist_path = "extracted_chars/" + (self.selection if selection == None else selection)
        
        movelist = getMovelist(self.movelist_path)
        
        moveNames = ["%d   %s" % (i, move['name']) for i, move in enumerate(movelist['moves'])]
        self.root.MovelistSelector.setMoves(moveNames)
        self.root.MovelistSelector.setCharacter(movelist['character_name'])
        self.root.movelist = movelist
        self.root.resetForms()
        
class MovelistSelector:
    def __init__(self, root):
        self.root = root
        movelistFrame = Frame(root)
        movelistFrame.pack(side='left', fill=Y)
        
        selectedChar = Label(movelistFrame, text="No selected char")
        selectedChar.pack()
        
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
        self.selectedChar['text'] = char
        
    def setMoves(self, moves):
        self.movelistSelect.delete(0,'end')
        for m in moves: self.movelistSelect.insert(END, m)
        
class MoveEditor:
    def __init__(self, rootFrame):
        container = Frame(rootFrame, bg='#999')
        container.grid(row=0, column=0, sticky="nsew")
        container.pack_propagate(False)
        
        moveLabel = Label(container, bg='#eee')
        moveLabel.pack(side='top', fill=X)
        
        self.westernFrame = Frame(container, bg='blue')
        self.westernFrame.pack(side='left', fill=BOTH, expand=True)
        
        self.easternFrame = Frame(container, bg='red')
        self.easternFrame.pack(side='right', fill=BOTH, expand=True)
        
        self.moveId = None
        self.editMode = None
        self.moveLabel = moveLabel
        self.fields = {}
        self.initFields()
        self.resetForm()
        
    def initFields(self):
        fields = sortKeys(moveFields.keys())
        sideBreakpoint = len(fields) / 2
        for i, field in enumerate(fields):
            container = Frame(self.westernFrame if i < sideBreakpoint else self.easternFrame)
            container.pack(side='top', anchor=NW, expand=False)

            fieldLabel = Label(container, text=field, width=15)
            fieldLabel.grid(row=0, column=0, sticky='w')
            
            sv = StringVar()
            sv.trace("w", lambda name, index, mode, field=field, sv=sv: self.onchange(field, sv))
            self.fields[field] = sv

            fieldInput = Entry(container, textvariable=sv)
            fieldInput.grid(row=0, column=1, sticky='ew')
    
    def onchange(self, field, sv):
        if self.editMode == None:
            return
        value = sv.get()
        print(field, value)
        
    def resetForm(self):
        self.editMode = None
        self.moveLabel['text'] = "No move selected"
        self.moveId = None
        for field in moveFields.keys():
            self.fields[field].set('')
        
    def setMove(self, moveData, moveId):
        self.editMode = None
        self.moveLabel['text'] = "(%s)    Move %d: %s" % (moveId, moveData['name'])
        self.moveId = moveId
            
        for field in moveData:
            if field in moveFields:
                self.fields[field].set(moveData[field])
        self.editMode = True

class GUI_TekkenMovesetExtractor(Tk):
    def __init__(self):
        Tk.__init__(self)
        
        self.wm_title("TekkenMovesetEditor 0.1") 
        self.iconbitmap('GUI_TekkenMovesetExtractor/renge.ico')
        self.minsize(960, 540)
        self.geometry("1280x720")
        
        self.Charalist = CharalistSelector(self)
        self.MovelistSelector = MovelistSelector(self)
        
        editorFrame = Frame(self)
        editorFrame.pack(side='right', fill=BOTH, expand=1)
        for i in range(2):
            editorFrame.grid_columnconfigure(i, weight=1, uniform="group1")
            editorFrame.grid_rowconfigure(i, weight=1)
        
        self.MoveEditor = MoveEditor(editorFrame)
        
        moveFrame2 = Frame(editorFrame, bg='green')
        moveFrame2.grid(row=0, column=1, sticky="nsew")
        moveFrame2 = Frame(editorFrame, bg='pink')
        moveFrame2.grid(row=1, column=0, sticky="nsew")
        moveFrame2 = Frame(editorFrame, bg='violet')
        moveFrame2.grid(row=1, column=1, sticky="nsew")
        
        self.movelist = None
        
        self.updateCharacterlist()
        self.Charalist.selectMoveset("2_JIN")
        self.hideCharaFrame()
        
    def hideCharaFrame(self):
        self.Charalist.hide()
        
    def updateCharacterlist(self):
        self.Charalist.updateCharacterlist()
        
    def resetForms(self):
        self.MoveEditor.resetForm()
        
    def onMoveSelection(self, event):
        w = event.widget
        try:
            move_id = int(w.curselection()[0])
            moveData = self.movelist['moves'][move_id]
            self.MoveEditor.setMove(moveData, move_id)
        except Exception as e:
            print(e)
            pass
        

if __name__ == "__main__":
    app = GUI_TekkenMovesetExtractor()
    app.mainloop()
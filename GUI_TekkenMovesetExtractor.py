# Python 3.6.5

from tkinter import *
from tkinter.ttk import Button
from re import match
from Addresses import game_addresses, GameClass
import sys
import os
import json
import time
import threading
import motbinExport as exportLib
import motbinImport as importLib

charactersPath = "./extracted_chars/"

monitorVerificationFrequency = 0.25
runningMonitors = [None, None]
creatingMonitor = [False, False]

def monitoringFunc(playerAddr, playerId, Tekken, moveset):
    monitorId = playerId - 1
    try:
        prevMoveset = Tekken.readInt(playerAddr + 0x14a0, 8)
        while runningMonitors[monitorId] != None:
            currMoveset = Tekken.readInt(playerAddr + 0x14a0, 8)
            if currMoveset != prevMoveset:
                print("Player %d: Moveset change noticed, cancelling change" % (playerId))
                moveset.copyUnknownOffsets(currMoveset)
                Tekken.writeInt(playerAddr + 0x14a0, moveset.motbin_ptr, 8)
            time.sleep(monitorVerificationFrequency)
        print("Monitor %d closing" % (playerId))
    except Exception as e:
        print(e)
        print("Monitor %d closing because of error" % (playerId))
        runningMonitors[monitorId] = None
        sys.exit(1)
    
def startMonitor(parent, playerId):
    if parent.selected_char == None:
        print("No character selected")
        return
    print("Starting monitor for p%d..." % (playerId))
    monitorId = playerId - 1
    creatingMonitor[monitorId] = True
    
    Tekken = GameClass("TekkenGame-Win64-Shipping.exe")
    folderPath = charactersPath + parent.selected_char 
    
    TekkenImporter = importLib.Importer()
    playerAddr = game_addresses['p%d_addr' % (playerId)]
    moveset = TekkenImporter.importMoveset(playerAddr, folderPath)
        
    monitor = threading.Thread(target=monitoringFunc, args=(playerAddr, playerId, Tekken, moveset))
    monitor.start()
    runningMonitors[monitorId] = monitor
    creatingMonitor[monitorId] = False
    
def getCharacterList():
    if not os.path.isdir(charactersPath):
        os.mkdir(charactersPath)
    folders = [folder for folder in os.listdir(charactersPath)]
    
    return sorted(folders)
    
def exportCharacter(parent, tekkenVersion, playerAddr, name=''):
    TekkenExporter = exportLib.Exporter(tekkenVersion, folder_destination=charactersPath)
    TekkenExporter.exportMoveset(playerAddr, name)
    parent.updateCharacterlist()
    
def exportAll(parent, tekkenVersion, key_match):
    player_addresses = [game_addresses[key] for key in game_addresses if match(key_match, key)]
    TekkenExporter = exportLib.Exporter(tekkenVersion)
    
    exportedMovesets = []
    
    for playerAddr in player_addresses:
        moveset_name = TekkenExporter.getPlayerMovesetName(playerAddr)
        if moveset_name not in exportedMovesets:
            print("Requesting export for %s..." % (moveset_name))
            moveset = TekkenExporter.exportMoveset(playerAddr)
            exportedMovesets.append(moveset_name)
            print()
        else:
            print('Player', moveset_name, 'already exported, not exporting again.')
            
    print('\nSuccessfully exported:')
    for name in exportedMovesets:
        print(name)
        
    parent.updateCharacterlist()
        
def importPlayer(parent, playerId):
    if parent.selected_char == None:
        print("No character selected")
        return
    folderPath = charactersPath + parent.selected_char 
    playerAddr = game_addresses['p%d_addr' % (playerId)]
    
    TekkenImporter = importLib.Importer()
    TekkenImporter.importMoveset(playerAddr, folderPath)
        
class TextRedirector(object):
    def __init__(self, TextArea, tag=''):
        self.TextArea = TextArea
        self.tag = tag
        
    def write(self, str):
        self.TextArea.configure(state="normal")
        self.TextArea.insert("end", str, (self.tag,))
        self.TextArea.configure(state="disabled")
        self.TextArea.see('end')
        self.TextArea.update()
        
    def flush(self):
        pass
        
class GUI_TekkenMovesetExtractor(Tk):
    def __init__(self):
        Tk.__init__(self)
        
        self.characterList = getCharacterList()
        self.selected_char = None
        self.chara_data = None
        
        self.wm_title("TekkenMovesetExtractor 0.7") 
        self.iconbitmap('GUI_TekkenMovesetExtractor/natsumi.ico')
        self.minsize(960, 540)
        self.geometry("960x540")
        
        self.consoleFrame = Frame(self, bg='#CCC')
        self.toolFrame = Frame(self, bg='pink')
        
        self.consoleFrame.grid(row=0, column=0, sticky="nsew")
        self.toolFrame.grid(row=0, column=1, sticky="nsew")
        
        self.grid_columnconfigure(0, weight=1, uniform="group1")
        self.grid_columnconfigure(1, weight=1, uniform="group1")
        self.grid_rowconfigure(0, weight=1)
        
        self.initConsoleArea()
        self.initToolArea()
        self.initExportArea()
        self.initImportArea()
        self.initImportActionsArea()
        
        self.createExportButtons()
        self.createCharacterList()
        
        try:
            with open("GUI_TekkenMovesetExtractor/readme.txt") as f:
                for line in f: print(line)
        except:
            pass
            
    def setMonitorButton(self, button, active):
        if active:
            self.monitorButtons[button]['text'] = 'Kill P%d Monitor' % (button + 1)
        else:
            self.monitorButtons[button]['text'] = 'Monitor P%d' % (button + 1)
        
    def initImportArea(self):
        self.charalistFrame = Frame(self.importFrame, bg='purple')
        self.charalistActions = Frame(self.importFrame, bg='green')
        
        self.charalistFrame.grid(row=0, column=0, sticky="nsew")
        self.charalistActions.grid(padx=15, row=0, column=1, sticky="nsew")
        
        
        self.importFrame.grid_columnconfigure(0, weight=1, uniform="group1")
        self.importFrame.grid_columnconfigure(1, weight=1, uniform="group1")
        self.importFrame.grid_rowconfigure(0, weight=1)
        
    def initImportActionsArea(self):
        self.charaInfoFrame = Frame(self.charalistActions, bg='purple')
        self.importButtonFrame = Frame(self.charalistActions, bg='green')
        
        self.charaInfoFrame.grid(row=0, column=0, sticky="nsew")
        self.importButtonFrame.grid(row=1, column=0, sticky="nsew")
        
        
        self.charalistActions.grid_columnconfigure(0, weight=1)
        self.charalistActions.grid_rowconfigure(0, weight=1, uniform="group1")
        self.charalistActions.grid_rowconfigure(1, weight=1, uniform="group1")
        
        
        self.selectionInfo = Label(self.charaInfoFrame, text="")
        self.selectionInfo.pack(side='top')
        button = self.createButton(self.charaInfoFrame, "Update list", (), GUI_TekkenMovesetExtractor.updateCharacterlist, side='bottom', expand='0')
        
    def initExportArea(self):
        self.t7_exportFrame = Frame(self.exportFrame, bg='red')
        self.tag2_exportFrame = Frame(self.exportFrame, bg='red')
        
        self.t7_exportFrame.grid(padx=18, pady=5, row=0, column=0, sticky="nsew")
        self.tag2_exportFrame.grid(padx=18, pady=5, row=0, column=1, sticky="nsew")
        
        
        self.exportFrame.grid_columnconfigure(0, weight=1, uniform="group1")
        self.exportFrame.grid_columnconfigure(1, weight=1, uniform="group1")
        self.exportFrame.grid_rowconfigure(0, weight=1)
        
    def initToolArea(self):
        self.exportFrame = Frame(self.toolFrame, bg='red')
        self.importFrame = Frame(self.toolFrame, bg='blue')
        
        self.exportFrame.grid(padx=10, pady=5, row=0, column=0, sticky="nsew")
        self.importFrame.grid(padx=10, pady=5, row=1, column=0, sticky="nsew")
        
        
        self.toolFrame.grid_columnconfigure(0, weight=1)
        self.toolFrame.grid_rowconfigure(0, weight=1, uniform="group1")
        self.toolFrame.grid_rowconfigure(1, weight=1, uniform="group1")
        
    def initConsoleArea(self):
        TextArea = Text(self.consoleFrame, wrap="word")
        TextArea.configure(state="disabled")
        TextArea.tag_configure("err", foreground="#f2114d", background="#dddddd")
        TextArea.pack(padx=10, pady=5, fill=BOTH, expand=1)
        
        sys.stdout = TextRedirector(TextArea)
        sys.stderr = TextRedirector(TextArea, "err")
        
    def updateCharacterlist(self):
        self.characterList = getCharacterList()
        self.charaList.delete(0,'end')
        self.selected_char = None
        if len(self.characterList) == 0:
            self.charaList.insert(0, "No moveset extracted yet...")
        else:
            self.charaList.insert(0, *self.characterList)
            
    def loadCharaInfo(self):
        path = charactersPath + self.selected_char
        try:
            json_file = next(file for file in os.listdir(path) if file.endswith(".json"))
            with open(path + '/' + json_file, "r") as f:
                m = json.load(f)
                f.close
                self.chara_data = [
                    "Moveset name: %s" % (m['character_name']),
                    "Character: %s" % (m['tekken_character_name']),
                    "Tekken Version: %s" % (m['version']),
                    "Exporter version: %s" % (m['export_version']),
                ]
        except Exception as e:
            self.chara_data = [ "Invalid moveset" ]
        self.selectionInfo['text'] = '\n'.join(self.chara_data)
        
    def onCharaSelectionChange(self, event):
        if len(self.characterList) == 0:
            return
        w = event.widget
        try:
            index = int(w.curselection()[0])
            self.selected_char = w.get(index)
            print("Selected", self.selected_char)
            self.loadCharaInfo()
        except:
            self.selected_char = None
            
    def toggleMonitor(self, parent, playerId):
        monitorId = playerId - 1 
        if creatingMonitor[monitorId] == True:
            print("!!! Can't start the same monitor twice !!!")
            return
        if runningMonitors[monitorId] != None:
            runningMonitors[monitorId] = None
            self.setMonitorButton(monitorId, False)
            print("Killed monitor for player %d" % (playerId))
        else:
            self.setMonitorButton(monitorId, True)
            try:
                startMonitor(self, playerId)
            except Exception as e:
                print(e, file=sys.stderr)
                self.setMonitorButton(monitorId, False)
                creatingMonitor[monitorId] = False
      
    def createCharacterList(self):
        self.charaList = Listbox(self.charalistFrame)
        self.charaList.bind('<<ListboxSelect>>', self.onCharaSelectionChange)
        self.updateCharacterlist()
        self.charaList.pack(fill=BOTH, expand=1)
        
        self.createButton(self.importButtonFrame, "Import to P1", (1,), importPlayer)
        self.createButton(self.importButtonFrame, "Import to P2", (2,), importPlayer)
        self.monitorButtons = [
            self.createButton(self.importButtonFrame, "Monitor P1", (1,), self.toggleMonitor),
            self.createButton(self.importButtonFrame, "Monitor P2", (2,), self.toggleMonitor)
        ]
        
    def createExportButtons(self):
        tekken7_addr_match = "p([0-9]+)_addr"
        playerAddresses = [key for key in game_addresses if match(tekken7_addr_match, key)]
        for playerid, player_key in enumerate(playerAddresses):
            self.createButton(self.t7_exportFrame, "Export: Tekken 7: Player %d" % (playerid + 1), (7, game_addresses[player_key]), exportCharacter)
        
        self.createButton(self.t7_exportFrame, "Export: Tekken 7: All", (7, tekken7_addr_match), exportAll)
        
        tag2_addr_match = "cemu_p([0-9]+)_addr"
        playerAddresses = [key for key in game_addresses if match(tag2_addr_match, key)]
        for playerid, player_key in enumerate(playerAddresses):
            self.createButton(self.tag2_exportFrame, "Export: Tekken Tag2: Player %d" % (playerid + 1), (2, game_addresses[player_key]), exportCharacter)
        
        self.createButton(self.tag2_exportFrame, "Export: Tekken Tag2: All", (2, tag2_addr_match), exportAll)
        
    def createButton(self, frame, text, const_args, callback, side='top', expand=1):
        exportButton = Button(frame)
        exportButton["text"] = text
        exportButton["command"] = lambda: callback(self, *const_args)
        exportButton.pack(side=side, fill=X, expand=expand)
        return exportButton

if __name__ == "__main__":
    app = GUI_TekkenMovesetExtractor()
    app.mainloop()
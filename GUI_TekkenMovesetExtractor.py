# Python 3.6.5

from tkinter import Tk, Menu, Frame, Listbox, Label, Text
from tkinter.ttk import Button
from re import match
from Addresses import game_addresses
import sys
import os
import json
import time
import threading
import subprocess 
import motbinExport as exportLib
import motbinImport as importLib
from GUI_TekkenMovesetEditor import GUI_TekkenMovesetEditor

charactersPath = "./extracted_chars/"
codeInjectionSize = 256

selfName = os.path.basename(__file__)
monitorVerificationFrequency   = (2)
runningMonitors = [None, None]
creatingMonitor = [False, False]
codeInjection = None

def hexToList(value, bytes_count):
    return [((value >> (b * 8)) & 0xFF) for b in range(bytes_count)]
    
def getSinglePlayerInjection(playerAddr, movesetAddr, importer):
    global codeInjection
    player = hexToList(playerAddr, 4)
    moveset = hexToList(movesetAddr, 8)
    
    codeSize = codeInjectionSize
    codeAddr = importer.allocateMem(codeSize)
    
    playerLocation = codeAddr + codeInjectionSize - 0x30
    loadedMovesetLocation = codeAddr + codeInjectionSize - 0x20
    importedMovesetLocation = codeAddr + codeInjectionSize - 0x10
    
    playerLocation_bytes = hexToList(playerLocation, 4)
    loadedMovesetLocation_bytes = hexToList(loadedMovesetLocation, 4)
    importedMovesetLocation_bytes = hexToList(importedMovesetLocation, 4)

    singlePlayerBytecode = [
        0x3B, 0x0c, 0x25, *playerLocation_bytes, #cmp ecx,[location]
        0x75, 0x3a, #jne end
        0x48, 0x89, 0x14, 0x25, *loadedMovesetLocation_bytes, # mov [location], rdx
        0x51, #push rcx
        0x50, #push rax
        0x53, #push rbx
        0x48, 0x31, 0xDB, #xor rbx, rbx
        0x48, 0x8b, 0x0c, 0x25, *importedMovesetLocation_bytes, #mov rcx, [location]
        0x48, 0x8b, 0x84, 0xda, 0x80, 0x02, 0x00, 0x00, #mov rax,[rdx+rbx*8+00000290]
        0x48, 0x89, 0x84, 0xd9, 0x80, 0x02, 0x00, 0x00, #mov [rcx+rbx*8+00000290], rax
        0x48, 0xff, 0xc3, #inc rbx
        0x48, 0x83, 0xfb, 0x0B, #cmp rbx, 11
        0x75, 0xe7, #jne -e7
        0x5b, #pop rbx
        0x58, #pop rax
        0x59, #pop rcx
        0x48, 0x8b, 0x14, 0x25, *importedMovesetLocation_bytes, #mov rdx,[3f180066]
        0x48, 0x89, 0x91, 0xa0, 0x14, 0x00, 0x00, #mov [rcx+14a0, rdx]
        0x48, 0x89, 0x91, 0xa8, 0x14, 0x00, 0x00, #mov [rcx+14a8, rdx]
        0xFF, 0x25, 0x00, 0x00, 0x00, 0x00 , 0xEd, 0x8C, 0x73, 0x40, 0x01, 0x00, 0x00, 0x00 #jmp 140738Ced
    ]
    
    importer.writeBytes(codeAddr, bytes(singlePlayerBytecode))
    importer.writeInt(playerLocation, playerAddr, 8)
    importer.writeInt(loadedMovesetLocation, movesetAddr, 8)
    importer.writeInt(importedMovesetLocation, movesetAddr, 8)
    
    codeInjection = codeAddr
    return codeAddr

def getBothPlayersInjection(movesetAddr, movesetAddr2, importer):
    global codeInjection
    moveset = hexToList(movesetAddr, 8)
    moveset2 = hexToList(movesetAddr2, 8)
    
    codeSize = codeInjectionSize
    codeAddr = importer.allocateMem(codeSize)
    
    playerLocation = codeAddr + codeInjectionSize - 0x30
    loadedMovesetLocation = codeAddr + codeInjectionSize - 0x20
    importedMovesetLocation = codeAddr + codeInjectionSize - 0x10
    
    playerLocation_bytes = hexToList(playerLocation, 4)
    playerLocation2_bytes = hexToList(playerLocation + 8, 4)
    loadedMovesetLocation_bytes = hexToList(loadedMovesetLocation, 4)
    loadedMovesetLocation2_bytes = hexToList(loadedMovesetLocation + 8, 4)
    importedMovesetLocation_bytes = hexToList(importedMovesetLocation, 4)
    importedMovesetLocation2_bytes = hexToList(importedMovesetLocation + 8, 4)

    twoPlayersBytecode = [
        0x3B, 0x0c, 0x25, *playerLocation_bytes, #cmp ecx,[location]
        0x75, 0x3a, #jne p2_check
        0x48, 0x89, 0x14, 0x25, *loadedMovesetLocation_bytes, # mov [location], rdx
        0x51, #push rcx
        0x50, #push rax
        0x53, #push rbx
        0x48, 0x31, 0xDB, #xor rbx, rbx
        0x48, 0x8b, 0x0c, 0x25, *importedMovesetLocation_bytes, #mov rcx, [location]
        0x48, 0x8b, 0x84, 0xda, 0x80, 0x02, 0x00, 0x00, #mov rax,[rdx+rbx*8+00000290]
        0x48, 0x89, 0x84, 0xd9, 0x80, 0x02, 0x00, 0x00, #mov [rcx+rbx*8+00000290], rax
        0x48, 0xff, 0xc3, #inc rbx
        0x48, 0x83, 0xfb, 0x0B, #cmp rbx, 11
        0x75, 0xe7, #jne -e7
        0x5b, #pop rbx
        0x58, #pop rax
        0x59, #pop rcx
        0x48, 0x8b, 0x14, 0x25, *importedMovesetLocation_bytes, #mov rdx,[3f180066]
        
        0x3B, 0x0c, 0x25, *playerLocation2_bytes, #cmp ecx,[location]
        0x75, 0x3a, #jne end
        0x48, 0x89, 0x14, 0x25, *loadedMovesetLocation2_bytes, # mov [location], rdx
        0x51, #push rcx
        0x50, #push rax
        0x53, #push rbx
        0x48, 0x31, 0xDB, #xor rbx, rbx
        0x48, 0x8b, 0x0c, 0x25, *importedMovesetLocation2_bytes, #mov rcx, [location]
        0x48, 0x8b, 0x84, 0xda, 0x80, 0x02, 0x00, 0x00, #mov rax,[rdx+rbx*8+00000290]
        0x48, 0x89, 0x84, 0xd9, 0x80, 0x02, 0x00, 0x00, #mov [rcx+rbx*8+00000290], rax
        0x48, 0xff, 0xc3, #inc rbx
        0x48, 0x83, 0xfb, 0x0B, #cmp rbx, 11
        0x75, 0xe7, #jne -e7
        0x5b, #pop rbx
        0x58, #pop rax
        0x59, #pop rcx
        0x48, 0x8b, 0x14, 0x25, *importedMovesetLocation2_bytes, #mov rdx,[3f180066]

        0x48, 0x89, 0x91, 0xa0, 0x14, 0x00, 0x00, #mov [rcx+14a0, rdx]
        0x48, 0x89, 0x91, 0xa8, 0x14, 0x00, 0x00, #mov [rcx+14a8, rdx]
        0xFF, 0x25, 0x00, 0x00, 0x00, 0x00 , 0xEd, 0x8C, 0x73, 0x40, 0x01, 0x00, 0x00, 0x00 #jmp 140738Ced
    ]
    
    importer.writeBytes(codeAddr, bytes(twoPlayersBytecode))
    
    if codeInjection != None:
        movesetAddresses = importer.readBytes(codeInjection + codeInjectionSize - 0x20, 0x20)
        importer.writeBytes(codeAddr + codeInjectionSize - 0x20, movesetAddresses)
    
    importer.writeInt(playerLocation, game_addresses.addr['p1_addr'], 8)
    importer.writeInt(playerLocation + 8, game_addresses.addr['p1_addr'] + game_addresses.addr['playerstruct_size'], 8)
    
    importer.writeInt(loadedMovesetLocation, movesetAddr, 8)
    importer.writeInt(loadedMovesetLocation + 8, movesetAddr2, 8)
    
    importer.writeInt(importedMovesetLocation, movesetAddr, 8)
    importer.writeInt(importedMovesetLocation + 8, movesetAddr2, 8)
    
    codeInjection = codeAddr
    return codeAddr
        
class Monitor:
    def __init__(self, playerId, TekkenImporter, parent):
        self.id = playerId - 1
        self.otherMonitorId = int(not self.id)
        self.playerId = playerId
        self.moveset = None
        
        self.Importer = TekkenImporter
        self.parent = parent
        self.selected_char = parent.selected_char
        self.invertedPlayers = -1
        
        self.getPlayerAddress()
        
        try:
            self.moveset = self.Importer.loadMoveset(folderName=(charactersPath + self.selected_char))
        except Exception as e:
            print(e, file=sys.stderr)
            self.exit()
            
    def start(self):
        print("\nMonitoring successfully started for player %d. Moveset: %s" % (self.playerId, self.moveset.m['character_name']))
        self.injectPermanentMovesetCode()
        
        try:
            self.monitor()
        except Exception as e:
            print(e, file=sys.stderr)
            self.exit()
        
            
    def injectPermanentMovesetCode(self):
        otherMonitor = None
        if runningMonitors[self.otherMonitorId] != None:
            otherMonitor = runningMonitors[self.otherMonitorId]
            otherPlayer, otherMoveset = otherMonitor.playerAddr, otherMonitor.moveset.motbin_ptr
            currentPlayer, currentMoveset = self.playerAddr, self.moveset.motbin_ptr
            
            codeAddr = getBothPlayersInjection(self.moveset.motbin_ptr, otherMoveset, self.Importer)
        else:
            codeAddr = getSinglePlayerInjection(self.playerAddr, self.moveset.motbin_ptr, self.Importer)
            
        jmpInstruction = [
            0xFF, 0x25, 0, 0, 0, 0, *hexToList(codeAddr, 8)
        ]
        
        self.Importer.writeBytes(game_addresses.addr['code_injection_addr'], bytes(jmpInstruction))
        
        if otherMonitor != None:
            otherMonitor.getPlayerAddress(forceWriting = True)
        
    def resetCodeInjection(self, forceReset=False):
        if runningMonitors[self.otherMonitorId] == None or forceReset:
            
            originalInstructions = [
                0x48, 0x89, 0x91, 0xa0, 0x14, 0, 0,
                0x48, 0x89, 0x91, 0xa8, 0x14, 0, 0,
            ]
            self.Importer.writeBytes(game_addresses.addr['code_injection_addr'], bytes(originalInstructions))
        else:
            runningMonitors[self.otherMonitorId].injectPermanentMovesetCode()
            
    def writeMovesetToCode(self, playerId):
        global codeInjection
        
        if codeInjection == None or self.moveset == None:
            return
        
        offset = ((playerId - 1) * 8)
        self.Importer.writeInt(codeInjection + codeInjectionSize - 0x10 + offset, self.moveset.motbin_ptr, 8)
        self.Importer.writeInt(codeInjection + codeInjectionSize - 0x20 + offset, self.moveset.motbin_ptr, 8)
        
    def getPlayerAddress(self, forceWriting = False):
        startingAddr = game_addresses.addr['playerid_starting_ptr']
        for i in range(3):
            startingAddr = self.Importer.readInt(startingAddr, 8)
            
        invertPlayers = self.Importer.readInt(startingAddr + 0x60, 4)
        
        playerId = self.playerId + invertPlayers
        if playerId == 3:
            playerId = 1
        self.playerAddr = game_addresses.addr['p%d_addr' % (playerId)]
            
        if self.invertedPlayers != invertPlayers or forceWriting:
            self.writeMovesetToCode(playerId)
            self.invertedPlayers = invertPlayers
        
    def getCharacterId(self):
        return self.Importer.readInt(self.playerAddr + game_addresses.addr['chara_id_offset'], 8)
        
    def applyCharacterAliases(self):
        self.moveset.applyCharacterIDAliases(self.playerAddr)
        
    def monitor(self):
        self.getPlayerAddress(forceWriting = True)
        
        self.Importer.writeInt(self.playerAddr + game_addresses.addr['motbin_offset'], self.moveset.motbin_ptr, 8)
        
        prev_charaId = self.getCharacterId()
        self.applyCharacterAliases()
        
        lastMotbinPtr = None
        usingMotaOffsets = False
        
        while runningMonitors[self.id] != None:
            try:
                self.getPlayerAddress()
                charaId = self.getCharacterId()
                
                if charaId != prev_charaId:
                    self.applyCharacterAliases()
                    prev_charaId = charaId
                
                time.sleep(monitorVerificationFrequency)
            except Exception as e:
                try:
                    self.Importer.readInt(self.moveset.motbin_ptr, 8) # Read on self to see if process still exists
                    time.sleep(monitorVerificationFrequency)
                except Exception as e:
                    print(e, file=sys.stderr)
                    print("Monitor %d closing because process can't be read" % (self.playerId), file=sys.stderr)
                    self.exit(errcode=1)
                    
        self.exit()
        
    def exit(self, errcode=1):
        print("Monitor %d closed." % (self.playerId))
        runningMonitors[self.id] = None
        creatingMonitor[self.id] = None
        self.parent.setMonitorButton(self.id, False)
        if errcode == 1:
            try:
                self.resetCodeInjection()
            except:
                pass
        sys.exit(errcode)
    
def startMonitor(parent, playerId):
    if parent.selected_char == None:
        raise Exception("No character selected")
    print("Starting monitor for p%d..." % (playerId))
    monitorId = playerId - 1
    
    creatingMonitor[monitorId] = True
    TekkenImporter = importLib.Importer()
        
    newMonitor = Monitor(playerId, TekkenImporter, parent)
    newThread = threading.Thread(target=newMonitor.start)
    
    newThread.start()
    runningMonitors[monitorId] = newMonitor
    creatingMonitor[monitorId] = False
    
def getCharacterList():
    if not os.path.isdir(charactersPath):
        os.mkdir(charactersPath)
    folders = [folder for folder in os.listdir(charactersPath) if os.path.isdir(charactersPath + folder)]
    
    return sorted(folders)
    
def exportCharacter(parent, tekkenVersion, playerAddr, name=''):
    game_addresses.reloadValues()
    TekkenExporter = exportLib.Exporter(tekkenVersion, folder_destination=charactersPath)
    TekkenExporter.exportMoveset(playerAddr, name)
    parent.updateCharacterlist()
    
def exportTag2Character(parent, tekkenVersion, playerAddr, name=''):
    game_addresses.reloadValues()
    TekkenExporter = exportLib.Exporter(tekkenVersion, folder_destination=charactersPath)
    playerAddr += TekkenExporter.getCemuP1Addr()
    TekkenExporter.exportMoveset(playerAddr, name)
    
    parent.updateCharacterlist()
    
def exportAllTag2(parent, tekkenVersion, playerSize):
    game_addresses.reloadValues()
    
    TekkenExporter = exportLib.Exporter(tekkenVersion, folder_destination=charactersPath)
    playerAddr = TekkenExporter.getCemuP1Addr()
    
    exportedMovesets = []
    
    for i in range(4):
        addr = playerAddr + (i * playerSize) 
        moveset_name = TekkenExporter.getPlayerMovesetName(addr)
        if moveset_name not in exportedMovesets:
            print("Requesting export for %s..." % (moveset_name))
            moveset = TekkenExporter.exportMoveset(addr)
            exportedMovesets.append(moveset_name)
            print()
        else:
            print('Player', moveset_name, 'already exported, not exporting again.')
            
    print('\nSuccessfully exported:')
    for name in exportedMovesets:
        print(name)
        
    parent.updateCharacterlist()
    
def exportAll(parent, tekkenVersion, key_match):
    game_addresses.reloadValues()
    player_addresses = [game_addresses.addr[key] for key in game_addresses.addr if match(key_match, key)]
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
    playerAddr = game_addresses.addr['p%d_addr' % (playerId)]
    
    TekkenImporter = importLib.Importer()
    TekkenImporter.importMoveset(playerAddr, folderPath)
    print("\nSuccessfully imported %s !" % (parent.selected_char))
        
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
        
def on_close():
    global runningMonitors
    existingMonitor = next((r for r in runningMonitors if r != None), None)
    if existingMonitor:
        try:
            existingMonitor.resetCodeInjection(forceReset=True)
        except:
            pass
    runningMonitors = [None, None]
    os._exit(0)
    
def openMovesetEditor():
    app = GUI_TekkenMovesetEditor(mainWindow=False)
    app.window.mainloop()
        
class GUI_TekkenMovesetExtractor(Tk):
    def __init__(self):
        Tk.__init__(self)
        
        menubar = Menu(self)
        menubar.add_command(label="Moveset Editor", command=openMovesetEditor)
        self.config(menu=menubar)
        
        
        self.characterList = getCharacterList()
        self.selected_char = None
        self.chara_data = None
        
        self.wm_title("TekkenMovesetExtractor 1.0.3") 
        self.iconbitmap('InterfaceData/natsumi.ico')
        self.minsize(960, 540)
        self.geometry("960x540")
        
        self.consoleFrame = Frame(self, bg='#CCC')
        self.toolFrame = Frame(self, bg='#aaaaaa')
        
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
        
        self.protocol("WM_DELETE_WINDOW", on_close)
        
        try:
            with open("InterfaceData/readme.txt") as f:
                for line in f: print(line)
        except:
            pass
            
    def setMonitorButton(self, button, active):
        text = 'Local' if button == 0 else 'Remote'
        if active:
            self.monitorButtons[button]['text'] = 'Kill %s player monitor' % (text)
        else:
            self.monitorButtons[button]['text'] = 'Set Online %s player' % (text)
        
    def initImportArea(self):
        self.charalistFrame = Frame(self.importFrame)
        self.charalistActions = Frame(self.importFrame)
        
        self.charalistFrame.grid(row=0, column=0, sticky="nsew")
        self.charalistActions.grid(padx=15, row=0, column=1, sticky="nsew")
        
        
        self.importFrame.grid_columnconfigure(0, weight=1, uniform="group1")
        self.importFrame.grid_columnconfigure(1, weight=1, uniform="group1")
        self.importFrame.grid_rowconfigure(0, weight=1)
        
    def initImportActionsArea(self):
        self.charaInfoFrame = Frame(self.charalistActions, bg='#999999')
        self.importButtonFrame = Frame(self.charalistActions, bg='#999999')
        
        self.charaInfoFrame.grid(row=0, column=0, sticky="nsew")
        self.importButtonFrame.grid(row=1, column=0, sticky="nsew")
        
        
        self.charalistActions.grid_columnconfigure(0, weight=1)
        self.charalistActions.grid_rowconfigure(0, weight=1, uniform="group1")
        self.charalistActions.grid_rowconfigure(1, weight=1, uniform="group1")
        
        
        self.selectionInfo = Label(self.charaInfoFrame, text="")
        self.selectionInfo.pack(side='top', fill='both', expand=1)
        button = self.createButton(self.charaInfoFrame, "Update character list", (), GUI_TekkenMovesetExtractor.updateCharacterlist, side='bottom', expand='0')
        
    def initExportArea(self):
        self.t7_exportFrame = Frame(self.exportFrame, bg='#aaaaaa')
        self.tag2_exportFrame = Frame(self.exportFrame, bg='#aaaaaa')
        
        self.t7_exportFrame.grid(padx=18, pady=5, row=0, column=0, sticky="nsew")
        self.tag2_exportFrame.grid(padx=18, pady=5, row=0, column=1, sticky="nsew")
        
        
        self.exportFrame.grid_columnconfigure(0, weight=1, uniform="group1")
        self.exportFrame.grid_columnconfigure(1, weight=1, uniform="group1")
        self.exportFrame.grid_rowconfigure(0, weight=1)
        
    def initToolArea(self):
        self.exportFrame = Frame(self.toolFrame, bg='#aaaaaa')
        self.importFrame = Frame(self.toolFrame, bg='#999999')
        
        self.exportFrame.grid(padx=10, pady=5, row=0, column=0, sticky="nsew")
        self.importFrame.grid(padx=10, pady=5, row=1, column=0, sticky="nsew")
        
        
        self.toolFrame.grid_columnconfigure(0, weight=1)
        self.toolFrame.grid_rowconfigure(0, weight=1, uniform="group1")
        self.toolFrame.grid_rowconfigure(1, weight=1, uniform="group1")
        
    def initConsoleArea(self):
        TextArea = Text(self.consoleFrame, wrap="word")
        TextArea.configure(state="disabled")
        TextArea.tag_configure("err", foreground="#f2114d", background="#dddddd")
        TextArea.pack(padx=10, pady=5, fill='both', expand=1)
        
        sys.stdout = TextRedirector(TextArea)
        sys.stderr = TextRedirector(TextArea, "err")
        
    def updateCharacterlist(self):
        self.characterList = getCharacterList()
        self.charaList.delete(0,'end')
        self.selected_char = None
        if len(self.characterList) == 0:
            self.charaList.insert(0, "No moveset extracted yet...")
        else:
            colors = [
                ["#fff", "#eee"], #TTT2
                ["#ddd", "#ccc"]  #T7
            ]
            for i, character in enumerate(self.characterList):
                self.charaList.insert('end', character)
                color = colors[character.startswith("7_")][i & 1]
                self.charaList.itemconfig(i, {'bg': color })
            
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
                    "Exporter version: %s\n" % (m['export_version']),
                ]
                self.chara_data.append('Hash: %s' % (m['original_hash']) if 'original_hash' in m else 'No hash')
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
            return
            
        if runningMonitors[monitorId] != None:
            runningMonitors[monitorId] = None
            creatingMonitor[monitorId] = True
            print("Killing monitor for player %d..." % (playerId))
        else:
            try:
                startMonitor(self, playerId)
                self.setMonitorButton(monitorId, True)
            except Exception as e:
                print(e, file=sys.stderr)
                self.setMonitorButton(monitorId, False)
                creatingMonitor[monitorId] = False
      
    def createCharacterList(self):
        self.charaList = Listbox(self.charalistFrame)
        self.charaList.bind('<<ListboxSelect>>', self.onCharaSelectionChange)
        self.updateCharacterlist()
        self.charaList.pack(fill='both', expand=1)
        
        self.createButton(self.importButtonFrame, "Import to P1", (1,), importPlayer)
        self.createButton(self.importButtonFrame, "Import to P2", (2,), importPlayer)
        self.monitorButtons = [
            self.createButton(self.importButtonFrame, "Set Online Local Player", (1,), self.toggleMonitor),
            self.createButton(self.importButtonFrame, "Set Online Remote Player", (2,), self.toggleMonitor)
        ]
        
    def createExportButtons(self):
        tekken7_addr_match = "p([1-9]+)_addr"
        playerAddresses = [key for key in game_addresses.addr if match(tekken7_addr_match, key)]
        for playerid, player_key in enumerate(playerAddresses):
            self.createButton(self.t7_exportFrame, "Export: Tekken 7: Player %d" % (playerid + 1), (7, game_addresses.addr[player_key]), exportCharacter)
        
        self.createButton(self.t7_exportFrame, "Export: Tekken 7: All Players", (7, tekken7_addr_match), exportAll)

        playerOffset = game_addresses.addr["cemu_playerstruct_size"]

        for playerid in range(4):
            self.createButton(self.tag2_exportFrame, "Export: Tekken Tag2: Player %d" % (playerid + 1), (2, playerid * playerOffset), exportTag2Character)
        
        self.createButton(self.tag2_exportFrame, "Export: Tekken Tag2: All players", (2, playerOffset), exportAllTag2)
        
    def createButton(self, frame, text, const_args, callback, side='top', expand=1):
        exportButton = Button(frame)
        exportButton["text"] = text
        exportButton["command"] = lambda: callback(self, *const_args)
        exportButton.pack(side=side, fill='x', expand=expand)
        return exportButton

if __name__ == "__main__":
    if "--editor" in sys.argv:
        app = GUI_TekkenMovesetEditor()
    else:
        app = GUI_TekkenMovesetExtractor()
    app.mainloop()
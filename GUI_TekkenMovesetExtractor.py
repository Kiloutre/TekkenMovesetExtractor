# Python 3.6.5

from tkinter import Tk, Menu, Frame, Listbox, Label, Text, messagebox, messagebox
from tkinter.ttk import Button
from re import match
from Addresses import game_addresses, AddressFile
import io
import sys
import os
import json
import time
import threading
import ctypes
import motbinExport as exportLib
import motbinImport as importLib
from win32com.client import Dispatch
from urllib import request

extractorVersion = "1.0.32.25"
charactersPath = "./extracted_chars/"
codeInjectionSize = 256
    
monitorVerificationFrequency = .1
runningMonitors = [None, None]
creatingMonitor = [False, False]
codeInjection = None

def createShortcut(path, target='', wDir='', icon='', args=''):
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = wDir
    if args != '': shortcut.Arguments = args
    if icon != '': shortcut.IconLocation = icon
    shortcut.save()
    
def getRequestFromURL(url):
    requestObject = request.Request(
        url,
        data=None,
    )
    return requestObject

def getFileFromRepo(address, path):
    requestObject = getRequestFromURL(address + path)
    content = request.urlopen(requestObject).read() 
    
    return content.decode('ascii')

def hexToList(value, bytes_count):
    return [((value >> (b * 8)) & 0xFF) for b in range(bytes_count)]

def allocateMovesetWritingInjection(movesetAddr, movesetAddr2, importer):
    global codeInjection
    
    codeSize = codeInjectionSize
    codeAddr = importer.allocateMem(codeSize)
    
    playerLocation = codeAddr + codeInjectionSize - 0x20
    newMovesetLocation = codeAddr + codeInjectionSize - 0x10
    
    playerLocation_bytes = hexToList(playerLocation, 8)
    playerLocation2_bytes = hexToList(playerLocation + 8, 8)
    codeInjectionEnd = hexToList(game_addresses['code_injection_addr'] + 0xE, 8)

    twoPlayersBytecode = [
        0x41, 0x52, #push r10
        0x4c, 0x8b, 0x15, 0xD7, 0x00, 0x00, 0x00, # mov r10, [codeInjection + 256 - 0x20] #playerLocation_bytes. compare to player address
        0x4c, 0x39, 0xd1, #cmp rcx, r10
        0x75, 0x30, #jne p2_check : wrong player, not continuing
        0x51, #push rcx
        0x50, #push rax
        0x53, #push rbx
        
        # loop, copy some animation like cam, hand and all to moveset in order to avoid crash (we dont import those yet)
        0x48, 0x31, 0xDB, #xor rbx, rbx
        0x48, 0x8b, 0x0D, 0xD5, 0x00, 0x00, 0x00, #mov rcx, [newMovesetLocation]
        
        
        0x48, 0x8b, 0x84, 0xda, 0x80, 0x02, 0x00, 0x00, #mov rax,[rdx+rbx*8+00000290]
        0x48, 0x89, 0x84, 0xd9, 0x80, 0x02, 0x00, 0x00, #mov [rcx+rbx*8+00000290], rax
        0x48, 0xff, 0xc3, #inc rbx
        0x48, 0x83, 0xfb, 0x0B, #cmp rbx, 11
        0x75, 0xe7, #jne -e7
        
        0x5b, #pop rbx
        0x58, #pop rax
        0x59, #pop rcx
        0x48, 0x8b, 0x15, 0xB2, 0x00, 0x00, 0x00, #mov rdx, [newMovesetLocation] #force new moveset
        
        
        
        #p2_check, same as above but with p2 moveset
        0x4c, 0x8b, 0x15, 0xA3, 0x00, 0x00, 0x00, # mov r10, [codeInjection + 256 - 0x20 + 8] #playerLocation2_bytes
        0x4c, 0x39, 0xd1, #cmp rcx, r10
        0x75, 0x30, #jne end
        0x51, #push rcx
        0x50, #push rax
        0x53, #push rbx
        
        # loop, copy some animation like cam, hand and all to moveset in order to avoid crash (we dont import those yet)
        0x48, 0x31, 0xDB, #xor rbx, rbx
        0x48, 0x8b, 0x0D, 0xa1, 0x00, 0x00, 0x00, #mov rcx, [newMovesetLocation + 8]
        
        0x48, 0x8b, 0x84, 0xda, 0x80, 0x02, 0x00, 0x00, #mov rax,[rdx+rbx*8+00000290]
        0x48, 0x89, 0x84, 0xd9, 0x80, 0x02, 0x00, 0x00, #mov [rcx+rbx*8+00000290], rax
        0x48, 0xff, 0xc3, #inc rbx
        0x48, 0x83, 0xfb, 0x0B, #cmp rbx, 11
        0x75, 0xe7, #jne -e7
        
        0x5b, #pop rbx
        0x58, #pop rax
        0x59, #pop rcx
        0x48, 0x8b, 0x15, 0x7E, 0x00, 0x00, 0x00, #mov rdx, [newMovesetLocation + 8] #force new moveset
        
        
        #end
        0x41, 0x5a, #pop r10
        0x48, 0x89, 0x91, 0x20, 0x15, 0x00, 0x00, #mov [rcx+1520, rdx]
        0x48, 0x89, 0x91, 0x28, 0x15, 0x00, 0x00, #mov [rcx+1528, rdx]
        0xFF, 0x25, 0x00, 0x00, 0x00, 0x00, *codeInjectionEnd #jmp
    ]
    
    importer.writeBytes(codeAddr, bytes(twoPlayersBytecode))
    
    
    if movesetAddr != None:
        importer.writeInt(playerLocation, game_addresses['t7_p1_addr'], 8)
        importer.writeInt(newMovesetLocation, movesetAddr, 8)
    else:
        importer.writeInt(playerLocation, 0, 8)
        importer.writeInt(newMovesetLocation, 0, 8)
        
    if movesetAddr2 != None:
        importer.writeInt(playerLocation + 8, game_addresses['t7_p1_addr'] + game_addresses['t7_playerstruct_size'], 8)
        importer.writeInt(newMovesetLocation + 8, movesetAddr2, 8)
    else:
        importer.writeInt(playerLocation + 8, 0, 8)
        importer.writeInt(newMovesetLocation + 8, 0, 8)
    
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
            self.moveset = self.Importer.loadMoveset(folderName=(charactersPath + self.selected_char), charactersPath=charactersPath)
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
            
            codeAddr = allocateMovesetWritingInjection(self.moveset.motbin_ptr, otherMoveset, self.Importer)
        else:
            if self.playerId == 1:
                codeAddr = allocateMovesetWritingInjection(self.moveset.motbin_ptr, None, self.Importer)
            else:
                codeAddr = allocateMovesetWritingInjection(None, self.moveset.motbin_ptr, self.Importer)
            
        jmpInstruction = [
            0xFF, 0x25, 0, 0, 0, 0, *hexToList(codeAddr, 8)
        ]
        
        self.Importer.writeBytes(game_addresses['code_injection_addr'], bytes(jmpInstruction))
        
        if otherMonitor != None:
            otherMonitor.getPlayerAddress(forceWriting = True)
        
    def resetCodeInjection(self, forceReset=False):
        if runningMonitors[self.otherMonitorId] == None or forceReset:
            
            originalInstructions = [
                0x48, 0x89, 0x91, 0x20, 0x15, 0, 0,
                0x48, 0x89, 0x91, 0x28, 0x15, 0, 0,
            ]
            self.Importer.writeBytes(game_addresses['code_injection_addr'], bytes(originalInstructions))
        else:
            runningMonitors[self.otherMonitorId].injectPermanentMovesetCode()
            
    def writeMovesetToCode(self, playerId):
        global codeInjection
        
        if codeInjection == None or self.moveset == None:
            return
            
        playerLocation = codeInjection + codeInjectionSize - 0x20
        newMovesetLocation = codeInjection + codeInjectionSize - 0x10
        
        
        offset = ((playerId - 1) * 8)
        
        self.Importer.writeInt(newMovesetLocation + offset, self.moveset.motbin_ptr, 8)
        self.Importer.writeInt(playerLocation + offset, self.playerAddr, 8)
            
        if runningMonitors[self.otherMonitorId] == None:
            otherOffset = (8 if offset == 0 else 0)
            self.Importer.writeInt(newMovesetLocation + otherOffset, 0, 8)
            self.Importer.writeInt(playerLocation + otherOffset, 0, 8)
        
    def getLocalPlayerSide(self):
        return self.Importer.readInt(game_addresses['playerid_ptr'], 4)
        
    def getPlayerAddress(self, forceWriting = False):
        self.playerAddr = self.Importer.getPlayerAddress(0)
        
        if self.playerAddr == None:
            self.invertedPlayers = -1
            return #player not loaded yet
        
        invertPlayers = self.getLocalPlayerSide()
        
        playerId = self.playerId + invertPlayers
        if playerId == 3:
            playerId = 1
        if playerId == 2:
            self.playerAddr += game_addresses['t7_playerstruct_size']
            
        if self.invertedPlayers != invertPlayers or forceWriting:
            self.writeMovesetToCode(playerId)
            self.invertedPlayers = invertPlayers
        
    def getCharacterId(self):
        if self.playerAddr == None: return -1
        return self.Importer.readInt(self.playerAddr + game_addresses['t7_chara_id_offset'], 8)
        
    def applyCharacterAliases(self):
        self.moveset.applyCharacterIDAliases(self.playerAddr)
        
    def monitor(self):
        self.getPlayerAddress(forceWriting = True)
        
        if self.playerAddr != None:
            try:
                moveset_addr = self.Importer.readInt(self.playerAddr + game_addresses['t7_motbin_offset'], 8)
                self.moveset.copyMotaOffsets(moveset_addr)
            except Exception as e:
                pass
            self.Importer.writeInt(self.playerAddr + game_addresses['t7_motbin_offset'], self.moveset.motbin_ptr, 8)
            
        prev_charaId = self.getCharacterId()
        
        if prev_charaId != -1: #character actually loaded
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
        os.mkdir(charactersPath)
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
    
def exportCharacter(parent, tekkenVersion, playerid, name=''):
    game_addresses.reloadValues()
    TekkenExporter = exportLib.Exporter(tekkenVersion, folder_destination=charactersPath)
    playerAddr = TekkenExporter.getP1Addr() + (playerid * game_addresses[tekkenVersion + '_playerstruct_size'])
    TekkenExporter.exportMoveset(playerAddr, name)
    
    parent.updateCharacterlist()
    
def exportAll(parent, TekkenVersion):
    game_addresses.reloadValues()
    
    TekkenExporter = exportLib.Exporter(TekkenVersion, folder_destination=charactersPath)
    playerAddr = TekkenExporter.getP1Addr()
    
    exportedMovesets = []
    playerSize = game_addresses[TekkenVersion + '_playerstruct_size']
    
    playerCount = 2
    if TekkenVersion + '_player_count' in game_addresses.addr:
        playerCount = game_addresses[TekkenVersion + '_player_count']
    
    for i in range(playerCount):
        moveset_name = TekkenExporter.getPlayerMovesetName(playerAddr)
        if moveset_name not in exportedMovesets:
            print("Requesting export for %s..." % (moveset_name))
            moveset = TekkenExporter.exportMoveset(playerAddr)
            exportedMovesets.append(moveset_name)
            print()
        else:
            print('Player', moveset_name, 'already exported, not exporting again.')
        playerAddr += playerSize
            
    print('\nSuccessfully exported:')
    for name in exportedMovesets:
        print(name)
        
    parent.updateCharacterlist()
        
def importPlayer(parent, playerId):
    if parent.selected_char == None:
        print("No character selected")
        return
    folderPath = charactersPath + parent.selected_char 
    
    
    TekkenImporter = importLib.Importer()
    playerAddr = TekkenImporter.getPlayerAddress(playerId - 1)
    TekkenImporter.importMoveset(playerAddr, folderPath, charactersPath=charactersPath)
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
    
def openMovesetEditor(mainWindow=False):
    from GUI_TekkenMovesetEditor import GUI_TekkenMovesetEditor
    if mainWindow: ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('kilo.TekkenMovesetEditor')
    app = GUI_TekkenMovesetEditor(mainWindow)
    app.window.mainloop()
    
def openAnimationEditor(mainWindow=False):
    from GUI_TekkenAnimationEditor import GUI_TekkenAnimationEditor
    if mainWindow: ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('kilo.TekkenAnimationEditor')
    app = GUI_TekkenAnimationEditor(mainWindow)
    app.window.mainloop()
    
def openCameraAnimator(mainWindow=False):
    from GUI_TekkenCameraAnimator import GUI_TekkenCameraAnimator
    if mainWindow: ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('kilo.TekkenCameraAnimator')
    app = GUI_TekkenCameraAnimator(mainWindow)
    app.window.mainloop()
    
def editorDescriptionfileToDict(filedata, base=10):
    resultingDict = {}
    for line in [l.strip() for l in filedata.split("\n") if len(l.strip()) != 0]:
        try:
            commaPos = line.find(',')
            val, label = line[:commaPos], line[commaPos + 1:].strip()
            resultingDict[int(val, base)] = label
        except Exception as e:
            pass
    return {key:resultingDict[key] for key in sorted(resultingDict)}
        
class GUI_TekkenMovesetExtractor(Tk):
    def __init__(self):
        Tk.__init__(self)
        
        menubar = Menu(self)
        menubar.add_command(label="Moveset Editor", command=openMovesetEditor)
        menubar.add_command(label="Animation Editor", command=openAnimationEditor)
        menubar.add_command(label="Camera Animator", command=openCameraAnimator)
        menubar.add_separator()
        menubar.add_command(label="Create shortcuts", command=self.createShortcuts)
        menubar.add_command(label="Extractor guide", command=self.openGuide)
        menubar.add_separator()
        menubar.add_command(label="[UPDATE] game_addresses.txt", command=self.updateAddressFile)
        menubar.add_command(label="[UPDATE] editor descriptions", command=self.updateEditorDescriptions)
        self.config(menu=menubar)
        
        
        self.characterList = getCharacterList()
        self.selected_char = None
        self.chara_data = None
        
        self.wm_title("TekkenMovesetExtractor " + extractorVersion) 
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
            
    def updateEditorDescriptions(self):
        for file, base in [('editorRequirements.txt', 10), ('editorProperties.txt', 16), ('editorCommands.txt', 16)]:
            path = 'InterfaceData/' + file
            newFiledata = getFileFromRepo(game_addresses['repo_link'], path)
            newDict = editorDescriptionfileToDict(newFiledata, base)
    
            if not os.path.exists(path): open(path, 'w').close()
            with open(path, 'r+') as f:
                currentDict = editorDescriptionfileToDict(f.read(), base)
                
                modified = False
                for key in newDict:
                    if key not in currentDict or currentDict[key] != newDict[key]:
                        currentDict[key] = newDict[key]
                        modified = True
                        
                if modified:
                    f.truncate(0)
                    f.seek(0, 0)
                    for key in sorted(currentDict):
                        prefix = ("0x%x" % key) if base == 16 else ("%d" % key)
                        f.write(prefix + ",%s\n" % currentDict[key])
                    messagebox.showinfo("Updated", "File %s successfully updated." % file,  parent=self)
                else:
                    print("\nNo update needed for file %s" % file)
        

            
    def updateAddressFile(self):
        filedata = getFileFromRepo(game_addresses['repo_link'], 'game_addresses.txt')
        newAddresses = AddressFile(data=filedata)
        
        if newAddresses['version'] != game_addresses['version']:
            with open("game_addresses.txt", "w") as f:
                f.write(filedata)
            game_addresses.reloadValues()
            messagebox.showinfo("Updated", "Addresses successfully updated.\nRestart this software for the effect to take place.",  parent=self)
        else:
            messagebox.showinfo("Not updating", "Nothing to update, file is up to date.",  parent=self)
            
    def openGuide(self):
        with open("InterfaceData/extractorGuide.txt", "r") as f:
            messagebox.showinfo("Guide", f.read(),  parent=self)
        
    def createShortcuts(self):
        targetDir = os.path.dirname(os.path.abspath(__file__)) + "\\"
        
        createShortcut(targetDir + "TekkenMovesetEditor.lnk", targetDir + "TekkenMovesetExtractor.exe", targetDir, targetDir + "InterfaceData\\renge.ico", "--editor")
        createShortcut(targetDir + "TekkenCameraAnimator.lnk", targetDir + "TekkenMovesetExtractor.exe", targetDir, targetDir + "InterfaceData\\komari.ico", "--camera")
        createShortcut(targetDir + "TekkenAnimationEditor.lnk", targetDir + "TekkenMovesetExtractor.exe", targetDir, targetDir + "InterfaceData\\hotaru.ico", "--animator")
            
        messagebox.showinfo("Created", "Shortcuts for the moveset editor, camera animator and the animation editor have been created!\nYou may move them as you please.", parent=self)
        
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
        for playerid in range(2):
            self.createButton(self.t7_exportFrame, "Export: Tekken 7: Player %d" % (playerid + 1), ("t7", playerid), exportCharacter)
        
        self.createButton(self.t7_exportFrame, "Export: Tekken 7: Both Players", ("t7",), exportAll)
        
        self.createButton(self.tag2_exportFrame, "Export: Tekken Tag2: All players", ("tag2",), exportAll)
        self.createButton(self.tag2_exportFrame, "Export: Tekken Rev: Both players", ("rev",), exportAll)
        self.createButton(self.tag2_exportFrame, "Export: Tekken 6: Both players", ("t6",), exportAll)
        self.createButton(self.tag2_exportFrame, "Export: Tekken 5: Both players", ("t5",), exportAll)
        self.createButton(self.tag2_exportFrame, "Export: Tekken 5 DR: Both players", ("t5dr",), exportAll)
        
    def createButton(self, frame, text, const_args, callback, side='top', expand=1):
        exportButton = Button(frame)
        exportButton["text"] = text
        exportButton["command"] = lambda: callback(self, *const_args)
        exportButton.pack(side=side, fill='x', expand=expand)
        return exportButton

if __name__ == "__main__":
    if "--editor" in sys.argv:
        openMovesetEditor(mainWindow=True)
    elif "--animator" in sys.argv:
        openAnimationEditor(mainWindow=True)
    elif "--camera" in sys.argv:
        openCameraAnimator(mainWindow=True)
    else:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('kilo.TekkenMovesetExtractor')
        app = GUI_TekkenMovesetExtractor()
        app.mainloop()
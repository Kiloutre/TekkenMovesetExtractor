# Python 3.6.5

from tkinter import *
from tkinter.ttk import *
from Addresses import GameClass, GameAddresses
exportLib = __import__("Ton-Chan's_Motbin_export")
importLib = __import__("Ton-Chan's_Motbin_import")

exportMoveset = exportLib.exportMoveset
importMoveset = importLib.importMoveset

charactersPath = "extracted_chars"
game_addresses = GameAddresses.a

def exportCharacter(tekkenVersion, playerAddr, name=''):
    processName = "TekkenGame-Win64-Shipping.exe" if tekkenVersion == 7 else "Cemu.exe"
    
    try:
        TekkenInstance = GameClass(processName)
    except:
        print("Could not find", processName, "process.")
        return
        
    exportLib.initGlobals(tekkenVersion)
    exportLib.initGameInstance(TekkenInstance)
    exportMoveset(playerAddr, name)

class GUI_TekkenMovesetExtractor(Tk):
    def __init__(self):
        Tk.__init__(self)
        
        self.wm_title("TekkenMovesetExtractor 0.6") 
        self.iconbitmap('GUI_TekkenMovesetExtractor/natsumi.ico')
        
        playerid = 1
        while playerid < 3:
            key = "p%d_ptr" % (playerid)
            if key not in game_addresses:
                break
            self.createExportButton("Tekken 7: Player %d" % (playerid), game_addresses[key], 7, exportCharacter)
            playerid += 1
            
        playerid = 1
        while playerid < 5:
            key = "cemu_p%d_ptr" % (playerid)
            if key not in game_addresses:
                break
            self.createExportButton("Tekken Tag2: Player %d" % (playerid), game_addresses[key], 2, exportCharacter)
            playerid += 1
        

    def createExportButton(self, name, addr, tekkenVersion, exportFunction):
        self.exportButton = Button(self)
        self.exportButton["text"] = "Export: " + name
        self.exportButton["command"] = lambda: exportFunction(tekkenVersion, addr)
        self.exportButton.pack(side="top")
        

if __name__ == "__main__":
    app = GUI_TekkenMovesetExtractor()
    app.mainloop()
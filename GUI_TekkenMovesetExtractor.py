# Python 3.6.5

from tkinter import *
from tkinter.ttk import *
from re import match
from Addresses import game_addresses
exportLib = __import__("Ton-Chan's_Motbin_export")
importLib = __import__("Ton-Chan's_Motbin_import")

charactersPath = "extracted_chars"

def exportCharacter(tekkenVersion, playerAddr, name=''):
    TekkenExporter = exportLib.Exporter(tekkenVersion)
    TekkenExporter.exportMoveset(playerAddr)
    
def exportAll(tekkenVersion, key_match):
    player_addresses = [game_addresses[key] for key in game_addresses if match(key_match, key)]
    TekkenExporter = exportLib.Exporter(tekkenVersion)
    
    exportedMovesets = []
    
    for playerAddr in player_addresses:
        moveset_name = TekkenExporter.getPlayerMovesetName(playerAddr)
        if moveset_name not in exportedMovesets:
            moveset = TekkenExporter.exportMoveset(playerAddr)
            exportedMovesets.append(moveset_name)
        else:
            print('Player', moveset_name, 'already exported, not exporting again.')
            
    print('\nSuccessfully exported:')
    for name in exportedMovesets:
        print(name)
        
class GUI_TekkenMovesetExtractor(Tk):
    def __init__(self):
        Tk.__init__(self)
        
        self.wm_title("TekkenMovesetExtractor 0.6") 
        self.iconbitmap('GUI_TekkenMovesetExtractor/natsumi.ico')
        
        playerid = 1
        while playerid < 3:
            key = "p%d_addr" % (playerid)
            if key not in game_addresses:
                break
            self.createExportButton("Tekken 7: Player %d" % (playerid), (7, game_addresses[key]), exportCharacter)
            playerid += 1
        self.createExportButton("Tekken 7: All", (7, "p([0-9]+)_addr"), exportAll)
            
        playerid = 1
        while playerid < 5:
            key = "cemu_p%d_addr" % (playerid)
            if key not in game_addresses:
                break
            self.createExportButton("Tekken Tag2: Player %d" % (playerid), (2, game_addresses[key]), exportCharacter)
            playerid += 1
        self.createExportButton("Tekken Tag2: All", (2, "cemu_(p[0-9]+)_addr"), exportAll)
        
    def createExportButton(self, name, const_args, exportFunction):
        self.exportButton = Button(self)
        self.exportButton["text"] = "Export: " + name
        self.exportButton["command"] = lambda: exportFunction(*const_args)
        self.exportButton.pack(side="top")
        

if __name__ == "__main__":
    app = GUI_TekkenMovesetExtractor()
    app.mainloop()
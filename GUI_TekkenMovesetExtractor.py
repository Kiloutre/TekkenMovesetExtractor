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
        
        tekken7_addr_match = "p([0-9]+)_addr"
        playerAddresses = [key for key in game_addresses if re.match(tekken7_addr_match, key)]
        for playerid, player_key in enumerate(playerAddresses):
            self.createExportButton("Tekken 7: Player %d" % (playerid + 1), (7, game_addresses[player_key]), exportCharacter)
        
        self.createExportButton("Tekken 7: All", (7, tekken7_addr_match), exportAll)
        
        tag2_addr_match = "p([0-9]+)_addr"
        playerAddresses = [key for key in game_addresses if re.match(tag2_addr_match, key)]
        for playerid, player_key in enumerate(playerAddresses):
            self.createExportButton("Tekken Tag2: Player %d" % (playerid + 1), (2, game_addresses[player_key]), exportCharacter)
        
        self.createExportButton("Tekken Tag2: All", (2, tekken7_addr_match), exportAll)
        
    def createExportButton(self, name, const_args, exportFunction):
        self.exportButton = Button(self)
        self.exportButton["text"] = "Export: " + name
        self.exportButton["command"] = lambda: exportFunction(*const_args)
        self.exportButton.pack(side="top")
        

if __name__ == "__main__":
    app = GUI_TekkenMovesetExtractor()
    app.mainloop()
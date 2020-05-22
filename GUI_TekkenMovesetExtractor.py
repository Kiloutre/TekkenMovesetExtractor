# Python 3.6.5

from tkinter import *
from tkinter.ttk import *
from Addresses import GameAddresses
exportLib = __import__("Ton-Chan's_Motbin_export")
importLib = __import__("Ton-Chan's_Motbin_import")

charactersPath = "extracted_chars"
game_addresses = GameAddresses.a

def exportCharacter(tekkenVersion, playerAddr, name=''):
    TekkenExporter = exportLib.Exporter(tekkenVersion)
    TekkenExporter.exportMoveset(playerAddr)
    
def exportAll(tekkenVersion, prefix):
    player_addresses = [game_addresses[key] for key in game_addresses if key.startswith(prefix)] #replace prefix with regex match
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
            key = "p%d_ptr" % (playerid)
            if key not in game_addresses:
                break
            self.createExportButton("Tekken 7: Player %d" % (playerid), 7, game_addresses[key], exportCharacter)
            playerid += 1
        self.createExportButton("Tekken 7: All", 7, "p", exportAll)
            
        playerid = 1
        while playerid < 5:
            key = "cemu_p%d_ptr" % (playerid)
            if key not in game_addresses:
                break
            self.createExportButton("Tekken Tag2: Player %d" % (playerid), 2, game_addresses[key], exportCharacter)
            playerid += 1
        self.createExportButton("Tekken Tag2: All", 2, "cemu_p", exportAll)
        
    def createExportButton(self, name, arg1, arg2, exportFunction): #use kwargs
        self.exportButton = Button(self)
        self.exportButton["text"] = "Export: " + name
        self.exportButton["command"] = lambda: exportFunction(arg1, arg2)
        self.exportButton.pack(side="top")
        

if __name__ == "__main__":
    app = GUI_TekkenMovesetExtractor()
    app.mainloop()
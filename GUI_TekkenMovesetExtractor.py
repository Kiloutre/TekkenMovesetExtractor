# Python 3.6.5

from tkinter import *
from tkinter.ttk import Button
from re import match
from Addresses import game_addresses
import sys
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
            print("Requesting export for %s..." % (moveset_name))
            moveset = TekkenExporter.exportMoveset(playerAddr)
            exportedMovesets.append(moveset_name)
        else:
            print('Player', moveset_name, 'already exported, not exporting again.')
            
    print('\nSuccessfully exported:')
    for name in exportedMovesets:
        print(name)
        
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
        
        self.wm_title("TekkenMovesetExtractor 0.6") 
        self.iconbitmap('GUI_TekkenMovesetExtractor/natsumi.ico')
        self.minsize(960, 540)
        self.geometry("960x540")
        
        self.left_frame = Frame(self, bg='#CCC')
        self.right_frame = Frame(self, bg='white')
        
        self.left_frame.TextArea = Text(self, wrap="word")
        self.left_frame.TextArea.configure(state="disabled")
        self.left_frame.TextArea.tag_configure("err", foreground="#f2114d", background="#dddddd")
        
        sys.stdout = TextRedirector(self.left_frame.TextArea)
        sys.stderr = TextRedirector(self.left_frame.TextArea, "err")
        
        tekken7_addr_match = "p([0-9]+)_addr"
        playerAddresses = [key for key in game_addresses if match(tekken7_addr_match, key)]
        for playerid, player_key in enumerate(playerAddresses):
            self.createExportButton("Tekken 7: Player %d" % (playerid + 1), (7, game_addresses[player_key]), exportCharacter)
        
        self.createExportButton("Tekken 7: All", (7, tekken7_addr_match), exportAll)
        
        tag2_addr_match = "p([0-9]+)_addr"
        playerAddresses = [key for key in game_addresses if match(tag2_addr_match, key)]
        for playerid, player_key in enumerate(playerAddresses):
            self.createExportButton("Tekken Tag2: Player %d" % (playerid + 1), (2, game_addresses[player_key]), exportCharacter)
        
        self.createExportButton("Tekken Tag2: All", (2, tekken7_addr_match), exportAll)
        
        self.left_frame.TextArea.grid(padx=10, pady=10, sticky="nsew")
        
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        
        self.grid_columnconfigure(0, weight=1, uniform="group1")
        self.grid_columnconfigure(1, weight=1, uniform="group1")
        self.grid_rowconfigure(0, weight=1)
        
        
    def createExportButton(self, name, const_args, exportFunction):
        self.exportButton = Button(self.right_frame)
        self.exportButton["text"] = "Export: " + name
        self.exportButton["command"] = lambda: exportFunction(*const_args)
        self.exportButton.pack(side="top")
        

if __name__ == "__main__":
    app = GUI_TekkenMovesetExtractor()
    app.mainloop()
import json
import os
import sys
import Aliases

f = [f for f in os.listdir() if f.startswith("2_")]

for file in f:
    filename = "%s/%s.json" % (file, file[2:])
    moves = None
    with open(filename, "r") as f:
        jsonFile = json.load(f)
        moves = jsonFile['moves']
        f.close()
    
    for m in moves:
        hitbox = m['hitbox_location'].to_bytes(4, 'big')
        name = m['name']
        
        for b in hitbox:
            if b == 0x23:
                print(file, name, hitbox)
                break
                
                
                
t7_char = "EDDY"
t7_print_move_info = "Cp_jplrp"

if t7_char != "":
    moves = None
    filename = "7_%s/%s.json" % (t7_char, t7_char)
    with open(filename, "r") as f:
        jsonFile = json.load(f)
        moves = jsonFile['moves']
        f.close()
        
    for m in moves:
        if m['name'] != t7_print_move_info:
            continue
        hitbox = m['hitbox_location'].to_bytes(4, 'big')
        print("T7", t7_char, m['name'], hitbox)
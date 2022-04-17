charIDs = {
    0: "Paul",
    1: "Law",
    2: "King",
    3: "Yoshimitsu",
    4: "Hwoarang",
    5: "Xiayou",
    6: "Jin",
    7: "Bryan",
    8: "Heihachi",
    9: "Kazuya",
    10: "Steve",
    11: "JACK7",
    12: "Asuka",
    13: "Devil Jin",
    14: "Feng",
    15: "Lili",
    16: "Dragunov",
    17: "Leo",
    18: "Lars",
    19: "Alisa",
    20: "Claudio",
    21: "Katarina",
    22: "Chloe",
    23: "Shaheen",
    24: "Josie",
    25: "Gigas",
    26: "Kazumi",
    27: "Devil Kazumi",
    28: "Nina",
    29: "Master Raven",
    30: "Lee",
    31: "Bob",
    32: "Akuma",
    33: "Kuma",
    34: "Panda",
    35: "Eddy",
    36: "Eliza",
    37: "Miguel",
    38: "SOLDIER",
    39: "YOUNG KAZUYA",
    40: "JACK4",
    41: "YOUNG HEIHACHI",
    42: "DUMMY",
    43: "Geese",
    44: "Noctis",
    45: "Anna",
    46: "Lei",
    47: "Marduk",
    48: "Armor King",
    49: "Julia",
    50: "Negan",
    51: "Zafina",
    52: "Ganryu",
    53: "Leroy",
    54: "Fahk",
    55: "Kuni",
    56: "Lidia",
    75: "NONE"
}

gamemodes = {
    1: "Practice",
    4: "Main Story",
    5: "Char episode",
    6: "Customization",
    7: "Treasure Battle",
    10: "VS"
}

req225 = {
    0: "No",
    1: "Yes",
    3: "Intro/Outro?"
}

storyBattles = {
    0: "Prologue",
    1: "Throwing KAZ off cliff",
    2: "HEI vs T-Force",
    3: "HEI vs NINA",
    4: "KAZ vs JACK4",
    5: "HEI vs JACK4",
    6: "HEI vs CLAUDIO",
    12: "HEI vs AKUMA 1",
    13: "HEI vs JACK6",
    14: "HEI vs AKUMA 2",
    18: "KAZ vs AKUMA 1",
    19: "KAZ vs AKUMA 2",
    21: "HEI vs KAZUMI",
    22: "HEI vs KAZ 1",
    23: "HEI vs KAZ 2",
    24: "HEI vs KAZ 3",
    25: "HEI vs KAZ 4",
    26: "???",
    27: "Special Chapter"
}

# Add req in this list and assign parameter list
# Format: reqId -> paramList
reqDetailsList = {
    217: charIDs,  # Char ID checks
    218: charIDs,
    219: charIDs,
    220: charIDs,
    221: charIDs,
    222: charIDs,
    223: charIDs,
    224: charIDs,
    225: req225,  # Player is CPU
    559: storyBattles,  # # Story Battle Number
    563: gamemodes,  # Game mode
}

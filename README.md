# Pre-requisites

- Python 3.6.5 specifically
- Pywin32: `python -m pip install pywin32 --user`

# Exporting movesets

This tool exports movesets from memory, you therefore need the game running with the target moveset loaded up already.
The extractor works with both Tekken 7 and Tag 2, as there is little differences between their moveset formats.

## Exporting from Tekken 7
In order to work with Tekken 7, the extractor only needs the player's base addresses, to be indicated at the entry `p1_addr` of the file `game_addresses.txt`.
You have to then start a game with the targeted moveset loaded up, and simply running the tool `Ton-Chan's_Motbin_export.py` without any arguments will do the job.

Every moveset extracted from Tekken7 will be prefixed with `7_`

## Exporting from Tag2 (CEMU, Wii U emulator)
It used to be that you needed to get a new address everytime you restart CEMU to extract moveset, but that isn't the case anymore.
Simply run the extractor with the argument `tag2` to extract tag2 characters. Example:

`python Ton-Chan's_Motbin_export.py tag2`

Every moveset extracted from Tag2 will be prefixed with `2_`

# Importing moveset into Tekken 7

Movesets are imported directly in memory, requiring the game to be loaded up and being only temporary.
After having extracted a moveset, you can import it like such:

`Ton-Chan's_Motbin_import.py CHARACTER` 

**CHARACTER** is to be replaced with the folder name of the target character, containing the .json and animation data.
Administrator rights may be required to import the moveset into memory.

# TODO:

- Fix Tag2 projectiles (doesn't seem possible at all)
- Fix missing TAG2 commands that use command buffer. Placeholder?
- Make bound use screw ressource?
- Fix wallsplat grabs that just act as regular airborne grabs
- Fix Kunimitsu backturned 4 that doesn't turn around
- Fix bound floorbreak that doesn't bound
- Look at tag2 intro, especially mokujin & combot
# Pre-requisites

- Python 3.6.5 specifically
- Pywin32: `python -m pip install pywin32 --user`

# Exporting movesets

This tool exports movesets from memory, you therefore need the game running with the target moveset loaded up already.
The extractor works with both Tekken 7 and Tag 2, as there is little differences between their moveset formats.

## Exporting from Tekken 7
In order to work with Tekken 7, the extractor only needs the player's base address, to be indicated at the entry `p1_ptr` of the file `game_addresses.txt`.
You have to then start a game with the targeted moveset loaded up, and simply running the tool `Ton-Chan's_Motbin_export.py` without any arguments will do the job.

Every moveset extracted from Tekken7 will be prefixed with `7_`

## Exporting from Tag2 (CEMU, Wii U emulator)
In order to work with Tag2, you need to first get the base address of the game in Cemu, and feed it to the variable `cemu_base` in `game_addresses.txt`
This address changes everytime CEMU is started. You can find it by finding any game-related value (an easy one is 32770 for crouching and 32769 for standing, in big endian), then looking at what accesses the value and dumping the r13 register from there. The r13 register will contain the `cemu_base` address.
Then, you need to run the extractor with the argument `tag2`. Example:

`python Ton-Chan's_Motbin_export.py tag2`

Every moveset extracted from Tag2 will be prefixed with `2_`

# Importing moveset into Tekken 7

Movesets are imported directly in memory, requiring the game to be loaded up and being only temporary.
After having extracted a moveset, you can import it like such:

`Ton-Chan's_Motbin_import.py CHARACTER` 

**CHARACTER** is to be replaced with the folder name of the target character, containing the .json and animation data.
Administrator rights may be required to import the moveset into memory.

# TODO:

- Fix projectiles crashing when used on the wrong character (Geese projectile without Geese loaded)
- Fix missing TAG2 commands that use command buffer. Placeholder?
- Fix wallbreak, balcony break and floorbreak on both T7 & Tag2
- Fix throws crashing (use a placeholder throw data the throw cannot be fully imported)
- Fix high and low wallsplats that have broken animations in Tag2
- Make bound use screw ressource?

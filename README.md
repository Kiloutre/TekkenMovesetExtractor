# Pre-requisites

- Python 3.6.5 specifically.

Make sure that the python version is correct by running the following command in the command line:

`python --version`


- Pywin32

Install Pywin32 after python, by running this in the command line:

`python -m pip install pywin32 --user`

# Importing movesets: GUI tool (very pretty)

Simply run the GUI tool by double-clicking the file `GUI_TekkenMovesetExtractor.py`. The following interface will appear:

![alt text](https://i.imgur.com/OmQzpHB.png)


# Exporting movesets : Console Tool

This tool exports movesets from memory, you therefore need the game running with the target moveset loaded up already.
The extractor works with both Tekken 7 and Tag 2, as there is little differences between their moveset formats.

## Exporting from Tekken 7
In order to work with Tekken 7, the extractor only needs the player's base addresses, to be indicated at the entry `p1_addr` of the file `game_addresses.txt`.
You have to then start a game with the targeted moveset loaded up, and simply running the tool `motbinExport.py` without any arguments will do the job.

Every moveset extracted from Tekken7 will be prefixed with `7_`

## Exporting from Tag2 (CEMU, Wii U emulator)
In order to work with Tag2, you need to first get the base address of the game in Cemu, and feed it to the variable `cemu_base` in `game_addresses.txt`	It used to be that you needed to get a new address everytime you restart CEMU to extract moveset, but that isn't the case anymore.
This address changes everytime CEMU is started. You can find it by finding any game-related value (an easy one is 32770 for crouching and 32769 for standing, in big endian), then looking at what accesses the value and dumping the r13 register from there. The r13 register will contain the `cemu_base` address.	Simply run the extractor with the argument `tag2` to extract tag2 characters. Example:
Then, you need to run the extractor with the argument `tag2`. Example:	


`python motbinExport.py tag2`

Every moveset extracted from Tag2 will be prefixed with `2_`

# Importing moveset into Tekken 7

Movesets are imported directly in memory, requiring the game to be loaded up and being only temporary.
After having extracted a moveset, you can import it like such:

`python motbinImport.py CHARACTER` 

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
- Rename 'unknown' of cancel into 'cancel_option' on next update
- Remove reliance on Python 3.6.5
- Fix tag2 armor king D/B+2 excessive pushback
- Add export naming option

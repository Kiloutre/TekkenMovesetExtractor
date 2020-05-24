# GUI tool (very pretty)

Simply run the GUI tool by double-clicking the file `GUI_TekkenMovesetExtractor.py`. The following interface will appear:

![Interface](https://pbs.twimg.com/media/EYt5eqXWoAEXQtI.png:large)

The GUI tools allows you to export or import moveset simply by clicking buttons.

# GUI tool: Exporting from T7

Simply load the characters through any mean (practice mode, versus mode, etc), then click any "Export: Tekken 7:" button.
The characters will be extracted by default in the `extracted_chars/` folder.


# Exporting from Tag2

In order to work with Tag2, you need to first get the base address of the game in Cemu, and feed it to the variable `cemu_base` in `game_addresses.txt`
This address changes everytime CEMU is started. You can find it by first finding any game-related value using Cheat Engine's scans.
An easy value is `32770` for crouching and `32769` for standing, in `4 bytes big endian`.
Or `41943040` for crouching and `25165824` for standing, in regular `4 bytes` value type.
Once you've singled out a game-related value, right click on it and click "Find out what accesses this address". Unpause the game and look at the list:
R13 in these list is always cemu_base, and cemu_p1_addr will always be the second argument (ex: `r12` in `[r13 + r12 + 000000B8`
![Finding cemu_base and cemu_p1_addr]https://i.imgur.com/jsgYLm2.png

cemu_base will change with every cemu restart, so you will have to do this again.
Once both cemu_base and cemu_p1_addr are at the right value in `game_addresses.txt`, export characters by clicking the Export buttons in the interface.


# Running the sources

## Pre-requisites for running the sources:

- Python 3.6.5 specifically, newever version don't work with the current code.

- Pywin32 : `python -m pip install pywin32 --user`


# Exporting movesets : From source code (console tool)

This tool exports movesets from memory, you therefore need the game running with the target moveset loaded up already.
The extractor works with both Tekken 7 and Tag 2, as there is little differences between their moveset formats.

## Exporting from Tekken 7
In order to work with Tekken 7, the extractor only needs the player's base addresses, to be indicated at the entry `p1_addr` of the file `game_addresses.txt`.
You have to then start a game with the targeted moveset loaded up, and simply running the tool `motbinExport.py` without any arguments will do the job.

Every moveset extracted from Tekken7 will be prefixed with `7_`

## Exporting from Tag2 (CEMU, Wii U emulator)

Refer to the previous Tag2 instructions in the GUI section to see how are CEMU addresses obtained.
Once the game_addresses.txt file is correct, simply run the following command to export Tag2 movesets:

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
- Fix Wang vs Wang crescent moon into wallbreak
- Detect Tag2 version & choose the right address

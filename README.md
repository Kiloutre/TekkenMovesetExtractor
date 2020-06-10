Special thanks to: **Dantarion, Zen, Robi0990 and DennisStanistan**, who heavily helped in the reverse engineering part of this project!

# Download

Download link, with executable:

https://github.com/Kiloutre/TekkenMovesetExtractor/releases

# GUI tool (very pretty)

Simply run the GUI tool by double-clicking the file `GUI_TekkenMovesetExtractor.py`. The following interface will appear:

![Interface](https://pbs.twimg.com/media/EYt5eqXWoAEXQtI.png:large)

The GUI tools allows you to export or import moveset simply by clicking buttons.

# GUI tool: Exporting from T7

Simply load the characters through any mean (practice mode, versus mode, etc), then click any "Export: Tekken 7:" button.
The characters will be extracted by default in the `extracted_chars/` folder.


# Exporting from Tag2  (CEMU, Wii U emulator)

In order to work with Tag2, you need to first get the base address of the game in Cemu, and feed it to the variable `cemu_base` in `game_addresses.txt`
This address changes everytime CEMU is started.

You can find it by first finding any game-related value using Cheat Engine's scans.

An easy value is `32770` for crouching and `32769` for standing, in `4 bytes big endian`.
Or `41943040` for crouching and `25165824` for standing, in regular `4 bytes` value type.

Once you've singled out a game-related value, right click on it and click "Find out what accesses this address". Unpause the game and look at the list:
R13 in these list is always cemu_base, and cemu_p1_addr will always be the second argument (ex: `r12` in `[r13 + r12 + 000000B8`

![Finding cemu_base and cemu_p1_addr](https://i.imgur.com/jsgYLm2.png)

Once both cemu_base and cemu_p1_addr are at the right value in `game_addresses.txt`, export characters by clicking the Export buttons in the interface.
cemu_p1_addr only needs to be found once, unless you change the Tag2 version you're using (different region, etc)

# Importing through the GUI

Movesets are imported in memory, so you should have the game running if you want to import a moveset.
Two options are available to you:

- Loading the moveset in a simple way, which means it will go away at the next loading screen. Those are the `Import to` buttons.
- Using "Monitors", which will also load the moveset in memory, but force that moveset on a specific player **constantly**. Those are the `Monitor` buttons.

Both buttons work the same: Select a moveset by clicking on it in the moveset list to the left of the import buttons, then click Import OR Monitor.
Import requires the game to be already loaded, which is usually what you'd want to use to mess around in practice mode.
Monitors can be started even from the main menu, and will work fine no matter how long you play;
If you wish to play online with a friend, both players should use monitors so that they can force movesets before the game is loaded.


# Export/Import by running the source code (not necessary)

## Pre-requisites for running the sources:

- Python 3.6.5 specifically, newever version don't work with the current code.

- Pywin32 : `python -m pip install pywin32 --user`

## Exporting from Tekken 7
This tool exports movesets from memory, you therefore need the game running with the target moveset loaded up already.

In order to work with Tekken 7, the extractor only needs the player's base addresses, to be indicated at the entry `p1_addr` of the file `game_addresses.txt`.
This address should only change with patches, so you should never have to find it yourself.
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
g
`python motbinImport.py CHARACTER` 

**CHARACTER** is to be replaced with the folder name of the target character, containing the .json and animation data.
Administrator rights may be required to import the moveset into memory.

# TODO:

- Fix Tag2 projectiles (doesn't seem possible at all)
- Fix missing TAG2 commands that use command buffer. Placeholder?
- Look at tag2 intro, especially mokujin & combot
- Remove reliance on Python 3.6.5
- Add export naming option
- Automatically get cemu_base from CEMU location
- Import anim & move names like tekken 7 does
- Import camera and projectiles for Tekken 7. Lee crashes with Lili or Leo RA.
- Look into making ttt2 intro and outro end automatically
- Use opponent for tag2 outros (might not be viable)
- Delete files before exporting moveset
- Tekken ball imitation using Akuma fireball, greenscreend on tekken 3 beach
- (Jin) Dj tag2 vs DJ tag2, treasure battle, online player buttons, crash on loadscreen
- Green Ogre 3~4 crash
- Allow throws using item moves?
- Rename "group_cancels" to "generic_cancels"
- Rename "anim_max_len" to "anim_len" in moves
- Split command in two 4bytes
- Rename move's u17 to distance
- Make cancel extradata and moves' voiceclip use a field?
- Make reaction lists and u1 lists uses fields instead of arrays
- Split attack hitlevel in 2? need to keep the order the same for tag2
- Check out eliza in tekken revolution for projectile struct

Moveset editor:
- Window to list animations and copy one to another character's folder
- Add note that requirement lists must end with 881
- Add note that extraprop lists must end with type 0
- Fix modifying tag2 movesets, 'if you change the requirement of a move to screw / bound with any tag 2 character, the game insta crashes'
# Exporting movesets

This tool exports movesets from memory, you therefore need the game running with the target moveset loaded up already.
The extractor works with both Tekken 7 and TekkenTag2, as their is little differences between their moveset formats.
The importer however currently only works with Tekken 7. It wouldn't be too hard to adapt it to Tag2, though.

## Exporting from Tekken 7
In order to work with Tekken 7, the extractor only needs the player's base address, to be indicated at the entry `p1_ptr` of the file `game_addresses.txt`.
You have to then start a game with the targeted moveset loaded up, and simply running the tool `Ton-Chan's_Motbin_export.py` without any arguments will do the job.

Every moveset extracted from Tekken7 will be prefixed with `7_`

## Exporting from Tag2 (CEMU)
In order to work with Tag2, you need to first get the base address of the game in Cemu, and feed it to the variable `base` at the top of `Ton-Chan's_Motbin_export.py`.
This address changes everytime CEMU is started.
Then, you need to run the extractor with the argument `tag2`. Example:

`python Ton-Chan's_Motbin_export.py tag2`

Every moveset extracted from Tag2 will be prefixed with `2_`

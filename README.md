# Tekken Moveset Extractor By [kiloutre](https://twitter.com/kiloutre) 

This tool's main purpose is to port over move lists and mechanics from Tekken Tag 2 into Tekken 7.

It also allows you to change the move set of characters already in Tekken 7 to other characters in the 7 roster.

## Getting Started

This is quite an involved process in this early stage but we are working towards making it more accessible for players in the future.


### Prerequisites

There will be a few programs you will have to download before being able to use this tool with Tekken 7.

* [Tekken Moveset Extractor](https://github.com/Kiloutre/TekkenMovesetExtractor/releases/) - The tool that does all the magic.
* [Cemu](https://cemu.info/) - A emulator used to run the Wii U port of Tekken Tag 2.
* [Python 3.6.5](https://www.python.org/downloads/release/python-365/) - Packages from Python are needed for this tool to run.
* [PYWIN32 using PIP](http://www.qarevolution.com/5-step-install-pywin32-using-pip/) - Much needed Python extensions.
* [Cheat Engine](https://www.cheatengine.org/) - Used to look into the opcodes in Cemu.
* Wii U Games Files For Tekken Tag 2 - You will have to acquire this yourself

### Installing & Walkthrough

### Python 3.6.5

1. Download version 3.6.5 of Python from the link provided. Making sure to pick the "Windows x86-64 executable installer" under files, if you're running windows that is.

2. Make sure during installation you've checked the "Add Python 3.6 to PATH" option

3. Go Through the normal steps of the installation and take note of where you've installed it as that will come in handy in the future.

4. Once the setup has completed, hit close.

### PYWIN32 using PIP

1. Make sure this is done after installing Python 3.6.5

2. Follow the instructions on the link provided in Prerequisites

3. If you get a warning saying " WARNING: You are using pip version 19.2.3, however version 20.1.1 is available. You should consider upgrading via the 'python -m pip install --upgrade pip' command." Ignore it as the version provided is fine

### Cemu

1. To install Cemu, head to their main website located [here](https://cemu.info/), and download the latest version.

2. The only settings you will need to change in Cemu are the input controls as you will have to navigate the menus.

Note: Wii U game files will come packaged as such:

![alt text](https://i.imgur.com/4D9BFBQ.png)

4. Click File -> Load and navigate to the code folder shown in the image above.

5. This folder contains the file we will use to run Tag 2: **Tekken.rpx**

6. Tag 2 should now launch and if you've set your input settings up correctly you should be able to navigate the menus.

7. Select offline mode and then practice.

Note: Picking solo or tag here does not matter as you can select in the Extractor which player you want to export.

8. Now you can pick the character you wish to transfer over to Tekken 7

Note: Your opponent does not matter

9. Now pick any stage and sit idle in it as we continue installing the rest of the needed programs.

Note: Take note of what version of Tekken Tag 2 you have as there will be 2: US & EU. The US version requires an extra step I will detail later.

### Tekken Moveset Extractor Install

1. Go to the link provided in prerequisites and download **TekkenMovesetExtractor.zip** from the latest release.

2. You can place this anywhere. It does not need to be in the same directory as Tekken.

3. Do not run this as we have to configure our most important program first.

### Cheat Engine

This part will be the most complex part of this guide so read carefully

1. Make sure you downloaded the latest version of Cheat Engine from the link provided

2. The install is quite straightforward, at the end of the installation launch Cheat Engine (you can try out the tutorial if you want)

Note: We are going to use Cheat Engine to find our Cemu_Base code

4. In Cheat Engine there will be an icon that is glowing different colors, you will want to click that button and select Cemu from the list provided.

5. Now that the Cemu process has been selected, right-click on the box where it says Value Type and select the top option which should say **"Define new custom type (Auto Assembler)"**

6. A box will appear with some code in it, delete all the code in this box and replace it with the code provided in this [Paste Bin](https://pastebin.com/U3xSNvVE) and hit OK.

Note: Now the Value Type box should state **"4 Byte Big Endian"** 

7. In the blank Value box put in the value **"32770"** and while doing your first scan (by hitting New Scan) make sure in Cemu you are crouching in the game during the whole scan process.

8. Once the scan has completed, you can let your character stance. Now in the left address list you will notice that one of the addresses has the value of **"32769"** this is the address we need to double click.

Note: The value **"32770"** is used to identify when the character is crouching and the value **"32769"** is used to identify when the character is standing.

9. Now that you've double-clicked the address, it should appear in the bottom box below. right-click it and select **"Find out what accesses this address"** 

10. Hit yes to the confirmation. You will see a list of instructions, you will need to select the instruction that holds both **“R13+R12”**. See below:

![alt text](https://i.imgur.com/cQaoq3c.png)

11. Once selected and highlighted look down to the lower box and find **“R13=”** this is that cemu_base we require before converting with TME.

12. Speaking of TME, you will now want to navigate to where you placed TME and open the game_addresses.txt file.

13. Grab the value after “R13=” and format it like this example number: **“0x12F4EF70000”** (Remove 0’s from the front and retain the back) paste that formatted value into the text file we just opened right after the cemu_base = 

```
# CEMU base address, changes at every CEMU restart
cemu_base = 0x12F4EF70000 (This is a example value yours will differ)
```
**IF YOU HAVE THE EU VERSION OF TEKKEN TAG 2 YOU DO NOT NEED TO FOLLOW THE NEXT STEP**

14. In the text file you will find **“cemu_p1_addr = “** you will want to place the value **“0x10884C70”** if you are using the American version of Tekken Tag 2

```
# CEMU player addresses, constant
cemu_p1_addr  = 0x10884C70
```
15. Now save the text file and open **“TekkenMovesetExtractor.exe”**

Note: Be aware that every time you need to import new characters you haven’t imported before, you will have to follow these steps again (besides No. 14)

## Using Tekken Moveset Extractor

16. After running the program (you should still have Cemu open in practice mode with the character you want to import in player 1 slot) Hit the button **“Export: Tekken Tag2: Player 1”** (Give some time for this to export, the program may freeze during this process, do not worry as this is normal)

17. The program will now convert the chosen character’s move list into one that can be imported into Tekken 7 (You can see your exported characters in the list on the right side of the application. (2_ means Tag 2 and 7_ mean Tekken 7)

![alt text](https://i.imgur.com/8Z67Rc9.png)

18. If you are happy with the list of characters you have imported, you can now close Cemu but make sure you do not close down **”TekkenMovesetExtractor.exe”** (Do take note that if you are wanting to import more characters after closing Cemu, you will have to follow the cheat engine section again)

### Importing into Tekken 7

1. Launch Tekken 7 and jump into practice with whatever Tekken 7 character you want

2. Once in practice mode head over to the Extractor, select one character from the list of imported characters and hit **”Monitor P1”**

3. You should now have the movelist of the character you chose to import!

And you’re done!

A few notes to end with:

* You can export Tekken 7 characters using the **”Export: Tekken7: Player 1”** option. This will add them to the list to be imported.
* This can be used online as long as the other person is running the tool also and has setup P2 as the character you have imported for yourself (if you don’t follow those rules, you will be desyncing a lot)
* A lot of rage arts and intro/outros are broken when using this tool


This guide was created by [LpeX](https://twitter.com/mrlpex)

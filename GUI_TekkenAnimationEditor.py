# Python 3.6.5

from tkinter import Tk, Frame, Listbox, Label, Scrollbar, StringVar, Toplevel, Menu, messagebox, Text, simpledialog, Button
from tkinter.ttk import Entry, Style
from Addresses import game_addresses, GameClass, VirtualAllocEx, VirtualFreeEx, MEM_RESERVE, MEM_COMMIT, PAGE_EXECUTE_READWRITE, VirtualFreeEx, MEM_DECOMMIT, MEM_RELEASE
import os
import re
import struct
import ctypes
import math

dataPath = "./AnimationEditor/"
editorVersion = "0.1"
        
colors = {
    'dark': {
        'BG': '#222',
        'labelBgColor': '#333',
        'listItemEvenBG': "#555",
        'listItemOddBG': "#666",
        'listItemText': "white",
        'ListBGColor': "#222",
        'buttonBGColor': "#666",
        'buttonTextColor': "#ddd",
        'labelTextColor': "#ddd",
        'listSelectedItemBG': '#756059',
        'listSelectedItem': '#eb9b7f',
        'groupColor0': '#683870',
        'groupColor1': '#307530',
        'groupColor2': '#2b6a75',
        'groupColor3': '#36248f',
        'groupColor4': '#ab3a8f',
        'groupColor5': '#c42929',
        'groupColor6': '#b88c2e',
    },
    'default': {
        'labelBgColor': '#ddd'
    }
}

groupedFields = [
    0, #Movement
    3, #Position
    9, #Rotation
    12, #Upper Body
    15, #Lower Body
    21, #Neck stuff
    24, #Neck stuff
    27, #Right Inner Shoulder
    30, #Right Outer Shoulder
    39, #Left Outer Shoulder
    42, #Left Outer Shoulder
    51,
    60
]

mirroredGroups = {
    39: 27,
    42: 30,
    60: 51,
}

fieldLabels = {
    0: 'Movement X',
    1: 'Height',
    2: 'Movement Z',
    3: 'Pos X',
    4: 'Pos Y (Height2)',
    5: 'Pos Z',
    6: 'Field 7',
    7: 'Field 8',
    8: 'Field 9',
    9: 'Rot X',
    10: 'Rot Y',
    11: 'Rot Z',
    12: 'Upper Body X',
    13: 'Upper Body Y',
    14: 'Upper Body Z',
    15: 'Lower Body X',
    16: 'Lower Body Y',
    17: 'Lower Body Z',
    18: 'Spine Flexure',
    19: 'Field 20',
    20: 'Field 21',
    21: 'Neck 22',
    22: 'Neck 23',
    23: 'Neck 24',
    24: 'Neck 25',
    25: 'Neck 26',
    26: 'Neck 27',
    27: 'Right Inner Shoulder X',
    28: 'Y',
    29: 'Z',
    30: 'Right Outer Shoulder X',
    31: 'Y',
    32: 'Z',
    33: 'Right Elbow',
    34: 'Right Hand 1',
    35: 'Right Hand 2',
    36: 'Right Hand 3',
    37: 'Right Hand 4',
    38: 'Right Hand 5',
    39: 'Left Inner Shoulder X',
    40: 'Y',
    41: 'Z',
    42: 'Left Outer Shoulder X',
    43: 'Y',
    44: 'Z',
    45: 'Left Elbow',
    46: 'Left Hand 1',
    47: 'Left Hand 2',
    48: 'Left Hand 3',
    49: 'Left Hand 4',
    50: 'Left Hand 5',
    51: 'Right Hip X',
    52: 'Right Hip Y',
    53: 'Right Hip Z',
    54: 'Right Knee Extension',
    55: 'Right Foot X',
    56: 'Right Foot Y',
    57: 'Right Foot Z',
    58: 'Right Leg 58',
    59: 'Right Leg 59',
    60: 'Left Hip X',
    61: 'Left Hip Y',
    62: 'Left Hip Z',
    63: 'Left Knee Extension',
    64: 'Left Foot X',
    65: 'Left Foot Y',
    66: 'Left Foot Z',
    67: 'Left Leg 68',
    68: 'Left Leg 69'
}

def getColor(key):
    isDark = True
    return colors['dark' if isDark else 'default'].get(key, '#fff')
    
def getAnimationList():
    if not os.path.isdir(dataPath):
        return []
    return [file for file in os.listdir(dataPath) if not os.path.isdir(dataPath + file) and file.endswith(".bin")]
     
def isFloat(value):
    return len(value) > 0 and re.match('^\-?[0-9]+(\.[0-9]+)?$', value)
     
class Animation:
    AnimC8OffsetTable = {
        0x17: 0x64,
        0x19: 0x6C,
        0x1B: 0x74,
        0x1d: 0x7c,
        0x1f: 0x80,
        0x21: 0x8c,
        0x23: 0x94,
        0x31: 0xcc 
    }
    
    movementOffsets = [0, 0x8, 0xC, 0x14]

    def __init__(self, filename=None, data=None):
        if filename == None and data == None:
            raise
            
        if filename != None:
            with open(filename, "rb") as f:
                self.data = list(f.read())
        else:
            self.data = data
            
        self.type = self.byte(0)
        self.type2 = self.byte(2)
        self.length = self.getLength()
        self.offset = self.getOffset()
        self.frame_size = self.getFramesize()
        self.field_count = int(self.frame_size / 4)
        self.size = self.calculateSize()
        self.recalculateSize() #Crop or add missing bytes if needed
        
    def recalculateSize(self):
        pastSize = self.size
        self.size = self.calculateSize()
        if self.size > pastSize:
            self.data += [0] * (self.size - pastSize)
        elif self.size < pastSize:
            self.data = self.data[:self.size]

    def calculateSize(self):
        if self.type == 0xC8:
            return self.getOffset() + (self.getFramesize() * self.length)
        else:
            return 0
        
    def getOffset(self):
        if self.type == 0xC8:
            return Animation.AnimC8OffsetTable[self.type2]
        else:
            return 0
        
    def getFramesize(self):
        if self.type  == 0xC8:
            return self.type2 * 0xC
        else:
            return 0
        
    def getLength(self):
        if self.type == 0xC8:
            return self.int(4)
        else:
            return self.short(self.short(2) * 2 + 4)
    
    def bToInt(self, offset, length):
        return int.from_bytes(bytes(self.data[offset:offset+length]), 'little')
    
    def int(self, offset):
        return self.bToInt(offset, 4)
    
    def short(self, offset):
        return self.bToInt(offset, 2)
        
    def byte(self, offset):
        return self.bToInt(offset, 1)
        
    def float(self, offset):
        return struct.unpack('f', bytes(self.data[offset:offset + 4]))[0]
            
    def writeInt(self, value, offset):
        for i in range(4):
            byteValue = (value >> (i * 8) ) & 0xFF
            self.data[offset + i] = byteValue
            
    def writeFloat(self, value, offset):
        byteData = struct.pack('f', value)
        for i in range(4):
            self.data[offset + i] = int(byteData[i])
        
    def getFieldOffset(self, frame, fieldId):
        if fieldId > self.field_count:
            raise
        return self.offset + (frame * self.frame_size) + (4 * fieldId)
        
    def getField(self, frame, fieldId):
        if fieldId > self.field_count:
            raise
        return self.float(self.getFieldOffset(frame, fieldId))
                
    def setField(self, value, frame, fieldId):
        if fieldId > self.field_count:
            raise
        self.writeFloat(value, self.offset + (frame * self.frame_size) + (4 * fieldId))
        
class AnimationSelector:
    def __init__(self, root, rootFrame):
        self.root = root
        mainFrame = Frame(rootFrame)
        mainFrame.pack(side='left', fill='y')
        
        animlist = Listbox(mainFrame, bg=getColor('ListBGColor'))
        animlist.bind('<<ListboxSelect>>', self.onSelectionChange)
        animlist.pack(fill='both', expand=1)
        
        buttons = [
            ("Load selected animation to editor", self.LoadAnimationToEditor),
            ("Extract game animation to file", self.root.ExtractCurrentAnimation),
            ("Duplicate file", self.CopyFile),
        ]
        
        for label, callback in buttons:
            newButton = Button(mainFrame, text=label, command=callback, bg=getColor('buttonBGColor'), fg=getColor('buttonTextColor'))
            newButton.pack(fill='x')
            
        liveEditingLabel = Label(mainFrame, bg=getColor('BG'), fg=getColor('labelTextColor'), text='Live editing:')
        liveEditingLabel.pack(fill='x')
        
        buttons2 = [
            ("Full anim [OFF]", self.root.ToggleLiveEditing),
            ("Frame-by-Frame [OFF]", self.root.ToggleFrameByFrame),
            ("Lock-In-Place [OFF]", self.ToggleLockInPlace),
        ]
       
        self.liveButtons = []
        for label, callback in buttons2:
            newButton = Button(mainFrame, text=label, command=callback, bg=getColor('buttonBGColor'), fg=getColor('buttonTextColor'))
            newButton.pack(fill='x')
            self.liveButtons.append(newButton)
        
        self.animlist = animlist
        self.frame = mainFrame
        
        self.itemList = []
        self.visible = True
        self.selectionIndex = -1
        
    def LoadAnimationToEditor(self):
        if self.selectionIndex < 0 or self.selectionIndex >= len(self.itemList):
            messagebox.showinfo('No animation selected', 'You have not selected an animation in the list', parent=self.root.window)
            return
        filename = self.itemList[self.selectionIndex]
        self.root.LoadAnimation(filename)
        self.colorItemlist()
        
    def CopyFile(self):
        if self.selectionIndex < 0 or self.selectionIndex >= len(self.itemList): return
        filename = self.itemList[self.selectionIndex]
        newFilename = filename[:-4] + "_new.bin"
        with open(dataPath + newFilename, "wb") as f:
            with open(dataPath + filename, "rb") as ff:
                f.write(ff.read())
        self.updateItemlist()
        
    def ToggleLockInPlace(self):
        self.root.ToggleLockInPlace()
        self.liveButtons[2]['text'] = 'Lock-In-Place [ON]' if self.root.lockInPlace else 'Lock-In-Place [OFF]'
        
    def SetLiveEditingButtonText(self):
        self.liveButtons[0]['text'] = 'Full anim [ON]' if self.root.fullanimEditing else 'Full anim [OFF]'
        self.liveButtons[1]['text'] = 'Frame-by-Frame [ON]' if self.root.frameByFrameEditing else 'Frame-by-Frame [OFF]'
        
    def toggleVisibility(self):
        if self.visible:
            self.hide()
        else:
            self.show()
       
    def hide(self):
        self.frame.pack_forget()
        self.visible = False
       
    def show(self):
        #self.root.MoveSelector.hide()
        self.frame.pack(side='left', fill='y')
        #self.root.MoveSelector.show()
        self.visible = True
        
    def colorItemlist(self):
        colors = [
            [getColor('listItemEvenBG'), getColor('listItemOddBG')]
        ]
        for i, item in enumerate(self.itemList):
            if i == self.selectionIndex:
                self.animlist.itemconfig(i, {'bg': getColor('listSelectedItemBG'), 'fg': getColor('listSelectedItem')})
            else:
                color = colors[0][i & 1]
                self.animlist.itemconfig(i, {'bg': color, 'fg': getColor('listItemText')})
    
        
    def updateItemlist(self):
        self.selectionIndex = -1
        self.animlist.delete(0, 'end')
        
        animationList = getAnimationList()
        if len(animationList) == 0:
            self.animlist.insert(0, "No animation...")
            self.animlist.itemconfig(0, {'fg': getColor('listItemText')})
        else:
            for anim in animationList: self.animlist.insert('end', anim)
        self.itemList = animationList
        self.colorItemlist()

    def onSelectionChange(self, event):
        if len(self.itemList) == 0:
            return
        w = event.widget
        try:
            index = int(w.curselection()[0])
            self.selectionIndex = int(index)
        except:
            self.selectionIndex = -1
        
def createMenu(root, menuActions, validationFunc=None, rootMenu=True):
    newMenu = Menu(root, tearoff=0)
    for label, command in menuActions:
        if isinstance(command, list):
            subMenu = createMenu(newMenu, command, validationFunc=validationFunc, rootMenu=False)
            newMenu.add_cascade(label=label, menu=subMenu)
        elif command == "separator":
            if rootMenu:
                newMenu.add_command(label='|', state='disabled')
            else:
                newMenu.add_separator()
        elif command == None:
            newMenu.add_command(label=label, state="disabled")
        else:
            wrappedFunction = None
            if validationFunc:
                wrappedFunction = lambda validationFunc=validationFunc, command=command : command() if validationFunc() else None
            else:
                wrappedFunction = command
            newMenu.add_command(label=label, command=wrappedFunction)
    return newMenu

class BaseFormEditor:
    def __init__(self, root, rootFrame, col=0, row=0, title=""):
        self.root = root
        self.rootFrame = rootFrame
        self.initEditor(col, row)
        
        if title != "": self.setTitle(title)
        
    def initEditor(self, col, row):
        container = Frame(self.rootFrame, bg=getColor('BG'))
        container.grid(row=row, column=col, sticky="nsew")
        #container.pack_propagate(False)
        
        label = Label(container, bg=getColor('labelBgColor'), fg=getColor('labelTextColor'))
        label.pack(side='top', fill='x')
        
        content = Frame(container, bg=getColor('BG'))
        content.pack(side='top', fill='both', expand=True)
        
        self.container = content
        self.label = label
        
    def setTitle(self, text):
        self.label['text'] = text
        
class FieldEditor:
    def __init__(self, root, rootFrame, fieldId, color=None):
        self.root = root
        self.rootFrame = rootFrame
        self.fieldId = fieldId
        
        
        self.initEditor(color)
        self.resetForm()
        
    def initEditor(self, labelColor):
        container = Frame(self.rootFrame, bg=getColor('BG'))
        container.pack(side='left', padx='1')
        
        if labelColor == None: labelColor = getColor('labelBgColor')
        
        label = Label(container, bg=labelColor, fg=getColor('labelTextColor'))
        label.pack(side='top', fill='x')
        
        content = Frame(container, bg=getColor('BG'))
        content.pack(side='top')
        
        sv = StringVar()
        sv.trace("w", lambda name, index, mode: self.onchange())
        fieldInput = Entry(content, textvariable=sv)
        fieldInput.pack()
        self.fieldInput = fieldInput
        self.sv = sv
        
        self.container = content
        self.label = label
        
    def setValue(self, newval, enable=False):
        self.editingEnabled = False
        self.sv.set(newval)
        self.editingEnabled = True
        
        if enable: 
            self.fieldInput.config(state='enabled')
            self.editingEnabled = True
        
    def onchange(self):
        if not self.editingEnabled: return
        value = self.sv.get()
        self.root.onFieldChange(self.fieldId, value)
        
    def setTitle(self, text):
        self.label['text'] = text
        
    def resetForm(self):
        self.setValue('')
        self.setTitle('')
        self.fieldInput.config(state='disabled')
        self.editingEnabled = False
        
def getFieldGroupIndex(id):
    if id in groupedFields: return groupedFields.index(id)
    elif id - 1 in groupedFields: return groupedFields.index(id - 1)
    elif id - 2 in groupedFields: return groupedFields.index(id - 2)
    else: return -1
    
def getFieldColor(fieldId, groupIndex):
    groupColorCount = 7
    
    colorIndex = groupIndex
    return getColor('groupColor' + str(colorIndex % groupColorCount))
      
class AnimationEditor(BaseFormEditor):
    def __init__(self, root, rootFrame):
        BaseFormEditor.__init__(self, root, rootFrame, title="No animation loaded")
        
        t = Frame(self.container, bg=getColor('BG'))
        t.pack(side='top')

        
        #FrameGoto = Frame(t)
        #FrameGoto.pack(side='top')
        currFrameLabel = Label(t, text='Frame:', fg=getColor('labelTextColor'), bg=getColor('labelBgColor'))
        currFrameLabel.pack(side='left')
        
        sv = StringVar()
        sv.trace("w", lambda name, index, mode, sv=sv: self.onFrameInput(sv))
        fieldInput = Entry(t, textvariable=sv)
        fieldInput.pack(side='left')
        
        separatorLabel = Label(t, text=' | ', fg=getColor('labelTextColor'), bg=getColor('labelBgColor'))
        #separatorLabel.grid(column=3, row=0)
        separatorLabel.pack(side='left')
        
        prevFrameButton = Button(t, fg=getColor('buttonTextColor'), bg=getColor('buttonBGColor'), text='< Previous ', command=lambda : self.setFrame(self.currentFrame - 1))
        prevFrameButton.pack(side='left')
        #prevFrameButton.grid(column=0, row=0)
        
        currFrameLabel = Label(t, text='', fg=getColor('labelTextColor'), bg=getColor('labelBgColor'))
        currFrameLabel.pack(side='left')
        #currFrameLabel.grid(column=1, row=0)
        self.currFrameLabel = currFrameLabel
        
        nextFrameButton = Button(t,  fg=getColor('buttonTextColor'),bg=getColor('buttonBGColor'), text=' Next >', command=lambda : self.setFrame(self.currentFrame + 1))
        nextFrameButton.pack(side='left')
        #nextFrameButton.grid(column=2, row=0)
        
        separatorLabel = Label(t, text=' | ', fg=getColor('labelTextColor'), bg=getColor('labelBgColor'))
        #separatorLabel.grid(column=3, row=0)
        separatorLabel.pack(side='left')
        
        prevFrameButton = Button(t, fg=getColor('buttonTextColor'),bg=getColor('buttonBGColor'), text='< Previous field ', command=lambda : self.setField(self.currentField - 1))
        prevFrameButton.pack(side='left')
        #prevFrameButton.grid(column=4, row=0)
        
        currFieldLabel = Label(t, text='', fg=getColor('labelTextColor'), bg=getColor('labelBgColor'))
        currFieldLabel.pack(side='left')
        #currFieldLabel.grid(column=5, row=0)
        self.currFieldLabel = currFieldLabel
        
        nextFrameButton = Button(t,  fg=getColor('buttonTextColor'),bg=getColor('buttonBGColor'), text=' Next field >', command=lambda : self.setField(self.currentField + 1))
        nextFrameButton.pack(side='left')
        #nextFrameButton.grid(column=6, row=0)
        
        self.fields = []
        
        for i in range(9):
            fieldContainer = Frame(self.container, bg=getColor('BG'))
            fieldContainer.pack(side='top', fill='both', pady=10)
            
            for x in range(8):
                fieldId = i * 8 + x
                
                if fieldId >= 69: break
                
                color = None
                groupIndex = getFieldGroupIndex(fieldId)
                if groupIndex > -1:
                    color = getFieldColor(fieldId, groupIndex)
                
                newField = FieldEditor(self, fieldContainer, fieldId, color)
                newField.setTitle(fieldLabels.get(fieldId, "Field %d" % (fieldId + 1)))
                self.fields.append(newField)
        
        self.fieldCount = len(self.fields)
        self.reset()
        
    def onFrameInput(self, sv):
        value = sv.get()
        try:
            value = int(value) - 1
            if value < self.Animation.length and value >= 0:
                self.setFrame(value)
        except:
            return
        
    def onFieldChange(self, fieldId, value):
        if isFloat(value):
            actualFieldId = fieldId + self.currentField
            self.Animation.setField(float(value), self.currentFrame, actualFieldId)
            self.root.onFieldChange(self.currentFrame, actualFieldId, value)
        
    def setField(self, newField):
        if self.Animation == None or newField > (self.Animation.field_count - self.fieldCount) or newField < 0: return
        self.currentField = newField
        self.currFieldLabel['text'] = "Field %d/%d" % (newField + 1, self.Animation.field_count)
        self.setFrame(self.currentFrame)
        
    def setFrame(self, newFrame):
        if self.Animation == None or newFrame < 0 or newFrame >= self.Animation.length: return
        self.currentFrame = newFrame
        self.currFrameLabel['text'] = "Frame %d/%d" % (newFrame + 1, self.Animation.length)
        self.root.onFrameChange(newFrame)
        
        for i in range(self.fieldCount):
            actualFieldId = i + self.currentField
            if actualFieldId < self.Animation.field_count:
                value = ("%01.3f" % self.Animation.getField(self.currentFrame, actualFieldId)).rstrip('0').rstrip('.')
                if float(value) == 0 and value[0] == "-": value = value[1:]
                self.fields[i].setValue(value, enable=True)
                self.fields[i].setTitle(fieldLabels.get(actualFieldId, "Field %d" % (actualFieldId + 1)))
            else:
                self.fields[i].resetForm()
        
    def LoadAnimation(self, filename):
        self.reset()
        self.Animation = Animation(dataPath + filename)
        
        if self.Animation.type != 0xC8:
            self.setTitle("Cannot load " + filename + ", animation format is not supposed")
            return False
        
        self.animationName = filename
        info = "  |  Length: %d frames  |  Bone per frame: %d  |  Size: %d bytes (%d KB)" % (self.Animation.length, self.Animation.field_count, self.Animation.size, self.Animation.size / 1000)
        self.setTitle("Editing: " + filename + info)
        self.setFrame(0)
        self.currFieldLabel['text'] = "Field 1/%d" % (self.Animation.field_count)
        return True
        
    def reset(self):
        self.Animation = None
        self.animationName = None
        self.currentFrame = 0
        self.currentField = 0
        self.currFrameLabel['text'] = 'Frame 0/0'
        self.currFieldLabel['text'] = 'Field 0/0'
        
class LiveEditor:
    def __init__(self, root):
        self.root = root
        self.playerAddress = game_addresses.addr['t7_p1_addr']
        self.stop()
        
    def setAnimation(self, anim):
        self.Animation = anim
        
    def startIfNeeded(self):
        if not self.running:
            return self.loadProcess()
        try:
            self.T.readInt(self.playerAddress, 4)
        except:
            self.stop()
        return self.running
        
    def isLastAllocationValid(self):
        if self.lastAllocation != None:
            try:
                return self.T.readInt(self.lastAllocation, 1) == 0xC8
            except:
                return False
        return False
        
    def CheckRunning(self):
        if not self.running: return False
        try:
            self.T.readInt(self.playerAddress, 4)
            if self.lastAllocation != None and self.T.readInt(self.lastAllocation, 1) != 0xC8:
                raise
        except:
            self.stop()
            return False
        return True
        
    def loadProcess(self):
        try:
            self.T = GameClass("TekkenGame-Win64-Shipping.exe")
            self.running = True
        except Exception as err:
            print(err)
            self.stop()
        return self.running
        
    def stop(self):
        self.Animation = None
        self.running = False
        self.T = None
        self.lastAllocation = None
        self.lastAllocationSize = 0
        
    def allocateMem(self, allocSize):
        return VirtualAllocEx(self.T.handle, 0, allocSize, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)
        
    def freeMem(self, addr, size):
        return VirtualFreeEx(self.T.handle, addr, 0, MEM_RELEASE) != None
        
    def writeFloat(self, addr, value):
        self.T.writeBytes(addr, struct.pack('f', value))
        
    def readFloat(self, addr):
        return struct.unpack('f', self.T.readBytes(addr, 4))[0]
        
    def getCurrentAnimationAddr(self):
        currmoveAddr = self.T.readInt(self.playerAddress + 0x220, 8)
        animationAddr = self.T.readInt(currmoveAddr + 0x10, 8)
        return animationAddr
        
    def getCurrentAnimationFilename(self):
        currmoveAddr = self.T.readInt(self.playerAddress + 0x220, 8)
        nameAddr = self.T.readInt(currmoveAddr + 0x8, 8)
        
        end = 0
        while self.T.readInt(nameAddr + end, 1) != 0:
            end += 1
        return self.T.readBytes(nameAddr, end).decode('ascii')
        
    def getCurrentAnimationData(self):
        animationAddr = self.getCurrentAnimationAddr()
        animationType = self.T.readInt(animationAddr, 1)
        if animationType == 0x64: return animationAddr, 0x64, 0, 0, 0
        
        animationLength = self.T.readInt(animationAddr + 4, 4)
        animationType2 = self.T.readInt(animationAddr + 2, 1)
        animationSize = Animation.AnimC8OffsetTable[animationType2] + ((animationType2 * 0xC) * animationLength)
        
        return animationAddr, animationType, animationType2, animationLength, animationSize
        
    def ExtractCurrentAnimation(self):
        if not self.startIfNeeded(): return None
        
        animationAddr, animationType, animationType2, animationLength, animationSize = self.getCurrentAnimationData()
        if animationType == 0x64:
            messagebox.showinfo('Incompatible animation', 'Cannot extract this animation: unsupported format', parent=self.root.window)
            return
        
        extractedAnim = Animation(data=list(self.T.readBytes(animationAddr, animationSize)))
        name = ''
        while len(name) == 0:
            name = simpledialog.askstring("Animation name", "What will be the file name? (Do not add .bin at the end)", parent=self.root.window, initialvalue = self.getCurrentAnimationFilename())
            if name == None: return
        with open(dataPath + name + '.bin', 'wb') as f:
            f.write(bytes(extractedAnim.data))
            
        self.root.onAnimationExtraction()
        
    def writeLoadedAnimBytes(self, singleFrameOfData=False):
        if self.lastAllocation == None: return
        if singleFrameOfData == False:
            self.T.writeBytes(self.lastAllocation, bytes(self.Animation.data))
        else:
            self.T.writeBytes(self.lastAllocation, bytes(self.Animation.data[:self.Animation.offset + self.Animation.frame_size]))
        
    def loadAnimInMemory(self, anim):
        if not self.startIfNeeded(): return None
        self.Animation = anim
        currmoveAddr = self.T.readInt(self.playerAddress + 0x220, 8)
        
        animationAddr = self.allocateMem(anim.size)
        freeAddr, freeSize = None, None
        if self.isLastAllocationValid():
            freeAddr, freeSize = self.lastAllocation, self.lastAllocationSize
        
        self.lastAllocation = animationAddr
        self.lastAllocationSize = anim.size
        
        self.writeLoadedAnimBytes()
        self.T.writeInt(currmoveAddr + 0x10, animationAddr, 8)
        
        if freeAddr != None:
            self.freeMem(freeAddr, freeSize)
        
        return animationAddr
        
    def resetLockInPlaceBytes(self, singleFrame = False):
        if self.lastAllocation == None: return

        length = self.Animation.length if singleFrame == False else 1
        
        for i in range(length):
            baseOffset = self.lastAllocation + self.Animation.offset
            baseLocalOffset = self.Animation.offset
            
            for offset in Animation.movementOffsets:
                self.T.writeBytes(baseOffset + offset, bytes(self.Animation.data[baseLocalOffset + offset:baseLocalOffset + offset + 4]))
                
            baseOffset += self.Animation.frame_size
            baseLocalOffset += self.Animation.frame_size
        
    def writeLockInPlaceBytes(self, singleFrame = False):
        if self.lastAllocation == None: return
        
        length = self.Animation.length if singleFrame == False else 1
        
        for i in range(length):
            baseOffset = self.lastAllocation + self.Animation.offset
            
            for offset in Animation.movementOffsets:
                self.T.writeBytes(baseOffset + offset, bytes([0] * 4))
                
            baseOffset += self.Animation.frame_size
        
    def writeSingleFrameBytes(self, frame):
        if self.lastAllocation == None: return
        totalSize = self.Animation.offset + self.Animation.frame_size
        startingBytePos = self.Animation.offset + (self.Animation.frame_size * frame)
        frameBytes = self.Animation.data[startingBytePos:startingBytePos + self.Animation.frame_size]
        
        self.T.writeBytes(self.lastAllocation + self.Animation.offset, frameBytes)
        self.T.writeInt(self.lastAllocation + 4, 1, 4)
        
        if self.root.lockInPlace:
            self.writeLockInPlaceBytes(True)
        
    def currentAnimIsLoadedOne(self):
        return self.running and self.lastAllocation != None and self.lastAllocation == self.getCurrentAnimationAddr()
        
    def readPointerPath(self, baseAddr, ptrlist):
        currAddr = self.T.readInt(baseAddr, 8)
        for ptr in ptrlist:
            currAddr = self.T.readInt(currAddr + ptr, 8)
        return currAddr
        
    def lockCamera(self):
        if not self.startIfNeeded(): return
        self.T.writeBytes(0x148B56F30, bytes([0x90] * 8))
        self.T.writeBytes(0x1416A2A4E, bytes([0x90] * 8))
        self.T.writeBytes(0x1416A2A65, bytes([0x90] * 6))
        self.T.writeBytes(0x1416A2A40, bytes([0x90] * 8))
        self.T.writeBytes(0x1416a2a5b, bytes([0x90] * 6))
        
    def unlockCamera(self):
        if not self.startIfNeeded(): return
        self.T.writeBytes(0x148B56F30, bytes([0xF3, 0x0f, 0x11, 0x89, 0x9c, 0x03, 000, 0x0]))
        self.T.writeBytes(0x1416A2A4E, bytes([0xF2, 0x0f, 0x11, 0x87, 0x04, 0x04, 0x0, 0x0]))
        self.T.writeBytes(0x1416A2A65, bytes([0x89, 0x87, 0x0c, 0x04, 0x0, 0x0]))
        self.T.writeBytes(0x1416A2A40, bytes([0xF2, 0x0F, 0x11, 0x87, 0xF8, 0x03, 0x0, 0x0]))
        self.T.writeBytes(0x1416a2a5b, bytes([0x89, 0x87, 0, 0x04, 0, 0]))
        
    def getCameraAddr(self):
        return self.readPointerPath(0x14377FCF0, [0x30, 0x418])
        
    def setCameraPos(self, id):
        if not self.startIfNeeded(): return
        camAddr = self.getCameraAddr()
        
        cam = self.root.cameraPresets[id]
        #self.writeFloat(camAddr + 0, 0) #aspect ratio
        self.writeFloat(camAddr + 0x39C, cam['fov']) #FOV
        self.writeFloat(camAddr + 0x404, cam['roty']) #roty
        self.writeFloat(camAddr + 0x40C, cam['tilt']) #tilt
        
        if cam['relative'] == 1: #Height-relativity
            self.writeFloat(camAddr + 0x408, cam['rotx']) #rotx
            self.writeFloat(camAddr + 0x3F8, cam['x']) #x
            self.writeFloat(camAddr + 0x3FC, cam['y']) #y
            self.writeFloat(camAddr + 0x400, (self.getPlayerHeight()) + cam['z']) #y
        elif cam['relative'] == 2: #Fullpos relativity (rotation included)
            fullAngle = (math.pi * 2)
            playerPos = self.getPlayerPos()
            playerRot = self.getPlayerRot() * (fullAngle / 65535)
            
            distance = math.sqrt(cam['x'] **2 + cam['y'] ** 2)
            camAngle = math.atan2(cam['y'], cam['x'])
            
            finalAngle = (camAngle - playerRot)
            
            newx = (distance) * math.cos(finalAngle)
            newy = (distance) * math.sin(finalAngle)
            
            camRotx = (cam['rotx'] - (self.getPlayerRot() * (360/ 65535))) % 360
            self.writeFloat(camAddr + 0x408, camRotx) #rotx
            self.writeFloat(camAddr + 0x3F8, newx + playerPos['x']) #x
            self.writeFloat(camAddr + 0x3FC, newy + playerPos['y']) #y
            self.writeFloat(camAddr + 0x400, playerPos['z'] + cam['z']) #y
        else:
            self.writeFloat(camAddr + 0x408, cam['rotx']) #rotx
            self.writeFloat(camAddr + 0x3F8, cam['x']) #x
            self.writeFloat(camAddr + 0x3FC, cam['y']) #y
            self.writeFloat(camAddr + 0x400, cam['z']) #z
            
    def getCameraPos(self):
        if not self.startIfNeeded(): return None
        camAddr = self.getCameraAddr()
        return {
            'fov': self.readFloat(camAddr + 0x39C),
            'rotx': self.readFloat(camAddr + 0x408),
            'roty': self.readFloat(camAddr + 0x404),
            'tilt': self.readFloat(camAddr + 0x40C),
            'x': self.readFloat(camAddr + 0x3F8),
            'y': self.readFloat(camAddr + 0x3FC),
            'z': self.readFloat(camAddr + 0x400)
        }
        
    def getPlayerHeight(self):
        return self.getPlayerFloorheight() + self.readFloat(self.playerAddress + 0xE4) / 10
        
    def getPlayerFloorheight(self):
        return self.readFloat(self.playerAddress + 0x1B0) / 10
        
    def getPlayerPos(self):
        return {
            'x': self.readFloat(self.playerAddress + 0xE8) / 10,
            'y': -(self.readFloat(self.playerAddress + 0xE0) / 10),
            'z': self.getPlayerHeight(),
        }
        
    def getPlayerRot(self):
        return self.T.readInt(self.playerAddress + 0xEE, 2)
        
class GUI_TekkenAnimationEditor():
    def __init__(self, mainWindow=True):
        window = Tk() if mainWindow else Toplevel()
        self.window = window

        boldButtonStyle = Style()
        boldButtonStyle.configure("Bold.TButton", font = ('Sans','10','bold'))
        
        self.setTitle()
        window.iconbitmap('InterfaceData/komari.ico')
        window.minsize(960, 540)
        window.geometry("1280x770")
        
        self.AnimationSelector = AnimationSelector(self, window) #Side menu
        self.AnimationSelector.updateItemlist()
        
        editorFrame = Frame(window, bg=getColor('BG')) #Main frale
        editorFrame.pack(side='right', fill='both', expand=1)
        editorFrame.grid_columnconfigure(0, weight=1, uniform="group1")
        editorFrame.grid_rowconfigure(0, weight=1, uniform="group1")
        
        self.AnimationEditor = AnimationEditor(self, editorFrame)
        
        self.liveEditing = False
        self.lockInPlace = False
        self.fullanimEditing = False
        self.frameByFrameEditing = False
        self.loadedAnimation = False
        self.importedCurrentAnim = False
        self.TekkenGame = None
        self.LiveEditor = LiveEditor(self)
        
        self.buildMenu()
        
    def buildMenu(self):
        cameraActionsMenu = [
            ("Lock-Camera", self.LiveEditor.lockCamera),
            ("Unlock-Camera", self.LiveEditor.unlockCamera),
            ("Save Camera pos", self.saveCamera),
            ("Reload presets", self.buildMenu),
            ("", "separator"),
        ]
        
        frameActionMenu = [
            ("Add (current position)", self.addFrame),
            ("Remove (current position)", self.removeFrame),
        ]
        
        self.cameraPresets = self.getPresetList()
        for i, p in enumerate(self.cameraPresets):
            name = "Position %d" % (i + 1) if p['name'] == '' else p['name']
            cameraActionsMenu.append((name, lambda self=self,i=i: self.LiveEditor.setCameraPos(i) ))
        
        menuActions = [
            ("Guide", self.showGuide),
            ("Extractable anims", self.showExtractable),
            #("Frame", frameActionMenu),
            ("Camera tools", cameraActionsMenu)
        ]
        
        menu = createMenu(self.window, menuActions)
        self.window.config(menu=menu)
        
    def removeFrame(self):
        self.buildMenu()
        if not self.AnimationEditor.Animation: return
        pass
        
    def addFrame(self):
        if not self.AnimationEditor.Animation: return
        pass
        
    def getPresetList(self):
        presetList = []
        
        with open(dataPath + "cameraPresets.txt", "r") as f:
            for line in f:
                try:
                    line = line.split("#")[0].strip()
                    if len(line) == 0: continue
                    fields = line.split(",")
                    presetList.append({
                        'name': fields[0],
                        'fov': float(fields[1]),
                        'rotx': float(fields[2]),
                        'roty': float(fields[3]),
                        'tilt': float(fields[4]),
                        'x': float(fields[5]),
                        'y': float(fields[6]),
                        'z': float(fields[7]),
                        'relative': int(fields[8]) if len(fields) >= 9 else 0
                    })
                except Exception as e:
                    print("Error parsing a line in cameraPresets.txt")
                    continue
        
        return presetList
        
    def saveCamera(self):
        data = self.LiveEditor.getCameraPos()
        playerPos = self.LiveEditor.getPlayerPos()
        playerRot = self.LiveEditor.getPlayerRot()
        
        cam = data.copy()
        cam['relative'] = 2
        
        if cam['relative'] == 1:
            cam['z'] -= playerPos['z'] #Relative player height
        elif cam['relative'] == 2:
            diffx = cam['x'] - playerPos['x']
            diffy = cam['y'] - playerPos['y']
            
            fullAngle = (math.pi * 2)
            playerAngle = playerRot * (fullAngle / 65535)
            
            distance = math.sqrt(diffx **2 + diffy ** 2)
            angle = math.atan2(diffx, diffy)
            
            finalAngle = (angle - playerAngle)
            
            newy = (distance) * math.cos(finalAngle)
            newx = (distance) * math.sin(finalAngle)
            
            cam['rotx'] = (cam['rotx'] + (playerRot * (360/ 65535))) % 360
            cam['x'] = newx
            cam['y'] = newy
            cam['z'] -= playerPos['z'] #Relative player height
        
        for k in cam:
            if isinstance(cam[k], float):
                cam[k] = ("%01.3f" % cam[k]).rstrip('0').rstrip('.')
                if float(cam[k]) == 0 and cam[k][0] == '-': cam[k] = cam[k][1:]
                
        presetName = ''
        
        while len(presetName) == 0:
            presetName = simpledialog.askstring("Preset name", "What will be the preset name?", parent=self.window, initialvalue = ('New Preset %d' % (len(self.cameraPresets) + 1)))
            if presetName == None: return
        
        with open(dataPath + "cameraPresets.txt", "a") as f:
            f.write("\n" + presetName + ', ' + ', '.join([str(cam[k]) for k in cam]))
        self.buildMenu()
            
        
    def showExtractable(self):
        moveList = "Asuka's ff3, DB1, 2 (last hit)\nAnna's RA (once it connects)\nBob/King/AK/Julia's Idle\nLike half of Negan's moveset"
        messagebox.showinfo("Guide", moveList,  parent=self.window)

    def showGuide(self):
        with open(dataPath + "guide.txt", "r") as f:
            messagebox.showinfo("Guide", f.read(),  parent=self.window)
        
    def LoadAnimation(self, filename):
        self.AnimationEditor.LoadAnimation(filename)
        if self.liveEditing: self.LoadLiveAnimation()
        
    def LoadLiveAnimation(self):
        if not self.AnimationEditor.Animation: return
        self.LiveEditor.loadAnimInMemory(self.AnimationEditor.Animation)
        if self.frameByFrameEditing: self.LiveEditor.writeSingleFrameBytes(self.AnimationEditor.currentFrame)
        elif self.lockInPlace: self.LiveEditor.writeLockInPlaceBytes()
        
    def ToggleLockInPlace(self):
        self.lockInPlace = not self.lockInPlace
        if not self.LiveEditor.CheckRunning(): return
        
        if self.lockInPlace:
            if self.frameByFrameEditing:
                self.LiveEditor.writeLockInPlaceBytes(singleFrame=True)
            else:
                self.LiveEditor.writeLockInPlaceBytes()
        else:
            if self.frameByFrameEditing:
                self.LiveEditor.resetLockInPlaceBytes(singleFrame=True)
            else:
                self.LiveEditor.resetLockInPlaceBytes()
        
    def onAnimationExtraction(self):
        self.AnimationSelector.updateItemlist()
        
    def onFrameChange(self, newFrame):
        if not self.frameByFrameEditing: return
        self.LiveEditor.writeSingleFrameBytes(newFrame)
        
    def onFieldChange(self, frame, fieldId, value):
        if not self.liveEditing or not self.LiveEditor.CheckRunning():
            return
        if self.lockInPlace and (fieldId * 4) in Animation.movementOffsets:
            return
        
        if self.fullanimEditing:
            offset = self.AnimationEditor.Animation.getFieldOffset(frame, fieldId)
            self.LiveEditor.writeFloat(self.LiveEditor.lastAllocation + offset, float(value))
        elif self.frameByFrameEditing:
            offset = self.AnimationEditor.Animation.getFieldOffset(0, fieldId)
            self.LiveEditor.writeFloat(self.LiveEditor.lastAllocation + offset, float(value))
        
    def ExtractCurrentAnimation(self):
        self.LiveEditor.ExtractCurrentAnimation()
        
    def EnableLiveEditing(self):
        if self.LiveEditor.lastAllocation == None:
            self.LoadLiveAnimation() #Load live animation the first time we start this up
        else:
            self.LiveEditor.startIfNeeded()
        self.liveEditing = True
        
    def ToggleFrameByFrame(self):
        if self.frameByFrameEditing:
            self.frameByFrameEditing = False
            self.liveEditing = False
            self.LiveEditor.stop()
        else: #enable
            if self.fullanimEditing: self.LiveEditor.writeSingleFrameBytes(self.AnimationEditor.currentFrame)
            self.fullanimEditing = False
            self.frameByFrameEditing = True
            self.EnableLiveEditing()
        self.AnimationSelector.SetLiveEditingButtonText()
        
    def ToggleLiveEditing(self):
        if self.fullanimEditing:
            self.fullanimEditing = False
            self.liveEditing = False
            self.LiveEditor.stop()
        else: #enable
            if self.frameByFrameEditing == True: self.LiveEditor.writeLoadedAnimBytes()
            self.frameByFrameEditing = False
            self.fullanimEditing = True
            self.EnableLiveEditing()
        self.AnimationSelector.SetLiveEditingButtonText()
            
    def setTitle(self, label = ""):
        title = "TekkenAnimationEditor %s" % (editorVersion)
        if label != "":
            title += " - " + label
        self.window.wm_title(title) 
        

if __name__ == "__main__":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('kilo.TekkenAnimationEditor')
    app = GUI_TekkenAnimationEditor()
    app.window.mainloop()

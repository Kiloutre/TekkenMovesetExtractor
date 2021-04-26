# Python 3.6.5

from tkinter import Tk, Frame, Listbox, Label, Scrollbar, StringVar, Toplevel, Menu, messagebox, Text, simpledialog, Button
from tkinter.ttk import Entry, Style
from Addresses import game_addresses, GameClass, VirtualAllocEx, VirtualFreeEx, MEM_RESERVE, MEM_COMMIT, PAGE_EXECUTE_READWRITE, VirtualFreeEx, MEM_DECOMMIT, MEM_RELEASE
import os
import re
import struct
import ctypes
import math
import pyperclip

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
        'framelistEven': "#555",
        'framelistOdd': "#666",
        'framelistHighlight': "#6f755a",
        'framelistHighlightText': "white",
        'framelistLabelEven': "#333",
        'framelistLabelOdd': "#444",
        'framelistLabelText': "#aaa",
        'framelistMarked1': "#7e3eb0", #Linear
        'framelistMarked2': "#4b9636", #Ease-in
        'framelistMarked3': "#ab2929", #Ease-out
        'framelistMarked4': "#ba9234", #Ease-in-out
        'framelistInBetweenEven': "#5880bf",
        'framelistInBetweenOdd': "#506b96"
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
    12: 'Spine 1 X',
    13: 'Spine 1 Y',
    14: 'Spine 1 Z',
    15: 'Hip X',
    16: 'Hip Y',
    17: 'Hip Z',
    18: 'Spine 2',
    19: 'Field 20',
    20: 'Field 21',
    21: 'Neck 22',
    22: 'Neck 23',
    23: 'Neck 24',
    24: 'Neck 25',
    25: 'Neck 26',
    26: 'Neck 27',
    27: 'Right Inner Shoulder X',
    28: 'Right Inner Shoulder Y',
    29: 'Right Inner Shoulder Z',
    30: 'Right Outer Shoulder X',
    31: 'Right Outer Shoulder Y',
    32: 'Right Arm X',
    33: 'Right Elbow X',
    34: 'Right Elbow Y',
    35: 'Right Elbow Z',
    36: 'Right Hand 3',
    37: 'Right Hand 4',
    38: 'Right Hand 5',
    39: 'Left Inner Shoulder X',
    40: 'Left Inner Shoulder Y',
    41: 'Left Inner Shoulder Z',
    42: 'Left Outer Shoulder X',
    43: 'Left Outer Shoulder Y',
    44: 'Left Arm X',
    45: 'Left Elbow X',
    46: 'Left Elbow Y',
    47: 'Left Elbow Z',
    48: 'Left Hand 3',
    49: 'Left Hand 4',
    50: 'Left Hand 5',
    51: 'Right Upleg',
    52: 'Right Upleg',
    53: 'Right Upleg',
    54: 'Right Foot',
    55: 'Right Upleg',
    56: 'Right Leg',
    57: 'Right Foot',
    58: 'Right Foot',
    59: 'Right Foot',
    60: 'Left Upleg',
    61: 'Left Upleg',
    62: 'Left Upleg',
    63: 'Left Foot',
    64: 'Left Upleg',
    65: 'Left Leg',
    66: 'Left Foot',
    67: 'Left Foot',
    68: 'Left Foot'
}

class Interpolation:
    def getFunction(type1, type2):
        if (type1 == 4 or type1 == 5) and (type2 == 3 or type2 == 5): #left frame is easeOut, right frame is easeIn
            return Interpolation.easeInOut 
        
        if type1 == 3 or type1 == 5: return Interpolation.easeIn
        if type2 == 4 or type2 == 5: return Interpolation.easeOut
        
        return Interpolation.linear
        
    def linear(timefactor):
        return timefactor
        
    def easeIn(timefactor):
        return timefactor * timefactor
        
    def easeOut(timefactor):
        return 1 - math.pow(1 - timefactor, 2)
        
    def easeInOut(timefactor):
        return (2 * timefactor * timefactor) if timefactor < 0.5 else (1 - pow(-2 * timefactor + 2, 2) / 2)
        
    def easeInExpo(timefactor):
        return 0 if timefactor == 0 else math.pow(2, 10 * timefactor - 10)
        
    def easeOutExpo(timefactor):
        return 1 if timefactor == 1 else pow(2, -10 * timefactor)

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
        self.recalculateSize() #Crop or add missing bytes if needed
        
    def recalculateSize(self):
        pastSize = len(self.data)
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
        
    def addFrames(self, count, position=-1, interpolate=False):
        if count <= 0: return
        if position == -1: position = self.length
                 
        self.length += count
        self.writeInt(self.length, 4)
        self.recalculateSize()
        
        for frame in range(self.length - 1, position + count - 1, -1): # Shift values to the right if needed
            for fieldId in range(self.field_count):
                value = self.getField(frame - count, fieldId)
                self.setField(value, frame, fieldId)
        
        if interpolate:
            if position == 0:
                for fieldId in range(self.field_count):
                    value = self.getField(position + count, fieldId)
                    for i in range(count):
                        self.setField(value, position + i, fieldId)
            else:
                self.interpolateBetweenFrames(position - 1, position + count)
    
    def removeFrames(self, count, position=-1):
        if count <= 0 or count >= self.length: return
        if position == -1: position = (self.length - count + 1)
        
        for frame in range(position, self.length - count):
            for fieldId in range(self.field_count):
                value = self.getField(frame + count, fieldId)
                self.setField(value, frame, fieldId)
        
        self.length -= count
        self.writeInt(self.length, 4)
        self.recalculateSize()
        
    def interpolateBetweenFrames(self, frame1, frame2, type1=2, type2=2):     
        diff = frame2 - frame1
        if diff == 1: return
        
        interpolationFunction = Interpolation.getFunction(type1, type2)
        
        for fieldId in range(self.field_count):
            value1 = self.getField(frame1, fieldId)
            value2 = self.getField(frame2, fieldId)
            for i in range(1, diff):
                valueDiff = value2 - value1
                newValue = value1 +  (valueDiff * interpolationFunction(i / diff))
                self.setField(newValue, frame1 + i, fieldId)
        
class AnimationSelector:
    def __init__(self, root, rootFrame):
        self.root = root
        mainFrame = Frame(rootFrame)
        mainFrame.pack(side='left', fill='y')
        
        listFrame = Frame(mainFrame)
        listFrame.pack(fill='both', expand=1)
        
        animlist = Listbox(listFrame, bg=getColor('ListBGColor'))
        animlist.bind('<<ListboxSelect>>', self.onSelectionChange)
        animlist.pack(side='left', fill='both', expand=1)
        
        vertscrollbar = Scrollbar(listFrame, command=animlist.yview)
        vertscrollbar.pack(side='right', fill='y')
        
        horiscrollbar = Scrollbar(mainFrame, command=animlist.xview, orient='horizontal')
        horiscrollbar.pack(fill='x')
        
        animlist.config(yscrollcommand=vertscrollbar.set)
        animlist.config(xscrollcommand=horiscrollbar.set)
        
        buttons = [
            ("Load selected to editor", self.LoadAnimationToEditor),
            ("Extract game animation", self.root.ExtractCurrentAnimation),
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
       
    def hide(self):
        self.frame.pack_forget()
       
    def show(self):
        self.frame.pack(side='left', fill='y')
        
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
            for anim in animationList: self.animlist.insert('end', anim[:-4])
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
        
        content = Frame(container, bg=getColor('BG'))
        content.pack(side='top', fill='both', expand=True)
        
        label = Label(container, bg=getColor('labelBgColor'), fg=getColor('labelTextColor'))
        label.pack(side='top', fill='x')
        
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
        
        if enable: self.enable()
        else: self.disable()
        
    def onchange(self):
        if not self.editingEnabled: return
        value = self.sv.get()
        self.root.onFieldChange(self.fieldId, value)
        
    def setTitle(self, text):
        self.label['text'] = text
        
    def enable(self):
        self.fieldInput.config(state='enabled')
        self.editingEnabled = True
    
    def disable(self):
        self.fieldInput.config(state='disabled')
        self.editingEnabled = False
        
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
        self.Animation = None
        self.keyframes = []
        self.keyframesTypes = {}
        
        self.fields = []
        
        for i in range(9):
            fieldContainer = Frame(self.container, bg=getColor('BG'))
            fieldContainer.pack(side='top', fill='both', pady=4)
            
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
        
        self.framelist = []
        self.framelistLabels = []
        self.framelistLength = 43
        
        framelistContainer = Frame(self.container, bg=getColor('labelBgColor'))
        framelistContainer.pack(side='top', fill='x')
        
        framelistLabelContainer = Frame(self.container, bg=getColor('labelBgColor'))
        framelistLabelContainer.pack(side='top', fill='x')
        
        for i in range(self.framelistLength):
            newLabel = Label(framelistContainer)
            newLabel.bind("<Button-1>", lambda event, self=self, i=i: self.onLabelClick(i))
            newLabel.pack(side='left')
            self.framelist.append(newLabel) #empty cube
            
            newLabel = Label(framelistLabelContainer)
            newLabel.bind("<Button-1>", lambda event, self=self, i=i: self.onLabelClick(i))
            newLabel.pack(side='left')
            self.framelistLabels.append(newLabel) #Text
            
        
        t = Frame(self.container, bg=getColor('labelBgColor'))
        t.pack(side='top', fill='x')
        
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
        
        self.reset()
        
    def getKeyframeType(self, frame):
        keyframeLen = len(self.keyframes)
        for i, f in enumerate(self.keyframes):
            if frame < f: return 0 #Regular frame
            if frame == f: return self.keyframesTypes[frame] # Type 2 or higher: marked frame
            if frame > f and (i + 1 != keyframeLen) and frame < self.keyframes[i + 1]: return 1 # In-between
        return 0
        
    def reinterpolateEverything(self):
        for i in range(len(self.keyframes) - 1):
            self.interpolateBetweenFrames(self.keyframes[i], self.keyframes[i + 1])
        
    def interpolateBetweenFrames(self, frame1, frame2):
        self.Animation.interpolateBetweenFrames(frame1, frame2, self.keyframesTypes[frame1], self.keyframesTypes[frame2])
        
    def interpolateMarkedFrame(self, frame):
        interpolated = False
        keyframeIndex = self.keyframes.index(frame)
        
        if keyframeIndex > 0:
            self.interpolateBetweenFrames(self.keyframes[keyframeIndex - 1], frame) #interpolate in
            interpolated = True
            
        if keyframeIndex < (len(self.keyframes) - 1):
            self.interpolateBetweenFrames(frame, self.keyframes[keyframeIndex + 1]) #interpolate in
            interpolated = True
            
        return interpolated
        
    def unmarkKeyframe(self):
        if not self.currentFrame in self.keyframes: return False
        interpolated = False
        
        keyframeIndex = self.keyframes.index(self.currentFrame)
        self.keyframes.pop(keyframeIndex)
        
        if keyframeIndex < (len(self.keyframes)):
            self.interpolateBetweenFrames(self.keyframes[keyframeIndex - 1], self.keyframes[keyframeIndex]) #interpolate out
            interpolated = True
        
        self.setFrame(self.currentFrame)
        self.updateFramelist()
        return interpolated
        
    def markKeyframe(self, type=2):
        if self.currentFrame in self.keyframes and self.keyframesTypes[self.currentFrame] == type: return False
        
        if self.currentFrame not in self.keyframes:
            self.keyframes.append(self.currentFrame)
            self.keyframes.sort()
        self.keyframesTypes[self.currentFrame] = type
        
        self.setFrame(self.currentFrame)
        self.updateFramelist()
        return self.interpolateMarkedFrame(self.currentFrame)
        
    def addFrames(self, count):
        self.Animation.addFrames(count, position=self.currentFrame, interpolate=True)
        
        if len(self.keyframes) >= 1:
            #Shift keyframes up
            oldDict = self.keyframesTypes.copy()
            self.keyframesTypes = {}
            for i, k in enumerate(self.keyframes):
                if k >= self.currentFrame:
                    self.keyframes[i] += count
                    self.keyframesTypes[k + count] = oldDict[k]
                else:
                    self.keyframesTypes[k] = oldDict[k]
            
            #Re-interpolate keyframes that were affected by the shifting
            keyframeLen = len(self.keyframes)
            for i, k in enumerate(self.keyframes):
                if (i + 1) < keyframeLen and self.keyframes[i + 1] >= self.currentFrame:
                    self.interpolateBetweenFrames(k, self.keyframes[i + 1])
                else: break
        
        self.setTitleInfo()
        self.setFrame(self.currentFrame)
        
    def removeFrames(self, count):
        for k in self.keyframes:
            #remove keyframes caught in the range
            if self.currentFrame <= k < self.currentFrame + count:
                self.keyframes.pop(self.keyframes.index(k))
            
        self.Animation.removeFrames(count, position=self.currentFrame)
            
        if len(self.keyframes) >= 1:
            oldDict = self.keyframesTypes.copy()
            self.keyframesTypes = {}
            #Shift keyframes down
            for i, k in enumerate(self.keyframes):
                if k >= self.currentFrame:
                    self.keyframes[i] -= count
                    self.keyframesTypes[k - count] = oldDict[k]
                else:
                    self.keyframesTypes[k] = oldDict[k]
                
            keyframeLen = len(self.keyframes)
            for i, k in enumerate(self.keyframes):
                if (i + 1) < keyframeLen and self.keyframes[i + 1] >= self.currentFrame:
                    self.interpolateBetweenFrames(k, self.keyframes[i + 1])
                else: break
        
        if self.currentFrame >= self.Animation.length:
            self.currentFrame = self.Animation.length - 1
        
        self.setTitleInfo()
        self.setFrame(self.currentFrame)
        
    def updateFramelist(self):
        framelistOffset = self.getFramelistOffset()
        animLength = self.framelistLength if not self.Animation else self.Animation.length
        
        for i in range(self.framelistLength):
            frame = i + framelistOffset
            labelText = "%03d" % (frame + 1)
           
            self.framelist[i]['text'] = labelText
            self.framelistLabels[i]['text'] = labelText
            
            if frame >= animLength:
                self.framelist[i]['fg'] = getColor('BG')
                self.framelist[i]['bg'] = getColor('BG')
                self.framelistLabels[i]['fg'] = getColor('BG')
                self.framelistLabels[i]['bg'] = getColor('BG')
            else:
                
                
                keyframeType = self.getKeyframeType(frame)
                
                if keyframeType >= 2: #Marked
                    self.framelist[i]['bg'] = getColor('framelistMarked' + str(keyframeType - 1))
                elif keyframeType == 1: #In-between
                    self.framelist[i]['bg'] = getColor('framelistInBetweenEven' if i & 1 == 0 else 'framelistInBetweenOdd')
                else:
                    self.framelist[i]['bg'] = getColor('framelistEven' if i & 1 == 0 else 'framelistOdd')
                    
                self.framelist[i]['fg'] = self.framelist[i]['bg']
                    
                if self.Animation and frame == self.currentFrame:
                    self.framelistLabels[i]['fg'] = getColor('framelistHighlightText')
                    self.framelistLabels[i]['bg'] = getColor('framelistHighlight')
                else:
                    self.framelistLabels[i]['fg'] = getColor('framelistLabelText')
                    self.framelistLabels[i]['bg'] = getColor('framelistLabelEven' if frame & 1 == 0 else 'framelistLabelOdd')
            
        
    def getFramelistOffset(self):
        if not self.Animation: return 0
        if self.Animation.length <= self.framelistLength: return 0
        
        middleFrame = int(self.framelistLength / 2)
        
        if self.currentFrame - middleFrame >= 0: # clear in-between opportunity
            return self.currentFrame - middleFrame
            
        return 0
        
    def onLabelClick(self, labelId):
        if self.Animation == None: return
        self.setFrame(labelId + self.getFramelistOffset())
        
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
            if self.getKeyframeType(self.currentFrame) == 0: #Regular frame, is cool
                self.root.onFieldChange(self.currentFrame, actualFieldId, value)
            else: #Marked frame
                self.interpolateMarkedFrame(self.currentFrame)
                self.root.onMarkedFieldChange()
        
    def setField(self, newField):
        if self.Animation == None or newField > (self.Animation.field_count - self.fieldCount) or newField < 0: return
        self.currentField = newField
        fieldLabel = "Field %d - %d /%d" % (newField + 1, newField + self.fieldCount, self.Animation.field_count)
        self.currFieldLabel['text'] = fieldLabel
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
                
                enabled = self.getKeyframeType(self.currentFrame) != 1 #notAnInbetween
                self.fields[i].setValue(value, enable=enabled)
                self.fields[i].setTitle(fieldLabels.get(actualFieldId, "Field %d" % (actualFieldId + 1)))
            else:
                self.fields[i].resetForm()
                
        self.updateFramelist()
        
    def setTitleInfo(self):
        info = "  |  Length: %d frames  |  Bone per frame: %d  |  Size: %d bytes (%d KB)" % (self.Animation.length, self.Animation.field_count, self.Animation.size, self.Animation.size / 1000)
        self.setTitle("Editing: " + self.animationName + info)
        
    def LoadAnimation(self, filename):
        self.reset()
        self.Animation = Animation(dataPath + filename)
        
        if self.Animation.type != 0xC8:
            self.setTitle("Cannot load " + filename + ", animation format is not supposed")
            return False
        
        self.animationName = filename
        self.setTitleInfo()
        self.setFrame(0)
        fieldLabel = "Field 1 - %d /%d" % (self.fieldCount, self.Animation.field_count)
        self.currFieldLabel['text'] = fieldLabel
        return True
        
    def reset(self):
        self.keyframes = []
        self.keyframesTypes = {}
        self.Animation = None
        self.animationName = None
        self.currentFrame = 0
        self.currentField = 0
        self.currFrameLabel['text'] = 'Frame 0/0'
        self.currFieldLabel['text'] = 'Field 1 - %d /0' % (self.fieldCount)
        self.updateFramelist()
        
class LiveEditor:
    def __init__(self, root):
        self.root = root
        self.stop()
        self.setPlayerAddress(0)
       
    def setPlayerAddress(self, playerId):
        self.playerAddress = game_addresses.addr['t7_p1_addr'] + (playerId * game_addresses.addr['t7_playerstruct_size'])
        
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
        self.allocations = []
        
    def allocateMem(self, allocSize):
        return VirtualAllocEx(self.T.handle, 0, allocSize, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)
        
    def freeMem(self, addr):
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
            if self.root.lockInPlace:
                self.writeLockInPlaceBytes()
        else:
            self.writeSingleFrameBytes(self.root.AnimationEditor.currentFrame)
        
    def registerAllocation(self, addr, target):
        self.allocations.append((addr, target))
        
    def freePastAllocations(self):
        i = 0
        while i < len(self.allocations):
            addr, target = self.allocations[i]
            try:
                if not self.T.readInt(target, 8) == addr:
                    raise
                i += 1
            except:
                self.freeMem(addr)
                self.allocations.pop(i)
        
    def loadAnimInMemory(self, anim):
        if not self.startIfNeeded(): return None
        self.Animation = anim
        currmoveAddr = self.T.readInt(self.playerAddress + 0x220, 8)
        
        animationAddr = self.allocateMem(anim.size)
        
        self.lastAllocation = animationAddr
        self.lastAllocationSize = anim.size
        
        self.writeLoadedAnimBytes()
        self.T.writeInt(currmoveAddr + 0x10, animationAddr, 8)
        self.T.writeInt(currmoveAddr + 0x68, anim.length, 4)
        
        self.freePastAllocations()
        self.registerAllocation(animationAddr, currmoveAddr + 0x10)
        
        return animationAddr
        
    def resetLockInPlaceBytes(self, singleFrame = False):
        if self.lastAllocation == None: return
        length = self.Animation.length if singleFrame == False else 1
        
        baseOffset = self.lastAllocation + self.Animation.offset
        baseLocalOffset = self.Animation.offset
        
        for i in range(length):
            
            for offset in Animation.movementOffsets:
                self.T.writeBytes(baseOffset + offset, bytes(self.Animation.data[baseLocalOffset + offset:baseLocalOffset + offset + 4]))
                
            baseOffset += self.Animation.frame_size
            baseLocalOffset += self.Animation.frame_size
        
    def writeLockInPlaceBytes(self, singleFrame = False):
        if self.lastAllocation == None: return
        length = self.Animation.length if singleFrame == False else 1
        
        baseOffset = self.lastAllocation + self.Animation.offset
        for i in range(length):
            
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
        else: #absolute
            self.writeFloat(camAddr + 0x408, cam['rotx']) #rotx
            self.writeFloat(camAddr + 0x3F8, cam['x']) #x
            self.writeFloat(camAddr + 0x3FC, cam['y']) #y
            self.writeFloat(camAddr + 0x400, cam['z']) #z
            
    def getCameraPos(self):
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
        
    def forceMoveLoop(self):
        if not self.CheckRunning(): return False
        currmoveAddr = self.T.readInt(self.playerAddress + 0x220, 8)
        cancelAddr = self.T.readInt(currmoveAddr + 0x20)
        
        while self.T.readInt(cancelAddr, 8) != 0x8000:
            cancelAddr += 0x28
            
        currmoveId = self.T.readInt(self.playerAddress + 0x350, 4)
        self.T.writeInt(currmoveAddr + 0x54, currmoveId, 2)
        self.T.writeInt(cancelAddr + 0x18, self.Animation.length, 4) #frame window start
        self.T.writeInt(cancelAddr + 0x1c, 32769, 4) #frame window end
        self.T.writeInt(cancelAddr + 0x20, self.Animation.length, 4) #starting frame
        self.T.writeInt(cancelAddr + 0x24, currmoveId, 2) #write current move id to cancel move id
        
class GUI_TekkenAnimationEditor():
    def __init__(self, mainWindow=True):
        window = Tk() if mainWindow else Toplevel()
        self.window = window

        boldButtonStyle = Style()
        boldButtonStyle.configure("Bold.TButton", font = ('Sans','10','bold'))
        
        self.setTitle()
        window.iconbitmap('InterfaceData/komari.ico')
        window.geometry("1163x539")
        self.setWindowSize(1163, 539)
        
        self.AnimationSelector = AnimationSelector(self, window) #Side menu
        self.AnimationSelector.updateItemlist()
        
        editorFrame = Frame(window, bg=getColor('BG')) #Main frale
        editorFrame.pack(side='left', fill='both', expand=1)
        editorFrame.grid_columnconfigure(0, weight=1, uniform="group1")
        editorFrame.grid_rowconfigure(0, weight=1, uniform="group1")
        
        self.AnimationEditor = AnimationEditor(self, editorFrame)
        
        self.editorFrame = editorFrame
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
            ("Save Camera pos (absolute)", lambda self=self:self.saveCamera(0)),
            ("Reload presets", self.buildMenu),
            ("", "separator"),
        ]
        
        frameActionMenu = [
            ("Add (at current position)", self.addMultipleFrames),
            ("Remove (from current position)", self.removeMultipleFrames),
            ("", "separator"),
            ("Mark keyframe (linear)", self.markKeyframe),
            ("Mark keyframe (ease in)", lambda self=self: self.markKeyframe(3)),
            ("Mark keyframe (ease out)", lambda self=self: self.markKeyframe(4)),
            ("Mark keyframe (ease in-out)", lambda self=self: self.markKeyframe(5)),
            ("Unmark keyframe", self.AnimationEditor.unmarkKeyframe),
        ]
        
        self.cameraPresets = self.getPresetList()
        for i, p in enumerate(self.cameraPresets):
            name = "Position %d" % (i + 1) if p['name'] == '' else p['name']
            cameraActionsMenu.append((name, lambda self=self,i=i: self.LiveEditor.setCameraPos(i) ))
        
        otherToolsMenu = [
            ("Set target as 1P", lambda self=self:self.LiveEditor.setPlayerAddress(0)),
            ("Set target as 2P", lambda self=self:self.LiveEditor.setPlayerAddress(1)),
            ("", "separator"),
            ("Copy frame to clipboard", self.copyFrameToClipboard),
            ("Paste frame data from clipboard", self.pasteFrameFromClipboard),
            ("", "separator"),
            ("Copy keyframe list to clipboard", self.copyKeyframesToClipboard),
            ("Paste keyframe list from clipboard", self.pasteKeyframesFromClipboard),
            #("", "separator"),
            #("Make current move loop into itself", self.forceCurrmoveLoop),
        ]
        
        menuActions = [
            ("Guide", self.showGuide),
            ("Extractable anims", self.showExtractable),
            ("Frame tools", frameActionMenu),
            ("Camera tools", cameraActionsMenu),
            ("Other tools", otherToolsMenu),
            ("Toggle left-menu display", self.toggleLeftMenuDisplay)
        ]
        
        self.leftMenuDisplay = True
        menu = createMenu(self.window, menuActions)
        self.window.config(menu=menu)
        
    def removeMultipleFrames(self):
        if not self.AnimationEditor.Animation:
            self.message("Error", "You have to load an animation before being able to remove frames")
            return

        frameCount = simpledialog.askinteger("Frame count", "How many frames do you want to remove?", parent=self.window, initialvalue=1)
        if frameCount == None: return
        try:
            frameCount = int(frameCount)
            if frameCount <= 0: raise
        except:
            self.message("Error", "Invalid frame count: not adding")
            return
            
        if self.AnimationEditor.Animation.length - frameCount <= 0:
            self.message("Error", "Error, removing too many frames")
            return
                
        self.AnimationEditor.removeFrames(frameCount)
        if self.liveEditing: self.LoadLiveAnimation() #todo: no need to re-allocate
        
    def addMultipleFrames(self):
        if not self.AnimationEditor.Animation:
            self.message("Error", "You have to load an animation before being able to add frames")
            return
            
        frameCount = simpledialog.askinteger("Frame count", "How many frames do you want to add?", parent=self.window, initialvalue=0)
        if frameCount == None: return
        try:
            frameCount = int(frameCount)
            if frameCount <= 0: raise
        except:
            self.message("Error", "Invalid frame count: not adding")
            return
                
        self.AnimationEditor.addFrames(frameCount)
        if self.liveEditing: self.LoadLiveAnimation() #todo: no need to re-allocate
        
    def setWindowSize(self, width, height):
        self.window.minsize(width, height)
        self.window.maxsize(width, height)
        
    def toggleLeftMenuDisplay(self):
        self.leftMenuDisplay = not self.leftMenuDisplay
        if not self.leftMenuDisplay:
            self.AnimationSelector.hide()
            self.setWindowSize(1026, 539)
        else:
            self.setWindowSize(1163, 539)
            self.hideEditor()
            self.AnimationSelector.show()
            self.showEditor()
        
    def showEditor(self):
        self.editorFrame.pack(side='left', fill='both', expand=1)
        
    def hideEditor(self):
        self.editorFrame.pack_forget()
        
    def copyKeyframesToClipboard(self):
        if not self.AnimationEditor.Animation:
            self.message("Error", "You have to load an animation before being able to copy keyframes")
            return
       
        keyframeList = ["%d;%d" % ((f, self.AnimationEditor.keyframesTypes[f])) for f in self.AnimationEditor.keyframes]
        
        pyperclip.copy(",".join(keyframeList))
        self.message("Copied", "Keyframe list successfuly copied")
        
    def pasteKeyframesFromClipboard(self):
        if not self.AnimationEditor.Animation:
            self.message("Error", "You have to load an animation before being able to paste data")
            return
            
        keyframeData = pyperclip.paste().strip()
        
        try:
            keyframeData = [k for k in keyframeData.split(",")]
            keyframeData = [x.split(";") for x in keyframeData]
            keyframeData = [(int(frame), int(type)) for frame, type in keyframeData]
            self.AnimationEditor.keyframes = []
            self.AnimationEditor.keyframesTypes = {}
            for frame, type in keyframeData:
                if frame >= self.AnimationEditor.Animation.length:
                    self.message("Error", "Keyframe list longer than animation, not pasting entire list.")
                    break
                self.AnimationEditor.keyframes.append(frame)
                self.AnimationEditor.keyframesTypes[frame] = type
            self.AnimationEditor.reinterpolateEverything()
        except Exception as e:
            print(e)
            self.message("Error", "Error pasting keyframe list: invalid data?")
            return
        self.AnimationEditor.setFrame(self.AnimationEditor.currentFrame)
        
    def copyFrameToClipboard(self):
        if not self.AnimationEditor.Animation:
            self.message("Error", "You have to load an animation before being able to copy")
            return
        
        floatList = [self.AnimationEditor.Animation.getField(self.AnimationEditor.currentFrame, f) for f in range(self.AnimationEditor.Animation.field_count)]

        for i in range(len(floatList)):
            floatList[i] = ("%01.3f" % floatList[i]).rstrip('0').rstrip('.')
            if float(floatList[i]) == 0 and floatList[i][0] == '-': floatList[i] = floatList[i][1:]
        
        pyperclip.copy(",".join(floatList))
        self.message("Copied", "Frame data successfuly copied")
        
    def pasteFrameFromClipboard(self):
        if not self.AnimationEditor.Animation:
            self.message("Error", "You have to load an animation before being able to paste data")
            return
            
        if self.AnimationEditor.getKeyframeType(self.AnimationEditor.currentFrame) == 1:
            self.message("Error", "You cannot paste data into an in-between")
            return
            
        animData = pyperclip.paste().strip()
        try:
            for i, f in enumerate(animData.split(",")):
                self.AnimationEditor.onFieldChange(i, f)
            self.AnimationEditor.setFrame(self.AnimationEditor.currentFrame)
        except Exception as e:
            self.message("Error", "Error pasting animation data: invalid data?")
            return
        
    def unmarkKeyframe():
        interpolated = self.AnimationEditor.unmarkKeyframe()
        if interpolated and self.liveEditing and self.fullanimEditing:
            self.LiveEditor.writeLoadedAnimBytes()
        
    def markKeyframe(self, type=2):
        interpolated = self.AnimationEditor.markKeyframe(type)
        if interpolated and self.liveEditing and self.fullanimEditing:
            self.LiveEditor.writeLoadedAnimBytes()
        
    def message(self, title, message):
        messagebox.showinfo(title, message, parent=self.window)
        
    def forceCurrmoveLoop(self):
        if not self.AnimationEditor.Animation or not self.LiveEditor.lastAllocation or not self.LiveEditor.CheckRunning(): 
            self.message("Error", "Load an animation in-game before clicking this button")
            return
        self.LiveEditor.forceMoveLoop()
        
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
        
    def saveCamera(self, relative=2):
        if not self.LiveEditor.startIfNeeded():
            self.message("Error", "Could not open process")
            return
            
        data = self.LiveEditor.getCameraPos()
        playerPos = self.LiveEditor.getPlayerPos()
        playerRot = self.LiveEditor.getPlayerRot()
        
        cam = data.copy()
        cam['relative'] = relative
        
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
        moveList = "Asuka's ff3, DB1, 2 (last hit)\nAnna's RA (once it connects)\nBob/King/AK/Julia's Idle\nLike half of Negan's moveset\nAnd more, but this should get you started easily..."
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
        
    def onMarkedFieldChange(self):
        if self.LiveEditor.CheckRunning():
            self.LiveEditor.writeLoadedAnimBytes(singleFrameOfData=self.frameByFrameEditing)
        
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

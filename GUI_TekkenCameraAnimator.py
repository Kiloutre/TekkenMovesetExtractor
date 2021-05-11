# Python 3.6.5

from tkinter import Tk, Frame, Listbox, Label, Scrollbar, StringVar, Toplevel, Menu, messagebox, Text, simpledialog, Button, Checkbutton, Canvas
from tkinter.ttk import Entry, Style, OptionMenu
from Addresses import game_addresses, GameClass, VirtualAllocEx, VirtualFreeEx, MEM_RESERVE, MEM_COMMIT, PAGE_EXECUTE_READWRITE, MEM_DECOMMIT, MEM_RELEASE
from time import sleep
import threading
import os
import re
import struct
import ctypes
import math
import pyperclip
from scipy import interpolate

dataPath = "./CameraAnimations/"
dataPath2 = "./InterfaceData/"
editorVersion = "1.1"
degToRad = (math.pi * 2) / 360
        
colors = {
    'dark': {
        'BG': '#222',
        'lighterBG': '#333',
        'labelBgColor': '#333',
        'listItemEvenBG': "#555",
        'listItemOddBG': "#666",
        'listItemText': "white",
        'listUnimportantItemText': "#c9c9c9",
        'ListBGColor': "#222",
        'buttonBGColor': "#666",
        'buttonTextColor': "#ddd",
        'buttonDisabledBG': "#4a4a4a",
        'labelTextColor': "#ddd",
        'listSelectedItemBG': '#324563',
        'listSelectedItem': '#eb9b7f',
        'groupColor0': '#683870',
        'groupColor1': '#307530',
        'groupColor2': '#2b6a75',
        'groupColor3': '#36248f',
        'groupColor4': '#ab3a8f',
        'groupColor5': '#c42929',
        'groupColor6': '#b88c2e'
    },
    'default': {
        'labelBgColor': '#ddd'
    }
}

frameFields = [
    'name',
    'fov',
    'dof',
    'x',
    'y',
    'z',
    'rotx',
    'roty',
    'tilt'
]

dataFields = [
    'fov',
    'dof',
    'x',
    'y',
    'z',
    'rotx',
    'roty',
    'tilt'
]

fieldTypes = {
    'name': 'text',
    'fov': 'float',
    'dof': 'float',
    'rotx': 'float',
    'roty': 'float',
    'tilt': 'float',
    'x': 'float',
    'y': 'float',
    'z': 'float'
}

fieldLabels = {
    'name': 'Frame name',
    'fov': 'Field of view',
    'dof': 'Depth of Field',
    'rotx': 'Yaw',
    'roty': 'Pitch',
    'tilt': 'Roll',
    'x': 'Position X',
    'y': 'Position Y',
    'z': 'Height'
}

groupKeys = [
    'duration',
    'delay',
    'interpolation',
    'easing',
    'pre_delay_pos',
    'relativity'
]

interpolationTypes = {
    0: "Linear",
    2: "Nearest",
    1: "Bézier Curve",
    3: "Bézier + Spline X/Y",
    5: "Bézier + Spline X/Y/Z",
    4: "Bézier + Circular X/Y",
    #6: "Catmull-Rom",
}
interpolationTypes2 = {interpolationTypes[k]:k for k in interpolationTypes}

relativityTypes = {
    0: "None",
    1: "P1 Pos",
    2: "P1 Pos & Height",
    3: "P1 Pos & Rotation",
    4: "P1 Pos & Height & Rotation",
    5: "P1 Look-At",
    11: "P2 Pos",
    12: "P2 Pos & Height",
    13: "P2 Pos & Rotation",
    14: "P2 Pos & Height & Rotation",
    15: "P2 Look-At"
}
relativityTypes2 = {relativityTypes[k]:k for k in relativityTypes}

easingTypes = {
    0: "Linear",
    1000: "---",
    1: "Ease in",
    2: "Ease in cubic",
    3: "Ease in quart",
    4: "Ease in expo",
    5: "Ease in elastic",
    1001: "---",
    6: "Ease out",
    7: "Ease out cubic",
    8: "Ease out quart",
    9: "Ease out expo",
    10: "Ease out elastic",
    1002: "---",
    11: "Ease in-out",
    12: "Ease in-out cubic",
    13: "Ease in-out quart",
    14: "Ease in-out expo",
    15: "Ease in-out elastic",
}
easingTypes2 = {easingTypes[k]:k for k in easingTypes}

class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.hovered = False
        
    def showtip(self, text):
        self.hovered = True
        sleep(0.3)
        if not self.hovered: return
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify='left',
                      background="#ffffe0", relief='solid', borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        self.hovered = False
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)
    
class Point:
    def __init__(self, x, y = None):
        
        if isinstance(x, Point):
            self.x = x.x
            self.y = x.y
        elif isinstance(x, dict):
            self.x = x['x']
            self.y = x['y']
        elif isinstance(x, float) and isinstance(y, float):
            self.x = x
            self.y = y
        else:
            self.x = 0
            self.y = 0
        
    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        else:
            return Point(self.x + other, self.y + other)
        
    def __sub__(self, other):
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        else:
            return Point(self.x - other, self.y - other)
        
    def __mul__(self, other):
        if isinstance(other, Point):
            return Point(self.x * other.x, self.y * other.y)
        else:
            return Point(self.x * other, self.y * other)
        2
    def __truediv__(self, other):
        if isinstance(other, Point):
            otherX = 1 if other.x == 0 else other.x #Failsafes
            otherY = 1 if other.y == 0 else other.y
            return Point(self.x / otherX, self.y / otherY)
        else:
            if other == 0: return Point(1, 1) #Failsafe
            return Point(self.x / other, self.y / other)
      
    def __str__(self):
        return "Point(%0.3f, %0.3f)," % (self.x, self.y)
      
    def dist(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
    
    def getXY(self):
        return self.x, self.y
    
class Interpolation:
    def getEasing(id):
        return {
            0: Interpolation.linear,
            1: Interpolation.easeIn,
            2: Interpolation.easeInCubic,
            3: Interpolation.easeInQuart,
            4: Interpolation.easeInExpo,
            5: Interpolation.easeInElastic,
            6: Interpolation.easeOut,
            7: Interpolation.easeOutCubic,
            8: Interpolation.easeOutQuart,
            9: Interpolation.easeOutExpo,
            10: Interpolation.easeOutElastic,
            11: Interpolation.easeInOut,
            12: Interpolation.easeInOutCubic,
            13: Interpolation.easeInOutQuart,
            14: Interpolation.easeInOutExpo,
            15: Interpolation.easeInOutElastic,
        }[id]
    
    def getInterpolation(id):
        return {
            0: Interpolation.linearCurveValue,
            1: Interpolation.getBezierCurveValue,
            2: Interpolation.nearestInterpolation,
            3: Interpolation.splineInterpolation,
            5: lambda points, t: Interpolation.splineInterpolation(points, t, withZ=True),
            4: Interpolation.circularInterpolation,
            #6: Interpolation.catmullRom,
        }[id]

    def linear(x):
        return x
        
    def easeIn(x):
        return x * x
        
    def easeOut(x):
        return 1 - math.pow(1 - x, 2)
        
    def easeInOut(x):
        return (2 * x * x) if x < 0.5 else (1 - math.pow(-2 * x + 2, 2) / 2)
        
    def easeInExpo(x):
        return 0 if x == 0 else math.pow(2, 10 * x - 10)
        
    def easeOutExpo(x):
        return (1 if x == 1 else 1 - math.pow(2, -10 * x))
        
    def easeInOutExpo(x):
        if x == 0 or x == 1: return x
        if x < 0.5: return math.pow(2, 20 * x - 10) / 2
        return (2 - math.pow(2, -20 * x + 10)) / 2
        return (1 if x == 1 else 1 - math.pow(2, -10 * x))
        
    def easeInQuart(x):
        return x * x * x * x
        
    def easeOutQuart(x):
        return 1 - math.pow(1 - x, 4)
        
    def easeInOutQuart(x):
        return 8 * x * x * x * x  if x < 0.5 else 1 - math.pow(-2 * x + 2, 4) / 2
        
    def easeInCubic(x):
        return x * x * x
        
    def easeOutCubic(x):
        return 1 - math.pow(1 - x, 3)
        
    def easeInOutCubic(x):
        return   4 * x * x * x  if x < 0.5 else 1 - math.pow(-2 * x + 2, 3) / 2
        
    def easeOutElastic(x):
        c4 = (2 * math.pi) / 3

        if x == 0 or x == 1: return x
        return math.pow(2, -10 * x) * math.sin((x * 10 - 0.75) * c4) + 1
        
    def easeInElastic(x):
        c4 = (2 * math.pi) / 3

        if x == 0 or x == 1: return x
        return -math.pow(2, 10 * x - 10) * math.sin((x * 10 - 10.75) * c4)
        
    def easeInOutElastic(x):
        c5 = (2 * math.pi) / 4.5

        if x == 0 or x == 1: return x
        return (-(math.pow(2, 20 * x - 10) * math.sin((20 * x - 11.125) * c5)) / 2) if x < 0.5 else (math.pow(2, -20 * x + 10) * math.sin((20 * x - 11.125) * c5)) / 2 + 1
    
    def interpolateLine(p0, p1, t):
        return {field:(p0[field] + (p1[field] - p0[field]) * t) for field in dataFields}
    
    def getBezierCurveValue(points, t):
        while len(points) > 1:
            points = [Interpolation.interpolateLine(points[i], points[i + 1], t) for i in range(0, len(points) - 1)]
        return points[0]
        
    def splineInterpolation(points, t, withZ=False):
        bezier = Interpolation.getBezierCurveValue(points, t)
        
        try:
            x = [p['x'] for p in points]
            y = [p['y'] for p in points]
            
            if withZ:
                z = [p['z'] for p in points]
                tck, u = interpolate.splprep([x, y, z], s = 0, per=False)
                xi, yi, zi = interpolate.splev([t], tck)
                bezier['z'] = zi[0]
            else:
                tck, u = interpolate.splprep([x, y], s = 0, per=False)
                xi, yi = interpolate.splev([t], tck)
                
            bezier['x'] = xi[0]
            bezier['y'] = yi[0]
        except:
            pass

        return bezier
        
    def linearCurveValue(points, t):
        pointsLen = len(points)
        idx = (pointsLen - 1) * t
        
        if int(idx + 1) >= pointsLen:
            if pointsLen == 1: return points[pointsLen - 1]
            remainder = (pointsLen - idx - 1) #extrapolate
            return Interpolation.interpolateLine(points[pointsLen - 1], points[pointsLen - 2], remainder)
        elif idx < 0:
            if pointsLen == 1: return points[0]
            return Interpolation.interpolateLine(points[0], points[1], idx) #extrapolate again
        else:
            remainder = (idx % 1) if idx >= 0 else (idx % -1) 
            idx = int(idx)
            return Interpolation.interpolateLine(points[idx], points[idx + 1], remainder)
    
    def lli8(x1, y1, x2, y2, x3, y3, x4, y4):
        nx =  (x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)
        ny = (x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)
        d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        return Point(nx, ny) / d
    
    def getCircleFromThreePoints(a, b, c):
        halfpi = math.pi / 2

        d1 = (b - a)
        d2 = (c - b)

        d1p = Point(d1.x * math.cos(halfpi) - d1.y * math.sin(halfpi),
                d1.x * math.sin(halfpi) + d1.y * math.cos(halfpi))
        d2p = Point(d2.x * math.cos(halfpi) - d2.y * math.sin(halfpi),
                d2.x * math.sin(halfpi) + d2.y * math.cos(halfpi))
                
        m1 = (a + b)/2
        m2 = (b + c)/2

        m1n = m1 + d1p
        m2n = m2 + d2p
        
        center = Interpolation.lli8(m1.x, m1.y, m1n.x, m1n.y, m2.x, m2.y, m2n.x, m2n.y)
        size = center.dist(a)
            
        startAngle = math.atan2(*(a - center).getXY())
        midAngle = math.atan2(*(b - center).getXY())
        endAngle = math.atan2(*(c - center).getXY())
        
        return center, size, startAngle, midAngle, endAngle
    
    def circularInterpolation(points, t):
        pointsLen = len(points)
        idx = (pointsLen - 1) * t
        remainder = idx % 1
        idx = int(idx)
        
        if (idx + 2 < pointsLen) and (idx >= 0):
            a = Point(points[idx])
            b = Point(points[idx+1])
            c = Point(points[idx+2])
            circle, size, s, e, e2 = Interpolation.getCircleFromThreePoints(a, b, c)
        elif (idx + 1 < pointsLen) and (idx > 0):
            a = Point(points[idx - 1])
            b = Point(points[idx + 0])
            c = Point(points[idx + 1])
            circle, size, s, e, e2 = Interpolation.getCircleFromThreePoints(a, b, c)
            s, e = e, e2
        else:
            return points[-1] #Todo: extrapolate properly
        
        diff = ((e - s) + math.pi) % (math.pi * 2) - math.pi
        diff = diff * remainder
        
        y = math.cos(s + diff) * size
        x = math.sin(s + diff) * size
        
        resPoint = Interpolation.getBezierCurveValue(points, t)
        resPoint['x'] = x + circle.x
        resPoint['y'] = y + circle.y
        return resPoint
    
    def nearestInterpolation(points, t):
        pointsLen = len(points)
        idx = pointsLen * t
        remainder = idx % 1
        return points[int(idx + 1 if ((idx % 1) >= 0.5 and idx + 1 < pointsLen) else idx)]
        
class Animation:
    def __init__(self, filename):
        self.filename = filename
        self.name = filename[:-4]
        self.groups = []
        self.cachedGroups = []
        
        with open(dataPath + filename, "r") as f:
            group = None
            for line in f:
                line = line.strip()
                if len(line) == 0 or line.startswith("#"): continue
                if re.match("^\[([^,=]+)\]$", line):
                    group = {
                        'name': line[1:-1],
                        'duration': 0,
                        'delay': 0,
                        'interpolation': 0,
                        'easing': 0,
                        'pre_delay_pos': 0,
                        'relativity': 0,
                        'length': 0,
                        'frames': []
                    }
                    self.groups.append(group)
                    self.cachedGroups.append(None)
                elif re.match("^\[(([a-z\_]+=[0-9]+)+, ?)*([a-z\_]+=[0-9]+)\]$", line):
                    for pair in line[1:-1].split(","):
                        key, value = [k.strip() for k in pair.split("=")]
                        if key in groupKeys: group[key] = int(value)
                elif re.match("^\[.*,( ?[0-9]+,)* ?[0-9]+\]$", line):
                    groupData = line[1:-1].split(",")
                    groupDataLen = len(groupData)
                    group = {
                        'name': groupData[0],
                        'duration': int(groupData[1]) if groupDataLen > 1 else 0,
                        'delay': int(groupData[2]) if groupDataLen > 2 else 0,
                        'interpolation': int(groupData[3]) if groupDataLen > 3 else 0,
                        'easing': int(groupData[4]) if groupDataLen > 4 else 0,
                        'pre_delay_pos': int(groupData[5]) if groupDataLen > 5 else 0,
                        'relativity': int(groupData[6]) if groupDataLen > 6 else 0,
                        'length': 0,
                        'frames': []
                    }
                    self.groups.append(group)
                    self.cachedGroups.append(None)
                else:
                    line = line.split(',')
                    group['frames'].append({field:getValueFromType(fieldTypes[field], line[i]) for i, field in enumerate(frameFields)})
                    group['length'] += 1
        
    def calculateCachedFrames(self, startingGroup=0, singleGroup=False):
        end = startingGroup + 1 if singleGroup else len(self.groups)
        
        for i, group in enumerate(self.groups[startingGroup:end]):
            if self.cachedGroups[startingGroup + i] == None:
                easingFunction = Interpolation.getEasing(group['easing'])
                interpolationFunction = Interpolation.getInterpolation(group['interpolation'])
                if group['length']> 0:
                    frames = [interpolationFunction(group['frames'], easingFunction(idx / (group['duration']))) for idx in range(group['duration'])]
                else:
                    frames = []
                self.cachedGroups[startingGroup + i] = {
                    'frames': frames, 
                    'length': len(frames),
                    'delay': group['delay'],
                    'duration': group['duration'],
                    'pre_delay_pos': group['pre_delay_pos'],
                    'relativity': group['relativity'],
                }
                
        return self.cachedGroups[startingGroup:end]
        
    def getValue(self, group, field, frame):
        return self.groups[group]['frames'][frame][field]
        
    def setValue(self, group, field, frame, value):
        self.groups[group]['frames'][frame][field] = value
        if field != 'name': self.cachedGroups[group] = None
        
    def addGroup(self, groupdata, position):
        self.groups.insert(position, groupdata)
        self.cachedGroups.insert(position, None)
        
    def removeGroup(self, position):
        self.groups.pop(position)
        self.cachedGroups.pop(position)
        
    def addFrame(self, group, framedata, position):
        self.groups[group]['frames'].insert(position, framedata)
        self.groups[group]['length'] += 1
        self.cachedGroups[group] = None
        
    def removeFrame(self, group, position):
        self.groups[group]['frames'].pop(position)
        self.groups[group]['length'] -= 1
        self.cachedGroups[group] = None
        
def getColor(key):
    isDark = True
    return colors['dark' if isDark else 'default'].get(key, '#fff')
    
def getAnimationList():
    if not os.path.isdir(dataPath):
        os.mkdir(dataPath)
        return []
    return [file for file in os.listdir(dataPath) if not os.path.isdir(dataPath + file) and file.endswith(".txt")]
        
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
    
def splitFrame(root, split):
    rowCount = 1 + (split == 'horizontal')
    colCount = 1 + (split == 'vertical')
    
    for i in range(rowCount):
        root.grid_rowconfigure(i, weight=1, uniform='group1' )
    for i in range(colCount):
        root.grid_columnconfigure(i, weight=1, uniform='group1' )
        
    Frame1 = Frame(root, bg=getColor('BG'))
    Frame1.grid(column=0, row=0, sticky='nsew')
    
    col, row = int(split == 'vertical'), int(split == 'horizontal')
    Frame2 = Frame(root, bg=getColor('BG'))
    Frame2.grid(column=col, row=row, sticky='nsew')
    
    return Frame1, Frame2
        
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
        
        #vertscrollbar = Scrollbar(listFrame, command=animlist.yview)
        #vertscrollbar.pack(side='right', fill='y')
        
        #horiscrollbar = Scrollbar(mainFrame, command=animlist.xview, orient='horizontal')
        #horiscrollbar.pack(fill='x')
        
        #animlist.config(yscrollcommand=vertscrollbar.set)
        #animlist.config(xscrollcommand=horiscrollbar.set)
        
        buttons = [
            ("Load selected", self.LoadAnimationToEditor),
            ("Create animation", self.CreateFile),
            #("Reload list", lambda self=self: self.UpdateItemlist(reloadOnly=True)),
            ("Reset camera", self.root.ResetCamera),
        ]
        
        for label, callback in buttons:
            newButton = Button(mainFrame, text=label, command=callback, bg=getColor('buttonBGColor'), fg=getColor('buttonTextColor'))
            newButton.pack(fill='x')
            
        self.saveButton = Button(mainFrame, text='Save file', command=self.root.SaveFile, bg=getColor('buttonBGColor'), fg=getColor('buttonTextColor'))
        self.saveButton.pack(fill='x')
        
        self.animlist = animlist
        self.frame = mainFrame
        
        self.itemList = []
        self.selectionIndex = -1
        self.selection = None
        self.setSaveButtonEnabled(False)
        
    def setSaveButtonEnabled(self, enabled):
        if enabled:
            self.saveButton.configure(state="normal")
            self.saveButton['bg'] = fg=getColor('buttonBGColor')
        else:
            self.saveButton.configure(state="disabled")
            self.saveButton['bg'] = fg=getColor('buttonDisabledBG')
        
    def LoadAnimationToEditor(self, selection=None):
        if selection == None and len(self.itemList) == 1:
            selection = self.itemList[0]
        else:
            if selection == None: selection = self.selection
            if selection == None:
                messagebox.showinfo('No animation selected', 'You have not selected an animation in the list', parent=self.root.window)
                return
            
        self.animlist.selection_clear(0, 'end')
        self.root.LoadAnimation(selection)
        self.colorItemlist()
        self.setSaveButtonEnabled(False)
        
    def CreateFile(self):
        initialValue = "New Animation %d" % (len(self.itemList) + 1)
        
        filename = simpledialog.askstring("Animation name", "What will be the file name?", parent=self.root.window, initialvalue=initialValue)
        if filename == None or len(filename.strip()) == 0: return
        filename = filename.strip() + ".txt"
        
        with open(dataPath + filename, "wb") as f:
            pass
            
        self.UpdateItemlist()
        self.LoadAnimationToEditor(filename)
        
    def UpdateItemlist(self, reloadOnly=False):
        if not reloadOnly:
            self.selectionIndex = -1
            self.selection = None
        self.animlist.delete(0, 'end')
        
        animationList = getAnimationList()
        if len(animationList) == 0:
            self.animlist.insert(0, "No animation...")
            self.animlist.itemconfig(0, {'fg': getColor('listItemText')})
        else:
            for anim in animationList: self.animlist.insert('end', anim[:-4])
        self.itemList = animationList
        self.colorItemlist()
        
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
                
    def onSelectionChange(self, event):
        if len(self.itemList) == 0:
            return
        w = event.widget
        try:
            index = int(w.curselection()[0])
            self.selectionIndex = int(index)
            self.selection = self.itemList[self.selectionIndex]
        except:
            self.selectionIndex = -1
            self.selection = None
       
    def hide(self):
        self.frame.pack_forget()
       
    def show(self):
        self.frame.pack(side='left', fill='y')

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
        #self.label['font'] = 'TkDefaultFont 9'

        
class FieldEditor:
    def __init__(self, root, rootFrame, fieldId, color=None):
        self.root = root
        self.rootFrame = rootFrame
        self.fieldId = fieldId
        
        
        self.initEditor(color)
        self.resetForm()
        
    def initEditor(self, labelColor):
        container = Frame(self.rootFrame, bg=getColor('BG'))
        
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
        
        self.baseContainer = container
        self.container = content
        self.label = label
        
    def setValue(self, newval):
        self.editingEnabled = False
        self.sv.set(newval)
        self.editingEnabled = True
        
        self.enable()
        
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
        self.fieldInput.config(state='disabled')
        self.editingEnabled = False
        
def getValueFromType(type, value):
    try:
        if type == 'text':
            value = value.strip()
            return value if len(value) != 0 else None
        elif type == 'float':
            return float(value)
    except:
        pass
    return None
        
def getStringValueFromType(type, value):
    if type == 'text': return value
    elif type == 'float':
        value = ("%01.03f" % value).rstrip('0').rstrip('.')
        return value[1:] if float(value) == 0 and value[0] == "-" else value
    return None
        
class AnimationEditor(BaseFormEditor):
    def __init__(self, root, rootFrame):
        BaseFormEditor.__init__(self, root, rootFrame, title="No animation loaded")
        self.Animation = None
        
        left, right = splitFrame(self.container, 'vertical')
        topRight, bottomRight = right, right
        #topRight, bottomRight = splitFrame(right, 'horizontal')
        farLeft, left = splitFrame(left, 'vertical')
        
        left['padx'] = 2
        right['padx'] = 2
        self.container['pady'] = 5
        self.container['padx'] = 5
        
        keyframeHeader = Frame(left, bg=getColor('BG'))
        keyframeHeader.pack(side='top', pady=(0, 3), fill='x')
        
        keyframeLabel = Label(keyframeHeader,  text='Keyframes:', bg=getColor('BG'), fg=getColor('labelTextColor'))
        keyframeLabel.pack(side='left')
        
        keyOrderDown = Button(keyframeHeader, bg=getColor('buttonBGColor'), fg=getColor('buttonTextColor'), text='↓')
        keyOrderDown['command'] = lambda self=self: self.reorderFrame(1)
        keyOrderDown.pack(side='right')
        keyOrderUp = Button(keyframeHeader, bg=getColor('buttonBGColor'), fg=getColor('buttonTextColor'), text='↑')
        keyOrderUp['command'] = lambda self=self: self.reorderFrame(-1)
        keyOrderUp.pack(side='right')
        CreateToolTip(keyOrderUp, 'Move keyframe up')
        CreateToolTip(keyOrderDown, 'Move keyframe down')
        
        pasteButton = Button(keyframeHeader, bg=getColor('buttonBGColor'), fg=getColor('buttonTextColor'), text='[P]')
        pasteButton['command'] = self.pasteFrame
        pasteButton.pack(side='right')
        copyButton = Button(keyframeHeader, bg=getColor('buttonBGColor'), fg=getColor('buttonTextColor'), text='[C]')
        copyButton['command'] = self.copyFrame
        copyButton.pack(side='right')
        CreateToolTip(pasteButton, 'Paste from clipboard')
        CreateToolTip(copyButton, 'Copy to clipboard')
        
        addKeyframeFromGame = Button(keyframeHeader, bg=getColor('buttonBGColor'), fg=getColor('buttonTextColor'), text='[GAME]')
        addKeyframeFromGame['command'] = lambda self=self: self.addFrame(fromGame=True)
        addKeyframeFromGame.pack(side='right')
        CreateToolTip(addKeyframeFromGame, 'Add keyframe from current camera position')
        
        framelist = Listbox(left, bg=getColor('ListBGColor'))
        framelist.bind('<<ListboxSelect>>', self.onSelectionChange)
        framelist.pack(side='top', fill='both', expand=1)
        
        removeFrameButton = Button(left, bg=getColor('buttonBGColor'), fg=getColor('buttonTextColor'), text='Remove keyframe')
        removeFrameButton['command'] = self.removeFrame
        removeFrameButton.pack(side='left')
        
        addFrameButton = Button(left, bg=getColor('buttonBGColor'), fg=getColor('buttonTextColor'), text='Add keyframe')
        addFrameButton['command'] = self.addFrame
        addFrameButton.pack(side='right')
        
        
        groupsHeader = Frame(farLeft, bg=getColor('BG'))
        groupsHeader.pack(side='top', pady=(0, 3), fill='x')
        
        groupLabel = Label(groupsHeader,  text='Groups:', bg=getColor('BG'), fg=getColor('labelTextColor'))
        groupLabel.pack(side='left')
        
        groupOrderDown = Button(groupsHeader, bg=getColor('buttonBGColor'), fg=getColor('buttonTextColor'), text='↓')
        groupOrderDown['command'] = lambda self=self: self.reorderGroup(1)
        groupOrderDown.pack(side='right')
        groupOrderDown = Button(groupsHeader, bg=getColor('buttonBGColor'), fg=getColor('buttonTextColor'), text='↑')
        groupOrderDown['command'] = lambda self=self: self.reorderGroup(-1)
        groupOrderDown.pack(side='right')
        CreateToolTip(groupOrderDown, 'Move group up')
        CreateToolTip(groupOrderDown, 'Move group down')
        
        grouplist = Listbox(farLeft, bg=getColor('ListBGColor'))
        grouplist.bind('<<ListboxSelect>>', self.onGroupSelectionChange)
        grouplist.pack(side='top', fill='both', expand=1)
        
        removeGroupButton = Button(farLeft, bg=getColor('buttonBGColor'), fg=getColor('buttonTextColor'), text='Remove group')
        removeGroupButton['command'] = self.removeGroup
        removeGroupButton.pack(side='left')
        
        addGroupButton = Button(farLeft, bg=getColor('buttonBGColor'), fg=getColor('buttonTextColor'), text='Add group')
        addGroupButton['command'] = self.addGroup
        addGroupButton.pack(side='right')
        
        
        
        fieldsFrame = Frame(topRight, bg=getColor('BG'))
        fieldsFrame.pack()
        #self.keyframeLabel = Label(fieldsFrame, bg=getColor('BG'), fg=getColor('labelTextColor'), text='Keyframe 0/0')
        #self.keyframeLabel.pack(side='top', pady=(0, 3))
        
        self.fields = []
        fieldFrame = None
        fieldPerLine = 3
        for i, field in enumerate(frameFields):
            if (i % fieldPerLine) == 0:
                fieldFrame = Frame(fieldsFrame, bg=getColor('BG'))
                fieldFrame.pack(anchor='w', expand=1, fill='both')
                
            if field == 'dof': # We skip that one
                continue
                
            newField = FieldEditor(self, fieldFrame, field, color=getColor('groupColor' + str(int(i / fieldPerLine))))
            newField.setTitle(fieldLabels[field])
            newField.baseContainer.pack(side='left', padx=2, pady=(0, 4))
            self.fields.append(newField)
            
        
        groupFrame = Frame(bottomRight, bg=getColor('lighterBG'))
        groupFrame.pack(fill='both')
        
        groupSettingsLabel = Label(groupFrame,  text='Group settings:', bg=getColor('lighterBG'), fg=getColor('labelTextColor'))
        groupSettingsLabel.pack(side='top')
        
        groupnameFrame = Frame(groupFrame, bg=getColor('lighterBG'))
        groupnameFrame.pack(side='top', pady=(0, 10))
        
        groupnameLabel = Label(groupnameFrame,  text='Name:', bg=getColor('lighterBG'), fg=getColor('labelTextColor'))
        groupnameLabel.pack(side='left', padx=(0, 7))
        groupnameVar = StringVar()
        groupnameVar.trace("w", lambda name, index, mode, groupnameVar=groupnameVar: self.onFieldChange('groupname', groupnameVar.get()))
        w = Entry(groupnameFrame, textvariable=groupnameVar, width=15)
        w.pack(side='left', padx=(0, 7))
        self.groupnameEntry = w
        
        preDelayLabel = Label(groupnameFrame,  text='Set pos before delay:', bg=getColor('lighterBG'), fg=getColor('labelTextColor'))
        preDelayLabel.pack(side='left', padx=(0, 7))
        preDelayCheckbox = Checkbutton(groupnameFrame, bg=getColor('lighterBG'))
        preDelayCheckbox['command'] = self.toggleSetPosBeforeDelay
        preDelayCheckbox.pack(side='left')
        self.preDelayCheckbox = preDelayCheckbox
        
        interpolationOptions = Frame(groupFrame, bg=getColor('lighterBG'))
        interpolationOptions.pack(side='top', pady=(0, 10))
        
        interpolationLabel = Label(interpolationOptions,  text='Interpolation:', bg=getColor('lighterBG'), fg=getColor('labelTextColor'))
        interpolationLabel.pack(side='left', padx=(0, 7))
        OPTIONS = [interpolationTypes[k] for k in interpolationTypes]
        interpolationVar = StringVar()
        interpolationVar.trace("w", lambda name, index, mode, interpolationVar=interpolationVar: self.onFieldChange('interpolation', interpolationVar.get()))
        w = OptionMenu(interpolationOptions, interpolationVar, OPTIONS[0], *OPTIONS)
        w.pack(side='left', padx=(0, 7))
        self.interpolationSelect = w
        
        easingLabel = Label(interpolationOptions,  text='Easing:', bg=getColor('lighterBG'), fg=getColor('labelTextColor'))
        easingLabel.pack(side='left', padx=(0, 7))
        OPTIONS = [easingTypes[k] for k in easingTypes]
        easingVar = StringVar()
        easingVar.trace("w", lambda name, index, mode, easingVar=easingVar: self.onFieldChange('easing', easingVar.get()))
        w = OptionMenu(interpolationOptions, easingVar, OPTIONS[0], *OPTIONS)
        w.pack(side='left', padx=(0, 15))
        self.easingSelect = w
        
        lengthOptions = Frame(groupFrame, bg=getColor('lighterBG'))
        lengthOptions.pack(side='top')
        
        lengthLabel = Label(lengthOptions,  text='Duration (frames):', bg=getColor('lighterBG'), fg=getColor('labelTextColor'))
        lengthLabel.pack(side='left', padx=(0, 6))
        
        lengthVar = StringVar()
        lengthVar.trace("w", lambda name, index, mode, lengthVar=lengthVar: self.onFieldChange('duration', lengthVar.get()))
        w = Entry(lengthOptions, textvariable=lengthVar, width=8)
        w.pack(side='left', padx=(0, 6))
        self.lengthEntry = w
        
        delayLabel = Label(lengthOptions,  text='Delay (frames):', bg=getColor('lighterBG'), fg=getColor('labelTextColor'))
        delayLabel.pack(side='left', padx=(0, 6))
        delayVar = StringVar()
        delayVar.trace("w", lambda name, index, mode, delayVar=delayVar: self.onFieldChange('delay', delayVar.get()))
        w = Entry(lengthOptions, textvariable=delayVar, width=8)
        w.pack(side='left', padx=(0, 6))
        self.delayEntry = w
        
        
        extraGroupTools = Frame(groupFrame, bg=getColor('lighterBG'))
        extraGroupTools.pack(pady=(10, 3))
        
        visualizeButton = Button(extraGroupTools, bg=getColor('buttonBGColor'), fg=getColor('buttonTextColor'), text='Visualize X/Y movement')
        visualizeButton['command'] = self.visualizeGroup
        visualizeButton.pack(side='left', padx=(0, 3))
        
        relativityLabel = Label(extraGroupTools,  text='Relativity:', bg=getColor('lighterBG'), fg=getColor('labelTextColor'))
        relativityLabel.pack(side='left', padx=(0, 7))
        OPTIONS = [relativityTypes[k] for k in relativityTypes]
        relativityVar = StringVar()
        relativityVar.trace("w", lambda name, index, mode, relativityVar=relativityVar: self.onFieldChange('relativity', relativityVar.get()))
        w = OptionMenu(extraGroupTools, relativityVar, OPTIONS[0], *OPTIONS)
        w.pack(side='left', padx=(0, 7))
        self.relativitySelect = w
        
        #advancedSettingsButton = Button(extraGroupTools, bg=getColor('buttonBGColor'), fg=getColor('buttonTextColor'), text='Advanced group settings')
        #advancedSettingsButton['command'] = self.openAdvancedSettings
        #advancedSettingsButton.pack(side='left')
        
        
        toolsFrame = Frame(bottomRight, bg=getColor('BG'))
        toolsFrame.pack(side='bottom')
        
        playAnimButton = Button(toolsFrame, text="Play from group", bg=getColor('buttonBGColor'), fg=getColor('buttonTextColor'))
        playAnimButton['command'] = lambda self=self: self.root.PlayAnimation(self.currentGroup)
        playAnimButton.pack(side='left')
        CreateToolTip(playAnimButton, "Play the entire animation from the current group downward")
        
        playGroupButton = Button(toolsFrame, text="Play group", bg=getColor('buttonBGColor'), fg=getColor('buttonTextColor'))
        playGroupButton['command'] = lambda self=self: self.root.PlayAnimation(self.currentGroup, True)
        playGroupButton.pack(side='left', padx=(4))
        CreateToolTip(playGroupButton, "Play only the current group")
        
        previewButton = Button(toolsFrame, text="[OFF] Live preview", bg=getColor('buttonBGColor'), fg=getColor('buttonTextColor'))
        previewButton['command'] = lambda self=self: self.root.toggleLivePreview()
        previewButton.pack(side='left', padx=(0, 4))
        CreateToolTip(previewButton, "Preview changes made to keyframes in live")
        
        liveControlButton = Button(toolsFrame, text="[OFF] Live Control", bg=getColor('buttonBGColor'), fg=getColor('buttonTextColor'))
        liveControlButton['command'] = lambda self=self: self.root.toggleLiveControl()
        liveControlButton.pack(side='left')
        CreateToolTip(liveControlButton, "Control the camera in-game with the in-game buttons: 1, 2, 3, 4, F, B, U, D")
        
        self.liveControlButton = liveControlButton
        self.playGroupButton = playGroupButton
        self.playAnimButton = playAnimButton
        self.previewButton = previewButton
        
        self.grouplist = grouplist
        self.framelist = framelist
        self.fieldVars = {
            'interpolation': interpolationVar,
            'easing': easingVar,
            'duration': lengthVar,
            'delay': delayVar,
            'name': groupnameVar,
            'relativity': relativityVar,
        }
        
        self.reset()
        self.canvas = None
        self.canvasWindow = None
        self.canvasWindowDefaultWidth = 400
        self.canvasWindowDefaultHeight = 400
        self.advancedWindow = None
        
    def getGroupToCanvasData(self):
        if self.group == None or self.group['length'] == 0: return [], [], 0, 0
        cachedGroup = self.Animation.calculateCachedFrames(self.currentGroup, True)[0]
        
        maxX = max(frame['x'] for frame in cachedGroup['frames'])
        minX = min(frame['x'] for frame in cachedGroup['frames'])
        maxY = max(frame['y'] for frame in cachedGroup['frames'])
        minY = min(frame['y'] for frame in cachedGroup['frames'])
        
        
        maxX2 = max(frame['x'] for frame in self.group['frames'])
        minX2 = min(frame['x'] for frame in self.group['frames'])
        maxY2 = max(frame['y'] for frame in self.group['frames'])
        minY2 = min(frame['y'] for frame in self.group['frames'])
        
        maxX = max(maxX, maxX2)
        minX = min(minX, minX2)
        maxY = max(maxY, maxY2)
        minY = min(minY, minY2)
        
        diffX = abs(maxX - minX)
        diffY = abs(maxY - minY) if maxY != minY else maxY
        biggestDiff = max(diffX, diffY)
        windowSize = min(self.canvasWindowWidth, self.canvasWindowHeight)
        zoomLevel = (windowSize / biggestDiff) * 0.80 if biggestDiff != 0 else 1
    
        offsetX = (self.canvasWindowWidth - (diffX * zoomLevel)) / 2
        offsetY = (self.canvasWindowHeight - (diffY * zoomLevel)) / 2
        
        color1 = (3, 252, 53)
        color2 = (252, 3, 3)
        diff = [color2[i] - color1[i] for i in range(3)]
        
        canvasPoints = []
        frameCount = len(cachedGroup['frames'])
        for i, frame in enumerate(cachedGroup['frames']):
            t = i / frameCount
            x = (frame['x'] - min(0, minX)) * zoomLevel + offsetX
            y = (frame['y'] - min(0, minY)) * zoomLevel + offsetY
            newColor = "".join(["%02x" % int(color1[n] + diff[n] * t) for n in range(3)])
            canvasPoints.append((x, y, "#" + newColor))
            
        keyframes = []
        for i, frame in enumerate(self.group['frames']):
            t = i / len(self.group['frames'])
            
            x = (frame['x'] - min(0, minX)) * zoomLevel + offsetX
            y = (frame['y'] - min(0, minY)) * zoomLevel + offsetY
            
            newColor = "".join(["%02x" % int(color1[n] + diff[n] * t) for n in range(3)])
            keyframes.append((x, y, "#" + newColor))
           
        return canvasPoints, keyframes, self.group['length'], self.group['interpolation']
        
    def updateCanvas(self):
        if self.canvas == None: return
        self.canvas.delete("all")
        
        canvasData, keyframes, keyframeCount, interpolationType = self.getGroupToCanvasData()
        if canvasData == [] or keyframeCount <= 1: return
        canvasDataLen = len(canvasData)
        keyframeWeight = int(canvasDataLen / (keyframeCount - 1))
        
        for i, data in enumerate(canvasData):
            x, y, color = data
            
            if interpolationType != 2 and (i + 1 < canvasDataLen): #Nearest = no line
                self.canvas.create_line(x, y, canvasData[i + 1][0], canvasData[i + 1][1], fill=color)
            if (i + 1 == canvasDataLen) or (i % keyframeWeight) == 0: #Keyframe
                x, y, color = keyframes[int((i + 1) / keyframeWeight)]
                pointSize = 5 if (i + 1 == canvasDataLen or i == 0) else 4
                self.canvas.create_oval(x - pointSize, y - pointSize, x + pointSize, y + pointSize, fill=color)
        
    def visualizeGroup(self):
        if self.canvasWindow != None:
            self.canvasWindow.deiconify()
            self.canvasWindow.focus_force()
            self.updateCanvas()
            return
        if self.group == None: return
        
        self.canvasWindowWidth = self.canvasWindowDefaultWidth
        self.canvasWindowHeight = self.canvasWindowDefaultHeight
        
        master = Toplevel()
        master.protocol("WM_DELETE_WINDOW", self.closeCanvas)
        master.bind("<Configure>", self.onCanvasResize)
        
        self.canvas = Canvas(master, width=self.canvasWindowWidth, height=self.canvasWindowHeight, bg=getColor('BG'))
        self.canvas.pack(fill='both', expand=True)
        
        self.updateCanvas()
        self.canvasWindow = master
        master.focus_force()
        master.mainloop()
        
    def openAdvancedSettings(self):
        if self.advancedWindow != None:
            self.advancedWindow.deiconify()
            self.advancedWindow.focus_force()
            return
        if self.group == None: return
        
        master = Toplevel(bg=getColor('lighterBG'))
        master.focus_force()
        master.protocol("WM_DELETE_WINDOW", self.closeAdvancedWindow)
        
        self.advancedWindow = master
        master.mainloop()
        
    def closeAdvancedWindow(self):
        self.advancedWindow.destroy()
        self.advancedWindow = None
        
    def onCanvasResize(self, event):
        if self.canvasWindow == None: return
        width = event.width
        height = event.height
        if width != self.canvasWindowWidth or height != self.canvasWindowHeight and width > 0 and height > 0:
            self.canvasWindowWidth = width
            self.canvasWindowHeight = height
            self.updateCanvas()
        
    def closeCanvas(self):
        self.canvasWindow.destroy()
        self.canvasWindow = None
        self.canvas = None
        
    def setControlEnabled(self, enabled):
        self.liveControlButton.configure(state=("normal" if enabled else "disabled"))
        
    def enablePlayback(self):
        self.playGroupButton.configure(state="normal")
        self.playAnimButton.configure(state="normal")
        self.previewButton.configure(state="normal")
        
    def disablePlayback(self):
        self.playGroupButton.configure(state="disabled")
        self.playAnimButton.configure(state="disabled")
        self.previewButton.configure(state="disabled")
        
    def toggleSetPosBeforeDelay(self):
        self.group['pre_delay_pos'] = int(not self.group['pre_delay_pos'])
        if self.Animation.cachedGroups[self.currentGroup] != None:
            self.Animation.cachedGroups[self.currentGroup]['pre_delay_pos'] = self.group['pre_delay_pos']
        if self.group['pre_delay_pos'] == 0:
            self.preDelayCheckbox.deselect()
        else:
            self.preDelayCheckbox.select()
        self.root.onAnimModification()
        
    def setEasingField(self):
        sleep(1 / 60)
        self.fieldVars['easing'].set(easingTypes[self.group['easing']])
        
    def discardCache(self):
        self.Animation.cachedGroups[self.currentGroup] = None
        self.updateCanvas()
        
    def onFieldChange(self, field, value):
        if self.Animation == None: return
        if field == "easing" and value == "---":
            threading.Thread(target=self.setEasingField).start()
            return False
        if field in frameFields:
            value = getValueFromType(fieldTypes[field], value)
            if value == None: return
            
            if field == 'name':
                value = value.replace(",", ".").strip()
                if len(value) == 0: return
                self.framelist.delete(self.currentFrame)
                self.framelist.insert(self.currentFrame, value)
                self.framelist.itemconfig(self.currentFrame, {'fg': getColor('listSelectedItem'), 'bg': getColor('listSelectedItemBG')})

            self.Animation.setValue(self.currentGroup, field, self.currentFrame, value)
            self.updateCanvas()
            self.root.onAnimModification(True)
        else:
            if self.enabledEditing:
                try:
                    if field == 'duration' or field == 'delay':
                        self.group[field] = int(value)  
                        if field == 'duration':
                            self.discardCache()
                        elif field == 'delay' and self.Animation.cachedGroups[self.currentGroup] != None:
                            self.Animation.cachedGroups[self.currentGroup]['delay'] = int(value)
                            self.updateCanvas()
                    elif field == 'groupname':
                        value = value.replace('[', '(').replace(']', ')').replace('=', '-').replace(',', '.').strip()
                        if len(value) > 0:
                            self.grouplist.delete(self.currentGroup)
                            self.grouplist.insert(self.currentGroup, value)
                            self.grouplist.itemconfig(self.currentGroup, {'fg': getColor('listSelectedItem'), 'bg': getColor('listSelectedItemBG')})
                            self.group['name'] = value
                    else:
                        selectDicts = {
                            'easing': easingTypes2,
                            'interpolation': interpolationTypes2,
                            'relativity': relativityTypes2,
                        }
                        self.group[field] = selectDicts[field][value]
                        self.discardCache()
                    self.root.onAnimModification(field == 'relativity')
                except:
                    pass
                
    def resetFrame(self):
        for field in self.fields: field.resetForm()
        self.disablePlayback()
        self.currentFrame = 0
        self.framelist.delete(0, 'end')
                
    def reset(self, formOnly=False):
        self.resetFrame()
        self.framelist.delete(0, 'end')
        self.grouplist.delete(0, 'end')
        self.lengthEntry.configure(state="disabled")
        self.delayEntry.configure(state="disabled")
        self.easingSelect.configure(state="disabled")
        self.interpolationSelect.configure(state="disabled")
        self.groupnameEntry.configure(state="disabled")
        self.relativitySelect.configure(state="disabled")
        self.preDelayCheckbox.configure(state="disabled")
        self.currentFrame = 0
        self.currentGroup = 0
        self.group = None
        if not formOnly: self.Animation = None
        
    def reorderFrame(self, order):
        if self.Animation == None or self.group == None: return
        if order == -1 and self.currentFrame == 0: return
        if order == 1 and (self.currentFrame + 1) == self.group['length']: return
        self.discardCache()
        
        self.group['frames'][self.currentFrame], self.group['frames'][self.currentFrame + order] = self.group['frames'][self.currentFrame + order], self.group['frames'][self.currentFrame]
        self.setFrame(self.currentFrame + order)
        self.updateFrameList()
        self.recolorFrameList()
        self.root.onAnimModification()
        
    def reorderGroup(self, order):
        if self.Animation == None or self.group == None: return
        if order == -1 and self.currentGroup == 0: return
        if order == 1 and (self.currentGroup + 1) >= len(self.Animation.groups): return
        
        self.Animation.groups[self.currentGroup], self.Animation.groups[self.currentGroup + order] = self.Animation.groups[self.currentGroup + order], self.Animation.groups[self.currentGroup]
        self.Animation.cachedGroups[self.currentGroup], self.Animation.cachedGroups[self.currentGroup + order] = self.Animation.cachedGroups[self.currentGroup + order], self.Animation.cachedGroups[self.currentGroup]
        self.updateCanvas()
        
        self.setGroup(self.currentGroup + order)
        self.updateGroupList()
        self.recolorGroupList()
        self.root.onAnimModification()
        
    def addGroup(self):
        if self.Animation == None: return
        groupData = {
            'name': 'New group',
            'duration': 60,
            'delay': 0,
            'easing': 0,
            'interpolation': 1,
            'pre_delay_pos': 0,
            'length': 0,
            'relativity': 0,
            'frames': []
        }
        self.Animation.addGroup(groupData, self.currentGroup + 1)
        self.updateGroupList()
        self.setGroup(self.currentGroup + 1 if self.currentGroup + 1 < len(self.Animation.groups) else self.currentGroup)
        self.root.onAnimModification()
        
    def removeGroup(self):
        if self.Animation == None or len(self.Animation.groups) == 0: return
        self.Animation.removeGroup(self.currentGroup)
        self.updateGroupList()
        if len(self.Animation.groups) == 0:
            self.reset(formOnly=True)
        else:
            self.setGroup(self.currentGroup if self.currentGroup < len(self.Animation.groups) else self.currentGroup - 1)
        self.root.onAnimModification()
        
    def copyFrame(self):
        if self.Animation == None or self.group == None or self.group['length'] == 0: return
        frame = self.group['frames'][self.currentFrame]
        frame['dof'] = 0.0
        pyperclip.copy(",".join([str(frame[k]) for k in frameFields]))
        messagebox.showinfo("Copied", "Keyframe data copied", parent=self.root.window)
        
    def pasteFrame(self):
        if self.Animation == None or self.group == None: return
        try:
            frameData = pyperclip.paste().strip().split(",")
            newFrame = {
                'name': frameData[0],
                'fov': float(frameData[1]),
                'dof': float(frameData[2]),
                'x': float(frameData[3]),
                'y': float(frameData[4]),
                'z': float(frameData[5]),
                'rotx': float(frameData[6]),
                'roty': float(frameData[7]),
                'tilt': float(frameData[8])
            }
        except:
            messagebox.showinfo("Error", "Error pasting frame data", parent=self.root.window)
            return
        self.Animation.addFrame(self.currentGroup, newFrame, self.currentFrame + 1)
        self.updateFrameList()
        self.setFrame(self.currentFrame + 1 if self.group['length'] > (self.currentFrame + 1) else self.currentFrame)
        self.root.onAnimModification(True)
        self.updateCanvas()
        
    def addFrame(self, fromGame = False):
        if self.Animation == None: return
        if len(self.Animation.groups) == 0: return messagebox.showinfo('Error', 'Please add a group first', parent=self.root.window)
        
        if fromGame == False:
            if (self.currentFrame + 1) < self.group['length']:
                framedata = Interpolation.interpolateLine(self.group['frames'][self.currentFrame], self.group['frames'][self.currentFrame + 1], 0.5)
            elif self.group['length'] != 0:
                framedata = self.group['frames'][self.currentFrame].copy()
            else:
                framedata = { 'fov': 65, 'dof': 0, 'x': 0, 'y': 0, 'z': 0, 'rotx': 0, 'roty': 0, 'tilt': 0}
        else:
            if not self.root.LiveEditor.startIfNeeded(): return
            framedata = self.root.LiveEditor.getCameraPos(self.group['relativity'])
            
        framedata['name'] = "%d" % (self.group['length'] + 1)
        while True:
            if next((f for f in self.group['frames'] if f['name'] == framedata['name']), None) == None:
                break
            framedata['name'] += "_2"
            
        
        self.Animation.addFrame(self.currentGroup, framedata, self.currentFrame + 1)
        self.updateFrameList()
        self.setFrame(self.currentFrame + 1 if self.group['length'] > (self.currentFrame + 1) else self.currentFrame)
        self.root.onAnimModification(True)
        self.updateCanvas()
        
    def removeFrame(self):
        if self.Animation == None: return
        if len(self.Animation.groups) == 0: return messagebox.showinfo('Error', 'Please add a group first', parent=self.root.window)
        if self.group['length'] == 0: return
        self.Animation.removeFrame(self.currentGroup, self.currentFrame)
        self.updateFrameList()
        if self.group['length'] == 0:
            self.resetFrame()
        else:
            self.setFrame(self.currentFrame if self.currentFrame < self.group['length'] else self.currentFrame - 1)
        self.updateCanvas()
        self.root.onAnimModification(True)
        
    def recolorFrameList(self):
        for i in range(self.group['length']):
            if i == self.currentFrame:
                self.framelist.itemconfig(i, {'fg': getColor('listSelectedItem'), 'bg': getColor('listSelectedItemBG')})
            else:
                self.framelist.itemconfig(i, {'fg': getColor('listUnimportantItemText'), 'bg': getColor('listItemOddBG' if i & 1 == 1 else 'listItemEvenBG')})
    
    def updateFrameList(self):
        self.framelist.delete(0, 'end')
        if self.Animation == None or len(self.Animation.groups) == 0 or self.group['length'] == 0:
            self.framelist.insert(0, 'No frame')
            self.framelist.itemconfig(0, {'fg': getColor('listItemText'), 'bg': getColor('listItemOddBG')})
            return
        for frame in self.group['frames']:
            self.framelist.insert('end', frame['name'])    
            
    def recolorGroupList(self):
        for i in range(len(self.Animation.groups)):
            if i == self.currentGroup:
                self.grouplist.itemconfig(i, {'fg': getColor('listSelectedItem'), 'bg': getColor('listSelectedItemBG')})
            else:
                self.grouplist.itemconfig(i, {'fg': getColor('listUnimportantItemText'), 'bg': getColor('listItemOddBG' if i & 1 == 1 else 'listItemEvenBG')})
            
    def updateGroupList(self):
        self.grouplist.delete(0, 'end')
        if self.Animation == None or len(self.Animation.groups) == 0:
            self.grouplist.insert(0, 'No group')
            self.grouplist.itemconfig(0, {'fg': getColor('listItemText'), 'bg': getColor('listItemOddBG')})
            return
        for group in self.Animation.groups:
            self.grouplist.insert('end', group['name'])
            
        self.recolorGroupList()
        
    def LoadAnimation(self, anim):
        self.reset()
        self.Animation = anim
        self.updateGroupList()
        if len(anim.groups) > 0: self.setGroup(0)
        self.setTitle("Loaded: " + anim.name)
          
    def onSelectionChange(self, event):
        if self.Animation == None: return
        w = event.widget
        try:
            index = int(w.curselection()[0])
            self.setFrame(index)
        except Exception as e:
            pass
          
    def onGroupSelectionChange(self, event):
        if self.Animation == None: return
        w = event.widget
        try:
            index = int(w.curselection()[0])
            self.setGroup(index)
        except Exception as e:
            pass
            
    def setGroup(self, index):
        self.group = self.Animation.groups[index]
        self.currentGroup = index
        self.enabledEditing = False
        self.lengthEntry.configure(state="enabled")
        self.delayEntry.configure(state="enabled")
        self.easingSelect.configure(state="enabled")
        self.interpolationSelect.configure(state="enabled")
        self.groupnameEntry.configure(state="enabled")
        self.relativitySelect.configure(state="enabled")
        self.recolorGroupList()
        self.updateFrameList()
        
        self.fieldVars['interpolation'].set(interpolationTypes[self.group['interpolation']])
        self.fieldVars['easing'].set(easingTypes[self.group['easing']])
        self.fieldVars['duration'].set(self.group['duration'])
        self.fieldVars['delay'].set(self.group['delay'])
        self.fieldVars['name'].set(self.group['name'])
        self.fieldVars['relativity'].set(relativityTypes[self.group['relativity']])
        
        self.preDelayCheckbox.configure(state="normal")
        if self.group['pre_delay_pos'] == 0:
            self.preDelayCheckbox.deselect()
        else:
            self.preDelayCheckbox.select()
        
        if self.group['length'] > 0: self.setFrame(0)
        else:
            self.enabledEditing = True
            self.resetFrame()
        self.updateCanvas()
            
    def setFrame(self, index):
        self.enabledEditing = False
        self.framelist.selection_clear(0, 'end')
        #self.keyframeLabel['text'] = 'Keyframe %d/%d' % (index + 1, self.group['length'])
        for field in self.fields:
            value = getStringValueFromType(fieldTypes[field.fieldId], self.Animation.getValue(self.currentGroup, field.fieldId, index))
            field.setValue(value)
        self.currentFrame = index
        self.recolorFrameList()
        self.enabledEditing = True
        self.root.onFrameChange()
        if not self.root.LiveEditor.runningAnimation:
            self.enablePlayback()
        
    def getFrame(self):
        return (None, None) if (self.group == None or self.group['length'] == 0) else (self.group['frames'][self.currentFrame], self.group['relativity'])

def matrixMult(mat, b):
    result = [[0] * 3] *3
    
    for i in range(3):
        for j in range(3):
            result[i][j] = sum([mat[i][k] * b[k][j] for k in range(3)])
            
    return result
        
class LiveEditor:
    def __init__(self, root):
        self.root = root
        self.setPlayer(0)
        self.stop()
        
    def setPlayer(self, id):
        self.playerAddress = game_addresses.addr['t7_p1_addr'] + (id * game_addresses.addr['t7_playerstruct_size'])
        
    def stop(self, exiting=False):
        self.camAddr = None
        self.inputbuffer = None
        self.T = None
        self.running = False
        self.runningAnimation = False
        self.liveEditing = False
        self.liveControl = False
        self.exiting = exiting
        
    def startIfNeeded(self):
        if self.T == None:
            return self.loadProcess()
        try:
            self.getCameraAddr()
        except:
            self.stop()
            return False
        return True
        
    def loadProcess(self):
        try:
            self.T = GameClass("TekkenGame-Win64-Shipping.exe")
            self.running = True
            self.getCameraAddr()
        except Exception as err:
            self.stop()
        return self.running
        
    def toggleLivePreview(self):
        self.liveEditing = not self.liveEditing
        if self.liveEditing:
            self.liveEditing = self.startIfNeeded()
            if self.liveEditing and self.liveControl: self.liveControl = False
        return self.liveEditing
        
    def toggleLiveControl(self):
        self.liveControl = not self.liveControl
        if self.liveControl:
            self.liveControl = self.startIfNeeded()
            if self.liveControl and self.liveEditing:
                self.liveEditing = False
                self.root.AnimationEditor.previewButton['text'] = '[OFF] Live preview'
        return self.liveControl
        
    def writeFloat(self, addr, value):
        self.T.writeBytes(addr, struct.pack('f', value))
        
    def readFloat(self, addr):
        return struct.unpack('f', self.T.readBytes(addr, 4))[0]
        
    def readPointerPath(self, baseAddr, ptrlist):
        currAddr = self.T.readInt(baseAddr, 8)
        for ptr in ptrlist:
            currAddr = self.T.readInt(currAddr + ptr, 8)
        return currAddr
        
    def moveCamera(self, camPos, inputs, frameHeld):
        distance = 3
        rotational = '1' in inputs or '3' in inputs
        up = 'U' in inputs
        down = 'D' in inputs
        left = 'B' in inputs
        right = 'F' in inputs
        
        if frameHeld > 260:
            if frameHeld > 300: frameHeld = 300
            distance += ((frameHeld - 230)) / 2
        elif frameHeld > 30:
            distance += ((frameHeld - 30) / 6) if frameHeld <= 90 else ((90 - 30) / 6)
            
        if rotational:
            rotationalDistance = (distance / 10)
            if rotationalDistance > 2: rotationalDistance = 2
            if '1' in inputs:
                if up:
                    camPos['roty'] += rotationalDistance
                elif down:
                    camPos['roty'] -= rotationalDistance
                if right:
                    camPos['rotx'] += rotationalDistance
                elif left:
                    camPos['rotx'] -= rotationalDistance
            else:
                if up:
                    camPos['fov'] -= rotationalDistance
                elif down:
                    camPos['fov'] += rotationalDistance
                if right:
                    camPos['tilt'] += rotationalDistance 
                elif left:
                    camPos['tilt'] -= rotationalDistance
        else:
            yaw = camPos['rotx'] * degToRad
            pitch = camPos['roty'] * degToRad
            roll = camPos['tilt'] * degToRad
        
            if '2' in inputs:
                camPos['z'] += distance
            elif '4' in inputs:
                camPos['z'] -= distance
            if up or down:
                xOffset = math.cos(yaw) * math.cos(pitch)
                yOffset = math.sin(yaw) * math.cos(pitch)
                zOffset = math.sin(pitch)
                
                newDistance = (distance if up else -distance)
                camPos['x'] = camPos['x'] + xOffset * newDistance
                camPos['y'] = camPos['y'] + yOffset * newDistance
                camPos['z'] = camPos['z'] + zOffset * newDistance
                
            if right or left:
                yaw += math.pi / 2
                xOffset = math.cos(yaw)
                yOffset = math.sin(yaw)
                
                newDistance = (distance if right else -distance)
                camPos['x'] = camPos['x'] + xOffset * newDistance
                camPos['y'] = camPos['y'] + yOffset * newDistance
            
        self.setCameraPos(camPos)
        return 0 if (rotational and not up and not down and not left and not right) else frameHeld + 1
        
    def nopInputsCode(self):
        self.T.writeBytes(game_addresses.addr['input_code_injection'], bytes([0x31, 0xC0, 0x90, 0x90])) # xor eax, eax ; nop; nop
        
    def resetInputsCode(self):
        if not self.T: return
        self.T.writeBytes(game_addresses.addr['input_code_injection'], bytes([0x8B, 0x44, 0x81, 0x20])) # mov eax,[rcx+rax*4+20]
        
    def liveControlLoop(self):
        self.lockCamera()
        self.getInputBufferAddr()
        self.nopInputsCode()
        try:
            frameHeld = 0
            while self.liveControl:
                inputs = self.getInputs()
                if len(inputs) != 0:
                    frameHeld = self.moveCamera(self.getCameraPos(), inputs, frameHeld)
                elif frameHeld > 0:
                    frameHeld -= 4
                self.waitSingleFrame()
        except:
            self.liveControl = False
            
        if not self.exiting: self.root.AnimationEditor.liveControlButton['text'] = '[OFF] Live control'       
        self.resetInputsCode()
        
    def playAnimation(self, groups):
        self.runningAnimation = True
        self.lockCamera()
        self.getCameraAddr()
        self.liveControl = False
        self.root.AnimationEditor.setControlEnabled(False)
        
        try:
            for g in groups:
                if g['delay'] > 0:
                    if g['pre_delay_pos'] > 0 and g['length'] > 0:
                        self.setCameraPos(g['frames'][0], g['relativity'])
                    self.waitFrame(g['delay'])
                for f in g['frames']:
                    if self.runningAnimation == False: raise
                    self.setCameraPos(f, g['relativity'])
                    self.waitFrame(1)
        except Exception as e:
            pass
        self.runningAnimation = False
        if not self.exiting:
            if self.root.AnimationEditor.getFrame()[0] != None:
                self.root.AnimationEditor.enablePlayback()
            self.root.AnimationEditor.setControlEnabled(True)
        
    def lockCamera(self):
        if not self.startIfNeeded(): return
        self.T.writeBytes(game_addresses.addr['camera_code_injection2'], bytes([0x90] * 8))
        self.T.writeBytes(game_addresses.addr['camera_code_injection'] + 0xE, bytes([0x90] * 8))
        self.T.writeBytes(game_addresses.addr['camera_code_injection'] + 0x25, bytes([0x90] * 6))
        self.T.writeBytes(game_addresses.addr['camera_code_injection'], bytes([0x90] * 8))
        self.T.writeBytes(game_addresses.addr['camera_code_injection'] + 0x1B, bytes([0x90] * 6))
        
    def unlockCamera(self):
        if not self.startIfNeeded(): return
        self.T.writeBytes(game_addresses.addr['camera_code_injection2'], bytes([0xF3, 0x0f, 0x11, 0x89, 0x9c, 0x03, 000, 0x0]))
        self.T.writeBytes(game_addresses.addr['camera_code_injection'] + 0xE, bytes([0xF2, 0x0f, 0x11, 0x87, 0x04, 0x04, 0x0, 0x0]))
        self.T.writeBytes(game_addresses.addr['camera_code_injection'] + 0x25, bytes([0x89, 0x87, 0x0c, 0x04, 0x0, 0x0]))
        self.T.writeBytes(game_addresses.addr['camera_code_injection'], bytes([0xF2, 0x0F, 0x11, 0x87, 0xF8, 0x03, 0x0, 0x0]))
        self.T.writeBytes(game_addresses.addr['camera_code_injection'] + 0x1B, bytes([0x89, 0x87, 0, 0x04, 0, 0]))
        
    def getCameraAddr(self):
        self.camAddr = self.readPointerPath(game_addresses.addr['camera_starting_ptr'], [0x30, 0x418])
        return self.camAddr
        
    def setCameraPos(self, cam, relative=0):
        camAddr = self.camAddr
        
        rotx = cam['rotx']
        roty = cam['roty']
        x = cam['x']
        y = cam['y']
        z = cam['z']
        
        if relative >= 11:
            relative -= 10
            self.setPlayer(1) #2p
        else:
            self.setPlayer(0) #1p
            
        if relative == 1: #Pos relativity
            playerPos = self.getPlayerPos()
            x += playerPos['x']
            y += playerPos['y']
        elif relative == 2: #Pos & height relativity
            playerPos = self.getPlayerPos()
            x += playerPos['x']
            y += playerPos['y']
            z += playerPos['z']
        elif relative == 3 or relative == 4: #Pos & height & rot relativity
            playerPos = self.getPlayerPos()
            playerRot = self.getPlayerRot() * ((math.pi * 2) / 65535)
            
            distance = math.sqrt(x ** 2 + y ** 2)
            camAngle = math.atan2(y, x)
            
            finalAngle = (camAngle - playerRot)
            
            newx = (distance) * math.cos(finalAngle)
            newy = (distance) * math.sin(finalAngle)
            
            x = newx + playerPos['x']
            y = newy + playerPos['y']
            if relative == 4: #height relativity
                z += playerPos['z']
                
            rotx = (rotx - (self.getPlayerRot() * (360/ 65535))) % 360
        elif relative == 5: #Look-at
            playerPos = self.getPlayerPos()
            diffx = playerPos['x'] - x
            diffy = playerPos['y'] - y
            diffz = z - playerPos['z']
            distance = math.sqrt(diffx ** 2 + diffy ** 2)
            
            rotx = math.atan2(diffy, diffx) * (180 / math.pi)
            roty = math.atan2(distance, diffz) * (180 / math.pi) - 90
        
        self.writeFloat(camAddr + 0x39C, cam['fov']) #FOV
        self.writeFloat(camAddr + 0x404, roty) #roty
        self.writeFloat(camAddr + 0x408, rotx) #rotx
        self.writeFloat(camAddr + 0x40C, cam['tilt']) #tilt
        self.writeFloat(camAddr + 0x3F8, x) #x
        self.writeFloat(camAddr + 0x3FC, y) #y
        self.writeFloat(camAddr + 0x400, z) #z
            
    def getCameraPos(self, relative=0):
        if not self.startIfNeeded(): return
        camAddr = self.getCameraAddr()
        cam = {
            'fov': self.readFloat(camAddr + 0x39C),
            'dof': 0,
            'rotx': self.readFloat(camAddr + 0x408),
            'roty': self.readFloat(camAddr + 0x404),
            'tilt': self.readFloat(camAddr + 0x40C),
            'x': self.readFloat(camAddr + 0x3F8),
            'y': self.readFloat(camAddr + 0x3FC),
            'z': self.readFloat(camAddr + 0x400)
        }
        
        if relative >= 11:
            relative -= 10
            self.setPlayer(1) #2p
            
        if relative == 1: #Pos
            playerPos = self.getPlayerPos()
            cam['x'] -= playerPos['x']
            cam['y'] -= playerPos['y']
        elif relative == 2: #Pos & height
            playerPos = self.getPlayerPos()
            cam['x'] -= playerPos['x']
            cam['y'] -= playerPos['y']
            cam['z'] -= playerPos['z']
        elif relative == 3 or relative == 4: #Pos & rot & height
            playerPos = self.getPlayerPos()
            playerRot = self.getPlayerRot()
            
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
            if relative == 4:
                cam['z'] -= playerPos['z'] #Relative player height
        
        return cam
        
    def getPlayerHeight(self):
        return self.getPlayerFloorheight() + self.readFloat(self.playerAddress + 0x114) / 10
        
    def getPlayerFloorheight(self):
        return self.readFloat(self.playerAddress + 0x1B0) / 10
        
    def getPlayerPos(self):
        return {
            'x': self.readFloat(self.playerAddress + 0xFC) / 10,
            'y': -(self.readFloat(self.playerAddress + 0xF4) / 10),
            'z': self.getPlayerHeight(),
        }
        
    def getPlayerRot(self):
        return self.T.readInt(self.playerAddress + 0x1c0, 2)
        
    def waitFrame(self, amount):
        currFrame = self.T.readInt(game_addresses.addr['frame_counter'], 4)
        targetFrame = currFrame + amount
        while currFrame < targetFrame:
            if currFrame < 10 or self.runningAnimation == False:
                raise
            currFrame = self.T.readInt(game_addresses.addr['frame_counter'], 4)
        
    def waitSingleFrame(self):
        currFrame = self.T.readInt(game_addresses.addr['frame_counter'], 4)
        originalFrame = currFrame
        while currFrame == originalFrame:
            if not self.liveControl: return
            currFrame = self.T.readInt(game_addresses.addr['frame_counter'], 4)
        
    keyvalues = {
        'U': 1,
        'D': 2,
        'B': 4,
        'F': 8,
        'MENU': 32,
        'ASSIST': 256,
        'RA': 512,
        '3': 4096,
        '4': 8192,
        '1': 16384,
        '2': 32768,
    }
    
    def getInputBufferAddr(self):
        self.inputbuffer = self.T.readInt(game_addresses.addr['input_buffer'], 8) + 0x20
        return self.inputbuffer

    def getInputs(self):
        inputs = self.T.readInt(self.inputbuffer, 2)
        return [f for f in LiveEditor.keyvalues if (inputs & LiveEditor.keyvalues[f]) != 0]
        
class GUI_TekkenCameraAnimator():
    def __init__(self, mainWindow=True):
        window = Tk() if mainWindow else Toplevel()
        self.window = window
        
        self.setTitle()
        window.iconbitmap(dataPath2 + 'hotaru.ico')
        window.geometry("960x372")
        window.minsize(500, 372)
        #self.setWindowSize(1163, 539)
        window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.AnimationSelector = AnimationSelector(self, window) #Side menu
        self.AnimationSelector.UpdateItemlist()
        
        editorFrame = Frame(window, bg=getColor('BG')) #Main frale
        editorFrame.pack(side='left', fill='both', expand=1)
        editorFrame.grid_columnconfigure(0, weight=1, uniform="group1")
        editorFrame.grid_rowconfigure(0, weight=1, uniform="group1")
        
        self.AnimationEditor = AnimationEditor(self, editorFrame)
        
        self.editorFrame = editorFrame
        self.TekkenGame = None
        self.LiveEditor = LiveEditor(self)
        
    def on_close(self):
        try: self.LiveEditor.resetInputsCode()
        except: pass
        self.LiveEditor.stop(exiting=True)
        self.window.destroy()
        
    def onAnimModification(self, dataModification=False):
        self.AnimationSelector.setSaveButtonEnabled(True)
        if dataModification: self.onFrameChange()
        
    def onFrameChange(self):
        if self.LiveEditor.liveEditing and not self.LiveEditor.runningAnimation:
            self.LiveEditor.lockCamera()
            if self.LiveEditor.running:
                self.LiveEditor.setCameraPos(*self.AnimationEditor.getFrame())
            else:
                self.AnimationEditor.previewButton['text'] = '[OFF] Live preview'
        
    def ResetCamera(self):
        self.LiveEditor.unlockCamera()
        self.LiveEditor.runningAnimation = False
        self.LiveEditor.liveEditing = False
        self.LiveEditor.liveControl = False
        self.AnimationEditor.previewButton['text'] = '[OFF] Live preview'
        self.AnimationEditor.enablePlayback()
        
    def openTekkenProcess(self):
        if not self.LiveEditor.startIfNeeded():
            message = 'Cannot open tekken process.'
            if not ctypes.windll.shell32.IsUserAnAdmin():
                message += '\nOpening Tekken\'s process might require administrator rights.'
            messagebox.showinfo('Error', message, parent=self.window)
            return False
        return True

    def toggleLivePreview(self):
        if not self.openTekkenProcess(): return
        result = self.LiveEditor.toggleLivePreview() 
        frameData, relativity = self.AnimationEditor.getFrame()
        self.AnimationEditor.previewButton['text'] = "[%s] Live preview" % ("ON" if result else "OFF")
        if result and frameData != None:
            self.LiveEditor.lockCamera()
            self.LiveEditor.setCameraPos(frameData, relativity)
        
    def toggleLiveControl(self):
        if not self.openTekkenProcess(): return
        result = self.LiveEditor.toggleLiveControl() 
        self.AnimationEditor.liveControlButton['text'] = "[%s] Live control" % ("ON" if result else "OFF")
        if result:
            newThread = threading.Thread(target=self.LiveEditor.liveControlLoop)
            newThread.start()
        
    def SaveFile(self):
        if self.AnimationEditor.Animation == None: return
        with open(dataPath + self.AnimationEditor.Animation.filename, "w") as f:
            for group in self.AnimationEditor.Animation.groups:
                line = "[%s]\n" % (group['name'])
                line += "[" + (", ".join(["%s=%d" % (key, group[key]) for key in groupKeys])) + "]\n"
                f.write(line)
                for frame in group['frames']:
                    line = ",".join([str(frame[field]) for field in frameFields])
                    f.write(line + "\n")
            self.AnimationSelector.setSaveButtonEnabled(False)
        
    def LoadAnimation(self, filename):
        LoadedAnim = None
        try:
            LoadedAnim = Animation(filename=filename)
        except:
            messagebox.showinfo('Error', 'Error importing the animation', parent=self.window)
            return
        self.AnimationEditor.LoadAnimation(LoadedAnim)
        #self.AnimationSelector.hide()
                
            
    def PlayAnimation(self, startingGroup=0, singleGroup=False):
        if not self.openTekkenProcess(): return
        if self.LiveEditor.runningAnimation: return messagebox.showinfo('Error', 'An animation is already playing', parent=self.window)
        
        self.AnimationEditor.disablePlayback()
        cachedGroups = self.AnimationEditor.Animation.calculateCachedFrames(startingGroup, singleGroup)
        newThread = threading.Thread(target=self.LiveEditor.playAnimation, args=(cachedGroups,))
        newThread.start()
            
    def setTitle(self, label = ""):
        title = "TekkenCameraAnimator %s" % (editorVersion)
        if label != "":
            title += " - " + label
        self.window.wm_title(title) 
        

if __name__ == "__main__":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('kilo.TekkenCameraAnimator')
    app = GUI_TekkenCameraAnimator()
    app.window.mainloop()

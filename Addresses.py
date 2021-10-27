# Python 3.6.5

import win32api, ctypes
import win32gui
import win32process
import win32con
from ctypes import wintypes as w
from win32com.client import GetObject
from re import findall, match

kernel32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi
    
class MODULEINFO(ctypes.Structure):
    _fields_ = [
        ("lpBaseOfDll", ctypes.c_void_p),
        ("SizeOfImage", w.DWORD),
        ("EntryPoint", ctypes.c_void_p),
    ]
    
GetModuleInformation = psapi.GetModuleInformation 
GetModuleInformation.restype = w.BOOL
GetModuleInformation.argtypes = [w.HANDLE, w.HMODULE, ctypes.POINTER(MODULEINFO), w.DWORD]

class AddressFile:
    def __init__(self, path=None, data=None):
        self.addr = {}
        
        self.path = path
        self.moduleAddr = None
        
        if self.path:
            self.reloadValues()
        elif data:
            self.readData(data)
            
    def __getitem__(self, item):
        return self.addr[item]
        
    def readData(self, data):
        self.data = data
        for line in data.split("\n"):
            line = line.strip()
            if len(line) == 0 or line[0] == "#":
                continue
            name, _ = findall('^([a-zA-Z0-9\_\-]+)( *= *)', line)[0]
            value = line[len(name + _):].split('#')[0]
            
            if value.find(",") != -1: #pointer path
                values = value.split(",")
                moduleRelative = values[0][0] == "+"
                values = [int(f, 16) for f in values]
                self.addr[name] = moduleRelative, values[0], values[1:]
            else:
                if match('\+0(x|X)[0-9a-fA-F]+', value): #relative to module addr
                    value = 1, int(value, 16), []
                elif match('-?0(x|X)[0-9a-fA-F]+', value):
                    value = int(value, 16)
                elif match('-?[0-9]+', value):
                    value = int(value, 10)
                else:
                    value = value.strip()
            
                self.addr[name] = value
                
    def applyModuleAddress(self, addr, pointerPathFunction):
        self.moduleAddr = addr
        
        for key in self.addr:
            if type(self.addr[key]) == tuple:
                valueType, value, ptrPath = self.addr[key]
                calculatedAddress = self.moduleAddr + value if valueType == 1 else value
                
                if len(ptrPath) > 0: #relative to main module
                    self.addr[key] = pointerPathFunction(calculatedAddress, ptrPath)
                else:
                    self.addr[key] = calculatedAddress
        
    def reloadValues(self):
        try:
            with open(self.path, "r") as f:
                self.readData(f.read())
                if self.moduleAddr != None:
                    try:
                        self.applyModuleAddress(self.moduleAddr)
                    except:
                        pass
        except Exception as e:
            print(e)
            print("Could not load game_addresses.txt properly")

game_addresses = AddressFile("game_addresses.txt")

    
class GameClass:
    def __init__(self, processName):
        self.PID = 0
        self.PROCESS = None
        self.windowTitle = None
        
        wmi = GetObject('winmgmts:')
        for p in wmi.InstancesOf('win32_process'):
            if p.Name == processName:  
                self.PID = int(p.Properties_('ProcessId'))
            
        if self.PID == 0:
            raise Exception("Couldn't find process \"%s\"" % (processName))
    
        self.PROCESS = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, 0, self.PID)
        self.handle = self.PROCESS.handle
        
        self.getWindowTitle()
        
        self.setModuleAddr(processName)
        if self.moduleAddr == None:
            self.setModuleAddr(".exe") #finds first module whose name ends in .exe

    def applyModuleAddress(self, addressDict):
        addressDict.applyModuleAddress(self.moduleAddr, self.readPointerPath) #used for addresses relative to tekken's main module, mainly useful for tekken 7
        
    def setModuleAddr(self, name):
        module_handles = win32process.EnumProcessModules(self.PROCESS)
        
        for m in module_handles:
            filename = win32process.GetModuleFileNameEx(self.PROCESS, m)
            if filename.endswith(name):
                self.moduleAddr = m
                
                module_info = MODULEINFO()
                res = GetModuleInformation(self.handle, m, ctypes.byref(module_info), ctypes.sizeof(module_info))
                
                self.moduleSize = module_info.SizeOfImage if res != 0  else None
                return
        self.moduleSize = None
        self.moduleAddr = None

    def enumWindowsProc(self, hwnd, lParam):
        if win32process.GetWindowThreadProcessId(hwnd)[1] == lParam:
            text = win32gui.GetWindowText(hwnd)
            if text and (win32api.GetWindowLong(hwnd, win32con.GWL_STYLE) & win32con.WS_VISIBLE):
                self.windowTitle = text
                return
        
    def getWindowTitle(self):
        win32gui.EnumWindows(self.enumWindowsProc, self.PID)
        return self.windowTitle

    def readBytes(self, addr, bytes_length):
        buff = ctypes.create_string_buffer(bytes_length)
        bufferSize = ctypes.sizeof(buff)
        bytesRead = ctypes.c_ulonglong(0)
        
        if ReadProcessMemory(self.handle, addr, buff, bufferSize, ctypes.byref(bytesRead)) != 1:
            raise Exception('Could not read memory addr "%x" (%d bytes): invalid address or process closed?' % (addr, bytes_length))

        return bytes(buff)
    
    def writeBytes(self, addr, value):
        return WriteProcessMemory(self.handle, addr, bytes(value), len(value), None)

    def readInt(self, addr, bytes_length=4, endian='little'):
        return int.from_bytes(self.readBytes(addr, bytes_length), endian)
        
    def writeInt(self, addr, value, bytes_length=0):
        if bytes_length <= 0:
            bytes_length = value.bit_length() + 7 // 8
        return self.writeBytes(addr, value.to_bytes(bytes_length, 'little'))
        
    def readPointerPath(self, currAddr, ptrlist):
        for ptr in ptrlist:
            old = currAddr
            currAddr = self.readInt(currAddr, 8) + ptr
        return currAddr
        
    def aobScan(self, toSearch, aligned=True): #This is terribly slow and should not be used until improvements to speed.
        #aobScan("48 89 91 ?? ?? 00 00")
        currAddr = self.moduleAddr
        moduleEnd = self.moduleAddr + self.moduleSize
        
        toSearch = ''.join(t.upper() for t in toSearch if t.isalnum() and ord(t.upper()) <= 70)
        hexNumbers = []
        for i in range(0, len(toSearch), 2):
            try:
                hexNumbers.append(int(toSearch[i:i+2], 16))
            except:
                hexNumbers.append(None)
        
        if aligned and currAddr % 4 != 0: currAddr += (4 - currAddr % 4) #4 bytes alignment
        step = 1 if not aligned else 4
        
        while currAddr < moduleEnd:
            b = self.readBytes(currAddr, 4)
            
            if b[0] == hexNumbers[0]:
                found = True
                for orig, comp in zip(hexNumbers, b):
                    if orig != comp and orig != None:
                        found = False
                        break
                if found:
                    return currAddr
            currAddr += step
        
        return None
        
def bToInt(data, offset, length, endian='little'):
    return int.from_bytes(data[offset:offset + length], endian)
    
    
ReadProcessMemory = kernel32.ReadProcessMemory
ReadProcessMemory.argtypes = [w.HANDLE, w.LPCVOID, w.LPVOID, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
ReadProcessMemory.restype = w.BOOL
        
WriteProcessMemory = kernel32.WriteProcessMemory
WriteProcessMemory.restype = w.BOOL
WriteProcessMemory.argtypes = [w.HANDLE, w.LPVOID, w.LPCVOID, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t) ]

VirtualAllocEx = kernel32.VirtualAllocEx
VirtualAllocEx.restype = w.LPVOID
VirtualAllocEx.argtypes = (w.HANDLE, w.LPVOID, w.DWORD, w.DWORD, w.DWORD)

VirtualFreeEx  = kernel32.VirtualFreeEx 
VirtualFreeEx.restype = w.LPVOID
VirtualFreeEx.argtypes = (w.HANDLE, w.LPVOID, w.DWORD, w.DWORD)

GetLastError = kernel32.GetLastError
GetLastError.restype = ctypes.wintypes.DWORD
GetLastError.argtypes = ()

MEM_RESERVE = 0x00002000
MEM_COMMIT = 0x00001000
MEM_DECOMMIT = 0x4000
MEM_RELEASE = 0x8000
PAGE_EXECUTE_READWRITE = 0x40
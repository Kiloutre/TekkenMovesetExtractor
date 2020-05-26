# Python 3.6.5

import win32api, ctypes
import win32gui
import win32process
import win32con
from ctypes import wintypes as w
from win32com.client import GetObject
from re import findall

kernel32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi

class AddressFile:
    def __init__(self, path):
        self.addr = {}
        self.path = path
        
        self.reloadValues()
        
    def reloadValues(self):
        with open(self.path, "r") as f:
            try:
                for line in f:
                    line = line.strip()
                    if len(line) == 0 or line[0] == "#":
                        continue
                    name, addr, _ = findall('([a-z0-9\_\-]+) += +(-?(0x)?[a-fA-F0-9]+)', line)[0]
                    self.addr[name] = int(addr, 16)
            except Exception as e:
                print(e)
                print("Invalid game_addresses.txt format at line.")
                print("Last line: ", line)
    
class GameClass:
    def __init__(self, processName):
        self.PID = 0
        self.PROCESS = None
        
        wmi = GetObject('winmgmts:')
        for p in wmi.InstancesOf('win32_process'):
            if p.Name == processName:  
                self.PID = int(p.Properties_('ProcessId'))
            
        if self.PID == 0:
            raise Exception("Couldn't find process \"%s\"" % (processName))
    
        self.PROCESS = win32api.OpenProcess(0x1F0FFF, 0, self.PID)
        self.handle = self.PROCESS.handle
        
        self.getWindowTitle()


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

game_addresses = AddressFile("game_addresses.txt")
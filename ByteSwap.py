# Python 3.6.5
import sys

def swapArrBytes(arr, index1, index2, len):
    for i in range(len):
        arr[index1 + i], arr[index2 + i] = arr[index2 + i], arr[index1 + i]
        
def swapBytes(arr, index1, index2):
    swapArrBytes(arr, index1, index2, 1)
        
def reverseEndian(arr, index, len):
    byteList = arr[index:index+len][::-1]
    for i, b in enumerate(byteList):
        arr[index + i] = b 
        
def bToInt(data, offset, length, order='little'):
    return int.from_bytes(bytes(data[offset:offset+length]), order)
    
def getT5AnimationLength(fb):
    return fb[0]
    
def getAnimationLength(fb):
    if fb[0] == 0xc8:
        return bToInt(fb, 4, 4)
    elif fb[0] == 0x64:
        return bToInt(fb, bToInt(fb, 2, 2) * 2 + 4, 2)
    else:
        return 0xffffffff

def SwapMotaBytes(fb):
    anim = AnimData(fb)
    if len(anim.data) >= 4 and bytes(anim.data[0:4]).decode('ascii') == 'MOTA':
        anim.swapBytes(4, 5)
        anim.swapBytes(6, 7)
        
        anim.reverseEndian(8, 4)
        anim.reverseEndian(0xc, 4)
        iVar1 = anim.bToInt(0xc, 4)
        uVar2 = iVar1
        uVar3 = 0
        if iVar1 != 0:
            while True:
                anim.reverseEndian(uVar3 * 4 + 0x14, 4)
                uVar1 = anim.bToInt(uVar3 * 4 + 0x14, 4)
                anim.SwapAnimationBytes(offset=uVar1)
                uVar1 = uVar3 + 1
                uVar3 = uVar1
                if uVar1 >= anim.bToInt(0xc, 4):
                    break
        return bytes(anim.data)
    else:
        return fb

class AnimData:
    def __init__(self, data):
        self.data = list(data)
        self.offset = 0
        
        if data[0] != 0x64 and data[0] != 0xC8 and (data[0] << 8) & 0xFFFF != 0x64:
            self.animType = 1 + (data[1] == 0xC8) # 1 = 0x64, 2 = 0xC8
        else:
            self.animType = 0 #Byteswapped already
        
    def swapBytes(self, idx1, idx2):
        byte1, byte2 = self.byte(idx1), self.byte(idx2)
        self.setByte(idx1, byte2)
        self.setByte(idx2, byte1)
        
    def bToInt(self, offset, length, order='little'):
        offset += self.offset
        return int.from_bytes(bytes(self.data[offset:offset+length]), order)
        
    def reverseEndian(self, idx, len):
        idx += self.offset
        byteList = self.data[idx:idx+len][::-1]
        for b in byteList:
            self.data[idx] = b 
            idx += 1
            
    def setByte(self, idx, value):
        self.data[self.offset + idx] = value
            
    def setByteFrom(self, dest, src):
        self.setByte(dest, self.byte(src))
        
    def int(self, idx):
        return self.bToInt(idx, 4)
        
    def short(self, idx):
        return self.bToInt(idx, 2)
        
    def byte(self, idx):
        return self.data[self.offset + idx]
        
    def SwapC8Anim(self):
        self.swapBytes(0x0, 0x1)
        self.swapBytes(0x2, 0x3)
        
        ofst = 4
        bVar1 = self.bToInt(ofst, 1)
        bVar2 = self.bToInt(2, 2)
        self.setByteFrom(ofst, 7)
        self.setByte(7, bVar1)
        self.swapBytes(5, 6)
        
        uVar3 = self.bToInt(ofst, 4)
        ofst2 = 8
        
        if bVar2 != 0: 
            for i in range(bVar2 - 1, -1, -1):
                self.swapBytes(ofst2, ofst2+3)
                self.swapBytes(ofst2+1, ofst2+2)
                ofst2 += 4
                
        if uVar3 != 0:
            while uVar3 != 0:
                uVar4 = bVar2
                while uVar4 != 0:
                    self.swapBytes(ofst2, ofst2+3)
                    self.swapBytes(ofst2+1, ofst2+2)
                    self.swapBytes(ofst2+4, ofst2+7)
                    self.swapBytes(ofst2+5, ofst2+6)
                    self.swapBytes(ofst2+8, ofst2+0xb)
                    self.swapBytes(ofst2+9, ofst2+10)
                    ofst2 += 0xc
                    uVar4 -= 1
                uVar3 -= 1
        return bytes(self.data[self.offset:])
        
    def Swap64Anim(self):
        auStack536 = [0] * 256

        self.swapBytes(0x0, 0x1)
        self.swapBytes(0x2, 0x3)
        
        uVar2 = self.bToInt(2, 2)
        ofst = 4
        
        if 0xff < uVar2:
            return None
        
        for i in range(uVar2):
            self.swapBytes(ofst, ofst+1)
            auStack536[i] = self.bToInt(ofst, 2)
            ofst += 2
            
        self.swapBytes(ofst, ofst+1)
        uVar3 = self.bToInt(ofst, 2)
        self.swapBytes(ofst+4, ofst+5)
        ofst2 = ofst + 6
        
        max = self.bToInt(ofst + 4, 2)
        if max != 0: 
            for i in range(max - 1, -1, -1):
                self.swapBytes(ofst2, ofst2+3)
                self.swapBytes(ofst2+1, ofst2+2)
                ofst2 += 4
        
        
        tlen = 0
        
        if uVar3 != 0:
            if uVar2 != 0:
                tlen = uVar2
                for i in range(uVar2):
                    bVar1 = self.bToInt(ofst2, 1)
                    if auStack536[i] - 4 < 4:
                        self.setByteFrom(ofst2, ofst2 + 1)
                        self.setByte(ofst2+1, bVar1)
                        self.swapBytes(ofst2+2, ofst2+3)
                        self.swapBytes(ofst2+4, ofst2+5)
                        ofst2 += 6
                    else:
                        self.setByteFrom(ofst2, ofst2 + 3)
                        self.setByte(ofst2+3, bVar1)
                        self.swapBytes(ofst2+1, ofst2+2)
                        self.swapBytes(ofst2+4, ofst2+7)
                        self.swapBytes(ofst2+6, ofst2+5)
                        self.swapBytes(ofst2+0xb, ofst2+8)
                        self.swapBytes(ofst2+0xa, ofst2+9)
                        ofst2 += 0xc
            uVar6 = (uVar3 + 0xe) >> 4
            if uVar6 != 0:
                ofst2 = ofst2+2
                uVar9 = uVar6
                while uVar9 > 0:
                    self.swapBytes(ofst2-2, ofst2+1)
                    self.swapBytes(ofst2-1, ofst2)
                    ofst2 += 4
                    uVar9 -= 1
        return bytes(self.data[self.offset:])
        
    def SwapAnimationBytes(self, offset=0):
        self.offset = offset
        if self.animType == 1:
            retVal = self.Swap64Anim()
        elif self.animType == 2:
            retVal = self.SwapC8Anim()
        else:
            retVal = None
        self.offset = 0
        return retVal
            
def SwapAnimBytes(animData):
    animation = AnimData(animData)
    return animation.SwapAnimationBytes()
        
def sadamitsuParse(filename):
    with open(filename, "r") as f:
        lines = [line[11:] for line in f]
        byteList = []
        for line in lines:
            for i in range(4):
                val = int(line[i * 2:i * 2 + 2], 16)
                byteList.append(val)
        return byteList
    return None
    
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("No filename provided")
        sys.exit(1)
        
    fileBytes = sadamitsuParse(sys.argv[1])
    fileBytes = SwapAnimBytes(fileBytes)
    
    with open(sys.argv[1][:-4] + "_new.bin", "wb") as f:
        f.write(bytes(fileBytes))
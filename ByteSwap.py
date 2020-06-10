# Python 3.6.5
import sys

def swapArrBytes(arr, index1, index2, len):
    for i in range(len):
        arr[index1 + i], arr[index2 + i] = arr[index2 + i], arr[index1 + i]
        
def bToInt(data, offset, length, order='little'):
    return int.from_bytes(bytes(data[offset:offset+length]), order)

def SwapAnimBytesC8(fb):
    swapArrBytes(fb, 0x0, 0x1, 1)
    swapArrBytes(fb, 0x2, 0x3, 1)
    
    ofst = 4
    bVar1 = bToInt(fb, ofst, 1)
    bVar2 = bToInt(fb, 2, 2)
    fb[ofst] = fb[7]
    fb[7] = bVar1
    swapArrBytes(fb, 5, 6, 1)
    
    uVar3 = bToInt(fb, ofst, 4)
    ofst2 = 8
    
    if bVar2 != 0: 
        for i in range(bVar2 - 1, -1, -1):
            swapArrBytes(fb, ofst2, ofst2+3, 1)
            swapArrBytes(fb, ofst2+1, ofst2+2, 1)
            ofst2 += 4
            
    if uVar3 != 0:
        while uVar3 != 0:
            uVar4 = bVar2
            while uVar4 != 0:
                swapArrBytes(fb, ofst2, ofst2+3, 1)
                swapArrBytes(fb, ofst2+1, ofst2+2, 1)
                swapArrBytes(fb, ofst2+4, ofst2+7, 1)
                swapArrBytes(fb, ofst2+5, ofst2+6, 1)
                swapArrBytes(fb, ofst2+8, ofst2+0xb, 1)
                swapArrBytes(fb, ofst2+9, ofst2+10, 1)
                ofst2 += 0xc
                uVar4 -= 1
            uVar3 -= 1
    return bytes(fb)

def SwapAnimBytes(fb):
    fb = list(fb)
    if fb[0] != 0x64 and fb[0] != 0xC8 and (fb[0] << 8) & 0xFFFF != 0x64:
        if fb[1] == 0xC8:
            return SwapAnimBytesC8(fb)
            
        auStack536 = [0] * 256

        swapArrBytes(fb, 0x0, 0x1, 1)
        swapArrBytes(fb, 0x2, 0x3, 1)
        
        uVar2 = bToInt(fb, 2, 2)
        ofst = 4
        
        if 0xff < uVar2:
            return None
        
        for i in range(uVar2):
            swapArrBytes(fb, ofst, ofst+1, 1)
            auStack536[i] = bToInt(fb, ofst, 2)
            ofst += 2
            
        swapArrBytes(fb, ofst, ofst+1, 1)
        uVar3 = bToInt(fb, ofst, 2)
        swapArrBytes(fb, ofst+4, ofst+5, 1)
        ofst2 = ofst + 6
        
        max = bToInt(fb, ofst + 4, 2)
        if max != 0: 
            for i in range(max - 1, -1, -1):
                swapArrBytes(fb, ofst2, ofst2+3, 1)
                swapArrBytes(fb, ofst2+1, ofst2+2, 1)
                ofst2 += 4
        
        if uVar3 != 0:
            if uVar2 != 0:
                for i in range(uVar2):
                    bVar1 = bToInt(fb, ofst2, 1)
                    if auStack536[i] - 4 < 4:
                        fb[ofst2] = fb[ofst2 + 1]
                        fb[ofst2+1] = bVar1
                        swapArrBytes(fb, ofst2+2, ofst2+3, 1)
                        swapArrBytes(fb, ofst2+4, ofst2+5, 1)
                        ofst2 += 6
                    else:
                        fb[ofst2] = fb[ofst2 + 3]
                        fb[ofst2+3] = bVar1
                        swapArrBytes(fb, ofst2+1, ofst2+2, 1)
                        swapArrBytes(fb, ofst2+4, ofst2+7, 1)
                        swapArrBytes(fb, ofst2+6, ofst2+5, 1)
                        swapArrBytes(fb, ofst2+0xb, ofst2+8, 1)
                        swapArrBytes(fb, ofst2+0xa, ofst2+9, 1)
                        ofst2 += 0xc
            uVar6 = (uVar3 + 0xe) >> 4
            if uVar6 != 0:
                ofst2 = ofst2+2
                uVar9 = uVar6
                while uVar9 > 0:
                    swapArrBytes(fb, ofst2-2, ofst2+1, 1)
                    swapArrBytes(fb, ofst2-1, ofst2, 1)
                    ofst2 += 4
                    uVar9 -= 1
        return bytes(fb)
    else:
        return None
        
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
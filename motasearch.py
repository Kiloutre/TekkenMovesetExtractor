import os

"""
The value format is 0xYZZ
Here Y is animation number and ZZ is how many frames should it take to blend into that position 
For example, Heihachi's stance has left hand mota (0x8429) value 0x114 
Here 0x100 means the animation number and it takes 0x14 (dec 20) frames for it to blend into that successfully 

290 = ??
298 = hands anim
"""

def bToInt(data, offset, length, endian='little'):
    return int.from_bytes(data[offset:offset + length], endian)
    
files = [f for f in os.listdir("extracted_chars\\.") if f.startswith("t7")]
    
for file in files:
    filename = "extracted_chars\\" + file + "\\mota_5.bin"
    print(file)
    f = open(filename, "rb")
    fdata = f.read()
    f.close()

    endianByte = fdata[5]
    endian = 'big' if endianByte == 1 else 'little'

    btoint = lambda d, o, l, e=endian: bToInt(d, o, l, e)

    animCountOffset = 0xC
    offsetList = 0x14

    animCount = bToInt(fdata, animCountOffset, 4, endian)
    print(animCount, "anims")

    for anim_idx in range(animCount):
        o = offsetList + anim_idx * 4
        
        animOffset = bToInt(fdata, o, 4, endian)
        
        if endianByte == 1: animOffset += 1
        
        firstbyte = bToInt(fdata, animOffset, 1)
        
        
        if firstbyte == 0xC8:  print("%d: %x - 0x%x" % (anim_idx, animOffset, firstbyte))
    print()
    print()
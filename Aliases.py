

offset98_aliases = [
    { 'id': 301989921, 'tag2_id': 4296 },
    { 'id': 67108864, 'tag2_id': 32 },
    { 'id': 16419, 'tag2_id': 4224 },
    { 'id': 33554465, 'tag2_id': 4288 },
    { 'id': 335544320, 'tag2_id': 40 },
    { 'id': 33554467, 'tag2_id': 4544 },
    { 'id': 33554432, 'tag2_id': 64 },
    { 'id': 33554464, 'tag2_id': 4160 },
    { 'id': 4194339, 'tag2_id': 536875392 },
    { 'id': 35, 'tag2_id': 16419 },
    { 'id': 335544323, 'tag2_id': 424 },
    { 'id': 67108865, 'tag2_id': 160 },
    { 'id': 268435456, 'tag2_id': 8 },
    { 'id': 335544325, 'tag2_id': 680 },
    { 'id': 2483027973, 'tag2_id': 681 },
    { 'id': 268435460, 'tag2_id': 520 },
    { 'id': 268435461, 'tag2_id': 648 },
    { 'id': 5, 'tag2_id': 640 },
    { 'id': 67108869, 'tag2_id': 544 },
    { 'id': 335544327, 'tag2_id': 680 },
    { 'id': 335544324, 'tag2_id': 552 },
    { 'id': 67108868, 'tag2_id': 544 },
    { 'id': 4, 'tag2_id': 512 },
    { 'id': 268435489, 'tag2_id': 4232 },
    { 'id': 268435457, 'tag2_id': 136 },
    { 'id': 33, 'tag2_id': 16419 },
    { 'id': 201326592, 'tag2_id': 48 },
    { 'id': 469762048, 'tag2_id': 56 },
    { 'id': 4227105, 'tag2_id': 541069440 },
    { 'id': 402653184, 'tag2_id': 24 },
    { 'id': 402653185, 'tag2_id': 152 },
    { 'id': 402653217, 'tag2_id': 4248 },
    { 'id': 134217761, 'tag2_id': 4240 },
    { 'id': 268451873, 'tag2_id': 2101384 },
    { 'id': 402653216, 'tag2_id': 4120 },
    { 'id': 268435488, 'tag2_id': 4104 },
    { 'id': 32, 'tag2_id': 4096 },
    { 'id': 1, 'tag2_id': 128 },
    { 'id': 268435493, 'tag2_id': 4744 },
    { 'id': 268435495, 'tag2_id': 5000 },
    { 'id': 37, 'tag2_id': 4736 },
    { 'id': 268435492, 'tag2_id': 4616 },
    { 'id': 36, 'tag2_id': 4608 },
    { 'id': 402653232, 'tag2_id': 6168 },
    { 'id': 48, 'tag2_id': 6144 },
    { 'id': 335544321, 'tag2_id': 168 },
    { 'id': 515, 'tag2_id': 65920 },
    { 'id': 402685985, 'tag2_id': 4198552 },
    { 'id': 268468257, 'tag2_id': 4198536 },
    { 'id': 32801, 'tag2_id': 4198528 },
    { 'id': 34849, 'tag2_id': 4460672 },
    { 'id': 67108866, 'tag2_id': 67108864 },
    { 'id': 67108867, 'tag2_id': 67108864 },
    { 'id': 67371008, 'tag2_id': 33554464 },
    { 'id': 335806464, 'tag2_id': 33554472 },
    { 'id': 134250529, 'tag2_id': 4198544 },
    { 'id': 268439585, 'tag2_id': 528520 },
    { 'id': 134217729, 'tag2_id': 144 },
    { 'id': 65, 'tag2_id': 8320 },
    { 'id': 66, 'tag2_id': 8448 },
    { 'id': 64, 'tag2_id': 8192 },
    { 'id': 167772195, 'tag2_id': 4560 },
    { 'id': 135266336, 'tag2_id': 134221840 },
    { 'id': 134250531, 'tag2_id': 4198800 },
    { 'id': 138412064, 'tag2_id': 536875024 },
    { 'id': 32800, 'tag2_id': 4198400 },
    { 'id': 32803, 'tag2_id': 4198784 },
    { 'id': 4194336, 'tag2_id': 536875008 },
]

requirements = [
    {
        'id': 881,
        'tag2_id': 690,
        'description': 'Requirements end'
    },
    {
        'id': 44,
        'tag2_id': 46,
        'description': 'Counterhit'
    },
    {
        'id': 135,
        'tag2_id': 133,
        'description': 'Death'
    },
    {
        'id': 68,
        'tag2_id': 65,
        'description': 'Incoming high'
    },
    {
        'id': 126,
        'tag2_id': 124,
        'description': 'Enemy downed'
    },
    {
        'id': 614,
        'tag2_id': 467,
        'description': 'Screw/Bound'
    },
    {
        'id': 615,
        'tag2_id': 466,
        'description': 'Juggle'
    },
    {
        'id': 80,
        'tag2_id': 77,
        'description': 'Back left spin'
    },
    {
        'id': 81,
        'tag2_id': 78,
        'description': 'Back right spin'
    },
    {
        'id': 47,
        'tag2_id': 49,
        'description': 'Blocked'
    },
    {
        'id': 33990,
        'tag2_id': 33531,
        'description': 'UNKNOWN (Jin 4 -> 32769)'
    }
]

def getTag2_offset98Alias(id):
    for r in offset98_aliases:
        if r['tag2_id'] == id:
            return r['id']
    return 0#id

def getRequirement(id):
    for r in requirements:
        if r['id'] == id:
            return r
    return None

def getTag2Requirement(id):
    for r in requirements:
        if r['tag2_id'] == id:
            return r
    return None
    
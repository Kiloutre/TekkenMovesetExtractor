

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
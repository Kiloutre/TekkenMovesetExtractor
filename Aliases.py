
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
        'id': 48,
        'tag2_id': 51,
        'description': 'Blocked2'
    },
    {
        'id': 33990,
        'tag2_id': 33531,
        'description': 'UNKNOWN (Jin 4 -> 32769)'
    },
    {
        'id': 216,
        'tag2_id': 199,
        'description': 'UNKNOWN (sDw_AIR00_)'
    },
    {
        'id': 352,
        'tag2_id': 313,
        'description': 'UNKNOWN (sDw_AIR00_)'
    },
    {
        'id': 32934,
        'tag2_id': 32918,
        'description': 'UNKNOWN (sDw_AIR00_)'
    },
    {
        'id': 182,
        'tag2_id': 165,
        'description': 'UNKNOWN (sDw_AIR00_)'
    },
    {
        'id': 148,
        'tag2_id': 146,
        'description': 'UNKNOWN (Co_UkemL0D)'
    },
    {
        'id': 149,
        'tag2_id': 147,
        'description': 'UNKNOWN (Co_UkemR0D)'
    },
    {
        'id': 146,
        'tag2_id': 144,
        'description': 'UNKNOWN (Co_UkemR0D)'
    },
    {
        'id': 147,
        'tag2_id': 145,
        'description': 'UNKNOWN (Co_UkemL0D)'
    },
    {
        'id': 84,
        'tag2_id': 81,
        'description': 'UNKNOWN (Co_UkerB00)'
    },
    {
        'id': 87,
        'tag2_id': 84,
        'description': 'UNKNOWN (32787)'
    },
    {
        'id': 36,
        'tag2_id': 36,
        'description': 'UNKNOWN (sSTEP_00B)'
    },
    {
        'id': 251,
        'tag2_id': 232,
        'description': 'UNKNOWN (sSTEP_00B)'
    },
    {
        'id': 150,
        'tag2_id': 148,
        'description': 'UNKNOWN (sSTEP_01L)'
    },
    {
        'id': 151,
        'tag2_id': 149,
        'description': 'UNKNOWN (sSTEP_01R)'
    },
    {
        'id': 289,
        'tag2_id': 262,
        'description': 'UNKNOWN (sSTEP_01R)'
    },
    {
        'id': 33716,
        'tag2_id': 33375,
        'description': 'UNKNOWN (sBL_mL00 / sBL_mR00)'
    },
    {
        'id': 846,
        'tag2_id': 665,
        'description': 'UNKNOWN (sBL_mL00 / sBL_mR00)',
        'param_alias': { #id, tag2_id
            7043: 6799,
            6887: 6661,
            6941: 6737,
            7019: 6773,
            7023: 6777
        }
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
    
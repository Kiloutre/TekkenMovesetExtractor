from copy import deepcopy
import sys
import json
from Aliases import fillAliasesDictonnaries, getMoveExtrapropAlias, getRequirementAlias
from moveDependencies import MoveDependencies, reaction_keys


def loadJson(filepath):
    try:
        with open(filepath) as f:
            data = json.load(f)
    except FileNotFoundError:
        data = None
    return data


def saveJson(filename, movesetData):
    with open(filename, "w") as f:
        json.dump(movesetData, f, indent=4)
    return


def search(pat, txt):
    M = len(pat)
    N = len(txt)
    for i in range(N - M + 1):
        j = 0
        while(j < M):
            if (txt[i + j] != pat[j]):
                break
            j += 1
        if (j == M):
            return i
    return -1


def isSame(moveset1, moveset2):
    return moveset1['version'] == moveset2['version'] \
        and moveset1['tekken_character_name'] == moveset2['tekken_character_name'] \
        and moveset1['character_name'] == moveset2['character_name'] \
        and moveset1['creator_name'] == moveset2['creator_name']


def isSameInDifferentGame(moveset1, moveset2):
    return moveset1['tekken_character_name'] == moveset2['tekken_character_name'] \
        and moveset1['creator_name'] == moveset2['creator_name']


def getMoveName(moveset, move_id: int):
    if move_id >= 0x8000:
        move_id = moveset['aliases'][move_id-0x8000]
    return moveset['moves'][move_id]['name']


def getMoveID(moveset, movename: str, start=0):
    n = len(moveset['moves'])
    start = 0 if (start >= n or start < 0) else start
    for i in range(start, n):
        if moveset['moves'][i]['name'] == movename:
            return i
    return -1


def getVoiceclipList(moveset, idx: int) -> list:
    list = []
    i = idx
    while True:
        voiceclip = moveset['voiceclips'][i]
        list.append(voiceclip)
        if voiceclip == 4294967295:
            break
        i += 1
    return list


def isLast(prop):
    return 0 == prop['id'] and 0 == prop['type'] and 0 == prop['value']


def getExtrapropsList(moveset, idx: int) -> list:
    list = []
    while True:
        prop = moveset['extra_move_properties'][idx]
        list.append(prop)
        if isLast(prop):
            break
        idx += 1
    return list


def getInputSequence(moveset, idx: int) -> list:
    seq = deepcopy(moveset['input_sequences'][idx])
    start = seq['extradata_idx']
    end = start + seq['u2']
    list = moveset['input_extradata'][start: end]
    seq['inputs'] = list
    return seq


def getReqList(moveset, idx: int) -> list:
    list = []
    while True:
        requirement = deepcopy(moveset['requirements'][idx])
        req, param = getRequirementAlias(
            moveset['version'], requirement['req'], requirement['param'])
        requirement['req'] = req
        requirement['param'] = param
        list.append(requirement)
        if (requirement['req'] == 881):  # TODO: Replace 881 with game end req val
            break
        idx += 1
    return list


# Find idx of the cancel extradata. Take source extradata value and find it's index in destination moveset
def findExtradataIndex(extradata_value: int, moveset: dict):
    for i, j in enumerate(moveset['cancel_extradata']):
        if j == extradata_value:
            return i

    # Add if it doesn't exist, add it
    moveset['cancel_extradata'].append(extradata_value)
    return len(moveset['cancel_extradata'])


class MoveCopier:
    def __init__(self, sourceMvst: dict, dstMvst: dict, dependency_name_id: dict, dependency_id_name: dict):
        if sourceMvst == None:
            raise BaseException('Source Moveset Empty')
        if dstMvst == None:
            raise BaseException('Destination Moveset Empty')
        if isSame(sourceMvst, dstMvst):
            raise BaseException('Source & Destination movesets are the same')
        if dstMvst['version'] != 'Tekken7':
            raise BaseException(
                'Destination Moveset is Not a Tekken 7 moveset. version =', dstMvst['version'])

        self.__srcMvst = sourceMvst
        self.__dstMvst = dstMvst
        self.__dependency_name_id = dependency_name_id
        self.__dependent_id_name = dependency_id_name

    def CopyAllDependentMoves(self):
        fillAliasesDictonnaries(self.__srcMvst['version'])
        indexesOfAddedMoves = []

        # Iterate the dictionary
        for _, src_move_id in enumerate(self.__dependent_id_name):
            # Create the move and get the ID
            new_move_id = self.softCopyMove(src_move_id)

            # Storing index of this newly created move
            indexesOfAddedMoves.append(new_move_id)
            print('Move Added: %s. Index = %d' %
                  (self.__dependent_id_name[src_move_id], indexesOfAddedMoves[-1]))

            # Creating extraprops list
            self.createExtramovePropertiesList(src_move_id, new_move_id)

        # Creating secondary properties. (cancels, reactions)
        for i, src_move_id in enumerate(self.__dependent_id_name):
            # Update transition
            self.updateTransition(src_move_id, indexesOfAddedMoves[i])

            # Get source move
            src_move = self.__srcMvst['moves'][src_move_id]

            # Get new move
            new_move_id = indexesOfAddedMoves[i]
            new_move = self.__dstMvst['moves'][new_move_id]

            # if their names aren't equal, break
            if src_move['name'] != new_move['name']:
                print('move Name not equal\nSource: %s\n New: %s' %
                      (src_move['name'], new_move['name']))
                break
            else:
                print('Creating cancel list of move', new_move['name'])

            # Get cancel index of src move
            src_move_cancel_idx = src_move['cancel_idx']

            # Set index to last cancel
            new_move_cancel_idx = len(self.__dstMvst['cancels'])

            # Copy Cancels
            size_of_new_cancel_list = self.copyCancelList(src_move_cancel_idx)

            # Assigning index to move whose cancel list was just created
            self.__dstMvst['moves'][new_move_id]['cancel_idx'] = new_move_cancel_idx

            # Adjusting rest of the cancels
            for j in range(new_move_id+1, len(self.__dstMvst['moves'])):
                self.__dstMvst['moves'][j]['cancel_idx'] += size_of_new_cancel_list

            # Creating hit conditions & reaction lists
            # new_move['hit_condition_idx'] = self.createHitCondition(
            #     src_move['hit_condition_idx'])

        return

    # Updates the transition attribute, this value may refer to a move that doesn't exist yet, so better to call this function after importing moves
    def updateTransition(self, src_move_id, new_move_id):
        new_move = self.__dstMvst['moves'][new_move_id]
        if new_move['transition'] >= 0x8000:
            return
        new_move['transition'] = getMoveID(
            self.__dstMvst, getMoveName(self.__srcMvst, new_move['transition']))
        return

    def softCopyMove(self, move_id: int):
        src_move = self.__srcMvst['moves'][move_id]

        # Creating a deep copy of Source move
        new_move = deepcopy(src_move)

        # Assigning attributes to this new move
        new_move['hit_condition_idx'] = 0
        new_move['extra_properties_idx'] = -1
        new_move['u8'] = len(self.__dstMvst['moves']) - new_move['u8_2'] + 2

        # Assigning idx
        new_move['cancel_idx'] = len(self.__dstMvst['cancels'])

        # Adding new move to end of the moves list
        self.__dstMvst['moves'].append(new_move)

        # Fixing u15
        # new_move['u15'] = convertU15(new_move['u15'])

        # Copying voice-clip
        voiceclip_idx = new_move['voiceclip_idx']
        new_move['voiceclip_idx'] = self.createNewVoiceclipList(voiceclip_idx)

        return len(self.__dstMvst['moves'])-1

    def createNewVoiceclipList(self, voiceclip_idx):
        if voiceclip_idx == -1:
            return -1
        new_list = getVoiceclipList(self.__srcMvst, voiceclip_idx)
        voiceclip_idx = len(self.__dstMvst['voiceclips'])
        for value in new_list:
            self.__dstMvst['voiceclips'].append(value)
        return voiceclip_idx

    def createExtramovePropertiesList(self, src_move_id, new_move_id):
        # Get moves
        new_move = self.__dstMvst['moves'][new_move_id]
        src_move = self.__srcMvst['moves'][src_move_id]

        # Read list of extraproperties and store them
        src_props_idx = src_move['extra_properties_idx']
        if src_props_idx == -1:
            return
        src_props_list = getExtrapropsList(self.__srcMvst, src_props_idx)

        # Create T7 equivalent of it
        new_props_list = []
        for prop in src_props_list:
            id, type, value = prop['id'], prop['type'], prop['value']
            type, id, value = getMoveExtrapropAlias(
                self.__srcMvst['version'], type, id, value)
            if id == None:
                break
            new_props_list.append({'id': id, 'type': type, 'value': value})

        # Assigning index
        new_index = len(self.__dstMvst['extra_move_properties'])
        new_move['extra_properties_idx'] = new_index
        for i in new_props_list:
            self.__dstMvst['extra_move_properties'].append(i)
        return new_index

    def createRequirementsList(self, reqList):
        idx = search(reqList, self.__dstMvst['requirements'])
        if idx == -1:
            idx = len(self.__dstMvst['requirements'])
            for req in reqList:
                self.__dstMvst['requirements'].append(req)
        return idx

    def createHitCondition(self, src_hit_idx: int) -> int:
        if src_hit_idx == 0:
            return 0
        src_reaction_list = self.__srcMvst['hit_conditions'][src_hit_idx]
        new_idx = len(self.__dstMvst['hit_conditions'])
        return new_idx

    def updateMoveID(self, new_cancel):
        if (new_cancel['command'] == 0x800b):
            return

        if new_cancel['move_id'] >= 0x8000:
            return

        new_cancel['move_id'] = getMoveID(
            self.__dstMvst, getMoveName(self.__srcMvst, new_cancel['move_id']))
        return

    def checkCommand(self, command):
        # If Group cancel, just skip it.
        # TODO: Figure out group cancel aliases and apply them
        if command == 0x800b:
            return True

        # If input sequence.
        if 0x800d <= command <= 0x81ff:
            inputSeq = getInputSequence(self.__srcMvst, command - 0x800d)
            self.createInputSequence(inputSeq)
            return True
        return False

    def createInputSequence(self, inputSeq):
        inputExtras = self.__dstMvst['input_extradata']
        last = inputExtras.pop()
        idx = len(inputExtras)
        for i in inputSeq['inputs']:
            inputExtras.append(i)
        inputExtras.append(last)
        del inputSeq['inputs']
        inputSeq['extradata_idx'] = idx
        self.__dstMvst['input_sequences'].append(inputSeq)
        return

    def copyCancelList(self, src_cancel_idx: int):
        count = 0
        while True:
            src_cancel = self.__srcMvst['cancels'][src_cancel_idx]
            new_cancel = deepcopy(src_cancel)

            # Check if it is an input sequence or group cancel
            if self.checkCommand(new_cancel['command']):
                src_cancel_idx += 1
                continue

            # Update extradata
            extradata_value = self.__srcMvst['cancel_extradata'][src_cancel['extradata_idx']]
            new_cancel['extradata_idx'] = findExtradataIndex(
                extradata_value, self.__dstMvst)

            # Update move ID
            self.updateMoveID(new_cancel)

            # Update requirement_idx
            reqList = getReqList(self.__srcMvst, src_cancel['requirement_idx'])
            new_cancel['requirement_idx'] = self.createRequirementsList(
                reqList)

            # Update the new cancel into 'cancels' list
            self.__dstMvst['cancels'].append(new_cancel)

            # Update iterator
            src_cancel_idx += 1
            count += 1

            if new_cancel['command'] == 0x8000:
                break
        return count


def copyMovesAcrossMovesets(sourceMvst, destMvst, targetMoveName):
    moveDependency_name_id, moveDependency_id_name = MoveDependencies(
        sourceMvst, destMvst, targetMoveName).getDependencies()
    copierObj = MoveCopier(sourceMvst, destMvst,
                           moveDependency_name_id, moveDependency_id_name)
    copierObj.CopyAllDependentMoves()
    # for _, id in enumerate(moveDependency_id_name):
    #     print(id, moveDependency_id_name[id])
    print("Done copying %s and all of it's dependencies" % targetMoveName)
    path = r"C:\Users\alikh\Documents\TekkenMovesetExtractor\extracted_chars\t7_JIN_TEST"
    # path = r"./"
    saveJson('%s/%s.json' % (path, destMvst['character_name']), destMvst)


def main():
    if len(sys.argv) < 4:
        print('Parameters:')
        print('1 = Source Moveset')
        print('2 = Desination Moveset')
        print('3 = Name of Move to Import')
        return

    if sys.argv[1] == None:
        print('Source moveset not passed')
        return

    if sys.argv[2] == None:
        print('Destination moveset not passed')
        return

    if sys.argv[3] == None:
        print('Target move not passed')
        return

    srcMvst = sys.argv[1]
    dstMvst = sys.argv[2]
    movName = sys.argv[3]

    copyMovesAcrossMovesets(srcMvst, dstMvst, movName)


def test():
    srcMvst = loadJson('./tag2_JIN.json')
    dstMvst = loadJson('./t7_JIN.json')
    movName = 'JIN_up03'
    copyMovesAcrossMovesets(srcMvst, dstMvst, movName)


if __name__ == '__main__':
    # main()
    # test()
    print('STILL Work in Progress')

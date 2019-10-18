import re
from functools import reduce

def isIndexedStep(step):
    return re.search(r'\[.*\]$', step) is not None

def isDefinite(path):
    return path.find('[*]') == -1

def isIndefinite(path):
    return not isDefinite(path)

def isSubPath(subPath, path):

    if subPath == '':
        return True

    subSteps = split(subPath)
    steps = split(path)

    if len(steps) < len(subSteps):
        return False

    for i in range(len(subSteps)):

        subKey = re.match(r'^\w+', subSteps[i]).group()
        key = re.match(r'^\w+', steps[i]).group()

        if subKey != key:
            return False
    
    return True

def split(query):
    """
    Splits query by '.' ignoring any in sqaure brackets.
    """
    split = []
    prevStartIndex = 0
    for match in re.finditer(r'\[.+?\]', query):
        matchStartIndex, newStartIndex = match.span()
        split.extend(query[prevStartIndex:matchStartIndex].split('.'))
        split[-1] = split[-1] + match.group()
        prevStartIndex = newStartIndex 
    split.extend(query[prevStartIndex:].split('.'))

    return [part for part in split if part != '']

def join(path):
    return '.'.join(path)

def steps(path):
    return len(split(path))

def getLastIndefiniteStepIndex(path):

    pathSplit = split(path)
    for i in range(steps(path) - 1, -1, -1):
        if pathSplit[i].find('[*]') != -1:
            return i
    
    return -1

# TODO: Fix if [] is not defined for array
def makeDefinite(indefinitePath, definitePath):
    
    lastIndex = getLastIndefiniteStepIndex(indefinitePath)

    if lastIndex == -1:
        # The path is already definite
        return indefinitePath

    # Plus 1 to include the step
    shortIndefinitePath = join(split(indefinitePath)[:lastIndex + 1])
    definitePath = join(split(definitePath)[:lastIndex + 1])

    if not isSubPath(definitePath, shortIndefinitePath) \
        or definitePath == '':
        return None

    fullPath = split(definitePath)[:lastIndex + 1]
    fullPath.extend(split(indefinitePath)[lastIndex + 1:])

    return join(fullPath)

def extractRegexFromString(regex, string, groups):
    
    newString = ''
    prevEndIndex = 0
    for match in re.finditer(regex, string):
        groups.append(match.group())
        newString = newString + string[prevEndIndex:match.start()] + '{' + str(len(groups) - 1) + '}'
        prevEndIndex = match.end()
    newString = newString + string[prevEndIndex:]

    return newString

def splitStepIntoKeyAndSelector(step):

    keyMatch = re.search(r'^\w+', step)
    key = '' if keyMatch is None else keyMatch.group()
    selectorMatch = re.search(r'\[.+\]$', step)
    selector = '' if selectorMatch is None else selectorMatch.group()[1:-1]

    return (key, selector)

class Parser():
    """
    Not sure if 'parser' is the correct terminology here.
    TODO: Look that up.
    """


    def __init__(self, quoteChars, openChars, closeChars):
        self._quoteChars = quoteChars
        self._openChars = openChars
        self._closeChars = closeChars
    
    def _isEscaped(self, string, index):
        return index > 0 and string[index - 1] == '\\'

    def _getCloseChar(self, openChar):
        return self._closeChars[self._openChars.index(openChar)]

    def split(self, string, splitChar):

        splitString = []
        prevSplit = 0

        i = 0
        while i < len(string):
            char = string[i]
            if not self._isEscaped(string, i):
                if char in self._quoteChars:
                    # Jump to end quote and ignore everything in between
                    i = self._findEndQuote(char, string, i)
                elif char in self._openChars:
                    # Jump to closing char and ignore everything inbetween
                    i = self._findClosingChar(char, string, i)
                elif char == splitChar:
                    splitString.append(string[prevSplit:i])
                    prevSplit = i + 1
            i = i + 1

        splitString.append(string[prevSplit: i])

        return splitString

    def _findEndQuote(self, quoteChar, string, startIndex):

        for i in range(startIndex + 1, len(string)):
            char = string[i]
            if char == quoteChar and not self._isEscaped(string, i):
                return i

        raise ValueError('No end quote. Text: {0}'.format(string[startIndex:]))

    def _findClosingChar(self, openChar, string, startIndex):

        i = startIndex + 1
        closeChar = self._getCloseChar(openChar)
        while i < len(string):
            char = string[i]
            if char in self._openChars and not self._isEscaped(string, i):
                # Skip to the close char for this open char
                i = self._findClosingChar(char, string, i)
            elif char in self._closeChars and not self._isEscaped(string, i):
                if char == closeChar:
                    return i
                else:
                    raise ValueError('Invalid string. Opening and closing characters not lined'
                    + ' up correctly. e.g. [(]) is invalid, [()] is valid.')
            i = i + 1

        raise ValueError('No closing character. Closing Char: {0}, Text: {1}'.format(closeChar, string[startIndex:]))

if __name__ == "__main__":
    
    #defPath = 'array[name=Darqk].wefwef.wefwefwef'
    #indefPath = 'array[*].tewertwef.ewfwefw'
    #notSubPath = 'obj.array2[2]'

    #print(makeDefinite(indefPath, defPath))
    #path = 'object.array[person.name="/[a-zA-Z\]\["]+/im"].person.name[type="first"]'
    path = 'object."a .ty [] person".array[person.name="dave"].person.name[type="first"]'
    parser = Parser(['"', "'"], ['['], [']'])
    print(parser.split(path, '.'))
    print(parser.split('person.name[ewdf.wefwef="few [ .w =]ewf"]="dave"', '='))
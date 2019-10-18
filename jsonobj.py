from abc import ABC, abstractmethod
import re
import pathutils
from functools import reduce
from selectors import *
from pathcomps import *

# TODO: More specific error messages

parser = pathutils.Parser(['"', "'"], ['['], [']'])

def _parseSubqueryMatchers(string, groups):

    subqueries = []
    for predicate in string.split(','):
        firstEqual = predicate.find('=')
        predicate = predicate.format(*groups)
        query, value = predicate[:firstEqual], predicate[firstEqual + 1:]
        subqueries.append(SubqueryMatcher(query, value))
    return subqueries

def build(path):
    # Extract the regexs and strings from the path - They
    # can interfere with the path parsing.
    # TODO: Do this for all values
    groups = []
    path = pathutils.extractRegexFromString(Path._regexRegex, path, groups)
    path = pathutils.extractRegexFromString(Path._stringRegex, path, groups)
    steps = pathutils.split(path)
    
    return _build(steps, groups)

def _build(steps, groups):

    if len(steps) == 0:
        return None
    
    step = steps.pop(0)
    key, selector = pathutils.splitStepIntoKeyAndSelector(step)

    if selector != '':
        # TODO: Put into seperate function
        if selector == '*':
            arraySelector = EverythingSelector()
        elif selector.rfind('=') == -1:
            arraySelector = IndexSelector(selector)
        else:
            matchers = _parseSubqueryMatchers(selector, groups)
            arraySelector = FirstCompleteMatchSelector(matchers)
        
        return ObjectNode(KeySelector(key), ArrayNode(arraySelector, _build(steps, groups)))
    else:
        return ObjectNode(KeySelector(key), _build(steps, groups))
    
class Path():

    # TODO: Compile these
    _regexRegex = r'(?<!\\)\/.+?(?<!\\)\/\w*'
    _stringRegex = r'(?<!\\)\".+?(?<!\\)\"|(?<!\\)\'.+?(?<!\\)\''

    def __init__(self, path):
        self._path = path
        self._root = build(path)
    
    def query(self, json):

        if self._path == '':
            return json
        
        try:
            return self._root.step(json)
        except ValueError as exception:
            raise ValueError('Path could not be traversed; {0}'.format(str(exception)))

    """
    def merge(self, path):

        minLength = min(self.length(), path.length())
        for i in range(minLength):
            pass
    """

class Matcher(ABC):

    @abstractmethod
    def isMatch(self, value):
        pass

class RegexMatcher(Matcher):

    def __init__(self, regexWithFlags):
        self._regexWithFlags = regexWithFlags
        self._pattern = self.buildPattern(regexWithFlags)
    
    def buildPattern(self, regexWithFlags):

        def charToFlag(char):
        
            if char == '':
                return 0
            elif char == 'i':
                return re.IGNORECASE
            elif char == 'm':
                return re.MULTILINE
            else:
                raise ValueError('Unsupported flag. Flag: {0}'.format(char))
        
        # Regex ensures we will find this
        flagsStartIndex = regexWithFlags.rfind('/')
        # Extract regex and flag string ignoring /
        regex = regexWithFlags[1:flagsStartIndex]
        flagsString = regexWithFlags[flagsStartIndex + 1:]
        
        # Convert flag characters into re.RegexFlag
        flagsList = list(map(lambda char: charToFlag(char), flagsString))
        # OR the flags together
        flags = reduce((lambda flag1, flag2: flag1 | flag2), flagsList, 0)
        # Compile the pattern
        return re.compile(regex, flags)

    def isMatch(self, value):
        return self._pattern.match(value) is not None

class ValueMatcher(Matcher):

    def __init__(self, value):
        self._value = value
    
    def isMatch(self, value):
        return self._value == value

class SubqueryMatcher(Matcher):

    _isRegexPattern = re.compile(r'^/.*/\w*$')
    _isQuotedPattern = re.compile(r'^".*"$|^\'.*\'$')

    def __init__(self, query, matcher):
        self._query = query
        self._path = Path(query)
        self._matcher = self.getMatcher(matcher)
    
    def _isRegex(self, string):
        return SubqueryMatcher._isRegexPattern.match(string) is not None

    def _isQuoted(self, string):
        return SubqueryMatcher._isQuotedPattern.match(string) is not None

    def _isInt(self, string):

        try:
            int(string)
            return True
        except ValueError:
            return False
    
    def _isFloat(self, string):

        try:
            float(string)
            return True
        except ValueError:
            return False

    def getMatcher(self, value):
        
        if self._isQuoted(value):
            return ValueMatcher(value[1:-1])
        elif self._isRegex(value):
            return RegexMatcher(value)
        elif value == 'null':
            return ValueMatcher(None)
        elif value == 'true':
            return ValueMatcher(True)
        elif value == 'false':
            return ValueMatcher(False)
        elif self._isInt(value):
            return ValueMatcher(int(value))
        elif self._isFloat(value):
            return ValueMatcher(float(value))
        else:
            raise ValueError('Unkown value type. Value {0}'.format(value))

    def isMatch(self, json):

        try:
            result = self._path.query(json)
        except ValueError as exception:
            raise ValueError('Subquery failed. Query: {0}; '.format(self._query) + str(exception))

        return self._matcher.isMatch(result)





if __name__ == "__main__":
    
    json = {
        'company' : 'The HoBros',
        'people' : [
            {
                'name' : {
                    'full' : 'Ciaran Hogan',
                    'first' : 'Ciaran',
                    'last' : 'Hogan'
                },
                'age' : 20,
                'swaggy' : True
            },
            {
                'name' : {
                    'full' : 'Tomas Hogan',
                    'first' : 'Tomas',
                    'last' : 'Hogan'
                },
                'age' : 21,
                'swaggy' : False
            },
            {
                'name' : {
                    'full' : 'Bob Billy Bobson',
                    'first' : 'Bob',
                    'last' : 'Bobson'
                },
                'age' : 45,
                'swaggy' : None
            }
        ]
    }

    query = 'people[name.full=/[a-z]+ [\w]+/i]'
    path = Path(query)
    print(path.query(json))
    

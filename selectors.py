from abc import ABC, abstractmethod
from functools import reduce

class Selector(ABC):

    def select(self, json):
        """
        Returns a valid json, 'one step' forward in it's path.
        """
        pass

    @abstractmethod
    def isDefinite(self):
        pass

class FirstCompleteMatchSelector(Selector):

    def __init__(self, matchers):
        self._matchers = matchers

    def select(self, json):

        for element in json:
            if self._isMatch(element):
                return element
        # TODO: Should this soft fail?
        # TODO: Print potential match values?
        raise ValueError('Selector failed to select anything.')
    
    def _isMatch(self, json):
        """
        Return whether all of the match conditions are met
        """
        matchersResolved = list(map(lambda matcher: matcher.isMatch(json), self._matchers))
        return reduce((lambda match1, match2: match1 and match2), matchersResolved, True)
    
    def isDefinite(self):
        return True

class KeySelector(Selector):

    def __init__(self, key):
        self._key = key

    def select(self, json):

        if self._key not in json:
            raise ValueError('Key not in JSON. Key: {0}'.format(self._key))

        return json.get(self._key)
    
    def isDefinite(self):
        return True

class IndexSelector(Selector):

    def __init__(self, index):
        try:
            self._index = int(index)
        except ValueError:
            raise ValueError('Invalid index value. Index: {0}'.format(index))
    
    def select(self, json):
        return json[self._index]

    def isDefinite(self):
        return True
    

class EverythingSelector(Selector):

    def select(self, json):
        
        for element in json:
            yield element

    def isDefinite(self):
        return False
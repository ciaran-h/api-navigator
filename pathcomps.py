from abc import ABC, abstractmethod
import json as jsonlib

class PathComponent(ABC):

    def __init__(self, selector, child):
        self._selector = selector
        self._child = child

    def step(self, json):

        try:
            self._validate(json)
        except ValueError as exception:
            # Build path to this point
            raise ValueError('JSON does not match '\
                + 'path structure; {0}'.format(str(exception)))
        
        if self._child is not None:
            if self._selector.isDefinite():
                return self._child.step(self._selector.select(json))
            else:
                result = []
                for selection in self._selector.select(json):
                    result.append(self._child.step(selection))
                return result
        else:
            if self._selector.isDefinite():
                return self._selector.select(json)
            else:
                result = []
                for selection in self._selector.select(json):
                    result.append(selection)
                return result
        
        return None
        #return subJson

    @abstractmethod
    def _validate(self, json):
        pass
    
    def isDefinite(self):
        """
        Returns whether or not a path will return a single result. i.e. whether a
        path needs more information to be traversed.
        """
        return self._selector.isDefinite()

class ObjectNode(PathComponent):
    
    def _validate(self, json):
        if type(json) is not dict:
            raise ValueError('Expecting an object (i.e. dict). Type: {0}'.format(type(json)))

class ArrayNode(PathComponent):

    def _validate(self, json):
        if type(json) is not list:
            raise ValueError('Expecting an array (i.e. list). Type: {0}'.format(type(json)))

class ValueNode(PathComponent):

    def _validate(self, json):
        if type(json) not in (int, str, bool, None):
            raise ValueError('Expecting an int, str, bool or null (i.e. None). Type: {0}'.format(type(json)))
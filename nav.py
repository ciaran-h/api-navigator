import jsonobj
from apiutils import Controller
from api import API
import copy

class APINav():

    def __init__(self, api):
        self._api = api
        self._sessionData = {}
        self._json = None
        self._alias = None

    def clone(self):
        navClone = APINav(self._api)
        
        navClone._sessionData = copy.deepcopy(self._sessionData)
        navClone._json = copy.deepcopy(self._json)
        navClone._alias = copy.deepcopy(self._alias)

        return navClone

    def getSessionData(self):
        return self._sessionData

    def navigate(self, aliasName, args=None):

        # Update profile with arguments provided by user
        if args is not None and len(args) > 0:
            for arg, value in args.items():
                self.update(arg, value)

        self._alias = self._api.getAlias(aliasName)
        # Attempt to navigate to the alias endpoint
        self._json = self._api.get(aliasName, self._sessionData)

        # Update profile values
        for arg, query in self._alias.getKnownArgs('').items():
            query = self.prepare(query)
            self.update(arg, jsonobj.Path(query).query(self._json))

    def filtr(self, paths):
        # TODO: Remove redundant updates
        for arg, query in self._alias.getKnownArgs(paths).items():
            query = self.prepare(query)
            self.update(arg, jsonobj.Path(query).query(self._json))

    def traverse(self, query):
        self._json = self.execute(query)

    def prepare(self, query):
        # Attempt to substitute profile values into the query
        return query.format(**self._sessionData)

    def execute(self, query):

        query = self.prepare(query)
        # Query the current json
        return jsonobj.Path(query).query(self._json)

    def update(self, argument, value):

        if argument in self._sessionData:
            if self._sessionData[argument] != value:
                raise ValueError(('That argument is already set in the '
                                  + 'profile with a difference value. Arg: {0}, '
                                  + 'Old Value: {1}, New Value: {2}')
                                 .format(argument, self._sessionData[argument], value))

        self._sessionData[argument] = value


if __name__ == "__main__":

    controller = Controller('Files/header.json')
    controller.registerRateLimit(15, 1)
    controller.registerRateLimit(95, 120)

    api = API('Files/endpoints.txt', 'Files/arguments.txt', controller)

    nav = APINav(api)

    nav.navigate('summoners', {'summonerName': 'Darqk'})
    print(nav.execute('name'))
    nav.navigate('matchlists')
    print(nav.execute('matches[0]'))

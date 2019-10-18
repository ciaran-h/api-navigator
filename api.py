import string
from apiutils import Controller
import re
import pathutils

# TODO: Support multiple parameters
def _parseParameters(self, endpoint):
    formatter = string.Formatter()
    return [a[1] for a in formatter.parse(endpoint)]

def loadEndpoints(fileName):

    aliasToEndpoints = {}

    with open(fileName, 'r') as endpointsFile:

        origin, alias = None, None
        
        for line in endpointsFile:
            # Strip whitespace characters
            strippedLine = line.strip()
            # Find index of last whitespace character at beginning of line
            lastWSCharIndex = len(line) - len(line.lstrip('\t'))
            # Count number of tabs up to the first non-whitespace character
            tabs = line.count('\t', 0, lastWSCharIndex)

            if tabs == 0:
                # Origin
                origin = strippedLine
            elif tabs == 1:
                # Alias
                alias = strippedLine
            elif tabs == 2:
                # Endpoint
                endpoint = Endpoint(origin + strippedLine)

                if alias in aliasToEndpoints:
                    aliasToEndpoints[alias].append(endpoint)
                else:
                    aliasToEndpoints[alias] = [endpoint]
            else:
                raise ValueError("Invalid indentation. Lines should be indented"
                + "by, at most, 2 tabs.")

    return aliasToEndpoints

def loadArguments(fileName):

    aliasToArgs = {}

    with open(fileName, 'r') as endpointsFile:

        alias = None
        
        for line in endpointsFile:
            # Strip whitespace characters
            strippedLine = line.strip()
            # Find index of last whitespace character at beginning of line
            lastWSCharIndex = len(line) - len(line.lstrip('\t'))
            # Count number of tabs up to the first non-whitespace character
            tabs = line.count('\t', 0, lastWSCharIndex)

            if tabs == 0:
                # Alias
                alias = strippedLine
            elif tabs == 1:
                
                arg = strippedLine.split('=')[0].strip()
                value = strippedLine.split('=')[1].strip()

                if alias in aliasToArgs:
                    aliasToArgs[alias][arg] = value
                else:
                    aliasToArgs[alias] = {arg : value}
            else:
                raise ValueError("Invalid indentation. Lines should be indented"
                + "by, at most, 2 tabs.")

    return aliasToArgs

class Endpoint():

    def __init__(self, endpoint):
        self._endpoint = endpoint
        # Parse the arguments (i.e. anything in {}) from the endpoint
        self._args = set(a[1] for a in string.Formatter().parse(endpoint))

    def get(self, profile, controller):

        url = self._endpoint.format(**profile)
        return controller.getJSON(url)
    
    def _hasRequiredArgs(self, args):
        return self._args.issubset(args)

class Alias():

    def __init__(self, name, endpoints, argToPath):
        self._name = name
        self._endpoints = endpoints
        self._argToPath = argToPath
    
    def getEndpoint(self, args):

        for endpoint in self._endpoints:
            if endpoint._hasRequiredArgs(args):
                return endpoint
        
        # Constructs a message of what information the user needs to
        # access any of the endpoints.
        helpMessage = 'Need ' + ' or '.join(', '.join("'" + arg + "'" for arg in endpoint._args) for endpoint in self._endpoints) + '.'

        raise ValueError('Not enough information. ' + helpMessage)
    
    def getKnownArgs(self, userPaths):
        '''
        Returns the arguments that can be know from this alias, including from the paths.
        '''
        args = {}
        # TODO: Burn this code and redo it
        for arg, argPath in self._argToPath.items():
            if pathutils.isDefinite(argPath):
                args[arg] = argPath
            else:
                # See if traversable using provided paths
                for userPath in userPaths:
                    defPath = pathutils.makeDefinite(argPath, userPath)
                    if defPath is not None:
                        args[arg] = defPath
                        break
        return args


    

class API():

    # TODO: Move loading into here
    # TODO: Enocde values inserted into url

    def __init__(self, endpointsFileName, argumentsFileName, rateController):

        self._rateController = rateController
        self._nameToAlias = {}

        # TODO: Get the file loading out of here
        aliasNameToEndpoints = loadEndpoints(endpointsFileName)
        aliasToArgs = loadArguments(argumentsFileName)

        for name, endpoints in aliasNameToEndpoints.items():
            self._nameToAlias[name] = Alias(name, endpoints, [] if name not in aliasToArgs else aliasToArgs[name])

    def getAlias(self, aliasName):

        try:
            return self._nameToAlias[aliasName]
        except KeyError:
            raise ValueError('Unknown alias. Alias Name: {0}'.format(aliasName))

    def get(self, aliasName, profile):
    
        alias = self.getAlias(aliasName)

        try:
            endpoint = alias.getEndpoint(profile.keys())
        except ValueError as e:
            raise ValueError('Error querying the "{0}" alias; {1}'.format(aliasName, str(e)))

        return endpoint.get(profile, self._rateController)

class TestController():

    def getJSON(self, url):
        return url

if __name__ == "__main__":
    
    '''
    aliasNameToEndpoints = loader.loadEndpoints()
    aliasToJump = loader.loadArguments()
    controller = TestController()
    api = API(aliasNameToEndpoints, controller)

    print(api.get('summoners', {'summonerName' : 'dave', 'queue' : '232', 'tier' : '5', 'division' : '2'}))
    '''

    endpoints = loadEndpoints('Files/endpoints.txt')
    argToPath = loadArguments('Files/arguments.txt')
    alias = Alias('matches', endpoints, argToPath['matches'])
    for arg, val in alias.getKnownArgs('participantIdentities[0]').items():
        print(arg, val)
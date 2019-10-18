from abc import ABC, abstractmethod, abstractproperty
import json
import re
import shlex
import xlsxwriter
import jsonutils
import os

# TODO: Look into seperating classes into seperate files


class Command(ABC):

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def syntax(self):
        pass

    @abstractproperty
    def desc(self):
        pass

    def __init__(self, console):
        self._console = console

    def run(self, nav, args):

        positionalArgs = []
        options = {}

        i = 0
        while i < len(args):
            currentArg = args[i]
            if currentArg[0] == '-':
                if i + 1 < len(args):
                    options[currentArg[1:]] = args[i + 1]
                    # Skip the next arg since we have already processed it
                    i = i + 1
                else:
                    options[currentArg[1:]]  = ''
            else:
                positionalArgs.append(currentArg)
            i = i + 1

        self._run(nav, positionalArgs, options)

    @abstractmethod
    def _run(self, nav, positionalArgs, options):
        pass

class Keys(Command):

    name = 'keys'
    syntax = 'keys [query]'
    desc = 'Prints a list of the keys at the query destination.'

    def _run(self, nav, positionalArgs, options):

        query = '' if len(positionalArgs) == 0 else positionalArgs[0]
        result = nav.execute(query)

        if type(result) is not dict:
            raise ValueError('Query must return object.')

        print(', '.join(nav.execute(query).keys()))

"""
class Traverse(Command):

    name = 'trav'
    syntax = 'trav <query>'
    desc = 'Traverses the current JSON to the query destination.'

    def _run(self, nav, positionalArgs, options):
        query = positionalArgs[0]
        nav.traverse(query)
"""

class Exit(Command):

    name = 'exit'
    syntax = 'exit'
    desc = 'Exits the console application.'

    def _run(self, nav, positionalArgs, options):
        self._console.close()


class Nav(Command):

    name = 'nav'
    syntax = 'nav <alias name> [\033[4m-arg value\033[0m]'
    desc = 'Navigates to an API endpoint under the specified alias, using the supplied arguments.'

    def _run(self, nav, positionalArgs, options):
        nav.navigate(positionalArgs[0], options)

class Filter(Command):

    name = 'filter'
    syntax = 'filter <query>'
    desc = 'Filters the specified JSON, potentially updating known arguments.'

    def _run(self, nav, positionalArgs, options):
        nav.filtr(positionalArgs)

class Open(Command):

    name = 'open'
    syntax = 'open'
    desc = 'Opens a worksheet.'

    def _run(self, nav, positionalArgs, options):
        pass


class Store(Command):

    name = 'store'
    syntax = 'store <query> <argument name>'
    desc = 'Saves the query result, in the session data under the argument name.'

    def _run(self, nav, positionalArgs, options):

        if len(positionalArgs) < 2:
            raise ValueError('Not enough arguments provided.')

        path = positionalArgs[0]
        name = positionalArgs[1]

        nav.update(name, nav.execute(path))


class PrintQ(Command):

    name = 'printq'
    syntax = 'printq [query]'
    desc = 'Prints the result of the query.'

    def _run(self, nav, positionalArgs, options):

        query = '' if len(positionalArgs) == 0 else positionalArgs[0]
        result = nav.execute(query)
        prettyJSON = json.dumps(result, indent=4, sort_keys=True)

        print(prettyJSON)

class Print(Command):

    name = 'print'
    syntax = 'print [query]'
    desc = 'Prints the result of the query.'

    def run(self, nav, args):
        for arg in args:
            print(nav.prepare(arg))
    
    def _run(self, nav, positionalArgs, options):
        pass

class Session(Command):

    name = 'session'
    syntax = 'session'
    desc = 'Prints the session data. i.e. The information that has been gathered by your queries/filters.'

    def _run(self, nav, positionalArgs, options):

        prettyJSON = json.dumps(nav.getSessionData(), indent=4, sort_keys=True)
        print(prettyJSON)

class Write(Command):

    name = 'write'
    syntax = 'write'
    desc = 'Writes the output of a query to a worksheet.'

    def _run(self, nav, positionalArgs, options):

        path = os.path.expanduser("~/Desktop/") + positionalArgs[0] + '.xlsx'
        workbook = xlsxwriter.Workbook(path)
        worksheet = workbook.add_worksheet('Sheet 1')
        jsonutils.writeToXLSX(worksheet, json)
        workbook.close()


class Close(Command):

    name = 'close'
    syntax = 'close'
    desc = 'Closes a worksheet.'

    def _run(self, nav, positionalArgs, options):
        pass


class Clear(Command):

    name = 'clear'
    syntax = 'clear'
    desc = 'Clears the console.'

    def _run(self, nav, positionalArgs, options):
        self._console.clear()

class Execute(Command):

    name = 'exec'
    syntax = 'exec <path> [\033[4m-arg value\033[0m]'
    desc = 'Executes the file as a command, line by line.'

    def _run(self, nav, positionalArgs, options):
        
        fileName = positionalArgs[0]

        with open(fileName, 'r') as lines:
            commands = [line.strip() for line in lines if line.strip() != '']

        if re.match(r'\s*#\s*Required:', commands[0], re.IGNORECASE) is not None:
            
            firstLine = commands.pop(0)

            # Parse the required args
            requiredArgs = set(arg.strip() for arg in firstLine.split(':', 1)[1].split(','))
            
            # Check that the user has supplied the require args
            if not requiredArgs.issubset(options.keys()):
                raise ValueError('Missing required arguments. Missing: {0}'
                    .format(', '.join(requiredArgs.difference(options.keys()))))
            
        
        nav = self._console.newNavigator()

        # Update the session data with all of the argument/values
        # supplied
        for arg, value in options.items():
            nav.update(arg, value)

        self._run_helper(nav, commands)
        
    def _run_helper(self, nav, commands):

        if len(commands) == 0:
            return

        command = commands.pop(0)

        lexer = shlex.shlex(command, posix=True)
        lexer.whitespace_split = True
        tokens = [token for token in lexer]
        
        if tokens[0] == 'for':
            argName = tokens[1]
            values = tokens[3:]
            for value in values:
                navClone = nav.clone()
                navClone.update(argName, value)
                #try:
                self._run_helper(navClone, commands.copy())
                #except Exception as e:
                #    raise Exception('Error executing command. Command: {0}{1}'.format(command, str(e)))
        else:
            #try:
            self._console.execute(nav, command)
            self._run_helper(nav, commands)
            #except Exception as e:
            #    raise Exception('Error executing command. Command: {0}{1}'.format(command, str(e)))

class Help(Command):

    name = 'help'
    syntax = 'help [command name]'
    desc = 'Provides information about a command or commands.'

    def _run(self, nav, positionalArgs, options):

        if len(positionalArgs) == 0:
            self._allCommandsHelp()
        else:
            commandName = positionalArgs[0]
            self._singleCommandHelp(commandName)

    def _singleCommandHelp(self, commandName):

        for command in self._console._commands:
            if command.name == commandName:
                print('\nCOMMAND\n\t{0}\nSYNTAX\n\t{1}\nDESCRIPTION\n\t{2}\n'.format(
                    command.name, command.syntax, command.desc))
                return

        raise ValueError(
            'Command with that name not found. Name: {0}'.format(commandName))

    def _allCommandsHelp(self):
        print('\nType help followed by a command name (e.g. help nav) for more specific information.')
        # Get a list of command names and descriptions sorted by name
        commandInfo = sorted([(command.name, command.desc)
                              for command in self._console._commands], key=lambda command: command[0])
        print('\nCOMMANDS\n\t{0}.'.format(
            ', '.join(name for name, desc in commandInfo)))
        print('\nDESCRIPTIONS')
        for name, desc in commandInfo:
            print('\t{0}\n\t\t{1}'.format(name, desc))
        print()

from commands import Command
import pkgutil
import importlib
import shlex
import os
from nav import APINav
from api import API
from apiutils import Controller

def printTitleBar(width):
    print('-' * width)
    print('|' + 'API Navigator'.center(width - 2, ' ') + '|')
    print('-' * width)

class Console():
    # TODO: RENAME PROFILE TO SESSION AND ALIAS TO PROFILE
    _prompt = '> '

    def __init__(self):
        self._closed = False
        self._load()

        # TODO: Burn this in fire and sprinkle holy water on the remains
        controller = Controller('Files/header.json')
        controller.registerRateLimit(15, 1)
        controller.registerRateLimit(95, 120)

        self._api = API('Files/endpoints.txt', 'Files/arguments.txt', controller)
        
        self._nav = APINav(self._api)
    
    def _load(self):

        self._commands = []

        for command in Command.__subclasses__():
            self._commands.append(command(self))

    def getCommand(self, name):

        for command in self._commands:
            if command.name == name:
                return command

    def newNavigator(self):
        return APINav(self._api)

    def close(self):
        self._closed = True
    
    def closed(self):
        return self._closed
    
    def clear(self):
        os.system('cls')
        printTitleBar(40)

    def execute(self, navigator, commandInput):
        
        # Parse tokens from command
        lexer = shlex.shlex(commandInput, posix=True)
        lexer.whitespace_split = True
        tokens = [token for token in lexer]

        # No command
        if len(tokens) == 0:
            return

        # Parse the command and arguments
        commandName = tokens.pop(0)
        commandArgs = tokens
        command = self.getCommand(commandName)

        # Run the command if we found it
        if command is not None:
            command.run(navigator, commandArgs)
        else:
            raise ValueError("Unkown input: type 'help' for a list of commands.")

    def run(self):

        self.clear()
        while not self.closed():
            commandInput = input(self._prompt)
            try:
                self.execute(self._nav, commandInput)
            except Exception as e:
                print('ERROR: ' + str(e))

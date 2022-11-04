"""
Contains Utility functions
"""
import re
import os
import errno
from datetime import date
from enum import Enum


class Constants(Enum):
    LINELENGTH = 125
    CURRYEAR = date.today().year
    TABSPACE = 4


class File:
    """
    Represents File class
    Use to write CPP code without worrying about formatting
    """

    def __init__(self, inName: str, inDescription: str, inPath: str):
        self.mName = inName
        self.mPath = inPath
        self.mDescription = inDescription
        self.__content = ''
        self.__spaces = 0
        self.writeHeader()

    def writeHeader(self):
        """Generates File Header content"""
        self.write(f'// {"=" * Constants.LINELENGTH.value}\n')
        self.write(f'/// @file {self.mName}\n')
        self.write(f'///\n')
        self.write(f'/// {self.mDescription}\n')
        self.write(f'///\n')
        self.write(f'/// Copyright (C) {Constants.CURRYEAR.value} Simba Technologies Incorporated.\n')
        self.write(f'// {"=" * Constants.LINELENGTH.value}\n\n')

    def write(self, inContent: str):
        self.__content += inContent
        # braceIdx = dict()
        # lastIdx = -1
        # for idx, ch in enumerate(inContent):
        #     if ch == '{':
        #         braceIdx[idx] = ch
        #     elif ch == '}':
        #         braceIdx[idx] = ch
        # for idx, brace in braceIdx.items():
        #     # Seperate statements by ";" to new line
        #     partContent = inContent[lastIdx + 1: idx].replace(';', ';\n')
        #     partContent = partContent.replace('\n', f'\n{self.__spaces * " "}')
        #     self.__content += f'{self.__spaces * " "}{partContent}' if len(partContent) > 0 else ''
        #     if brace == '{':
        #         self.__content += f'\n{self.__spaces * " "}{brace}\n'
        #         self.__spaces += 4
        #     else:
        #         self.__spaces -= 4
        #         self.__content += f'\n{self.__spaces * " "}{brace}'
        #     lastIdx = idx
        # self.__content += inContent[lastIdx + 1:].replace('\n', f'\n{self.__spaces * " "}')

    def save(self):
        with open(os.path.join(self.mPath, self.mName), 'w') as file:
            file.write(self.__content.replace('\t', f'{" " * 4}'))

    @staticmethod
    def createDir(inDirPath: str, inMode: int = 0o777):
        """Creates the absent directories from the given path."""
        try:
            os.makedirs(inDirPath, inMode)
        except OSError as err:
            # Re-raise the error unless it's for already existing directory
            if err.errno != errno.EEXIST or not os.path.isdir(inDirPath):
                raise

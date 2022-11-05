"""
Contains Utility functions
"""
import re
import os
import errno
from enum import Enum
from datetime import date

from MDEF import PreReqCall


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
        """
        Write content to file buffer
        TODO: Implement CPP code formatting
        """
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

    def writePreReqCalls(self, inPreReqCall: PreReqCall, indentLevel: int):
        """Generates Pre-req calls contents"""
        tab = '\t'
        self.write(f'{tab * indentLevel}{"{"}\n')
        self.write(f'{tab * indentLevel}{"{"}\n')
        self.write(f'{tab * (indentLevel + 1)}// ReadAPI Prereqcall\n')
        self.write(f'{tab * (indentLevel + 1)}SaaSPreReqCall table_preReqCall1;\n')
        self.write(f'{tab * (indentLevel + 1)}table_preReqCall1.SetEndPoint("{inPreReqCall.Endpoint}");\n')
        if inPreReqCall.Pageable:
            # TODO: Implement PreReqCall specific pagination config
            self.write(f'{tab * (indentLevel + 1)}table_preReqCall1.SetPaginationHandler(paginationHandler);\n')
        self.write(f'{tab * (indentLevel + 1)}// ServiceReq param key read details\n')
        for item in inPreReqCall.ReqParamKeys:
            self.write(f'{tab * (indentLevel + 1)}{"{"}\n')
            self.write(f'{tab * (indentLevel + 2)}SaaSSvcReqParamKey table_svcReqParamKey;\n')
            self.write(f'{tab * (indentLevel + 2)}table_svcReqParamKey.SetKeyName("{item.KeyName}");\n')
            if item.RespAttrField is not None and len(item.RespAttrField) > 0:
                self.write(f'{tab * (indentLevel + 2)}'
                           f'table_svcReqParamKey.SetSvcRespAttrField("{item.RespAttrField}");\n')
            if item.IsParameter:
                self.write(f'{tab * (indentLevel + 2)}table_preReqCall1.SetParameterType();\n')
            if item.IsReferenced:
                self.write(f'{tab * (indentLevel + 2)}table_preReqCall1.SetReferencedType();\n')
            if item.MaxValuesPerCall > 0:
                self.write(f'{tab * (indentLevel + 2)}table_preReqCall1.SetMaxValuesPerCall({item.MaxValuesPerCall});\n')
            self.write(f'{tab * (indentLevel + 2)}table_preReqCall1.AddSvcReqParamKey(table_svcReqParamKey);\n')
            self.write(f'{tab * (indentLevel + 1)}{"}"}\n')
        if inPreReqCall.ListRoot is not None and len(inPreReqCall.ListRoot) > 0:
            self.write(f'{tab * (indentLevel + 1)}table_preReqCall1.SetListRoot("{inPreReqCall.ListRoot}");\n')
        if inPreReqCall.Pageable and inPreReqCall.Pagination is not None:
            # TODO: Prepare Pagination data
            self.write(f'{tab * (indentLevel + 1)}table_preReqCall1.SetPaginationData(GetPaginationDataDetails_ROWCOUNT());\n')
        if inPreReqCall.ChildPreReqCall is not None:
            self.writeChildPreReqCalls(inPreReqCall.ChildPreReqCall, indentLevel + 1, 2)
        self.write(f'{tab * (indentLevel + 1)}table_readApiEndpoint.SetPreReqCall(table_preReqCall1);\n')
        self.write(f'{tab * indentLevel}{"}"}\n')

    def writeChildPreReqCalls(self, inPreReqCall: PreReqCall, indentLevel: int, inIdent: int = 1):
        """Generates Pre-req calls contents"""
        tab = '\t'
        self.write(f'{tab * indentLevel}{"{"}\n')
        self.write(f'{tab * (indentLevel + 1)}// ReadAPI Nested Prereqcall\n')
        self.write(f'{tab * (indentLevel + 1)}SaaSPreReqCall table_preReqCall{inIdent};\n')
        self.write(f'{tab * (indentLevel + 1)}table_preReqCall{inIdent}.SetEndPoint("{inPreReqCall.Endpoint}");\n')
        if inPreReqCall.Pageable:
            # TODO: Implement PreReqCall specific pagination config
            self.write(f'{tab * (indentLevel + 1)}table_preReqCall{inIdent}.SetPaginationHandler(paginationHandler);\n')
        self.write(f'{tab * (indentLevel + 1)}// ServiceReq param key read details\n')
        for item in inPreReqCall.ReqParamKeys:
            self.write(f'{tab * (indentLevel + 1)}{"{"}\n')
            self.write(f'{tab * (indentLevel + 2)}SaaSSvcReqParamKey table_svcReqParamKey;\n')
            self.write(f'{tab * (indentLevel + 2)}table_svcReqParamKey.SetKeyName("{item.KeyName}");\n')
            if item.RespAttrField is not None and len(item.RespAttrField) > 0:
                self.write(f'{tab * (indentLevel + 2)}'
                           f'table_svcReqParamKey.SetSvcRespAttrField("{item.RespAttrField}");\n')
            if item.IsParameter:
                self.write(f'{tab * (indentLevel + 2)}table_preReqCall{inIdent}.SetParameterType();\n')
            if item.IsReferenced:
                self.write(f'{tab * (indentLevel + 2)}table_preReqCall{inIdent}.SetReferencedType();\n')
            if item.MaxValuesPerCall > 0:
                self.write(f'{tab * (indentLevel + 2)}table_preReqCall{inIdent}.SetMaxValuesPerCall({item.MaxValuesPerCall});\n')
            self.write(f'{tab * (indentLevel + 2)}table_preReqCall{inIdent}.AddSvcReqParamKey(table_svcReqParamKey);\n')
            self.write(f'{tab * (indentLevel + 1)}{"}"}\n')
        if inPreReqCall.ListRoot is not None and len(inPreReqCall.ListRoot) > 0:
            self.write(f'{tab * (indentLevel + 1)}table_preReqCall{inIdent}.SetListRoot("{inPreReqCall.ListRoot}");\n')
        if inPreReqCall.Pageable and inPreReqCall.Pagination is not None:
            # TODO: Prepare Pagination data
            self.write(f'{tab * (indentLevel + 1)}table_preReqCall{inIdent}.SetPaginationData(GetPaginationDataDetails_ROWCOUNT());\n')
        if inPreReqCall.ChildPreReqCall is not None:
            self.writeChildPreReqCalls(inPreReqCall.ChildPreReqCall, indentLevel + 1, inIdent + 1)
        self.write(f'{tab * (indentLevel + 1)}table_preReqCall{inIdent - 1}.SetPreReqCall(table_preReqCall{inIdent});\n')
        self.write(f'{tab * indentLevel}{"}"}\n')

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

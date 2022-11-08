"""
Contains Utility functions
"""
import re
import os
import errno
from enum import Enum
from datetime import date

from MDEF import ColumnPushdown, Column, ListVariablesPreCall, Pagination, PrimaryKey, PreReqCall, ReadAPI


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

    def writePrimaryKeys(self, inPrimaryKeys: list[PrimaryKey], inTableName: str, indent: int = 1):
        tab = '\t'
        self.write(f'{tab * indent}// Primary Key\n')
        self.write(f'{tab * indent}{"{"}\n')
        self.write(f'{tab * (indent + 1)}SaaSTablePKeyColumn tablePKey;\n')
        self.write(f'{tab * (indent + 1)}tablePKey.SetPKeyName("pk_{inTableName}");\n')
        for pKey in inPrimaryKeys:
            self.write(f'{tab * (indent + 1)}{"{"}\n')
            self.write(f'{tab * (indent + 2)}SaaSPK pKey{inTableName};\n')
            self.write(f'{tab * (indent + 2)}pKey{inTableName}.SetPkColumn({pKey.Index});\n')
            self.write(f'{tab * (indent + 2)}tablePKey.AddPK(pKey{inTableName});\n')
            self.write(f'{tab * (indent + 1)}{"}"}\n')
        self.write(f'{tab * (indent + 1)}table.SetPkeyColumns(tablePKey);\n')
        self.write(f'{tab * indent}{"}"}\n')

    def writeColumnPushdown(self, inColPushdown: ColumnPushdown, indent: int = 1):
        tab = '\t'
        self.write(f'{tab * indent}SaaSColumnPushdown columnPushdown;\n')
        self.write(f'{tab * indent}columnPushdown.SetSupport(true);\n')
        self.write(f'{tab * indent}columnPushdown.SetSvcReqParamKey("'
                   f'{f"{inColPushdown.ParamDelimiter}".join(inColPushdown.ParamKey)}'
                   f'";\n')
        self.write(f'{tab * indent}columnPushdown.SetSvcReqParamDelimiter("{inColPushdown.ParamDelimiter}");\n')

    def writePreReqCalls(self, inPreReqCall: PreReqCall, indentLevel: int):
        """Generates Pre-req calls contents"""
        tab = '\t'
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
        """Generates Nested Pre-req calls contents"""
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

    def writeColumns(self, inColumns: list[Column], indent: int = 1):
        tab = '\t'
        self.write(f'{tab * indent}// Static Columns\n')
        self.write(f'{tab * indent}{"{"}\n')
        for column in inColumns:
            self.write(f'{tab * (indent + 1)}{"{"}\n')
            self.write(f'{tab * (indent + 2)}SaaSTableColumn column_table;\n')
            self.write(f'{tab * (indent + 2)}column_table.SetName("{column.Name}");\n')

            self.write(f'{tab * (indent + 2)}SaaSMetadata metadata_column_table;\n')
            colMetadata = column.Metadata
            self.write(f'{tab * (indent + 2)}metadata_column_table.SetSqlType({colMetadata.SQLType});\n')
            if colMetadata.SourceType is not None and len(colMetadata.SourceType) > 0:
                self.write(f'{tab * (indent + 2)}metadata_column_table.SetSourceType({colMetadata.SourceType.upper()});\n')
            if colMetadata.IsUnsigned:
                self.write(f'{tab * (indent + 2)}metadata_column_table.SetIsUnsigned({str(colMetadata.IsUnsigned).lower()});\n')
            if colMetadata.Length > 0:
                self.write(f'{tab * (indent + 2)}metadata_column_table.SetLength({colMetadata.Length});\n')
            if colMetadata.Scale > 0:
                self.write(f'{tab * (indent + 2)}metadata_column_table.SetScale({colMetadata.Scale});\n')
            if colMetadata.Precision > 0:
                self.write(f'{tab * (indent + 2)}metadata_column_table.SetPrecision({colMetadata.Precision});\n')
            self.write(f'{tab * (indent + 2)}column_table.SetMetadata(metadata_column_table);\n')

            self.write(f'{tab * (indent + 2)}column_table.SetNullable({str(column.Nullable).lower()});\n')
            self.write(f'{tab * (indent + 2)}column_table.SetUpdatable({str(column.Updatable).lower()});\n')
            self.write(f'{tab * (indent + 2)}column_table.SetPassdownable({str(column.Passdownable).lower()});\n')
            if column.ListResult is not None and len(column.ListResult) > 0:
                self.write(f'{tab * (indent + 2)}column_table.SetSvcRespAttrListResult("{column.ListResult}");\n')
            if column.ItemResult is not None and len(column.ItemResult) > 0:
                self.write(f'{tab * (indent + 2)}column_table.SetSvcRespAttrItemResult("{column.ItemResult}");\n')
            if column.QueryMapping is not None and len(column.QueryMapping) > 0:
                self.write(f'{tab * (indent + 2)}column_table.SetSvcReqParamQueryMapping("{column.QueryMapping}");\n')
            if column.ReturnIdPath is not None and len(column.ReturnIdPath) > 0:
                self.write(f'{tab * (indent + 2)}column_table.SetSvcRespAttrReturnIdPath("{column.ReturnIdPath}");\n')
            if column.PushdownMapping is not None and len(column.PushdownMapping) > 0:
                self.write(f'{tab * (indent + 2)}column_table.SetColumnPushDownMapping("{column.PushdownMapping}");\n')
            if column.SyntheticIndexColumn:
                # Do nothing. Virtual tables not implemented
                pass
            self.write(f'{tab * (indent + 2)}table.AddColumn(column_table);\n')
            self.write(f'{tab * (indent + 1)}{"}"}\n')
        self.write(f'{tab * indent}{"{"}\n')

    def writeReadAPI(self, inReadAPI: ReadAPI, inPagination: Pagination, indent: int = 1):
        tab = '\t'
        self.write(f'{tab * indent}// ReadAPI\n')
        self.write(f'{tab * indent}{"{"}\n')
        self.write(f'{tab * (indent + 1)}SaaSReadApi table_readApi;\n')
        if inPagination is not None:
            self.write(f'{tab * (indent + 1)}table_readApi.SetPaginationHandler(paginationHandler);\n')
        self.write(f'{tab * (indent + 1)}// ReadAPI Endpoints\n')
        self.write(f'{tab * (indent + 1)}{"{"}\n')
        endpoint = inReadAPI.Endpoint
        self.write(f'{tab * (indent + 2)}SaaSReadApiEndpoint table_readApiEndpoint;\n')
        self.write(f'{tab * (indent + 2)}table_readApiEndpoint.SetListEndPoint("{endpoint.ListEndpoint}");\n')
        self.write(f'{tab * (indent + 2)}table_readApiEndpoint.SetItemEndPoint("{endpoint.ItemEndpoint}");\n')
        self.write(f'{tab * (indent + 2)}table_readApiEndpoint.SetType("{endpoint.Type}");\n')
        if inPagination is not None:
            # TODO: Fix me
            self.write(f'{tab * (indent + 2)}table_readApiEndpoint.SetPaginationData(GetPaginationDataDetails());\n')
        if endpoint.PreReqCall is not None:
            self.writePreReqCalls(endpoint.PreReqCall, indent + 2)
        self.write(f'{tab * (indent + 2)}table_readApi.SetEndPoint(table_readApiEndpoint);\n')
        self.write(f'{tab * (indent + 1)}{"}"}\n')
        self.write(f'{tab * (indent + 1)}table_readApi.SetMethod("{inReadAPI.Method}");\n')
        if inReadAPI.Accept is not None and len(inReadAPI.Accept) > 0:
            self.write(f'{tab * (indent + 1)}table_readApi.SetAccept("{inReadAPI.Accept}");\n')
        if inReadAPI.ContentType is not None and len(inReadAPI.ContentType) > 0:
            self.write(f'{tab * (indent + 1)}table_readApi.SetContentType("{inReadAPI.ContentType}");\n')
        if inReadAPI.ParameterFormat is not None and len(inReadAPI.ParameterFormat) > 0:
            self.write(f'{tab * (indent + 1)}table_readApi.SetParameterFormat("{inReadAPI.ParameterFormat}");\n')
        if inReadAPI.ListRoot is not None and len(inReadAPI.ListRoot) > 0:
            self.write(f'{tab * (indent + 1)}table_readApi.SetListRoot("{inReadAPI.ListRoot}");\n')
        if inReadAPI.ItemRoot is not None and len(inReadAPI.ItemRoot) > 0:
            self.write(f'{tab * (indent + 1)}table_readApi.SetItemRoot("{inReadAPI.ItemRoot}");\n')
        self.write(f'{tab * (indent + 1)}table_apiAccess.SetReadApi(table_readApi);\n')
        self.write(f'{tab * (indent + 1)}{"}"}\n')
        self.write(f'{tab * (indent + 1)}table.SetAPIAccess(table_apiAccess);\n')
        self.write(f'{tab * indent}{"}"}\n')

    def writeListVariables(self, inListVariables: list[ListVariablesPreCall], indent: int = 1):
        tab = '\t'
        self.write(f'{tab * indent}// List Variable PreCalls\n')
        for listVar in inListVariables:
            self.write(f'{tab * indent}{"{"}\n')
            self.write(f'{tab * (indent + 1)}SaaSListVariable table_listvariable;\n')
            self.write(f'{tab * (indent + 1)}table_listvariable.SetEndpoint("{listVar.Endpoint}");\n')
            for variable in listVar.Variables:
                self.write(f'{tab * (indent + 1)}{"{"}\n')
                self.write(f'{tab * (indent + 2)}SaaSVariable table_variable;\n')
                self.write(f'{tab * (indent + 2)}table_variable.SetVariableName("{variable.Name}");\n')
                self.write(f'{tab * (indent + 2)}table_variable.SetSvcRespAttrMapping("{variable.MappedName}");\n')
                self.write(f'{tab * (indent + 2)}table_listvariable.AddVariables(table_variable);\n')
                self.write(f'{tab * (indent + 1)}{"}"}\n')
            if listVar.AcceptType is not None and len(listVar.AcceptType) > 0:
                self.write(f'{tab * (indent + 1)}table_listvariable.SetAcceptType("{listVar.AcceptType}");\n')
            if listVar.Root is not None and len(listVar.Root) > 0:
                self.write(f'{tab * (indent + 1)}table_listvariable.SetVariableRoot("{listVar.Root}");\n')
            if listVar.DefaultValue is not None and len(listVar.DefaultValue) > 0:
                self.write(f'{tab * (indent + 1)}table_listvariable.SetSvcRespAttrDefaultValue("{listVar.DefaultValue}");\n')
            self.write(f'{tab * (indent + 1)}skeleton_table.AddListVariablesPrecalls(table_listvariable);\n')
            self.write(f'{tab * indent}{"}"}\n')
        self.write('\n')

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

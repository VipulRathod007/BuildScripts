"""
Contains definition of MDEF class
"""
import re
import sys
from enum import Enum
from abc import abstractmethod
from collections import OrderedDict


class Constants(Enum):
    KEY = 'Key'
    NAME = 'Name'
    DATASOURCE = 'Datasource'
    BASEURL = 'BaseURL'
    PAGINATION = 'Pagination'
    PAGINATIONTYPE = 'PaginationType'
    TESTURLENDPOINT = 'TestURL_endpoint'
    TIMESTAMPFORMAT = 'TimestampFormat'
    ISUNIXTIMESTAMPFORMAT = 'IsUnixTimeStampFormat'
    TIMESTAMPUNIT = 'TimestampUnit'
    ISLAZYINITIALIZATION = 'IsLazyInitialization'
    DOESSERVERSUPPORTTHROTTLING = 'DoesServerSupportThrottling'
    AUTHBROWSECONNECTMAP = 'AuthBrowseConnectMap'
    AUTHPROFILES = 'AuthProfiles'
    TABLENAME = 'TableName'
    TABLES = 'Tables'
    SKELETONTABLE = 'SkeletonTable'
    SORTABLE = 'Sortable'
    PAGEABLE = 'Pageable'
    COLUMNPUSHDOWN = 'ColumnPushdown'
    ITEMENDPOINTCOLUMNNAMES = 'ItemEndpointColumnNames'
    PKEYCOLUMN = 'PKeyColumn'
    FKEYCOLUMN = 'FKeyColumn'
    COLUMNS = 'Columns'
    APIACCESS = 'APIAccess'
    READAPI = 'ReadAPI'
    CREATEAPI = 'CreateAPI'
    UPDATEAPI = 'UpdateAPI'
    DELETEAPI = 'DeleteAPI'
    TABLESCHEMANAME = 'TableSchemaName'
    SUPPORT = 'Support'
    SVCREQPARAMKEY = 'SvcReqParam_Key'
    SVCREQPARAMDELIMITER = 'SvcReqParam_Delimiter'
    PKCOLUMNNAME = 'PKColumnName'
    RELATEDFKCOLUMNS = 'RelatedFKColumns'
    FOREIGNKEYCOLUMNS = 'ForeignKeyColumns'
    REFERENCETABLE = 'ReferenceTable'
    REFERENCETABLESCHEMA = 'ReferenceTableSchema'
    ISUNSIGNED = 'IsUnsigned'
    LENGTH = 'Length'
    PRECISION = 'Precision'
    SQLTYPE = 'SQLType'
    SCALE = 'Scale'
    SOURCETYPE = 'SourceType'
    METADATA = 'Metadata'
    COLUMNPUSHDOWN_MAPPING = 'ColumnPushdown_Mapping'
    NULLABLE = 'Nullable'
    PASSDOWNABLE = 'Passdownable'
    SVCREQPARAM_QUERYMAPPING = 'SvcReqParam_QueryMapping'
    SVCRESPATTR_ITEMRESULT = 'SvcRespAttr_ItemResult'
    SVCRESPATTR_LISTRESULT = 'SvcRespAttr_ListResult'
    SVCRESPATTR_RETURNIDPATH = 'SvcRespAttr_ReturnIdPath'
    SYNTHETICINDEXCOLUMN = 'SyntheticIndexColumn'
    UPDATABLE = 'Updatable'
    ISPARAMETER = 'IsParameter'
    ISREFERENCED = 'IsReferenced'
    MAXVALUESPERCALL = 'MaxValuesPerCall'
    SVCRESPATTRFIELD = 'SvcRespAttr_Field'
    KEYNAME = 'keyName'
    ROOT = 'Root'
    SVCREQPARAMKEYS = 'SvcReqParam_Keys'
    ITEMENDPOINT = 'ItemEndpoint'
    ITEMENDPOINTHASARRAYRESPONSE = 'ItemEndpointHasArrayResponse'
    LISTENDPOINT = 'ListEndpoint'
    PREREQCALL = 'PreReqCall'
    TYPE = 'Type'
    ACCEPT = 'Accept'
    BODYSKELETON = 'BodySkeleton'
    CONTENTTYPE = 'ContentType'
    DATAPATH = 'DataPath'
    ENDPOINT = 'Endpoint'
    ITEMROOT = 'ItemRoot'
    LISTROOT = 'ListRoot'
    METHOD = 'Method'
    COLUMNREQUIREMENTS = 'ColumnRequirements'
    PARAMETERFORMAT = 'ParameterFormat'
    ENCBROWSECONNECTKEY = 'EncBrowseConnectKey'
    ISSENSITIVEKEY = 'IsSensitiveKey'
    VALUE = 'Value'
    PATH = 'Path'
    HEADERS = 'Headers'
    EXPECTEDPARAMS = 'ExpectedParams'
    REQUIREDPARAMS = 'RequiredParams'
    SEQUENCE = 'Sequence'
    TOKENTYPE = 'TokenType'
    ISEXPIRATIONDATAAVAILABLE = 'IsExpirationDataAvailable'
    ISAUTOREFRESHSUPPORTED = 'IsAutoRefreshSupported'
    REFRESHTOKENWITHINRANGE = 'RefreshTokenWithinRange'
    AUTH_WINDOWHEIGHT = 'Auth_WindowHeight'
    AUTH_WINDOWWIDTH = 'Auth_WindowWidth'
    VERIFYHOST = 'VerifyHost'
    VERIFYPEER = 'VerifyPeer'


class Parsable:
    """Represents Abstract Parsable class"""
    @abstractmethod
    def parse(self, inData):
        pass


class AuthBrowseConnectMap(Parsable):
    def __init__(self):
        self.__mKey = None
        self.__mEncKey = None
        self.__mIsSensitive = None

    def parse(self, inData):
        """Parses AuthBrowseConnectMap content"""
        assert isinstance(inData, dict)
        self.__mKey = inData[Constants.KEY.value]
        self.__mEncKey = inData[Constants.ENCBROWSECONNECTKEY.value] \
            if Constants.ENCBROWSECONNECTKEY.value in inData else None
        self.__mIsSensitive = inData[Constants.ISSENSITIVEKEY.value] \
            if Constants.ISSENSITIVEKEY.value in inData else False
        return self

    @property
    def Key(self):
        return self.__mKey

    @property
    def EncBrowseConnectKey(self):
        return self.__mEncKey

    @property
    def IsSensitive(self):
        return self.__mIsSensitive


class Pagination:

    def __init__(self, inType: str):
        self.__pagingmap__ = {
            'INDEX_BASED_PAGINATION': 'SAAS_PAGE_TYPE_INDEX_BASED',
            'BODY_BASED_PAGINATION': 'SAAS_PAGE_TYPE_BODY_BASED',
            'HEADER_BASED_PAGINATION': 'SAAS_PAGE_TYPE_HEADER_BASED',
            'TOKEN_BASED_PAGINATION': 'SAAS_PAGE_TYPE_TOKEN_BASED'
        }
        if inType in self.__pagingmap__:
            self.__mType = self.__pagingmap__[inType]
        else:
            raise ValueError(f'Unsupported Pagination type provided: {inType}')

    @property
    def Type(self):
        return self.__mType


class ColumnPushdown(Parsable):
    def __init__(self):
        self.__mParamDelimiter = None
        self.__mParamKey = list()
        self.__mSupport = False

    def parse(self, inData):
        """Parses ColumnPushdown MDEF Content"""
        assert isinstance(inData, dict)
        if Constants.SUPPORT.value in inData and inData[Constants.SUPPORT.value]:
            self.__mSupport = inData[Constants.SUPPORT.value]
            self.__mParamKey = inData[Constants.SVCREQPARAMKEY.value]
            self.__mParamDelimiter = inData[Constants.SVCREQPARAMDELIMITER.value]
        return self

    @property
    def Supported(self) -> bool:
        return self.__mSupport

    @property
    def ParamKey(self) -> list[str]:
        return self.__mParamKey

    @property
    def ParamDelimiter(self) -> str:
        return self.__mParamDelimiter


class PrimaryKey:
    def __init__(self, inName: str, inFKCols: list[str]):
        self.__mRelatedFKColumns = inFKCols
        self.__mName = inName
        self.__mIndex = -1

    @property
    def Name(self):
        return self.__mName

    @property
    def Index(self):
        return self.__mIndex

    @Index.setter
    def Index(self, inIdx: int):
        self.__mIndex = inIdx

    @property
    def RelatedFKColumns(self) -> list[str]:
        return self.__mRelatedFKColumns


class ForeignKey:
    def __init__(self):
        self.__mReferenceTableSchema = None
        self.__mReferenceTable = None
        self.__mForeignKeyMap = None

    @property
    def ForeignKeyMap(self) -> dict:
        return self.__mForeignKeyMap

    @ForeignKeyMap.setter
    def ForeignKeyMap(self, inForeignKeyMap: dict):
        self.__mForeignKeyMap = inForeignKeyMap

    @property
    def ReferenceTable(self) -> str:
        return self.__mReferenceTable

    @ReferenceTable.setter
    def ReferenceTable(self, inReferenceTable: str):
        self.__mReferenceTable = inReferenceTable

    @property
    def ReferenceTableSchema(self) -> str:
        return self.__mReferenceTableSchema

    @ReferenceTableSchema.setter
    def ReferenceTableSchema(self, inReferenceTableSchema: str):
        self.__mReferenceTableSchema = inReferenceTableSchema


class ColumnMetadata(Parsable):
    def __init__(self):
        self.__mSourceType = ''
        self.__mScale = 0
        self.__mSQLType = None
        self.__mPrecision = 0
        self.__mLength = 0
        self.__mIsUnsigned = False

    def parse(self, inData):
        """Parses Column's Metadata content"""
        assert isinstance(inData, dict)
        for key, val in inData.items():
            if Constants.SQLTYPE.value == key:
                self.__mSQLType = val
            elif Constants.SOURCETYPE.value == key:
                self.__mSourceType = val
            elif Constants.LENGTH.value == key:
                self.__mLength = val
            elif Constants.PRECISION.value == key:
                self.__mPrecision = val
            elif Constants.SCALE.value == key:
                self.__mScale = val
            elif Constants.ISUNSIGNED.value == key:
                self.__mIsUnsigned = val
            else:
                raise Exception(f'Unhandled key encountered: {key}')
        return self


    @property
    def IsUnsigned(self) -> bool:
        return self.__mIsUnsigned

    @IsUnsigned.setter
    def IsUnsigned(self, isUnsigned: bool):
        self.__mIsUnsigned = isUnsigned

    @property
    def Length(self) -> int:
        return self.__mLength

    @Length.setter
    def Length(self, inLength: int):
        self.__mLength = inLength

    @property
    def Precision(self) -> int:
        return self.__mPrecision

    @Precision.setter
    def Precision(self, inPrecision: int):
        self.__mPrecision = inPrecision

    @property
    def Scale(self) -> int:
        return self.__mScale

    @Scale.setter
    def Scale(self, inScale: int):
        self.__mScale = inScale

    @property
    def SQLType(self) -> str:
        return self.__mSQLType

    @SQLType.setter
    def SQLType(self, inSQLType: str):
        self.__mSQLType = inSQLType

    @property
    def SourceType(self) -> str:
        return self.__mSourceType

    @SourceType.setter
    def SourceType(self, inSourceType: str):
        self.__mSourceType = inSourceType


class Column(Parsable):
    def __init__(self):
        self.__mName = ''
        self.__mReturnIdPath = ''
        self.__mPushdownMapping = ''
        self.__mQueryMapping = ''
        self.__mItemResult = ''
        self.__mListResult = ''
        self.__mMetadata = None
        self.__mPassdownable = False
        self.__mUpdatable = False
        self.__mNullable = False
        self.__mSyntheticIndexColumn = False

    def parse(self, inData):
        """Parses Column MDEF Content"""
        assert isinstance(inData, dict)
        for key, val in inData.items():
            if Constants.NAME.value == key:
                self.__mName = val
            elif Constants.METADATA.value == key:
                self.__mMetadata = ColumnMetadata().parse(inData[Constants.METADATA.value])
            elif Constants.NULLABLE.value == key:
                self.__mNullable = val
            elif Constants.UPDATABLE.value == key:
                self.__mUpdatable = val
            elif Constants.PASSDOWNABLE.value == key:
                self.__mPassdownable = val
            elif Constants.SVCRESPATTR_LISTRESULT.value == key:
                self.__mListResult = val
            elif Constants.SVCRESPATTR_ITEMRESULT.value == key:
                self.__mItemResult = val
            elif Constants.SVCREQPARAM_QUERYMAPPING.value == key:
                self.__mQueryMapping = val
            elif Constants.SVCRESPATTR_RETURNIDPATH.value == key:
                self.__mReturnIdPath = val
            elif Constants.COLUMNPUSHDOWN_MAPPING.value == key:
                self.__mPushdownMapping = val
            elif Constants.SYNTHETICINDEXCOLUMN.value == key:
                # self.__mSyntheticIndexColumn = val
                # Virtual table not supported yet
                pass
        return self

    @property
    def Name(self):
        return self.__mName

    @Name.setter
    def Name(self, inName: str):
        self.__mName = inName

    @property
    def SyntheticIndexColumn(self) -> bool:
        return self.__mSyntheticIndexColumn

    @SyntheticIndexColumn.setter
    def SyntheticIndexColumn(self, isSyntheticIndexColumn: bool):
        self.__mSyntheticIndexColumn = isSyntheticIndexColumn

    @property
    def Nullable(self) -> bool:
        return self.__mNullable

    @Nullable.setter
    def Nullable(self, isNullable: bool):
        self.__mNullable = isNullable

    @property
    def Updatable(self) -> bool:
        return self.__mUpdatable

    @Updatable.setter
    def Updatable(self, isUpdatable: bool):
        self.__mUpdatable = isUpdatable

    @property
    def Passdownable(self) -> bool:
        return self.__mPassdownable

    @Passdownable.setter
    def Passdownable(self, isPassdownable: bool):
        self.__mPassdownable = isPassdownable

    @property
    def Metadata(self) -> ColumnMetadata:
        return self.__mMetadata

    @Metadata.setter
    def Metadata(self, inMetadata: ColumnMetadata):
        self.__mMetadata = inMetadata

    @property
    def ListResult(self) -> str:
        return self.__mListResult

    @ListResult.setter
    def ListResult(self, inListResult: str):
        self.__mListResult = inListResult

    @property
    def ItemResult(self) -> str:
        return self.__mItemResult

    @ItemResult.setter
    def ItemResult(self, inItemResult: str):
        self.__mItemResult = inItemResult

    @property
    def QueryMapping(self) -> str:
        return self.__mQueryMapping

    @QueryMapping.setter
    def QueryMapping(self, inQueryMapping: str):
        self.__mQueryMapping = inQueryMapping

    @property
    def PushdownMapping(self) -> str:
        return self.__mPushdownMapping

    @PushdownMapping.setter
    def PushdownMapping(self, inPushdownMapping: str):
        self.__mPushdownMapping = inPushdownMapping

    @property
    def ReturnIdPath(self) -> str:
        return self.__mReturnIdPath

    @ReturnIdPath.setter
    def ReturnIdPath(self, inReturnIdPath: str):
        self.__mReturnIdPath = inReturnIdPath


class ReqParamKey(Parsable):
    def __init__(self):
        self.__mRespAttrField = None
        self.__mKeyName = None
        self.__mMaxValuesPerCall = 0
        self.__mIsReferenced = False
        self.__mIsParameter = False

    def parse(self, inData):
        """Parses SvcReqParamKeys MDEF Content"""
        assert isinstance(inData, dict)
        for key, val in inData.items():
            if Constants.KEYNAME.value == key:
                self.__mKeyName = val
            elif Constants.SVCRESPATTRFIELD.value == key:
                self.__mRespAttrField = val
            elif Constants.ISREFERENCED.value == key:
                self.__mIsReferenced = val
            elif Constants.ISPARAMETER.value == key:
                self.__mIsParameter = val
            elif Constants.MAXVALUESPERCALL.value == key:
                self.__mMaxValuesPerCall = val
            else:
                # TODO: Remove pass once all the keys are handled
                pass
                # raise Exception(f'Unhandled key encountered: {key}')
        return self

    @property
    def IsParameter(self) -> bool:
        return self.__mIsParameter

    @IsParameter.setter
    def IsParameter(self, isParameter: bool):
        self.__mIsParameter = isParameter

    @property
    def IsReferenced(self) -> bool:
        return self.__mIsReferenced

    @IsReferenced.setter
    def IsReferenced(self, isIsReferenced: bool):
        self.__mIsReferenced = isIsReferenced

    @property
    def MaxValuesPerCall(self) -> int:
        return self.__mMaxValuesPerCall

    @MaxValuesPerCall.setter
    def MaxValuesPerCall(self, isMaxValuesPerCall: int):
        self.__mMaxValuesPerCall = isMaxValuesPerCall

    @property
    def KeyName(self) -> int:
        return self.__mKeyName

    @KeyName.setter
    def KeyName(self, inKeyName: int):
        self.__mKeyName = inKeyName

    @property
    def RespAttrField(self) -> str:
        return self.__mRespAttrField

    @RespAttrField.setter
    def RespAttrField(self, inRespAttrField: str):
        self.__mRespAttrField = inRespAttrField


class PreReqCall(Parsable):
    def __init__(self):
        self.__mPageable = False
        self.__mPagination = None
        self.__mReqParamKeys = list()
        self.__mChildPreReqCall = None
        self.__mListRoot = None
        self.__mParameterFormat = None
        self.__mEndpoint = None

    def parse(self, inData):
        """Parses PreReqCall MDEF Content"""
        assert isinstance(inData, dict)
        for key, val in inData.items():
            if Constants.ENDPOINT.value == key:
                self.__mEndpoint = val
            elif Constants.ROOT.value == key:
                self.__mListRoot = val
            elif Constants.PAGEABLE.value == key:
                self.__mPageable = val
            elif Constants.PARAMETERFORMAT.value == key:
                self.__mParameterFormat = val
            elif Constants.PREREQCALL.value == key:
                self.__mChildPreReqCall = PreReqCall().parse(val)
            elif Constants.SVCREQPARAMKEYS.value == key:
                for item in val:
                    self.__mReqParamKeys.append(ReqParamKey().parse(item))
            elif Constants.PAGINATION.value == key:
                self.__mPagination = Pagination(val[Constants.PAGINATIONTYPE.value])
            else:
                # TODO: Remove pass once all the keys are handled
                pass
                # raise Exception(f'Unhandled key encountered: {key}')
        return self

    @property
    def Endpoint(self):
        return self.__mEndpoint

    @Endpoint.setter
    def Endpoint(self, inEndpoint: str):
        self.__mEndpoint = inEndpoint

    @property
    def ReqParamKeys(self) -> list[ReqParamKey]:
        return self.__mReqParamKeys

    @ReqParamKeys.setter
    def ReqParamKeys(self, inReqParamKeys: list[ReqParamKey]):
        self.__mReqParamKeys = inReqParamKeys

    @property
    def ParameterFormat(self):
        return self.__mParameterFormat

    @ParameterFormat.setter
    def ParameterFormat(self, inParameterFormat: str):
        self.__mParameterFormat = inParameterFormat

    @property
    def ListRoot(self):
        return self.__mListRoot

    @ListRoot.setter
    def ListRoot(self, inListRoot: str):
        self.__mListRoot = inListRoot

    @property
    def ChildPreReqCall(self):
        return self.__mChildPreReqCall

    @ChildPreReqCall.setter
    def ChildPreReqCall(self, inChildPreReqCall):
        self.__mChildPreReqCall = inChildPreReqCall

    @property
    def Pageable(self) -> bool:
        return self.__mPageable

    @Pageable.setter
    def Pageable(self, isPageable: bool):
        self.__mPageable = isPageable

    @property
    def Pagination(self) -> Pagination:
        return self.__mPagination


class Endpoint(Parsable):
    def __init__(self):
        self.__mItemEndpointArrayResponse = False
        self.__mPreReqCall = None
        self.__mType = None
        self.__mItemEndpoint = None
        self.__mListEndpoint = None

    def parse(self, inData):
        """Parses Endpoint MDEF Content"""
        assert isinstance(inData, dict)
        for key, val in inData.items():
            if Constants.LISTENDPOINT.value == key:
                self.__mListEndpoint = val
            elif Constants.ITEMENDPOINT.value == key:
                self.__mItemEndpoint = val
            elif Constants.ITEMENDPOINTHASARRAYRESPONSE.value == key:
                self.__mItemEndpointArrayResponse = val
            elif Constants.TYPE.value == key:
                self.__mType = val
            elif Constants.PREREQCALL.value == key:
                self.__mPreReqCall = PreReqCall().parse(val)
            else:
                # TODO: Remove pass once all the keys are handled
                pass
                # raise Exception(f'Unhandled key encountered: {key}')
        return self

    @property
    def ListEndpoint(self) -> str:
        return self.__mListEndpoint

    @ListEndpoint.setter
    def ListEndpoint(self, inListEndpoint: str):
        self.__mListEndpoint = inListEndpoint

    @property
    def ItemEndpoint(self):
        return self.__mItemEndpoint

    @ItemEndpoint.setter
    def ItemEndpoint(self, inItemEndpoint: str):
        self.__mItemEndpoint = inItemEndpoint

    @property
    def ItemEndpointHasArrayResponse(self) -> bool:
        return self.__mItemEndpointArrayResponse

    @ItemEndpointHasArrayResponse.setter
    def ItemEndpointHasArrayResponse(self, inItemEndpointHasArrayResponse: bool):
        self.__mItemEndpointArrayResponse = inItemEndpointHasArrayResponse

    @property
    def Type(self):
        return self.__mType

    @Type.setter
    def Type(self, inType: str):
        self.__mType = inType

    @property
    def PreReqCall(self):
        return self.__mPreReqCall

    @PreReqCall.setter
    def PreReqCall(self, inPreReqCall: str):
        self.__mPreReqCall = inPreReqCall


class ReadAPI(Parsable):
    # TODO: Add HttpModifiers support

    __paramformat__ = {
        'BODY': 'PARAM_FORMAT_BODY',
        'URL': 'PARAM_FORMAT_URL',
        'QUERY': 'PARAM_FORMAT_QUERY'
    }

    def __init__(self):
        self.__mItemRoot = None
        self.__mListRoot = None
        self.__mParameterFormat = None
        self.__mContentType = None
        self.__mAccept = None
        self.__mDataPath = None
        self.__mBodySkeleton = None
        self.__mMethod = None
        self.__mColumnReq = list()
        self.__mEndpoint = None

    def parse(self, inData):
        """Parses ReadAPI MDEF Content"""
        assert isinstance(inData, dict)
        for key, val in inData.items():
            if Constants.METHOD.value == key:
                self.__mMethod = val
            elif Constants.COLUMNREQUIREMENTS.value == key:
                self.__mColumnReq = val
            elif Constants.BODYSKELETON.value == key:
                self.__mBodySkeleton = val
            elif Constants.DATAPATH.value == key:
                self.__mDataPath = val
            elif Constants.ENDPOINT.value == key:
                self.__mEndpoint = Endpoint().parse(val)
            elif Constants.ACCEPT.value == key:
                self.__mAccept = val
            elif Constants.CONTENTTYPE.value == key:
                self.__mContentType = val
            elif Constants.PARAMETERFORMAT.value == key:
                self.__mParameterFormat = ReadAPI.__paramformat__[val.upper()]
            elif Constants.LISTROOT.value == key:
                self.__mListRoot = val
            elif Constants.ITEMROOT.value == key:
                self.__mItemRoot = val
            else:
                # TODO: Remove pass once all keys handled
                pass
                # raise Exception(f'Unhandled key encountered: {key}')
        return self

    @property
    def Method(self):
        return self.__mMethod

    @Method.setter
    def Method(self, inMethod: str):
        self.__mMethod = inMethod

    @property
    def ColumnRequirements(self):
        return self.__mColumnReq

    @ColumnRequirements.setter
    def ColumnRequirements(self, inColumnRequirements: list[str]):
        self.__mColumnReq = inColumnRequirements

    @property
    def Endpoint(self):
        return self.__mEndpoint

    @Endpoint.setter
    def Endpoint(self, inEndpoint: Endpoint):
        self.__mEndpoint = inEndpoint

    @property
    def BodySkeleton(self):
        return self.__mBodySkeleton

    @BodySkeleton.setter
    def BodySkeleton(self, inBodySkeleton: str):
        self.__mBodySkeleton = inBodySkeleton

    @property
    def DataPath(self):
        return self.__mDataPath

    @DataPath.setter
    def DataPath(self, inDataPath: str):
        self.__mDataPath = inDataPath

    @property
    def Accept(self):
        return self.__mAccept

    @Accept.setter
    def Accept(self, inAccept: str):
        self.__mAccept = inAccept

    @property
    def ContentType(self):
        return self.__mContentType

    @ContentType.setter
    def ContentType(self, inContentType: str):
        self.__mContentType = inContentType

    @property
    def ParameterFormat(self):
        return self.__mParameterFormat

    @ParameterFormat.setter
    def ParameterFormat(self, inParameterFormat: str):
        self.__mParameterFormat = ReadAPI.__paramformat__[inParameterFormat.upper()]

    @property
    def ListRoot(self):
        return self.__mListRoot

    @ListRoot.setter
    def ListRoot(self, inListRoot: str):
        self.__mListRoot = inListRoot

    @property
    def ItemRoot(self):
        return self.__mItemRoot

    @ItemRoot.setter
    def ItemRoot(self, inItemRoot: str):
        self.__mItemRoot = inItemRoot


class Table(Parsable):
    def __init__(self):
        self.__mReadAPI = None
        self.__mColumns = list()
        self.__mForeignKeys = list()
        self.__mPrimaryKeys = list()
        self.__mColumnPushdown = None
        self.__mTableSchemaName = None
        self.__mItemEndpointColumnNames = list()
        self.__mPageable = None
        self.__mSortable = None
        self.__mName = None
        self.__mPagination = None

    def parse(self, inData):
        """Parses Tables MDEF Content"""
        assert isinstance(inData, dict)
        for key, val in inData.items():
            if Constants.TABLENAME.value == key:
                self.__mName = MDEF.cleanName(val)
            elif Constants.TABLESCHEMANAME.value == key:
                self.__mTableSchemaName = val
            elif Constants.PKEYCOLUMN.value == key:
                for pKeyDataOut in val.values():
                    for pKeyData in pKeyDataOut:
                        self.__mPrimaryKeys.append(PrimaryKey(
                            pKeyData[Constants.PKCOLUMNNAME.value],
                            pKeyData[Constants.RELATEDFKCOLUMNS.value]
                            if Constants.RELATEDFKCOLUMNS.value in pKeyData else None)
                        )
            elif Constants.ITEMENDPOINTCOLUMNNAMES.value == key:
                self.__mItemEndpointColumnNames = val
            elif Constants.SORTABLE.value == key:
                self.__mSortable = val
            elif Constants.PAGEABLE.value == key:
                self.__mPageable = val
            elif Constants.PAGINATION.value == key:
                self.__mPagination = Pagination(val[Constants.PAGINATIONTYPE.value])
            elif Constants.COLUMNPUSHDOWN.value == key:
                self.__mColumnPushdown = ColumnPushdown().parse(val)
            elif Constants.COLUMNS.value == key:
                for colData in val:
                    self.__mColumns.append(Column().parse(colData))
            elif Constants.APIACCESS.value == key:
                # TODO: Support DML operations
                for apiName, apiData in val.items():
                    if Constants.READAPI.value == apiName:
                        self.__mReadAPI = ReadAPI().parse(apiData)
                pass
            else:
                # TODO: Remove pass once VTables implemented
                pass
                # raise Exception(f'Unhandled Key encountered: {key}')
        return self

    @property
    def Name(self) -> str:
        return self.__mName

    @Name.setter
    def Name(self, inName: str):
        self.__mName = inName

    @property
    def PaginationType(self) -> Pagination:
        return self.__mPagination

    @PaginationType.setter
    def PaginationType(self, inType: Pagination):
        self.__mPagination = inType

    @property
    def Sortable(self) -> bool:
        return self.__mSortable

    @Sortable.setter
    def Sortable(self, isSortable: bool):
        self.__mSortable = isSortable

    @property
    def Pageable(self) -> bool:
        return self.__mPageable

    @Pageable.setter
    def Pageable(self, isPageable: bool):
        self.__mPageable = isPageable

    @property
    def ItemEndpointColumnNames(self) -> list:
        return self.__mItemEndpointColumnNames

    @ItemEndpointColumnNames.setter
    def ItemEndpointColumnNames(self, inItemEndpointColumnNames: list[str]):
        self.__mItemEndpointColumnNames = inItemEndpointColumnNames

    @property
    def TableSchemaName(self) -> str:
        return self.__mTableSchemaName

    @TableSchemaName.setter
    def TableSchemaName(self, inTableSchemaName: str):
        self.__mTableSchemaName = inTableSchemaName

    @property
    def ColumnPushdown(self) -> ColumnPushdown:
        return self.__mColumnPushdown

    @ColumnPushdown.setter
    def ColumnPushdown(self, inColumnPushdown: ColumnPushdown):
        self.__mColumnPushdown = inColumnPushdown

    @property
    def PrimaryKeys(self) -> list[PrimaryKey]:
        return self.__mPrimaryKeys

    @PrimaryKeys.setter
    def PrimaryKeys(self, inPrimaryKeys: list[PrimaryKey]):
        self.__mPrimaryKeys = inPrimaryKeys

    @property
    def ForeignKeys(self) -> list[ForeignKey]:
        return self.__mForeignKeys

    @ForeignKeys.setter
    def ForeignKeys(self, inForeignKey: list[ForeignKey]):
        self.__mForeignKeys = inForeignKey

    @property
    def Columns(self) -> list[Column]:
        return self.__mColumns

    @Columns.setter
    def Columns(self, inColumns: list[Column]):
        self.__mColumns = inColumns

    @property
    def ReadAPI(self) -> ReadAPI:
        return self.__mReadAPI

    @property
    def FullName(self):
        return f'{self.__mTableSchemaName}{self.__mName}'


class SkeletonTable(Table):
    pass


class Header:
    def __init__(self, inKey: str, inValue: str):
        self.__mKey = inKey
        self.__mValue = inValue

    @property
    def Key(self):
        return self.__mKey

    @property
    def Value(self):
        return self.__mValue


class ExpectedParam:
    def __init__(self, inKey: str, inPath: str):
        self.__mKey = inKey
        self.__mPath = inPath

    @property
    def Key(self):
        return self.__mKey

    @property
    def Path(self):
        return self.__mPath


class AuthSequence:
    def __init__(self, inReqParams: list, inHeaders: list[Header], inExpParams: list[ExpectedParam]):
        self.__mHeaders = inHeaders
        self.__mReqParams = inReqParams
        self.__mExpParams = inExpParams

    @property
    def Headers(self):
        return self.__mHeaders

    @property
    def RequiredParams(self):
        return self.__mReqParams

    @property
    def ExpectedParams(self):
        return self.__mExpParams


class AuthFlow(Parsable):
    def __init__(self):
        self.__mName = None
        self.__mAuthSequences = None

    def parse(self, inData):
        """Parses AuthFlow MDEF Content"""
        assert isinstance(inData, dict)
        flowName, sequences = None, list()
        if Constants.NAME.value in inData:
            flowName = inData[Constants.NAME.value]
        if Constants.SEQUENCE.value in inData:
            for seq in inData[Constants.SEQUENCE.value]:
                reqParams = list()
                expParams = list()
                headers = list()
                if Constants.REQUIREDPARAMS.value in seq:
                    for param in seq[Constants.REQUIREDPARAMS.value]:
                        reqParams.append(param[Constants.KEY.value])
                if Constants.EXPECTEDPARAMS.value in seq:
                    for param in seq[Constants.EXPECTEDPARAMS.value]:
                        expParams.append(ExpectedParam(param[Constants.KEY.value], param[Constants.PATH.value]))
                if Constants.HEADERS.value in seq:
                    for item in seq[Constants.HEADERS.value]:
                        headers.append(Header(item[Constants.KEY.value], item[Constants.VALUE.value]))
                sequences.append(AuthSequence(reqParams, headers, expParams))
        self.__mName = flowName
        self.__mAuthSequences = sequences
        return self

    @property
    def Name(self):
        return self.__mName

    @property
    def AuthSequences(self):
        return self.__mAuthSequences


class AuthProfile:
    def __init__(self, inName: str, inAuthFlows: list[AuthFlow]):
        self.__mName = inName
        self.__mAuthFlows = inAuthFlows

    @property
    def Name(self):
        return self.__mName

    @property
    def AuthFlows(self):
        return self.__mAuthFlows


class AuthProfiles(Parsable):
    def __init__(self):
        self.__mVerifyPeer = None
        self.__mVerifyHost = None
        self.__mAuthWindowWidth = None
        self.__mAuthWindowHeight = None
        self.__mRefreshTokenWithinRange = None
        self.__mIsAutoRefreshSupported = None
        self.__mIsExpirationDataAvailable = None
        self.__mTokenType = None
        self.__mAuthProfiles = list()

    def parse(self, inData):
        """Parses AuthProfiles MDEF Content"""
        assert isinstance(inData, dict)
        for name, value in inData.items():
            if name == 'Types':
                continue
            elif isinstance(value, list):
                authFlows = list()
                for authFlow in value:
                    authFlows.append(AuthFlow().parse(authFlow))
                self.__mAuthProfiles.append(AuthProfile(name, authFlows))
            else:
                if name == Constants.TOKENTYPE.value:
                    self.__mTokenType = value
                elif name == Constants.AUTH_WINDOWHEIGHT.value:
                    self.__mAuthWindowHeight = value
                elif name == Constants.AUTH_WINDOWWIDTH.value:
                    self.__mAuthWindowWidth = value
                elif name == Constants.ISAUTOREFRESHSUPPORTED.value:
                    self.__mIsAutoRefreshSupported = value
                elif name == Constants.ISEXPIRATIONDATAAVAILABLE.value:
                    self.__mIsExpirationDataAvailable = value
                elif name == Constants.REFRESHTOKENWITHINRANGE.value:
                    self.__mRefreshTokenWithinRange = value
                elif name == Constants.VERIFYHOST.value:
                    self.__mVerifyHost = value
                elif name == Constants.VERIFYPEER.value:
                    self.__mVerifyPeer = value
                else:
                    # TODO: Remove pass once all params can be well handled by script
                    # raise Exception(f'Unhandled Key encountered: {name}')
                    pass
        return self

    @property
    def TokenType(self):
        return self.__mTokenType

    @TokenType.setter
    def TokenType(self, inVal: str):
        self.__mTokenType = inVal

    @property
    def IsExpirationDataAvailable(self):
        return self.__mIsExpirationDataAvailable

    @IsExpirationDataAvailable.setter
    def IsExpirationDataAvailable(self, inVal: str):
        self.__mIsExpirationDataAvailable = inVal

    @property
    def IsAutoRefreshSupported(self):
        return self.__mIsAutoRefreshSupported

    @IsAutoRefreshSupported.setter
    def IsAutoRefreshSupported(self, inVal: str):
        self.__mIsAutoRefreshSupported = inVal

    @property
    def RefreshTokenWithinRange(self):
        return self.__mRefreshTokenWithinRange

    @RefreshTokenWithinRange.setter
    def RefreshTokenWithinRange(self, inVal: str):
        self.__mRefreshTokenWithinRange = inVal

    @property
    def AuthWindowHeight(self):
        return self.__mAuthWindowHeight

    @AuthWindowHeight.setter
    def AuthWindowHeight(self, inVal: str):
        self.__mAuthWindowHeight = inVal

    @property
    def AuthWindowWidth(self):
        return self.__mAuthWindowWidth

    @AuthWindowWidth.setter
    def AuthWindowWidth(self, inVal: str):
        self.__mAuthWindowWidth = inVal

    @property
    def VerifyHost(self):
        return self.__mVerifyHost

    @VerifyHost.setter
    def VerifyHost(self, inVal: str):
        self.__mVerifyHost = inVal

    @property
    def VerifyPeer(self):
        return self.__mVerifyPeer

    @VerifyPeer.setter
    def VerifyPeer(self, inVal: str):
        self.__mVerifyPeer = inVal

    @property
    def AllProfiles(self) -> list[AuthProfile]:
        return self.__mAuthProfiles


class MDEF:
    """Represents MDEF class"""

    def __init__(self, inMDEFContent: dict):
        self.__mContent = inMDEFContent
        self.__mCache = OrderedDict()
        self.__parse()

    def __parse(self):
        try:
            self.__mDataSource = self.__mContent[Constants.DATASOURCE.value]
            self.__mBaseURL = self.__mContent[Constants.BASEURL.value]
            self.__mTestURLEndpoint = self.__mContent[Constants.TESTURLENDPOINT.value]
            self.__mTimeStampFormat = self.__mContent[Constants.TIMESTAMPFORMAT.value]
            self.__mIsUnixTimeStamp = self.__mContent[Constants.ISUNIXTIMESTAMPFORMAT.value]
            self.__mTimeStampUnit = self.__mContent[Constants.TIMESTAMPUNIT.value]
            self.__mIsLazyInitialization = self.__mContent[Constants.ISLAZYINITIALIZATION.value]
            self.__mDoesServerSupportThrottling = self.__mContent[Constants.DOESSERVERSUPPORTTHROTTLING.value]

            # Parses Auth Browse Connect Map
            self.__mAuthBrowseConnectMap = list()
            for item in self.__mContent[Constants.AUTHBROWSECONNECTMAP.value]:
                self.__mAuthBrowseConnectMap.append(AuthBrowseConnectMap().parse(item))

            # Parses Auth profiles
            self.__mAuthProfiles = AuthProfiles().parse(self.__mContent[Constants.AUTHPROFILES.value])

            # Parses GLobal pagination
            if Constants.PAGINATION.value in self.__mContent:
                self.__mGlobalPagination = Pagination(
                    self.__mContent[Constants.PAGINATION.value][Constants.PAGINATIONTYPE.value]
                )

            # Parse tables
            self.__mTables = list()
            for tableData in self.__mContent[Constants.TABLES.value]:
                self.__mTables.append(Table().parse(tableData))

            # Parse SkeletonTables
            self.__mSkeletonTables = list()
            if Constants.SKELETONTABLE.value in self.__mContent:
                for tableData in self.__mContent[Constants.SKELETONTABLE.value]:
                    skeletonTable = SkeletonTable()
                    tableData = tableData['TableDefinition']
                    skeletonTable.Name = MDEF.cleanName(tableData[Constants.TABLENAME.value])
                    if Constants.TABLESCHEMANAME.value in tableData:
                        skeletonTable.TableSchemaName = tableData[Constants.TABLESCHEMANAME.value]
                    self.__mSkeletonTables.append(skeletonTable)
        except KeyError as error:
            print(f'{error} key not found in MDEF')
            sys.exit(1)
        except Exception as error:
            print(f'Error: {error}')
            sys.exit(1)

    @property
    def AuthProfiles(self):
        return self.__mAuthProfiles

    @property
    def PaginationType(self):
        return self.__mGlobalPagination

    @property
    def DataSource(self):
        return self.__mDataSource

    @property
    def BaseURL(self):
        return self.__mBaseURL

    @property
    def TestURLEndpoint(self):
        return self.__mTestURLEndpoint

    @property
    def TimestampFormat(self):
        return self.__mTimeStampFormat

    @property
    def IsUnixTimeStampFormat(self):
        return self.__mIsUnixTimeStamp

    @property
    def TimestampUnit(self):
        return self.__mTimeStampUnit

    @property
    def IsLazyInitialization(self):
        return self.__mIsLazyInitialization

    @property
    def DoesServerSupportThrottling(self):
        return self.__mDoesServerSupportThrottling

    @property
    def AuthBrowseConnectMap(self):
        return self.__mAuthBrowseConnectMap

    @property
    def Tables(self):
        return self.__mTables

    @property
    def SkeletonTables(self):
        return self.__mSkeletonTables

    def __check(self, inKey: str, inSource: dict):
        """Checks if given key is present in Source"""
        return inKey in inSource

    @staticmethod
    def cleanName(inName: str):
        """Removes Variable placeholders and separators"""
        inName = inName.replace('_', '')
        startIdx = inName.find('{{')
        if startIdx == -1:
            return inName
        else:
            endIdx = inName.find('}}')
            return f'{inName[:startIdx]}{inName[endIdx + 2:]}'

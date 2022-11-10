"""
Contains definition of Configurable classes
"""

from abc import abstractmethod
from MDEF import *
from Util import File


class Configurable:
    """Represents Configurable abstract class"""

    @staticmethod
    @abstractmethod
    def Configure(inMDEF: MDEF, inOutputDir: str):
        pass


class ConfigurationCPP(Configurable):
    """Represents a class that writes Configuration.cpp"""

    @staticmethod
    def Configure(inMDEF: MDEF, inOutputDir: str):
        writer = File('Configuration.cpp', f'{inMDEF.DataSource} Driver Configuration', inOutputDir)
        writer.write('#include "Configuration.h"\n')
        writer.write('#include "ConfigurationHelpers.h"\n')
        writer.write('#include "Authentication/IAuthenticationHandler.h"\n')
        writer.write('#include "Authentication/SaaSAuthenticationFactory.h"\n')
        writer.write('#include "Pagination/SaaSPaginationFactory.h"\n')
        writer.write('#include "Pagination/IPaginationHandler.h"\n')
        writer.write('#include "Parser/IParserHandler.h"\n')
        writer.write('#include "Parser/SaaSParserFactory.h"\n')
        writer.write('#include "SimbaEngine/SharedPtr.h"\n\n')
        writer.write('using namespace Simba::SaaSSDK;\n')
        writer.write(f'using namespace Simba::SaaSSDK::{inMDEF.DataSource}ODBC;\n\n')
        writer.write('AutoPtr<ISaaSStaticConfiguration> Simba::SaaSSDK::SaaSSDKDSIFactory()\n{\n'
                     '\treturn AutoPtr<ISaaSStaticConfiguration>(new ' + inMDEF.DataSource + 'ODBCStaticConfiguration);\n}\n')
        writer.write(f'void {inMDEF.DataSource}ODBCStaticConfiguration::PopulateMetaDataConfiguration('
                     'SaaSConfiguration& out_configs)\n'
                     '{\n'
                     '\t// Base configuration\n'
                     '\t{\n'
                     f'\t\tout_configs.SetDataSource("{inMDEF.DataSource}");\n'
                     f'\t\tout_configs.SetBaseUrl("{inMDEF.BaseURL}");\n'
                     f'\t\tout_configs.SetTestUrlEndpoint("{inMDEF.TestURLEndpoint}");\n'
                     f'\t\tout_configs.SetTimestampFormat("{inMDEF.TimestampFormat}");\n'
                     f'\t\tout_configs.SetIsUnixTimeStampFormat({str(inMDEF.IsUnixTimeStampFormat).lower()});\n'
                     f'\t\tout_configs.SetTimestampUnit({inMDEF.TimestampUnit});\n'
                     f'\t\tout_configs.SetIsLazyInitialization({str(inMDEF.IsLazyInitialization).lower()});\n'
                     f'\t\tout_configs.SetIsThrothrottlingSupported({str(inMDEF.DoesServerSupportThrottling).lower()});\n'
                     '\t}\n')
        # prepares AuthBrowseConnectMap
        writer.write('\t// AuthBrowseConnectMap\n'
                     '\t{\n')
        for idx, authBrowseData in enumerate(inMDEF.AuthBrowseConnectMap):
            key = authBrowseData.Key
            encKey = authBrowseData.EncBrowseConnectKey
            writer.write(f'\t\tSaaSAuthBrowseConnectMap map{key.replace("_", "")};\n')
            writer.write(f'\t\tmap{key.replace("_", "")}.SetKey("{key}");\n')
            if encKey is not None:
                writer.write(f'\t\tmap{key.replace("_", "")}.SetEncBrowseConnectKey("{encKey}");\n')
            writer.write(f'\t\tout_configs.GetAuthBrowseConnectMap().insert('
                         f'{"{"}"{key}" , map{key.replace("_", "")}{"}"});\n')
            writer.write('\n' if idx != len(inMDEF.AuthBrowseConnectMap) - 1 else '')
        writer.write('\t}\n')

        # prepares AuthProfiles
        writer.write('\t// AuthProfiles\n'
                     '\t{\n'
                     '\t\tSaaSAuthProfiles authProfile;\n')
        for idx, profile in enumerate(inMDEF.AuthProfiles.AllProfiles):
            if len(profile.AuthFlows) == 0:
                continue
            writer.write(f'\t\t// {profile.Name}\n')
            writer.write('\t\t{\n')
            writer.write(
                f'\t\t\tstd::vector<SaaSAuthSequence> authSeq{profile.Name.replace(" ", "").replace(".", "")};\n')
            writer.write('\t\t\t{\n')
            for authFlow in profile.AuthFlows:
                writer.write(f'\t\t\t\t// {authFlow.Name}\n')
                for flowIdx, authSeq in enumerate(authFlow.AuthSequences):
                    writer.write(f'\t\t\t\tSaaSBrowseConnectSequence browseSeq{authFlow.Name}{flowIdx + 1};\n')
                    writer.write('\t\t\t\t{\n')
                    for reqParam in authSeq.RequiredParams:
                        writer.write(f'\t\t\t\t\tSaaSRequiredParam reqParam{reqParam.replace("_", "")};\n')
                        writer.write(f'\t\t\t\t\treqParam{reqParam.replace("_", "")}.SetKey("{reqParam}");\n')
                        writer.write(f'\t\t\t\t\tbrowseSeq{authFlow.Name}{flowIdx + 1}.GetRequiredParams().'
                                     f'push_back(reqParam{reqParam.replace("_", "")});\n\n')

                    for headerIdx, header in enumerate(authSeq.Headers):
                        writer.write(f'\t\t\t\t\tSaaSHeader header{headerIdx + 1};\n')
                        writer.write(f'\t\t\t\t\theader{headerIdx + 1}.SetKey("{header.Key}");\n')
                        writer.write(f'\t\t\t\t\theader{headerIdx + 1}.SetValue("{header.Value}");\n')
                        writer.write(
                            f'\t\t\t\t\tbrowseSeq{authFlow.Name}{flowIdx + 1}.GetHeaders().push_back(header{headerIdx + 1});\n\n')

                    for expParam in authSeq.ExpectedParams:
                        writer.write(f'\t\t\t\t\tSaaSExpectedParam expParam{expParam.Key.replace("_", "")};\n')
                        writer.write(f'\t\t\t\t\texpParam{expParam.Key.replace("_", "")}.SetKey("{expParam.Key}");\n')
                        writer.write(f'\t\t\t\t\texpParam{expParam.Key.replace("_", "")}.SetPath("{expParam.Path}");\n')
                        writer.write(f'\t\t\t\t\tbrowseSeq{authFlow.Name}{flowIdx + 1}.GetExpectedParams().'
                                     f'push_back(expParam{expParam.Key.replace("_", "")});\n\n')
                    writer.write('\t\t\t\t}\n')

                writer.write(f'\t\t\t\tSaaSAuthSequence authSeq{authFlow.Name};\n')
                writer.write(f'\t\t\t\tauthSeq{authFlow.Name}.SetName("{authFlow.Name}");\n')
                for _ in range(1, len(authFlow.AuthSequences) + 1):
                    writer.write(f'\t\t\t\tauthSeq{authFlow.Name}.GetSequence().push_back('
                                 f'browseSeq{authFlow.Name}{_});\n')
                writer.write(
                    f'\t\t\t\tauthSeq{profile.Name.replace(" ", "").replace(".", "")}.push_back(authSeq{authFlow.Name});\n')
                writer.write('\n')
            writer.write('\t\t\t}\n')
            writer.write(f'\t\t\tauthProfile.GetAuthSequence().insert({"{"} "{profile.Name}", '
                         f'authSeq{profile.Name.replace(" ", "").replace(".", "")} {"}"});\n')
            writer.write(f'\t\t\tauthProfile.GetTypes().push_back("{profile.Name}");\n')
            writer.write('\t\t}\n\n')

        authProfiles = inMDEF.AuthProfiles
        if authProfiles.TokenType is not None:
            writer.write(f'\t\tauthProfile.SetTokenType("{authProfiles.TokenType}");\n')
        if authProfiles.IsExpirationDataAvailable is not None:
            writer.write(f'\t\tauthProfile.SetIsExpirationDataAvailable('
                         f'"{str(authProfiles.IsExpirationDataAvailable).lower()}");\n')
        if authProfiles.IsAutoRefreshSupported is not None:
            writer.write(
                f'\t\tauthProfile.setIsAutoRefreshSupported("{str(authProfiles.IsAutoRefreshSupported).lower()}");\n')
        if authProfiles.RefreshTokenWithinRange is not None:
            writer.write(
                f'\t\tauthProfile.SetRefreshTokenWithinRange("{str(authProfiles.RefreshTokenWithinRange).lower()}");\n')
        if authProfiles.VerifyHost is not None:
            writer.write(f'\t\tauthProfile.SetVerifyHost("{str(authProfiles.VerifyHost).lower()}");\n')
        if authProfiles.VerifyPeer is not None:
            writer.write(f'\t\tauthProfile.SetVerifyPeer("{str(authProfiles.VerifyPeer).lower()}");\n')
        if authProfiles.AuthWindowHeight is not None:
            writer.write(f'\t\tauthProfile.SetAuthWindowHeight({authProfiles.AuthWindowHeight});\n')
        if authProfiles.AuthWindowWidth is not None:
            writer.write(f'\t\tauthProfile.SetAuthWindowWidth({authProfiles.AuthWindowWidth});\n')
        writer.write('\t\tout_configs.SetAuthProfiles(authProfile);\n\n')

        authHandlerMap = {
            'SAAS_AUTH_VALUE_OAUTH_2': ['OAuth_2.0', 'OAuth 2.0'],
            'SAAS_AUTH_VALUE_ACCESS_TOKEN': ['Access_Token', 'Access Token'],
            'SAAS_AUTH_VALUE_BASIC': ['Basic', 'Basic Authentication'],
            'SAAS_AUTH_VALUE_MWS': ['MWS']
        }
        # Create Auth handlers
        for authProfile in authProfiles.AllProfiles:
            authHandler = ''
            for key, val in authHandlerMap.items():
                if authProfile.Name in val:
                    authHandler = key
                    break
            writer.write(f'\t\t// {authProfile.Name}\n')
            writer.write('\t\t{\n')
            writer.write('\t\t\tIAuthenticationHandler* authHandler =\n')
            writer.write(f'\t\t\tSaaSAuthenticationFactory::CreateAuthenticationHandler({authHandler});\n\n')
            for authName in authHandlerMap[authHandler]:
                writer.write(f'\t\t\tout_configs.AddAuthHandler("{authName}", authHandler);\n')
            writer.write('\t\t}\n')
        writer.write('\t}\n')

        # Prepare Parsers
        # TODO: Come up with better solution rather than hard-coding
        writer.write('\t// Parser handlers\n')
        writer.write('\t{\n')
        writer.write('\t\tSaaSParser::SaaSParserFactory factory;\n')
        writer.write('\t\tSaaSParser::IParserHandler* parserHandler =\n')
        writer.write('\t\tfactory.CreateParserHandler(SaaSParser::SAAS_JSON_PARSER);\n')
        writer.write('\n')
        writer.write('\t\tout_configs.AddParserHandler("application/json", parserHandler);\n')
        writer.write('\t}\n\n')

        # Prepare Tables
        writer.write('\t// Tables\n')
        writer.write('\t{\n')
        for table in inMDEF.Tables:
            writer.write(f'\t\t{table.FullName}(out_configs);\n')
        writer.write('\t}\n\n')

        # Prepare Skeleton Tables
        writer.write('\t// Skeleton Tables\n')
        writer.write('\t{\n')
        for table in inMDEF.SkeletonTables:
            writer.write(f'\t\t{table.FullName}(out_configs);\n')
        writer.write('\t}\n')
        writer.write('}')
        writer.save()


class ConfigurationH(Configurable):
    """Represents a class that writes Configuration.h"""

    @staticmethod
    def Configure(inMDEF: MDEF, inOutputDir: str):
        writer = File('Configuration.h', f'{inMDEF.DataSource} Driver Configuration', inOutputDir)
        writer.write('#ifndef _CONFIGURATION_H_\n')
        writer.write('#define _CONFIGURATION_H_\n\n')
        writer.write('#include "SaaSSDK.h"\n\n')
        writer.write('namespace Simba\n{\n')
        writer.write('\tnamespace SaaSSDK\n'
                     '\t{\n')
        writer.write(f'\t\tnamespace {inMDEF.DataSource}ODBC\n'
                     '\t\t{\n')
        writer.write('\t\t\t/// @brief EloquaODBCStaticConfiguration abstract class, '
                     'SaaS SDK user need to implement this class as the\n'
                     '\t\t\t///        starting point. And need to fill in the configuration details.\n')
        writer.write(f'\t\t\tclass {inMDEF.DataSource}ODBCStaticConfiguration : public ISaaSStaticConfiguration\n')
        writer.write('\t\t\t{\n')
        writer.write('\t\t\tpublic:\n')
        writer.write('\t\t\t\t/// @brief  To populate the meta data configurations for the data source.\n'
                     '\t\t\t\tvirtual void PopulateMetaDataConfiguration(SaaSConfiguration& out_configs);\n\n')

        writer.write('\t\t\t\t/// @brief To populate the driver wide settings.\n'
                     '\t\t\t\t///\n'
                     '\t\t\t\t/// @param out_driverConfigs The static driver wide configuration details.\n'
                     '\t\t\t\t///\n'
                     '\t\t\t\tvirtual void PopulateDriverWideConfiguration(SaaSDriverConfig& out_driverConfig);\n\n')

        writer.write("\t\t\t\t/// @brief The connection string key list which are marked sensistive and "
                     "it's value is not to visible in\n"
                     "\t\t\t\t///        log and should be masked in the logs.\n"
                     "\t\t\t\t///\n"
                     "\t\t\t\t/// @param out_sensitiveList The simba_wstring vector holding sensitive key's name.\n"
                     "\t\t\t\t///\n"
                     "\t\t\t\tvirtual void PopulateSensitiveList(std::vector<simba_wstring>& out_sensitiveList);\n\n")

        writer.write('\t\t\t\t/// @brief To populate the connection configuration to be set.\n'
                     '\t\t\t\t///\n'
                     '\t\t\t\t/// @param in_connIdent     The connection identifier value passed in connection string\n'
                     '\t\t\t\t/// @param out_connConfig   The list of connection configuration.\n'
                     '\t\t\t\t///\n'
                     '\t\t\t\tvirtual void PopulateConnectionConfiguration(\n'
                     '\t\t\t\t\tconst simba_wstring& in_connIdent,\n'
                     '\t\t\t\t\tSaaSConnectionConfig& out_connConfig);\n')
        writer.write('\t\t\t}\n')
        writer.write('\t\t}\n')
        writer.write('\t}\n')
        writer.write('}\n')
        writer.write('#endif _CONFIGURATION_H_\n')
        writer.save()


class ConfigurationHelpersH(Configurable):
    """Represents a class that writes ConfigurationHelpers.h"""
    @staticmethod
    def Configure(inMDEF: MDEF, inOutputDir: str):
        writer = File('ConfigurationHelpers.h', f'{inMDEF.DataSource} Driver ConfigurationHelpers', inOutputDir)
        writer.write('#ifndef __CONFIGURATIONHELPERS_H__\n')
        writer.write('#define __CONFIGURATIONHELPERS_H__\n\n')
        writer.write('#include "SaaSSDK.h"\n'
                     '#include "Configuration/SaaSIndexBasedPaginationData.h"\n\n')
        writer.write('namespace Simba\n'
                     '{\n'
                     '\tnamespace SaaSSDK\n'
                     '\t{\n'
                     '\t\tclass SaaSConfiguration;\n'
                     '\t}\n'
                     '}\n\n')

        # TODO: Enhance Pagination handlers logic here
        writer.write('Simba::Support::SharedPtr<Simba::SaaSSDK::SaaSPagination::SaaSIndexBasedPaginationData> '
                     'GetPaginationDataDetails_EMPTY();\n'
                     'Simba::Support::SharedPtr<Simba::SaaSSDK::SaaSPagination::SaaSIndexBasedPaginationData> '
                     'GetPaginationDataDetails_ROWCOUNT();\n\n')

        writer.write('// Tables\n')
        for table in inMDEF.Tables:
            writer.write(f'void {table.FullName}(Simba::SaaSSDK::SaaSConfiguration& io_configs);\n')
        writer.write('\n')
        writer.write('// Skeleton Tables\n')
        for table in inMDEF.SkeletonTables:
            writer.write(f'void {table.FullName}(Simba::SaaSSDK::SaaSConfiguration& io_configs);\n')
        writer.write('\n')
        writer.write('#endif __CONFIGURATIONHELPERS_H__\n')
        writer.save()


class DriverWideConfigurationCPP(Configurable):
    """Represents a class that write DriverWideConfiguration.cpp"""

    @staticmethod
    def Configure(inMDEF: MDEF, inOutputDir: str):
        writer = File('DriverWideConfiguration.cpp', f'{inMDEF.DataSource} DriverWide Configuration', inOutputDir)
        writer.write('#include "Configuration.h"\n'
                     '#include <vector>\n\n')
        writer.write('using namespace Simba::SaaSSDK;\n'
                     f'using namespace Simba::SaaSSDK::{inMDEF.DataSource}ODBC;\n\n')
        writer.write(f'void {inMDEF.DataSource}ODBCStaticConfiguration::PopulateDriverWideConfiguration('
                     f'SaaSDriverConfig& out_driverConfig)\n')
        writer.write('{\n')
        writer.write(f'\tout_driverConfig.SetDriverName("{inMDEF.DataSource}ODBC");\n'
                     '\tout_driverConfig.SetVendorName("Simba");\n'
                     f'\tout_driverConfig.SetDataSourceName("{inMDEF.DataSource}");\n\n'
                     f'\tProductVersion prodVer(2, 10, 0, 1000);\n'
                     f'\tout_driverConfig.SetVersion(prodVer);\n\n'
                     f'\tout_driverConfig.SetDidFileName("{inMDEF.DataSource}ODBC.did");\n'
                     f'\tout_driverConfig.SetErrorMsgFile("{inMDEF.DataSource}Error.xml");\n'
                     f'\tout_driverConfig.SetComponentIdentifier(401);\n'
                     f'\tout_driverConfig.SetComponentName("{inMDEF.DataSource}");\n')
        writer.write('}\n\n')
        writer.write(f'void {inMDEF.DataSource}ODBCStaticConfiguration::PopulateSensitiveList('
                     f'std::vector<simba_wstring>& out_sensitiveList)\n')
        writer.write('{\n')
        for authMap in inMDEF.AuthBrowseConnectMap:
            if authMap.IsSensitive:
                writer.write(f'\tout_sensitiveList.push_back("{authMap.Key}");\n')
        writer.write('}\n\n')
        writer.write(f'void {inMDEF.DataSource}ODBCStaticConfiguration::PopulateConnectionConfiguration(\n'
                     f'\tconst simba_wstring& in_connIdent,\n'
                     f'\tSaaSConnectionConfig& out_connConfig)\n')
        writer.write('{\n')
        writer.write('\tAutoPtr<SaaSConnectionConfigValue> connConfig;\n')
        writer.write('\n')
        writer.write(f'\tconnConfig = new SaaSConnectionConfigValue(SAAS_CONN_CURRENT_CATALOG, DT_WSTRING, '
                     f'new simba_wstring(L"{inMDEF.DataSource}"));\n'
                     f'\tout_connConfig.AddToConnConfigMap(connConfig.Detach());\n')
        writer.write('\n')
        writer.write(f'\tconnConfig = new SaaSConnectionConfigValue(SAAS_CONN_DBMS_NAME, DT_WSTRING, '
                     f'new simba_wstring(L"{inMDEF.DataSource}"));\n'
                     f'\tout_connConfig.AddToConnConfigMap(connConfig.Detach());\n')
        writer.write('}\n')
        writer.save()


class AbstractTableConfig:
    """Represents a class that writes Common Tables' configurations"""

    @staticmethod
    def writePrimaryKeys(inWriter: File, inPrimaryKeys: list[PrimaryKey], inTableName: str, indent: int = 1):
        tab = '\t'
        inWriter.write(f'{tab * indent}// Primary Key\n')
        inWriter.write(f'{tab * indent}{"{"}\n')
        inWriter.write(f'{tab * (indent + 1)}SaaSTablePKeyColumn tablePKey;\n')
        inWriter.write(f'{tab * (indent + 1)}tablePKey.SetPKeyName("pk_{inTableName}");\n')
        for pKey in inPrimaryKeys:
            inWriter.write(f'{tab * (indent + 1)}{"{"}\n')
            inWriter.write(f'{tab * (indent + 2)}SaaSPK pKey{inTableName};\n')
            inWriter.write(f'{tab * (indent + 2)}pKey{inTableName}.SetPkColumn({pKey.Index});\n')
            inWriter.write(f'{tab * (indent + 2)}tablePKey.AddPK(pKey{inTableName});\n')
            inWriter.write(f'{tab * (indent + 1)}{"}"}\n')
        inWriter.write(f'{tab * (indent + 1)}table.SetPkeyColumns(tablePKey);\n')
        inWriter.write(f'{tab * indent}{"}"}\n')

    @staticmethod
    def writeForeignKeys(inWriter: File, inForeignKeys: list[ForeignKey], indent: int = 1):
        tab = '\t'
        inWriter.write(f'{tab * indent}// Foreign Keys\n')
        for fKey in inForeignKeys:
            for fKeyCol in fKey.ForeignKeyColumns:
                inWriter.write(f'{tab * indent}{"{"}\n')
                inWriter.write(f'{tab * (indent + 1)}SaaSFKeyColumn tableFKey;\n')
                inWriter.write(f'{tab * (indent + 1)}SaaSForeignKeyColumns tableFKeyCol;\n')
                inWriter.write(f'{tab * (indent + 1)}tableFKeyCol.SetFKeyColumnName("{fKeyCol.ForeignKey}");\n')
                inWriter.write(f'{tab * (indent + 1)}tableFKeyCol.SetPrimaryKeyColumnName("{fKeyCol.PrimaryKey}");\n')
                inWriter.write(f'{tab * (indent + 1)}tableFKey.SetReferenceTable("{fKey.ReferenceTable}");\n')
                if fKey.ReferenceTableSchema is not None and len(fKey.ReferenceTableSchema) > 0:
                    inWriter.write(
                        f'{tab * (indent + 1)}tableFKey.SetReferenceTableSchema("{fKey.ReferenceTableSchema}");\n'
                    )
                inWriter.write(f'{tab * (indent + 1)}table.AddForeignKeyColumn(tableFKey);\n')
                inWriter.write(f'{tab * indent}{"}"}\n')

    @staticmethod
    def writeColumnPushdown(inWriter: File, inColPushdown: ColumnPushdown, indent: int = 1):
        tab = '\t'
        inWriter.write(f'{tab * indent}SaaSColumnPushdown columnPushdown;\n')
        inWriter.write(f'{tab * indent}columnPushdown.SetSupport(true);\n')
        inWriter.write(f'{tab * indent}columnPushdown.SetSvcReqParamKey("'
                   f'{f"{inColPushdown.ParamDelimiter}".join(inColPushdown.ParamKey)}'
                   f'";\n')
        inWriter.write(f'{tab * indent}columnPushdown.SetSvcReqParamDelimiter("{inColPushdown.ParamDelimiter}");\n')

    @staticmethod
    def writePreReqCalls(inWriter: File, inPreReqCall: PreReqCall, indentLevel: int):
        """Generates Pre-req calls contents"""
        tab = '\t'
        inWriter.write(f'{tab * indentLevel}{"{"}\n')
        inWriter.write(f'{tab * (indentLevel + 1)}// ReadAPI Prereqcall\n')
        inWriter.write(f'{tab * (indentLevel + 1)}SaaSPreReqCall table_preReqCall1;\n')
        inWriter.write(f'{tab * (indentLevel + 1)}table_preReqCall1.SetEndPoint("{inPreReqCall.Endpoint}");\n')
        inWriter.write(f'{tab * (indentLevel + 1)}// ServiceReq param key read details\n')
        for item in inPreReqCall.ReqParamKeys:
            inWriter.write(f'{tab * (indentLevel + 1)}{"{"}\n')
            inWriter.write(f'{tab * (indentLevel + 2)}SaaSSvcReqParamKey table_svcReqParamKey;\n')
            inWriter.write(f'{tab * (indentLevel + 2)}table_svcReqParamKey.SetKeyName("{item.KeyName}");\n')
            if item.RespAttrField is not None and len(item.RespAttrField) > 0:
                inWriter.write(
                    f'{tab * (indentLevel + 2)}table_svcReqParamKey.SetSvcRespAttrField("{item.RespAttrField}");\n'
                )
            if item.IsParameter:
                inWriter.write(f'{tab * (indentLevel + 2)}table_preReqCall1.SetParameterType();\n')
            if item.IsReferenced:
                inWriter.write(f'{tab * (indentLevel + 2)}table_preReqCall1.SetReferencedType();\n')
            if item.MaxValuesPerCall > 0:
                inWriter.write(
                    f'{tab * (indentLevel + 2)}table_preReqCall1.SetMaxValuesPerCall({item.MaxValuesPerCall});\n'
                )
            inWriter.write(f'{tab * (indentLevel + 2)}table_preReqCall1.AddSvcReqParamKey(table_svcReqParamKey);\n')
            inWriter.write(f'{tab * (indentLevel + 1)}{"}"}\n')
        if inPreReqCall.ListRoot is not None and len(inPreReqCall.ListRoot) > 0:
            inWriter.write(f'{tab * (indentLevel + 1)}table_preReqCall1.SetListRoot("{inPreReqCall.ListRoot}");\n')
        if inPreReqCall.Pageable and inPreReqCall.Pagination is not None:
            # TODO: Prepare Pagination data
            inWriter.write(f'{tab * (indentLevel + 1)}table_preReqCall1.IsPageable();\n')
            inWriter.write(f'{tab * (indentLevel + 1)}table_preReqCall.SetPaginationHandler(paginationHandler);\n')
            inWriter.write(
                f'{tab * (indentLevel + 1)}table_preReqCall1.SetPaginationData(GetPaginationDataDetails_ROWCOUNT());\n'
            )
        if inPreReqCall.ChildPreReqCall is not None:
            AbstractTableConfig.writeChildPreReqCalls(inWriter, inPreReqCall.ChildPreReqCall, indentLevel + 1, 2)
        inWriter.write(f'{tab * (indentLevel + 1)}table_readApiEndpoint.SetPreReqCall(table_preReqCall1);\n')
        inWriter.write(f'{tab * indentLevel}{"}"}\n')

    @staticmethod
    def writeChildPreReqCalls(inWriter: File, inPreReqCall: PreReqCall, indentLevel: int, inIdent: int = 1):
        """Generates Nested Pre-req calls contents"""
        tab = '\t'
        inWriter.write(f'{tab * indentLevel}{"{"}\n')
        inWriter.write(f'{tab * (indentLevel + 1)}// ReadAPI Nested Prereqcall\n')
        inWriter.write(f'{tab * (indentLevel + 1)}SaaSPreReqCall table_preReqCall{inIdent};\n')
        inWriter.write(f'{tab * (indentLevel + 1)}table_preReqCall{inIdent}.SetEndPoint("{inPreReqCall.Endpoint}");\n')
        if inPreReqCall.Pageable:
            # TODO: Implement PreReqCall specific pagination config
            inWriter.write(
                f'{tab * (indentLevel + 1)}table_preReqCall{inIdent}.SetPaginationHandler(paginationHandler);\n'
            )
        inWriter.write(f'{tab * (indentLevel + 1)}// ServiceReq param key read details\n')
        for item in inPreReqCall.ReqParamKeys:
            inWriter.write(f'{tab * (indentLevel + 1)}{"{"}\n')
            inWriter.write(f'{tab * (indentLevel + 2)}SaaSSvcReqParamKey table_svcReqParamKey;\n')
            inWriter.write(f'{tab * (indentLevel + 2)}table_svcReqParamKey.SetKeyName("{item.KeyName}");\n')
            if item.RespAttrField is not None and len(item.RespAttrField) > 0:
                inWriter.write(
                    f'{tab * (indentLevel + 2)}table_svcReqParamKey.SetSvcRespAttrField("{item.RespAttrField}");\n'
                )
            if item.IsParameter:
                inWriter.write(f'{tab * (indentLevel + 2)}table_preReqCall{inIdent}.SetParameterType();\n')
            if item.IsReferenced:
                inWriter.write(f'{tab * (indentLevel + 2)}table_preReqCall{inIdent}.SetReferencedType();\n')
            if item.MaxValuesPerCall > 0:
                inWriter.write(
                    f'{tab * (indentLevel + 2)}table_preReqCall{inIdent}.SetMaxValuesPerCall({item.MaxValuesPerCall});\n'
                )
            inWriter.write(
                f'{tab * (indentLevel + 2)}table_preReqCall{inIdent}.AddSvcReqParamKey(table_svcReqParamKey);\n'
            )
            inWriter.write(f'{tab * (indentLevel + 1)}{"}"}\n')
        if inPreReqCall.ListRoot is not None and len(inPreReqCall.ListRoot) > 0:
            inWriter.write(
                f'{tab * (indentLevel + 1)}table_preReqCall{inIdent}.SetListRoot("{inPreReqCall.ListRoot}");\n'
            )
        if inPreReqCall.Pageable and inPreReqCall.Pagination is not None:
            # TODO: Prepare Pagination data
            inWriter.write(f'{tab * (indentLevel + 1)}table_preReqCall1.IsPageable();\n')
            inWriter.write(f'{tab * (indentLevel + 1)}table_preReqCall.SetPaginationHandler(paginationHandler);\n')
            inWriter.write(
                f'{tab * (indentLevel + 1)}table_preReqCall{inIdent}.SetPaginationData('
                f'GetPaginationDataDetails_ROWCOUNT());\n'
            )
        if inPreReqCall.ChildPreReqCall is not None:
            AbstractTableConfig.writeChildPreReqCalls(inWriter, inPreReqCall.ChildPreReqCall, indentLevel + 1, inIdent + 1)
        inWriter.write(
            f'{tab * (indentLevel + 1)}table_preReqCall{inIdent - 1}.SetPreReqCall(table_preReqCall{inIdent});\n'
        )
        inWriter.write(f'{tab * indentLevel}{"}"}\n')

    @staticmethod
    def writeColumns(inWriter: File, inColumns: list[Column], indent: int = 1, isSkeletonColumn: bool = False):
        tab = '\t'
        if isSkeletonColumn:
            inWriter.write(f'{tab * indent}// Skeleton Column Definition\n')
        else:
            inWriter.write(f'{tab * indent}// Static Columns\n')
        inWriter.write(f'{tab * indent}{"{"}\n')
        for column in inColumns:
            inWriter.write(f'{tab * (indent + 1)}{"{"}\n')
            inWriter.write(f'{tab * (indent + 2)}SaaSTableColumn column_table;\n')
            inWriter.write(f'{tab * (indent + 2)}column_table.SetName("{column.Name}");\n')

            inWriter.write(f'{tab * (indent + 2)}SaaSMetadata metadata_column_table;\n')
            colMetadata = column.Metadata
            inWriter.write(f'{tab * (indent + 2)}metadata_column_table.SetSqlType({colMetadata.SQLType});\n')
            if colMetadata.SourceType is not None and len(colMetadata.SourceType) > 0:
                inWriter.write(
                    f'{tab * (indent + 2)}metadata_column_table.SetSourceType({colMetadata.SourceType.upper()});\n'
                )
            if colMetadata.IsUnsigned:
                inWriter.write(
                    f'{tab * (indent + 2)}metadata_column_table.SetIsUnsigned({str(colMetadata.IsUnsigned).lower()});\n'
                )
            if colMetadata.Length > 0:
                inWriter.write(f'{tab * (indent + 2)}metadata_column_table.SetLength({colMetadata.Length});\n')
            if colMetadata.Scale > 0:
                inWriter.write(f'{tab * (indent + 2)}metadata_column_table.SetScale({colMetadata.Scale});\n')
            if colMetadata.Precision > 0:
                inWriter.write(f'{tab * (indent + 2)}metadata_column_table.SetPrecision({colMetadata.Precision});\n')
            inWriter.write(f'{tab * (indent + 2)}column_table.SetMetadata(metadata_column_table);\n')

            inWriter.write(f'{tab * (indent + 2)}column_table.SetNullable({str(column.Nullable).lower()});\n')
            inWriter.write(f'{tab * (indent + 2)}column_table.SetUpdatable({str(column.Updatable).lower()});\n')
            inWriter.write(f'{tab * (indent + 2)}column_table.SetPassdownable({str(column.Passdownable).lower()});\n')
            if column.ListResult is not None and len(column.ListResult) > 0:
                inWriter.write(f'{tab * (indent + 2)}column_table.SetSvcRespAttrListResult("{column.ListResult}");\n')
            if column.ItemResult is not None and len(column.ItemResult) > 0:
                inWriter.write(f'{tab * (indent + 2)}column_table.SetSvcRespAttrItemResult("{column.ItemResult}");\n')
            if column.QueryMapping is not None and len(column.QueryMapping) > 0:
                inWriter.write(f'{tab * (indent + 2)}column_table.SetSvcReqParamQueryMapping("{column.QueryMapping}");\n')
            if column.ReturnIdPath is not None and len(column.ReturnIdPath) > 0:
                inWriter.write(f'{tab * (indent + 2)}column_table.SetSvcRespAttrReturnIdPath("{column.ReturnIdPath}");\n')
            if column.PushdownMapping is not None and len(column.PushdownMapping) > 0:
                inWriter.write(f'{tab * (indent + 2)}column_table.SetColumnPushDownMapping("{column.PushdownMapping}");\n')
            if column.SyntheticIndexColumn:
                # Do nothing. Virtual tables not implemented
                pass
            if isSkeletonColumn:
                inWriter.write(f'{tab * (indent + 2)}skeleton_columns.SetSkeletonColumnDefinition(column_table);\n')
            else:
                inWriter.write(f'{tab * (indent + 2)}table.AddColumn(column_table);\n')
            inWriter.write(f'{tab * (indent + 1)}{"}"}\n')
        inWriter.write(f'{tab * indent}{"}"}\n')

    @staticmethod
    def writeSkeletonColumns(inWriter: File, inColumns: list[SkeletonColumn], indent: int = 1):
        tab = '\t'
        inWriter.write(f'{tab * indent}// Skeleton Columns\n')
        inWriter.write(f'{tab * indent}{"{"}\n')
        for skeletonCol in inColumns:
            inWriter.write(f'{tab * (indent + 1)}SaaSSkeletonColumn skeleton_columns;\n')
            AbstractTableConfig.writeColumns(inWriter, [skeletonCol.ColumnDefinition], indent + 1, True)
            AbstractTableConfig.writeListVariables(inWriter, [skeletonCol.ListVariableAccess], indent + 1, True)
            inWriter.write(f'{tab * (indent + 1)}table.AddSkeletonColumn(skeleton_columns);\n')
        inWriter.write(f'{tab * indent}{"}"}\n')

    @staticmethod
    def writeReadAPI(inWriter: File, inReadAPI: ReadAPI, inPagination: Pagination, indent: int = 1):
        tab = '\t'
        inWriter.write(f'{tab * indent}// ReadAPI\n')
        inWriter.write(f'{tab * indent}{"{"}\n')
        inWriter.write(f'{tab * (indent + 1)}SaaSReadApi table_readApi;\n')
        if inPagination is not None:
            inWriter.write(f'{tab * (indent + 1)}table_readApi.SetPaginationHandler(paginationHandler);\n')
        inWriter.write(f'{tab * (indent + 1)}// ReadAPI Endpoints\n')

        inWriter.write(f'{tab * (indent + 1)}{"{"}\n')
        endpoint = inReadAPI.Endpoint
        inWriter.write(f'{tab * (indent + 2)}SaaSReadApiEndpoint table_readApiEndpoint;\n')
        inWriter.write(f'{tab * (indent + 2)}table_readApiEndpoint.SetListEndPoint("{endpoint.ListEndpoint}");\n')
        inWriter.write(f'{tab * (indent + 2)}table_readApiEndpoint.SetItemEndPoint("{endpoint.ItemEndpoint}");\n')
        inWriter.write(f'{tab * (indent + 2)}table_readApiEndpoint.SetType("{endpoint.Type}");\n')
        if inPagination is not None:
            # TODO: Fix me
            inWriter.write(f'{tab * (indent + 2)}table_readApiEndpoint.SetPaginationData(GetPaginationDataDetails());\n')
        if endpoint.PreReqCall is not None:
            AbstractTableConfig.writePreReqCalls(inWriter, endpoint.PreReqCall, indent + 2)
        inWriter.write(f'{tab * (indent + 2)}table_readApi.SetEndPoint(table_readApiEndpoint);\n')
        inWriter.write(f'{tab * (indent + 1)}{"}"}\n')

        inWriter.write(f'{tab * (indent + 1)}table_readApi.SetMethod("{inReadAPI.Method}");\n')
        if inReadAPI.Accept is not None and len(inReadAPI.Accept) > 0:
            inWriter.write(f'{tab * (indent + 1)}table_readApi.SetAccept("{inReadAPI.Accept}");\n')
        if inReadAPI.ContentType is not None and len(inReadAPI.ContentType) > 0:
            inWriter.write(f'{tab * (indent + 1)}table_readApi.SetContentType("{inReadAPI.ContentType}");\n')
        if inReadAPI.ParameterFormat is not None and len(inReadAPI.ParameterFormat) > 0:
            inWriter.write(f'{tab * (indent + 1)}table_readApi.SetParameterFormat({inReadAPI.ParameterFormat});\n')
        if inReadAPI.ListRoot is not None and len(inReadAPI.ListRoot) > 0:
            inWriter.write(f'{tab * (indent + 1)}table_readApi.SetListRoot("{inReadAPI.ListRoot}");\n')
        if inReadAPI.ItemRoot is not None and len(inReadAPI.ItemRoot) > 0:
            inWriter.write(f'{tab * (indent + 1)}table_readApi.SetItemRoot("{inReadAPI.ItemRoot}");\n')
        inWriter.write(f'{tab * (indent + 1)}table_apiAccess.SetReadApi(table_readApi);\n')
        inWriter.write(f'{tab * indent}{"}"}\n')

    @staticmethod
    def writeListVariables(inWriter: File, inListVariables: list[ListVariable], indent: int = 1,
                           isListVariableAccess: bool = False):
        tab = '\t'
        if isListVariableAccess:
            inWriter.write(f'{tab * indent}// List Variable Access\n')
        else:
            inWriter.write(f'{tab * indent}// List Variable PreCalls\n')
        for listVar in inListVariables:
            inWriter.write(f'{tab * indent}{"{"}\n')
            inWriter.write(f'{tab * (indent + 1)}SaaSListVariable table_listvariable;\n')
            inWriter.write(f'{tab * (indent + 1)}table_listvariable.SetEndpoint("{listVar.Endpoint}");\n')
            for variable in listVar.Variables:
                inWriter.write(f'{tab * (indent + 1)}{"{"}\n')
                inWriter.write(f'{tab * (indent + 2)}SaaSVariable table_variable;\n')
                inWriter.write(f'{tab * (indent + 2)}table_variable.SetVariableName("{variable.Name}");\n')
                inWriter.write(f'{tab * (indent + 2)}table_variable.SetSvcRespAttrMapping("{variable.MappedName}");\n')
                inWriter.write(f'{tab * (indent + 2)}table_listvariable.AddVariables(table_variable);\n')
                inWriter.write(f'{tab * (indent + 1)}{"}"}\n')
            if listVar.AcceptType is not None and len(listVar.AcceptType) > 0:
                inWriter.write(f'{tab * (indent + 1)}table_listvariable.SetAcceptType("{listVar.AcceptType}");\n')
            if listVar.Root is not None and len(listVar.Root) > 0:
                inWriter.write(f'{tab * (indent + 1)}table_listvariable.SetVariableRoot("{listVar.Root}");\n')
            if listVar.DefaultValue is not None and len(listVar.DefaultValue) > 0:
                inWriter.write(
                    f'{tab * (indent + 1)}table_listvariable.SetSvcRespAttrDefaultValue("{listVar.DefaultValue}");\n'
                )
            if isListVariableAccess:
                inWriter.write(f'{tab * (indent + 1)}skeleton_columns.SetListVariableAccess(table_listvariable);\n')
            else:
                inWriter.write(f'{tab * (indent + 1)}skeleton_table.AddListVariablesPrecalls(table_listvariable);\n')
            inWriter.write(f'{tab * indent}{"}"}\n')
        inWriter.write('\n')

    @staticmethod
    def Configure(inTable, inDataSource: str, inWriter: File):
        inWriter.write('#include "Authentication/SaaSAuthenticationFactory.h"\n')
        inWriter.write('#include "ConfigurationHelpers.h"\n')
        inWriter.write('#include "Configuration/SaaSConfiguration.h"\n')
        inWriter.write('#include "Pagination/SaaSPaginationFactory.h"\n\n')
        inWriter.write('using namespace Simba::SaaSSDK;\n\n')
        inWriter.write(f'void {inTable.FullName}(SaaSConfiguration& io_configs)\n')
        inWriter.write('{\n')
        inWriter.write('\tSaaSTable table;\n')
        inWriter.write(f'\ttable.SetTableCatalogName(L"{inDataSource}");\n')
        inWriter.write(f'\ttable.SetTableName(L"{inTable.Name}");\n')
        if inTable.TableSchemaName is not None and len(inTable.TableSchemaName) > 0:
            inWriter.write(f'\ttable.SetTableSchemaName(L"{inTable.TableSchemaName}");\n')
        if inTable.Sortable:
            inWriter.write('\ttable.SetSortable();\n')
        if inTable.Pageable:
            inWriter.write('\ttable.SetPageable();\n')
        if inTable.ColumnPushdown is not None and inTable.ColumnPushdown.Supported:
            AbstractTableConfig.writeColumnPushdown(inWriter, inTable.ColumnPushdown, 1)
        if inTable.ItemEndpointColumnNames is not None and len(inTable.ItemEndpointColumnNames) > 0:
            for item in inTable.ItemEndpointColumnNames:
                inWriter.write(f'\ttable.AddItemEndpointColumnNames("{item}");\n')

        # Primary Key
        AbstractTableConfig.writePrimaryKeys(inWriter, inTable.PrimaryKeys, inTable.Name, 1)

        # Foreign Key
        AbstractTableConfig.writeForeignKeys(inWriter, inTable.ForeignKeys, 1)

        # Prepare Columns
        AbstractTableConfig.writeColumns(inWriter, inTable.Columns, 1)

        # Prepare SkeletonTables
        AbstractTableConfig.writeSkeletonColumns(inWriter, inTable.SkeletonColumns, 1)

        # Prepares Pagination
        if inTable.Pageable:
            if inTable.PaginationType.Type is not None:
                inWriter.write('\t// Pagination\n')
                inWriter.write('\tSaaSPagination::IPaginationHandler* paginationHandler =\n')
                inWriter.write('\tSaaSPagination::SaaSPaginationFactory::CreatePaginationHandler('
                               f'SaaSPagination::{inTable.PaginationType.Type});\n\n')

        # Prepares APIAccess
        inWriter.write('\t// APIAccess\n')
        inWriter.write('\t{\n')
        inWriter.write('\t\tSaaSTableApiAccess table_apiAccess;\n')
        # Prepares Read API
        AbstractTableConfig.writeReadAPI(inWriter, inTable.ReadAPI, inTable.PaginationType, 2)
        inWriter.write('\t\ttable.SetAPIAccess(table_apiAccess);\n')
        inWriter.write('\t}\n\n')


class TableConfig(Configurable):
    """Represents a class that writes Tables' configurations"""

    @staticmethod
    def Configure(inMDEF: MDEF, inOutputDir: str):
        for table in inMDEF.Tables:
            writer = File(f'{table.FullName}.cpp', f'{inMDEF.DataSource} {table.FullName} configurations', inOutputDir)
            AbstractTableConfig.Configure(table, inMDEF.DataSource, writer)
            writer.write('\tio_configs.AddTable(table);\n')
            writer.write('}')
            writer.save()


class SkeletonTableConfig(Configurable):
    """Represents a class that writes SkeletonTables' configurations"""

    @staticmethod
    def Configure(inMDEF: MDEF, inOutputDir: str):
        for table in inMDEF.SkeletonTables:
            writer = File(f'{table.FullName}.cpp', f'{inMDEF.DataSource} {table.FullName} configurations', inOutputDir)
            AbstractTableConfig.Configure(table, inMDEF.DataSource, writer)
            # Prepares SkeletonTables
            writer.write('\t// Skeleton Table information\n')
            writer.write('\tSaaSSkeletonTable skeleton_table;\n')
            writer.write('\tskeleton_table.SetTableDefinition(table);\n\n')

            # Prepares List Variable PreCalls
            AbstractTableConfig.writeListVariables(writer, table.ListVariables, 1)
            writer.write('\tio_configs.SetSkeletonTableInitialized(false);\n')
            writer.write('\tio_configs.AddSkeletonTable(skeleton_table);\n')
            writer.write('}')
            writer.save()

import os
import sys
import json
import shutil
from datetime import date
from MDEF import MDEF
from Util import File


def writeConfiguration(inMDEF: MDEF, inOutputDir: str):
    """Prepares Configuration.cpp"""
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
        writer.write(f'\t\t\tstd::vector<SaaSAuthSequence> authSeq{profile.Name.replace(" ", "").replace(".", "")};\n')
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
                    writer.write(f'\t\t\t\t\tbrowseSeq{authFlow.Name}{flowIdx + 1}.GetHeaders().push_back(header{headerIdx + 1});\n\n')

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
            writer.write(f'\t\t\t\tauthSeq{profile.Name.replace(" ", "").replace(".", "")}.push_back(authSeq{authFlow.Name});\n')
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
        writer.write(f'\t\tauthProfile.setIsAutoRefreshSupported("{str(authProfiles.IsAutoRefreshSupported).lower()}");\n')
    if authProfiles.RefreshTokenWithinRange is not None:
        writer.write(f'\t\tauthProfile.SetRefreshTokenWithinRange("{str(authProfiles.RefreshTokenWithinRange).lower()}");\n')
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


def writeConfigurationH(inMDEF: MDEF, inOutputDir: str):
    """Prepares Configuration.h"""
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


def writeConfigurationHelpersH(inMDEF: MDEF, inOutputDir: str):
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


def writeDriverWideConfiguration(inMDEF: MDEF, inOutputDir: str):
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


def main(inMDEFPath: str, inOutputDir: str):
    if os.path.exists(inMDEFPath):
        inMDEFPath = os.path.abspath(inMDEFPath)
    else:
        print(f'Invalid MDEF path: {inMDEFPath}')
    configDir = os.path.join(inOutputDir, 'Configs')
    if os.path.exists(configDir):
        shutil.rmtree(configDir)
    File.createDir(configDir)

    with open(inMDEFPath, 'r') as file:
        mdefContent = json.load(file)
    mdef = MDEF(mdefContent)

    writeConfiguration(mdef, configDir)
    writeConfigurationH(mdef, configDir)
    writeConfigurationHelpersH(mdef, configDir)
    writeDriverWideConfiguration(mdef, configDir)


if __name__ == '__main__':
    # if len(sys.argv) < 3:
    #     print(f'Too few inputs\nRun python {os.path.basename(__file__)} <MDEFPath> <OutputDir>')
    #     sys.exit(1)
    # main(sys.argv[1], sys.argv[2])
    main(r'C:\Users\vrathod\Perforce\VR_WPT\Drivers\Memphis\DataSources\Eloqua\Common\Maintenance\1.6\MDEF\driver-d.mdef', '.')

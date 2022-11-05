import os
import shutil
import sys
import json
from datetime import date
from MDEF import MDEF
from Util import File


def writeTableConfigurations(inMDEF: MDEF, inOutputDir: str):
    """Prepares Table Configurations"""
    tablesDir = os.path.join(inOutputDir, 'Tables')
    shutil.rmtree(tablesDir)
    os.mkdir(tablesDir)
    for table in inMDEF.Tables:
        writer = File(f'{table.FullName}.cpp', f'{inMDEF.DataSource} {table.FullName} configurations', tablesDir)
        writer.write('#include "Authentication/SaaSAuthenticationFactory.h"\n'
                     '#include "ConfigurationHelpers.h"\n'
                     '#include "Configuration/SaaSConfiguration.h"\n'
                     '#include "Pagination/SaaSPaginationFactory.h"\n\n')
        writer.write('using namespace Simba::SaaSSDK;\n\n')
        writer.write(f'void {table.FullName}(SaaSConfiguration& io_configs)\n')
        writer.write('{\n')
        writer.write('\tSaaSTable table;\n')
        writer.write(f'\ttable.SetTableCatalogName(L"{inMDEF.DataSource}")\n')
        writer.write(f'\ttable.SetTableName(L"{table.Name}");\n')
        if table.TableSchemaName is not None and len(table.TableSchemaName) > 0:
            writer.write(f'\ttable.SetTableSchemaName(L"{table.TableSchemaName}");\n')
        if table.Sortable:
            writer.write('\ttable.SetSortable();\n')
        if table.Pageable:
            writer.write('\ttable.SetPageable();\n')
        if table.ColumnPushdown is not None and table.ColumnPushdown.Supported:
            columnPushdown = table.ColumnPushdown
            writer.write('\tSaaSColumnPushdown columnPushdown;\n')
            writer.write('\tcolumnPushdown.SetSupport(true);\n')
            writer.write(f'\tcolumnPushdown.SetSvcReqParamKey("'
                         f'{f"{columnPushdown.ParamDelimiter}".join(columnPushdown.ParamKey)})'
                         f'";\n')
            writer.write(f'\tcolumnPushdown.SetSvcReqParamDelimiter("{columnPushdown.ParamDelimiter}");\n')

        # Primary Key
        writer.write('\t// Primary Key\n')
        writer.write('\t{\n')
        writer.write('\t\tSaaSTablePKeyColumn tablePKey;\n')
        writer.write(f'\t\ttablePKey.SetPKeyName("pk_{table.Name}");\n')
        for pKey in table.PrimaryKeys:
            # Finds Primary Key Column Index
            for idx, col in enumerate(table.Columns):
                if pKey.Name == col.Name:
                    pKey.Index = idx
                    break
            if pKey.Index == -1:
                raise Exception(f'Error: {pKey.Name} not found in columns of {table.FullName}')
            writer.write('\t\t{\n')
            writer.write(f'\t\t\tSaaSPK pKey{table.Name};\n'
                         f'\t\t\tpKey{table.Name}.SetPkColumn({pKey.Index});\n')
            writer.write(f'\t\t\ttablePKey.AddPK(pKey{table.Name});\n')
            writer.write('\t\t}\n')
        writer.write(f'\t\ttable.SetPkeyColumns(tablePKey);\n')
        writer.write('\t}\n')

        # Prepare Columns
        writer.write('\t// Static Columns\n')
        writer.write('\t{\n')
        for column in table.Columns:
            writer.write('\t\t{\n')
            writer.write('\t\t\tSaaSTableColumn column_table;\n')
            writer.write(f'\t\t\tcolumn_table.SetName("{column.Name}");\n')
            writer.write('\t\t\tSaaSMetadata metadata_column_table;\n')
            colMetadata = column.Metadata
            writer.write(f'\t\t\tmetadata_column_table.SetSqlType({colMetadata.SQLType});\n')
            if colMetadata.SourceType is not None and len(colMetadata.SourceType) > 0:
                writer.write(f'\t\t\tmetadata_column_table.SetSourceType({colMetadata.SourceType.upper()});\n')
            if colMetadata.IsUnsigned:
                writer.write(f'\t\t\tmetadata_column_table.SetIsUnsigned({str(colMetadata.IsUnsigned).lower()});\n')
            if colMetadata.Length > 0:
                writer.write(f'\t\t\tmetadata_column_table.SetLength({colMetadata.Length});\n')
            if colMetadata.Scale > 0:
                writer.write(f'\t\t\tmetadata_column_table.SetScale({colMetadata.Scale});\n')
            if colMetadata.Precision > 0:
                writer.write(f'\t\t\tmetadata_column_table.SetPrecision({colMetadata.Precision});\n')
            writer.write(f'\t\t\tcolumn_table.SetMetadata(metadata_column_table);\n')
            writer.write(f'\t\t\tcolumn_table.SetNullable({str(column.Nullable).lower()});\n')
            writer.write(f'\t\t\tcolumn_table.SetUpdatable({str(column.Updatable).lower()});\n')
            writer.write(f'\t\t\tcolumn_table.SetPassdownable({str(column.Passdownable).lower()});\n')
            if column.ListResult is not None and len(column.ListResult) > 0:
                writer.write(f'\t\t\tcolumn_table.SetSvcRespAttrListResult("{column.ListResult}");\n')
            if column.ItemResult is not None and len(column.ItemResult) > 0:
                writer.write(f'\t\t\tcolumn_table.SetSvcRespAttrItemResult("{column.ItemResult}");\n')
            if column.QueryMapping is not None and len(column.QueryMapping) > 0:
                writer.write(f'\t\t\tcolumn_table.SetSvcReqParamQueryMapping("{column.QueryMapping}");\n')
            if column.ReturnIdPath is not None and len(column.ReturnIdPath) > 0:
                writer.write(f'\t\t\tcolumn_table.SetSvcRespAttrReturnIdPath("{column.ReturnIdPath}");\n')
            if column.PushdownMapping is not None and len(column.PushdownMapping) > 0:
                writer.write(f'\t\t\tcolumn_table.SetColumnPushDownMapping("{column.PushdownMapping}");\n')
            if column.SyntheticIndexColumn:
                # Do nothing. Virtual tables not implemented
                pass
            writer.write('\t\t\ttable.AddColumn(column_table);\n')
            writer.write('\t\t}\n')
        writer.write('\t}\n')

        # Prepares Pagination
        if table.Pageable:
            currType = inMDEF.PaginationType.Type if inMDEF.PaginationType is not None else None
            currType = table.PaginationType.Type if table.PaginationType is not None else currType
            if currType is not None:
                writer.write('\t// Pagination\n')
                writer.write('\tSaaSPagination::IPaginationHandler* paginationHandler =\n')
                writer.write('\tSaaSPagination::SaaSPaginationFactory::CreatePaginationHandler('
                             f'SaaSPagination::{currType});\n\n')

        # Prepares APIAccess
        writer.write('\t// APIAccess\n')
        writer.write('\t{\n')
        writer.write('\t\tSaaSTableApiAccess table_apiAccess;\n')
        # Prepares Read API
        writer.write('\t\t// ReadAPI\n')
        writer.write('\t\t{\n')
        readAPI = table.ReadAPI
        writer.write('\t\t\tSaaSReadApi table_readApi;\n')
        if table.Pageable:
            writer.write('\t\t\ttable_readApi.SetPaginationHandler(paginationHandler);\n')
        writer.write('\t\t\t// ReadAPI Endpoints\n')
        writer.write('\t\t\t{\n')
        endpoint = readAPI.Endpoint
        writer.write('\t\t\t\tSaaSReadApiEndpoint table_readApiEndpoint;\n')
        writer.write(f'\t\t\t\ttable_readApiEndpoint.SetListEndPoint("{endpoint.ListEndpoint}");\n')
        writer.write(f'\t\t\t\ttable_readApiEndpoint.SetItemEndPoint("{endpoint.ItemEndpoint}");\n')
        writer.write(f'\t\t\t\ttable_readApiEndpoint.SetType("{endpoint.Type}");\n')
        # TODO: Fix me
        writer.write(f'\t\t\t\ttable_readApiEndpoint.SetPaginationData(GetPaginationDataDetails());\n')
        if endpoint.PreReqCall is not None:
            writer.writePreReqCalls(endpoint.PreReqCall, 4)
        writer.write('\t\t\t\ttable_readApi.SetEndPoint(table_readApiEndpoint);\n')
        writer.write('\t\t\t}\n')
        writer.write(f'\t\t\ttable_readApi.SetMethod("{readAPI.Method}");\n')
        if readAPI.Accept is not None and len(readAPI.Accept) > 0:
            writer.write(f'\t\t\ttable_readApi.SetAccept("{readAPI.Accept}");\n')
        if readAPI.ContentType is not None and len(readAPI.ContentType) > 0:
            writer.write(f'\t\t\ttable_readApi.SetContentType("{readAPI.ContentType}");\n')
        if readAPI.ParameterFormat is not None and len(readAPI.ParameterFormat) > 0:
            writer.write(f'\t\t\ttable_readApi.SetParameterFormat({readAPI.ParameterFormat});\n')
        if readAPI.ListRoot is not None and len(readAPI.ListRoot) > 0:
            writer.write(f'\t\t\ttable_readApi.SetListRoot("{readAPI.ListRoot}");\n')
        if readAPI.ItemRoot is not None and len(readAPI.ItemRoot) > 0:
            writer.write(f'\t\t\ttable_readApi.SetItemRoot("{readAPI.ItemRoot}");\n')
        writer.write(f'\t\t\ttable_apiAccess.SetReadApi(table_readApi);\n')
        writer.write('\t\t}\n')
        writer.write('\t\ttable.SetAPIAccess(table_apiAccess);\n')
        writer.write('\t}\n')
        writer.write('\tio_configs.AddTable(table);\n')
        writer.write('}')
        writer.save()


def main(inMDEFPath: str, inOutputDir: str):
    if os.path.exists(inMDEFPath):
        inMDEFPath = os.path.abspath(inMDEFPath)
    else:
        print(f'Invalid MDEF path: {inMDEFPath}')
    File.createDir(inOutputDir)

    with open(inMDEFPath, 'r') as file:
        mdefContent = json.load(file)
    mdef = MDEF(mdefContent)

    writeTableConfigurations(mdef, inOutputDir)


if __name__ == '__main__':
    # if len(sys.argv) < 3:
    #     print(f'Too few inputs\nRun python {os.path.basename(__file__)} <MDEFPath> <OutputDir>')
    #     sys.exit(1)
    # main(sys.argv[1], sys.argv[2])
    main(r'C:\Users\vrathod\Perforce\VR_WPT\Drivers\Memphis\DataSources\Eloqua\Common\Maintenance\1.6\MDEF\driver-d.mdef', '.')

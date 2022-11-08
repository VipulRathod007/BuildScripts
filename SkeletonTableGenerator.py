import os
import json
import shutil

from MDEF import MDEF
from Util import File


def writeSkeletonTableConfigurations(inMDEF: MDEF, inOutputDir: str):
    """Prepares Skeleton Table Configurations"""
    # TODO: Implement SkeletonColumns, ListVariables
    for table in inMDEF.SkeletonTables:
        writer = File(f'{table.FullName}.cpp', f'{inMDEF.DataSource} {table.FullName} configurations', inOutputDir)
        writer.write('#include "Authentication/SaaSAuthenticationFactory.h"\n')
        writer.write('#include "ConfigurationHelpers.h"\n')
        writer.write('#include "Configuration/SaaSConfiguration.h"\n')
        writer.write('#include "Pagination/SaaSPaginationFactory.h"\n\n')
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
            writer.writeColumnPushdown(table.ColumnPushdown, 1)
        if table.ItemEndpointColumnNames is not None and len(table.ItemEndpointColumnNames) > 0:
            for item in table.ItemEndpointColumnNames:
                writer.write(f'\ttable.AddItemEndpointColumnNames("{item}");\n')

        # Primary Key
        writer.writePrimaryKeys(table.PrimaryKeys, table.Name, 1)

        # Prepare Columns
        writer.writeColumns(table.Columns, 1)

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
        # Prepares Read API
        writer.writeReadAPI(table.ReadAPI, table.PaginationType, 2)
        writer.write('\t\ttable.SetAPIAccess(table_apiAccess);\n')
        writer.write('\t}\n\n')

        # Prepares SkeletonTables
        writer.write('\t// Skeleton Table information\n')
        writer.write('\tSaaSSkeletonTable skeleton_table;\n')
        writer.write('\tskeleton_table.SetTableDefinition(table);\n\n')

        # Prepares List Variable PreCalls
        writer.writeListVariables(table.ListVariables, 1)
        writer.write('\tio_configs.SetSkeletonTableInitialized(false);\n')
        writer.write('\tio_configs.AddSkeletonTable(skeleton_table);\n')
        writer.write('}')
        writer.save()


def main(inMDEFPath: str, inOutputDir: str):
    if os.path.exists(inMDEFPath):
        inMDEFPath = os.path.abspath(inMDEFPath)
    else:
        print(f'Invalid MDEF path: {inMDEFPath}')
    tablesDir = os.path.join(inOutputDir, 'SkeletonTables')
    if os.path.exists(tablesDir):
        shutil.rmtree(tablesDir)
    File.createDir(tablesDir)

    with open(inMDEFPath, 'r') as file:
        mdefContent = json.load(file)
    mdef = MDEF(mdefContent)

    writeSkeletonTableConfigurations(mdef, tablesDir)


if __name__ == '__main__':
    # if len(sys.argv) < 3:
    #     print(f'Too few inputs\nRun python {os.path.basename(__file__)} <MDEFPath> <OutputDir>')
    #     sys.exit(1)
    # main(sys.argv[1], sys.argv[2])
    main(r'C:\Users\vrathod\Perforce\VR_WPT\Drivers\Memphis\DataSources\Eloqua\Common\Maintenance\1.6\MDEF\driver-d.mdef', '.')

#         if 'FKeyColumn' in table_definition:
#             table_script+='\t\tSaaSFKeyColumn tableFKey;\n'
#             table_script+='\t\tSaaSForeignKeyColumns tableFKeyCol;\n'
#             for f_key_column in table_definition['FKeyColumn']:
#                 foreign_key_column=f_key_column['ForeignKeyColumns']
#                 for column_name in foreign_key_column:
#                     table_script+='\t\ttableFKeyCol.SetFKeyColumnName("'+column_name+'");\n'
#                 table_script+='\t\ttableFKey.SetReferenceTable("");\n'
#             if 'ReferenceTableSchema' in table_definition:
#                 table_script+='\t\ttableFKey.SetReferenceTableSchema("");\n'
#             table_script+='\t\ttableFKey.SetForeignKeyColumns(tableFKeyCol);\n'
#             table_script+='\t\ttable1.AddForeignKeyColumn(tableFKey);\n\n'
#
#         pkey_column=table_definition['PKeyColumn']
#         table_pkey_script='\t\tSaaSTablePKeyColumn tablePKey;\n'
#         pKey_name='pk_'+table_name
#         for PKColumn in pkey_column[pKey_name]:
#             pkey_column_name=PKColumn['PKColumnName']
#             table_pkey_script+='\t\ttablePKey.AddPKColumnNames("'+pkey_column_name+'");\n'
#         table_pkey_script+='\t\ttablePKey.SetPKeyName("'+pKey_name+'");\n'
#         table_pkey_script+='\t\ttable.SetPkeyColumns(tablePKey);\n'
#         final_script+=table_pkey_script+'\n'
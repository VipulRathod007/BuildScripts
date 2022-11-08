import os
import shutil
import sys
import json
from datetime import date
from MDEF import MDEF
from Util import File


def writeTableConfigurations(inMDEF: MDEF, inOutputDir: str):
    """Prepares Table Configurations"""
    for table in inMDEF.Tables:
        writer = File(f'{table.FullName}.cpp', f'{inMDEF.DataSource} {table.FullName} configurations', inOutputDir)
        writer.write('#include "Authentication/SaaSAuthenticationFactory.h"\n'
                     '#include "ConfigurationHelpers.h"\n'
                     '#include "Configuration/SaaSConfiguration.h"\n'
                     '#include "Pagination/SaaSPaginationFactory.h"\n\n')
        writer.write('using namespace Simba::SaaSSDK;\n\n')
        writer.write(f'void {table.FullName}(SaaSConfiguration& io_configs)\n')
        writer.write('{\n')
        writer.write('\tSaaSTable table;\n')
        writer.write(f'\ttable.SetTableCatalogName(L"{inMDEF.DataSource}");\n')
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

        # Prepare Skeleton Columns
        writer.writeSkeletonColumns(table.SkeletonColumns, 1)

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
        writer.writeReadAPI(table.ReadAPI, table.PaginationType, 2)
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
    tablesDir = os.path.join(inOutputDir, 'Tables')
    if os.path.exists(tablesDir):
        shutil.rmtree(tablesDir)
    File.createDir(tablesDir)

    with open(inMDEFPath, 'r') as file:
        mdefContent = json.load(file)
    mdef = MDEF(mdefContent)

    writeTableConfigurations(mdef, tablesDir)


if __name__ == '__main__':
    # if len(sys.argv) < 3:
    #     print(f'Too few inputs\nRun python {os.path.basename(__file__)} <MDEFPath> <OutputDir>')
    #     sys.exit(1)
    # main(sys.argv[1], sys.argv[2])
    main(
        r'C:\Users\vrathod\Perforce\VR_WPT\Drivers\Memphis\DataSources\Eloqua\Common\Maintenance\1.6\MDEF\driver-d.mdef',
        '.')

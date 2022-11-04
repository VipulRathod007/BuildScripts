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

        if table.Pageable:
            currType = inMDEF.PaginationType.Type if inMDEF.PaginationType is not None else None
            currType = table.PaginationType.Type if table.PaginationType is not None else currType
            if currType is not None:
                writer.write('\t// Pagination\n')
                writer.write('\tSaaSPagination::IPaginationHandler* paginationHandler =\n')
                writer.write('\tSaaSPagination::SaaSPaginationFactory::CreatePaginationHandler('
                             f'SaaSPagination::{currType});\n\n')
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


#     final_script+='\t // Access API\n'
#     final_script+='\t{\n'
#     final_script+='\t\tSaaSTableApiAccess table_apiAccess;\n'
#
#     read_api_script='\t\t// ReadAPI\n'
#     read_api_script+='\t\t{\n'
#     read_api_script+='\t\t\tSaaSReadApi table_readApi;\n'
#     read_api_script+='\t\t\t//table_readApi.SetPaginationHandler(paginationHandler);\n\n'
#     read_api_script+='\t\t\t// Read API endpoints\n'
#     read_api_script+='\t\t\t{\n'
#     read_api_script+='\t\t\t\tSaaSReadApiEndpoint table_readApiEndpoint;\n'
#
#     api_access=table_data['APIAccess']
#     read_api=api_access['ReadAPI']
#     endpoint = read_api['Endpoint']
#     if 'ItemEndpoint' in endpoint:
#         item_end_point=endpoint['ItemEndpoint']
#         read_api_script+='\t\t\t\ttable_readApiEndpoint.SetItemEndPoint(\n\t\t\t\t"'+item_end_point+'");\n'
#     list_end_point=endpoint['ListEndpoint']
#     read_api_script+='\t\t\t\ttable_readApiEndpoint.SetListEndPoint(\n\t\t\t\t"'+list_end_point+'");\n'
#     if 'Type' in endpoint:
#         end_point_type=endpoint['Type']
#         read_api_script+='\t\t\t\ttable_readApiEndpoint.SetType("'+end_point_type+'");\n'
#         if 'PREREQ_CALLS'==end_point_type:
#             pre_req_call=endpoint['PreReqCall']
#             read_api_script+='\t\t\t\t// Read API pre-reqcall\n'
#             read_api_script+='\t\t\t\t{\n'
#             read_api_script+='\t\t\t\t\tSaaSPreReqCall table_preReqCall;\n'
#             if 'Endpoint' in pre_req_call:
#                 endpoint=pre_req_call['Endpoint']
#                 read_api_script+='\t\t\t\t\ttable_preReqCall.SetEndPoint("'+endpoint+'");\n'
#             read_api_script+='\t\t\t\t\ttable_preReqCall.IsPageable();\n'
#             read_api_script+='\t\t\t\t\t// Setting pagination handler marks that pagination is supported for the pre-reqcall\n'
#             read_api_script+='\t\t\t\t\ttable_preReqCall.SetPaginationHandler(paginationHandler);\n'
#             read_api_script+='\t\t\t\t\t// ServiceReq param key read details\n'
#             for req_param in pre_req_call['SvcReqParam_Keys']:
#                 read_api_script+='\t\t\t\t\t{\n'
#                 read_api_script+='\t\t\t\t\t\tSaaSSvcReqParamKey table_svcReqParamKey;\n'
#                 key_name=req_param['keyName']
#                 read_api_script+='\t\t\t\t\t\ttable_svcReqParamKey.SetKeyName("'+key_name+'");\n'
#                 resp_attr_field=req_param['SvcRespAttr_Field']
#                 read_api_script+='\t\t\t\t\t\ttable_svcReqParamKey.SetSvcRespAttrField("'+resp_attr_field+'");\n'
#                 if 'MaxValuesPerCall' in req_param:
#                     max_val_per_call=str(req_param['MaxValuesPerCall'])
#                     read_api_script+='\t\t\t\t\t\ttable_svcReqParamKey.SetMaxValuesPerCall('+max_val_per_call+');\n'
#                 if '"IsParameter": true' in req_param:
#                     read_api_script+='\t\t\t\t\t\ttable_svcReqParamKey.SetParameterType();\n'
#                 if '"IsReferenced" : true' in req_param:
#                     read_api_script+='\t\t\t\t\t\ttable_svcReqParamKey.IsReferencedType();\n'
#                 read_api_script+='\t\t\t\t\t\ttable_preReqCall.AddSvcReqParamKey(table_svcReqParamKey);\n'
#                 read_api_script+='\t\t\t\t\t}\n'
#             if 'Root' in pre_req_call:
#                 root=pre_req_call['Root']
#                 read_api_script+='\t\t\t\t\ttable_preReqCall.SetListRoot("'+root+'");\n'
#             read_api_script+='\t\t\t\t\ttable_preReqCall.SetPaginationData(GetPaginationDataDetails_ROWCOUNT());\n'
#             read_api_script+='\t\t\t\t\ttable_readApiEndpoint.SetPreReqCall(table_preReqCall);\n'
#             read_api_script+='\t\t\t\t}\n'
#         else:
#             if 'ListRoot' in read_api:
#                 list_root=read_api['ListRoot']
#                 read_api_script+='\t\t\t\ttable_readApi.SetListRoot("'+list_root+'");\n'
#             if 'ItemRoot' in read_api:
#                 item_root=read_api['ItemRoot']
#                 read_api_script+='\t\t\t\ttable_readApi.SetItemRoot("'+item_root+'");\n'
#
#     read_api_script+='\t\t\t\ttable_readApi.SetEndPoint(table_readApiEndpoint);\n'
#     read_api_script+='\t\t\t}\n'
#     if 'Method' in read_api:
#         method=read_api['Method']
#         read_api_script+='\t\t\ttable_readApi.SetMethod("'+method+'");\n'
#     if 'Accept' in read_api:
#         accept=read_api['Accept']
#         read_api_script+='\t\t\ttable_readApi.SetAccept("'+accept+'");\n'
#     if 'ContentType' in read_api:
#         content_type=read_api['ContentType']
#         read_api_script+='\t\t\ttable_readApi.SetContentType("'+content_type+'");\n'
#     if 'ParameterFormat' in read_api:
#         param_format=read_api['ParameterFormat']
#         if param_format=='Url':
#             read_api_script+='\t\t\ttable_readApi.SetParameterFormat(PARAM_FORMAT_URL);\n'
#         if param_format=='Body':
#             read_api_script+='\t\t\ttable_readApi.SetParameterFormat(PARAM_FORMAT_BODY);\n'
#         if param_format=='Query':
#             read_api_script+='\t\t\ttable_readApi.SetParameterFormat(PARAM_FORMAT_QUERY);\n'
#
#     read_api_script+='\t\t\ttable_apiAccess.SetReadApi(table_readApi);\n'
#     read_api_script+='\t\t}\n'
#     read_api_script+='\t\ttable.SetAPIAccess(table_apiAccess);\n'
#     read_api_script+='\t}\n'
#     final_script+=read_api_script
#     final_script+='}\n'
#     file_name=table_schema_name+table_name
#     final_script=final_script.replace('True','true')
#     final_script=final_script.replace('False','false')
#
#     final_script=final_script.replace('Template',data_source_name)
#     final_script=final_script.replace('FUNCTION_NAME',file_name)
#     final_script=final_script.replace('FILENAME',file_name+'.cpp')
#
#     table_name=table_name.replace("{","")
#     table_name=table_name.replace("}","")
#     table_schema_name=table_schema_name.replace("{","")
#     table_schema_name=table_schema_name.replace("}","")
#
#     file_path=sys.argv[2]+file_name+'.cpp'
#     f_final = open(file_path,'w')
#     f_final.write(final_script)
#
#     # Closing file
#     f_final.close()
# f_input.close()
#
#
#
#
#
import json
from datetime import date
import sys
# creating the date object of today's date
todays_date = date.today()

# Opening JSON file
f_input = open(sys.argv[1]+'\driver-d.mdef','r')
data_input = json.load(f_input)
data_source_name=data_input['Datasource']

if 'SkeletonTable' in data_input:
    for skeleton_table_script in data_input['SkeletonTable']:
        final_script='// ==========================================================================================================================\n'
        final_script+='/// @file FILENAME \n'
        final_script+='///\n'
        final_script+='/// Template Driver Configuration.\n'
        final_script+='///\n'
        final_script+='/// Copyright (C) '+str(todays_date.year)+' Simba Technologies Incorporated.\n'
        final_script+='// ==========================================================================================================================\n'
        final_script+='\n'
        final_script+='#include "Authentication/SaaSAuthenticationFactory.h"\n'
        final_script+='#include "ConfigurationHelpers.h"\n'
        final_script+='#include "Configuration/SaaSConfiguration.h"'
        final_script+='\n'

        final_script+='using namespace Simba::SaaSSDK;\n'
        final_script+='\n'
        table_definition=skeleton_table_script['TableDefinition']
        table_script='\t\t// Table information\n'
        table_script='\t\tSaaSTable table;\n'
        table_name=table_definition['TableName']
        table_script+='\t\ttable.SetTableName("'+table_name+'");\n'
        if 'TableSchemaName' in table_definition:
            table_schema_name=table_definition['TableSchemaName']
            table_script+='\t\ttable.SetTableSchemaName("'+table_schema_name+'");\n'
        if 'Sortable' in table_definition:    
            table_script+='\t\ttable.SetSortable();\n'
        if 'Pageable' in table_definition:        
            table_script+='\t\ttable.SetPageable();\n'
        if 'ItemEndpointColumnNames' in table_definition:                     
            for item_endpoint_column_name in table_definition['ItemEndpointColumnNames']:  
                table_script+='\t\ttable.AddItemEndpointColumnNames("'+item_endpoint_column_name+'");\n'
                
        if 'FKeyColumn' in table_definition: 
            table_script+='\t\tSaaSFKeyColumn tableFKey;\n'
            table_script+='\t\tSaaSForeignKeyColumns tableFKeyCol;\n'
            for f_key_column in table_definition['FKeyColumn']:  
                foreign_key_column=f_key_column['ForeignKeyColumns']
                for column_name in foreign_key_column:
                    table_script+='\t\ttableFKeyCol.SetFKeyColumnName("'+column_name+'");\n'
                table_script+='\t\ttableFKey.SetReferenceTable("");\n'
            if 'ReferenceTableSchema' in table_definition: 
                table_script+='\t\ttableFKey.SetReferenceTableSchema("");\n'
            table_script+='\t\ttableFKey.SetForeignKeyColumns(tableFKeyCol);\n'
            table_script+='\t\ttable1.AddForeignKeyColumn(tableFKey);\n\n'

        
        # table_script+='\t\ttable.SetValPath("display_value");\n\n'

        function_data='void FUNCTION_NAME(SaaSConfiguration& out_configuration)\n{\n'  
        final_script+=function_data
        final_script+='\t\t// Skeleton Table information\n'
        final_script+='\t\tSaaSSkeletonTable skeleton_table;\n'
        final_script+='\t\tSaaSListVariable skeleton_column_variable_access;\n'
        
        if 'SkeletonColumn' in table_definition:
            skeleton_column_script='\t\tSaaSSkeletonColumn skeleton_columns;\n'
            for skeleton_column in table_definition['SkeletonColumn']:
                List_variable_access=skeleton_column['ListVariableAccess']
                end_point=List_variable_access['Endpoint']
                if 'AcceptType' in List_variable_access:        
                    access_type=List_variable_access['AcceptType']
                    
                for varible_data in List_variable_access['Variables']:
                    variable_name=varible_data['VariableName']
                    svc_resp_attr_mapping=varible_data['SvcRespAttr_Mapping']
                    column_varible_script='\t\t{\n'
                    column_varible_script+='\t\t\tSaaSVariable skeleton_column_access_variable;\n'
                    column_varible_script+='\t\t\tskeleton_column_access_variable.SetVariableName("'+str(variable_name)+'");\n'
                    column_varible_script+='\t\t\tskeleton_column_access_variable.SetSvcRespAttrMapping("'+svc_resp_attr_mapping+'");\n'
                    column_varible_script+='\t\t\tskeleton_column_variable_access.AddVariables(skeleton_column_access_variable);\n'
                    column_varible_script+='\t\t}\n'
                    
                    final_script+=column_varible_script
                final_script+='\t\tskeleton_column_variable_access.SetEndpoint("'+end_point+'");\n'
                final_script+='\t\tskeleton_column_variable_access.SetAcceptType("'+access_type+'");\n'           
                final_script+='\n'
                
                column_definition=skeleton_column['ColumnDefinition']
                metadata=column_definition['Metadata']
                skeleton_column_script+='\t\t{\n\t\t\tSaaSTableColumn skeleton_column;\n'
                skeleton_column_script+='\t\t\tSaaSColumnDefinition skeleton_column_columnDefinition;\n'
                
                if 'SQLType' in metadata:        
                    sql_type=metadata['SQLType']
                    skeleton_column_script+='\t\t\tskeleton_column_columnDefinition.SetSQLType("'+sql_type+'");\n'

                if 'IsUnsigned' in metadata:                
                    is_unsigned=str(metadata['IsUnsigned'])
                    skeleton_column_script+='\t\t\tskeleton_column_columnDefinition.SetIsUnsigned("'+is_unsigned+'");\n'
                    
                if 'Length' in metadata:        
                    length=str(metadata['Length'])
                    skeleton_column_script+='\t\t\tskeleton_column_columnDefinition.SetLength("'+length+'");\n'
                    
                if 'Precision' in metadata:        
                    precision=str(metadata['Precision'])
                    skeleton_column_script+='\t\t\tskeleton_column_columnDefinition.SetPrecision("'+precision+'");\n'
                    
                if 'Scale' in metadata:                    
                    scale=str(metadata['Scale'])
                    skeleton_column_script+='\t\t\tskeleton_column_columnDefinition.SetScale("'+scale+'");\n'
                    
                name=column_definition['Name']
                skeleton_column_script+='\t\t\tskeleton_column.SetName("'+name+'");\n'
                
                if 'Nullable' in metadata:                    
                    nullable=str(column_definition['Nullable'])
                    skeleton_column_script+='\t\tskeleton_column.SetNullable("'+nullable+'");\n'

                if 'Passdownable' in metadata:    
                    passdownable=str(column_definition['Passdownable'])
                    skeleton_column_script+='\t\t\tskeleton_column.SetPassdownable("'+passdownable+'");\n'
                    
                if 'Updatable' in metadata:
                    updatable=str(column_definition['Updatable'])
                    skeleton_column_script+='\t\t\tskeleton_column.SetUpdatable("'+updatable+'");\n'
                    
                list_result=column_definition['SvcRespAttr_ListResult']
                skeleton_column_script+='\t\t\tskeleton_column.SetSvcRespAttrListResult("'+list_result+'");\n'
                item_result=column_definition['SvcRespAttr_ItemResult']
                skeleton_column_script+='\t\t\tskeleton_column.SetSvcRespAttrItemResult("'+item_result+'");\n'
                
                if 'SvcReqParam_QueryMapping' in metadata:
                    query_mapping=column_definition['SvcReqParam_QueryMapping']
                    skeleton_column_script+='\t\t\tskeleton_column.SetSvcReqParamQueryMapping("'+query_mapping+'");\n'

                if 'ColumnPushdown_Mapping' in metadata:
                    passdown_mapping=column_definition['ColumnPushdown_Mapping']
                    skeleton_column_script+='\t\t\tskeleton_column.SetColumnPushDownMapping("'+passdown_mapping+'");\n'

                skeleton_column_script+='\t\t\tskeleton_column.SetColumnDefinition(skeleton_column_columnDefinition);\n'
                skeleton_column_script+='\t\t\tskeleton_columns.SetSkeletonColumnDefinition(skeleton_column);\n' 
                skeleton_column_script+='\t\t}\n'            
            
            final_script+=skeleton_column_script
            final_script+='\t\tskeleton_columns.SetListVariableAccess(skeleton_column_variable_access);\n\n'    
            table_script+='\t\ttable.AddSkeletonColumn(skeleton_columns);\n'
            final_script+=table_script+'\n'
            
        pkey_column=table_definition['PKeyColumn']
        table_pkey_script='\t\tSaaSTablePKeyColumn tablePKey;\n'
        pKey_name='pk_'+table_name
        for PKColumn in pkey_column[pKey_name]:  
            pkey_column_name=PKColumn['PKColumnName']
            table_pkey_script+='\t\ttablePKey.AddPKColumnNames("'+pkey_column_name+'");\n'
        table_pkey_script+='\t\ttablePKey.SetPKeyName("'+pKey_name+'");\n'
        table_pkey_script+='\t\ttable.SetPkeyColumns(tablePKey);\n'
        final_script+=table_pkey_script+'\n'
        column_pushdown_script='\t\tSaaSColumnPushdown columnPushdown;\n'
        if 'ColumnPushdown' in table_definition:        
            column_pushdown=table_definition['ColumnPushdown']
        if 'Support' in column_pushdown:                        
            support=column_pushdown['Support']
            column_pushdown_script+='\t\tcolumnPushdown.SetSupport('+str(support)+');\n'

        column_pushdown_script+='\t\ttable.SetColumnPushdown(columnPushdown);\n'
        final_script+=column_pushdown_script+'\n'
        api_access=table_definition['APIAccess']
        Read_api=api_access['ReadAPI']
        api_access_script='\t\tSaaSTableApiAccess table_apiAccess;\n'          
        api_access_script+='\t\tSaaSReadApi table_readApi;\n'
        method=Read_api['Method']
        api_access_script+='\t\ttable_readApi.SetMethod("'+method+'");\n'
        if 'ItemEndpoint' in Read_api:    
            listroot=Read_api['ListRoot']
            api_access_script+='\t\ttable_readApi.SetListRoot("'+listroot+'");\n\n'

        api_access_script+='\t\tSaaSReadApiEndpoint table_readApiEndpoint;\n'
        if 'ItemEndpoint' in Read_api:    
            item_endpoint=Read_api['Endpoint']['ItemEndpoint']
            api_access_script+='\t\ttable_readApiEndpoint.SetItemEndPoint("'+item_endpoint+'");\n'
        list_endpoint=Read_api['Endpoint']['ListEndpoint']
        api_access_script+='\t\ttable_readApiEndpoint.SetListEndPoint("'+list_endpoint+'");\n'
        if 'Type' in Read_api:                     
            endpoint_type=Read_api['Endpoint']['Type']
            api_access_script+='\t\ttable_readApiEndpoint.SetType("'+endpoint_type+'");\n'

        api_access_script+='\t\ttable_readApi.SetEndPoint(table_readApiEndpoint);\n'
        api_access_script+='\t\ttable_apiAccess.SetReadApi(table_readApi);\n'

        api_access_script+='\t\ttable.SetAPIAccess(table_apiAccess);\n'
        api_access_script+='\t\tskeleton_table.SetTableDefinition(table);\n'
        final_script+=api_access_script+'\n'
        table_list_variable_script='\t\tSaaSListVariable table_listvariable;\n'
        for list_variable_data in skeleton_table_script['ListVariablesPrecalls']:
            endpoint=list_variable_data['Endpoint']
            if 'AcceptType' in list_variable_data:        
                accepting_type=list_variable_data['AcceptType']
                table_list_variable_script+='\t\ttable_listvariable.SetAcceptType("'+accepting_type+'");\n'
            if 'VariableRoot' in list_variable_data:        
                variable_root=list_variable_data['VariableRoot']
                table_list_variable_script+='\t\ttable_listvariable.SetVariableRoot("'+variable_root+'");\n'
            for varibles_data in list_variable_data['Variables']:
                table_varible_script='\t\t{\n'
                variable_name=varibles_data['VariableName']
                svc_resp_attr_mapping=varibles_data['SvcRespAttr_Mapping']
                table_varible_script+='\t\t\tSaaSVariable table_variable;\n'
                table_varible_script+='\t\t\ttable_variable.SetVariableName("'+str(variable_name)+'");\n'
                table_varible_script+='\t\t\ttable_variable.SetSvcRespAttrMapping("'+svc_resp_attr_mapping+'");\n'
                table_varible_script+='\t\t\ttable_listvariable.AddVariables(table_variable);\n'
                table_varible_script+='\t\t}\n'
                table_list_variable_script+=table_varible_script
            
            table_list_variable_script+='\t\ttable_listvariable.SetEndpoint("'+endpoint+'");\n'
            table_list_variable_script+='\t\tskeleton_table.AddListVariablesPrecalls(table_listvariable);\n'
            table_list_variable_script+='\t\tout_configuration.SetSkeletonTableInitialized(false);\n'
            table_list_variable_script+='\t\tout_configuration.AddSkeletonTable(skeleton_table);\n'
        final_script+=table_list_variable_script+'\n}'        
        final_script=final_script.replace('True','true')
        final_script=final_script.replace('False','false')
        final_script=final_script.replace('Template',data_source_name)
        table_name=table_name.replace("_{{tablename}}","")
        table_name=table_name.replace("{","")
        table_name=table_name.replace("}","")
        table_schema_name=table_schema_name.replace("{","")
        table_schema_name=table_schema_name.replace("}","")
        file_name=table_schema_name+table_name
        final_script=final_script.replace('FILENAME',file_name+'.cpp')
        final_script=final_script.replace('FUNCTION_NAME',file_name)

        file_path=sys.argv[2]+file_name+'.cpp'
        f_final = open(file_path,'w')
        f_final.write(final_script)
                    
        # Closing files
        f_final.close()
f_input.close()
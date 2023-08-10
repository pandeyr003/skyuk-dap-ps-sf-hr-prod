import pulumi
from pulumi_azure_native import storage
from pulumi_azure_native import resources
from pulumi_azure_native import authorization
from pulumi_azure_native import datafactory
from pulumi_azure_native import compute
from pulumi_azure_native import network
from pulumi_azure_native import sql
from pulumi_azure_native import web
from pulumi_azure_native import keyvault
from pulumi_azure_native import batch
from pulumi_azure_native import managedidentity
from pulumi_azure_native import insights
from pulumi_azure_native import alertsmanagement

from pulumi import ResourceOptions

pulumi_config = pulumi.Config()
clientConfig = authorization.get_client_config()


def deployResources():
    resource_group = resources.ResourceGroup("skyuk-dap-hr-prod-resgroup",
                                             location="uksouth",
                                             resource_group_name="skyuk-dap-hr-prod-resgroup")

    skyuk_dap_hr_prod_vnet = network.VirtualNetwork("skyuk-dap-hr-prod-vnet",
                                                    address_space=network.AddressSpaceArgs(
                                                        address_prefixes=["10.0.0.0/16"],
                                                    ),
                                                    enable_ddos_protection=False,
                                                    location="uksouth",
                                                    resource_group_name=resource_group.name,
                                                    subnets=[network.SubnetArgs(
                                                        address_prefix="10.0.0.0/24",
                                                        delegations=[network.DelegationArgs(
                                                            id="/subscriptions/9f78709a-9b22-4058-9344-693b333eefe8/resourceGroups/skyuk-dap-hr-prod-resgroup/providers/Microsoft.Network/virtualNetworks/skyuk-dap-hr-prod-vnet/subnets/default/delegations/delegation",
                                                            name="delegation",
                                                            service_name="Microsoft.Web/serverfarms",
                                                            type="Microsoft.Network/virtualNetworks/subnets/delegations",
                                                        )],
                                                        id="/subscriptions/9f78709a-9b22-4058-9344-693b333eefe8/resourceGroups/skyuk-dap-hr-prod-resgroup/providers/Microsoft.Network/virtualNetworks/skyuk-dap-hr-prod-vnet/subnets/default",
                                                        name="default",
                                                        private_endpoint_network_policies="Disabled",
                                                        private_link_service_network_policies="Enabled",
                                                        service_endpoints=[
                                                            network.ServiceEndpointPropertiesFormatArgs(
                                                                locations=[
                                                                    "uksouth",
                                                                    "ukwest",
                                                                ],
                                                                service="Microsoft.Storage",
                                                            )],
                                                        type="Microsoft.Network/virtualNetworks/subnets",
                                                    )],
                                                    virtual_network_name="skyuk-dap-hr-prod-vnet")

    storage_account = storage.StorageAccount("skyukdaphrprodsa",
                                             access_tier=storage.AccessTier.HOT,
                                             account_name="skyukdaphrprodsa",
                                             allow_shared_key_access=False,
                                             enable_https_traffic_only=True,
                                             encryption=storage.EncryptionArgs(
                                                 key_source="Microsoft.Storage",
                                                 services=storage.EncryptionServicesArgs(
                                                     blob=storage.EncryptionServiceArgs(
                                                         enabled=True,
                                                         key_type="Account",
                                                     ),
                                                     file=storage.EncryptionServiceArgs(
                                                         enabled=True,
                                                         key_type="Account",
                                                     ),
                                                 ),
                                             ),
                                             is_hns_enabled=True,
                                             kind="StorageV2",
                                             location="uksouth",
                                             minimum_tls_version="TLS1_2",
                                             network_rule_set=storage.NetworkRuleSetArgs(
                                                 bypass="AzureServices",
                                                 default_action=storage.DefaultAction.DENY,
                                                 ip_rules=[
                                                     storage.IPRuleArgs(
                                                         action=storage.Action.ALLOW,
                                                         i_p_address_or_range="90.216.134.0/24",
                                                     ),
                                                     storage.IPRuleArgs(
                                                         action=storage.Action.ALLOW,
                                                         i_p_address_or_range="90.216.150.0/24",
                                                     ),
                                                 ],
                                                 resource_access_rules=[
                                                     storage.ResourceAccessRuleArgs(
                                                         resource_id="/subscriptions/9f78709a-9b22-4058-9344-693b333eefe8/resourcegroups/skyuk-dap-hr-prod-resgroup/providers/Microsoft.DataFactory/factories/skyuk-dap-hr-prod-adf",
                                                         tenant_id="68b865d5-cf18-4b2b-82a4-a4eddb9c5237",
                                                     )],
                                                 virtual_network_rules=[
                                                     storage.VirtualNetworkRuleArgs(
                                                         action=storage.Action.ALLOW,
                                                         state="Succeeded",
                                                         virtual_network_resource_id="/subscriptions/9f78709a-9b22-4058-9344-693b333eefe8/resourceGroups/skyuk-dap-hr-prod-resgroup/providers/Microsoft.Network/virtualNetworks/skyuk-dap-hr-prod-vnet/subnets/default",
                                                     )],
                                             ),
                                             resource_group_name=resource_group.name,
                                             routing_preference=storage.RoutingPreferenceArgs(
                                                 publish_internet_endpoints=False,
                                                 publish_microsoft_endpoints=True,
                                                 routing_choice="MicrosoftRouting",
                                             ),
                                             sku=storage.SkuArgs(
                                                 name="Standard_LRS",
                                             ))

    peoplesoft = storage.BlobContainer("peoplesoft",
                                       account_name="skyukdaphrprodsa",
                                       container_name="peoplesoft/",
                                       default_encryption_scope="$account-encryption-key",
                                       deny_encryption_scope_override=False,
                                       public_access=storage.PublicAccess.NONE,
                                       resource_group_name=resource_group.name)

    raw = storage.Blob("raw",
                       access_tier=storage.BlobAccessTier.HOT,
                       account_name="skyukdaphrprodsa",
                       blob_name="raw",
                       container_name="peoplesoft",
                       content_md5="",
                       content_type="application/octet-stream",
                       metadata={
                           "hdi_isfolder": "true",
                       },
                       resource_group_name=resource_group.name,
                       type=storage.BlobType.BLOCK)

    config = storage.Blob("config",
                          access_tier=storage.BlobAccessTier.HOT,
                          account_name="skyukdaphrprodsa",
                          blob_name="config",
                          container_name="peoplesoft",
                          metadata={
                              "hdi_isfolder": "true",
                          },
                          resource_group_name=resource_group.name,
                          type=storage.BlobType.BLOCK)

    staging = storage.Blob("staging",
                           access_tier=storage.BlobAccessTier.HOT,
                           account_name="skyukdaphrprodsa",
                           blob_name="staging",
                           container_name="peoplesoft",
                           metadata={
                               "hdi_isfolder": "true",
                           },
                           resource_group_name=resource_group.name,
                           type=storage.BlobType.BLOCK)

    ps_pubsshkey = compute.SshPublicKey("ps-pubsshkey",
                                        location="uksouth",
                                        resource_group_name=resource_group.name,
                                        ssh_public_key_name="ps-pubsshkey")

    sf_pubsshkey = compute.SshPublicKey("sf-pubsshkey",
                                        location="uksouth",
                                        resource_group_name=resource_group.name,
                                        ssh_public_key_name="sf-pubsshkey")

    skyukdaphrpsuser = storage.LocalUser("skyukdaphrpsuser",
                                         account_name="skyukdaphrprodsa",
                                         has_shared_key=False,
                                         has_ssh_key=True,
                                         has_ssh_password=False,
                                         home_directory="peoplesoft/raw/",
                                         permission_scopes=[storage.PermissionScopeArgs(
                                             permissions="rwlc",
                                             resource_name="peoplesoft",
                                             service="blob",
                                         )],
                                         resource_group_name=resource_group.name,
                                         username="skyukdaphrpsuser")

    skyukdaphrsfuser = storage.LocalUser("skyukdaphrsfuser",
                                         account_name="skyukdaphrprodsa",
                                         has_shared_key=False,
                                         has_ssh_key=True,
                                         has_ssh_password=False,
                                         home_directory="salesforce/raw/",
                                         permission_scopes=[storage.PermissionScopeArgs(
                                             permissions="rwlc",
                                             resource_name="salesforce",
                                             service="blob",
                                         )],
                                         resource_group_name=resource_group.name,
                                         username="skyukdaphrsfuser")

    skyuk_dap_hr_ps_prod_sql_server = sql.Server("skyuk-dap-hr-ps-prod-sql-server",
                                                 administrator_login="hrpsadmin",
                                                 administrator_login_password=pulumi_config.require_secret(
                                                     "dbpassword"),
                                                 location="uksouth",
                                                 minimal_tls_version="None",
                                                 public_network_access="Enabled",
                                                 resource_group_name=resource_group.name,
                                                 server_name="skyuk-dap-hr-ps-prod-sql-server",
                                                 version="12.0")

    skyuk_dap_hr_sf_prod_sql_server = sql.Server("skyuk-dap-hr-sf-prod-sql-server",
                                                 administrator_login="hrsfadmin",
                                                 administrator_login_password=pulumi_config.require_secret(
                                                     "dbpassword1"),
                                                 location="uksouth",
                                                 minimal_tls_version="None",
                                                 public_network_access="Enabled",
                                                 resource_group_name=resource_group.name,
                                                 server_name="skyuk-dap-hr-sf-prod-sql-server",
                                                 version="12.0")

    skyuk_dap_hr_ps_prod_sql_db = sql.Database("skyuk-dap-hr-ps-prod-sql-db",
                                               catalog_collation="SQL_Latin1_General_CP1_CI_AS",
                                               collation="SQL_Latin1_General_CP1_CI_AS",
                                               database_name="skyuk-dap-hr-ps-prod-sql-db",
                                               location="uksouth",
                                               maintenance_configuration_id="/subscriptions/9f78709a-9b22-4058-9344-693b333eefe8/providers/Microsoft.Maintenance/publicMaintenanceConfigurations/SQL_Default",
                                               max_size_bytes=268435456000,
                                               read_scale="Disabled",
                                               requested_backup_storage_redundancy="Geo",
                                               resource_group_name=resource_group.name,
                                               server_name="skyuk-dap-hr-ps-prod-sql-server",
                                               sku=sql.SkuArgs(
                                                   capacity=50,
                                                   name="Standard",
                                                   tier="Standard",
                                               ),
                                               zone_redundant=False)

    skyuk_dap_hr_sf_prod_sql_db = sql.Database("skyuk-dap-hr-sf-prod-sql-db",
                                               catalog_collation="SQL_Latin1_General_CP1_CI_AS",
                                               collation="SQL_Latin1_General_CP1_CI_AS",
                                               database_name="skyuk-dap-hr-sf-prod-sql-db",
                                               location="uksouth",
                                               maintenance_configuration_id="/subscriptions/9f78709a-9b22-4058-9344-693b333eefe8/providers/Microsoft.Maintenance/publicMaintenanceConfigurations/SQL_Default",
                                               max_size_bytes=268435456000,
                                               read_scale="Disabled",
                                               requested_backup_storage_redundancy="Geo",
                                               resource_group_name=resource_group.name,
                                               server_name="skyuk-dap-hr-sf-prod-sql-server",
                                               sku=sql.SkuArgs(
                                                   capacity=50,
                                                   name="Standard",
                                                   tier="Standard",
                                               ),
                                               zone_redundant=False)

    skyuk_dap_sab_prod_batch = batch.BatchAccount("skyuk-dap-hr-prod-batch",
                                                  account_name="skyukdaphrprodbatch",
                                                  encryption=batch.EncryptionPropertiesArgs(
                                                      key_source=batch.KeySource.MICROSOFT_BATCH,
                                                  ),
                                                  identity=batch.BatchAccountIdentityArgs(
                                                      type=batch.ResourceIdentityType.SYSTEM_ASSIGNED,
                                                  ),
                                                  location=resource_group.location,
                                                  pool_allocation_mode=batch.PoolAllocationMode.BATCH_SERVICE,
                                                  public_network_access=batch.PublicNetworkAccessType.ENABLED,
                                                  resource_group_name=resource_group.name)

    prod_pool = batch.Pool("prod-pool",
                           account_name="skyukdaphrprodbatch",
                           deployment_configuration=batch.DeploymentConfigurationArgs(
                               virtual_machine_configuration={
                                   "imageReference": batch.ImageReferenceArgs(
                                       offer="dsvm-win-2019",
                                       publisher="microsoft-dsvm",
                                       sku="winserver-2019",
                                       version="latest",
                                   ),
                                   "nodeAgentSkuId": "batch.node.windows amd64",
                               },
                           ),
                           pool_name="prod-pool",
                           resource_group_name=resource_group.name,
                           scale_settings=batch.ScaleSettingsArgs(
                               auto_scale=batch.AutoScaleSettingsArgs(
                                   evaluation_interval="PT5M",
                                   formula="$TargetDedicatedNodes=1",
                               ),
                           ),
                           vm_size="STANDARD_D8S_V3")

    skyuk_dap_hr_ps_prod_adf = datafactory.Factory("skyuk-dap-hr-ps-prod-adf",
                                                   factory_name="skyuk-dap-hr-ps-prod-adf",
                                                   identity=datafactory.FactoryIdentityArgs(
                                                       type="SystemAssigned",
                                                   ),
                                                   location="uksouth",
                                                   public_network_access="Enabled",
                                                   resource_group_name=resource_group.name)

    skyuk_dap_hr_sf_prod_adf = datafactory.Factory("skyuk-dap-hr-sf-prod-adf",
                                                   factory_name="skyuk-dap-hr-sf-prod-adf",
                                                   identity=datafactory.FactoryIdentityArgs(
                                                       type="SystemAssigned",
                                                   ),
                                                   location="uksouth",
                                                   public_network_access="Enabled",
                                                   resource_group_name=resource_group.name)

    ls_sqldb = datafactory.LinkedService("ls_sqldb",
                                         factory_name="skyuk-dap-hr-ps-prod-adf",
                                         linked_service_name="ls_sqldb",
                                         properties=datafactory.AzureSqlDatabaseLinkedServiceArgs(
                                             connection_string="integrated security=False;encrypt=True;connection timeout=30;data source=skyuk-dap-hr-ps-prod-sql-server.database.windows.net;initial catalog=skyuk-dap-hr-ps-prod-sql-db;user id=dbadmin",
                                             encrypted_credential="ew0KICAiVmVyc2lvbiI6ICIyMDE3LTExLTMwIiwNCiAgIlByb3RlY3Rpb25Nb2RlIjogIktleSIsDQogICJTZWNyZXRDb250ZW50VHlwZSI6ICJQbGFpbnRleHQiLA0KICAiQ3JlZGVudGlhbElkIjogIkRBVEFGQUNUT1JZQDAxRjhCQzUwLURBNjktNEQ5OC1CNjA0LTkyNzYzQTE5QTA5Ml9kN2NhZDI1NS0zODE0LTRkODktOTBhMC00M2I0MjNhMTZlYTIiDQp9",
                                             type="AzureSqlDatabase",
                                         ),
                                         resource_group_name=resource_group.name)

    ls_sqldb_sf = datafactory.LinkedService("ls_sqldb_sf",
                                            factory_name="skyuk-dap-hr-sf-prod-adf",
                                            linked_service_name="ls_sqldb",
                                            properties=datafactory.AzureSqlDatabaseLinkedServiceArgs(
                                                connection_string="integrated security=False;encrypt=True;connection timeout=30;data source=skyuk-dap-hr-sf-prod-sql-server.database.windows.net;initial catalog=skyuk-dap-hr-sf-prod-sql-db;user id=dbadmin",
                                                encrypted_credential="ew0KICAiVmVyc2lvbiI6ICIyMDE3LTExLTMwIiwNCiAgIlByb3RlY3Rpb25Nb2RlIjogIktleSIsDQogICJTZWNyZXRDb250ZW50VHlwZSI6ICJQbGFpbnRleHQiLA0KICAiQ3JlZGVudGlhbElkIjogIkRBVEFGQUNUT1JZQDAxRjhCQzUwLURBNjktNEQ5OC1CNjA0LTkyNzYzQTE5QTA5Ml9kN2NhZDI1NS0zODE0LTRkODktOTBhMC00M2I0MjNhMTZlYTIiDQp9",
                                                type="AzureSqlDatabase",
                                            ),
                                            resource_group_name=resource_group.name)

    ls_prodsaconfig = datafactory.LinkedService("ls_prodsaconfig",
                                                factory_name="skyuk-dap-hr-ps-prod-adf",
                                                linked_service_name="ls_prodsaconfig",
                                                properties=datafactory.AzureBlobStorageLinkedServiceArgs(
                                                    connection_string="DefaultEndpointsProtocol=https;AccountName=prodsaconfig;EndpointSuffix=core.windows.net;",
                                                    encrypted_credential="ew0KICAiVmVyc2lvbiI6ICIyMDE3LTExLTMwIiwNCiAgIlByb3RlY3Rpb25Nb2RlIjogIktleSIsDQogICJTZWNyZXRDb250ZW50VHlwZSI6ICJQbGFpbnRleHQiLA0KICAiQ3JlZGVudGlhbElkIjogIkRBVEFGQUNUT1JZQDAxRjhCQzUwLURBNjktNEQ5OC1CNjA0LTkyNzYzQTE5QTA5Ml83ZWU5NDcxZC0xMTJlLTQyYWEtYTlhMC0zNWE5ZmJmY2MyNDMiDQp9",
                                                    type="AzureBlobStorage",
                                                ),
                                                resource_group_name=resource_group.name)

    ls_prodsaconfig_sf = datafactory.LinkedService("ls_prodsaconfig_sf",
                                                   factory_name="skyuk-dap-hr-sf-prod-adf",
                                                   linked_service_name="ls_prodsaconfig",
                                                   properties=datafactory.AzureBlobStorageLinkedServiceArgs(
                                                       connection_string="DefaultEndpointsProtocol=https;AccountName=prodsaconfig;EndpointSuffix=core.windows.net;",
                                                       encrypted_credential="ew0KICAiVmVyc2lvbiI6ICIyMDE3LTExLTMwIiwNCiAgIlByb3RlY3Rpb25Nb2RlIjogIktleSIsDQogICJTZWNyZXRDb250ZW50VHlwZSI6ICJQbGFpbnRleHQiLA0KICAiQ3JlZGVudGlhbElkIjogIkRBVEFGQUNUT1JZQDAxRjhCQzUwLURBNjktNEQ5OC1CNjA0LTkyNzYzQTE5QTA5Ml83ZWU5NDcxZC0xMTJlLTQyYWEtYTlhMC0zNWE5ZmJmY2MyNDMiDQp9",
                                                       type="AzureBlobStorage",
                                                   ),
                                                   resource_group_name=resource_group.name)

    ls_batch_service = datafactory.LinkedService("ls_batch_service",
                                                 factory_name="skyuk-dap-hr-ps-prod-adf",
                                                 linked_service_name="ls_batch_service",
                                                 properties=datafactory.AzureBatchLinkedServiceArgs(
                                                     account_name="skyukdaphrprodbatch",
                                                     batch_uri="https://skyukdaphrprodbatch.uksouth.batch.azure.com",
                                                     encrypted_credential="ew0KICAiVmVyc2lvbiI6ICIyMDE3LTExLTMwIiwNCiAgIlByb3RlY3Rpb25Nb2RlIjogIktleSIsDQogICJTZWNyZXRDb250ZW50VHlwZSI6ICJQbGFpbnRleHQiLA0KICAiQ3JlZGVudGlhbElkIjogIkRBVEFGQUNUT1JZQDAxRjhCQzUwLURBNjktNEQ5OC1CNjA0LTkyNzYzQTE5QTA5Ml9hZTc1NTIyNS00ZGE0LTRiNGQtYjNlNy05NzFhYTM1NjRiYzUiDQp9",
                                                     linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                         reference_name="ls_prodsaconfig",
                                                         type="LinkedServiceReference",
                                                     ),
                                                     pool_name="prod-pool",
                                                     type="AzureBatch",
                                                 ),
                                                 resource_group_name=resource_group.name)

    ls_batch_service_sf = datafactory.LinkedService("ls_batch_service_sf",
                                                    factory_name="skyuk-dap-hr-sf-prod-adf",
                                                    linked_service_name="ls_batch_service",
                                                    properties=datafactory.AzureBatchLinkedServiceArgs(
                                                        account_name="skyukdaphrprodbatch",
                                                        batch_uri="https://skyukdaphrprodbatch.uksouth.batch.azure.com",
                                                        encrypted_credential="ew0KICAiVmVyc2lvbiI6ICIyMDE3LTExLTMwIiwNCiAgIlByb3RlY3Rpb25Nb2RlIjogIktleSIsDQogICJTZWNyZXRDb250ZW50VHlwZSI6ICJQbGFpbnRleHQiLA0KICAiQ3JlZGVudGlhbElkIjogIkRBVEFGQUNUT1JZQDAxRjhCQzUwLURBNjktNEQ5OC1CNjA0LTkyNzYzQTE5QTA5Ml9hZTc1NTIyNS00ZGE0LTRiNGQtYjNlNy05NzFhYTM1NjRiYzUiDQp9",
                                                        linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                            reference_name="ls_prodsaconfig",
                                                            type="LinkedServiceReference",
                                                        ),
                                                        pool_name="prod-pool",
                                                        type="AzureBatch",
                                                    ),
                                                    resource_group_name=resource_group.name)

    ls_adls = datafactory.LinkedService("ls_adls",
                                        factory_name="skyuk-dap-hr-ps-prod-adf",
                                        linked_service_name="ls_adls",
                                        properties=datafactory.AzureBlobFSLinkedServiceArgs(
                                            type="AzureBlobFS",
                                            url="https://skyukdaphrprodsa.dfs.core.windows.net/",
                                        ),
                                        resource_group_name=resource_group.name)

    ls_adls_sf = datafactory.LinkedService("ls_adls_sf",
                                           factory_name="skyuk-dap-hr-sf-prod-adf",
                                           linked_service_name="ls_adls",
                                           properties=datafactory.AzureBlobFSLinkedServiceArgs(
                                               type="AzureBlobFS",
                                               url="https://skyukdaphrprodsa.dfs.core.windows.net/",
                                           ),
                                           resource_group_name=resource_group.name)

    ds_prodsatarget = datafactory.Dataset("ds_prodsatarget",
                                          dataset_name="ds_prodsatarget",
                                          factory_name="skyuk-dap-hr-ps-prod-adf",
                                          properties=datafactory.AzureSqlTableDatasetArgs(
                                              linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                  reference_name="ls_sqldb",
                                                  type="LinkedServiceReference",
                                              ),
                                              schema=[
                                                  {
                                                      "name": "CONTAINER_NAME",
                                                      "type": "varchar",
                                                  },
                                                  {
                                                      "name": "FILENAME",
                                                      "type": "varchar",
                                                  },
                                                  {
                                                      "name": "URL",
                                                      "type": "varchar",
                                                  },
                                                  {
                                                      "name": "TOBEDELETED",
                                                      "type": "char",
                                                  },
                                              ],
                                              table="tb_ps_attachments_url_lookup",
                                              type="AzureSqlTable",
                                          ),
                                          resource_group_name=resource_group.name)

    ds_prodsaconfig = datafactory.Dataset("ds_prodsaconfig",
                                          dataset_name="ds_prodsaconfig",
                                          factory_name="skyuk-dap-hr-ps-prod-adf",
                                          properties=datafactory.DelimitedTextDatasetArgs(
                                              column_delimiter=",",
                                              escape_char="\\",
                                              first_row_as_header=True,
                                              linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                  reference_name="ls_prodsaconfig",
                                                  type="LinkedServiceReference",
                                              ),
                                              location=datafactory.AzureBlobStorageLocationArgs(
                                                  container="config",
                                                  file_name="table_filename_url.csv",
                                                  type="AzureBlobStorageLocation",
                                              ),
                                              quote_char="\"",
                                              schema=[
                                                  {
                                                      "name": "Name",
                                                      "type": "String",
                                                  },
                                                  {
                                                      "name": "Category",
                                                      "type": "String",
                                                  },
                                                  {
                                                      "name": "Status",
                                                      "type": "String",
                                                  },
                                                  {
                                                      "name": "Error",
                                                      "type": "String",
                                                  },
                                              ],
                                              type="DelimitedText",
                                          ),
                                          resource_group_name=resource_group.name)

    ds_attachment_zip = datafactory.Dataset("ds_attachment_zip",
                                            dataset_name="ds_attachment_zip",
                                            factory_name="skyuk-dap-hr-ps-prod-adf",
                                            properties=datafactory.BinaryDatasetArgs(
                                                linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                    reference_name="ls_adls",
                                                    type="LinkedServiceReference",
                                                ),
                                                location=datafactory.AzureBlobFSLocationArgs(
                                                    file_system="peoplesoft",
                                                    folder_path="raw/decrypted",
                                                    type="AzureBlobFSLocation",
                                                ),
                                                type="Binary",
                                            ),
                                            resource_group_name=resource_group.name)

    ds_raw_zip = datafactory.Dataset("ds_raw_zip",
                                     dataset_name="ds_raw_zip",
                                     factory_name="skyuk-dap-hr-ps-prod-adf",
                                     properties=datafactory.BinaryDatasetArgs(
                                         compression=datafactory.DatasetCompressionArgs(
                                             level="Optimal",
                                             type="ZipDeflate",
                                         ),
                                         linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                             reference_name="ls_adls",
                                             type="LinkedServiceReference",
                                         ),
                                         location=datafactory.AzureBlobFSLocationArgs(
                                             file_name={
                                                 "type": "Expression",
                                                 "value": "@dataset().ZipFileName",
                                             },
                                             file_system="peoplesoft",
                                             folder_path="raw/decrypted",
                                             type="AzureBlobFSLocation",
                                         ),
                                         parameters={
                                             "ZipFileName": datafactory.ParameterSpecificationArgs(
                                                 type="string",
                                             ),
                                         },
                                         type="Binary",
                                     ),
                                     resource_group_name=resource_group.name)

    ds_extracted_zip = datafactory.Dataset("ds_extracted_zip",
                                           dataset_name="ds_extracted_zip",
                                           factory_name="skyuk-dap-hr-ps-prod-adf",
                                           properties=datafactory.BinaryDatasetArgs(
                                               linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                   reference_name="ls_adls",
                                                   type="LinkedServiceReference",
                                               ),
                                               location=datafactory.AzureBlobFSLocationArgs(
                                                   file_system="peoplesoft",
                                                   folder_path="staging",
                                                   type="AzureBlobFSLocation",
                                               ),
                                               type="Binary",
                                           ),
                                           resource_group_name=resource_group.name)

    ds_attachment_zip_sf = datafactory.Dataset("ds_attachment_zip_sf",
                                               dataset_name="ds_attachment_zip",
                                               factory_name="skyuk-dap-hr-sf-prod-adf",
                                               properties=datafactory.BinaryDatasetArgs(
                                                   linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                       reference_name="ls_adls",
                                                       type="LinkedServiceReference",
                                                   ),
                                                   location=datafactory.AzureBlobFSLocationArgs(
                                                       file_system="salesforce",
                                                       folder_path="raw/attachments",
                                                       type="AzureBlobFSLocation",
                                                   ),
                                                   type="Binary",
                                               ),
                                               resource_group_name=resource_group.name)

    ds_config_lookup_sf = datafactory.Dataset("ds_config_lookup_sf",
                                              dataset_name="ds_config_lookup",
                                              factory_name="skyuk-dap-hr-sf-prod-adf",
                                              properties=datafactory.DelimitedTextDatasetArgs(
                                                  column_delimiter=",",
                                                  escape_char="\\",
                                                  first_row_as_header=True,
                                                  linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                      reference_name="ls_adls",
                                                      type="LinkedServiceReference",
                                                  ),
                                                  location=datafactory.AzureBlobFSLocationArgs(
                                                      file_name={
                                                          "type": "Expression",
                                                          "value": "@dataset().filename",
                                                      },
                                                      file_system="salesforce",
                                                      folder_path="config",
                                                      type="AzureBlobFSLocation",
                                                  ),
                                                  parameters={
                                                      "filename": datafactory.ParameterSpecificationArgs(
                                                          type="string",
                                                      ),
                                                  },
                                                  quote_char="\"",
                                                  schema=[
                                                      {
                                                          "name": "FILENAME",
                                                          "type": "String",
                                                      },
                                                      {
                                                          "name": "TARGETTABLENAME",
                                                          "type": "String",
                                                      },
                                                      {
                                                          "name": "PURGINGPERIOD",
                                                          "type": "String",
                                                      },
                                                  ],
                                                  type="DelimitedText",
                                              ),
                                              resource_group_name=resource_group.name)

    ds_csv_data_sf = datafactory.Dataset("ds_csv_data_sf",
                                         dataset_name="ds_csv_data",
                                         factory_name="skyuk-dap-hr-sf-prod-adf",
                                         properties=datafactory.DelimitedTextDatasetArgs(
                                             column_delimiter=",",
                                             escape_char="\"",
                                             first_row_as_header=True,
                                             linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                 reference_name="ls_adls",
                                                 type="LinkedServiceReference",
                                             ),
                                             location=datafactory.AzureBlobFSLocationArgs(
                                                 file_name={
                                                     "type": "Expression",
                                                     "value": "@dataset().filename",
                                                 },
                                                 file_system="salesforce",
                                                 folder_path="staging/static_data",
                                                 type="AzureBlobFSLocation",
                                             ),
                                             parameters={
                                                 "filename": datafactory.ParameterSpecificationArgs(
                                                     type="string",
                                                 ),
                                             },
                                             quote_char="\"",
                                             type="DelimitedText",
                                         ),
                                         resource_group_name=resource_group.name)

    ds_csv_zip_sf = datafactory.Dataset("ds_csv_zip_sf",
                                        dataset_name="ds_csv_zip",
                                        factory_name="skyuk-dap-hr-sf-prod-adf",
                                        properties=datafactory.BinaryDatasetArgs(
                                            compression=datafactory.DatasetCompressionArgs(
                                                level="Optimal",
                                                type="ZipDeflate",
                                            ),
                                            linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                reference_name="ls_adls",
                                                type="LinkedServiceReference",
                                            ),
                                            location=datafactory.AzureBlobFSLocationArgs(
                                                file_name="CSV_FILES.zip",
                                                file_system="salesforce",
                                                folder_path="raw/static_data",
                                                type="AzureBlobFSLocation",
                                            ),
                                            type="Binary",
                                        ),
                                        resource_group_name=resource_group.name)

    ds_database_table_lookup_sf = datafactory.Dataset("ds_database_table_lookup_sf",
                                                      dataset_name="ds_database_table_lookup",
                                                      factory_name="skyuk-dap-hr-sf-prod-adf",
                                                      properties=datafactory.AzureSqlTableDatasetArgs(
                                                          linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                              reference_name="ls_sqldb",
                                                              type="LinkedServiceReference",
                                                          ),
                                                          parameters={
                                                              "tablename": datafactory.ParameterSpecificationArgs(
                                                                  type="string",
                                                              ),
                                                          },
                                                          table={
                                                              "type": "Expression",
                                                              "value": "@dataset().tablename",
                                                          },
                                                          type="AzureSqlTable",
                                                      ),
                                                      resource_group_name=resource_group.name)

    ds_prodsatarget_sf = datafactory.Dataset("ds_prodsatarget_sf",
                                             dataset_name="ds_prodsatarget",
                                             factory_name="skyuk-dap-hr-sf-prod-adf",
                                             properties=datafactory.AzureSqlTableDatasetArgs(
                                                 linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                     reference_name="ls_sqldb",
                                                     type="LinkedServiceReference",
                                                 ),
                                                 schema=[
                                                     {
                                                         "name": "CONTAINER_NAME",
                                                         "type": "varchar",
                                                     },
                                                     {
                                                         "name": "FILENAME",
                                                         "type": "varchar",
                                                     },
                                                     {
                                                         "name": "URL",
                                                         "type": "varchar",
                                                     },
                                                     {
                                                         "name": "TOBEDELETED",
                                                         "type": "char",
                                                     },
                                                 ],
                                                 table="tb_sf_attachments_url_lookup",
                                                 type="AzureSqlTable",
                                             ),
                                             resource_group_name=resource_group.name)

    ds_prodsaconfig_sf = datafactory.Dataset("ds_prodsaconfig_sf",
                                             dataset_name="ds_prodsaconfig",
                                             factory_name="skyuk-dap-hr-sf-prod-adf",
                                             properties=datafactory.DelimitedTextDatasetArgs(
                                                 column_delimiter=",",
                                                 escape_char="\\",
                                                 first_row_as_header=True,
                                                 linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                     reference_name="ls_prodsaconfig",
                                                     type="LinkedServiceReference",
                                                 ),
                                                 location=datafactory.AzureBlobStorageLocationArgs(
                                                     container="config",
                                                     file_name="table_filename_url.csv",
                                                     type="AzureBlobStorageLocation",
                                                 ),
                                                 quote_char="\"",
                                                 schema=[
                                                     {
                                                         "name": "Name",
                                                         "type": "String",
                                                     },
                                                     {
                                                         "name": "Category",
                                                         "type": "String",
                                                     },
                                                     {
                                                         "name": "Status",
                                                         "type": "String",
                                                     },
                                                     {
                                                         "name": "Error",
                                                         "type": "String",
                                                     },
                                                 ],
                                                 type="DelimitedText",
                                             ),
                                             resource_group_name=resource_group.name)

    ds_extracted_csv_sf = datafactory.Dataset("ds_extracted_csv_sf",
                                              dataset_name="ds_extracted_csv",
                                              factory_name="skyuk-dap-hr-sf-prod-adf",
                                              properties=datafactory.BinaryDatasetArgs(
                                                  linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                      reference_name="ls_adls",
                                                      type="LinkedServiceReference",
                                                  ),
                                                  location=datafactory.AzureBlobFSLocationArgs(
                                                      file_system="salesforce",
                                                      folder_path="staging/static_data",
                                                      type="AzureBlobFSLocation",
                                                  ),
                                                  type="Binary",
                                              ),
                                              resource_group_name=resource_group.name)

    ds_extracted_zip_sf = datafactory.Dataset("ds_extracted_zip_sf",
                                              dataset_name="ds_extracted_zip",
                                              factory_name="skyuk-dap-hr-sf-prod-adf",
                                              properties=datafactory.BinaryDatasetArgs(
                                                  linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                      reference_name="ls_adls",
                                                      type="LinkedServiceReference",
                                                  ),
                                                  location=datafactory.AzureBlobFSLocationArgs(
                                                      file_system="salesforce",
                                                      folder_path="staging/attachments",
                                                      type="AzureBlobFSLocation",
                                                  ),
                                                  type="Binary",
                                              ),
                                              resource_group_name=resource_group.name)

    ds_metadata_csv_sf = datafactory.Dataset("ds_metadata_csv_sf",
                                             dataset_name="ds_metadata_csv",
                                             factory_name="skyuk-dap-hr-sf-prod-adf",
                                             properties=datafactory.DelimitedTextDatasetArgs(
                                                 column_delimiter=",",
                                                 escape_char="\\",
                                                 first_row_as_header=True,
                                                 linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                     reference_name="ls_adls",
                                                     type="LinkedServiceReference",
                                                 ),
                                                 location=datafactory.AzureBlobFSLocationArgs(
                                                     file_system="salesforce",
                                                     folder_path="staging/static_data",
                                                     type="AzureBlobFSLocation",
                                                 ),
                                                 quote_char="\"",
                                                 type="DelimitedText",
                                             ),
                                             resource_group_name=resource_group.name)

    ds_raw_zip_sf = datafactory.Dataset("ds_raw_zip_sf",
                                        dataset_name="ds_raw_zip",
                                        factory_name="skyuk-dap-hr-sf-prod-adf",
                                        properties=datafactory.BinaryDatasetArgs(
                                            compression=datafactory.DatasetCompressionArgs(
                                                level="Optimal",
                                                type="ZipDeflate",
                                            ),
                                            linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                reference_name="ls_adls",
                                                type="LinkedServiceReference",
                                            ),
                                            location=datafactory.AzureBlobFSLocationArgs(
                                                file_name={
                                                    "type": "Expression",
                                                    "value": "@dataset().ZipFileName",
                                                },
                                                file_system="salesforce",
                                                folder_path="raw/attachments",
                                                type="AzureBlobFSLocation",
                                            ),
                                            parameters={
                                                "ZipFileName": datafactory.ParameterSpecificationArgs(
                                                    type="string",
                                                ),
                                            },
                                            type="Binary",
                                        ),
                                        resource_group_name=resource_group.name)

    pl_data_preparation_url = datafactory.Pipeline("pl_data_preparation_url",
                                                   activities=[
                                                       datafactory.CustomActivityArgs(
                                                           command="python url_prep_script_ps.py",
                                                           folder_path="config",
                                                           linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                               reference_name="ls_batch_service",
                                                               type="LinkedServiceReference",
                                                           ),
                                                           name="prepare URLs",
                                                           policy=datafactory.ActivityPolicyArgs(
                                                               retry=0,
                                                               retry_interval_in_seconds=30,
                                                               secure_input=False,
                                                               secure_output=False,
                                                               timeout="0.12:00:00",
                                                           ),
                                                           resource_linked_service=datafactory.LinkedServiceReferenceArgs(
                                                               reference_name="ls_prodsaconfig",
                                                               type="LinkedServiceReference",
                                                           ),
                                                           type="Custom",
                                                       ),
                                                       datafactory.CopyActivityArgs(
                                                           depends_on=[datafactory.ActivityDependencyArgs(
                                                               activity="prepare URLs",
                                                               dependency_conditions=["Succeeded"],
                                                           )],
                                                           enable_staging=False,
                                                           inputs=[datafactory.DatasetReferenceArgs(
                                                               reference_name="ds_prodsaconfig",
                                                               type="DatasetReference",
                                                           )],
                                                           name="Load URLs",
                                                           outputs=[datafactory.DatasetReferenceArgs(
                                                               reference_name="ds_prodsatarget",
                                                               type="DatasetReference",
                                                           )],
                                                           policy=datafactory.ActivityPolicyArgs(
                                                               retry=0,
                                                               retry_interval_in_seconds=30,
                                                               secure_input=False,
                                                               secure_output=False,
                                                               timeout="0.12:00:00",
                                                           ),
                                                           sink=datafactory.AzureSqlSinkArgs(
                                                               sql_writer_use_table_lock=False,
                                                               type="AzureSqlSink",
                                                               write_behavior="insert",
                                                           ),
                                                           source=datafactory.DelimitedTextSourceArgs(
                                                               format_settings=datafactory.DelimitedTextReadSettingsArgs(
                                                                   type="DelimitedTextReadSettings",
                                                               ),
                                                               store_settings=datafactory.AzureBlobStorageReadSettingsArgs(
                                                                   enable_partition_discovery=False,
                                                                   recursive=True,
                                                                   type="AzureBlobStorageReadSettings",
                                                               ),
                                                               type="DelimitedTextSource",
                                                           ),
                                                           translator={
                                                               "type": "TabularTranslator",
                                                               "typeConversion": True,
                                                               "typeConversionSettings": {
                                                                   "allowDataTruncation": True,
                                                                   "treatBooleanAsNumber": False,
                                                               },
                                                           },
                                                           type="Copy",
                                                       ),
                                                       datafactory.DeleteActivityArgs(
                                                           dataset=datafactory.DatasetReferenceArgs(
                                                               reference_name="ds_prodsaconfig",
                                                               type="DatasetReference",
                                                           ),
                                                           depends_on=[datafactory.ActivityDependencyArgs(
                                                               activity="Load URLs",
                                                               dependency_conditions=["Succeeded"],
                                                           )],
                                                           enable_logging=True,
                                                           log_storage_settings=datafactory.LogStorageSettingsArgs(
                                                               linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                                   reference_name="ls_prodsaconfig",
                                                                   type="LinkedServiceReference",
                                                               ),
                                                               path="config",
                                                           ),
                                                           name="Delete CSV",
                                                           policy=datafactory.ActivityPolicyArgs(
                                                               retry=0,
                                                               retry_interval_in_seconds=30,
                                                               secure_input=False,
                                                               secure_output=False,
                                                               timeout="0.12:00:00",
                                                           ),
                                                           store_settings=datafactory.AzureBlobStorageReadSettingsArgs(
                                                               enable_partition_discovery=False,
                                                               recursive=True,
                                                               type="AzureBlobStorageReadSettings",
                                                           ),
                                                           type="Delete",
                                                       ),
                                                   ],
                                                   factory_name="skyuk-dap-hr-ps-prod-adf",
                                                   pipeline_name="pl_data_preparation_url",
                                                   resource_group_name=resource_group.name)

    pl_decrypt = datafactory.Pipeline("pl_decrypt",
                                      activities=[
                                          datafactory.CustomActivityArgs(
                                              command="python blob-aes-decryption_production.py",
                                              folder_path="config",
                                              linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                  reference_name="ls_batch_service",
                                                  type="LinkedServiceReference",
                                              ),
                                              name="decrypt",
                                              policy=datafactory.ActivityPolicyArgs(
                                                  retry=0,
                                                  retry_interval_in_seconds=30,
                                                  secure_input=False,
                                                  secure_output=False,
                                                  timeout="0.12:00:00",
                                              ),
                                              resource_linked_service=datafactory.LinkedServiceReferenceArgs(
                                                  reference_name="ls_prodsaconfig",
                                                  type="LinkedServiceReference",
                                              ),
                                              type="Custom",
                                          ),
                                          datafactory.GetMetadataActivityArgs(
                                              dataset=datafactory.DatasetReferenceArgs(
                                                  reference_name="ds_attachment_zip",
                                                  type="DatasetReference",
                                              ),
                                              depends_on=[datafactory.ActivityDependencyArgs(
                                                  activity="decrypt",
                                                  dependency_conditions=["Succeeded"],
                                              )],
                                              field_list=["childItems"],
                                              format_settings=datafactory.BinaryReadSettingsArgs(
                                                  type="BinaryReadSettings",
                                              ),
                                              name="CountZipFile",
                                              policy=datafactory.ActivityPolicyArgs(
                                                  retry=0,
                                                  retry_interval_in_seconds=30,
                                                  secure_input=False,
                                                  secure_output=False,
                                                  timeout="0.12:00:00",
                                              ),
                                              store_settings=datafactory.AzureBlobFSReadSettingsArgs(
                                                  enable_partition_discovery=False,
                                                  type="AzureBlobFSReadSettings",
                                              ),
                                              type="GetMetadata",
                                          ),
                                          datafactory.ForEachActivityArgs(
                                              activities=[datafactory.CopyActivityArgs(
                                                  enable_staging=False,
                                                  inputs=[datafactory.DatasetReferenceArgs(
                                                      parameters={
                                                          "ZipFileName": {
                                                              "type": "Expression",
                                                              "value": "@item().name",
                                                          },
                                                      },
                                                      reference_name="ds_raw_zip",
                                                      type="DatasetReference",
                                                  )],
                                                  name="ExtractZip",
                                                  outputs=[datafactory.DatasetReferenceArgs(
                                                      reference_name="ds_extracted_zip",
                                                      type="DatasetReference",
                                                  )],
                                                  policy=datafactory.ActivityPolicyArgs(
                                                      retry=0,
                                                      retry_interval_in_seconds=30,
                                                      secure_input=False,
                                                      secure_output=False,
                                                      timeout="0.12:00:00",
                                                  ),
                                                  sink=datafactory.BinarySinkArgs(
                                                      store_settings=datafactory.AzureBlobFSWriteSettingsArgs(
                                                          type="AzureBlobFSWriteSettings",
                                                      ),
                                                      type="BinarySink",
                                                  ),
                                                  source=datafactory.BinarySourceArgs(
                                                      format_settings=datafactory.BinaryReadSettingsArgs(
                                                          compression_properties=datafactory.ZipDeflateReadSettingsArgs(
                                                              preserve_zip_file_name_as_folder=False,
                                                              type="ZipDeflateReadSettings",
                                                          ),
                                                          type="BinaryReadSettings",
                                                      ),
                                                      store_settings=datafactory.AzureBlobFSReadSettingsArgs(
                                                          recursive=True,
                                                          type="AzureBlobFSReadSettings",
                                                      ),
                                                      type="BinarySource",
                                                  ),
                                                  type="Copy",
                                              )],
                                              depends_on=[datafactory.ActivityDependencyArgs(
                                                  activity="CountZipFile",
                                                  dependency_conditions=["Succeeded"],
                                              )],
                                              is_sequential=True,
                                              items=datafactory.ExpressionArgs(
                                                  type="Expression",
                                                  value="@activity('CountZipFile').output.childItems",
                                              ),
                                              name="ForEachZipFile",
                                              type="ForEach",
                                          ),
                                      ],
                                      factory_name="skyuk-dap-hr-ps-prod-adf",
                                      pipeline_name="pl_decrypt",
                                      resource_group_name=resource_group.name)

    pl_zip_extraction_ps = datafactory.Pipeline("pl_zip_extraction_ps",
                                                activities=[
                                                    datafactory.GetMetadataActivityArgs(
                                                        dataset=datafactory.DatasetReferenceArgs(
                                                            reference_name="ds_attachment_zip",
                                                            type="DatasetReference",
                                                        ),
                                                        field_list=["childItems"],
                                                        format_settings=datafactory.BinaryReadSettingsArgs(
                                                            type="BinaryReadSettings",
                                                        ),
                                                        name="CountZipFile",
                                                        policy=datafactory.ActivityPolicyArgs(
                                                            retry=0,
                                                            retry_interval_in_seconds=30,
                                                            secure_input=False,
                                                            secure_output=False,
                                                            timeout="0.12:00:00",
                                                        ),
                                                        store_settings=datafactory.AzureBlobFSReadSettingsArgs(
                                                            enable_partition_discovery=False,
                                                            recursive=True,
                                                            type="AzureBlobFSReadSettings",
                                                        ),
                                                        type="GetMetadata",
                                                    ),
                                                    datafactory.ForEachActivityArgs(
                                                        activities=[
                                                            datafactory.CopyActivityArgs(
                                                                enable_staging=False,
                                                                inputs=[
                                                                    datafactory.DatasetReferenceArgs(
                                                                        parameters={
                                                                            "ZipFileName": {
                                                                                "type": "Expression",
                                                                                "value": "@item().name",
                                                                            },
                                                                        },
                                                                        reference_name="ds_raw_zip",
                                                                        type="DatasetReference",
                                                                    )],
                                                                name="ExtractZip",
                                                                outputs=[
                                                                    datafactory.DatasetReferenceArgs(
                                                                        reference_name="ds_extracted_zip",
                                                                        type="DatasetReference",
                                                                    )],
                                                                policy=datafactory.ActivityPolicyArgs(
                                                                    retry=0,
                                                                    retry_interval_in_seconds=30,
                                                                    secure_input=False,
                                                                    secure_output=False,
                                                                    timeout="0.12:00:00",
                                                                ),
                                                                sink=datafactory.BinarySinkArgs(
                                                                    store_settings=datafactory.AzureBlobFSWriteSettingsArgs(
                                                                        type="AzureBlobFSWriteSettings",
                                                                    ),
                                                                    type="BinarySink",
                                                                ),
                                                                source=datafactory.BinarySourceArgs(
                                                                    format_settings=datafactory.BinaryReadSettingsArgs(
                                                                        compression_properties=datafactory.ZipDeflateReadSettingsArgs(
                                                                            preserve_zip_file_name_as_folder=False,
                                                                            type="ZipDeflateReadSettings",
                                                                        ),
                                                                        type="BinaryReadSettings",
                                                                    ),
                                                                    store_settings=datafactory.AzureBlobFSReadSettingsArgs(
                                                                        recursive=True,
                                                                        type="AzureBlobFSReadSettings",
                                                                    ),
                                                                    type="BinarySource",
                                                                ),
                                                                type="Copy",
                                                            )],
                                                        depends_on=[
                                                            datafactory.ActivityDependencyArgs(
                                                                activity="CountZipFile",
                                                                dependency_conditions=["Succeeded"],
                                                            )],
                                                        is_sequential=True,
                                                        items=datafactory.ExpressionArgs(
                                                            type="Expression",
                                                            value="@activity('CountZipFile').output.childItems",
                                                        ),
                                                        name="ForEachZipFile",
                                                        type="ForEach",
                                                    ),
                                                ],
                                                factory_name="skyuk-dap-hr-ps-prod-adf",
                                                pipeline_name="pl_zip_extraction",
                                                resource_group_name=resource_group.name)

    pl_data_load_csv_sf = datafactory.Pipeline("pl_data_load_csv_sf",
                                               activities=[
                                                   datafactory.GetMetadataActivityArgs(
                                                       dataset=datafactory.DatasetReferenceArgs(
                                                           reference_name="ds_metadata_csv",
                                                           type="DatasetReference",
                                                       ),
                                                       depends_on=[datafactory.ActivityDependencyArgs(
                                                           activity="CheckLookupFileLoadNeeded",
                                                           dependency_conditions=["Succeeded"],
                                                       )],
                                                       field_list=["childItems"],
                                                       format_settings=datafactory.DelimitedTextReadSettingsArgs(
                                                           type="DelimitedTextReadSettings",
                                                       ),
                                                       name="Get Metadata from csv blob",
                                                       policy=datafactory.ActivityPolicyArgs(
                                                           retry=0,
                                                           retry_interval_in_seconds=30,
                                                           secure_input=False,
                                                           secure_output=False,
                                                           timeout="0.12:00:00",
                                                       ),
                                                       store_settings=datafactory.AzureBlobFSReadSettingsArgs(
                                                           enable_partition_discovery=False,
                                                           recursive=True,
                                                           type="AzureBlobFSReadSettings",
                                                       ),
                                                       type="GetMetadata",
                                                   ),
                                                   datafactory.ForEachActivityArgs(
                                                       activities=[
                                                           datafactory.CopyActivityArgs(
                                                               depends_on=[datafactory.ActivityDependencyArgs(
                                                                   activity="LookupTargetTableName",
                                                                   dependency_conditions=["Succeeded"],
                                                               )],
                                                               enable_skip_incompatible_row=False,
                                                               enable_staging=False,
                                                               inputs=[datafactory.DatasetReferenceArgs(
                                                                   parameters={
                                                                       "filename": {
                                                                           "type": "Expression",
                                                                           "value": "@item().name",
                                                                       },
                                                                   },
                                                                   reference_name="ds_csv_data",
                                                                   type="DatasetReference",
                                                               )],
                                                               log_settings=datafactory.LogSettingsArgs(
                                                                   copy_activity_log_settings=datafactory.CopyActivityLogSettingsArgs(
                                                                       enable_reliable_logging=False,
                                                                       log_level="Warning",
                                                                   ),
                                                                   enable_copy_activity_log=True,
                                                                   log_location_settings=datafactory.LogLocationSettingsArgs(
                                                                       linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                                           reference_name="ls_adls",
                                                                           type="LinkedServiceReference",
                                                                       ),
                                                                       path="salesforce/config",
                                                                   ),
                                                               ),
                                                               name="LoadTableWithCSVData",
                                                               outputs=[datafactory.DatasetReferenceArgs(
                                                                   parameters={
                                                                       "tablename": {
                                                                           "type": "Expression",
                                                                           "value": "@activity('LookupTargetTableName').output.firstRow.TargetTableName",
                                                                       },
                                                                   },
                                                                   reference_name="ds_database_table_lookup",
                                                                   type="DatasetReference",
                                                               )],
                                                               policy=datafactory.ActivityPolicyArgs(
                                                                   retry=0,
                                                                   retry_interval_in_seconds=30,
                                                                   secure_input=False,
                                                                   secure_output=False,
                                                                   timeout="0.12:00:00",
                                                               ),
                                                               sink=datafactory.AzureSqlSinkArgs(
                                                                   disable_metrics_collection=False,
                                                                   pre_copy_script={
                                                                       "type": "Expression",
                                                                       "value": "TRUNCATE TABLE @{activity('LookupTargetTableName').output.firstRow.TargetTableName}",
                                                                   },
                                                                   sql_writer_use_table_lock=False,
                                                                   type="AzureSqlSink",
                                                                   write_behavior="insert",
                                                               ),
                                                               source=datafactory.DelimitedTextSourceArgs(
                                                                   format_settings=datafactory.DelimitedTextReadSettingsArgs(
                                                                       type="DelimitedTextReadSettings",
                                                                   ),
                                                                   store_settings=datafactory.AzureBlobFSReadSettingsArgs(
                                                                       enable_partition_discovery=False,
                                                                       recursive=True,
                                                                       type="AzureBlobFSReadSettings",
                                                                   ),
                                                                   type="DelimitedTextSource",
                                                               ),
                                                               translator={
                                                                   "type": "TabularTranslator",
                                                                   "typeConversion": True,
                                                                   "typeConversionSettings": {
                                                                       "allowDataTruncation": False,
                                                                       "treatBooleanAsNumber": False,
                                                                   },
                                                               },
                                                               type="Copy",
                                                               validate_data_consistency=False,
                                                           ),
                                                           datafactory.IfConditionActivityArgs(
                                                               depends_on=[datafactory.ActivityDependencyArgs(
                                                                   activity="LoadTableWithCSVData",
                                                                   dependency_conditions=["Succeeded"],
                                                               )],
                                                               expression=datafactory.ExpressionArgs(
                                                                   type="Expression",
                                                                   value="@equals(activity('LoadTableWithCSVData').output.rowsCopied,activity('LoadTableWithCSVData').output.rowsRead)",
                                                               ),
                                                               if_true_activities=[datafactory.DeleteActivityArgs(
                                                                   dataset=datafactory.DatasetReferenceArgs(
                                                                       parameters={
                                                                           "filename": {
                                                                               "type": "Expression",
                                                                               "value": "@item().name",
                                                                           },
                                                                       },
                                                                       reference_name="ds_csv_data",
                                                                       type="DatasetReference",
                                                                   ),
                                                                   enable_logging=True,
                                                                   log_storage_settings=datafactory.LogStorageSettingsArgs(
                                                                       linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                                           reference_name="ls_adls",
                                                                           type="LinkedServiceReference",
                                                                       ),
                                                                       path="salesforce/config/logging/filedeletion",
                                                                   ),
                                                                   name="DeleteProcessedCSV",
                                                                   policy=datafactory.ActivityPolicyArgs(
                                                                       retry=0,
                                                                       retry_interval_in_seconds=30,
                                                                       secure_input=False,
                                                                       secure_output=False,
                                                                       timeout="0.12:00:00",
                                                                   ),
                                                                   store_settings=datafactory.AzureBlobFSReadSettingsArgs(
                                                                       enable_partition_discovery=False,
                                                                       recursive=True,
                                                                       type="AzureBlobFSReadSettings",
                                                                   ),
                                                                   type="Delete",
                                                               )],
                                                               name="CheckFileLoadSuccessful",
                                                               type="IfCondition",
                                                           ),
                                                           datafactory.LookupActivityArgs(
                                                               dataset=datafactory.DatasetReferenceArgs(
                                                                   parameters={
                                                                       "tablename": "tb_sf_filelookup",
                                                                   },
                                                                   reference_name="ds_database_table_lookup",
                                                                   type="DatasetReference",
                                                               ),
                                                               first_row_only=True,
                                                               name="LookupTargetTableName",
                                                               policy=datafactory.ActivityPolicyArgs(
                                                                   retry=0,
                                                                   retry_interval_in_seconds=30,
                                                                   secure_input=False,
                                                                   secure_output=False,
                                                                   timeout="0.12:00:00",
                                                               ),
                                                               source=datafactory.AzureSqlSourceArgs(
                                                                   partition_option="None",
                                                                   query_timeout="00:01:00",
                                                                   sql_reader_query={
                                                                       "type": "Expression",
                                                                       "value": "SELECT TARGETTABLENAME FROM tb_sf_filelookup WHERE FILENAME = '@{item().name}'",
                                                                   },
                                                                   type="AzureSqlSource",
                                                               ),
                                                               type="Lookup",
                                                           ),
                                                           datafactory.SqlServerStoredProcedureActivityArgs(
                                                               depends_on=[datafactory.ActivityDependencyArgs(
                                                                   activity="LoadTableWithCSVData",
                                                                   dependency_conditions=["Failed"],
                                                               )],
                                                               linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                                   reference_name="ls_sqldb",
                                                                   type="LinkedServiceReference",
                                                               ),
                                                               name="Audit Log_fail",
                                                               policy=datafactory.ActivityPolicyArgs(
                                                                   retry=0,
                                                                   retry_interval_in_seconds=30,
                                                                   secure_input=False,
                                                                   secure_output=False,
                                                                   timeout="0.12:00:00",
                                                               ),
                                                               stored_procedure_name="[dbo].[sp_copy_activity_audit_log]",
                                                               stored_procedure_parameters={
                                                                   "error": {
                                                                       "type": "String",
                                                                       "value": {
                                                                           "type": "Expression",
                                                                           "value": "@activity('LoadTableWithCSVData').output.errors[0].Message",
                                                                       },
                                                                   },
                                                                   "filename": {
                                                                       "type": "String",
                                                                       "value": {
                                                                           "type": "Expression",
                                                                           "value": "@item().name",
                                                                       },
                                                                   },
                                                                   "logFilePath": {
                                                                       "type": "String",
                                                                       "value": {
                                                                           "type": "Expression",
                                                                           "value": "@activity('LoadTableWithCSVData').output.logFilePath",
                                                                       },
                                                                   },
                                                                   "rowsCopied": {
                                                                       "type": "Int64",
                                                                       "value": {
                                                                           "type": "Expression",
                                                                           "value": "@activity('LoadTableWithCSVData').output.rowsCopied",
                                                                       },
                                                                   },
                                                                   "rowsRead": {
                                                                       "type": "Int64",
                                                                       "value": {
                                                                           "type": "Expression",
                                                                           "value": "@activity('LoadTableWithCSVData').output.rowsRead",
                                                                       },
                                                                   },
                                                                   "rowsSkipped": {
                                                                       "type": "Decimal",
                                                                   },
                                                                   "runId": {
                                                                       "type": "String",
                                                                       "value": {
                                                                           "type": "Expression",
                                                                           "value": "@pipeline().RunId",
                                                                       },
                                                                   },
                                                                   "starttime": {
                                                                       "type": "DateTime",
                                                                       "value": {
                                                                           "type": "Expression",
                                                                           "value": "@activity('LoadTableWithCSVData').output.executionDetails[0].start",
                                                                       },
                                                                   },
                                                                   "status": {
                                                                       "type": "String",
                                                                       "value": {
                                                                           "type": "Expression",
                                                                           "value": "@activity('LoadTableWithCSVData').output.executionDetails[0].status",
                                                                       },
                                                                   },
                                                               },
                                                               type="SqlServerStoredProcedure",
                                                           ),
                                                           datafactory.SqlServerStoredProcedureActivityArgs(
                                                               depends_on=[datafactory.ActivityDependencyArgs(
                                                                   activity="CheckFileLoadSuccessful",
                                                                   dependency_conditions=["Succeeded"],
                                                               )],
                                                               linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                                   reference_name="ls_sqldb",
                                                                   type="LinkedServiceReference",
                                                               ),
                                                               name="Audit Log_success",
                                                               policy=datafactory.ActivityPolicyArgs(
                                                                   retry=0,
                                                                   retry_interval_in_seconds=30,
                                                                   secure_input=False,
                                                                   secure_output=False,
                                                                   timeout="0.12:00:00",
                                                               ),
                                                               stored_procedure_name="[dbo].[sp_copy_activity_audit_log]",
                                                               stored_procedure_parameters={
                                                                   "error": {
                                                                       "type": "String",
                                                                   },
                                                                   "filename": {
                                                                       "type": "String",
                                                                       "value": {
                                                                           "type": "Expression",
                                                                           "value": "@item().name",
                                                                       },
                                                                   },
                                                                   "logFilePath": {
                                                                       "type": "String",
                                                                       "value": {
                                                                           "type": "Expression",
                                                                           "value": "@activity('LoadTableWithCSVData').output.logFilePath",
                                                                       },
                                                                   },
                                                                   "rowsCopied": {
                                                                       "type": "Int64",
                                                                       "value": {
                                                                           "type": "Expression",
                                                                           "value": "@activity('LoadTableWithCSVData').output.rowsCopied",
                                                                       },
                                                                   },
                                                                   "rowsRead": {
                                                                       "type": "Int64",
                                                                       "value": {
                                                                           "type": "Expression",
                                                                           "value": "@activity('LoadTableWithCSVData').output.rowsRead",
                                                                       },
                                                                   },
                                                                   "rowsSkipped": {
                                                                       "type": "Decimal",
                                                                   },
                                                                   "runId": {
                                                                       "type": "String",
                                                                       "value": {
                                                                           "type": "Expression",
                                                                           "value": "@pipeline().RunId",
                                                                       },
                                                                   },
                                                                   "starttime": {
                                                                       "type": "DateTime",
                                                                       "value": {
                                                                           "type": "Expression",
                                                                           "value": "@activity('LoadTableWithCSVData').output.executionDetails[0].start",
                                                                       },
                                                                   },
                                                                   "status": {
                                                                       "type": "String",
                                                                       "value": {
                                                                           "type": "Expression",
                                                                           "value": "@activity('LoadTableWithCSVData').output.executionDetails[0].status",
                                                                       },
                                                                   },
                                                               },
                                                               type="SqlServerStoredProcedure",
                                                           ),
                                                       ],
                                                       depends_on=[datafactory.ActivityDependencyArgs(
                                                           activity="Get Metadata from csv blob",
                                                           dependency_conditions=["Completed"],
                                                       )],
                                                       is_sequential=True,
                                                       items=datafactory.ExpressionArgs(
                                                           type="Expression",
                                                           value="@activity('Get Metadata from csv blob').output.childItems",
                                                       ),
                                                       name="ForEachCSV",
                                                       type="ForEach",
                                                   ),
                                                   datafactory.GetMetadataActivityArgs(
                                                       dataset=datafactory.DatasetReferenceArgs(
                                                           parameters={
                                                               "filename": "FileLookup.csv",
                                                           },
                                                           reference_name="ds_config_lookup",
                                                           type="DatasetReference",
                                                       ),
                                                       depends_on=[datafactory.ActivityDependencyArgs(
                                                           activity="CSVExtractionFromZip",
                                                           dependency_conditions=["Succeeded"],
                                                       )],
                                                       field_list=["lastModified"],
                                                       format_settings=datafactory.DelimitedTextReadSettingsArgs(
                                                           type="DelimitedTextReadSettings",
                                                       ),
                                                       name="GetLookupFileLastModDate",
                                                       policy=datafactory.ActivityPolicyArgs(
                                                           retry=0,
                                                           retry_interval_in_seconds=30,
                                                           secure_input=False,
                                                           secure_output=False,
                                                           timeout="0.12:00:00",
                                                       ),
                                                       store_settings=datafactory.AzureBlobFSReadSettingsArgs(
                                                           enable_partition_discovery=False,
                                                           recursive=True,
                                                           type="AzureBlobFSReadSettings",
                                                       ),
                                                       type="GetMetadata",
                                                   ),
                                                   datafactory.IfConditionActivityArgs(
                                                       depends_on=[datafactory.ActivityDependencyArgs(
                                                           activity="GetLookupFileLastModDate",
                                                           dependency_conditions=["Succeeded"],
                                                       )],
                                                       expression=datafactory.ExpressionArgs(
                                                           type="Expression",
                                                           value="@equals(greater(activity('GetLookupFileLastModDate').output.lastModified,addHours(utcNow(),-24)),true)",
                                                       ),
                                                       if_true_activities=[datafactory.CopyActivityArgs(
                                                           enable_staging=False,
                                                           inputs=[datafactory.DatasetReferenceArgs(
                                                               parameters={
                                                                   "filename": "FileLookup.csv",
                                                               },
                                                               reference_name="ds_config_lookup",
                                                               type="DatasetReference",
                                                           )],
                                                           name="LoadLookupTableData",
                                                           outputs=[datafactory.DatasetReferenceArgs(
                                                               parameters={
                                                                   "tablename": "tb_sf_filelookup",
                                                               },
                                                               reference_name="ds_database_table_lookup",
                                                               type="DatasetReference",
                                                           )],
                                                           policy=datafactory.ActivityPolicyArgs(
                                                               retry=0,
                                                               retry_interval_in_seconds=30,
                                                               secure_input=False,
                                                               secure_output=False,
                                                               timeout="0.12:00:00",
                                                           ),
                                                           sink=datafactory.AzureSqlSinkArgs(
                                                               disable_metrics_collection=False,
                                                               pre_copy_script="TRUNCATE TABLE tb_sf_filelookup",
                                                               sql_writer_use_table_lock=False,
                                                               type="AzureSqlSink",
                                                               write_behavior="insert",
                                                           ),
                                                           source=datafactory.DelimitedTextSourceArgs(
                                                               format_settings=datafactory.DelimitedTextReadSettingsArgs(
                                                                   type="DelimitedTextReadSettings",
                                                               ),
                                                               store_settings=datafactory.AzureBlobFSReadSettingsArgs(
                                                                   enable_partition_discovery=False,
                                                                   recursive=False,
                                                                   type="AzureBlobFSReadSettings",
                                                               ),
                                                               type="DelimitedTextSource",
                                                           ),
                                                           translator={
                                                               "type": "TabularTranslator",
                                                               "typeConversion": True,
                                                               "typeConversionSettings": {
                                                                   "allowDataTruncation": True,
                                                                   "treatBooleanAsNumber": False,
                                                               },
                                                           },
                                                           type="Copy",
                                                       )],
                                                       name="CheckLookupFileLoadNeeded",
                                                       type="IfCondition",
                                                   ),
                                                   datafactory.CopyActivityArgs(
                                                       enable_staging=False,
                                                       inputs=[datafactory.DatasetReferenceArgs(
                                                           reference_name="ds_csv_zip",
                                                           type="DatasetReference",
                                                       )],
                                                       name="CSVExtractionFromZip",
                                                       outputs=[datafactory.DatasetReferenceArgs(
                                                           reference_name="ds_extracted_csv",
                                                           type="DatasetReference",
                                                       )],
                                                       policy=datafactory.ActivityPolicyArgs(
                                                           retry=0,
                                                           retry_interval_in_seconds=30,
                                                           secure_input=False,
                                                           secure_output=False,
                                                           timeout="0.12:00:00",
                                                       ),
                                                       sink=datafactory.BinarySinkArgs(
                                                           store_settings=datafactory.AzureBlobFSWriteSettingsArgs(
                                                               type="AzureBlobFSWriteSettings",
                                                           ),
                                                           type="BinarySink",
                                                       ),
                                                       source=datafactory.BinarySourceArgs(
                                                           format_settings=datafactory.BinaryReadSettingsArgs(
                                                               compression_properties=datafactory.ZipDeflateReadSettingsArgs(
                                                                   preserve_zip_file_name_as_folder=False,
                                                                   type="ZipDeflateReadSettings",
                                                               ),
                                                               type="BinaryReadSettings",
                                                           ),
                                                           store_settings=datafactory.AzureBlobFSReadSettingsArgs(
                                                               recursive=True,
                                                               type="AzureBlobFSReadSettings",
                                                           ),
                                                           type="BinarySource",
                                                       ),
                                                       type="Copy",
                                                   ),
                                                   datafactory.DeleteActivityArgs(
                                                       dataset=datafactory.DatasetReferenceArgs(
                                                           reference_name="ds_csv_zip",
                                                           type="DatasetReference",
                                                       ),
                                                       depends_on=[datafactory.ActivityDependencyArgs(
                                                           activity="ForEachCSV",
                                                           dependency_conditions=["Succeeded"],
                                                       )],
                                                       enable_logging=True,
                                                       log_storage_settings=datafactory.LogStorageSettingsArgs(
                                                           linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                               reference_name="ls_adls",
                                                               type="LinkedServiceReference",
                                                           ),
                                                           path="taleo/salesforce/logging/filedeletion",
                                                       ),
                                                       name="DeleteZipFiles",
                                                       policy=datafactory.ActivityPolicyArgs(
                                                           retry=0,
                                                           retry_interval_in_seconds=30,
                                                           secure_input=False,
                                                           secure_output=False,
                                                           timeout="0.12:00:00",
                                                       ),
                                                       store_settings=datafactory.AzureBlobFSReadSettingsArgs(
                                                           enable_partition_discovery=False,
                                                           recursive=True,
                                                           type="AzureBlobFSReadSettings",
                                                       ),
                                                       type="Delete",
                                                   ),
                                               ],
                                               factory_name="skyuk-dap-hr-sf-prod-adf",
                                               pipeline_name="pl_data_load_csv",
                                               resource_group_name=resource_group.name)

    pl_data_preparation_url_sf = datafactory.Pipeline("pl_data_preparation_url_sf",
                                                      activities=[
                                                          datafactory.CustomActivityArgs(
                                                              command="python url_prep_script_sf.py",
                                                              folder_path="config",
                                                              linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                                  reference_name="ls_batch_service",
                                                                  type="LinkedServiceReference",
                                                              ),
                                                              name="prepare URLs",
                                                              policy=datafactory.ActivityPolicyArgs(
                                                                  retry=0,
                                                                  retry_interval_in_seconds=30,
                                                                  secure_input=False,
                                                                  secure_output=False,
                                                                  timeout="0.12:00:00",
                                                              ),
                                                              resource_linked_service=datafactory.LinkedServiceReferenceArgs(
                                                                  reference_name="ls_prodsaconfig",
                                                                  type="LinkedServiceReference",
                                                              ),
                                                              type="Custom",
                                                          ),
                                                          datafactory.CopyActivityArgs(
                                                              depends_on=[
                                                                  datafactory.ActivityDependencyArgs(
                                                                      activity="prepare URLs",
                                                                      dependency_conditions=["Succeeded"],
                                                                  )],
                                                              enable_staging=False,
                                                              inputs=[
                                                                  datafactory.DatasetReferenceArgs(
                                                                      reference_name="ds_prodsaconfig",
                                                                      type="DatasetReference",
                                                                  )],
                                                              name="Load URLs",
                                                              outputs=[
                                                                  datafactory.DatasetReferenceArgs(
                                                                      reference_name="ds_prodsatarget",
                                                                      type="DatasetReference",
                                                                  )],
                                                              policy=datafactory.ActivityPolicyArgs(
                                                                  retry=0,
                                                                  retry_interval_in_seconds=30,
                                                                  secure_input=False,
                                                                  secure_output=False,
                                                                  timeout="0.12:00:00",
                                                              ),
                                                              sink=datafactory.AzureSqlSinkArgs(
                                                                  sql_writer_use_table_lock=False,
                                                                  type="AzureSqlSink",
                                                                  write_behavior="insert",
                                                              ),
                                                              source=datafactory.DelimitedTextSourceArgs(
                                                                  format_settings=datafactory.DelimitedTextReadSettingsArgs(
                                                                      type="DelimitedTextReadSettings",
                                                                  ),
                                                                  store_settings=datafactory.AzureBlobStorageReadSettingsArgs(
                                                                      enable_partition_discovery=False,
                                                                      recursive=True,
                                                                      type="AzureBlobStorageReadSettings",
                                                                  ),
                                                                  type="DelimitedTextSource",
                                                              ),
                                                              translator={
                                                                  "type": "TabularTranslator",
                                                                  "typeConversion": True,
                                                                  "typeConversionSettings": {
                                                                      "allowDataTruncation": True,
                                                                      "treatBooleanAsNumber": False,
                                                                  },
                                                              },
                                                              type="Copy",
                                                          ),
                                                          datafactory.DeleteActivityArgs(
                                                              dataset=datafactory.DatasetReferenceArgs(
                                                                  reference_name="ds_prodsaconfig",
                                                                  type="DatasetReference",
                                                              ),
                                                              depends_on=[
                                                                  datafactory.ActivityDependencyArgs(
                                                                      activity="Load URLs",
                                                                      dependency_conditions=["Succeeded"],
                                                                  )],
                                                              enable_logging=True,
                                                              log_storage_settings=datafactory.LogStorageSettingsArgs(
                                                                  linked_service_name=datafactory.LinkedServiceReferenceArgs(
                                                                      reference_name="ls_prodsaconfig",
                                                                      type="LinkedServiceReference",
                                                                  ),
                                                                  path="config",
                                                              ),
                                                              name="Delete CSV",
                                                              policy=datafactory.ActivityPolicyArgs(
                                                                  retry=0,
                                                                  retry_interval_in_seconds=30,
                                                                  secure_input=False,
                                                                  secure_output=False,
                                                                  timeout="0.12:00:00",
                                                              ),
                                                              store_settings=datafactory.AzureBlobStorageReadSettingsArgs(
                                                                  enable_partition_discovery=False,
                                                                  recursive=True,
                                                                  type="AzureBlobStorageReadSettings",
                                                              ),
                                                              type="Delete",
                                                          ),
                                                      ],
                                                      factory_name="skyuk-dap-hr-sf-prod-adf",
                                                      pipeline_name="pl_data_preparation_url",
                                                      resource_group_name=resource_group.name)

    pl_zip_extraction_sf = datafactory.Pipeline("pl_zip_extraction_sf",
                                                activities=[
                                                    datafactory.GetMetadataActivityArgs(
                                                        dataset=datafactory.DatasetReferenceArgs(
                                                            reference_name="ds_attachment_zip",
                                                            type="DatasetReference",
                                                        ),
                                                        field_list=["childItems"],
                                                        format_settings=datafactory.BinaryReadSettingsArgs(
                                                            type="BinaryReadSettings",
                                                        ),
                                                        name="CountZipFile",
                                                        policy=datafactory.ActivityPolicyArgs(
                                                            retry=0,
                                                            retry_interval_in_seconds=30,
                                                            secure_input=False,
                                                            secure_output=False,
                                                            timeout="0.12:00:00",
                                                        ),
                                                        store_settings=datafactory.AzureBlobFSReadSettingsArgs(
                                                            enable_partition_discovery=False,
                                                            recursive=True,
                                                            type="AzureBlobFSReadSettings",
                                                        ),
                                                        type="GetMetadata",
                                                    ),
                                                    datafactory.ForEachActivityArgs(
                                                        activities=[
                                                            datafactory.CopyActivityArgs(
                                                                enable_staging=False,
                                                                inputs=[
                                                                    datafactory.DatasetReferenceArgs(
                                                                        parameters={
                                                                            "ZipFileName": {
                                                                                "type": "Expression",
                                                                                "value": "@item().name",
                                                                            },
                                                                        },
                                                                        reference_name="ds_raw_zip",
                                                                        type="DatasetReference",
                                                                    )],
                                                                name="ExtractZip",
                                                                outputs=[
                                                                    datafactory.DatasetReferenceArgs(
                                                                        reference_name="ds_extracted_zip",
                                                                        type="DatasetReference",
                                                                    )],
                                                                policy=datafactory.ActivityPolicyArgs(
                                                                    retry=0,
                                                                    retry_interval_in_seconds=30,
                                                                    secure_input=False,
                                                                    secure_output=False,
                                                                    timeout="0.12:00:00",
                                                                ),
                                                                sink=datafactory.BinarySinkArgs(
                                                                    store_settings=datafactory.AzureBlobFSWriteSettingsArgs(
                                                                        type="AzureBlobFSWriteSettings",
                                                                    ),
                                                                    type="BinarySink",
                                                                ),
                                                                source=datafactory.BinarySourceArgs(
                                                                    format_settings=datafactory.BinaryReadSettingsArgs(
                                                                        compression_properties=datafactory.ZipDeflateReadSettingsArgs(
                                                                            preserve_zip_file_name_as_folder=False,
                                                                            type="ZipDeflateReadSettings",
                                                                        ),
                                                                        type="BinaryReadSettings",
                                                                    ),
                                                                    store_settings=datafactory.AzureBlobFSReadSettingsArgs(
                                                                        recursive=True,
                                                                        type="AzureBlobFSReadSettings",
                                                                    ),
                                                                    type="BinarySource",
                                                                ),
                                                                type="Copy",
                                                            )],
                                                        depends_on=[
                                                            datafactory.ActivityDependencyArgs(
                                                                activity="CountZipFile",
                                                                dependency_conditions=["Succeeded"],
                                                            )],
                                                        is_sequential=True,
                                                        items=datafactory.ExpressionArgs(
                                                            type="Expression",
                                                            value="@activity('CountZipFile').output.childItems",
                                                        ),
                                                        name="ForEachZipFile",
                                                        type="ForEach",
                                                    ),
                                                ],
                                                factory_name="skyuk-dap-hr-sf-prod-adf",
                                                pipeline_name="pl_zip_extraction",
                                                resource_group_name=resource_group.name)

    asp_skyukdaphrpsprodresgroup = web.AppServicePlan("ASP-skyukdaphrpsprodresgroup",
                                                      hyper_v=False,
                                                      is_spot=False,
                                                      is_xenon=False,
                                                      kind="elastic",
                                                      location="UK South",
                                                      maximum_elastic_worker_count=20,
                                                      name="ASP-skyukdaphrpsprodresgroup",
                                                      per_site_scaling=False,
                                                      reserved=True,
                                                      resource_group_name=resource_group.name,
                                                      sku=web.SkuDescriptionArgs(
                                                          capacity=1,
                                                          family="EP",
                                                          name="EP1",
                                                          size="EP1",
                                                          tier="ElasticPremium",
                                                      ),
                                                      target_worker_count=0,
                                                      target_worker_size_id=0)

    asp_skyukdaphrsfprodresgroup = web.AppServicePlan("ASP-skyukdaphrsfprodresgroup",
                                                      hyper_v=False,
                                                      is_spot=False,
                                                      is_xenon=False,
                                                      kind="elastic",
                                                      location="UK South",
                                                      maximum_elastic_worker_count=20,
                                                      name="ASP-skyukdaphrsfprodresgroup",
                                                      per_site_scaling=False,
                                                      reserved=True,
                                                      resource_group_name=resource_group.name,
                                                      sku=web.SkuDescriptionArgs(
                                                          capacity=1,
                                                          family="EP",
                                                          name="EP1",
                                                          size="EP1",
                                                          tier="ElasticPremium",
                                                      ),
                                                      target_worker_count=0,
                                                      target_worker_size_id=0)

    get_blob_object_ps = web.WebApp("get-blob-object-ps",
                                    client_affinity_enabled=False,
                                    client_cert_enabled=False,
                                    client_cert_mode=web.ClientCertMode.REQUIRED,
                                    container_size=1536,
                                    daily_memory_time_quota=0,
                                    enabled=True,
                                    host_name_ssl_states=[
                                        web.HostNameSslStateArgs(
                                            host_type=web.HostType.STANDARD,
                                            name="get-blob-object-ps.azurewebsites.net",
                                            ssl_state=web.SslState.DISABLED,
                                        ),
                                        web.HostNameSslStateArgs(
                                            host_type=web.HostType.REPOSITORY,
                                            name="get-blob-object-ps.scm.azurewebsites.net",
                                            ssl_state=web.SslState.DISABLED,
                                        ),
                                    ],
                                    host_names_disabled=False,
                                    https_only=True,
                                    hyper_v=False,
                                    identity=web.ManagedServiceIdentityArgs(
                                        type=web.ManagedServiceIdentityType.SYSTEM_ASSIGNED,
                                    ),
                                    is_xenon=False,
                                    key_vault_reference_identity="SystemAssigned",
                                    kind="functionapp,linux",
                                    location="UK South",
                                    name="get-blob-object-ps",
                                    redundancy_mode=web.RedundancyMode.NONE,
                                    reserved=True,
                                    resource_group_name=resource_group.name,
                                    scm_site_also_stopped=False,
                                    server_farm_id="/subscriptions/9f78709a-9b22-4058-9344-693b333eefe8/resourceGroups/skyuk-dap-hr-prod-resgroup/providers/Microsoft.Web/serverfarms/ASP-skyukdaphrpsprodresgroup",
                                    site_config=web.SiteConfigArgs(
                                        acr_use_managed_identity_creds=False,
                                        always_on=False,
                                        function_app_scale_limit=0,
                                        http20_enabled=False,
                                        linux_fx_version="Python|3.10",
                                        minimum_elastic_instance_count=1,
                                        number_of_workers=1,
                                    ),
                                    storage_account_required=False,
                                    virtual_network_subnet_id="/subscriptions/9f78709a-9b22-4058-9344-693b333eefe8/resourcegroups/skyuk-dap-hr-prod-resgroup/providers/Microsoft.Network/virtualNetworks/skyuk-dap-hr-prod-vnet/subnets/default")

    get_blob_object_sf = web.WebApp("get-blob-object-sf",
                                    client_affinity_enabled=False,
                                    client_cert_enabled=False,
                                    client_cert_mode=web.ClientCertMode.REQUIRED,
                                    container_size=1536,
                                    daily_memory_time_quota=0,
                                    enabled=True,
                                    host_name_ssl_states=[
                                        web.HostNameSslStateArgs(
                                            host_type=web.HostType.STANDARD,
                                            name="get-blob-object-sf.azurewebsites.net",
                                            ssl_state=web.SslState.DISABLED,
                                        ),
                                        web.HostNameSslStateArgs(
                                            host_type=web.HostType.REPOSITORY,
                                            name="get-blob-object-sf.scm.azurewebsites.net",
                                            ssl_state=web.SslState.DISABLED,
                                        ),
                                    ],
                                    host_names_disabled=False,
                                    https_only=True,
                                    hyper_v=False,
                                    identity=web.ManagedServiceIdentityArgs(
                                        type=web.ManagedServiceIdentityType.SYSTEM_ASSIGNED,
                                    ),
                                    is_xenon=False,
                                    key_vault_reference_identity="SystemAssigned",
                                    kind="functionapp,linux",
                                    location="UK South",
                                    name="get-blob-object-sf",
                                    redundancy_mode=web.RedundancyMode.NONE,
                                    reserved=True,
                                    resource_group_name=resource_group.name,
                                    scm_site_also_stopped=False,
                                    server_farm_id="/subscriptions/9f78709a-9b22-4058-9344-693b333eefe8/resourceGroups/skyuk-dap-hr-prod-resgroup/providers/Microsoft.Web/serverfarms/ASP-skyukdaphrsfprodresgroup",
                                    site_config=web.SiteConfigArgs(
                                        acr_use_managed_identity_creds=False,
                                        always_on=False,
                                        function_app_scale_limit=0,
                                        http20_enabled=False,
                                        linux_fx_version="Python|3.10",
                                        minimum_elastic_instance_count=1,
                                        number_of_workers=1,
                                    ),
                                    storage_account_required=False,
                                    virtual_network_subnet_id="/subscriptions/9f78709a-9b22-4058-9344-693b333eefe8/resourcegroups/skyuk-dap-hr-prod-resgroup/providers/Microsoft.Network/virtualNetworks/skyuk-dap-hr-prod-vnet/subnets/default")

    get_blob_object_ps = insights.Component("get-blob-object-ps",
                                            application_type="web",
                                            kind="web",
                                            location="uksouth",
                                            request_source="IbizaAIExtensionEnablementBlade",
                                            resource_group_name=resource_group.name,
                                            resource_name_="get-blob-object-ps")

    get_blob_object_sf = insights.Component("get-blob-object-sf",
                                            application_type="web",
                                            kind="web",
                                            location="uksouth",
                                            request_source="IbizaAIExtensionEnablementBlade",
                                            resource_group_name=resource_group.name,
                                            resource_name_="get-blob-object-sf")

    # Export the primary key of the Storage Account
    primary_key = pulumi.Output.all(resource_group.name, storage_account.name) \
        .apply(lambda args: storage.list_storage_account_keys(
        resource_group_name=args[0],
        account_name=args[1]
    )).apply(lambda accountKeys: accountKeys.keys[0].value)

    pulumi.export("primary_storage_key", primary_key)


deployResources()

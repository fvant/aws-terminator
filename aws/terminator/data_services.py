from . import DbTerminator, Terminator, get_tag_dict_from_tag_list


class DmsSubnetGroup(DbTerminator):
    @staticmethod
    def create(credentials):
        def paginate_dms_subnet_groups(client):
            return client.get_paginator('describe_replication_subnet_groups').paginate().build_full_result()['ReplicationSubnetGroups']

        return Terminator._create(credentials, DmsSubnetGroup, 'dms', paginate_dms_subnet_groups)

    @property
    def id(self):
        return self.instance['ReplicationSubnetGroupIdentifier']

    @property
    def name(self):
        return self.instance['ReplicationSubnetGroupIdentifier']

    def terminate(self):
        self.client.delete_replication_subnet_group(ReplicationSubnetGroupIdentifier=self.id)


class GlueConnection(Terminator):
    @staticmethod
    def create(credentials):
        return Terminator._create(credentials, GlueConnection, 'glue', lambda client: client.get_connections()['ConnectionList'])

    @property
    def id(self):
        return self.instance['Name']

    @property
    def name(self):
        return self.instance['Name']

    @property
    def created_time(self):
        return self.instance['CreationTime']

    def terminate(self):
        self.client.delete_connection(ConnectionName=self.name)


class Glacier(Terminator):
    @staticmethod
    def create(credentials):
        return Terminator._create(credentials, Glacier, 'glacier', lambda client: client.list_vaults()['VaultList'])

    @property
    def id(self):
        return self.instance['VaultARN']

    @property
    def name(self):
        return self.instance['VaultName']

    @property
    def created_time(self):
        return self.instance['CreationDate']

    def terminate(self):
        self.client.delete_vault(vaultName=self.name)


class RdsDbParameterGroup(DbTerminator):
    @staticmethod
    def create(credentials):
        return Terminator._create(credentials, RdsDbParameterGroup, 'rds', lambda client: client.describe_db_parameter_groups()['DBParameterGroups'])

    @property
    def id(self):
        return self.instance['DBParameterGroupArn']

    @property
    def name(self):
        return self.instance['DBParameterGroupName']

    def terminate(self):
        self.client.delete_db_parameter_group(DBParameterGroupName=self.name)


class RedshiftCluster(Terminator):
    @staticmethod
    def create(credentials):

        def get_available_clusters(client):
            # describe_clusters does not have a parameter to filter results
            # The key "ClusterCreateTime" does not exist while the cluster is being created.
            ignore_states = ('creating', 'deleting',)
            clusters = client.describe_clusters()['Clusters']
            return [cluster for cluster in clusters if cluster['ClusterStatus'] not in ignore_states]

        return Terminator._create(credentials, RedshiftCluster, 'redshift', get_available_clusters)

    @property
    def name(self):
        return get_tag_dict_from_tag_list(self.instance.get('Tags')).get('Name')

    @property
    def id(self):
        return self.instance['ClusterIdentifier']

    @property
    def created_time(self):
        return self.instance['ClusterCreateTime']

    def terminate(self):
        self.client.delete_cluster(ClusterIdentifier=self.id, SkipFinalClusterSnapshot=True)

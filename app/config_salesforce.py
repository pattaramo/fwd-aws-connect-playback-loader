import os
from database import Database
from aws_lambda_powertools import Logger

CONFIG_DB_NAME = os.environ.get('CONFIG_DB_NAME')

class ConfigSalesforce:
    def init(self, config):
        self.config = config.copy()
        self.config['db_database_name'] = CONFIG_DB_NAME
        self.database = Database(self.config)

    def get_voicecall_records(self):
        try:
            db_connection = self.database.get_connection()
            cursor = db_connection.cursor()
            cursor.execute("SELECT * FROM voicecall")
            voicecall_records = cursor.fetchall()
            return voicecall_records
        except Exception as e:
            Logger.error("Error in retrieving voicecall records: {}".format(e))
            raise e
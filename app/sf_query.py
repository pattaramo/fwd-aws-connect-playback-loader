import os, time, json, datetime
from aws_lambda_powertools import Logger
from simple_salesforce.exceptions import SalesforceExpiredSession
from config_salesforce import ConfigSalesforce

logger = Logger(service="dialer-lead-loader", child=True)

from sf_auth import SfAuth

SF_API_RETRY = int(os.environ['SF_API_RETRY'])


class SfLoader:

    def __init__(self, config):
        self.sf_auth = SfAuth()
        self.config = config

    def query(self, sql):
        result = None

        # retry sf api loop
        for i in range(1, SF_API_RETRY):
            logger.debug(f"sf_query start round {i}")

            try:
                sf = self.sf_auth.get_sf()

                # invoke SF command here
                # how to use https://github.com/simple-salesforce/simple-salesforce
                #sql = 'SELECT Id,Insured_HomePhone__c,Insured_Mobile__c,Owner_Mobile__c FROM Welcome_Call__c'
                #sql = 'SELECT name from Account'
                result = sf.query_all(sql)

                break
            except (SalesforceExpiredSession, ConnectionError) as e:
                # re-login as session expired
                logger.info(f"sf_query cache session expired")
                self.sf_auth.login()
                # raise exception if retry exceed
                if i == (SF_API_RETRY - 1): raise
            except Exception as e:
                message = f"{type(e).__name__} {str(e)}"[:100]
                logger.info(f"sf_query exception {type(e).__name__} {message}")
                # raise exception if retry exceed
                if i == (SF_API_RETRY - 1): raise

            # retry delay
            time.sleep(2 * i)

        fields = {"totalSize": result['totalSize']}
        logger.info(f"sf_query complete has {result['totalSize']} rows",
                    extra=fields)

        return result

    def getSQL(self, sfuuid, level, limit, max_retry, sf_record_id_list, sf_record_dnis_list):
        sql_result = None
        sf_object_name = None

        # Overwrite DB_NAME to 'config' database
        SFConfig = ConfigSalesforce(self.config)

        # Get SOSQL from SF_CAMPAIGN_UUID
        results = SFConfig.select_by_sfuuid(sfuuid)
        if results['data']:
            for result in results['data']:
                sql_result = result['soql_get_lead']
                sf_object_name = result['object_name']

                # Append WHERE coditions from contact_after and handling_level
                level_condition = ""
                now = datetime.datetime.now()
                date_time_str = now.strftime("%Y-%m-%dT%H:%M:%Sz")

                # Contact after condition
                more_condition = f" and (Contact_After__c <= {date_time_str} or Contact_After__c = null)"

                # Handling level condition
                if level > 0:
                    level_condition = f" and Handling_Level__c = 'Level {level}'"
                more_condition += level_condition

                # Max retry condition
                max_retry_condition = f" and (Number_of_Attempts__c < {max_retry} or Number_of_Attempts__c = null)"
                more_condition += max_retry_condition

                # not load duplicate id
                if len(sf_record_id_list) > 0:
                    for sf_record_id in sf_record_id_list:
                        more_condition += f" and Id != '{sf_record_id}'"

                # not load duplicate phone number
                dnis_fields = self.get_dnis_fields(sql_result)
                if len(dnis_fields) > 0:
                    for sf_record_dnis in sf_record_dnis_list:
                        for dnis_field in dnis_fields:
                            more_condition += f" and {dnis_field} != '{sf_record_dnis}'"

                # add condition
                sql_result += more_condition

                # Append ORDER_MODE from Campaign
                if self.orderMode == 1:
                    order_str = ' ORDER BY Status__c DESC, CreatedDate ASC'  #this wil make INPROGRESS_RETRY_x came first
                else:
                    order_str = ' ORDER BY Status__c ASC, CreatedDate ASC'  #this will make NEW came first

                sql_result += order_str
                sql_result += f' LIMIT {limit}'

        logger.info(f'SOQL_QUERY: {sql_result}')
        return sql_result, sf_object_name

    def setOrderMode(self, mode):
        self.orderMode = mode

    def get_dnis_fields(self, soql):
        dnis_fields = []
        soql_dnis_fields = soql.split(",", 4)

        dnis_field = soql_dnis_fields[1].strip()
        if not dnis_field.startswith('Format'):
            dnis_fields.append(dnis_field)
        
        dnis_field = soql_dnis_fields[2].strip()
        if not dnis_field.startswith('Format'):
            dnis_fields.append(dnis_field)
        
        dnis_field = soql_dnis_fields[3].strip()
        if not dnis_field.startswith('Format'):
            dnis_fields.append(dnis_field)

        return dnis_fields

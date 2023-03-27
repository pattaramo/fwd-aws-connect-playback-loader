import os
from datetime import datetime, timedelta
from aws_lambda_powertools import Logger, Tracer
from ssm import SsmConfig
from sf_query import SfLoader
#from playback_data import PlaybackData
from playback_detail import PlaybackDetail

tracer = Tracer()
logger = Logger(service="playback-loader")

ssm_parameter_path = os.environ['SSM_PARAMETER_PATH']
ssm_config = None

PLAYBACK_THRESHOLD = int(os.environ['PLAYBACK_THRESHOLD'])


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event=None, context=None):
    global ssm_config
    if ssm_config is None:
        ssm = SsmConfig()
        logger.info("Loading SsmConfig")
        ssm.load_config(ssm_parameter_path)
        ssm_config = ssm.get_config()
    '''if event.get("query_soql"):
        query_soql()
        logger.info("method class query_soql")
    if event.get("query_path"):
        query_path()
        logger.info("method class query_path")'''
    if event.get("insert_data"):
        insert_data()
        logger.info("method class insert_data")
    if event.get("join_table"):
        join_table()
        logger.info("method class join_table")
    
def query_soql():
    #query data
    dt = datetime.now() - timedelta(hours=1)
    logger.info(dt)
    str_dt = dt.strftime('%Y-%m-%dT%H:00:00z')
    end_dt = (dt + timedelta(hours=1) - timedelta(seconds=1)).strftime('%Y-%m-%dT%H:%M:%Sz')
    #str_dt = "2023-01-01T00:00:00z"
    #end_dt = "2023-02-09T00:00:00z"
    logger.info(str_dt)
    logger.info(end_dt)
    sql = f"SELECT vendorcallkey,id,fromphonenumber,callstartdatetime,callenddatetime,calltype,queuename FROM voicecall WHERE createddate >= {str_dt} AND createddate <= {end_dt}"
    logger.info(sql)

    sf_loader = SfLoader(ssm_config)
    try:
        data = sf_loader.query(sql)
        logger.info("Successfully queried Salesforce")
    except Exception as e:
        logger.error(f"Error querying Salesforce: {e}")
        raise
    return data

def query_path():
    #query path
    '''dt = datetime.now() - timedelta(hours=1)
    logger.info(dt)
    str_dt = dt.strftime('%Y-%m-%dT%H:00:00z')
    end_dt = (dt + timedelta(hours=1) - timedelta(seconds=1)).strftime('%Y-%m-%dT%H:%M:%Sz')
    sql_path = f"SELECT VoiceCallId, CreatedDate, Name FROM VoiceCallRecording WHERE CreatedDate >= {str_dt} AND CreatedDate <= {end_dt}"'''
    
    sql_path = f"SELECT VoiceCallId, CreatedDate, Name FROM VoiceCallRecording"
    logger.info(sql_path)

    sf_loader = SfLoader(ssm_config)
    try:
        path = sf_loader.query(sql_path)
        logger.info("Successfully queried Voice Record")
    except Exception as e:
        logger.error(f"Error querying Voice Record: {e}")
        raise
    return path


def insert_data():
    #insert detail
    logger.info("insert_detail_data")
    data = query_soql()
    records=data['records']
    logger.info(records)
    playback_detail = PlaybackDetail(ssm_config)
    for item in records:
        logger.info(item)
        playback_detail.insert(item)
    
    #insert path
    logger.info("insert_path")
    path = query_path()
    logger.info(path)
    voicepath=path['records']
    logger.info(voicepath)
    for item in voicepath:
        logger.info(item)
        playback_detail.insert_path(item)

def join_table():
    playback_detail = PlaybackDetail(ssm_config)
    playback_detail.join()
    logger.info("Table join completed")

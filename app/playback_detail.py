from aws_lambda_powertools import Logger
from database import Database
import datetime

logger = Logger(service="playback-loader", child=True)

class PlaybackDetail:

    def __init__(self, config):
        self.config = config
        self.database = Database(config)

    def insert(self, data):
        logger.debug("playback_detail: insert start")
        connection = self.database.get_connection()

        chCallStartDateTime = data['CallStartDateTime']
        # parse the date and time string into a datetime object
        parsed_datetime = datetime.datetime.strptime(chCallStartDateTime, '%Y-%m-%dT%H:%M:%S.%f%z')
        # add 7 hours to the datetime object
        new_datetime = parsed_datetime + datetime.timedelta(hours=7)
        # format the new datetime object as YYYY-MM-DD HH:mm:ss
        CallStartDateTime = new_datetime.strftime('%Y-%m-%d %H:%M:%S')
        #print(CallStartDateTime)


        chCallEndDateTime = data['CallEndDateTime']
        # parse the date and time string into a datetime object
        parsed_datetime = datetime.datetime.strptime(chCallEndDateTime, '%Y-%m-%dT%H:%M:%S.%f%z')
        # add 7 hours to the datetime object
        new_datetime = parsed_datetime + datetime.timedelta(hours=7)
        # format the new datetime object as YYYY-MM-DD HH:mm:ss
        CallEndDateTime = new_datetime.strftime('%Y-%m-%d %H:%M:%S')
        #print(CallEndDateTime)

        
        with connection.cursor() as cur:
            sql = f"INSERT INTO fwd_playback_detail (VendorCallKey,Id, FromPhoneNumber, CallStartDateTime, CallEndDateTime, CallType, QueueName) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (data['VendorCallKey'], data['Id'],
                data['FromPhoneNumber'], 
                CallStartDateTime,
                CallEndDateTime,
                data['CallType'], data['QueueName']
                )
            cur.execute(sql, val)
            connection.commit()

    
    def insert_path(self, data):
        logger.debug("callrecord_path: insert start")
        connection = self.database.get_connection()

        chCreatedDate = data['CreatedDate']
        # parse the date and time string into a datetime object
        parsed_datetime = datetime.datetime.strptime(chCreatedDate, '%Y-%m-%dT%H:%M:%S.%f%z')
        # add 7 hours to the datetime object
        new_datetime = parsed_datetime + datetime.timedelta(hours=7)
        # format the new datetime object as YYYY-MM-DD HH:mm:ss
        CreatedDate = new_datetime.strftime('%Y/%m/%d')
        #print(CreatedDate)
        #Path = "https://amazon-connect-154981430904.s3.ap-southeast-1.amazonaws.com/connect/fwd-lab/CallRecordings"
        Path = "s3://amazon-connect-154981430904/connect/fwd-lab/CallRecordings"
        file_name = f"{data['Name']}.wav"
        VoicePath =f"{Path}/{CreatedDate}/{file_name}"
        print (VoicePath)

        with connection.cursor() as cur:
            sql = f"INSERT INTO fwd_voicerecord_path (VoiceCallId, VoicePath) VALUES (%s, %s)"
            
            val = (data['VoiceCallId'],
                    VoicePath,
                    )
            print(val)
            cur.execute(sql, val)
            connection.commit()

    def join(self):
        logger.info(f"Join Table")
        connection = self.database.get_connection()
        with connection.cursor() as cur:
            try:
                # join the fwd_playback_detail and fwd_voicerecord_path tables on the "id" column
                sql_join = ("SELECT fwd_playback_detail.id, fwd_playback_detail.vendorcallkey, fwd_playback_detail.fromphonenumber, fwd_playback_detail.callstartdatetime, fwd_playback_detail.callenddatetime, fwd_playback_detail.calltype, fwd_playback_detail.queuename, fwd_voicerecord_path.voicepath FROM fwd_playback_detail JOIN fwd_voicerecord_path ON fwd_playback_detail.id = fwd_voicerecord_path.voicecallid")
                cur.execute(sql_join)
                result = cur.fetchall()
                print(result)
                return result
            except Exception as e:
                logger.error(f"An error occurred during the join operation: {e}")
                return None
        

        

import boto3, os
from aws_lambda_powertools import Logger
from simple_salesforce import Salesforce
from ssm import SsmConfig

logger = Logger(service="playback-loader", child=True)
client = boto3.client('ssm')

sf_ssm_parameter_path = os.environ.get('SF_SSM_PARAMETER_PATH')

# global variable
sf_ssm_config = None

class SfAuth:

    def __init__(self):
        global sf_ssm_config
        # Initialize ssm_config if it doesn't yet exist
        if sf_ssm_config is None:
            ssm = SsmConfig()
            logger.debug("Loading SsmConfig")
            ssm.load_config(sf_ssm_parameter_path)
            sf_ssm_config = ssm

        config = sf_ssm_config.get_config()
        if len(config['cache_sf_instance']) <= 1:
            self.login()
        else:
            self.sf = Salesforce(instance=config['cache_sf_instance'],
                                 session_id=config['cache_session_id'])

    def get_sf(self):
        return self.sf

    def login(self):
        logger.debug(f"SfAuth login start")

        global sf_ssm_config
        config = sf_ssm_config.get_config()
        self.sf = Salesforce(username=config['username'],
                             consumer_key=config['consumer_key'],
                             privatekey=config['private_key'],
                             domain=config['domain']) 

        # save session to ssm to prevent login multiple time over the day
        sf_ssm_config.update_parameter(
            f"{sf_ssm_parameter_path}/cache_session_id", self.sf.session_id)
        sf_ssm_config.update_parameter(
            f"{sf_ssm_parameter_path}/cache_sf_instance", self.sf.sf_instance)

        # reload configuration
        sf_ssm_config.load_config(sf_ssm_parameter_path)
        logger.debug(f"SfAuth login completed")
        return self.sf

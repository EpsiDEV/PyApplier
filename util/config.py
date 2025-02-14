import configparser

import logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class Config:
    def __init__(self, config_file="config.ini"):
        """
        Configparser wrapper for reading config.ini
        Args:
            config_file (str, optional): _description_. Defaults to "config.ini".
        """
        self.config = configparser.ConfigParser()
        self.config.read(config_file, "utf-8")
        
    def get(self, key, section='config'):
        return self.config.get(section, key)\
            .removeprefix("\"")\
            .removesuffix("\"")\
            .strip()\
            .replace("\\n", "\n")
    
if __name__ == "__main__":
    config = Config()
    print(config.get('hydroxide_path'))
    print(config.get('proton_username'))
    print(config.get('bridge_password'))
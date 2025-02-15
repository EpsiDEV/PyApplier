from openai import OpenAI

import logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class LMWriter:
    def __init__(self, config):
        """
        Generates cover letter using OpenAI's API
        """
        self.config = config
        self.client: OpenAI = OpenAI(base_url = config.get('openai_base_url', 'openai'), api_key = config.get('openai_api_key', 'openai'))
        self.models = ["CHATGPT-4O-LATEST"] 
        
    def generate_lm(self, company_info: str, user_info: str = None, first_part: str = None, save_to_file: bool = True):
        """
        Generates a cover letter using OpenAI's API
        Args:
            company_info (str): _description_
            job_info (str): _description_
            user_info (str): _description_
        """
        logger.info(f"Generating cover letter for {company_info}")
        
        if user_info is None:
            user_info = self.config.get("body", "email").replace("\\n", "\n")
        
        
        if first_part is None:
            first_part = self.config.get("lm_first_part", "openai")
        
        
        prompt = self.config.get("lm_prompt", "openai").format(COMPANY_INFO=company_info, USER_INFO=user_info, FIRST_PART=first_part)
        instructions = self.config.get("lm_system_instructions", "openai")
        
        response = self.client.chat.completions.create(
            model = self.models[0].lower(),
            messages=[
                {
                    "role": "system",
                    "content": instructions,
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens = 1000,
            stream = False
        )
        
        logger.info(f"Generated cover letter for {company_info}")
        
        output = first_part + "\n\n" + response.choices[0].message.content.strip()
        
        if save_to_file:
            logger.info(f"Saving cover letter for {company_info} to file LM.txt")
            with open("LM.txt", "w", encoding="utf-8") as f:
                f.write(output)
        
        return output
    

if __name__ == "__main__":
    from config import Config
    config = Config()
    lm_writer = LMWriter(config)
    print(lm_writer.generate_lm(company_info="Google"))
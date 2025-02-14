import re
import requests
from openai import OpenAI
from bs4 import BeautifulSoup
from googlesearch import search
from util.config import Config

import logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class Scraper:
    def __init__(self, config: Config, num_results: int = 150, max_emails: int = 50, use_ai: bool = False):
        """
        Initialize the Scraper with search query and desired number of results.
        """
        self.query = config.get('google_query', 'scraper')
        self.num_results = num_results
        self.emails = set()
        self.max_emails = max_emails
        self.blacklist = config.get('email_blacklist', 'scraper').split(' ')
        
        if use_ai:
            self.openai = OpenAI(base_url=config.get('openai_base_url', 'openai'), api_key = config.get('openai_api_key', 'openai'))
        else:
            self.openai = None
        
        logger.info(f"Blacklist: {self.blacklist}")

    def get_search_results(self):
        """
        Uses googlesearch with advanced option to get enriched results (title, URL, description).
        """
        logger.info(f"Searching for {self.query} with {self.num_results} results")
        results = []
        try:
            for result in search(
                self.query,
                num_results = self.num_results,
                advanced = True,
                lang = "fr",
                region = "fr"
            ):
                results.append(result)
        except Exception as e:
            logger.exception(e)
            
        return results

    def fetch_page(self, url: str):
        """
        Fetches HTML content from a URL by adding headers to avoid 403 errors.
        """
        logger.debug(f"Fetching {url}")
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "priority": "u=0, i",
            "referer": "https://www.google.com/",
            "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate", 
            "sec-fetch-site": "cross-site",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers, timeout=1)
            if response.status_code == 200:
                return response.text
            else:
                logger.error(f"Error fetching {url}: code {response.status_code}")
        except Exception as e:
            logger.error(f"Exception while fetching {url}: {e}")
        return ""

    def extract_emails(self, text: str) -> set[str]:
        """
        Extracts email addresses from text using a regular expression.
        """
        tlds = r'(?:com|net|org|fr|studio|dev|io|tech)'
        email_regex = r'\b[a-z0-9._%+-]+@[a-zA-Z0-9.-]+\.' + tlds + r'\b'
        blacklist_regex = '|'.join(self.blacklist)
        emails = set(re.findall(email_regex, text, re.IGNORECASE))
        
        filtered_emails = {email for email in emails if not re.search(blacklist_regex, email)}
        
        valid_emails = set()
        for email in filtered_emails:
            local_part, domain = email.split('@', 1)
            if local_part.islower() and local_part.replace('.', '').replace('_', '').isalnum():
                valid_emails.add(email)
        logger.debug(f"Extracted {len(valid_emails)} valid emails from text")
        return valid_emails

    def run(self):
        """
        Executes the entire process:
         - Gets Google search results
         - Extracts emails from description and HTML content of each URL
         - Stops once x emails have been collected
        """
        results = self.get_search_results()
        logger.info(f"Number of results found: {len(results)}")
        
        for res in results:
            if hasattr(res, 'description') and res.description:
                description_emails = self.extract_emails(res.description)
                if description_emails:
                    logger.info(f"Emails found in description for {res.url}: {description_emails}")
                self.emails.update(description_emails)
            
            # extract emails from the page content
            page_content = self.fetch_page(res.url)
            if page_content:
                soup = BeautifulSoup(page_content, 'html.parser')
                text = soup.get_text()
                page_emails = self.extract_emails(text)
                if page_emails:
                    logger.info(f"Emails found in {res.url}: {page_emails}")
                self.emails.update(page_emails)
            
            if len(self.emails) >= self.max_emails:
                break
            
        return list(self.emails)[:self.max_emails]
    
    @staticmethod
    def domainFromURL(url: str) -> str:
        """
        Extracts the domain name from a URL.
        """
        return url.split('/')[2]

    @staticmethod
    def domainFromEmail(email: str) -> str:
        """
        Extracts the domain name from an email address.
        """
        return email.split('@')[1]
    
    def getCompanyInfo(self, domain: str) -> dict:
        """
        Retrieves information about a company based on its domain
        """
        if not self.openai:
            logger.warning("OpenAI client not initialized - skipping company info retrieval")
            return {}

        company_info = {}
        url = f"https://www.{domain}"

        try:
            page_content = self.fetch_page(url)
            if page_content:
                soup = BeautifulSoup(page_content, 'html.parser')
                text = soup.get_text()

                try:
                    response = self.openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Summarize the following text concisely:"},
                            {"role": "user", "content": text}
                        ],
                        max_tokens=150,
                        temperature=0.7
                    )
                    company_info['summary'] = response.choices[0].message.content.strip()
                except Exception as e:
                    logger.error(f"Error summarizing text: {e}")

        except Exception as e:
            logger.exception(f"Error retrieving company info for {domain}: {e}")

        return company_info
    
if __name__ == "__main__":
    from config import Config
    config = Config()
    scraper = Scraper(config, num_results=500, max_emails=100)
    emails = scraper.run()
    
    print("\nCollected emails:")
    for email in emails:
        print(email)

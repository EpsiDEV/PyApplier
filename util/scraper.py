import re
import requests
from bs4 import BeautifulSoup
from googlesearch import search

class Scraper:
    def __init__(self, query: str, num_results: int = 50, max_emails: int = 50):
        """
        Initialize the Scraper with search query and desired number of results.
        """
        self.query = query
        self.num_results = num_results
        self.emails = set()
        self.max_emails = max_emails

    def get_search_results(self):
        """
        Uses googlesearch with advanced option to get enriched results (title, URL, description).
        """
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
            print("Error during Google search:", e)
            
        return results

    def fetch_page(self, url: str):
        """
        Fetches HTML content from a URL by adding headers to avoid 403 errors.
        """
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
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Error fetching {url}: code {response.status_code}")
        except Exception as e:
            print(f"Exception while fetching {url}: {e}")
        return ""

    def extract_emails(self, text: str) -> set[str]:
        """
        Extracts email addresses from text using a regular expression.
        """
        email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return set(re.findall(email_regex, text))

    def run(self):
        """
        Executes the entire process:
         - Gets Google search results
         - Extracts emails from description and HTML content of each URL
         - Stops once 50 emails have been collected
        """
        results = self.get_search_results()
        print(f"Number of results found: {len(results)}")
        
        for res in results:
            if hasattr(res, 'description') and res.description:
                description_emails = self.extract_emails(res.description)
                if description_emails:
                    print(f"Emails found in description for {res.url}: {description_emails}")
                self.emails.update(description_emails)
            
            # extract emails from the page content
            page_content = self.fetch_page(res.url)
            if page_content:
                soup = BeautifulSoup(page_content, 'html.parser')
                text = soup.get_text()
                page_emails = self.extract_emails(text)
                if page_emails:
                    print(f"Emails found in {res.url}: {page_emails}")
                self.emails.update(page_emails)
            
            if len(self.emails) >= self.max_emails:
                break
            
        return list(self.emails)[:self.max_emails]

if __name__ == "__main__":
    from config import Config
    config = Config()
    query = config.get('google_query', 'scraper')
    scraper = Scraper(query, num_results=200, max_emails=100)
    emails = scraper.run()
    
    print("\nCollected emails:")
    for email in emails:
        print(email)

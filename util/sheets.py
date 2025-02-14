import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

import logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class Sheets:
    def __init__(self, config):
        """
        Initialize the Logger with Google Sheets API credentials.
        """
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(config.get('google_sheets_creds_path', 'drive'), scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open(config.get('google_sheets_name', 'drive')).sheet1

    def log_email(self, company_name, url, email_address):
        """
        Logs email information to the Google Sheet.
        """
        row = [
            company_name,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            f'=HYPERLINK("{url}", "Lien")',
            email_address,
            "Non",
            "Non",
            "Non",
            "Candidature spontanée"
        ]
        
        self.sheet.append_row(row, value_input_option='USER_ENTERED')
        
        logger.info(f"Logged email for {company_name} to Google Sheet.")


if __name__ == "__main__":
    from config import Config
    config = Config()
    sheets = Sheets(config)

    company_name = "Example Company"
    url = "https://example.com"
    email_address = "contact@example.com"

    sheets.log_email(company_name, url, email_address)
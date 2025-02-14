log_to_spreadsheet =   True
ask_before_applying =  True
open_before_applying = True

from util.config import Config
from util.emailer import Emailer
from util.lmwriter import LMWriter
from util.lmformatter import LMFormatter
from util.scraper import Scraper
import os
import json

if not os.path.exists("blacklist.json"):
    blacklist = {
        "emails": [],
        "domains": []
    }
    with open("blacklist.json", "w+", encoding="utf-8") as f:
        json.dump(blacklist, f, indent = 4)
else:
    with open("blacklist.json", "r", encoding="utf-8") as f:
        blacklist = json.load(f)
    

if log_to_spreadsheet:
    from util.sheets import Sheets

if open_before_applying:
    import webbrowser

cfg = Config()
emailer = Emailer(cfg)
lm_writer = LMWriter(cfg)
lm_formatter = LMFormatter(cfg)
scraper = Scraper(cfg, num_results = 1000, max_emails = 1000, use_ai = True)
sheets = Sheets(cfg)

#----- DATA SCRAPING
companies = {}
emails = scraper.run()

for email in emails:
    domain = Scraper.domainFromEmail(email)
    if domain not in companies:
        companies[domain] = {"emails": []}
    companies[domain]["emails"].append(email)

for domain in companies.keys():
    companies[domain]["info"] = scraper.getCompanyInfo(domain)

print(companies)


past_recipients = emailer.fetch_sent_recipients()

if not companies:
    print("No companies found.")
else:
    for domain_name, company in companies.items():
        
        recipient_email = company['emails'][0]
        if recipient_email in past_recipients:
            continue # skip since we already sent
        
        if recipient_email in blacklist["emails"]:
            print(f"Skipping {recipient_email} since it is blacklisted...")
            continue
        
        if open_before_applying:
            webbrowser.open(f"https://www.{domain_name}")
        
        if ask_before_applying:
            user_input = input(f"\n\n{company['info']}\nDo you want to send an application to {recipient_email} at {domain_name}? Y/N: ")

            if user_input.lower() != 'y':
                print(f"Skipping email to {recipient_email} at {domain_name} and added to blacklist")
                blacklist["emails"].append(recipient_email)
                blacklist["domains"].append(domain_name)
                with open("blacklist.json", "w", encoding="utf-8") as f:
                    json.dump(blacklist, f, indent = 4)
                continue
        
        print(f"Generating cover letter for {domain_name}")
        
        lm_text = lm_writer.generate_lm(
            company_info = company['info'], 
            save_to_file = False
        )
        
        print(f"Generated LM: {lm_text}")
        
        # if ask_before_applying:
        #     user_input = input(f"Do you want to send this to {recipient_email} at {domain_name}? Y/N: ")
        #     if user_input.lower() != 'y':
        #         print(f"Skipping LM email to {recipient_email} at {domain_name} and added to blacklist")
        #         blacklist["emails"].append(recipient_email)
        #         blacklist["domains"].append(domain_name)
        #         with open("blacklist.json", "w", encoding="utf-8") as f:
        #             json.dump(blacklist, f, indent = 4)
        #         continue
            
        lm_formatter.format_to_pdf(
            text = lm_text,
            output_path = cfg.get('lm_output_path', 'pdf')
        )
        
        emailer.send_email(
            from_email = cfg.get('gmail_adress'),
            to_email = recipient_email,
            subject = cfg.get('subject', 'email'),
            body = cfg.get('body', 'email'),
            attachments = [cfg.get('cv_path', 'pdf'), cfg.get('lm_output_path', 'pdf')]
        )
        
        if log_to_spreadsheet:
            sheets.log_email(domain_name, f"https://www.{domain_name}", recipient_email)
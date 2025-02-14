import os
import smtplib
import imaplib
import email
import email.encoders as encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

import logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class Emailer:
    def __init__(self, config):
        self.username = config.get('gmail_adress')
        self.password = config.get('gmail_app_password')
        self.display_name = config.get('display_name')
        self.smtp_host = config.get('smtp_host')
        self.smtp_port = config.get('smtp_port')

    def send_email(self, from_email, to_email, subject, body, attachments=None):
        logger.info(f"Sending email from REDACTED to REDACTED with subject '{subject}'")
        msg = MIMEMultipart()
        
        msg['From'] = f"{self.display_name} <{from_email}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        if attachments:
            for attachment in attachments:
                if not attachment.lower().endswith('.pdf'):
                    logger.warning(f"Skipping non-PDF attachment: {attachment}")
                    continue
                with open(attachment, 'rb') as f:
                    mime_attachment = MIMEBase('application', 'pdf')
                    mime_attachment.set_payload(f.read())
                    encoders.encode_base64(mime_attachment)
                    filename = os.path.basename(attachment)
                    mime_attachment.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                    mime_attachment.add_header('Content-Transfer-Encoding', 'base64')

                    msg.attach(mime_attachment)

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as smtp:
                smtp.starttls()
                smtp.login(self.username, self.password)
                smtp.sendmail(from_email, to_email, msg.as_string())
            logger.info("Email sent successfully!")
            return True
        except Exception as e:
            raise e
        
        
    def fetch_sent_recipients(self):
        """
        Fetches every past email recipient of the current account.
        Used to avoid contacting the same adress twice.
        """
        logging.info("Fetching past email recipients...")
        try:
            mail = imaplib.IMAP4_SSL(self.smtp_host)
            mail.login(self.username, self.password)
            mail.select('"[Gmail]/Sent Mail"')

            result, data = mail.search(None, 'ALL')
            email_ids = data[0].split()

            recipients = set()
            for email_id in email_ids:
                result, msg_data = mail.fetch(email_id, '(RFC822)')
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                if msg['To']:
                    recipients.update([addr.strip() for addr in msg['To'].split(',')])

            mail.logout()
            logging.debug(f"Past recipients: {recipients}")
            return recipients

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return set()

        
        
if __name__ == "__main__":
    
    
    from config import Config
    config = Config()
    print(config.get('lm_output_path', 'pdf'))
    
    emailer = Emailer(config)
    emailer.send_email(
        from_email=f"{config.get('gmail_adress')}",
        to_email=f"{config.get('gmail_adress')}",
        subject=config.get('subject', 'email'),
        body=config.get('body', 'email'),
        attachments=[config.get('cv_path', 'pdf'), config.get('lm_output_path', 'pdf')]
    )
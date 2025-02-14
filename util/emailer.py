import os
import smtplib
import email.encoders as encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

class Emailer:
    def __init__(self, config):
        """_summary_

        Args:
            username (_type_): _description_
            password (_type_): _description_
            smtp_host (str, optional): _description_. Defaults to 'localhost'.
            smtp_port (int, optional): _description_. Defaults to 1025.
        """
        self.username = config.get('proton_username')
        self.password = config.get('bridge_password')
        self.smtp_host = config.get('smtp_host')
        self.smtp_port = config.get('smtp_port')

    def send_email(self, from_email, to_email, subject, body, attachments=None):
        print(f"Sending email from {from_email} to {to_email} with subject '{subject}'")
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        if attachments:
            for attachment in attachments:
                with open(attachment, 'rb') as f:
                    mime_attachment = MIMEBase('application', 'octet-stream')
                    mime_attachment.set_payload(f.read())
                    encoders.encode_base64(mime_attachment)
                    filename = os.path.basename(attachment)
                    mime_attachment.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                    msg.attach(mime_attachment)

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as smtp:
                smtp.login(self.username, self.password)
                smtp.sendmail(from_email, to_email, msg.as_string())
            print("Email sent successfully!")
            return True
        except Exception as e:
            raise e
        
    def __str__(self):
        return f"Emailer(username={self.username}, smtp_host={self.smtp_host}, smtp_port={self.smtp_port})"
    
    def __repr__(self):
        return self.__str__()

if __name__ == "__main__":
    from config import Config
    config = Config()
    emailer = Emailer(config)
    emailer.send_email(
        from_email=f"{config.get('proton_username')}@proton.me",
        to_email=f"{config.get('proton_username')}@proton.me",
        subject="Test Email via Hydroxide",
        body="This is an automated email sent using Hydroxide and Python."
    )
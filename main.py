from util.config import Config
from util.emailer import Emailer
from util.lmwriter import LMWriter
from util.lmformatter import LMFormatter

cfg = Config()
emailer = Emailer(cfg)
lm_writer = LMWriter(cfg)
lm_formatter = LMFormatter(cfg.get('lm_template_path', 'pdf'))

send_email = True
company_info = """
hardcoded (for now) company info
"""

receiver_email = "hardcoded (for now) receiver email"

lm_formatter.format_to_pdf(
    text = lm_writer.generate_lm(
        company_info = company_info, 
        save_to_file = False),
    output_path = cfg.get('lm_output_path', 'pdf')
)
if send_email:
    emailer.send_email(
        from_email = f"{cfg.get('proton_username')}@proton.me",
        to_email = receiver_email,
        subject = cfg.get('subject', 'email'),
        body = cfg.get('body', 'email'),
        attachments = [cfg.get('cv_path', 'pdf'), cfg.get('lm_output_path', 'pdf')]
    )
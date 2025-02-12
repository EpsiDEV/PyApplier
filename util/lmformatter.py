from datetime import datetime
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

class LMFormatter:
    def __init__(self, template_path: str):
        """
        Initializes the LMFormatter with a template PDF file.
        
        Args:
            template_path (str): Path to the template PDF file.
        """
        self.template_path = template_path

    def format_to_pdf(self, text: str, output_path: str = "output.pdf"):
        """
        Places the current date at a fixed position and inserts the provided text.
        
        Args:
            text (str): The text to be inserted into the PDF. It can contain newlines (\n).
            output_path (str): The path where the formatted PDF will be saved.
        """
        print(f"Formatting text to PDF")
        
        # Read the template PDF
        reader = PdfReader(self.template_path)
        writer = PdfWriter()

        # Create a new PDF layer for replacements
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)

        # Replace newlines (\n) with HTML <br/> tags
        text_with_breaks = text.replace("\n", "<br/>")

        styles = getSampleStyleSheet()
        style = styles["BodyText"]
        style.fontName = "Helvetica"
        style.fontSize = 10
        style.leading = 12
        style.alignment = 4  # Justified alignment

        x_offset = 10
        y_offset = 120
        margin = 70
        width = letter[0] - 2 * margin
        height = letter[1] - 2 * margin

        paragraph = Paragraph(text_with_breaks, style)
        paragraph.wrapOn(can, width, height)
        
        paragraph_y = letter[1] - margin - paragraph.height - y_offset
        paragraph.drawOn(can, margin - x_offset, paragraph_y)

        current_date = datetime.now().strftime("%d/%m/%Y")
        can.setFont("Helvetica-Bold", 10.5)
        can.drawString(490, 773, current_date) # Feel free to change position depending on your template

        can.save()

        # Merge the new PDF layer with the template
        packet.seek(0)
        new_pdf = PdfReader(packet)

        for page in reader.pages:
            page.merge_page(new_pdf.pages[0])
            writer.add_page(page)

        with open(output_path, "wb") as output_pdf:
            writer.write(output_pdf)
            
        print(f"PDF formatted successfully to {output_path}")

if __name__ == "__main__":
    from lmwriter import LMWriter
    from config import Config
    config = Config()
    formatter = LMFormatter(config.get('lm_template_path', 'pdf'))
    writer = LMWriter(config)
    text = writer.generate_lm("Google", save_to_file = False)
    formatter.format_to_pdf(text, config.get('lm_output_path', 'pdf'))
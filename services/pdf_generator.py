# services/pdf_generator.py
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from io import BytesIO

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader("templates"))

def generate_pdf(cv_data: dict) -> bytes:
    # Render the Jinja2 HTML template with data
    template = env.get_template("cv_template.html")
    html_content = template.render(cv=cv_data)

    # Convert to PDF using WeasyPrint
    html = HTML(string=html_content)
    pdf_buffer = BytesIO()
    html.write_pdf(pdf_buffer)
    pdf_buffer.seek(0)

    return pdf_buffer.getvalue()




# # services/pdf_generator.py
# import pdfkit
# from jinja2 import Environment, FileSystemLoader
# from io import BytesIO

# # Configure Jinja2 template environment
# env = Environment(loader=FileSystemLoader("templates"))

# # Configure PDFKit (you may adjust wkhtmltopdf path if needed)
# wkhtmltopdf_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
# pdfkit_config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)


# def generate_pdf(cv_data: dict) -> bytes:
#     # Render the Jinja2 HTML template
#     template = env.get_template("cv_template.html")
#     html_content = template.render(cv=cv_data)

#     # PDFKit options to improve layout
#     options = {
#         "page-size": "A4",
#         "margin-top": "10mm",
#         "margin-right": "10mm",
#         "margin-bottom": "10mm",
#         "margin-left": "10mm",
#         "zoom": "1.5",  # Scale content to fill page better
#         "dpi": 300,      # Higher quality text
#         "encoding": "UTF-8",
#     }

#     # Convert HTML to PDF using PDFKit (wkhtmltopdf)
#     pdf_bytes = pdfkit.from_string(html_content, False, configuration=pdfkit_config, options=options)
#     return BytesIO(pdf_bytes).getvalue()













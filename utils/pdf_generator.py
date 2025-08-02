import pdfkit

def generate_pdf(html_content, output_path):
    options = {
        'page-size': 'A4',
        'encoding': "UTF-8",
    }
    pdfkit.from_string(html_content, output_path, options=options)
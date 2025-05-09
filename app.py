from flask import Flask, render_template, request, jsonify, make_response
import markdown
import traceback
import io
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return render_template('index.html')

# Add OPTIONS method for CORS preflight


@app.route('/export', methods=['POST', 'OPTIONS'])
def export_pdf():
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        html_content = request.json.get('html')
        if not html_content:
            return jsonify({"error": "No HTML content provided"}), 400

        # Add some basic styling for the PDF
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{ size: A4; margin: 1cm; }}
                body {{ font-family: Arial, sans-serif; margin: 0; }}
                pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; }}
                code {{ font-family: monospace; }}
                h1, h2, h3, h4, h5, h6 {{ color: #333; }}
                a {{ color: #0066cc; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        try:
            # Try using reportlab + html2text as primary method
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            import html2text

            app.logger.info("Using reportlab + html2text for PDF generation")

            # Convert HTML to markdown text
            text_maker = html2text.HTML2Text()
            text_maker.ignore_links = False
            markdown_text = text_maker.handle(html_content)

            # Create PDF
            pdf_buffer = io.BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
            styles = getSampleStyleSheet()

            # Split markdown into paragraphs and convert to reportlab elements
            elements = []
            for line in markdown_text.split('\n\n'):
                if line.strip():
                    elements.append(Paragraph(line.replace(
                        '\n', '<br/>'), styles['Normal']))
                    elements.append(Spacer(1, 12))

            doc.build(elements)
            pdf_buffer.seek(0)

            # Return PDF
            response = make_response(pdf_buffer.getvalue())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'attachment; filename=rendered.pdf'
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response

        except Exception as pdf_error:
            # Log the error
            app.logger.error(
                f"ReportLab PDF generation failed: {str(pdf_error)}")

            # If reportlab fails, return HTML file instead
            app.logger.warning("PDF generation failed, falling back to HTML")
            response = make_response(styled_html)
            response.headers['Content-Type'] = 'text/html'
            response.headers['Content-Disposition'] = 'attachment; filename=rendered.html'
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response

    except Exception as e:
        app.logger.error(f"Export error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Use the PORT environment variable provided by Render
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)

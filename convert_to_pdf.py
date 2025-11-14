#!/usr/bin/env python3
"""
Convert Markdown files to professionally formatted PDFs
"""

import markdown2
from weasyprint import HTML, CSS
from datetime import datetime

def markdown_to_pdf(markdown_file, pdf_file, title):
    """Convert a markdown file to a styled PDF"""

    # Read markdown content
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # Convert markdown to HTML
    html_content = markdown2.markdown(
        markdown_content,
        extras=['tables', 'fenced-code-blocks', 'break-on-newline', 'header-ids']
    )

    # Create styled HTML document
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <style>
            @page {{
                size: letter;
                margin: 0.75in;
                @bottom-right {{
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 9pt;
                    color: #757575;
                }}
                @bottom-left {{
                    content: "SCal Mobile - {title}";
                    font-size: 9pt;
                    color: #757575;
                }}
            }}

            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                font-size: 10pt;
                line-height: 1.6;
                color: #1A1A1A;
                max-width: 100%;
            }}

            h1 {{
                color: #2C2C2C;
                font-size: 24pt;
                font-weight: 700;
                margin-top: 0;
                margin-bottom: 20pt;
                padding-bottom: 10pt;
                border-bottom: 3px solid #2C2C2C;
                page-break-after: avoid;
            }}

            h2 {{
                color: #2C2C2C;
                font-size: 18pt;
                font-weight: 600;
                margin-top: 24pt;
                margin-bottom: 12pt;
                page-break-after: avoid;
            }}

            h3 {{
                color: #2C2C2C;
                font-size: 14pt;
                font-weight: 600;
                margin-top: 18pt;
                margin-bottom: 10pt;
                page-break-after: avoid;
            }}

            h4 {{
                color: #3A3A3A;
                font-size: 12pt;
                font-weight: 600;
                margin-top: 14pt;
                margin-bottom: 8pt;
                page-break-after: avoid;
            }}

            p {{
                margin-bottom: 10pt;
                text-align: justify;
            }}

            ul, ol {{
                margin-bottom: 10pt;
                padding-left: 20pt;
            }}

            li {{
                margin-bottom: 6pt;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15pt 0;
                font-size: 9pt;
                page-break-inside: avoid;
            }}

            th {{
                background: #2C2C2C;
                color: white;
                padding: 8pt;
                text-align: left;
                font-weight: 600;
            }}

            td {{
                padding: 8pt;
                border-bottom: 1px solid #E0E0E0;
            }}

            tr:nth-child(even) {{
                background: #F9F9F9;
            }}

            code {{
                font-family: 'Courier New', monospace;
                background: #F5F5F5;
                padding: 2pt 4pt;
                border-radius: 3pt;
                font-size: 9pt;
                color: #2C2C2C;
            }}

            pre {{
                background: #F5F5F5;
                padding: 12pt;
                border-left: 4px solid #2C2C2C;
                overflow-x: auto;
                margin: 15pt 0;
                page-break-inside: avoid;
            }}

            pre code {{
                background: none;
                padding: 0;
            }}

            blockquote {{
                border-left: 4px solid #757575;
                padding-left: 15pt;
                margin-left: 0;
                color: #757575;
                font-style: italic;
            }}

            hr {{
                border: none;
                border-top: 2px solid #E0E0E0;
                margin: 20pt 0;
            }}

            strong {{
                font-weight: 600;
                color: #2C2C2C;
            }}

            a {{
                color: #2C2C2C;
                text-decoration: none;
                border-bottom: 1px solid #757575;
            }}

            .cover-page {{
                text-align: center;
                padding-top: 200pt;
                page-break-after: always;
            }}

            .cover-title {{
                font-size: 32pt;
                font-weight: 700;
                color: #2C2C2C;
                margin-bottom: 20pt;
            }}

            .cover-subtitle {{
                font-size: 16pt;
                color: #757575;
                margin-bottom: 10pt;
            }}

            .cover-date {{
                font-size: 12pt;
                color: #757575;
                margin-top: 40pt;
            }}
        </style>
    </head>
    <body>
        <div class="cover-page">
            <div class="cover-title">{title}</div>
            <div class="cover-subtitle">SCal Mobile</div>
            <div class="cover-subtitle">Strategic Partnership Development</div>
            <div class="cover-date">Generated: {datetime.now().strftime('%B %d, %Y')}</div>
        </div>
        {html_content}
    </body>
    </html>
    """

    # Convert HTML to PDF
    HTML(string=styled_html).write_pdf(pdf_file)
    print(f"✓ Successfully created: {pdf_file}")

if __name__ == '__main__':
    # Convert Partnership Pipeline
    print("Converting PARTNERSHIP_PIPELINE.md to PDF...")
    markdown_to_pdf(
        'PARTNERSHIP_PIPELINE.md',
        'SCal_Mobile_Partnership_Pipeline.pdf',
        'IMEI Data Provider Partnership Pipeline'
    )

    # Convert Backend Analysis
    print("\nConverting BACKEND_ANALYSIS.md to PDF...")
    markdown_to_pdf(
        'BACKEND_ANALYSIS.md',
        'SCal_Mobile_Backend_Analysis.pdf',
        'GSM Fusion Backend Analysis'
    )

    print("\n✓ All documents converted successfully!")
    print("\nGenerated PDFs:")
    print("  1. SCal_Mobile_Partnership_Pipeline.pdf")
    print("  2. SCal_Mobile_Backend_Analysis.pdf")

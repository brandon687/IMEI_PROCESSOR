#!/usr/bin/env python3
"""
Convert Markdown files to professionally formatted PDFs using ReportLab
"""

import re
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self.doc_title = kwargs.get('doc_title', 'SCal Mobile')

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor('#757575'))
        self.drawRightString(
            7.5 * inch, 0.5 * inch,
            f"Page {self._pageNumber} of {page_count}"
        )
        self.drawString(
            0.75 * inch, 0.5 * inch,
            f"SCal Mobile - {self.doc_title}"
        )

def clean_markdown_formatting(text):
    """Remove or convert markdown formatting that doesn't translate well"""
    # Remove XML/HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Convert bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Convert italic
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    # Convert inline code
    text = re.sub(r'`(.+?)`', r'<font name="Courier" size="9" color="#2C2C2C">\1</font>', text)
    return text

def parse_markdown_to_pdf(markdown_file, pdf_file, title):
    """Convert markdown file to styled PDF"""

    # Read markdown content
    with open(markdown_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Create PDF
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=1*inch,
    )

    # Define styles
    styles = getSampleStyleSheet()

    # Custom styles
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#2C2C2C'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#757575'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))

    styles.add(ParagraphStyle(
        name='CustomH1',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#2C2C2C'),
        spaceAfter=15,
        spaceBefore=20,
        fontName='Helvetica-Bold',
        borderWidth=2,
        borderColor=colors.HexColor('#2C2C2C'),
        borderPadding=5
    ))

    styles.add(ParagraphStyle(
        name='CustomH2',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2C2C2C'),
        spaceAfter=12,
        spaceBefore=18,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='CustomH3',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=colors.HexColor('#2C2C2C'),
        spaceAfter=10,
        spaceBefore=14,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='CustomH4',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=colors.HexColor('#3A3A3A'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#1A1A1A'),
        spaceAfter=10,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    ))

    styles.add(ParagraphStyle(
        name='CustomCode',
        parent=styles['Code'],
        fontSize=8,
        textColor=colors.HexColor('#2C2C2C'),
        backColor=colors.HexColor('#F5F5F5'),
        leftIndent=10,
        fontName='Courier'
    ))

    # Build story (content)
    story = []

    # Cover page
    story.append(Spacer(1, 2.5*inch))
    story.append(Paragraph(title, styles['CustomTitle']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("SCal Mobile", styles['CustomSubtitle']))
    story.append(Paragraph("Strategic Partnership Development", styles['CustomSubtitle']))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y')}",
        styles['CustomSubtitle']
    ))
    story.append(PageBreak())

    # Parse markdown content
    in_code_block = False
    code_lines = []
    in_list = False
    list_items = []
    table_lines = []
    in_table = False

    for line in lines:
        line = line.rstrip()

        # Handle code blocks
        if line.startswith('```'):
            if in_code_block:
                # End code block
                code_text = '\n'.join(code_lines)
                story.append(Preformatted(code_text, styles['CustomCode']))
                story.append(Spacer(1, 10))
                code_lines = []
                in_code_block = False
            else:
                # Start code block
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        # Handle tables
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                in_table = True
                table_lines = []
            table_lines.append(line)
            continue
        else:
            if in_table:
                # Process table
                if len(table_lines) > 2:  # Has header and data
                    table_data = []
                    for tline in table_lines:
                        if '---' not in tline:  # Skip separator line
                            cells = [cell.strip() for cell in tline.split('|')[1:-1]]
                            table_data.append(cells)

                    if table_data:
                        t = Table(table_data)
                        t.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C2C2C')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 9),
                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 1), (-1, -1), 8),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                            ('TOPPADDING', (0, 0), (-1, 0), 8),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E0E0')),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9F9F9')]),
                        ]))
                        story.append(t)
                        story.append(Spacer(1, 15))
                in_table = False
                table_lines = []

        # Skip empty lines
        if not line.strip():
            if in_list and list_items:
                # End list
                for item in list_items:
                    story.append(item)
                list_items = []
                in_list = False
            story.append(Spacer(1, 10))
            continue

        # Handle headers
        if line.startswith('# '):
            text = clean_markdown_formatting(line[2:])
            story.append(Paragraph(text, styles['CustomH1']))
        elif line.startswith('## '):
            text = clean_markdown_formatting(line[3:])
            story.append(Paragraph(text, styles['CustomH2']))
        elif line.startswith('### '):
            text = clean_markdown_formatting(line[4:])
            story.append(Paragraph(text, styles['CustomH3']))
        elif line.startswith('#### '):
            text = clean_markdown_formatting(line[5:])
            story.append(Paragraph(text, styles['CustomH4']))

        # Handle horizontal rules
        elif line.strip() == '---':
            story.append(Spacer(1, 10))

        # Handle lists
        elif line.strip().startswith(('- ', '* ', '+ ')):
            in_list = True
            text = clean_markdown_formatting(line.strip()[2:])
            bullet_style = ParagraphStyle(
                'Bullet',
                parent=styles['CustomBody'],
                leftIndent=20,
                bulletIndent=10,
                bulletText='•'
            )
            list_items.append(Paragraph(f'• {text}', bullet_style))

        elif re.match(r'^\d+\.', line.strip()):
            in_list = True
            text = clean_markdown_formatting(re.sub(r'^\d+\.\s*', '', line.strip()))
            bullet_style = ParagraphStyle(
                'Numbered',
                parent=styles['CustomBody'],
                leftIndent=20,
            )
            match = re.match(r'^(\d+)\.', line.strip())
            if match:
                num = match.group(1)
                list_items.append(Paragraph(f'{num}. {text}', bullet_style))

        # Regular paragraphs
        else:
            if in_list and list_items:
                for item in list_items:
                    story.append(item)
                list_items = []
                in_list = False

            text = clean_markdown_formatting(line)
            if text.strip():
                story.append(Paragraph(text, styles['CustomBody']))

    # Build PDF
    doc.build(
        story,
        onFirstPage=lambda canvas, doc: None,
        onLaterPages=lambda canvas, doc: None,
        canvasmaker=lambda *args, **kwargs: NumberedCanvas(*args, doc_title=title, **kwargs)
    )

    print(f"✓ Successfully created: {pdf_file}")

if __name__ == '__main__':
    # Convert Partnership Pipeline
    print("Converting PARTNERSHIP_PIPELINE.md to PDF...")
    parse_markdown_to_pdf(
        'PARTNERSHIP_PIPELINE.md',
        'SCal_Mobile_Partnership_Pipeline.pdf',
        'IMEI Data Provider Partnership Pipeline'
    )

    # Convert Backend Analysis
    print("\nConverting BACKEND_ANALYSIS.md to PDF...")
    parse_markdown_to_pdf(
        'BACKEND_ANALYSIS.md',
        'SCal_Mobile_Backend_Analysis.pdf',
        'GSM Fusion Backend Analysis'
    )

    print("\n✓ All documents converted successfully!")
    print("\nGenerated PDFs:")
    print("  1. SCal_Mobile_Partnership_Pipeline.pdf")
    print("  2. SCal_Mobile_Backend_Analysis.pdf")

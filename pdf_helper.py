import pdftotext
import pdfrw
import re
import pandas as pd


def pdf_to_text(path):
    with open(path, "rb") as f:
        pdf = pdftotext.PDF(f, physical=True)
    return pdf


def slice_pdf_pages(source, target):
    writer = pdfrw.PdfWriter()
    for page in pdfrw.PdfReader(source).pages:
        for x in [0, 0.5]:
            for y in [0, 0.5]:
                new_page = pdfrw.PageMerge()
                new_page.add(page, viewrect=(x, y, 0.499, 0.499))
                writer.addpages([new_page.render()])
    writer.write(target)
    return target


def get_lines_from_text(text_str, page_no):
    regex = r"(^\s{0,15}(?P<line>\d+)\s+((?P<speaker>[A-Z\s]+)\:\s+)?(?P<text>.*)$)"
    matches = re.finditer(regex, text_str, re.MULTILINE)
    lines = pd.DataFrame()
    for matchNum, match in enumerate(matches, start=1):
        lines = lines.append(match.groupdict(), ignore_index=True)
    lines['page'] = page_no
    return lines




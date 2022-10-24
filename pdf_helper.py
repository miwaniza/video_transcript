import pdftotext
import pdfrw



def pdf_to_text(path):
    with open(path, "rb") as f:
        pdf = pdftotext.PDF(f, physical=True)
    return pdf

def slice_pdf_pages(source, target)
    writer = pdfrw.PdfWriter()
    for page in pdfrw.PdfReader(source).pages:
        for x in [0, 0.5]:
            for y in [0, 0.5]:
                new_page = pdfrw.PageMerge()
                new_page.add(page, viewrect=(x, y, 0.5, 0.5))
                writer.addpages([new_page.render()])
    writer.write(target)
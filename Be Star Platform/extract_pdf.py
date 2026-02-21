import fitz
doc = fitz.open('Be Star Event – Official Smart Event Platform.pdf')
text = ''.join([page.get_text() for page in doc])
with open('pdf_content.txt', 'w', encoding='utf-8') as f:
    f.write(text)

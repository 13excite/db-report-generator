import PyPDF2

file=open('rechnung.pdf',"rb")

reader=PyPDF2.PdfReader(file)

page1=reader.pages[0]
page_count = len(reader.pages)
print(page_count)
pdfData=page1.extract_text()
print(pdfData)

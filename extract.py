from PyPDF2 import PdfFileReader

#  open the file
target_file = "./public/upload/PENELITIAN_6064836_5 (1).pdf"
pdf = PdfFileReader(open(target_file, 'rb'))

# get num of pages
num_pages = pdf.getNumPages()
print(num_pages)

# extract text using loop
text = ""
for i in range(num_pages):
    page = pdf.getPage(i)
    text = text + " " + page.extractText()

print(text)
print(len(text))
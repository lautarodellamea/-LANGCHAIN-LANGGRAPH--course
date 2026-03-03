# PARA CARGAR PDF
#  pip install pypdf
# from langchain.document_loaders import PyPDFLoader

# loader = PyPDFLoader("C:\\LAUTARO\\LANGCHAIN\\curso_langchain\\tema_3\\cv-lautaro-della-mea.pdf")

# # documento pdf procesado
# pages = loader.load()

# print(dir(pages[0])) # lista de metodos y atributos del objeto pages [0] es la primera pagina del documento pdf
# print(pages) # lista de paginas del documento pdf

# for i, page in enumerate(pages):
#     print(f"=== Pagina {i+1} ===")
#     print(f"Contenido: {page.page_content}")
#     print(f"Metadatos: {page.metadata}")



# PARA CARGAR WEBS 
# pip install beautifulsoup4
from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://techmind.ac/")

docs = loader.load()

print(docs)
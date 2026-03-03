# pip install chromadb
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFDirectoryLoader # carga todos los pdf de un directorio
from langchain_text_splitters import RecursiveCharacterTextSplitter


# UNA VEZ CARGADO LOS DATOS EN LA BASE DE DATOS, NO NECESITAMOS VOLVER A CARGARLOS
loader = PyPDFDirectoryLoader("C:\\LAUTARO\\LANGCHAIN\\curso_langchain\\tema_3\\contratos")
documentos = loader.load()

print(f"Se cargaron {len(documentos)} documentos desde el directorio.")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=5000,
    chunk_overlap=1000 # mientras mas pequeños los fragmentos menos informacion en cada uno de ellos
)

docs_split = text_splitter.split_documents(documentos)

print(f"Se crearon {len(docs_split)} chunks de texto.")

vectorstore = Chroma.from_documents(
    docs_split,
    embedding=OpenAIEmbeddings(model="text-embedding-3-large"),
    persist_directory="C:\\LAUTARO\\LANGCHAIN\\curso_langchain\\tema_3\\05\\chroma_db"
)

##############################################################################################

consulta = "¿Dónde se encuentra el local del contrato en el que participa María Jiménez Campos"


# busqueda por similitud el k es el numero de fragmentos que queremos que nos devuelva
resultados = vectorstore.similarity_search(consulta, k=3)

print("Top 3 documentos mas similares a la consulta:\n")
for i, doc in enumerate(resultados, start=1):
    print(f"Contenido: {doc.page_content}")
    print(f"Metadatos: {doc.metadata}")


# estas son consultas basadas en similitud semantica, luego esta respuesta se la pasariamos a un LLM para que nos de una respuesta mas coherente y precisa

# En este ejemplo se realiza una búsqueda por similitud semántica directamente
# sobre el vectorstore (Chroma) usando similarity_search.
# No se está utilizando explícitamente la abstracción Retriever de LangChain.
# El método devuelve los k fragmentos más relevantes según cercanía vectorial,
# y luego estos resultados podrían pasarse a un LLM para generar una respuesta final (RAG).
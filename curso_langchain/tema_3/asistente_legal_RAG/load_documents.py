# Script para cargar documentos PDF en la base de datos vectorial del asistente legal
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import CHROMA_DB_PATH, EMBEDDING_MODEL

# Ruta a los contratos
CONTRATOS_PATH = "C:\\LAUTARO\\LANGCHAIN\\curso_langchain\\tema_3\\contratos"

print("Cargando documentos PDF...")
loader = PyPDFDirectoryLoader(CONTRATOS_PATH)
documentos = loader.load()

print(f"Se cargaron {len(documentos)} documentos desde el directorio.")

# Configurar el text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

# Dividir documentos en chunks
docs_split = text_splitter.split_documents(documentos)

print(f"Se crearon {len(docs_split)} chunks de texto.")

# Crear o actualizar la base de datos vectorial
print("Creando embeddings y guardando en la base de datos...")
vectorstore = Chroma.from_documents(
    docs_split,
    embedding=OpenAIEmbeddings(model=EMBEDDING_MODEL),
    persist_directory=CHROMA_DB_PATH
)

print(f"Documentos cargados exitosamente en: {CHROMA_DB_PATH}")
print(f"Total de chunks indexados: {len(docs_split)}")


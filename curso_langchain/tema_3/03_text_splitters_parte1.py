from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. Cargar el documento PDF
loader = PyPDFLoader("C:\\LAUTARO\\LANGCHAIN\\curso_langchain\\tema_3\\03\\quijote.pdf")
pages = loader.load()

# Dividir el texto en chunks
text_splitter = RecursiveCharacterTextSplitter(
  chunk_size=10000, # tamaño aprox de cada fragmento 
  chunk_overlap=200 # cantidad de caracteres que se solapan entre cada fragmento
  # podriamos definir por que caracteres quisieramos dividir (saltos de linea, espacios, etc)
  )

chunks = text_splitter.split_documents(pages)


# 3. Pasar el texto al LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
summaries = []

# hacemos peticion a los 10 primeros fragmentos para no gastar tanto
i = 0
for chunk in chunks:
  if i >= 10:
    break
  response = llm.invoke(f"Haz un resumen de los puntos mas importantes del siguiente fragmento: {chunk.page_content}")
  summaries.append(response.content)
  i += 1

print(summaries)

# for chunk in chunks:
#   response = llm.invoke(f"Haz un resumen de los puntos mas importantes del siguiente fragmento: {chunk.page_content}")
#   summaries.append(response.content)
  
final_summary = llm.invoke(f"Combina y sintetiza estos resumenes en un solo resumen coherente y completo: {" ".join(summaries)}")

print(final_summary.content)
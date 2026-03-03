from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_classic.retrievers.multi_query import MultiQueryRetriever

# Estamos abriendo una base de datos que ya esta cargada en la memoria, no necesitamos volver a cargar los datos

vectorstore = Chroma(
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-large"),
    persist_directory="C:\\LAUTARO\\LANGCHAIN\\curso_langchain\\tema_3\\05\\chroma_db"
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# creamos un retriever basado en la base de datos, search_type es el tipo de busqueda que queremos realizar, search_kwargs son los argumentos de la busqueda, en este caso k es el numero de fragmentos que queremos que nos devuelva
# una vez que obtiene resultados los fusiona y desduplica a diferencia de la busqueda con el metodo de la base de datos que nos devuelve los resultados sin fusion y sin desduplicar
# nos dara la info filtrada y para esto hace uso de un LLM
base_retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})
retriever = MultiQueryRetriever.from_llm(retriever=base_retriever, llm=llm)

consulta = "¿Dónde se encuentra el local del contrato en el que participa María Jiménez Campos?"
resultados = retriever.invoke(consulta)

print("Top documentos mas similares a la consulta:\n")
for i, doc in enumerate(resultados, start=1):
    print(f"Contenido: {doc.page_content}")
    print(f"Metadatos: {doc.metadata}")
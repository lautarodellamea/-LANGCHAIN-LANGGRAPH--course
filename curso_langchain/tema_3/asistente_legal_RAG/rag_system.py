from langchain_community.vectorstores import Chroma # Base de datos vectorial. Guarda embeddings y permite buscar por similitud.

# ChatOpenAI: el modelo que genera texto.
# OpenAIEmbeddings: convierte texto en números (vectores).
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from langchain_core.prompts import PromptTemplate # Plantilla para armar prompts dinámicos.
from langchain_core.runnables import RunnablePassthrough # Permite pasar datos sin modificarlos dentro del pipeline.
from langchain_core.output_parsers import StrOutputParser # Convierte la respuesta del modelo en string plano.
from langchain_classic.retrievers.multi_query import MultiQueryRetriever # Genera varias versiones de la pregunta automáticamente para mejorar búsqueda.
from langchain_classic.retrievers import EnsembleRetriever # Combina varios retrievers (como un promedio inteligente).
import streamlit as st # Para hacer la app web.

from config import *
from prompts import *

# Esta función arma TODO el sistema.
# Y está cacheada: Para que no se reconstruya todo cada vez que alguien hace una pregunta.
@st.cache_resource
def initialize_rag_system():

    # Vector Store - Carga la base vectorial desde disco.
    # Usa embeddings para poder buscar.
    vectorestore = Chroma(
        embedding_function=OpenAIEmbeddings(model=EMBEDDING_MODEL),\
        persist_directory=CHROMA_DB_PATH
    )

    # Modelos
    # Separamos los modelos para: Generar variaciones de preguntas (mejor búsqueda) y Generar la respuesta final
    llm_queries = ChatOpenAI(model=QUERY_MODEL, temperature=0)
    llm_generation = ChatOpenAI(model=GENERATION_MODEL, temperature=0)

    # Retriever MMR (Maximal Margin Relevance) -> metodo mas avanzado que similitud por coseno, este tambien se centra en la diversidad (se va a preocupar que haya documentos relevantes diferentes entre ellos, obteniendo mejores resultados)
    
    # MMR =
    # Busca documentos:
    # relevantes pero distintos entre sí, evita traer 5 párrafos iguales.

    # Parámetros:
    # k: cuantos documentos finales traer
    # lambda_mult: cuánto prioriza diversidad
    # fetch_k: cuantos candidatos analiza antes de elegir
    base_retriever = vectorestore.as_retriever(
        search_type=SEARCH_TYPE,
        search_kwargs={
            "k": SEARCH_K,
            "lambda_mult": MMR_DIVERSITY_LAMBDA,
            "fetch_k": MMR_FETCH_K
        }
    )

    # Retriever adicional con similarity para comparar
    # Clásico:
    # Busca solo por similitud matemática, más simple, menos inteligente.
    similarity_retriever = vectorestore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": SEARCH_K}
    )

    # Prompt personalizado para MultiQueryRetriever
    # MUY clave. ¿Qué hace?

    # El modelo transforma: "¿Dónde está el contrato de María?" En algo tipo:
    # ¿En qué local figura María?
    # ¿Cuál es la dirección del contrato?
    # ¿Dónde se ubica el documento?

    # Luego busca con cada una.

    # Resultado:
    # 📈 Mejores documentos encontrados.
    multi_query_prompt = PromptTemplate.from_template(MULTI_QUERY_PROMPT)

    # MultiQueryRetriever con prompt personalizado
    mmr_multi_retriever = MultiQueryRetriever.from_llm(
        retriever=base_retriever,
        llm=llm_queries,
        prompt=multi_query_prompt
    )

    # Ensemble Retriever que combinar MMR y similarity
    # Si activás: ENABLE_HYBRID_SEARCH Se combinan:
    # MMR + MultiQuery (70%)   +   Similarity (30%)
    # Es como:
    # "Le hago caso más al inteligente, pero no ignoro al clásico."
    if ENABLE_HYBRID_SEARCH:
        ensemble_retriever = EnsembleRetriever(
            retrievers=[mmr_multi_retriever, similarity_retriever],
            weights=[0.7, 0.3], # mayor peso a MMR
            similarity_threshold=SIMILARITY_THRESHOLD
        )
        final_retriever = ensemble_retriever
    else:
        final_retriever = mmr_multi_retriever

    # Prompt del RAG
    # molde de la respuesta.
    prompt = PromptTemplate.from_template(RAG_TEMPLATE)

    # Funcion para formatear y preprocesar los documentos recuperados
    # Función para que el contexto quede lindo.
    # En vez de pasar texto crudo, ayuda MUCHÍSIMO al modelo.
    def format_docs(docs):
        formatted = []

        for i, doc in enumerate(docs, 1):
            header = f"[Fragmento {i}]"
            
            if doc.metadata:
                if 'source' in doc.metadata:
                    source = doc.metadata['source'].split("\\")[-1] if '\\' in doc.metadata['source'] else doc.metadata['source']
                    header += f" - Fuente: {source}"
                if 'page' in doc.metadata:
                    header += f" - Pagina: {doc.metadata['page']}"
        
            content = doc.page_content.strip()
            formatted.append(f"{header}\n{content}")
        
        return "\n\n".join(formatted)


    # Busca documentos
    # Formatea documentos
    # Mete eso + pregunta en el prompt
    # Llama al modelo
    # Devuelve texto limpio
    # Es un pipeline.
    rag_chain = (
        {
            "context": final_retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm_generation
        | StrOutputParser()
    )

    return rag_chain, final_retriever

# Cuando el usuario pregunta:
# Ejecuta el chain
# Devuelve respuesta
# También devuelve los fragmentos usados (para mostrar transparencia)
def query_rag(question):
    try:
        rag_chain, retriever = initialize_rag_system()

        # Obtener respuesta
        response = rag_chain.invoke(question)

        # Obtener documentos para mostrarlos
        # Usar invoke() que es el método estándar en versiones recientes de LangChain
        docs = retriever.invoke(question)

        # Formatear los documentos para mostrar
        docs_info = []
        for i, doc in enumerate(docs[:SEARCH_K], 1):
            doc_info = {
                "fragmento": i,
                "contenido": doc.page_content[:1000] + "..." if len(doc.page_content) > 1000 else doc.page_content,
                "fuente": doc.metadata.get('source', 'No especificada').split("\\")[-1],
                "pagina": doc.metadata.get('page', 'No especificada')
            }
            docs_info.append(doc_info)
        
        return response, docs_info
    
    except Exception as e:
        error_msg = f"Error al procesar la cosulta: {str(e)}"
        return error_msg, []
    
# Devuelve la config actual para mostrar en UI.
# Sirve para debugging y transparencia.
def get_retriever_info():
    """Obtiene información sobre la configuración del retriever"""
    return {
        "tipo": f"{SEARCH_TYPE.upper()} + MultiQuery" + (" + Hybrid" if ENABLE_HYBRID_SEARCH else ""),
        "documentos": SEARCH_K,
        "diversidad": MMR_DIVERSITY_LAMBDA,
        "candidatos": MMR_FETCH_K,
        "umbral": SIMILARITY_THRESHOLD if ENABLE_HYBRID_SEARCH else "N/A"
    }
# 🚀 Curso Completo: LangChain, LangGraph y Agentes IA con Python

Repositorio con ejercicios y proyectos del curso de LangChain, LangGraph y Agentes de IA con Python.

**Curso:** [Curso Completo LangChain, LangGraph y Agentes IA con Python](https://www.udemy.com/course/curso-completo-langchain-langgraph-y-agentes-ia-con-python/)

## 📚 Contenido del Curso

Este repositorio contiene ejemplos prácticos y proyectos implementados durante el curso, organizados por temas:

### Tema 1: Introducción a LangChain
- Hello World con diferentes modelos (OpenAI, Gemini)
- Streamlit Chatbot básico
- LCEL (LangChain Expression Language)

### Tema 2: Prompts y Output Parsers
- Prompt Templates
- Chat Prompt Templates
- Output Parsers
- Proyecto: Analizador de CVs con Streamlit

### Tema 3: RAG (Retrieval Augmented Generation)
- Document Loaders
- Text Splitters
- Embeddings y Vector Stores
- Multi-Query Retriever
- Proyecto: Asistente Legal RAG

### Tema 4: LangGraph
- Workflows con StateGraph
- Control de flujo condicional
- Checkpointing y persistencia
- Proyecto: Helpdesk con RAG + LangGraph

## 🛠️ Tecnologías Utilizadas

- **Python 3.11+**
- **LangChain** - Framework para aplicaciones con LLMs
- **LangGraph** - Construcción de workflows con grafos de estado
- **Streamlit** - Interfaces web interactivas
- **ChromaDB** - Base de datos vectorial
- **OpenAI API** - Modelos GPT
- **Google Gemini** - Modelos alternativos

## ⚙️ Configuración

### Requisitos Previos

```bash
# Clonar el repositorio
git clone https://github.com/lautarodellamea/-LANGCHAIN-LANGGRAPH--course.git
cd LANGCHAIN
```

### Instalación

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias (crear requirements.txt según necesidad)
pip install langchain langchain-openai langchain-community langgraph streamlit chromadb
```

### Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
OPENAI_API_KEY=tu_api_key_aqui
```

## 📁 Estructura del Repositorio

```
LANGCHAIN/
├── curso_langchain/
│   ├── tema_1/          # Introducción y primeros pasos
│   ├── tema_2/          # Prompts y Output Parsers
│   │   └── cv_analyzer/ # Proyecto: Analizador de CVs
│   ├── tema_3/          # RAG y Vector Stores
│   │   └── asistente_legal_RAG/ # Proyecto: Asistente Legal
│   └── tema_4/          # LangGraph
│       └── helpdesk-con-IA-langgraph-y-RAG/ # Proyecto: Helpdesk
└── README.md
```

## 🎯 Proyectos Principales

### 1. Analizador de CVs (Tema 2)
Sistema de análisis de CVs usando LangChain y Streamlit.

### 2. Asistente Legal RAG (Tema 3)
Sistema RAG completo para consultas sobre contratos legales.

### 3. Helpdesk con RAG + LangGraph (Tema 4)
Sistema de helpdesk inteligente con:
- Búsqueda vectorial (RAG)
- Clasificación automática
- Human-in-the-loop
- Checkpointing con SQLite

## 🚀 Ejecutar Proyectos

### Streamlit Apps

```bash
# Desde el directorio del proyecto
streamlit run app.py
```

### Scripts Python

```bash
python nombre_del_script.py
```

## 📝 Notas

- Los archivos con secretos (`credentials.json`, `test.py`) están excluidos del repositorio por seguridad.
- Las bases de datos locales (`*.db`, `chroma_db/`) no se incluyen en el repositorio.
- Cada proyecto puede tener sus propias dependencias específicas.

## 🔗 Enlaces Útiles

- [Curso en Udemy](https://www.udemy.com/course/curso-completo-langchain-langgraph-y-agentes-ia-con-python/)
- [Documentación LangChain](https://python.langchain.com/)
- [Documentación LangGraph](https://langchain-ai.github.io/langgraph/)

## 📄 Licencia

Este repositorio contiene código de ejemplo del curso. Úsalo como referencia para tus propios proyectos.

---

**Desarrollado durante el curso de LangChain, LangGraph y Agentes IA con Python**


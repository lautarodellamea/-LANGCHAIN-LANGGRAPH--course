from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from operator import attrgetter

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

@tool("user_db_tool")
def herramienta_personalizada(query: str) -> str:
    """Consulta la base de datos de usuarios de la empresa y devuelve el resultado de la consulta.""" # descripcion de la herramienta que le sirve al LLM para saber que hacer con ella
    return f"Respuesta a la consulta: {query}"

# enlazamos la herramienta al LLM
llm_with_tools = llm.bind_tools([herramienta_personalizada])

# creamos la cadena de herramientas
# Extrae las llamadas a herramientas (tool_calls).
# Ejecuta la herramienta por cada llamada.
chain = llm_with_tools | attrgetter("tool_calls") | herramienta_personalizada.map()

response = chain.invoke("Genera un resumen de la informacion sobre el usuario UX341234 que se encuentra en nuestra base de datos.")
# response = chain.invoke("Cual es la capital de España?") # con esta pregunta no usa la herramienta porque nada que ver

print(response)
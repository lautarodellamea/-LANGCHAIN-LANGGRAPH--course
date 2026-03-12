# el profe prefiere usarlo sin el structured tool, sino con el tool de langchain_core
# from langchain_core.tools import tool
from langchain_core.tools import StructuredTool

def herramienta_personalizada(query: str) -> str:
    """Consulta la base de datos de usuarios de la empresa."""
    # Codigo que accede a la base de datos
    return f"Respuesta a la consulta: {query}"

mi_tool = StructuredTool.from_function(herramienta_personalizada)

print(mi_tool.run("Consulta de prueba"))
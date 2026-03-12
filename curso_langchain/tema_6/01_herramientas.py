# el propio LLM es el encargado de ejecutar las herramientas o invocar la fucnionalidad.
from langchain_core.tools import Tool
from langchain_experimental.utilities import PythonREPL


# inicializamos la herramienta 
python_repl = PythonREPL()

# la registro con un nombre y una descripcion
tool = Tool(
    name="Python_repl",
    func=python_repl.run,
    description="Ejecuta codigo en Python en un interprete para calculos o logica matematica."
)

output = tool.run("print(2+2)")
print(output)



# # Respuesta tradicional (texto libre)
# "Necesito usar la herramienta de búsqueda con el término 'clima en Madrid'

# Tool calling moderno (estructurado)
# {
# 'tool calls" : [
#   {
#    "name": "buscar_clima",
#    "args": {"ciudad": "Madrid", "pais": "España"},
#    "id": "call_123"
#   }
#  ]
# }

# Ahora los modelos en vez de generar texto para saber que herramienta usar, generan un JSON con la herramienta y los argumentos que debe usar.
# devuelven 2 cosas, contenido que se proporciona al LLM que llamo la herramienta y tool artefacts que son datos que no se envian al modelo pero los tenemos disponibles para procesamiento posterior.
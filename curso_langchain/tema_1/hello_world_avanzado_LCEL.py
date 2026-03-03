from langchain_openai import ChatOpenAI

# en langchain 1.x es:
# from langchain_core.prompts import PromptTemplate
from langchain.prompts import PromptTemplate

# en langchain 1.x es:
# from langchain_classic.chains import LLMChain
# esto queda deprecado y se introduce un nuevo mecanismo para definir cadenas
# LCEL: langChain expresion language 
from langchain.chains import LLMChain

# iniciamos el modelo de lenguaje (el 4 mini es barato)
# la temperatura controla lo aleatorio o detirminista que sera el llm
# cuanto mayor se acerque a 1 mas creativo
chat = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

plantilla = PromptTemplate(
  input_variables=["nombre"],
  template="saluda al usuario cons su nombre.\nNombre del usuario: {nombre}\nAsistente:",
)

chain = plantilla | chat

resutado = chain.invoke({
  "nombre": "Lautaro"
})
print( resutado.content )
 
# este es el mecanismo RECOMENDADO para definir cadenas
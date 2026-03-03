from langchain_openai import ChatOpenAI

# iniciamos el modelo de lenguaje (el 4 mini es barato)
# la temperatura controla lo aleatorio o detirminista que sera el llm
# cuanto mayor se acerque a 1 mas creativo
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

pregunta = "¿En que año llego el ser humano al espacio?"

print("Pregunta:", pregunta)

# con invoke invocamos al llm
respuesta = llm.invoke(pregunta)
print("Respuesta del modelo:", respuesta.content)

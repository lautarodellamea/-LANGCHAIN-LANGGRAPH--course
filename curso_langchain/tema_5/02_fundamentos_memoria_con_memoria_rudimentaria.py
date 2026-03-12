from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente útil."),
    MessagesPlaceholder(variable_name="history"), # guardamos el historial de la conversacion en la plantilla del prompt
    ("human", "{input}")
])

chain = prompt | llm

history = []

print("Chat en terminal (escribe 'salir' para terminar)\n")

while True:
    try:
        user_input = input("Tú: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nHasta luego!")
        break

    if not user_input:
        continue
    if user_input.lower() in {"salir", "exit", "quit"}:
        print("Hasta luego!")
        break

    respuesta = chain.invoke({"history": history, "input": user_input})
    print("Asistente:", respuesta.content)

    # actualizamos el historial de la conversacion
    history.extend([
      HumanMessage(content=user_input), 
      AIMessage(content=respuesta.content)
    ])



# Con MessagePlaceholder podemos guardar el historial de la conversacion pero de forma rudimentaria, no es lo mas optimo
# ya que concatenamos todos los mensajes tanto los de usuario como los de la IA, dentro del listado history, y lo proporcionamos dentro de la ventana de contexto del propmt que enviamos en cada una de las invocaciones
# el consumo de recursos puede ser elevado y si hubiese varios usuarios conectados, se podrian entremezclar las cosas, no hay sesiones que identifiquen a cada usuario y su conversacion
# es una forma muy basica que no sirve para aplicaciones profesionales
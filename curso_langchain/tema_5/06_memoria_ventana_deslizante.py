# en el caso de conversaciones muy largas donde incluso se supere la ventana de contexto conviene usar una estrategia (de tantas que hay, ver documento), la que usaremos ahora se llama memoria con ventana deslizante esta mantiene los ultimos n mensajes, despues existe otra que guarda un resumen de la conversacion, vectorial, etc.

from langgraph.graph import MessagesState, StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.messages import trim_messages

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# para que alguien que lea el codigo entienda que estamos usando la estrategia de ventana deslizante, creamos la clase de estado WindowedState que hereda de MessagesState y no hace nada, solo es para saber que estamos usando la estrategia de ventana deslizante
class WindowedState(MessagesState):
    pass

workflow = StateGraph(state_schema=WindowedState)

# trim_messages es una funcion que permite dividir un mensaje en diferentes fragmentos
trimmer = trim_messages(
    strategy="last", # n ultimos mensajes
    max_tokens=6, # maximo de tokens que se pueden guardar en la ventana
    token_counter=len, # funcion que permite contar el numero de tokens de un mensaje (en este caso usamos la funcion len que permite contar el numero de caracteres de un mensaje)
    start_on="human", # se empieza a contar desde el mensaje del usuario, asegura que al dividir los mensajes siempre se empiece desde el mensaje del usuario
    include_system=True # se incluye el mensaje del sistema
)

def chatbot_node(state):
    """Nodo que procesa mensajes y genera respuestas."""
    trimmed_messages = trimmer.invoke(state["messages"])
    system_prompt = "Eres un asistente amigable que recuerda conversaciones previas."
    messages = [SystemMessage(content=system_prompt)] + trimmed_messages
    response = llm.invoke(messages)
    return {"messages": [response]}

workflow.add_node("chatbot", chatbot_node)
workflow.add_edge(START, "chatbot")

# Compilar el grafo
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

def chat(message, thread_id="sesion_terminal"):
    config = {"configurable": {"thread_id": thread_id}}
    result = app.invoke({"messages": [HumanMessage(content=message)]}, config)
    return result["messages"][-1].content

if __name__ == "__main__":
    print("Chat en terminal (escribe 'salir' para terminar)\n")
    session_id = "sesion_terminal"

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

        respuesta = chat(user_input, session_id)
        print("Asistente:", respuesta)
import streamlit as st # libreria/framwork que nos permite crear interfaces web
from langchain_openai import ChatOpenAI

# en langchain 1.x es:
# from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
# el SystemMessage son instrucciones que le damos al llm para que sepa como comportarse con los usuarios
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate

# Configuración inicial
st.set_page_config(page_title="Chatbot Básico", page_icon="🤖")
st.title("🤖 Chatbot Básico con LangChain")
st.markdown("Este es un *chatbot de ejemplo* construido con LangChain + Streamlit. ¡Escribe tu mensaje abajo para comenzar!")

with st.sidebar:
    st.header("Configuración")
    temperature = st.slider("Temperatura", 0.0, 1.0, 0.5, 0.1)
    model_name = st.selectbox("Modelo", ["gpt-3.5-turbo", "gpt-4", "gpt-4o-mini"])
    
    # Recrear el modelo con nuevos parámetros
    chat_model = ChatOpenAI(model=model_name, temperature=temperature)

# Inicializar el historial de mensajes en session_state
# mas adelante mantendremos memoria mediante langchain
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Crear el template de prompt con comportamiento específico
prompt_template = PromptTemplate(
    input_variables=["mensaje", "historial"],
    template=
    """
    Eres un asistente útil y amigable llamado ChatBot Pro. 

    Historial de conversación:
    {historial}

    Responde de manera clara y concisa a la siguiente pregunta: {mensaje}
    """
)

# Crear cadena usando LCEL (LangChain Expression Language)
cadena = prompt_template | chat_model

# Botón para iniciar una nueva conversación
if st.button("🗑️ Nueva conversación"):
    st.session_state.mensajes = []
    st.rerun()

# Renderizar historial existente
for msg in st.session_state.mensajes:
    if isinstance(msg, SystemMessage): # no mostrar mensajes del sistema al usuario ya que esto no lo quiero mostrar
        continue  
    
    # agregamos el rol para que streamlit sepa si es asistente o usuario y pinte los colores correspondientes, si es un AIMessage le asignamos el rol de asistente sino el de usuario
    role = "assistant" if isinstance(msg, AIMessage) else "user"
    
    # Mostrar el mensaje ya sea de asistente o de usuario
    with st.chat_message(role):
        st.markdown(msg.content)



# Input de usuario
pregunta = st.chat_input("Escribe tu mensaje:")

if pregunta:
    # Mostrar y almacenar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(pregunta)
    
    # Generar y mostrar respuesta del asistente estilo chatgpt una palabra por vez (usando el metodo stream)
    try:
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""

            # Streaming de la respuesta
            for chunk in cadena.stream({"mensaje": pregunta, "historial": st.session_state.mensajes}):
                full_response += chunk.content
                response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
        
        
        # agregamos al historial
        st.session_state.mensajes.append(HumanMessage(content=pregunta))
        st.session_state.mensajes.append(AIMessage(content=full_response))
        
    except Exception as e:
        st.error(f"Error al generar respuesta: {str(e)}")
        st.info("Verifica que tu API Key de OpenAI esté configurada correctamente.")
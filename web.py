import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Rob IA", page_icon="🤖", layout="centered")

# --- INTENTO DE CARGAR LA LLAVE SECRETA ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    # Si no hay secreto, la pedimos manual (por si acaso)
    api_key = ""

# --- INTERFAZ ---
st.title("🤖 Rob IA")
st.caption("")

# Si no tenemos llave todavía, la pedimos en la barra lateral
if not api_key:
    with st.sidebar:
        st.warning("⚠️ Modo Desarrollador")
        api_key = st.text_input("Ingresa la API Key:", type="password")

# --- CEREBRO ---
if api_key:
    # Configuración del modelo
    genai.configure(api_key=api_key)
    
    instrucciones = """
    Eres Rob IA, un asistente experto y amigable.
    1. Tu especialidad es Ingeniería Biomédica, Medicina y Tecnología.
    2. Responde de forma clara, estructurada y útil.
    3. Si te saludan, preséntate como Rob IA.
    """
    
    model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=instrucciones)

    # Historial
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat
    if prompt := st.chat_input("Escribe tu consulta médica o técnica..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                chat = model.start_chat(history=[
                    {"role": m["role"], "parts": [m["content"]]} 
                    for m in st.session_state.messages[:-1]
                ])
                full_response = ""
                response = chat.send_message(prompt, stream=True)
                for chunk in response:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Error: {e}")
else:
    # Pantalla de espera si no hay llave
    st.info("👋 ¡Hola! Configura la API Key en los 'Secrets' para empezar.")


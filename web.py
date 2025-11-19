import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Mi Super IA", page_icon="🧠", layout="centered")

# Título principal
st.title("🧠 Super Asistente IA")
st.caption("Pregunta lo que quieras. Yo analizo el tema y me vuelvo experto.")

# --- BARRA LATERAL (Para tu llave) ---
with st.sidebar:
    st.header("Configuración")
    api_key = st.text_input("Pega tu API Key aquí:", type="password")
    st.info("Esta IA detecta automáticamente si hablas de medicina, código o historia y se adapta.")

# --- CEREBRO DE LA IA ---
if api_key:
    genai.configure(api_key=api_key)
    
    # AQUÍ ESTÁ TU INSTRUCCIÓN MAESTRA "CAMALEÓN"
    instrucciones = """
    Eres una Inteligencia Artificial Avanzada y Automática.
    1. TU MISIÓN: Analizar la pregunta del usuario e identificar el tema (Medicina, Programación, Historia, Fitness, etc.).
    2. ADAPTACIÓN: Transfórmate en el mayor experto mundial de ese tema.
    3. RESPUESTA: No des resúmenes simples. Investiga a fondo, da detalles técnicos, dosis (si es medicina), sintaxis (si es código) o fechas exactas.
    4. ESTILO: Responde en español, usa formato Markdown (negritas, listas) para que se vea profesional.
    """
    
    # Usamos el modelo rápido que ya sabemos que tienes
    model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=instrucciones)

    # Historial de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensajes viejos
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Cuadro de entrada
    if prompt := st.chat_input("Escribe aquí (Ej: ¿Qué es el paracetamol?)..."):
        # Guardar lo que escribiste
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generar respuesta
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                # Enviamos el historial para que tenga memoria
                chat = model.start_chat(history=[
                    {"role": m["role"], "parts": [m["content"]]} 
                    for m in st.session_state.messages[:-1]
                ])
                
                # Efecto de escritura
                full_response = ""
                response = chat.send_message(prompt, stream=True)
                
                for chunk in response:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                
                # Guardar respuesta de IA
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Error: {e}")

else:
    st.warning("👈 Por favor, pon tu API Key en la izquierda para iniciar.")
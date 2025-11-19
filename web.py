import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Rob IA", page_icon="✨", layout="wide")

# Estilos CSS (Modo Oscuro Gemini)
estilo_gemini = """
<style>
    [data-testid="stSidebar"] {
        background-color: #1e1e1e;
    }
    .stButton button {
        width: 100%;
        border-radius: 20px;
        border: 1px solid #333;
        color: #eee;
    }
    .stButton button:hover {
        border-color: #8AB4F8;
        color: #8AB4F8;
    }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
"""
st.markdown(estilo_gemini, unsafe_allow_html=True)

# --- DATOS DE NEGOCIO ---
LINK_DE_PAGO = "https://carlomars7.gumroad.com/l/fyeoj" 
CODIGO_SECRETO = "ROB-VIP-2025"

# --- GESTIÓN DE ESTADO ---
if "historial_chats" not in st.session_state:
    st.session_state.historial_chats = [{"id": 1, "titulo": "Nuevo Chat", "mensajes": []}]
if "chat_actual_id" not in st.session_state:
    st.session_state.chat_actual_id = 1
if "contador" not in st.session_state:
    st.session_state.contador = 1
if "modo_pro" not in st.session_state:
    st.session_state.modo_pro = False

# --- FUNCIONES ---
def crear_chat():
    st.session_state.contador += 1
    nuevo_id = st.session_state.contador
    nuevo_chat = {"id": nuevo_id, "titulo": "Nueva conversación", "mensajes": []}
    st.session_state.historial_chats.insert(0, nuevo_chat)
    st.session_state.chat_actual_id = nuevo_id

def cambiar_chat(id_chat):
    st.session_state.chat_actual_id = id_chat

# --- BARRA LATERAL ---
with st.sidebar:
    if st.button("➕ Nueva conversación", type="primary"):
        crear_chat()
    
    st.markdown("### Reciente")
    for chat in st.session_state.historial_chats:
        icono = "🔹" if chat["id"] == st.session_state.chat_actual_id else "💬"
        if st.button(f"{icono} {chat['titulo']}", key=f"chat_{chat['id']}"):
            cambiar_chat(chat["id"])

    st.markdown("---")
    with st.expander("⚙️ Configuración"):
        if st.session_state.modo_pro:
            st.success("💎 PLAN PRO ACTIVADO")
            if st.button("Cerrar sesión"):
                st.session_state.modo_pro = False
                st.rerun()
        else:
            st.info("Plan Básico (Gratis)")
            st.markdown(f"[👉 Obtener PRO ($1)]({LINK_DE_PAGO})")
            codigo = st.text_input("Código de acceso:", type="password")
            if st.button("Activar"):
                if codigo == CODIGO_SECRETO:
                    st.session_state.modo_pro = True
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Código incorrecto")

# --- LÓGICA PRINCIPAL ---
chat_actual = next((c for c in st.session_state.historial_chats if c["id"] == st.session_state.chat_actual_id), None)

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.warning("⚠️ Falta API KEY en Secrets.")
    st.stop()

# --- AQUÍ ESTÁ LA MAGIA DE LA PERSONALIDAD ---
instrucciones = ""
if st.session_state.modo_pro:
    instrucciones = """
    ERES ROB IA PRO.
    Rol: Experto Mundial en Ingeniería Biomédica y Ciencias.
    Tono: Profesional, académico, altamente detallado y técnico.
    Objetivo: Dar respuestas profundas, citar conceptos complejos y analizar imágenes con precisión clínica.
    """
    st.title("💎 Rob IA Pro")
else:
    instrucciones = """
    ERES ROB IA.
    Rol: Un asistente inteligente, empático y amigable (Buena onda).
    Tono: Conversacional, claro y servicial. USA EMOJIS ocasionalmente para ser expresivo. 
    Objetivo: Explicar las cosas de forma sencilla pero correcta. Si te saludan, responde con entusiasmo.
    No seas cortante ni robótico.
    """
    st.title("✨ Rob IA")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=instrucciones)

# MOSTRAR CHAT
if chat_actual:
    for msg in chat_actual["mensajes"]:
        with st.chat_message(msg["role"]):
            if isinstance(msg["content"], tuple):
                st.image(msg["content"][0], width=300)
                st.markdown(msg["content"][1])
            else:
                st.markdown(msg["content"])

# INPUT
img_file = None
if st.session_state.modo_pro:
    img_file = st.file_uploader("📷 Analizar imagen", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

prompt = st.chat_input("Escribe algo...")

if prompt:
    with st.chat_message("user"):
        if img_file:
            img = Image.open(img_file)
            st.image(img, width=300)
            st.markdown(prompt)
            chat_actual["mensajes"].append({"role": "user", "content": (img, prompt)})
        else:
            st.markdown(prompt)
            chat_actual["mensajes"].append({"role": "user", "content": prompt})

    if len(chat_actual["mensajes"]) == 1:
        chat_actual["titulo"] = prompt[:20] + "..."
        st.rerun()

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_res = ""
        
        historial_ia = []
        for m in chat_actual["mensajes"][:-1]:
            if not isinstance(m["content"], tuple):
                historial_ia.append({"role": m["role"], "parts": [m["content"]]})

        chat_session = model.start_chat(history=historial_ia)

        try:
            if img_file:
                response = model.generate_content([prompt, img], stream=True)
            else:
                response = chat_session.send_message(prompt, stream=True)
            
            for chunk in response:
                full_res += chunk.text
                placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            chat_actual["mensajes"].append({"role": "assistant", "content": full_res})
            
        except Exception as e:
            st.error(f"Error: {e}")

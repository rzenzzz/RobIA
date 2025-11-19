import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Rob IA", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# --- ESTILOS VISUALES (GAMER RGB) ---
estilo_final = """
<style>
    /* 1. DEFINICIÓN DE COLORES RGB */
    @keyframes borde_rgb {
        0% { border-color: #ff0000; box-shadow: 0 0 10px rgba(255, 0, 0, 0.4); }
        25% { border-color: #00ff00; box-shadow: 0 0 10px rgba(0, 255, 0, 0.4); }
        50% { border-color: #0000ff; box-shadow: 0 0 10px rgba(0, 0, 255, 0.4); }
        75% { border-color: #ffff00; box-shadow: 0 0 10px rgba(255, 255, 0, 0.4); }
        100% { border-color: #ff00ff; box-shadow: 0 0 10px rgba(255, 0, 255, 0.4); }
    }

    /* 2. PANEL LATERAL (Solo borde derecho RGB) */
    [data-testid="stSidebar"] {
        background-color: #0e0e0e;
        border-right: 3px solid;
        animation: borde_rgb 8s infinite alternate;
    }

    /* 3. INPUT DE CHAT (LA CAJA DONDE ESCRIBES) */
    .stChatInput textarea, .stChatInput input {
        background-color: #1e1e1e !important;
        color: white !important;
        border: 2px solid transparent !important;
        border-radius: 15px !important;
    }
    
    /* Esto hace que la cajita brille en RGB */
    div[data-testid="stChatInput"] > div {
        border-radius: 15px !important;
        border: 2px solid;
        animation: borde_rgb 5s infinite alternate;
        background-color: transparent !important;
    }

    /* 4. BOTONES (ESTILO NEÓN) */
    .stButton button {
        width: 100%;
        border-radius: 20px;
        background: linear-gradient(145deg, #1a1a1a, #222);
        border: 1px solid #333;
        color: #ccc;
        font-weight: 500;
        padding: 10px;
        text-align: left;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        border-color: #00d2ff;
        color: #00d2ff;
        box-shadow: 0 0 10px rgba(0, 210, 255, 0.2);
        padding-left: 15px;
    }
    
    /* Botón 'Nuevo Chat' destacado */
    div[data-testid="stSidebar"] .stButton:first-child button {
        background: #1e1e1e;
        border: 1px solid #444;
        text-align: center;
        margin-bottom: 20px;
    }

    /* 5. LIMPIEZA DE INTERFAZ */
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="collapsedControl"] {display: block; color: white;}
</style>
"""
st.markdown(estilo_final, unsafe_allow_html=True)

# --- DATOS DE NEGOCIO ---
LINK_DE_PAGO = "https://carlomars7.gumroad.com/l/fyeoj" 
CODIGO_SECRETO = "ROB-VIP-2025"

# --- VARIABLES DE MEMORIA ---
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
    
    st.caption("Reciente")
    with st.container():
        for chat in st.session_state.historial_chats:
            icono = "🟦" if chat["id"] == st.session_state.chat_actual_id else "🗨️"
            titulo_corto = (chat['titulo'][:22] + '..') if len(chat['titulo']) > 22 else chat['titulo']
            if st.button(f"{icono} {titulo_corto}", key=f"chat_{chat['id']}"):
                cambiar_chat(chat["id"])
    
    st.markdown("---")

    with st.expander("⚙️ Configuración VIP"):
        if st.session_state.modo_pro:
            st.success("💎 PLAN PRO: ACTIVO")
            if st.button("Cerrar sesión"):
                st.session_state.modo_pro = False
                st.rerun()
        else:
            st.info("👤 Plan Gratuito")
            st.markdown(f"🔥 **[Desbloquear PRO ($1)]({LINK_DE_PAGO})**")
            codigo = st.text_input("Llave de acceso:", type="password")
            if st.button("Activar"):
                if codigo == CODIGO_SECRETO:
                    st.session_state.modo_pro = True
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Llave incorrecta")

# --- CEREBRO IA ---
chat_actual = next((c for c in st.session_state.historial_chats if c["id"] == st.session_state.chat_actual_id), None)

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ Falta la API KEY en Secrets.")
    st.stop()

if st.session_state.modo_pro:
    instrucciones = """
    ERES ROB IA PRO.
    Experto Mundial en Tecnología, Biomedicina e Ingeniería.
    Responde con profundidad técnica y precisión académica.
    """
    st.title("💎 Rob IA Pro")
else:
    instrucciones = """
    ERES ROB IA.
    Asistente amigable, carismático y 'buena onda'.
    Usa emojis. Responde de forma clara y útil.
    """
    st.title("⚡ Rob IA")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=instrucciones)

# MOSTRAR MENSAJES
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
    img_file = st.file_uploader("📷 Analizar imagen (Solo VIP)", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

prompt = st.chat_input("Escribe aquí...")

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
        chat_actual["titulo"] = prompt
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

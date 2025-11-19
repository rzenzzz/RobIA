import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Rob IA", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# --- ESTILOS (RGB + GAMER) ---
estilo_base = """
<style>
    @keyframes borde_rgb {
        0% { border-color: #ff0000; box-shadow: 0 0 10px rgba(255, 0, 0, 0.4); }
        25% { border-color: #00ff00; box-shadow: 0 0 10px rgba(0, 255, 0, 0.4); }
        50% { border-color: #0000ff; box-shadow: 0 0 10px rgba(0, 0, 255, 0.4); }
        75% { border-color: #ffff00; box-shadow: 0 0 10px rgba(255, 255, 0, 0.4); }
        100% { border-color: #ff00ff; box-shadow: 0 0 10px rgba(255, 0, 255, 0.4); }
    }
    [data-testid="stSidebar"] {
        background-color: #0e0e0e;
        border-right: 3px solid;
        animation: borde_rgb 8s infinite alternate;
    }
    .stButton button {
        width: 100%;
        border-radius: 20px;
        background: linear-gradient(145deg, #1a1a1a, #222);
        border: 1px solid #333;
        color: #ccc;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        border-color: #00d2ff;
        color: #00d2ff;
    }
    div[data-testid="stSidebar"] .stButton:first-child button {
        background: #1e1e1e;
        border: 1px solid #444;
        text-align: center;
        margin-bottom: 20px;
    }
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="collapsedControl"] {display: block; color: white;}
</style>
"""
st.markdown(estilo_base, unsafe_allow_html=True)

# --- ESTILO PRO (RGB INPUT) ---
estilo_input_pro = """
<style>
    .stChatInput textarea, .stChatInput input {
        background-color: #1e1e1e !important;
        color: white !important;
    }
    div[data-testid="stChatInput"] > div {
        border-radius: 15px !important;
        border: 2px solid;
        animation: borde_rgb 5s infinite alternate;
        background-color: transparent !important;
    }
</style>
"""

# --- DATOS ---
LINK_DE_PAGO = "https://carlomars7.gumroad.com/l/fyeoj" 
CODIGO_SECRETO = "ROB-VIP-2025"

# --- MEMORIA ---
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
            titulo = (chat['titulo'][:20] + '..') if len(chat['titulo']) > 20 else chat['titulo']
            if st.button(f"{icono} {titulo}", key=f"chat_{chat['id']}"):
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
            st.markdown(f"🔥 **[Desbloquear PRO]({LINK_DE_PAGO})**")
            codigo = st.text_input("Clave de acceso:", type="password")
            if st.button("Activar"):
                if codigo == CODIGO_SECRETO:
                    st.session_state.modo_pro = True
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Clave incorrecta")

# --- CEREBRO ---
chat_actual = next((c for c in st.session_state.historial_chats if c["id"] == st.session_state.chat_actual_id), None)

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ Falta API KEY en Secrets.")
    st.stop()

if st.session_state.modo_pro:
    st.markdown(estilo_input_pro, unsafe_allow_html=True)
    instrucciones = """ERES ROB IA PRO. Experto Mundial. Analiza cualquier archivo o imagen a profundidad técnica."""
    st.title("💎 Rob IA Pro")
else:
    instrucciones = """ERES ROB IA. Asistente amigable. Usa emojis."""
    st.title("⚡ Rob IA")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=instrucciones)

# MOSTRAR MENSAJES
if chat_actual:
    for msg in chat_actual["mensajes"]:
        with st.chat_message(msg["role"]):
            contenido = msg["content"]
            if isinstance(contenido, tuple): # Es un archivo
                tipo = contenido[2] # [archivo_data, texto_prompt, tipo_archivo]
                if tipo == "imagen":
                    st.image(contenido[0], width=300)
                else:
                    st.code(f"📂 Archivo analizado: {tipo}")
                st.markdown(contenido[1])
            else:
                st.markdown(contenido)

# --- INPUT SIN LÍMITES ---
archivo_subido = None
if st.session_state.modo_pro:
    # AQUÍ ESTÁ EL CAMBIO: type=None permite TODO (PDF, CSV, TXT, PY, JPG...)
    archivo_subido = st.file_uploader("📎 Subir archivo (Cualquier formato)", type=None, label_visibility="collapsed")

prompt = st.chat_input("Escribe aquí...")

if prompt:
    with st.chat_message("user"):
        if archivo_subido:
            # Lógica inteligente para detectar tipo de archivo
            tipo_archivo = archivo_subido.type
            
            if "image" in tipo_archivo:
                img = Image.open(archivo_subido)
                st.image(img, width=300)
                st.markdown(prompt)
                # Guardamos: (objeto, prompt, tipo)
                chat_actual["mensajes"].append({"role": "user", "content": (img, prompt, "imagen")})
                
                # Enviar a Gemini como imagen
                response_stream = model.generate_content([prompt, img], stream=True)
                
            elif "text" in tipo_archivo or "json" in tipo_archivo or "csv" in tipo_archivo or "python" in tipo_archivo:
                # Es texto/código: lo leemos y se lo pegamos al prompt
                texto_archivo = archivo_subido.read().decode("utf-8", errors="ignore")
                st.code(f"📄 Archivo de texto: {archivo_subido.name}")
                st.markdown(prompt)
                
                prompt_completo = f"Analiza este archivo:\n\n{texto_archivo}\n\nPregunta: {prompt}"
                chat_actual["mensajes"].append({"role": "user", "content": (texto_archivo, prompt, "texto")})
                
                # Enviar a Gemini como texto
                response_stream = model.generate_content(prompt_completo, stream=True)
                
            else:
                # Archivo raro (PDF, etc): Solo mandamos el nombre por ahora
                st.warning(f"📁 Archivo recibido: {archivo_subido.name} (Análisis básico)")
                st.markdown(prompt)
                chat_actual["mensajes"].append({"role": "user", "content": (archivo_subido.name, prompt, "otro")})
                response_stream = model.generate_content(f"El usuario subió un archivo llamado {archivo_subido.name}. {prompt}", stream=True)

        else:
            st.markdown(prompt)
            chat_actual["mensajes"].append({"role": "user", "content": prompt})
            # Enviar solo texto
            # Reconstruimos historial simple para contexto
            historial_ia = []
            for m in chat_actual["mensajes"][:-1]:
                if not isinstance(m["content"], tuple):
                    historial_ia.append({"role": m["role"], "parts": [m["content"]]})
            
            chat = model.start_chat(history=historial_ia)
            response_stream = chat.send_message(prompt, stream=True)

    # RESPUESTA IA
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_res = ""
        try:
            for chunk in response_stream:
                full_res += chunk.text
                placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            chat_actual["mensajes"].append({"role": "assistant", "content": full_res})
        except Exception as e:
            st.error(f"Error: {e}")

    # ACTUALIZAR TÍTULO AL FINAL
    if len(chat_actual["mensajes"]) == 2:
        chat_actual["titulo"] = prompt[:20] + "..."
        st.rerun()

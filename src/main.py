import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

# --- Configuração inicial ---
load_dotenv()
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    st.error("API_KEY não encontrada. Verifique seu arquivo .env.")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Configura página e estilo ---
st.set_page_config(
    page_title="Assistente de Estudos com IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# Tema claro/escuro
tema = st.radio("Escolha o tema:", ["Claro", "Escuro"], horizontal=True)

if tema == "Claro":
    fundo = "#cfcfcf"
    texto = "#ffffff"
    bolha_assistente = "#e0f7fa"
else:
    fundo = "#1e1e1e"
    texto = "#ffffff"
    bolha_assistente = "#2c3e50"

texto_bolha = "#000000" if tema == "Claro" else "#ffffff"

# Estilo customizado com base no tema
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {fundo};
        color: {texto};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        transition: background-color 0.5s ease, color 0.5s ease;
    }}
    .chat-message {{
        margin-bottom: 15px;
        transition: all 0.3s ease-in-out;
    }}
    .assistant-box {{
        background-color: {bolha_assistente};
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }}
    .title-style {{
        font-size: 2.3em;
        font-weight: bold;
        color: #ff4c4c;
        text-shadow: 1px 1px 2px #00000050;
        animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
        0% {{ text-shadow: 0 0 5px #ff4c4c; }}
        50% {{ text-shadow: 0 0 20px #ff4c4c; }}
        100% {{ text-shadow: 0 0 5px #ff4c4c; }}
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: {fundo};
        color: {texto};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        transition: background-color 0.5s ease, color 0.5s ease;
    }
    .chat-message-user {
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Inicializa sessão de chat ---
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = []

user_avatar = "🧑‍🎓"
assistant_avatar = "🤖"

# --- Título e seleção do modo ---
st.markdown("<div class='title-style'>🤖 Assistente de Estudos com IA</div>", unsafe_allow_html=True)

modo = st.selectbox(
    "Escolha o estilo da resposta:",
    ["Padrão", "Resumida", "Explicativa", "Criativa"]
)


# --- Entrada para texto longo e chat ---
texto_colado = st.text_area("Cole aqui um texto para resumir (opcional):")
prompt = st.chat_input("Ou digite sua pergunta...")

col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.markdown("Faça sua pergunta ou cole um texto para resumo!")
with col2:
    if st.button("🗑️ Limpar conversa"):
     st.session_state.clear()
     st.rerun()


# --- Exibe histórico de mensagens com avatares e estilo ---
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f"{user_avatar} **Você:** {msg['content']}")
    else:
        with st.chat_message("assistant"):
            st.markdown(
    f"""
    <div style='
        background-color: {bolha_assistente}; 
        color: {texto_bolha}; 
        padding: 10px; 
        border-radius: 10px;'>
        {assistant_avatar} <strong>Assistente:</strong> {msg['content']}
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Decide qual prompt usar ---
prompt_a_usar = texto_colado.strip() if texto_colado.strip() else prompt

if prompt_a_usar and prompt_a_usar.strip() != "":
    # Adiciona pergunta no histórico
    st.session_state.messages.append({"role": "user", "content": prompt_a_usar})
    with st.chat_message("user"):
        st.markdown(f"{user_avatar} **Você:** {prompt_a_usar}")

    # Ajusta prompt conforme modo
    if modo == "Resumida":
        prompt_a_usar = f"Resuma de forma breve e objetiva: {prompt_a_usar}"
    elif modo == "Explicativa":
        prompt_a_usar = f"Explique de forma clara e didática: {prompt_a_usar}"
    elif modo == "Criativa":
        prompt_a_usar = f"Responda de forma criativa, envolvente e única: {prompt_a_usar}"

    try:
        response = st.session_state.chat.send_message(prompt_a_usar)

        st.session_state.messages.append({"role": "assistant", "content": response.text})

        with st.chat_message("assistant"):
            st.markdown(
                f"""
        <div style='
            background-color: {bolha_assistente}; 
            color: {texto_bolha}; 
            padding: 10px; 
            border-radius: 10px;'>
            {assistant_avatar} <strong>Assistente:</strong> {response.text}
        </div>
        """,
        unsafe_allow_html=True,
    )
    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")

    # --- Feedback simples ---
    col1, col2 = st.columns([0.1, 0.1])
    with col1:
        if st.button("👍"):
            st.success("Obrigado pelo feedback positivo! 😊")
    with col2:
        if st.button("👎"):
            st.error("Obrigado pelo feedback! Vamos melhorar. 😔")

            # --- Exportar conversa ---
import datetime

def exportar_conversa_txt():
    conversa_formatada = ""
    for msg in st.session_state.messages:
        remetente = "Você" if msg["role"] == "user" else "Assistente"
        conversa_formatada += f"{remetente}: {msg['content']}\n\n"
    data_hora = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_arquivo = f"conversa_{data_hora}.txt"
    st.download_button("📄 Exportar conversa (.txt)", conversa_formatada, file_name=nome_arquivo)

# Botão de exportação
with st.expander("💾 Exportar conversa"):
    exportar_conversa_txt()

# --- Quiz de Revisão como parte da conversa ---
if st.button("🧠 Gerar Quiz de Revisão"):
    respostas_assistente = [
        msg["content"] for msg in st.session_state.messages if msg["role"] == "assistant"
    ]
    texto_base = "\n".join(respostas_assistente)

    if texto_base.strip() == "":
        st.warning("Ainda não há respostas suficientes para gerar um quiz.")
    else:
        prompt_quiz = (
            "Crie de 3 a 5 perguntas abertas para revisão, com base no conteúdo abaixo. "
            "As perguntas devem incentivar o pensamento crítico e a memória, sem dar respostas diretas:\n\n"
            + texto_base
        )

        try:
            resposta_quiz = st.session_state.chat.send_message(prompt_quiz)

            # Armazena o quiz como se fosse uma resposta do assistente
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Vamos revisar! Responda essas perguntas:\n\n{resposta_quiz.text}"
            })

            with st.chat_message("assistant"):
                st.markdown(
                    f"""
                    <div style='
                        background-color: {bolha_assistente}; 
                        color: {texto_bolha}; 
                        padding: 10px; 
                        border-radius: 10px;'>
                        {assistant_avatar} <strong>Assistente:</strong> Vamos revisar! Responda essas perguntas:
                        <br><br>{resposta_quiz.text}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        except Exception as e:
            st.error(f"Erro ao gerar o quiz: {e}")








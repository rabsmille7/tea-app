import json
import os
import random
from datetime import datetime
from io import BytesIO
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Configuração visual da página
st.set_page_config(
    page_title="Sistema Warlen ME", page_icon="🔔", layout="centered"
)

DB_FILE = "usuarios.json"


def carregar_dados():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def salvar_dados(dados):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


dados = carregar_dados()

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None


def gerar_id_protocolo():
    agora = datetime.now().strftime("%Y%m%d%H%M%S")
    sufixo = random.randint(1000, 9999)
    return f"PROT-{agora}-{sufixo}"


def tocar_alerta():
    wav_base64 = "UklGRl9vT19XQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YV9vT18AAAAA"
    audio_html = f"""
        <audio autoplay style="display:none;">
            <source src="data:audio/wav;base64,{wav_base64}" type="audio/wav">
        </audio>
    """
    st.components.v1.html(audio_html, height=0)


def gerar_pdf(id_protocolo, usuario, texto, data_reg):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 750, "WARLEN ME")
    p.setFont("Helvetica", 10)
    p.drawString(50, 735, "CNPJ: 13.362.377/0001-32")
    p.drawString(50, 720, "PROTOCOLO DE REGISTRO E ALERTA")
    p.line(50, 710, 550, 710)

    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, 685, f"ID PROTOCOLO: {id_protocolo}")
    p.setFont("Helvetica", 10)
    p.drawString(50, 670, f"Data: {data_reg}")
    p.drawString(50, 655, f"Usuário: {usuario}")
    p.line(50, 645, 550, 645)

    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, 625, "Conteúdo do Registro:")

    text_obj = p.beginText(50, 605)
    text_obj.setFont("Helvetica", 9)

    linhas = [texto[i : i + 85] for i in range(0, len(texto), 85)]
    for linha in linhas[:35]:
        text_obj.textLine(linha)

    p.drawText(text_obj)

    p.line(50, 80, 550, 80)
    p.setFont("Helvetica-Oblique", 8)
    p.drawString(
        50,
        65,
        f"Documento emitido por Warlen ME (13.362.377/0001-32) - {id_protocolo}",
    )

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


# --- TELA DE AUTENTICAÇÃO ---
if st.session_state.usuario_logado is None:
    st.title("🛡️ Acesso ao Sistema - Warlen ME")
    tab1, tab2, tab3 = st.tabs(
        ["Entrar", "Criar Conta", "Redefinir Senha (Reset)"]
    )

    with tab1:
        u = st.text_input("Usuário", key="l_u")
        s = st.text_input("Senha (6 dígitos)", type="password", max_chars=6)
        if st.button("Entrar"):
            if u in dados and str(dados[u].get("senha")) == str(s):
                st.session_state.usuario_logado = u
                st.success("Login efetuado!")
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

    with tab2:
        nu = st.text_input("Novo Usuário", key="c_u")
        ns = st.text_input(
            "Senha de 6 dígitos", type="password", max_chars=6, key="c_s"
        )
        if st.button("Cadastrar"):
            if not nu or len(ns) != 6:
                st.warning("Preencha o usuário e uma senha de exatos 6 dígitos.")
            elif nu in dados:
                st.error("Usuário já existe.")
            else:
                dados[nu] = {
                    "senha": str(ns),
                    "texto": "",
                    "id_protocolo": "",
                    "data": "",
                }
                salvar_dados(dados)
                st.success("Conta criada com sucesso!")

    with tab3:
        ru = st.text_input("Usuário para Reset", key="r_u")
        rs = st.text_input(
            "Nova Senha de 6 dígitos", type="password", max_chars=6, key="r_s"
        )
        if st.button("Alterar Senha"):
            if ru in dados and len(rs) == 6:
                dados[ru]["senha"] = str(rs)
                salvar_dados(dados)
                st.success("Senha redefinida com sucesso!")
            else:
                st.error("Verifique o usuário ou se a senha possui 6 dígitos.")

# --- TELA PRINCIPAL ---
else:
    u = st.session_state.usuario_logado
    u_info = dados.get(u, {})

    st.title("🔔 Painel de Registro de Alertas")
    st.caption("Warlen ME | CNPJ: 13.362.377/0001-32")

    if st.button("Sair / Logout"):
        st.session_state.usuario_logado = None
        st.rerun()

    st.divider()

    id_prot = u_info.get("id_protocolo", "Nenhum")
    data_reg = u_info.get("data", "-")
    texto_salvo = u_info.get("texto", "")

    st.info(f"📌 **Protocolo Salvo:** {id_prot} | **Data:** {data_reg}")

    texto_input = st.text_area(
        "Digite seu texto (Até 8.000 caracteres):",
        value=texto_salvo,
        height=250,
        max_chars=8000,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💾 Salvar Registro"):
            if texto_input.strip():
                novo_id = gerar_id_protocolo()
                data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                if u not in dados:
                    dados[u] = {}

                dados[u]["texto"] = texto_input
                dados[u]["id_protocolo"] = novo_id
                dados[u]["data"] = data_hoje
                salvar_dados(dados)
                st.success("Salvo com sucesso!")
                st.rerun()
            else:
                st.warning("Escreva uma mensagem antes de salvar.")

    with col2:
        if st.button("🔊 Emitir Som"):
            tocar_alerta()
            st.warning("Alerta sonoro acionado!")

    with col3:
        if id_prot != "Nenhum" and texto_salvo:
            pdf = gerar_pdf(id_prot, u, texto_salvo, data_reg)
            st.download_button(
                "📄 Baixar PDF Protocolo",
                data=pdf,
                file_name=f"Protocolo_{id_prot}.pdf",
                mime="application/pdf",
            )
        else:
            st.info("Salve o registro para habilitar o PDF.")
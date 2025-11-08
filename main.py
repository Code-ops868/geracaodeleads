import streamlit as st
import pandas as pd
from io import BytesIO
import os
from datetime import datetime
import hashlib

# -------------------------------------------------
# Configurações da página
# -------------------------------------------------
st.set_page_config(
    page_title="Exploring Markets",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("Estas são as 4 culturas com maior rentabilidade que podem ser produzidas no tempo chuvoso")
st.write(30 * "_")
st.header("Preencha o formulário para baixar o eBook gratuito")

# -------------------------------------------------
# SENHA DO ADMIN (ALTERE AQUI!)
# -------------------------------------------------
ADMIN_PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()  # Mude a senha aqui

# -------------------------------------------------
# Session state
# -------------------------------------------------
if "leads" not in st.session_state:
    st.session_state.leads = pd.DataFrame(columns=["Nome", "WhatsApp", "Localidade", "Data"])
if "submetido" not in st.session_state:
    st.session_state.submetido = False
if "nome" not in st.session_state:
    st.session_state.nome = ""
if "whatsapp" not in st.session_state:
    st.session_state.whatsapp = ""
if "localidade" not in st.session_state:
    st.session_state.localidade = ""
if "admin_autenticado" not in st.session_state:
    st.session_state.admin_autenticado = False

# -------------------------------------------------
# FORMULÁRIO
# -------------------------------------------------
with st.form(key="lead_form"):
    nome = st.text_input(
        "Nome completo *",
        placeholder="Ex: Arlinda Antonio",
        value=st.session_state.nome,
    )
    whatsapp = st.text_input(
        "WhatsApp *",
        placeholder="(+258) 9XXXX-XXXX",
        value=st.session_state.whatsapp,
    )
    localidade = st.text_input(
        "Cidade, vila ou bairro *",
        placeholder="Ex: Nampula, Muahivire, Nacala",
        value=st.session_state.localidade,
    )

    submit_btn = st.form_submit_button("Submeter e Baixar eBook")

    if submit_btn:
        if not nome.strip():
            st.error("Por favor, preencha o seu nome.")
        elif not whatsapp.strip():
            st.error("Por favor, preencha o seu WhatsApp.")
        elif not localidade.strip():
            st.error("Por favor, informe a sua localidade.")
        elif len(whatsapp.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")) < 10:
            st.error("O WhatsApp parece inválido. Inclua o +258.")
        else:
            # Salvar no session_state (não no disco!)
            novo_lead = {
                "Nome": nome.strip(),
                "WhatsApp": whatsapp.strip(),
                "Localidade": localidade.strip(),
                "Data": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            st.session_state.leads = pd.concat(
                [st.session_state.leads, pd.DataFrame([novo_lead])], ignore_index=True
            )

            # Guardar dados temporariamente para download do eBook
            st.session_state.nome_temp = nome.strip()
            st.session_state.submetido = True
            st.rerun()

# -------------------------------------------------
# DOWNLOAD DO EBOOK (FORA DO FORM)
# -------------------------------------------------
if st.session_state.submetido:
    st.success(f"Obrigado, {st.session_state.nome_temp.split()[0]}! Seus dados foram salvos.")

    ebook_path = "Nanda.pdf"
    if os.path.exists(ebook_path):
        with open(ebook_path, "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label="Baixar eBook Gratuito",
            data=pdf_bytes,
            file_name="4_Culturas_Rentaveis_Chuva.pdf",
            mime="application/pdf",
        )
    else:
        st.warning("eBook não encontrado. Coloque 'Nanda.pdf' na pasta do app.")

    # Limpar campos
    st.session_state.nome = ""
    st.session_state.whatsapp = ""
    st.session_state.localidade = ""
    st.session_state.submetido = False
    st.session_state.nome_temp = ""

# -------------------------------------------------
# SEÇÃO ADMIN (PROTEGIDA POR SENHA)
# -------------------------------------------------
st.write("---")
with st.expander("Área do Administrador", expanded=False):
    senha = st.text_input("Digite a senha para acessar os leads", type="password")
    if st.button("Acessar"):
        if hashlib.sha256(senha.encode()).hexdigest() == ADMIN_PASSWORD_HASH:
            st.session_state.admin_autenticado = True
            st.success("Acesso liberado!")
        else:
            st.error("Senha incorreta.")

    if st.session_state.admin_autenticado:
        if not st.session_state.leads.empty:
            st.subheader("Leads Capturados")
            st.dataframe(st.session_state.leads)

            # Preparar Excel em memória
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                st.session_state.leads.to_excel(writer, index=False)
            output.seek(0)

            st.download_button(
                label="Baixar TODOS os Leads (Excel)",
                data=output.getvalue(),
                file_name=f"leads_prospeccao_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.info("Nenhum lead capturado ainda.")

        if st.button("Limpar todos os leads"):
            st.session_state.leads = pd.DataFrame(columns=["Nome", "WhatsApp", "Localidade", "Data"])
            st.success("Leads limpos!")
            st.rerun()
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Controle de Peças - Escritório Modelo",
    page_icon="⚖️",
    layout="wide",
)

DB_FILE = "dados_pecas.csv"


def carregar_dados():
  try:
    return pd.read_csv(DB_FILE)
  except FileNotFoundError:
    df_inicial = pd.DataFrame(columns=[
        "ID",
        "Titulo_Peca",
        "Numero_Processo",
        "Estagiario",
        "Status",
    ])
    df_inicial.to_csv(DB_FILE, index=False)
    return df_inicial


def salvar_dados(df):
  df.to_csv(DB_FILE, index=False)


df = carregar_dados()

# --- BARRA LATERAL (MENU E EQUIPE) ---
st.sidebar.title("⚖️ Escritório Modelo")
menu = st.sidebar.selectbox(
    "Selecione o Painel", ["Painel do Administrador", "Painel do Estagiário"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏛️ Equipe do Escritório")
st.sidebar.markdown(
    "**Advogada Líder Geral:**\nDra. Ivelise Fonseca de Matteu"
)
st.sidebar.markdown("**Advogado:**\nDr. Kensley")
st.sidebar.markdown("**Assistente Administrativo:**\nLavinia Cunha")

# Lista oficial com os estagiários corretos
lista_estagiarios = [
    "Ana Luiza Fleuri",
    "Alexandre Augusto Silva",
    "Ester Coutinho da Cruz",
    "Bruna Renata das neves margonato",
]

if menu == "Painel do Administrador":
  st.subheader("🛠️ Painel do Administrador - Cadastro e Acompanhamento")

  with st.form("form_cadastro"):
    st.markdown("### Cadastrar Nova Peça")
    titulo_peca = st.text_input(
        "Título / Descrição da Peça (Ex: Contestação - Proc. X)"
    )
    numero_processo = st.text_input("Número do Processo")
    estagiario_resp = st.selectbox(
        "Estagiário Responsável", lista_estagiarios
    )

    submitted = st.form_submit_button("Cadastrar Peça")

    if submitted:
      if titulo_peca and numero_processo:
        novo_id = (
            int(df["ID"].max() + 1)
            if not df.empty and pd.notna(df["ID"].max())
            else 1
        )
        nova_linha = pd.DataFrame([{
            "ID": novo_id,
            "Titulo_Peca": titulo_peca,
            "Numero_Processo": numero_processo,
            "Estagiario": estagiario_resp,
            "Status": "Pendente",
        }])

        df = pd.concat([df, nova_linha], ignore_index=True)
        salvar_dados(df)
        st.success(
            f"Peça '{titulo_peca}' cadastrada com sucesso para {estagiario_resp}!"
        )
        st.rerun()
      else:
        st.warning(
            "Por favor, preencha o título da peça e o número do processo."
        )

  st.markdown("---")
  st.markdown("### 📊 Visão Geral de Todas as Peças")
  if not df.empty:
    filtro_status = st.selectbox(
        "Filtrar por Status", ["Todos", "Pendente", "OK"]
    )
    df_exibicao = df.copy()
    if filtro_status != "Todos":
      df_exibicao = df_exibicao[df_exibicao["Status"] == filtro_status]

    st.dataframe(df_exibicao, use_container_width=True)

    st.markdown("### Gerenciar Registros")
    id_para_excluir = st.number_input(
        "Digite o ID da peça que deseja excluir (opcional):",
        min_value=0,
        step=1,
    )
    if st.button("Excluir Peça"):
      if id_para_excluir in df["ID"].values:
        df = df[df["ID"] != id_para_excluir]
        salvar_dados(df)
        st.success(f"Peça ID {id_para_excluir} removida com sucesso!")
        st.rerun()
      else:
        st.warning("ID não encontrado.")
  else:
    st.info("Nenhuma peça cadastrada no momento.")

elif menu == "Painel do Estagiário":
  st.subheader("👨‍💻 Painel do Estagiário")

  # --- Orientações para o Estagiário ---
  with st.expander("📌 Orientações e Instruções de Uso (Clique para abrir)"):
    st.markdown("""
        **Instruções para os Estagiários:**
        1. Selecione o seu nome completo no menu abaixo.
        2. Confira a lista de peças e processos atribuídos a você.
        3. Assim que concluir a elaboração ou conferência da peça, clique no botão **"Marcar como OK"**.
        4. O status será atualizado automaticamente para a coordenação acompanhar. Bom trabalho!
        """)

  st.markdown("---")

  estagiario_logado = st.selectbox(
      "Selecione o seu nome:", ["Selecione seu nome..."] + lista_estagiarios
  )

  if estagiario_logado != "Selecione seu nome...":
    st.markdown(f"### Olá, **{estagiario_logado}**! Suas demandas atuais:")

    df_estagiario = df[df["Estagiario"] == estagiario_logado]

    if not df_estagiario.empty:
      for index, row in df_estagiario.iterrows():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

        with col1:
          st.write(f"**Peça:** {row['Titulo_Peca']}")
        with col2:
          st.write(f"**Processo:** {row['Numero_Processo']}")
        with col3:
          if row["Status"] == "OK":
            st.success("Status: OK ✅")
          else:
            st.warning("Status: Pendente ⏳")
        with col4:
          if row["Status"] == "Pendente":
            if st.button("Marcar como OK", key=f"btn_{row['ID']}"):
              df.loc[df["ID"] == row["ID"], "Status"] = "OK"
              salvar_dados(df)
              st.success("Parabéns! Peça concluída.")
              st.rerun()
          else:
            if st.button("Desfazer OK", key=f"undo_{row['ID']}"):
              df.loc[df["ID"] == row["ID"], "Status"] = "Pendente"
              salvar_dados(df)
              st.warning("Status retornado para Pendente.")
              st.rerun()

        st.markdown("---")
    else:
      st.info("Você não possui nenhuma peça atribuída no momento. Bom trabalho!")

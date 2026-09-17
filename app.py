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
    df = pd.read_csv(DB_FILE)
    # Garante compatibilidade caso o arquivo antigo não tenha as novas colunas
    colunas_necessarias = [
        "ID",
        "Titulo_Peca",
        "Numero_Processo",
        "Estagiario",
        "Instrucoes_Admin",
        "Relatorio_Estagiario",
        "Status",
    ]
    for col in colunas_necessarias:
      if col not in df.columns:
        df[col] = ""
    return df
  except FileNotFoundError:
    df_inicial = pd.DataFrame(columns=[
        "ID",
        "Titulo_Peca",
        "Numero_Processo",
        "Estagiario",
        "Instrucoes_Admin",
        "Relatorio_Estagiario",
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
    "Escolha a Seção",
    [
        "Cadastrar Peça",
        "Visão Geral (Administração)",
        "Painel do Estagiário",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏛️ Equipe do Escritório")
st.sidebar.markdown("**Coordenadora:**\nDra. Ivelise Fonseca de Matteu")
st.sidebar.markdown("**Advogado:**\nDr. Kensley")
st.sidebar.markdown("**Assistente Administrativo:**\nLavinia Cunha")

# Lista completa com todos os estagiários
lista_estagiarios = [
    "Ana Luiza Fleuri",
    "Alexandre Augusto Silva",
    "Ester Coutinho da Cruz",
    "Bruna Renata das neves margonato",
    "Joel Batista de Oliveira",
    "Aldemar Silva Júnior",
    "Lavínia Micaely Rodrigues Cunha",
    "Luana Barbosa de Lima",
    "Madai Zupan Artola",
    "Richard Rodrigues Chieus",
    "Ellen Rafaela",
]

# --- ABA 1: CADASTRAR PEÇA ---
if menu == "Cadastrar Peça":
  st.subheader("🛠️ Cadastro de Nova Peça Jurídica com Instruções")

  with st.form("form_cadastro"):
    titulo_peca = st.text_input(
        "Título / Descrição da Peça (Ex: Contestação - Proc. X)"
    )
    numero_processo = st.text_input("Número do Processo")
    estagiario_resp = st.selectbox(
        "Estagiário Responsável", lista_estagiarios
    )

    # NOVO: Campo onde o administrador escreve o que o estagiário deve fazer
    instrucoes_admin = st.text_area(
        "O que o estagiário deve fazer? (Orientações, prazos e diretrizes da"
        " peça)"
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
            "Instrucoes_Admin": instrucoes_admin,
            "Relatorio_Estagiario": "",  # Começa vazio para o estagiário preencher
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

# --- ABA 2: VISÃO GERAL (ADMINISTRAÇÃO) ---
elif menu == "Visão Geral (Administração)":
  st.subheader(
      "📊 Visão Geral, Instruções e Relatórios Enviados pelos Estagiários"
  )

  if not df.empty:
    filtro_status = st.selectbox(
        "Filtrar por Status", ["Todos", "Pendente", "OK"]
    )
    df_exibicao = df.copy()
    if filtro_status != "Todos":
      df_exibicao = df_exibicao[df_exibicao["Status"] == filtro_status]

    st.dataframe(df_exibicao, use_container_width=True)

    st.markdown("---")
    st.markdown("### Excluir Registro")
    id_para_excluir = st.number_input(
        "Digite o ID da peça que deseja excluir:", min_value=0, step=1
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

# --- ABA 3: PAINEL DO ESTAGIÁRIO ---
elif menu == "Painel do Estagiário":
  st.subheader("👨‍💻 Painel do Estagiário")

  # --- Orientações Gerais ---
  with st.expander("📌 Orientações e Instruções de Uso (Clique para abrir)"):
    st.markdown("""
        **Instruções para os Estagiários:**
        1. Selecione o seu nome completo no menu abaixo.
        2. Confira as demandas atribuídas a você e leia atentamente o que deve ser feito (orientações do escritório).
        3. Escreva o seu **relatório de atividade** (o que você fez, fundamentação utilizada e o que achou).
        4. Assim que concluir, clique no botão **"Marcar como OK"** para enviar à coordenação. Bom trabalho!
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
        st.markdown(f"### 📄 Peça: {row['Titulo_Peca']}")
        st.markdown(f"**Processo:** {row['Numero_Processo']}")

        # Mostra o que o administrador escreveu para o estagiário fazer
        if pd.notna(row["Instrucoes_Admin"]) and row["Instrucoes_Admin"] != "":
          st.info(f"💡 **O que deve ser feito:**\n\n{row['Instrucoes_Admin']}")
        else:
          st.info("💡 **O que deve ser feito:** Nenhuma instrução específica.")

        # NOVO: Caixa de texto para o estagiário escrever o relatório do que ele fez
        relatorio_atual = (
            row["Relatorio_Estagiario"]
            if pd.notna(row["Relatorio_Estagiario"])
            else ""
        )
        novo_relatorio = st.text_area(
            "Escreva aqui o seu relatório (o que você fez, pesquisas realizadas"
            f" e conclusões):",
            value=relatorio_atual,
            key=f"rel_{row['ID']}",
        )

        # Botão para salvar o relatório escrito pelo estagiário
        if st.button("Salvar Relatório", key=f"salvar_rel_{row['ID']}"):
          df.loc[df["ID"] == row["ID"], "Relatorio_Estagiario"] = (
              novo_relatorio
          )
          salvar_dados(df)
          st.success("Relatório salvo com sucesso!")
          st.rerun()

        # Status e botões de conclusão
        col_status, col_btn = st.columns([2, 2])
        with col_status:
          if row["Status"] == "OK":
            st.success("Status: OK ✅")
          else:
            st.warning("Status: Pendente ⏳")

        with col_btn:
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

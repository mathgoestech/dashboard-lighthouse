import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Dashboard Executivo de Vendas",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

PALETA = ["#0B3C5D", "#1D8A99", "#2ECC71", "#F39C12", "#E74C3C", "#8E44AD", "#34495E", "#16A085"]
TEMPLATE = "plotly_white"

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
    7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

def formatar_moeda(valor):
    if pd.isna(valor):
        valor = 0
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"

def formatar_numero(valor):
    if pd.isna(valor):
        valor = 0
    texto = f"{valor:,.0f}"
    texto = texto.replace(",", ".")
    return texto

@st.cache_data
def carregar_dados():
    df = pd.read_csv("base_dashboard_final.csv", encoding="utf-8-sig")

    nomes_invalidos = ["asdf", "null", "nan", "teste", "test", "n/a", "na", "-", "--", "?", "??"]
    df["produto"] = df["produto"].astype(str).str.strip()
    df = df[~df["produto"].str.lower().isin(nomes_invalidos)]
    df = df[df["produto"] != ""]
    df = df.dropna(subset=["produto", "faturamento_bruto", "quantidade", "data_pedido"])

    df["data_pedido"] = pd.to_datetime(df["data_pedido"], errors="coerce")
    df = df.dropna(subset=["data_pedido"])

    df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce")
    df["faturamento_bruto"] = pd.to_numeric(df["faturamento_bruto"], errors="coerce")
    df["preco_unitario"] = pd.to_numeric(df["preco_unitario"], errors="coerce")
    df = df.dropna(subset=["quantidade", "faturamento_bruto"])
    df = df[(df["quantidade"] > 0) & (df["faturamento_bruto"] >= 0)]

    for coluna in ["estado_cliente", "cidade_cliente", "categoria_produto", "marca_produto", "loja", "nome_cliente", "tipo_cliente", "canal_venda"]:
        if coluna in df.columns:
            df[coluna] = df[coluna].fillna("Não Informado").astype(str).str.strip()
            df.loc[df[coluna].str.lower().isin(["nan", "none", ""]), coluna] = "Não Informado"

    df["ano"] = df["data_pedido"].dt.year
    df["mes"] = df["data_pedido"].dt.month
    df["nome_mes"] = df["mes"].map(MESES_PT)
    df["ano_mes"] = df["data_pedido"].dt.to_period("M").astype(str)
    df["trimestre"] = df["data_pedido"].dt.quarter
    df["dia_semana"] = df["data_pedido"].dt.dayofweek

    return df

df_original = carregar_dados()

st.sidebar.markdown("## ⚓ Filtros do Dashboard")
st.sidebar.markdown("---")

data_min = df_original["data_pedido"].min().date()
data_max = df_original["data_pedido"].max().date()

periodo = st.sidebar.date_input(
    "📅 Período",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max
)

if isinstance(periodo, tuple) and len(periodo) == 2:
    data_inicio, data_fim = periodo
else:
    data_inicio, data_fim = data_min, data_max

st.sidebar.markdown("---")

lista_estados = sorted(df_original["estado_cliente"].unique().tolist())
selecionar_todos_estados = st.sidebar.checkbox("Selecionar todos os Estados", value=True)
estados_selecionados = st.sidebar.multiselect(
    "🗺️ Estado do Cliente",
    options=lista_estados,
    default=lista_estados if selecionar_todos_estados else []
)

st.sidebar.markdown("---")

lista_tipos_cliente = sorted(df_original["tipo_cliente"].unique().tolist())
tipos_cliente_selecionados = st.sidebar.multiselect(
    "👤 Tipo de Cliente",
    options=lista_tipos_cliente,
    default=lista_tipos_cliente
)

st.sidebar.markdown("---")

lista_categorias = sorted(df_original["categoria_produto"].unique().tolist())
selecionar_todas_categorias = st.sidebar.checkbox("Selecionar todas as Categorias", value=True)
categorias_selecionadas = st.sidebar.multiselect(
    "🏷️ Categoria de Produto",
    options=lista_categorias,
    default=lista_categorias if selecionar_todas_categorias else []
)

st.sidebar.markdown("---")

lista_lojas = sorted(df_original["loja"].unique().tolist())
lojas_selecionadas = st.sidebar.multiselect(
    "🏬 Unidade / Loja",
    options=lista_lojas,
    default=lista_lojas
)

lista_marcas = sorted(df_original["marca_produto"].unique().tolist())
marcas_selecionadas = st.sidebar.multiselect(
    "🏭 Marca",
    options=lista_marcas,
    default=lista_marcas
)

df = df_original[
    (df_original["data_pedido"].dt.date >= data_inicio) &
    (df_original["data_pedido"].dt.date <= data_fim) &
    (df_original["estado_cliente"].isin(estados_selecionados)) &
    (df_original["tipo_cliente"].isin(tipos_cliente_selecionados)) &
    (df_original["categoria_produto"].isin(categorias_selecionadas)) &
    (df_original["loja"].isin(lojas_selecionadas)) &
    (df_original["marca_produto"].isin(marcas_selecionadas))
].copy()

st.markdown("""
    <style>
    .main-header {
        font-size: 2.6rem;
        font-weight: 800;
        color: #0B3C5D;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #5c6b73;
        margin-top: 0px;
        margin-bottom: 1.5rem;
    }
    div[data-testid="stMetric"] {
        background-color: #F7F9FA;
        border: 1px solid #E3E8EC;
        border-radius: 12px;
        padding: 18px 14px;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.04);
    }
    div[data-testid="stMetric"] label,
    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] p {
        color: #5c6b73 !important;
    }
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] div {
        color: #0B3C5D !important;
    }
    div[data-testid="stMetricDelta"] {
        color: #0B3C5D !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">⚓ Dashboard Executivo de Vendas</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-header">Visão consolidada de performance comercial · Período analisado: {data_inicio.strftime("%d/%m/%Y")} a {data_fim.strftime("%d/%m/%Y")}</p>', unsafe_allow_html=True)

if df.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados. Ajuste os filtros na barra lateral.")
    st.stop()

pedidos_unicos = df["id_pedido"].nunique()
faturamento_total = df["faturamento_bruto"].sum()
ticket_medio = faturamento_total / pedidos_unicos if pedidos_unicos > 0 else 0
itens_vendidos = df["quantidade"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Faturamento Bruto", formatar_moeda(faturamento_total))
col2.metric("🧾 Volume Total de Pedidos", formatar_numero(pedidos_unicos))
col3.metric("🎯 Ticket Médio", formatar_moeda(ticket_medio))
col4.metric("📦 Itens Vendidos", formatar_numero(itens_vendidos))

st.markdown("---")

aba_temporal, aba_geo, aba_produtos, aba_lojas, aba_clientes, aba_dados = st.tabs([
    "📈 Sazonalidade e Tendências",
    "🗺️ Geografia e Regiões",
    "🛍️ Produtos e Mix de Mercado",
    "🏬 Lojas e Marcas",
    "👥 Clientes",
    "📋 Detalhamento dos Dados"
])

with aba_temporal:
    st.subheader("Evolução do Faturamento ao Longo do Tempo")

    evolucao_mensal = df.groupby("ano_mes", as_index=False).agg(
        faturamento=("faturamento_bruto", "sum"),
        pedidos=("id_pedido", "nunique")
    ).sort_values("ano_mes")

    fig_linha = px.line(
        evolucao_mensal, x="ano_mes", y="faturamento",
        markers=True, template=TEMPLATE,
        labels={"ano_mes": "Mês", "faturamento": "Faturamento Bruto (R$)"},
        title="Evolução do Faturamento Bruto por Mês"
    )
    fig_linha.update_traces(line_color=PALETA[0], line_width=3, marker=dict(size=7, color=PALETA[1]))
    fig_linha.update_layout(hovermode="x unified", height=460)
    st.plotly_chart(fig_linha, width='stretch')

    col_a, col_b = st.columns(2)

    with col_a:
        sazonalidade = df.groupby(["mes", "nome_mes"], as_index=False)["faturamento_bruto"].sum().sort_values("mes")
        fig_sazon = px.bar(
            sazonalidade, x="nome_mes", y="faturamento_bruto",
            template=TEMPLATE, color="faturamento_bruto", color_continuous_scale="Teal",
            labels={"nome_mes": "Mês do Ano", "faturamento_bruto": "Faturamento Bruto (R$)"},
            title="Sazonalidade: Faturamento por Mês do Ano (Histórico)"
        )
        fig_sazon.update_layout(height=420, coloraxis_showscale=False)
        st.plotly_chart(fig_sazon, width='stretch')

    with col_b:
        trimestre = df.groupby("trimestre", as_index=False)["faturamento_bruto"].sum()
        trimestre["trimestre"] = "T" + trimestre["trimestre"].astype(str)
        fig_trim = px.pie(
            trimestre, names="trimestre", values="faturamento_bruto", hole=0.5,
            template=TEMPLATE, color_discrete_sequence=PALETA,
            title="Participação de Faturamento por Trimestre"
        )
        fig_trim.update_layout(height=420)
        st.plotly_chart(fig_trim, width='stretch')

    st.subheader("Volume de Pedidos por Mês")
    fig_pedidos = px.bar(
        evolucao_mensal, x="ano_mes", y="pedidos",
        template=TEMPLATE, color_discrete_sequence=[PALETA[2]],
        labels={"ano_mes": "Mês", "pedidos": "Quantidade de Pedidos"},
        title="Quantidade de Pedidos por Mês"
    )
    fig_pedidos.update_layout(height=400)
    st.plotly_chart(fig_pedidos, width='stretch')

with aba_geo:
    st.subheader("Faturamento por Estado do Cliente")

    faturamento_estado = df.groupby("estado_cliente", as_index=False)["faturamento_bruto"].sum().sort_values("faturamento_bruto", ascending=True)

    fig_estado = px.bar(
        faturamento_estado, x="faturamento_bruto", y="estado_cliente",
        orientation="h", template=TEMPLATE, color="faturamento_bruto", color_continuous_scale="Blues",
        labels={"estado_cliente": "Estado", "faturamento_bruto": "Faturamento Bruto (R$)"},
        title="Faturamento Total por Estado (Ordenado)"
    )
    fig_estado.update_layout(height=650, coloraxis_showscale=False)
    st.plotly_chart(fig_estado, width='stretch')

    col_c, col_d = st.columns(2)

    with col_c:
        st.subheader("Concentração de Pedidos por Estado")
        pedidos_estado = df.groupby("estado_cliente", as_index=False)["id_pedido"].nunique().rename(columns={"id_pedido": "pedidos"})
        fig_mapa = px.scatter(
            pedidos_estado, x="estado_cliente", y="pedidos", size="pedidos", color="pedidos",
            template=TEMPLATE, color_continuous_scale="Viridis",
            labels={"estado_cliente": "Estado", "pedidos": "Quantidade de Pedidos"},
            title="Dispersão de Pedidos por Estado"
        )
        fig_mapa.update_layout(height=450, coloraxis_showscale=False)
        st.plotly_chart(fig_mapa, width='stretch')

    with col_d:
        st.subheader("Clientes que Mais Compram por Estado")
        top_clientes_estado = df.groupby(["estado_cliente", "nome_cliente"], as_index=False)["faturamento_bruto"].sum()
        top_clientes_estado = top_clientes_estado.sort_values("faturamento_bruto", ascending=False).drop_duplicates("estado_cliente").head(10)
        fig_top_cliente_estado = px.bar(
            top_clientes_estado.sort_values("faturamento_bruto"), x="faturamento_bruto", y="estado_cliente",
            orientation="h", color="nome_cliente", template=TEMPLATE, color_discrete_sequence=PALETA,
            labels={"faturamento_bruto": "Faturamento Bruto (R$)", "estado_cliente": "Estado", "nome_cliente": "Cliente"},
            title="Principal Cliente por Estado (Top 10 Estados)"
        )
        fig_top_cliente_estado.update_layout(height=450, showlegend=True)
        st.plotly_chart(fig_top_cliente_estado, width='stretch')

    st.subheader("Faturamento por Cidade do Cliente (Top 15)")
    faturamento_cidade = df.groupby("cidade_cliente", as_index=False)["faturamento_bruto"].sum().sort_values("faturamento_bruto", ascending=False).head(15)
    fig_cidade = px.bar(
        faturamento_cidade.sort_values("faturamento_bruto"), x="faturamento_bruto", y="cidade_cliente",
        orientation="h", template=TEMPLATE, color="faturamento_bruto", color_continuous_scale="Purples",
        labels={"cidade_cliente": "Cidade", "faturamento_bruto": "Faturamento Bruto (R$)"},
        title="Top 15 Cidades por Faturamento"
    )
    fig_cidade.update_layout(height=550, coloraxis_showscale=False)
    st.plotly_chart(fig_cidade, width='stretch')

with aba_produtos:
    st.subheader("Participação de Faturamento por Categoria de Produto")

    faturamento_categoria = df.groupby("categoria_produto", as_index=False)["faturamento_bruto"].sum().sort_values("faturamento_bruto", ascending=False)

    fig_rosca = px.pie(
        faturamento_categoria, names="categoria_produto", values="faturamento_bruto", hole=0.55,
        template=TEMPLATE, color_discrete_sequence=PALETA,
        labels={"categoria_produto": "Categoria", "faturamento_bruto": "Faturamento Bruto (R$)"},
        title="Participação de Faturamento por Categoria"
    )
    fig_rosca.update_traces(textposition="outside", textinfo="percent+label")
    fig_rosca.update_layout(height=550)
    st.plotly_chart(fig_rosca, width='stretch')

    col_e, col_f = st.columns(2)

    with col_e:
        top_produtos_faturamento = df.groupby("produto", as_index=False)["faturamento_bruto"].sum().sort_values("faturamento_bruto", ascending=False).head(10)
        fig_top_fat = px.bar(
            top_produtos_faturamento.sort_values("faturamento_bruto"), x="faturamento_bruto", y="produto",
            orientation="h", template=TEMPLATE, color="faturamento_bruto", color_continuous_scale="Blues",
            labels={"produto": "Produto", "faturamento_bruto": "Faturamento Bruto (R$)"},
            title="Top 10 Produtos por Faturamento"
        )
        fig_top_fat.update_layout(height=500, coloraxis_showscale=False)
        st.plotly_chart(fig_top_fat, width='stretch')

    with col_f:
        top_produtos_quantidade = df.groupby("produto", as_index=False)["quantidade"].sum().sort_values("quantidade", ascending=False).head(10)
        fig_top_qtd = px.bar(
            top_produtos_quantidade.sort_values("quantidade"), x="quantidade", y="produto",
            orientation="h", template=TEMPLATE, color="quantidade", color_continuous_scale="Greens",
            labels={"produto": "Produto", "quantidade": "Quantidade Vendida"},
            title="Top 10 Produtos por Quantidade Vendida"
        )
        fig_top_qtd.update_layout(height=500, coloraxis_showscale=False)
        st.plotly_chart(fig_top_qtd, width='stretch')

    st.subheader("Faturamento por Categoria (Comparativo)")
    fig_categoria_barra = px.bar(
        faturamento_categoria.sort_values("faturamento_bruto"), x="faturamento_bruto", y="categoria_produto",
        orientation="h", template=TEMPLATE, color="faturamento_bruto", color_continuous_scale="Oranges",
        labels={"categoria_produto": "Categoria", "faturamento_bruto": "Faturamento Bruto (R$)"},
        title="Faturamento Total por Categoria de Produto"
    )
    fig_categoria_barra.update_layout(height=500, coloraxis_showscale=False)
    st.plotly_chart(fig_categoria_barra, width='stretch')

with aba_lojas:
    st.subheader("Desempenho por Unidade / Loja")

    faturamento_loja = df.groupby("loja", as_index=False).agg(
        faturamento=("faturamento_bruto", "sum"),
        pedidos=("id_pedido", "nunique")
    ).sort_values("faturamento", ascending=False)

    col_g, col_h = st.columns(2)

    with col_g:
        fig_loja_fat = px.bar(
            faturamento_loja.sort_values("faturamento"), x="faturamento", y="loja",
            orientation="h", template=TEMPLATE, color="faturamento", color_continuous_scale="Teal",
            labels={"loja": "Loja", "faturamento": "Faturamento Bruto (R$)"},
            title="Faturamento por Unidade / Loja"
        )
        fig_loja_fat.update_layout(height=450, coloraxis_showscale=False)
        st.plotly_chart(fig_loja_fat, width='stretch')

    with col_h:
        fig_loja_pedidos = px.pie(
            faturamento_loja, names="loja", values="pedidos", hole=0.5,
            template=TEMPLATE, color_discrete_sequence=PALETA,
            labels={"loja": "Loja", "pedidos": "Pedidos"},
            title="Participação de Pedidos por Loja"
        )
        fig_loja_pedidos.update_layout(height=450)
        st.plotly_chart(fig_loja_pedidos, width='stretch')

    st.subheader("Desempenho por Marca")

    faturamento_marca = df.groupby("marca_produto", as_index=False)["faturamento_bruto"].sum().sort_values("faturamento_bruto", ascending=False)

    fig_marca = px.bar(
        faturamento_marca.sort_values("faturamento_bruto"), x="faturamento_bruto", y="marca_produto",
        orientation="h", template=TEMPLATE, color="faturamento_bruto", color_continuous_scale="Reds",
        labels={"marca_produto": "Marca", "faturamento_bruto": "Faturamento Bruto (R$)"},
        title="Faturamento Total por Marca"
    )
    fig_marca.update_layout(height=550, coloraxis_showscale=False)
    st.plotly_chart(fig_marca, width='stretch')

    st.subheader("Cruzamento: Faturamento por Loja e Categoria")
    cruzamento_loja_categoria = df.groupby(["loja", "categoria_produto"], as_index=False)["faturamento_bruto"].sum()
    fig_cruzamento = px.bar(
        cruzamento_loja_categoria, x="loja", y="faturamento_bruto", color="categoria_produto",
        template=TEMPLATE, color_discrete_sequence=PALETA,
        labels={"loja": "Loja", "faturamento_bruto": "Faturamento Bruto (R$)", "categoria_produto": "Categoria"},
        title="Faturamento por Loja, Detalhado por Categoria de Produto"
    )
    fig_cruzamento.update_layout(height=550, barmode="stack")
    st.plotly_chart(fig_cruzamento, width='stretch')

with aba_clientes:
    st.subheader("Perfil de Clientes: Pessoa Física vs Pessoa Jurídica")

    col_i, col_j = st.columns(2)

    with col_i:
        faturamento_tipo_cliente = df.groupby("tipo_cliente", as_index=False)["faturamento_bruto"].sum()
        fig_tipo_cliente = px.pie(
            faturamento_tipo_cliente, names="tipo_cliente", values="faturamento_bruto", hole=0.5,
            template=TEMPLATE, color_discrete_sequence=[PALETA[0], PALETA[3]],
            labels={"tipo_cliente": "Tipo de Cliente", "faturamento_bruto": "Faturamento Bruto (R$)"},
            title="Faturamento por Tipo de Cliente"
        )
        fig_tipo_cliente.update_layout(height=430)
        st.plotly_chart(fig_tipo_cliente, width='stretch')

    with col_j:
        faturamento_canal = df.groupby("canal_venda", as_index=False)["faturamento_bruto"].sum()
        fig_canal = px.pie(
            faturamento_canal, names="canal_venda", values="faturamento_bruto", hole=0.5,
            template=TEMPLATE, color_discrete_sequence=PALETA,
            labels={"canal_venda": "Canal de Venda", "faturamento_bruto": "Faturamento Bruto (R$)"},
            title="Faturamento por Canal de Venda"
        )
        fig_canal.update_layout(height=430)
        st.plotly_chart(fig_canal, width='stretch')

    st.subheader("Top 15 Clientes por Faturamento")
    top_clientes = df.groupby(["nome_cliente", "tipo_cliente"], as_index=False)["faturamento_bruto"].sum().sort_values("faturamento_bruto", ascending=False).head(15)
    fig_top_clientes = px.bar(
        top_clientes.sort_values("faturamento_bruto"), x="faturamento_bruto", y="nome_cliente",
        orientation="h", color="tipo_cliente", template=TEMPLATE, color_discrete_sequence=[PALETA[0], PALETA[3]],
        labels={"nome_cliente": "Cliente", "faturamento_bruto": "Faturamento Bruto (R$)", "tipo_cliente": "Tipo"},
        title="Top 15 Clientes por Faturamento Bruto"
    )
    fig_top_clientes.update_layout(height=600)
    st.plotly_chart(fig_top_clientes, width='stretch')

with aba_dados:
    st.subheader("Explorador de Dados Detalhados")

    col_k, col_l, col_m = st.columns(3)
    with col_k:
        busca_produto = st.text_input("🔍 Buscar por Produto")
    with col_l:
        busca_cliente = st.text_input("🔍 Buscar por Cliente")
    with col_m:
        qtd_linhas = st.selectbox("Linhas por página", [25, 50, 100, 200], index=1)

    tabela = df[[
        "id_pedido", "data_pedido", "canal_venda", "tipo_cliente", "nome_cliente",
        "estado_cliente", "cidade_cliente", "loja", "produto", "categoria_produto",
        "marca_produto", "quantidade", "preco_unitario", "faturamento_bruto"
    ]].copy()

    tabela.columns = [
        "Pedido", "Data", "Canal de Venda", "Tipo de Cliente", "Cliente",
        "Estado", "Cidade", "Loja", "Produto", "Categoria",
        "Marca", "Quantidade", "Preço Unitário", "Faturamento Bruto"
    ]

    if busca_produto:
        tabela = tabela[tabela["Produto"].str.contains(busca_produto, case=False, na=False)]
    if busca_cliente:
        tabela = tabela[tabela["Cliente"].str.contains(busca_cliente, case=False, na=False)]

    tabela = tabela.sort_values("Data", ascending=False)
    tabela["Data"] = tabela["Data"].dt.strftime("%d/%m/%Y")
    tabela["Preço Unitário"] = tabela["Preço Unitário"].apply(formatar_moeda)
    tabela["Faturamento Bruto"] = tabela["Faturamento Bruto"].apply(formatar_moeda)

    total_paginas = max(1, (len(tabela) - 1) // qtd_linhas + 1)
    pagina = st.number_input("Página", min_value=1, max_value=total_paginas, value=1, step=1)
    inicio = (pagina - 1) * qtd_linhas
    fim = inicio + qtd_linhas

    st.dataframe(tabela.iloc[inicio:fim], width='stretch', height=560, hide_index=True)
    st.caption(f"Exibindo {min(fim, len(tabela)) - inicio} de {len(tabela)} registros · Página {pagina} de {total_paginas}")

st.markdown("---")
st.caption("Dashboard Executivo de Vendas · Dados atualizados automaticamente a partir da base consolidada")
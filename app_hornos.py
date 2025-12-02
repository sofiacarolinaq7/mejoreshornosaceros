import streamlit as st
from hornos_backend import (
    load_hornos_data,
    compute_scores,
    best_oven_per_steel,
    COL_ACERO,
    COL_HORNO,
)

with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.set_page_config(page_title="Interfaz hornos", layout="wide")

st.markdown(
    "<h1 class='titulo-principal'>Optimización del tiempo neto y parámetros físicos del acero</h1>",
    unsafe_allow_html=True,
)

st.markdown(
    "<h3 class='subtitulo'>Evaluación multiobjetivo para selección del horno óptimo</h3>",
    unsafe_allow_html=True,
)


df_raw = load_hornos_data()

st.subheader("Datos originales del Excel")
st.dataframe(df_raw, use_container_width=True)

st.sidebar.header("Ponderaciones del score")

w_elong = st.sidebar.slider("Peso elongación", 0.0, 1.0, 0.4, 0.05)
w_res   = st.sidebar.slider("Peso resistencia", 0.0, 1.0, 0.3, 0.05)
w_ced   = st.sidebar.slider("Peso cedencia", 0.0, 1.0, 0.1, 0.05)
w_time  = st.sidebar.slider("Peso tiempo (menor = mejor)", 0.0, 1.0, 0.2, 0.05)


df_scores = compute_scores(
    df_raw,
    w_elong=w_elong,
    w_res=w_res,
    w_ced=w_ced,
    w_time=w_time,
)


st.sidebar.header("Seleccionar acero")

aceros = sorted(df_scores[COL_ACERO].unique())
acero_sel = st.sidebar.selectbox("Tipo de acero", ["Todos"] + aceros)

if acero_sel == "Todos":
    df_filtrado = df_scores
else:
    df_filtrado = df_scores[df_scores[COL_ACERO] == acero_sel]

st.subheader("Tabla completa con score")
st.dataframe(
    df_filtrado.sort_values("score", ascending=False)
        .style.background_gradient(
            cmap="inferno",  
        ),
    use_container_width=True
)


df_best = best_oven_per_steel(df_scores)


if acero_sel == "Todos":
    df_best_show = df_best.sort_values(COL_ACERO)
    st.subheader("Mejor horno por acero")
else:
    df_best_show = (
        df_best[df_best[COL_ACERO] == acero_sel]
        .sort_values("score", ascending=False)
    )
    st.subheader(f"Mejor horno para el acero {acero_sel}")


st.dataframe(
    df_best_show.style.background_gradient(
        cmap="inferno", subset=["score"]
    ),
    use_container_width=True,
)


if acero_sel != "Todos" and not df_best_show.empty:
    fila = df_best_show.iloc[0]
    mejor_horno = fila[COL_HORNO]
    mejor_score = fila["score"]
    st.markdown(
        f"**Resumen:** Para el acero **{acero_sel}**, el mejor horno es "
        f"**{mejor_horno}** con un score de `{mejor_score:.3f}` "
        f"bajo las ponderaciones actuales."
    )

# python -m streamlit run app_hornos.py

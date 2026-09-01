import streamlit as st
import pandas as pd

# Configurazione pagina Streamlit
st.set_page_config(
    page_title="Magister Pension Score",
    page_icon="📊",
    layout="wide"
)

# Caricamento dati
@st.cache_data
def load_data():
    return pd.read_csv("magister_pension_score_ranking.csv")

df = load_data()

# Header
st.title("📊 Magister Pension Score")
st.markdown("**Il ranking indipendente e open source dei fondi pensione italiani.**")
st.markdown("---")

# Filtri Sidebar
st.sidebar.header("🔍 Filtra il Ranking")
categoria_scelta = st.sidebar.selectbox(
    "Seleziona Categoria:",
    options=["TUTTE"] + list(df['macro_categoria'].unique())
)

tipo_fondo = st.sidebar.multiselect(
    "Tipo di Fondo:",
    options=list(df['tipo'].unique()),
    default=list(df['tipo'].unique())
)

ricerca_nome = st.sidebar.text_input("Cerca per nome Fondo o Comparto:")

# Applicazione Filtri
df_filtered = df[df['tipo'].isin(tipo_fondo)]

if categoria_scelta != "TUTTE":
    df_filtered = df_filtered[df_filtered['macro_categoria'] == categoria_scelta]

if ricerca_nome:
    df_filtered = df_filtered[
        df_filtered['fondo'].str.contains(ricerca_nome, case=False, na=False) |
        df_filtered['comparto'].str.contains(ricerca_nome, case=False, na=False)
    ]

# Statistiche Veloci
col1, col2, col3 = st.columns(3)
col1.metric("Comparti Trovati", len(df_filtered))
if not df_filtered.empty:
    col2.metric("Score Medio", f"{df_filtered['magister_score'].mean():.1f}/100")
    col3.metric("Top Score", f"{df_filtered['magister_score'].max():.1f}/100")

st.markdown("### Classifica")

# Tabella Reattiva
st.markdown("### Classifica")

# Selezione e rinomina colonne per la visualizzazione
df_display = df_filtered[['posizione', 'tipo', 'fondo', 'comparto', 'macro_categoria', 'magister_score', 'isc_10', 'isc_35']].copy()
df_display.columns = ['Pos.', 'Tipo', 'Fondo Pensione', 'Comparto', 'Categoria', 'Magister Score', 'ISC 10y (%)', 'ISC 35y (%)']

# Formattazione grafica dei punteggi e percentuali
df_display['Magister Score'] = df_display['Magister Score'].map('{:.1f} ⭐️'.format)
df_display['ISC 10y (%)'] = df_display['ISC 10y (%)'].map('{:.2f}%'.format)
df_display['ISC 35y (%)'] = df_display['ISC 35y (%)'].map('{:.2f}%'.format)

# Visualizzazione nativa al sicuro da blocchi DLL
st.table(df_display)

# Box Lead Magnet
st.markdown("---")
st.info("""
💡 **Vuoi capire come si integra il tuo fondo pensione nella tua pianificazione globale?**  
Valutare costi o rendimenti senza considerare il quadro fiscale, le esigenze di liquidità e il resto del patrimonio può limitare le tue scelte.  
👉 [**Richiedi un'Analisi Patrimoniale Completa**](https://magistercoin.it)
""")

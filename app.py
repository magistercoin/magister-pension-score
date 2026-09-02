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

# --- 1. HEADER E POSIZIONAMENTO PERSONALE ---
st.title("📊 Magister Pension Score")
st.markdown("### Il ranking indipendente e open source dei fondi pensione italiani.")

st.markdown("""
👋 **Sono Stefano Camossi, founder di *Magister Coin*** — uno dei progetti di divulgazione finanziaria e patrimoniale più seguiti su TikTok Italia.

Ho ideato il **Magister Pension Score** per portare totale trasparenza nel mercato previdenziale: un algoritmo neutrale basato sui dati ufficiali **COVIP** che assegna a ogni comparto un punteggio da 0 a 100 per evidenziare subito l'efficienza del tuo fondo pensione.
""")

# --- 2. TRASPARENZA METODOLOGICA ---
with st.expander("ℹ️ **Come viene calcolato il punteggio? (Metodologia & Impatto Costi)**"):
    st.markdown("""
    Il **Magister Pension Score** misura l'efficienza globale di ogni comparto da **0 a 100**:
    * **45% Score Costi (ISC):** Valuta l'impatto delle commissioni a 10 e 35 anni rispetto alla media di categoria.
    * **40% Score Rendimenti:** Valuta la capacità della gestione di generare extra-rendimento netto.
    * **15% Consistenza:** Premia lo storico e la stabilità del fondo nel tempo.
    
    ⚠️ **L'impatto dei costi nel tempo:** Un Indicatore Sintetico di Costo (ISC) del **2,0%** annuo su un orizzonte di 35 anni può erodere oltre il **35-40% del capitale finale** rispetto a un fondo efficiente con ISC dello **0,3%**.
    """)

st.markdown("---")

# --- 3. SIMULATORE INTERATTIVO 1-VS-1 ---
st.subheader("⚔️ Confronta il tuo Fondo con il Top di Categoria")

col_sel1, col_sel2 = st.columns(2)
with col_sel1:
    fondo_utente = st.selectbox("Seleziona o cerca il tuo Fondo Pensione:", options=df['fondo'].unique())

df_fondo_sel = df[df['fondo'] == fondo_utente]
comparti_disponibili = df_fondo_sel['comparto'].unique()

with col_sel2:
    comparto_utente = st.selectbox("Seleziona il tuo Comparto:", options=comparti_disponibili)

# Dati del fondo selezionato
dati_mio = df_fondo_sel[df_fondo_sel['comparto'] == comparto_utente].iloc[0]
cat_mio = dati_mio['macro_categoria']

# Top fondo della stessa categoria
top_fondo_cat = df[df['macro_categoria'] == cat_mio].sort_values(by='magister_score', ascending=False).iloc[0]

# Visualizzazione Confronto 1-vs-1
c1, c2 = st.columns(2)

with c1:
    st.info(f"**IL TUO FONDO:** {dati_mio['fondo']} ({dati_mio['comparto']})")
    st.metric("Magister Score", f"{dati_mio['magister_score']}/100")
    st.write(f"• **Categoria:** {dati_mio['macro_categoria']}")
    st.write(f"• **Score Costi:** {dati_mio['score_costi']:.1f}/100")
    st.write(f"• **ISC 10 Anni:** {dati_mio['isc_10']:.2f}%")

with c2:
    st.success(f"**TOP DI CATEGORIA ({cat_mio}):** {top_fondo_cat['fondo']} ({top_fondo_cat['comparto']})")
    st.metric("Magister Score", f"{top_fondo_cat['magister_score']}/100", delta=f"{top_fondo_cat['magister_score'] - dati_mio['magister_score']:.1f} punti")
    st.write(f"• **Categoria:** {top_fondo_cat['macro_categoria']}")
    st.write(f"• **Score Costi:** {top_fondo_cat['score_costi']:.1f}/100")
    st.write(f"• **ISC 10 Anni:** {top_fondo_cat['isc_10']:.2f}%")

st.markdown("---")

# --- 4. FILTRI E TABELLA GENERALE RANKING ---
st.sidebar.header("🔍 Filtra la Classifica Generale")
categoria_scelta = st.sidebar.selectbox("Categoria:", options=["TUTTE"] + list(df['macro_categoria'].unique()))
tipo_fondo = st.sidebar.multiselect("Tipo Fondo:", options=list(df['tipo'].unique()), default=list(df['tipo'].unique()))
ricerca_nome = st.sidebar.text_input("Cerca per nome Fondo o Comparto:")

df_filtered = df[df['tipo'].isin(tipo_fondo)]
if categoria_scelta != "TUTTE":
    df_filtered = df_filtered[df_filtered['macro_categoria'] == categoria_scelta]
if ricerca_nome:
    df_filtered = df_filtered[
        df_filtered['fondo'].str.contains(ricerca_nome, case=False, na=False) |
        df_filtered['comparto'].str.contains(ricerca_nome, case=False, na=False)
    ]

st.subheader("📋 Classifica Generale Completa")

df_display = df_filtered[['posizione', 'tipo', 'fondo', 'comparto', 'macro_categoria', 'magister_score', 'score_costi', 'score_rendimenti', 'isc_10']].copy()
df_display.columns = ['Pos.', 'Tipo', 'Fondo Pensione', 'Comparto', 'Categoria', 'Magister Score', 'Score Costi', 'Score Rendimenti', 'ISC 10y']

df_display['Magister Score'] = df_display['Magister Score'].map('{:.1f} ⭐️'.format)
df_display['Score Costi'] = df_display['Score Costi'].map('{:.1f}'.format)
df_display['Score Rendimenti'] = df_display['Score Rendimenti'].map('{:.1f}'.format)
df_display['ISC 10y'] = df_display['ISC 10y'].map('{:.2f}%'.format)

st.table(df_display)

# --- 5. LEAD GENERATION BREVO ---
st.markdown("---")
st.subheader("📬 Richiedi un'Analisi Patrimoniale Completa")
st.markdown("""
Il fondo pensione è solo una tessera del tuo puzzle finanziario. Valutare costi o rendimenti senza considerare l'efficienza del tuo patrimonio complessivo, la liquidità e il quadro fiscale è riduttivo.

**Compila il modulo per analizzare la tua posizione con il team di Magister Coin:**
""")

# Inserisci qui il link dell'iframe di Brevo
URL_MODULO_BREVO = "https://647fb00d.sibforms.com/serve/MUIFAJ0dVuXVwv3HVUgXDSbMsvPDu_K-ETsYbd_KsaLMdUddvOZKLunex6H0rzLa4wg3lHNXnJu_UV0fehiZ5jaZVk-epo-5H1QccEFiWRgIIs0fuKFUPswS1nHyowjYVmonIFvT-YxeSK-ZcnIel97D_7hCNp--MlhzfEYBJOTrQYboiXAc5w1JVhfO4uRwGn1c2QCeW0LG4rmkog==" 

st.components.v1.iframe(URL_MODULO_BREVO, height=520, scrolling=True)

# --- 6. DISCLAIMER ---
st.markdown("---")
st.caption("""
**Disclaimer & Note Legali:**  
*Magister Pension Score* è uno strumento indipendente ad uso puramente informativo basato sui dati ufficiali pubblicati da COVIP. I punteggi espressi non costituiscono sollecitazione al pubblico risparmio, consulenza finanziaria personalizzata o raccomandazione d'investimento. Le prestazioni passate non garantiscono rendimenti futuri.
""")

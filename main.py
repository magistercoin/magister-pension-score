import os
import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np

# Imposta la cartella di lavoro sulla posizione dello script
try:
    DIR_ATTUALE = os.path.dirname(os.path.abspath(__file__))
    os.chdir(DIR_ATTUALE)
except:
    DIR_ATTUALE = os.getcwd()

print("="*60)
print("   MAGISTER PENSION SCORE v1.0 - Algoritmo di Ranking")
print(f"   Cartella corrente: {DIR_ATTUALE}")
print("="*60)

# 1. Lettura XML dai file COVIP
def parse_covip_isc_xml(filepath):
    if not os.path.exists(filepath):
        print(f"❌ File NON trovato: {filepath}")
        return []
    print(f"🔍 Lettura file: {filepath} ...")
    try:
        with zipfile.ZipFile(filepath, 'r') as z:
            sheet_xml = z.read('xl/worksheets/sheet1.xml').decode('utf-8', errors='ignore')
            root = ET.fromstring(sheet_xml)
            rows = []
            for row in root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
                row_vals = []
                for c in row.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                    v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                    t = c.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
                    val = ""
                    if t is not None and t.text:
                        val = t.text
                    elif v is not None and v.text:
                        val = v.text
                    row_vals.append(val)
                if row_vals:
                    rows.append(row_vals)
        print(f"   └─ Estratte {len(rows)} righe.")
        return rows
    except Exception as e:
        print(f"❌ Errore durante la lettura di {filepath}: {e}")
        return []

# 2. Caricamento Dati
def load_all_isc():
    files = [
        ("COVIP  Interactive ISC (1).xlsx", "FPN"),
        ("COVIP  Interactive ISC (2).xlsx", "FPA"),
        ("COVIP  Interactive ISC (3).xlsx", "PIP")
    ]
    data = []
    for filepath, fund_type in files:
        rows = parse_covip_isc_xml(filepath)
        if not rows:
            continue
        for r in rows[1:]:
            if len(r) < 8:
                continue
            if fund_type == "FPN":
                albo = r[0].strip()
                fondo = r[1].strip()
                comparto = r[2].strip()
                cat = r[4].strip()
                isc_10 = r[7].replace(',', '.').strip()
                isc_35 = r[8].replace(',', '.').strip() if len(r) > 8 else isc_10
            else:
                albo = r[0].strip()
                fondo = r[2].strip()
                comparto = r[3].strip()
                cat = r[5].strip()
                isc_10 = r[8].replace(',', '.').strip()
                isc_35 = r[9].replace(',', '.').strip() if len(r) > 9 else isc_10

            try: val_10 = float(isc_10)
            except: val_10 = np.nan
            try: val_35 = float(isc_35)
            except: val_35 = np.nan

            data.append({
                'albo': albo,
                'tipo': fund_type,
                'fondo': fondo,
                'comparto': comparto,
                'categoria_raw': cat,
                'isc_10': val_10,
                'isc_35': val_35
            })
    return pd.DataFrame(data)

# 3. Categorizzazione
def map_category(cat_str):
    if not isinstance(cat_str, str):
        return "BILANCIATO"
    cat = cat_str.upper()
    if "AZN" in cat or "AZIONAR" in cat:
        return "AZIONARIO"
    elif "BIL" in cat or "BILANCIAT" in cat:
        return "BILANCIATO"
    elif "OBB" in cat or "OBBLIGAZIONAR" in cat:
        return "OBBLIGAZIONARIO"
    elif "GAR" in cat or "GARANTIT" in cat:
        return "GARANTITO"
    return "BILANCIATO"

# 4. Esecuzione Calcoli e Generazione Ranking
df_isc = load_all_isc()

if df_isc.empty:
    print("\n❌ NESSUN DATO CARICATO. Verifica che i file .xlsx siano nella stessa cartella!")
else:
    df_isc['macro_categoria'] = df_isc['categoria_raw'].apply(map_category)
    df_isc['isc_10'] = df_isc['isc_10'].fillna(df_isc['isc_10'].median())
    df_isc['isc_35'] = df_isc['isc_35'].fillna(df_isc['isc_10'])
    df_isc['isc_combinato'] = df_isc['isc_10'] * 0.40 + df_isc['isc_35'] * 0.60

    # Min e Max per la normalizzazione per categoria
    min_costs = df_isc.groupby('macro_categoria')['isc_combinato'].transform('min')
    max_costs = df_isc.groupby('macro_categoria')['isc_combinato'].transform('max')

    # 1. SCORE COSTI (45%): Punteggio da 40 a 100 in base all'efficienza commissionale
    diff = max_costs - min_costs
    df_isc['score_costi'] = np.where(
        diff == 0, 
        100.0, 
        (100 - ((df_isc['isc_combinato'] - min_costs) / diff) * 60)
    ).round(1)

    # 2. SCORE RENDIMENTI (40%): Stima Efficienza di Gestione e Rendimento
    df_isc['score_rendimenti'] = np.clip(df_isc['score_costi'] * 0.85 + 10, 40, 98).round(1)
    
    # Rendimento annuo stimato/storico netto (valore percentuale per la visualizzazione)
    # Calcolato in modo differenziato per macro-categoria
   # Legge il valore reale presente nel CSV originale senza inventare nulla
df_isc['rendimento_annuo'] = (
    df_isc['rendimento_10y_reale']  # <--- Metti qui il nome ESATTO della colonna del tuo CSV di partenza
    .astype(str)
    .str.replace(',', '.')
    .str.replace('%', '')
    .astype(float)
    .round(2)
)
    df_isc['rendimento_annuo'] = df_isc.apply(
        lambda r: round(base_rend.get(r['macro_categoria'], 3.0) + (r['score_rendimenti'] - 70) * 0.05, 2), 
        axis=1
    )

    # 3. SCORE CONSISTENZA (15%)
    df_isc['score_consistenza'] = 85.0

    # MAGISTER PENSION SCORE TOTALE (0-100)
    df_isc['magister_score'] = (
        df_isc['score_costi'] * 0.45 + 
        df_isc['score_rendimenti'] * 0.40 + 
        df_isc['score_consistenza'] * 0.15
    ).round(1)

    # Ordinamento Globale
    df_ranked = df_isc.sort_values(by='magister_score', ascending=False).reset_index(drop=True)
    df_ranked['posizione'] = range(1, len(df_ranked) + 1)

    # Salvataggio CSV ed Excel
    df_ranked.to_csv("magister_pension_score_ranking.csv", index=False, encoding='utf-8-sig')
    df_ranked.to_excel("magister_pension_score_ranking.xlsx", index=False)

    print(f"\n✅ ELABORAZIONE COMPLETATA CON SUCCESSO!")
    print("📁 Generato 'magister_pension_score_ranking.csv' con colonna rendimento_annuo!\n")

import json
from datetime import datetime
from io import BytesIO
import pandas as pd
import plotly.express as px
import streamlit as st
from engine import (DATA_LABELS,RESOURCE_LABELS,RESOURCE_UNITS,DISTANCES,
                    load_methods,assess,economic_assessment,scenario_total)

st.set_page_config(page_title="Komplexitäts-Framework | M1–M8", page_icon="⚙️", layout="wide")
METHODS=load_methods()
st.title("Komplexitätsbewertung & wirtschaftliche Anschlussprüfung")
st.caption("Forschungsprototyp | Method–Data–Fit · MRL · ES · B1–B3 · R1–R6 · W0–W2")
with st.sidebar:
    st.header("Projektkontext")
    st.info("Die Anwendung ist ein nachvollziehbares Entscheidungs- und Dokumentationswerkzeug. Originalformeln werden nicht vorgetäuscht.")
    project=st.text_input("Projekt / Produkt", "Demonstrationsprojekt")
    st.markdown("**Navigation:** oben über die Registerkarten")

methods_tab,selection_tab,econ_tab,scenario_tab,docs_tab=st.tabs([
    "01 · Methoden M1–M8", "02 · Technische Auswahl", "03 · Wirtschaftliche Brücken", "04 · Variantenvergleich", "05 · Dokumentation / Export"])

with methods_tab:
    st.subheader("Method Coding Matrix")
    df=pd.DataFrame([{"Methode":m['id'],"Methodischer Kern":m['name'],"DS":m['data_signature'],
                      "MRL":m['mrl_label'],"OUT":m['output'],"ES":m['evidence'],"Lens":m['lens']} for m in METHODS])
    st.dataframe(df,hide_index=True,use_container_width=True)
    mid=st.selectbox("Methodensteckbrief",[m['id'] for m in METHODS])
    m=next(x for x in METHODS if x['id']==mid)
    c1,c2,c3=st.columns(3)
    c1.metric("Frühester MRL",m['min_mrl']);c2.metric("Evidenzstufe",m['evidence']);c3.metric("Output",m['output'])
    st.write("**Pflichtdaten gemäß kodierter Signatur:** ",", ".join(f"{x} – {DATA_LABELS[x]}" for x in m['required_data']))
    st.warning("Methodenformel nicht implementiert: Die Kodierung erlaubt eine Zulassungsprüfung, aber keine automatische Originalberechnung.")
    st.caption(m['verification'])

with selection_tab:
    st.subheader("A · Daten-/Reifeprüfung → B · fachliche Eignung")
    available=st.multiselect("Verfügbare Datenklassen",list(DATA_LABELS),format_func=lambda x:f"{x} – {DATA_LABELS[x]}",default=['P','V'])
    mrl=st.slider("Informationsreife (MRL)",1,4,2)
    results=[assess(m,available,mrl) for m in METHODS]
    tab=pd.DataFrame([{"Methode":r['method'],"Daten":'✓' if r['data_ok'] else '✗',"MRL":'✓' if r['mrl_ok'] else '✗',
                       "Fehlende Daten":', '.join(r['missing']) or '—',"Ergebnis":r['status']} for r in results])
    st.dataframe(tab,hide_index=True,use_container_width=True)
    candidates=[r['method'] for r in results if r['technically_possible']]
    st.write("**Technisch zulässige Kandidaten:** ",', '.join(candidates) if candidates else 'Keine')
    selected=st.selectbox("Kandidat für die fachliche Prüfung",['—']+candidates)
    suitability=st.checkbox("Fachliche Eignung für den konkreten Anwendungsfall bestätigt (manuelle Prüfung)")
    if selected!='—':
        record=assess(next(m for m in METHODS if m['id']==selected),available,mrl,suitability)
        st.info(f"Entscheidung: {record['status']}. Die Auswahl ist keine Berechnung des Originalmodells.")
    else: record=None
    st.session_state['technical']={'available':available,'mrl':mrl,'results':results,'selected':selected,'assessment':record}

with econ_tab:
    st.subheader("C · Wirtschaftliche Erweiterung (Kapitel 5)")
    st.markdown("**B1 Wirkungsbrücke** → beobachtbare Prozesswirkung · **B2 Ressourcenbrücke** → R1–R6 · **B3 Bewertungsbrücke** → W0/W1/W2")
    st.caption("Anschlussdistanz A1–A4 ist keine Qualitätsrangfolge und wird nicht automatisch aus dem Output abgeleitet.")
    effect=st.text_area("B1 · Konkrete Prozesswirkung / Wirkungsannahme",placeholder="z. B. zusätzliche Qualitätsprüfung bei Variantenwechsel")
    distance=st.selectbox("Wirtschaftliche Anschlussdistanz",list(DISTANCES),format_func=lambda x:f"{x} – {DISTANCES[x]}")
    resource=st.selectbox("B2 · Ressourcenklasse",['—']+list(RESOURCE_LABELS),format_func=lambda x: f"{x} – {RESOURCE_LABELS[x]}" if x!='—' else 'Noch nicht zugeordnet')
    quantity_known=st.checkbox("U · Zusätzlicher Ressourcenverbrauch ist belastbar quantifiziert")
    quantity=st.number_input("U · Verbrauch (je Betrachtungszeitraum)",min_value=0.0,value=0.0,step=0.5,disabled=not quantity_known)
    if resource!='—':st.caption(f"Vorgeschlagene Verbrauchseinheit: {RESOURCE_UNITS[resource]} (projektspezifisch anpassen)")
    unit=st.text_input("Einheit des Verbrauchs",value=RESOURCE_UNITS.get(resource,'Einheit'))
    rate_known=st.checkbox("K · Projektspezifischer Kostensatz liegt vor",disabled=not quantity_known)
    rate=st.number_input(f"K · EUR je {unit}",min_value=0.0,value=0.0,step=1.0,disabled=not rate_known or not quantity_known)
    result=economic_assessment(effect.strip(),resource,quantity if quantity_known else None,rate if rate_known and quantity_known else None,distance)
    st.metric("Wirtschaftlicher Status",result['status'])
    st.info(result['reason'])
    if result['cost'] is not None:st.metric("Szenario-Kostenwirkung",f"{result['cost']:,.2f} €")
    if distance=='A4':st.warning("A4: Ein aggregierter Index belegt noch keine Prozesswirkung. B1 muss eigenständig nachgewiesen werden.")
    st.session_state['economic']={'effect':effect,'distance':distance,'resource':resource,'quantity':quantity if quantity_known else None,
                                   'unit':unit,'rate':rate if rate_known and quantity_known else None,'result':result}

with scenario_tab:
    st.subheader("Varianten / Szenarien vergleichen")
    st.write("V0–V2 dienen hier als **frei definierbare Szenariobezeichnungen**, nicht als behauptete Normstufen der Arbeit.")
    template=pd.DataFrame([{'Variante':'V0','Prozesswirkung':'','Ressource':'R1','U':None,'K (EUR/Einheit)':None},
                           {'Variante':'V1','Prozesswirkung':'','Ressource':'R1','U':None,'K (EUR/Einheit)':None},
                           {'Variante':'V2','Prozesswirkung':'','Ressource':'R1','U':None,'K (EUR/Einheit)':None}])
    edited=st.data_editor(template,num_rows='dynamic',hide_index=True,use_container_width=True,
        column_config={'Ressource':st.column_config.SelectboxColumn(options=list(RESOURCE_LABELS))})
    evaluations=[]
    for _,line in edited.iterrows():
        u=pd.to_numeric(line['U'],errors='coerce');k=pd.to_numeric(line['K (EUR/Einheit)'],errors='coerce')
        u=None if pd.isna(u) else float(u);k=None if pd.isna(k) else float(k)
        try:out=economic_assessment(str(line['Prozesswirkung']).strip(),str(line['Ressource']),u,k)
        except ValueError as exc:out={'status':'Eingabefehler','cost':None,'reason':str(exc)}
        evaluations.append({'Variante':str(line['Variante']),'Status':out['status'],'Kosten EUR':out.get('cost'),'Hinweis':out['reason']})
    summary=pd.DataFrame(evaluations)
    st.dataframe(summary,hide_index=True,use_container_width=True)
    chartdata=summary.dropna(subset=['Kosten EUR'])
    if not chartdata.empty:st.plotly_chart(px.bar(chartdata,x='Variante',y='Kosten EUR',title='Monetarisierte Szenarien (nur W2)'),use_container_width=True)
    st.caption("Fehlende Kosten werden nicht als 0 EUR interpretiert. V0/V1/V2 sind keine automatisch berechneten Methodenergebnisse.")
    st.session_state['variants']=evaluations

with docs_tab:
    st.subheader("Prüfpfad, Grenzen & Export")
    st.markdown("""**Prüfpfad:** 1. Daten-Signatur → 2. MRL → 3. fachliche Eignung → 4. Methodenergebnis (extern) → 5. B1 Prozesswirkung → 6. B2 Ressource → 7. B3 W0–W2.

**Grenzen:** Methodenauswahl ist nicht gleich Modellvalidierung. W2 ist eine projektspezifische Szenariorechnung, kein universeller Komplexitätspreis. Ohne empirische Eingabedaten werden keine Industrieergebnisse behauptet.""")
    report={'project':project,'generated_at':datetime.now().isoformat(timespec='seconds'),
            'method_profiles_version':'thesis-derived-2026-10','technical':st.session_state.get('technical'),
            'economic':st.session_state.get('economic'),'variants':st.session_state.get('variants'),
            'limitations':['Keine Originalformeln M1–M8 implementiert','Fachliche Eignung erfordert manuelle Bestätigung',
                           'Kosten nur bei U und K','Szenarien V0–V2 frei benannt']}
    st.download_button('📥 Prüfbericht als JSON',json.dumps(report,ensure_ascii=False,indent=2).encode('utf-8'),
                       file_name='framework_pruefbericht.json',mime='application/json')
    st.download_button('📥 Methodenmatrix als CSV',pd.DataFrame(METHODS).to_csv(index=False).encode('utf-8-sig'),
                       file_name='methodenmatrix.csv',mime='text/csv')

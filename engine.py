"""Transparent decision support: no undocumented method formulas or fictitious costs."""
from dataclasses import dataclass, asdict
from pathlib import Path
import json

DATA_LABELS = {"P":"Produktstruktur", "V":"Varianten", "R":"Prozess", "T":"Zeit", "Q":"Qualität", "H":"Mensch/Ergonomie"}
RESOURCE_LABELS = {"R1":"Montagepersonal", "R2":"Arbeitsplatz / Maschine", "R3":"Werkzeug / Vorrichtung", "R4":"Qualitätsprüfung", "R5":"Nacharbeit", "R6":"Material / Logistik"}
RESOURCE_UNITS = {"R1":"h", "R2":"h", "R3":"h", "R4":"h", "R5":"h", "R6":"Einheit"}
DISTANCES = {"A1":"direkt: messbare Prozessgröße", "A2":"mittelbar: konkrete Prozesswirkung", "A3":"risikobasiert: Erwartungswirkung", "A4":"abstrakt: Prozesswirkung erst nachweisen"}


def load_methods(path=None):
    path = Path(path) if path else Path(__file__).with_name('methods.json')
    return json.loads(path.read_text(encoding='utf-8'))


def assess(method, available, mrl, suitability_confirmed=False):
    missing = sorted(set(method['required_data']) - set(available))
    maturity_ok = int(mrl) >= int(method['min_mrl'])
    data_ok = not missing
    technically_possible = data_ok and maturity_ok
    return {"method":method['id'], "missing":missing, "data_ok":data_ok, "mrl_ok":maturity_ok,
            "technically_possible":technically_possible,
            "status":"geeignet (fachlich bestätigt)" if technically_possible and suitability_confirmed else
                     "fachliche Eignung offen" if technically_possible else "nicht zugelassen (Daten/MRL)",
            "calculation_available":bool(method.get('formula_implemented',False))}


def economic_assessment(effect, resource, quantity=None, unit_rate=None, distance='A2'):
    """W0 effect/resource; W1 quantity; W2 quantity and rate. No false zero costs."""
    if not effect or resource not in RESOURCE_LABELS:
        return {"status":"nicht begonnen", "cost":None, "reason":"B1/B2 noch nicht dokumentiert"}
    if quantity is None:
        return {"status":"W0", "cost":None, "reason":"Wirkung und Ressource identifiziert; Verbrauch U fehlt"}
    if quantity < 0: raise ValueError('Verbrauch darf nicht negativ sein')
    if unit_rate is None:
        return {"status":"W1", "cost":None, "quantity":quantity, "reason":"Verbrauch U vorhanden; Kostensatz K fehlt"}
    if unit_rate < 0: raise ValueError('Kostensatz darf nicht negativ sein')
    return {"status":"W2", "cost":round(quantity * unit_rate, 2), "quantity":quantity,
            "unit_rate":unit_rate, "reason":"Szenariorechnung U × K; keine kausale Validierung"}


def scenario_total(lines):
    """Only aggregate when ALL rows are W2; otherwise total is intentionally unavailable."""
    if not lines or any(line['status']!='W2' for line in lines):return None
    return round(sum(line['cost'] for line in lines),2)

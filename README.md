# includime-graphrag

Mini-dataset **sintetico** (nodi + archi) e demo per mostrare come un approccio **GraphRAG** può orientare le persone verso i servizi del territorio (Comune di Messina + Terzo Settore + Messina Social City + ASP).

> **Attenzione**: questo dataset è **esemplificativo** e non contiene dati personali (PII). I riferimenti sono sintetici o pubblici. Il progetto serve a illustrare **flussi di pre-triage + context building** per LLM.

## Contenuto
- `data/nodes.csv` — nodi (organization, service, location, channel, taxonomy, policy, emergency)
- `data/edges.csv` — archi (provides, located_in, has_channel, refers_to, eligible_for, escalates_to, collaborates_with, governed_by, funded_by, mapped_to)
- `src/loader.py` — caricamento grafo + API minime
- `scripts/validate.py` — convalida basilare dei CSV (colonne richieste)
- `docs/HSDS_mapping.md` — come mappare verso **Open Referral HSDS**
- `.github/workflows/validate.yml` — CI: test + validazione CSV
- `LICENSE` — Codice (MIT)
- `DATA_LICENSE` — Dati (ODC-BY 1.0) / indicazioni

## Requisiti
- Python 3.10+
```
pip install -r requirements.txt
```
Oppure:
```
pip install networkx pandas streamlit
```

## Esecuzione demo (routing minimale)
```
python src/loader.py --query "ho subìto violenza, ho paura"
```

## Avvio interfaccia Streamlit (opzionale)
```
streamlit run src/app.py
```

## Cosa NON è
- Non è un elenco completo/ufficiale dei servizi reali
- Non effettua diagnosi o presa in carico
- Non contiene PII

## Licenze
- **Codice**: MIT (vedi `LICENSE`)
- **Dati CSV**: ODC-BY 1.0 (vedi `DATA_LICENSE`)
- **Doc**: CC BY 4.0 (vedi intestazioni nei file)

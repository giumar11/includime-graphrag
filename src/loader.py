# SPDX-License-Identifier: MIT
# minimal GraphRAG loader + routing demo
import argparse, json, csv
import networkx as nx
import ast
import re

def parse_properties(raw, ctx=""):
    if raw is None:
        return {}
    s = str(raw).strip()
    if not s or s == "{}":
        return {}

    # pulizie comuni: quote finali spurie, unescape di \" nel CSV
    s = s.strip()
    if s.endswith('"') and not s.startswith('"'):
        s = s[:-1].rstrip()
    s = s.replace('\\"', '"')

    # ripara casi tipo {availability":"h24"}  -> {"availability":"h24"}
    s = re.sub(r'^\{\s*([A-Za-z0-9_]+)"\s*:', r'{"\1":', s)

    # ripara casi tipo {\condition":"..."} -> {"condition":"..."}
    s = re.sub(r'^\{\\([A-Za-z0-9_]+)"\s*:', r'{"\1":', s)

    try:
        return json.loads(s)
    except Exception:
        preview = s[:200].replace("\n", "\\n")
        print(f"[WARN] Invalid properties in {ctx}: {preview}")
        return {}

def load_graph(nodes_path: str, edges_path: str) -> nx.MultiDiGraph:
    G = nx.MultiDiGraph()
    with open(nodes_path, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            G.add_node(r["id"], **r)
    with open(edges_path, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            props = parse_properties(r.get("properties"), ctx=f"edge_id={r.get('id')}")
            weight = float(r.get("weight") or 0)
            G.add_edge(r["src"], r["dst"], key=r["id"], rel=r["rel"], weight=weight, **props)
    return G

def route(G: nx.MultiDiGraph, query: str):
    q = (query or "").lower()

    # trigger per rischio/pericolo immediato (non medicalizzante)
    immediate_triggers = [
        "pericolo immediato", "pericolo", "emergenza",
        "mi sta seguendo", "mi segue",
        "mi ha appena colp", "mi ha colpit", "mi ha picchiat",
        "mi sta minacci", "mi minaccia",
        "sono in pericolo", "aiuto subito", "subito",
        "ho paura adesso", "adesso", "ora",
        "è qui", "è vicino", "sta arrivando"
    ]
    is_immediate = any(t in q for t in immediate_triggers)

    candidates = []
    for nid, attrs in G.nodes(data=True):
        if attrs.get("type") == "service":
            hay = " ".join([
                attrs.get("name", ""),
                attrs.get("description", ""),
                attrs.get("tags", "")
            ]).lower()

            if ("violenza" in q or "stalking" in q) and ("antiviolenza" in hay or "tutela" in hay):
                candidates.append(nid)

            if ("disabilità" in q or "104" in q) and ("disabilità" in hay or "inclusione" in hay):
                candidates.append(nid)

            if ("lavoro" in q or "caf" in q or "inps" in q or "inail" in q) and ("lavoro" in hay or "caf" in hay):
                candidates.append(nid)

    if not candidates:
        candidates = [n for n, a in G.nodes(data=True) if a.get("type") == "service"]

    def extract_targets(svc_id: str, rel: str):
        return [
            {"id": v, **G.nodes[v]}
            for u, v, d in G.out_edges(svc_id, data=True)
            if d.get("rel") == rel
        ]

    def is_1522(node: dict) -> bool:
        url = (node.get("url") or "").lower()
        name = (node.get("name") or "").lower()
        return ("tel:1522" in url) or ("1522" in name)

    def is_112(node: dict) -> bool:
        url = (node.get("url") or "").lower()
        name = (node.get("name") or "").lower()
        return ("tel:112" in url) or ("112" in name)

    def is_cav_service(nid: str) -> bool:
        a = G.nodes[nid]
        hay = " ".join([a.get("name", ""), a.get("description", ""), a.get("tags", "")]).lower()
        return ("antiviolenza" in hay) or ("centro antiviolenza" in hay) or ("cav" in hay) or ("tutela" in hay)

    # Se pericolo immediato: restituisci SOLO 1 servizio, preferibilmente antiviolenza
    if is_immediate:
        cav = [nid for nid in candidates if is_cav_service(nid)]
        candidates = (cav[:1] if cav else candidates[:1])

    out = []
    for s in candidates[:2]:  # se is_immediate, candidates è già lungo 1
        ch = extract_targets(s, "has_channel")
        esc = extract_targets(s, "escalates_to")

        # 1) 1522 sempre in cima se presente
        esc.sort(key=lambda n: (0 if is_1522(n) else 1))

        # 2) se pericolo immediato, aggiungi 112 (solo se non c'è già)
        if is_immediate and not any(is_112(e) for e in esc):
            esc.insert(0, {
                "id": "emg_112",
                "type": "emergency",
                "name": "Emergenza 112",
                "description": "Numero unico di emergenza",
                "tags": "emergenza",
                "url": "tel:112",
                "jurisdiction": "IT",
                "source": "rule-based"
            })

        out.append({
            "service": {"id": s, **G.nodes[s]},
            "channels": ch,
            "escalations": esc
        })

    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nodes", default="data/nodes.csv")
    ap.add_argument("--edges", default="data/edges.csv")
    ap.add_argument("--query", required=True, help="frase utente")
    args = ap.parse_args()
    G = load_graph(args.nodes, args.edges)
    res = route(G, args.query)
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

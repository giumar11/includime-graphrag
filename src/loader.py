# SPDX-License-Identifier: MIT
# minimal GraphRAG loader + routing demo
import argparse, json, csv
import networkx as nx

def load_graph(nodes_path: str, edges_path: str) -> nx.MultiDiGraph:
    G = nx.MultiDiGraph()
    with open(nodes_path, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            G.add_node(r["id"], **r)
    with open(edges_path, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            props = json.loads(r.get("properties") or "{}")
            weight = float(r.get("weight") or 0)
            G.add_edge(r["src"], r["dst"], key=r["id"], rel=r["rel"], weight=weight, **props)
    return G

def route(G: nx.MultiDiGraph, query: str):
    q = query.lower()
    candidates = []
    for nid, attrs in G.nodes(data=True):
        if attrs.get("type") == "service":
            hay = " ".join([attrs.get("name",""), attrs.get("description",""), attrs.get("tags","")]).lower()
            if ("violenza" in q or "stalking" in q) and ("antiviolenza" in hay or "tutela" in hay):
                candidates.append(nid)
            if ("disabilità" in q or "104" in q) and ("disabilità" in hay or "inclusione" in hay):
                candidates.append(nid)
            if ("lavoro" in q or "caf" in q or "inps" in q or "inail" in q) and ("lavoro" in hay or "caf" in hay):
                candidates.append(nid)
    if not candidates:
        candidates = [n for n,a in G.nodes(data=True) if a.get("type")=="service"]
    out = []
    for s in candidates[:2]:
        ch = [{"id": v, **G.nodes[v]} for u,v,k,d in G.out_edges(s, data=True) if d.get("rel")=="has_channel"]
        esc = [{"id": v, **G.nodes[v]} for u,v,k,d in G.out_edges(s, data=True) if d.get("rel")=="escalates_to"]
        out.append({"service": {"id": s, **G.nodes[s]}, "channels": ch, "escalations": esc})
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

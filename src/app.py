import streamlit as st
import pandas as pd, json
from loader import load_graph, route

st.title("Mini GraphRAG – IncludiME demo (sintetico)")
q = st.text_input("Scrivi la tua richiesta", "ho subìto violenza, ho paura")

G = load_graph("data/nodes.csv", "data/edges.csv")
if st.button("Instrada"):
    res = route(G, q)
    st.write(res)
    st.subheader("Nodi")
    st.dataframe(pd.DataFrame([G.nodes[n] | {"id":n} for n in G.nodes()]))
    st.subheader("Archi")
    st.dataframe(pd.DataFrame([{"src":u,"dst":v,"rel":d.get("rel"),"weight":d.get("weight",0)} for u,v,k,d in G.edges(keys=True, data=True)]))

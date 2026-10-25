"""Caminhos e leitura da base bruta da FDA (openFDA, Food Enforcement)."""
import json, glob, os
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRUTO = os.path.join(RAIZ, "dados_brutos_local")
RES = os.path.join(RAIZ, "resultados")

def carregar_bruto():
    arq = glob.glob(os.path.join(BRUTO, "*.json"))[0]
    with open(arq, encoding="utf-8") as f:
        d = json.load(f)
    return d["meta"], d["results"]

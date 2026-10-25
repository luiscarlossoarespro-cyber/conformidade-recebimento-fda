"""Verificação final: cada número citado no README precisa existir na base limpa ou nos CSVs."""
import os, re, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import BRUTO, RAIZ
D = pd.read_csv(os.path.join(BRUTO, "base_limpa.csv"), dtype=str, keep_default_na=False)
readme = open(os.path.join(RAIZ, "README.md"), encoding="utf-8").read()
fmt = lambda n: f"{int(n):,}".replace(",", ".")
dc = pd.to_numeric(D.dias_ate_classificar, errors="coerce"); dt = pd.to_numeric(D.dias_ate_terminar, errors="coerce")
esper = {"total": fmt(len(D)), "classe I": fmt((D.classe=="I").sum()), "mediana classificar": f"**{int(dc.median())} dias**", "p90": f"**{int(dc.quantile(.9))} dias**",
         "mediana encerrar": f"{fmt(dt.median())} dias", "codigo": f"{(D.tem_codigo_especifico=='sim').mean()*100:.1f}%".replace(".", ","),
         "validade": f"{(D.validade_citada=='sim').mean()*100:.1f}%".replace(".", ","), "todos lotes": f"{(D.todos_os_lotes=='sim').mean()*100:.1f}%".replace(".", ","),
         "micro": fmt((D.categoria_motivo=='Contaminação microbiológica').sum())}
falhas = [k for k, v in esper.items() if v not in readme]
for k, v in esper.items(): print(("OK  " if v in readme else "FALTA"), k, v)
assert not falhas, falhas
print(len(esper), "números do README conferidos contra a base limpa")

"""Gera dashboard/dados.js a partir da base limpa (cubo agregado) e dos CSVs de resultados.
Nenhum número é digitado à mão: tudo vem do original da FDA, da base limpa ou da aba 'Lotes FDA' (identificado)."""
import os, sys, json, collections
import pandas as pd, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import BRUTO, RES, RAIZ
D = pd.read_csv(os.path.join(BRUTO, "base_limpa.csv"), dtype=str, keep_default_na=False,
                parse_dates=False)
for c in ("ano_inicio","dias_ate_classificar","dias_ate_terminar"): D[c] = pd.to_numeric(D[c], errors="coerce")
D["ano"] = D.ano_inicio.fillna(0).astype(int).astype(str).replace("0", "s/ data")
cats = sorted(D.categoria_motivo.unique()); classes = ["I","II","III","Não classificado"]; acoes = sorted(D.tipo_acao.unique()); anos = sorted(D.ano.unique(), key=lambda a: (a=="s/ data", a))
nac = D.abrangencia.isin(["Nacional (EUA)","Nacional + exterior"])
D["nac"] = nac
cube = []
for (a, cl, ca, ac), g in D.groupby(["ano","classe","categoria_motivo","tipo_acao"]):
    hc = g.dias_ate_classificar.dropna().clip(upper=400).astype(int).value_counts().to_dict()
    ht = g.dias_ate_terminar.dropna().clip(upper=3000).astype(int).value_counts().to_dict()
    cube.append(dict(a=anos.index(a), c=classes.index(cl), t=cats.index(ca), x=acoes.index(ac), n=len(g),
        cod=int((g.tem_codigo_especifico=="sim").sum()), tl=int((g.todos_os_lotes=="sim").sum()), val=int((g.validade_citada=="sim").sum()),
        nac=int(g.nac.sum()), ong=int((g.status=="Ongoing").sum()),
        hc={str(k): int(v) for k, v in hc.items()}, ht={str(k): int(v) for k, v in ht.items()}))
# série mensal (mês x classe x tipo x quem iniciou)
D["mes"] = D.data_inicio.str[:7]
meses = sorted(m for m in D.mes.unique() if m)
mensal = [dict(m=meses.index(m), c=classes.index(cl), t=cats.index(ca), x=acoes.index(ac), n=len(g))
          for (m, cl, ca, ac), g in D[D.mes != ""].groupby(["mes","classe","categoria_motivo","tipo_acao"])]
# empresas (período completo)
E = D.groupby("empresa_padrao").agg(n=("recall_number","size"), c1=("classe", lambda s: int((s=="I").sum())), anos=("ano_inicio", lambda s: int(s.dropna().nunique()))).sort_values("n", ascending=False).head(15).reset_index()
est = D[(D.pais=="United States")&(D.estado!="")].groupby("estado").agg(n=("recall_number","size"), c1=("classe", lambda s: int((s=="I").sum()))).sort_values("n", ascending=False).head(10).reset_index()
aud = pd.read_csv(os.path.join(RES, "01_auditoria_qualidade.csv"), sep=";", encoding="utf-8-sig")
conf = pd.read_csv(os.path.join(RES, "02_conferencia_planilha.csv"), sep=";", encoding="utf-8-sig")
rec = pd.read_csv(os.path.join(RES, "03_reconciliacao_planilha.csv"), sep=";", encoding="utf-8-sig")
val = pd.read_csv(os.path.join(RES, "04_validade_lotes_fda.csv"), sep=";", encoding="utf-8-sig").fillna("")
dados = dict(validade=val.to_dict("records"), anos=anos, classes=classes, cats=cats, acoes=acoes, cubo=cube, meses=meses, mensal=mensal,
    empresas=E.to_dict("records"), estados=est.to_dict("records"),
    auditoria=aud.fillna("").to_dict("records"), conferencia=conf.fillna("").to_dict("records"), reconciliacao=rec.to_dict("records"),
    gerado="2026-10-25", fonte="openFDA Food Enforcement, exportado em 14/10/2026 (29.485 registros)")
with open(os.path.join(RAIZ, "dashboard", "dados.js"), "w", encoding="utf-8") as f:
    f.write("window.DADOS=" + json.dumps(dados, ensure_ascii=False, separators=(",", ":"), default=lambda o: o.item() if hasattr(o,'item') else str(o)) + ";")
print(len(cube), "células;", os.path.getsize(os.path.join(RAIZ,"dashboard","dados.js"))//1024, "KB")
print(E.to_string()); print(est.to_string())

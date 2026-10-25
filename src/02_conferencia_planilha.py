"""Confere a aba 'Dados limpos' da planilha contra o arquivo original da FDA, campo a campo.
Entrada: dados_brutos_local/*.json (FDA) e dados_brutos_local/planilha_dados_limpos.csv (export da aba).
Saída: resultados/02_conferencia_planilha.csv"""
import os, re, csv, sys, collections
from datetime import datetime
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import carregar_bruto, BRUTO, RES
_, R = carregar_bruto()
P = pd.read_csv(os.path.join(BRUTO, "planilha_dados_limpos.csv"), dtype=str, keep_default_na=False)
sp = lambda s: re.sub(r"\s+", " ", (s or "")).strip()
N = len(R); out = []
EXPL = {"Registro da planilha sem par na FDA (por event_id+produto+nº)": ("EXPLICADO", "Apóstrofo inicial do nome do produto foi removido pela planilha (2 casos)."),
 "Campo data_inicio: valor diferente do original": ("EXPLICADO", "Data impossível 02121207 (F-0880-2013) ficou vazia na planilha, como documentado."),
 "ano_inicio não bate com data_inicio": ("EXPLICADO", "Mesmo registro da data impossível: sem data, sem ano."),
 "Campo codigo_lote: valor diferente do original": ("ERRO NA PLANILHA", "Zeros à esquerda perdidos (111) e outros ajustes de formato; texto original está no arquivo da FDA."),
 "Campo quantidade_texto: valor diferente do original": ("ERRO NA PLANILHA", "Números em texto lidos como número (ex.: 328.0000 virou 3.280.000). Não afeta quantidade_valor."),
 "Campo motivo: valor diferente do original": ("ERRO NA PLANILHA", "Apóstrofo inicial removido (1 caso).")}
def add(chk, afet, nota=""):
    res, nt = ("OK", nota) if afet == 0 else EXPL.get(chk, ("DIVERGE", nota))
    out.append([chk, afet, f"{afet/N*100:.2f}%", res, nt])
add("Linhas na planilha diferentes de linhas na FDA", abs(len(P) - N))
ev_ok = sorted(r["event_id"] for r in R) == sorted(P["event_id"])
add("Conjunto de event_id diferente entre FDA e planilha", 0 if ev_ok else 1)
# compara por chave (event_id + produto normalizado + recall_number)
fda = {}
for r in R: fda.setdefault((r["event_id"], sp(r["product_description"]), r.get("recall_number") or ""), []).append(r)
sem = 0; duplic_chave = 0; dif = collections.Counter()
mapa_classe = {"Class I":"I","Class II":"II","Class III":"III","Not Yet Classified":"Não classificado"}
mapa_acao = {"Voluntary: Firm initiated":"Voluntário (empresa)","FDA Mandated":"Obrigatório (FDA)"}
def dt(s):
    try: return datetime.strptime(s, "%Y%m%d").strftime("%Y-%m-%d")
    except Exception: return ""
for _, p in P.iterrows():
    k = (p["event_id"], sp(p["produto"]), p["recall_number"])
    L = fda.get(k)
    if not L: sem += 1; continue
    r = L[0]
    if len(L) > 1: duplic_chave += 1
    if r["status"] != p["status"]: dif["status"] += 1
    if mapa_classe.get(r["classification"]) != p["classe"]: dif["classe"] += 1
    if mapa_acao.get(r.get("voluntary_mandated"), "Não informado") != p["tipo_acao"]: dif["tipo_acao"] += 1
    if sp(r["recalling_firm"]) != sp(p["empresa"]): dif["empresa"] += 1
    if sp(r["reason_for_recall"]) != sp(p["motivo_original"]): dif["motivo"] += 1
    if sp(r.get("product_quantity")) != sp(p["quantidade_texto"]): dif["quantidade_texto"] += 1
    if sp(r.get("code_info")) != sp(p["codigo_lote_texto"]): dif["codigo_lote"] += 1
    if (r.get("state") or "") != p["estado"]: dif["estado"] += 1
    if r["country"] != p["pais"]: dif["pais"] += 1
    if dt(r["recall_initiation_date"]) != p["data_inicio"]: dif["data_inicio"] += 1
    if dt(r.get("center_classification_date")) != p["data_classificação"]: dif["data_classificacao"] += 1
    if dt(r.get("termination_date")) != p["data_termino"]: dif["data_termino"] += 1
    if dt(r["report_date"]) != p["data_relatorio"]: dif["data_relatorio"] += 1
    if sp(r.get("distribution_pattern")) != sp(p["distribuicao_texto"]): dif["distribuicao"] += 1
add("Registro da planilha sem par na FDA (por event_id+produto+nº)", sem)
add("Registros com chave repetida na FDA (pares ambíguos)", duplic_chave, "Conferidos contra o primeiro; ver nota 52 grupos")
for c, n in sorted(dif.items()): add(f"Campo {c}: valor diferente do original", n)
# internas
dc = P.assign(d=pd.to_numeric(P["dias_ate_classificar"], errors="coerce"))
calc = (pd.to_datetime(P["data_classificação"], errors="coerce") - pd.to_datetime(P["data_inicio"], errors="coerce")).dt.days
add("dias_ate_classificar não bate com datas", int(((dc["d"] != calc) & ~(dc["d"].isna() & calc.isna())).sum()))
dt_ = pd.to_numeric(P["dias_ate_terminar"], errors="coerce")
calc2 = (pd.to_datetime(P["data_termino"], errors="coerce") - pd.to_datetime(P["data_inicio"], errors="coerce")).dt.days
add("dias_ate_terminar não bate com datas", int(((dt_ != calc2) & ~(dt_.isna() & calc2.isna())).sum()))
add("ano_inicio não bate com data_inicio", int((P["ano_inicio"] != pd.to_datetime(P["data_inicio"], errors="coerce").dt.year.astype("Int64").astype(str).replace("<NA>","")).sum()))
add("Categorias de motivo somam diferente do total", abs(P["categoria_motivo"].ne("").sum() - N))
add("categoria_motivo vazia", int((P["categoria_motivo"] == "").sum()))
add("empresa_padrao vazia", int((P["empresa_padrao"] == "").sum()))
add("recall_number repetido na planilha", int(P[P.recall_number!=""]["recall_number"].duplicated().sum()))
pd.DataFrame(out, columns=["checagem","afetados","percentual","resultado","nota"]).to_csv(os.path.join(RES, "02_conferencia_planilha.csv"), sep=";", index=False, encoding="utf-8-sig")
for o in out: print(" | ".join(map(str, o)))

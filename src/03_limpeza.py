"""Limpeza: monta a base analítica a partir do ARQUIVO ORIGINAL da FDA.
Campos copiados do original (com espaços normalizados). Campos derivados por regra da planilha
(categoria do motivo, abrangência, validade citada, todos os lotes, empresa padronizada) vêm da aba
'Dados limpos' e são conferidos aqui. Nada é inventado: o que está errado na fonte é marcado, não corrigido."""
import os, re, sys, collections
from datetime import datetime
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import carregar_bruto, BRUTO, RES, RAIZ
_, R = carregar_bruto()
S = pd.read_csv(os.path.join(BRUTO, "planilha_dados_limpos.csv"), dtype=str, keep_default_na=False)
sp = lambda s: re.sub(r"\s+", " ", (s or "")).strip()
chave = lambda ev, prod, nr: (ev, sp(prod).lstrip("'"), nr)
M = {}
for _, p in S.iterrows(): M[chave(p["event_id"], p["produto"], p["recall_number"])] = p
def dt(s):
    try:
        d = datetime.strptime(s, "%Y%m%d").date()
        return d if d.year >= 2000 else None
    except Exception: return None
mc = {"Class I": "I", "Class II": "II", "Class III": "III", "Not Yet Classified": "Não classificado"}
ma = {"Voluntary: Firm initiated": "Voluntário (empresa)", "FDA Mandated": "Obrigatório (FDA)"}
rows = []; sempar = 0
for r in R:
    nr = r.get("recall_number") or ""
    p = M.get(chave(r["event_id"], r["product_description"], nr))
    if p is None: sempar += 1; continue
    ini, cla, ter, rep = (dt(r.get(k) or "") for k in ("recall_initiation_date", "center_classification_date", "termination_date", "report_date"))
    flags = []
    if not re.fullmatch(r"[A-Z]-\d{4}-\d{4}", nr): flags.append("número de recolhimento ausente ou fora do padrão")
    if r["recall_initiation_date"] and ini is None: flags.append("data de início inválida (não corrigida)")
    if not r.get("center_classification_date"): flags.append("sem data de classificação")
    rows.append(dict(
        recall_number=nr, event_id=r["event_id"], status=r["status"], classe=mc.get(r["classification"]),
        tipo_acao=ma.get(r.get("voluntary_mandated"), "Não informado"), empresa=sp(r["recalling_firm"]), empresa_padrao=p["empresa_padrao"],
        estado=r.get("state") or "", pais=r["country"], produto=sp(r["product_description"]), motivo=sp(r["reason_for_recall"]),
        categoria_motivo=p["categoria_motivo"], quantidade_texto=sp(r.get("product_quantity")),
        quantidade_valor=p["quantidade_valor"], quantidade_unidade=p["quantidade_unidade"],
        codigo_lote_texto=sp(r.get("code_info")), tem_codigo_especifico=p["tem_codigo_especifico"], todos_os_lotes=p["todos_os_lotes"],
        validade_citada=p["validade_citada"], abrangencia=p["abrangencia"],
        data_inicio=ini, data_classificacao=cla, data_termino=ter, data_relatorio=rep,
        sinais="; ".join(flags)))
D = pd.DataFrame(rows)
print("sem par:", sempar, "linhas:", len(D))
for c in ("data_inicio","data_classificacao","data_termino","data_relatorio"): D[c] = pd.to_datetime(D[c])
D["ano_inicio"] = D.data_inicio.dt.year
D["dias_ate_classificar"] = (D.data_classificacao - D.data_inicio).dt.days
D["dias_ate_terminar"] = (D.data_termino - D.data_inicio).dt.days
# repetição de quantidade por evento (volume somado seria inflado)
k = D.groupby(["event_id","quantidade_texto"]).recall_number.transform("size")
D["qtd_repetida_no_evento"] = (D.quantidade_texto != "") & (k > 1)
# possível reenvio: mesmo evento+empresa+produto+código, nº diferente (mantido: cada nº é um recolhimento da FDA)
g = D.groupby(["event_id","empresa","produto","codigo_lote_texto"]).recall_number.transform("size")
D["mesmo_produto_e_lote_no_evento"] = g > 1
D["ordem_original"] = range(len(D))
D.to_csv(os.path.join(BRUTO, "base_limpa.csv"), index=False, encoding="utf-8")
# reconciliação com números oficiais da planilha
rec = [("Registros", len(D), 29485), ("Classe I", int((D.classe=="I").sum()), 12976), ("Classe II", int((D.classe=="II").sum()), 14745),
       ("Classe III", int((D.classe=="III").sum()), 1762), ("Não classificado", int((D.classe=="Não classificado").sum()), 2),
       ("Obrigatório (FDA)", int((D.tipo_acao=="Obrigatório (FDA)").sum()), 396), ("Ongoing", int((D.status=="Ongoing").sum()), 1079),
       ("Mediana dias até classificar", float(D.dias_ate_classificar.median()), 38.0), ("Média dias até classificar", round(float(D.dias_ate_classificar.mean()),1), 68.5),
       ("P90 dias até classificar", float(D.dias_ate_classificar.quantile(.9)), 136.0), ("Microbiológica", int((D.categoria_motivo=="Contaminação microbiológica").sum()), 12992),
       ("Rotulagem/embalagem", int((D.categoria_motivo=="Rotulagem / embalagem").sum()), 1767), ("Com código específico", int((D.tem_codigo_especifico=="sim").sum()), 26205),
       ("Todos os lotes", int((D.todos_os_lotes=="sim").sum()), 3016), ("Validade citada", int((D.validade_citada=="sim").sum()), 11494)]
out = pd.DataFrame(rec, columns=["indicador","recalculado_do_original","valor_na_planilha"]); out["bate"] = out.recalculado_do_original == out.valor_na_planilha
out.to_csv(os.path.join(RES, "03_reconciliacao_planilha.csv"), sep=";", index=False, encoding="utf-8-sig")
print(out.to_string())
print(D.sinais.value_counts().head(8).to_string())
print("reenvio:", int(D.mesmo_produto_e_lote_no_evento.sum()), "qtd repetida:", int(D.qtd_repetida_no_evento.sum()))

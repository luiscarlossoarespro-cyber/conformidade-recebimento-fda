"""Auditoria de qualidade da base bruta da FDA. Gera resultados/01_auditoria_qualidade.csv
Cada linha = uma checagem (regra, quantidade afetada, %, decisão). Nenhum dado é alterado aqui."""
import csv, re, sys, collections
from datetime import datetime, date
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from comum import carregar_bruto, RES
import os
meta, R = carregar_bruto()
N = len(R); linhas = []
def add(grupo, regra, qtd, decisao, detalhe=""):
    linhas.append([grupo, regra, qtd, f"{qtd/N*100:.2f}%", decisao, detalhe])
def vazio(v): return v is None or (isinstance(v, str) and v.strip() == "")
def d8(s):
    try: return datetime.strptime(s, "%Y%m%d").date()
    except Exception: return None
hoje = date(2026, 10, 25)

add("Total", "Registros na base", N, "Conferido contra meta.total da FDA", f"meta.total={meta['results']['total']}")
# nulos
for c in R[0].keys():
    if c == "openfda": continue
    q = sum(vazio(r.get(c)) for r in R)
    add("Nulos", f"Coluna {c} vazia", q, "Manter vazio (não preencher)" if q else "Sem ação")
# duplicados
cnt = collections.Counter(r.get("recall_number") for r in R if not vazio(r.get("recall_number")))
add("Duplicados", "recall_number repetido", sum(v-1 for v in cnt.values() if v > 1), "Chave única: nenhuma ação" )
def chave_total(r): return tuple((k, str(v)) for k, v in sorted(r.items()))
c2 = collections.Counter(chave_total(r) for r in R)
add("Duplicados", "Linha idêntica em todas as colunas", sum(v-1 for v in c2.values() if v > 1), "Remover se > 0")
c3 = collections.Counter((r["event_id"], r["recalling_firm"], r["product_description"], r.get("code_info")) for r in R)
dup3 = sum(v-1 for v in c3.values() if v > 1)
add("Duplicados", "Mesmo evento+empresa+produto+código, com recall_number diferente", dup3, "Verificar: pode ser reenvio legítimo", "")
c4 = collections.Counter((r["recalling_firm"], r["product_description"], r.get("code_info"), r["recall_initiation_date"]) for r in R)
add("Duplicados", "Mesma empresa+produto+código+data de início", sum(v-1 for v in c4.values() if v > 1), "Verificar caso a caso")
# formato recall_number
bad = sum(1 for r in R if not vazio(r.get("recall_number")) and not re.fullmatch(r"[A-Z]-\d{4}-\d{4}", r["recall_number"]))
add("Formato", "recall_number fora do padrão X-0000-0000", bad, "Documentar")
# datas
D = {k: [d8(r.get(k)) if not vazio(r.get(k)) else None for r in R] for k in ["recall_initiation_date","center_classification_date","termination_date","report_date"]}
for k, v in D.items():
    fmt_ruim = sum(1 for r, x in zip(R, v) if not vazio(r.get(k)) and x is None)
    add("Datas", f"{k}: formato inválido", fmt_ruim, "Excluir só o campo")
    add("Datas", f"{k}: data futura (> 25/10/2026)", sum(1 for x in v if x and x > hoje), "Marcar")
    add("Datas", f"{k}: antes de 2000", sum(1 for x in v if x and x.year < 2000), "Marcar")
ini, cla, ter, rep = D["recall_initiation_date"], D["center_classification_date"], D["termination_date"], D["report_date"]
add("Datas", "Classificação antes do início", sum(1 for a, b in zip(ini, cla) if a and b and b < a), "Marcar e não calcular dias")
add("Datas", "Término antes do início", sum(1 for a, b in zip(ini, ter) if a and b and b < a), "Marcar e não calcular dias")
add("Datas", "Relatório antes do início", sum(1 for a, b in zip(ini, rep) if a and b and b < a), "Marcar")
add("Datas", "Término antes da classificação", sum(1 for a, b in zip(cla, ter) if a and b and b < a), "Marcar")
# categorias
def dist(c): return collections.Counter(r.get(c) for r in R)
for c, ok in [("status", None), ("classification", None), ("voluntary_mandated", None), ("country", None), ("product_type", None)]:
    d = dist(c); det = "; ".join(f"{k}={v}" for k, v in d.most_common(8))
    add("Categorias", f"{c}: valores distintos = {len(d)}", 0, "Conferir lista", det)
ws = sum(1 for r in R for k in ("recalling_firm","product_description","reason_for_recall","city") if isinstance(r.get(k), str) and r[k] != r[k].strip())
add("Texto", "Espaços extras no início/fim (empresa, produto, motivo, cidade)", ws, "Aparar espaços")
dbl = sum(1 for r in R for k in ("recalling_firm","product_description","reason_for_recall") if isinstance(r.get(k), str) and "  " in r[k])
add("Texto", "Espaços duplos dentro do texto", dbl, "Normalizar espaços")
# empresas: variantes de nome
def norm(s): return re.sub(r"[^A-Z0-9 ]", "", s.upper()).strip()
g = collections.defaultdict(set)
for r in R:
    if not vazio(r.get("recalling_firm")): g[re.sub(r"\b(INC|LLC|CO|CORP|CORPORATION|COMPANY|LTD|LP|THE)\b","",norm(r["recalling_firm"])).split().__len__() and " ".join(re.sub(r"\b(INC|LLC|CO|CORP|CORPORATION|COMPANY|LTD|LP|THE)\b","",norm(r["recalling_firm"])).split())].add(r["recalling_firm"])
varia = {k: v for k, v in g.items() if len(v) > 1}
add("Empresas", "Nomes padronizados com mais de uma grafia original", len(varia), "Usar nome padronizado nos rankings", "; ".join(list(varia)[:3]))
add("Empresas", "Empresas distintas (grafia original)", 0, "Informativo", str(len({r['recalling_firm'] for r in R})))
# estado / país
add("Local", "Estado vazio", sum(vazio(r.get("state")) for r in R), "Manter vazio (muitos são fora dos EUA)")
add("Local", "País diferente de United States", sum(1 for r in R if r.get("country") != "United States"), "Manter; filtrar nos rankings de estado")
# quantidade
def qnum(s):
    if vazio(s): return None
    m = re.search(r"(\d[\d,\.]*)", s)
    if not m: return None
    t = m.group(1).replace(",", "")
    try: return float(t)
    except Exception: return None
add("Quantidade", "Texto sem número legível", sum(1 for r in R if not vazio(r.get("product_quantity")) and qnum(r["product_quantity"]) is None), "Deixar vazio")
add("Quantidade", "Quantidade igual a zero", sum(1 for r in R if qnum(r.get("product_quantity")) == 0), "Marcar")
# código / lote
add("Lote", "code_info vazio", sum(vazio(r.get("code_info")) for r in R), "Manter vazio")
add("Lote", "Cita 'all' / 'todos os lotes'", sum(1 for r in R if isinstance(r.get("code_info"), str) and re.search(r"\ball\b", r["code_info"], re.I)), "Marcar como todos os lotes (regra aproximada)")
# eventos
ev = collections.defaultdict(set)
for r in R: ev[r["event_id"]].add(r["recalling_firm"])
add("Eventos", "event_id com mais de uma empresa", sum(1 for v in ev.values() if len(v) > 1), "Informativo: evento pode ter várias empresas")
os.makedirs(RES, exist_ok=True)
with open(os.path.join(RES, "01_auditoria_qualidade.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f, delimiter=";"); w.writerow(["grupo","regra","quantidade","percentual","decisao","detalhe"]); w.writerows(linhas)
for l in linhas: print(" | ".join(map(str, l)))

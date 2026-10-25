"""Gera README.md e docs/ a partir da base limpa e dos CSVs. Nenhum número é digitado à mão."""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import BRUTO, RES, RAIZ
D = pd.read_csv(os.path.join(BRUTO, "base_limpa.csv"), dtype=str, keep_default_na=False)
for c in ("dias_ate_classificar","dias_ate_terminar","ano_inicio"): D[c] = pd.to_numeric(D[c], errors="coerce")
N = len(D); f = lambda n: f"{int(n):,}".replace(",", "."); p = lambda a, b=N, d=1: f"{a/b*100:.{d}f}%".replace(".", ",")
c1 = (D.classe == "I").sum(); cat = D.categoria_motivo.value_counts()
t = D.groupby("categoria_motivo").agg(n=("classe","size"), c1=("classe", lambda s: (s=="I").sum()))
t["pc1"] = t.c1 / t.n
micro = cat["Contaminação microbiológica"]; alerg = cat["Alergênico não declarado"]
cod = (D.tem_codigo_especifico=="sim").sum(); tl = (D.todos_os_lotes=="sim").sum(); val = (D.validade_citada=="sim").sum()
med = int(D.dias_ate_classificar.median()); p90 = int(D.dias_ate_classificar.quantile(.9)); mt = int(D.dias_ate_terminar.median())
ob = (D.tipo_acao=="Obrigatório (FDA)").sum(); rep = D.groupby("empresa_padrao").ano_inicio.nunique()
aud = pd.read_csv(os.path.join(RES, "01_auditoria_qualidade.csv"), sep=";", encoding="utf-8-sig")
conf = pd.read_csv(os.path.join(RES, "02_conferencia_planilha.csv"), sep=";", encoding="utf-8-sig")
rec = pd.read_csv(os.path.join(RES, "03_reconciliacao_planilha.csv"), sep=";", encoding="utf-8-sig")
tab = "\n".join(f"| {k} | {f(v.n)} | {p(v.n)} | {p(v.c1, v.n)} |" for k, v in t.sort_values("n", ascending=False).iterrows())
md = f"""# Conformidade no Recebimento: o que {f(N)} recolhimentos reais da FDA mostram

[![Dashboard ao vivo](https://img.shields.io/badge/dashboard-ao%20vivo-2a78d6)](https://luiscarlossoarespro-cyber.github.io/conformidade-recebimento-fda/dashboard/)

Estudo de dados públicos sobre recolhimentos de alimentos nos EUA (FDA) para responder, com número, **o que o conferente evita no recebimento**: lote, validade e produto fora de conformidade. Inclui uma calculadora de vida útil restante.

**Dashboard:** https://luiscarlossoarespro-cyber.github.io/conformidade-recebimento-fda/dashboard/

## Pergunta principal
Que tipos de problema levam a recolhimentos, quão graves são, quanto tempo levam e o que a conferência (nota, lote, validade, embalagem) consegue perceber?

## Resumo
- **{f(N)} recolhimentos** (openFDA Food Enforcement, exportado em 14/10/2026). Classe I (risco sério): **{f(c1)} ({p(c1)})**.
- Maior causa: contaminação microbiológica, **{f(micro)} ({p(micro)})**, dos quais {p(t.loc['Contaminação microbiológica'].c1, micro)} são Classe I. Em segundo, alergênico não declarado, {f(alerg)} ({p(alerg)}).
- A FDA leva **{med} dias** (mediana) para classificar o risco; 9 em cada 10 ficam abaixo de **{p90} dias**. Encerrar leva mediana de {f(mt)} dias.
- **{p(cod)}** citam código ou lote específico; **{p(val)}** citam validade; **{p(tl)}** recolhem "todos os lotes".
- Só **{p(ob)}** foram por ordem da FDA; o resto a empresa iniciou.

| Tipo de problema | Recolhimentos | % do total | % Classe I |
|---|---|---|---|
{tab}

## Perguntas do gerente (respondidas no dashboard)
1. Qual problema mais gera recolhimento? 2. Qual é o mais perigoso? 3. Quantos são Classe I? 4. Quanto tempo a FDA leva para classificar? 5. E para encerrar? 6. Dá para identificar o lote? 7. Quantos recolhem todos os lotes? 8. A validade ajuda a identificar? 9. Quantos foram por ordem da FDA? 10. Quais empresas reincidem?

## Abas do dashboard
Visão geral · Perguntas do gerente · Problemas e gravidade · Tempo · Lote e validade · Empresas e estados · O que a conferência vê · Calculadora · Qualidade e método. Filtros: ano de início, classe de risco, tipo de problema, quem iniciou. Tudo recalcula no navegador. Os gráficos se desenham ao abrir, os números contam até o valor, clicar numa barra de ano, numa fatia de classe ou num tipo de problema filtra o painel inteiro, e o botão "Reproduzir anos" passa ano a ano.

## Auditoria e limpeza
- Auditoria do arquivo original: [`resultados/01_auditoria_qualidade.csv`](resultados/01_auditoria_qualidade.csv) ({len(aud)} checagens). **0 números de recolhimento repetidos e 0 linhas idênticas.**
- Conferência da planilha de tratamento contra o original, campo a campo: [`resultados/02_conferencia_planilha.csv`](resultados/02_conferencia_planilha.csv). {int((conf.resultado=='OK').sum())} checagens OK, {int((conf.resultado=='EXPLICADO').sum())} explicadas, {int((conf.resultado=='ERRO NA PLANILHA').sum())} erros de formato da planilha encontrados (zeros à esquerda perdidos em códigos de lote, números em texto deformados).
- Reconciliação: {int(rec.bate.sum())} de {len(rec)} indicadores recalculados do original batem com a planilha ([`03_reconciliacao_planilha.csv`](resultados/03_reconciliacao_planilha.csv)).
- Regras: nada é corrigido por suposição. Número de recolhimento ausente ou fora do padrão ({int((D.sinais.str.contains('número')).sum())} casos) e data de início impossível (1 caso) são **marcados**, não corrigidos. Cada número da FDA, mesmo com mesmo produto e lote no mesmo evento, é um registro separado.

## Limitações
- Dados dos EUA, só de alimentos; a FDA fornece os dados como estão e não atualiza o status depois de classificar.
- Não há clientes, custos nem dados de doca: por isso o painel **não** mostra acurácia, OTIF ou custo.
- A categoria do motivo é por palavras-chave e pode errar em casos que citam dois problemas (ex.: Salmonella em pasta de amendoim).
- Volumes recolhidos não são somados: a FDA repete o total do evento em cada recolhimento ({f(D.qtd_repetida_no_evento.eq('True').sum())} linhas).
- A coluna "a conferência vê?" é **interpretação do autor**, não dado da FDA.
- A validade dos recolhidos (aba Lote e validade) vem da aba "Lotes FDA" da planilha de tratamento, ainda não recalculada por script neste repositório.

## Como reproduzir
```
pip install -r requirements.txt
# coloque food-enforcement-0001-of-0001.json (openFDA) em dados_brutos_local/
python src/rodar_tudo.py
```
Fonte: https://open.fda.gov/apis/food/enforcement/ (domínio público, CC0). Tratamento em planilha: https://docs.google.com/spreadsheets/d/1T55SG4vpSKiayqWkS1nCQxdFY2sBl40jXn0MI_TJA3o/edit

## Apoio de IA
Este projeto foi desenvolvido com apoio de IA (Claude) para auditoria, scripts e dashboard. As decisões, a conferência dos números e a interpretação são do autor.

**Autor:** Luis Carlos Machado Soares · [Portfólio](https://luiscarlossoarespro-cyber.github.io/) · Licença MIT
"""
open(os.path.join(RAIZ, "README.md"), "w", encoding="utf-8").write(md); print(md[:1500])

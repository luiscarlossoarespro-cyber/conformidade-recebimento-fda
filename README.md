# Conformidade no Recebimento: o que 29.485 recolhimentos reais da FDA mostram

[![Dashboard ao vivo](https://img.shields.io/badge/dashboard-ao%20vivo-2a78d6)](https://luiscarlossoarespro-cyber.github.io/conformidade-recebimento-fda/dashboard/)

Estudo de dados públicos sobre recolhimentos de alimentos nos EUA (FDA) para responder, com número, **o que o conferente evita no recebimento**: lote, validade e produto fora de conformidade. Inclui uma calculadora de vida útil restante.

**Dashboard:** https://luiscarlossoarespro-cyber.github.io/conformidade-recebimento-fda/dashboard/

**Vídeo de demonstração (2 min 40 s):**

https://github.com/user-attachments/assets/adf70707-9097-4411-8309-292b25377042

## Pergunta principal
Que tipos de problema levam a recolhimentos, quão graves são, quanto tempo levam e o que a conferência (nota, lote, validade, embalagem) consegue perceber?

## Resumo
- **29.485 recolhimentos** (openFDA Food Enforcement, exportado em 14/10/2026). Classe I (risco sério): **12.976 (44,0%)**.
- Maior causa: contaminação microbiológica, **12.992 (44,1%)**, dos quais 75,0% são Classe I. Em segundo, alergênico não declarado, 8.041 (27,3%).
- A FDA leva **38 dias** (mediana) para classificar o risco; 9 em cada 10 ficam abaixo de **136 dias**. Encerrar leva mediana de 215 dias.
- **88,9%** citam código ou lote específico; **39,0%** citam validade; **10,2%** recolhem "todos os lotes".
- Só **1,3%** foram por ordem da FDA; o resto a empresa iniciou.

| Tipo de problema | Recolhimentos | % do total | % Classe I |
|---|---|---|---|
| Contaminação microbiológica | 12.992 | 44,1% | 75,0% |
| Alergênico não declarado | 8.041 | 27,3% | 34,5% |
| Corpo estranho | 2.544 | 8,6% | 0,3% |
| Processo / higiene / deterioração | 2.214 | 7,5% | 0,4% |
| Rotulagem / embalagem | 1.767 | 6,0% | 14,5% |
| Químico / substância indevida | 1.312 | 4,4% | 8,2% |
| Outros | 615 | 2,1% | 13,8% |

## Perguntas do gerente (respondidas no dashboard)
1. Qual problema mais gera recolhimento? 2. Qual é o mais perigoso? 3. Quantos são Classe I? 4. Quanto tempo a FDA leva para classificar? 5. E para encerrar? 6. Dá para identificar o lote? 7. Quantos recolhem todos os lotes? 8. A validade ajuda a identificar? 9. Quantos foram por ordem da FDA? 10. Quais empresas reincidem?

## Abas do dashboard
Visão geral · Perguntas do gerente · Problemas e gravidade · Tempo · Lote e validade · Empresas e estados · O que a conferência vê · Calculadora · Qualidade e método. Filtros: ano de início, classe de risco, tipo de problema, quem iniciou. Tudo recalcula no navegador. Os gráficos se desenham ao abrir, os números contam até o valor, clicar numa barra de ano, numa fatia de classe ou num tipo de problema filtra o painel inteiro, e o botão "Reproduzir anos" passa ano a ano.

## Auditoria e limpeza
- Auditoria do arquivo original: [`resultados/01_auditoria_qualidade.csv`](resultados/01_auditoria_qualidade.csv) (61 checagens). **0 números de recolhimento repetidos e 0 linhas idênticas.**
- Conferência da planilha de tratamento contra o original, campo a campo: [`resultados/02_conferencia_planilha.csv`](resultados/02_conferencia_planilha.csv). 9 checagens OK, 3 explicadas, 3 erros de formato da planilha encontrados (zeros à esquerda perdidos em códigos de lote, números em texto deformados).
- Reconciliação: 15 de 15 indicadores recalculados do original batem com a planilha ([`03_reconciliacao_planilha.csv`](resultados/03_reconciliacao_planilha.csv)).
- Regras: nada é corrigido por suposição. Número de recolhimento ausente ou fora do padrão (47 casos) e data de início impossível (1 caso) são **marcados**, não corrigidos. Cada número da FDA, mesmo com mesmo produto e lote no mesmo evento, é um registro separado.

## Limitações
- Dados dos EUA, só de alimentos; a FDA fornece os dados como estão e não atualiza o status depois de classificar.
- Não há clientes, custos nem dados de doca: por isso o painel **não** mostra acurácia, OTIF ou custo.
- A categoria do motivo é por palavras-chave e pode errar em casos que citam dois problemas (ex.: Salmonella em pasta de amendoim).
- Volumes recolhidos não são somados: a FDA repete o total do evento em cada recolhimento (11.170 linhas).
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

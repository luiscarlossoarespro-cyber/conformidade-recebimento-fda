# Resultados

- `01_auditoria_qualidade.csv`: auditoria do arquivo original da FDA (nulos, duplicados, datas, categorias).
- `02_conferencia_planilha.csv`: conferência campo a campo da aba "Dados limpos" contra o original.
- `03_reconciliacao_planilha.csv`: 15 indicadores recalculados do original contra a planilha.
- `04_validade_lotes_fda.csv`: validade dos recolhidos. **Fonte: aba "Lotes FDA" da planilha** (regras rígidas documentadas no Diário de tratamento, etapa 8), copiada de lá; este número ainda não foi recalculado por script neste repositório.

"""Refaz o projeto do zero: auditoria, conferência, limpeza, dados do dashboard, README e teste."""
import subprocess, sys, os
d = os.path.dirname(os.path.abspath(__file__))
for s in ["01_auditoria.py", "02_conferencia_planilha.py", "03_limpeza.py", "10_dados_dashboard.py", "08_relatorio.py", "04_verificar_numeros.py", "11_testar_dashboard.py"]:
    print("==", s); subprocess.run([sys.executable, "-I", os.path.join(d, s)], check=True)

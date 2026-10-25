"""Abre o dashboard num navegador, percorre as abas, checa erros e confere filtros contra a base limpa."""
import os, sys, pandas as pd
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import BRUTO, RAIZ
D = pd.read_csv(os.path.join(BRUTO, "base_limpa.csv"), dtype=str, keep_default_na=False)
D["ano"] = pd.to_numeric(D.ano_inicio, errors="coerce"); D["dc"] = pd.to_numeric(D.dias_ate_classificar, errors="coerce")
erros = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.on("console", lambda m: erros.append(m.text) if m.type == "error" else None); pg.on("pageerror", lambda e: erros.append(str(e)))
    pg.goto("file://" + os.path.join(RAIZ, "dashboard", "index.html")); pg.wait_for_timeout(1400)
    kp = lambda: pg.eval_on_selector_all("#p-geral .k b", "e=>e.map(x=>x.textContent)")
    print("sem filtro:", kp())
    esp = [f"{len(D):,}".replace(",", "."), f"{(D.classe=='I').mean()*100:.1f}%".replace(".", ","), f"{int(D.dc.median())} dias"]
    assert kp()[:3] == esp, (kp()[:3], esp)
    # filtro: ano 2012 + Classe I
    pg.select_option("#fa", label="2012"); pg.select_option("#fc", label="Classe I"); pg.wait_for_timeout(1400)
    S = D[(D.ano == 2012) & (D.classe == "I")]
    print("2012 + Classe I:", kp()[:3], "esperado", len(S), int(S.dc.median()))
    assert kp()[0] == f"{len(S):,}".replace(",", "."); assert kp()[2] == f"{int(S.dc.median())} dias"
    pg.click("#limpar")
    # clique no gráfico filtra o painel inteiro
    pg.wait_for_timeout(1200); pg.click("#p-geral rect[data-fa='5']"); pg.wait_for_timeout(1400)
    print("clique na barra do ano:", pg.input_value("#fa"), kp()[:2])
    pg.click("#limpar"); pg.wait_for_timeout(300)
    pg.evaluate("document.querySelector(\"#p-geral circle[data-fc='0']\").dispatchEvent(new MouseEvent('click',{bubbles:true}))"); pg.wait_for_timeout(1400); print("clique na rosca ->", pg.input_value("#fc"), kp()[:2])
    pg.click("#limpar"); pg.wait_for_timeout(300)
    pg.click("#p-geral .play"); pg.wait_for_timeout(2300); print("reproduzir anos ->", pg.input_value("#fa")); pg.click("#p-geral .play"); pg.wait_for_timeout(300); pg.click("#limpar")
    for k in ["geral","perg","prob","tempo","lote","emp","barr","calc","qual"]:
        pg.evaluate(f"abrirAba('{k}')"); pg.wait_for_timeout(1500)
        vis = pg.eval_on_selector(f"#p-{k}", "e=>e.innerText.length"); print(k, "texto", vis)
        pg.screenshot(path=os.path.join(RAIZ, "dashboard", f"_shot_{k}.png"), full_page=True)
    pg.evaluate("abrirAba('calc')"); pg.fill("#dp", "2026-01-01"); pg.fill("#dv", "2026-12-31"); pg.fill("#dr", "2026-06-01"); pg.fill("#pm", "80")
    print(pg.text_content("#res"))
    pg.set_viewport_size({"width": 390, "height": 800}); pg.evaluate("abrirAba('geral')"); pg.wait_for_timeout(300)
    print("rolagem lateral no celular:", pg.evaluate("document.documentElement.scrollWidth>innerWidth"))
    b.close()
print("erros de console:", erros)

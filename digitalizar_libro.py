#!/usr/bin/env python3
"""
Digitalizador automático de libros en archive.org (modo 2up).
Por cada doble página: captura Selenium → OCR Tesseract → traducción Ollama → siguiente.

Uso:
    conda activate openinterpreter
    python digitalizar_libro.py

Configuración en la sección CONFIGURACIÓN de abajo.
"""

import re
import subprocess
import sys
import time
import io
from pathlib import Path

from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# ── CONFIGURACIÓN ──────────────────────────────────────────────────────────────
BOOK_ID    = "systemanticshows00gall"
PAGE_START = 1      # hoja archive.org desde donde empezar
PAGE_END   = 135    # última hoja
PAGE_STEP  = 2      # modo 2up: avanzar de 2 en 2
MODELO     = "qwen3:14b"
SALIDA     = Path("./traduccion_systemantics")
LOGIN_TIME   = 50   # segundos para hacer login manual al inicio
TIMEOUT_CARGA = 30  # segundos máximos esperando que cargue cada página
# ──────────────────────────────────────────────────────────────────────────────

ANSI_RE = re.compile(r'\x1b\[[0-9;?]*[a-zA-Z]|\r')


def url_pagina(n: int) -> str:
    return f"https://archive.org/details/{BOOK_ID}/page/n{n}/mode/2up"


def capturar_pagina(driver) -> bytes:
    """
    Captura solo el área de las páginas del libro.
    Intento 1: screenshot del elemento .BRtwoPageView o .BRcontainer (Selenium).
    Intento 2: bounding box via JS + recorte PIL (se adapta a cualquier tamaño de ventana).
    Intento 3: screenshot completo como último recurso.
    """
    # ── Intento 1: element screenshot ────────────────────────────────────────
    for selector in (".BRtwoPageView", ".BRcontainer"):
        try:
            el = driver.find_element(By.CSS_SELECTOR, selector)
            if el.size["width"] > 100 and el.size["height"] > 100:
                return el.screenshot_as_png
        except Exception:
            continue

    # ── Intento 2: bounding box JS + recorte manual ───────────────────────────
    try:
        rect = driver.execute_script("""
            var selectors = ['.BRtwoPageView', '.BRcontainer', '#BookReader'];
            for (var i = 0; i < selectors.length; i++) {
                var el = document.querySelector(selectors[i]);
                if (el && el.offsetWidth > 100) {
                    var r = el.getBoundingClientRect();
                    return {x: r.left, y: r.top, w: r.width, h: r.height};
                }
            }
            return null;
        """)
        if rect and rect["w"] > 100:
            png  = driver.get_screenshot_as_png()
            img  = Image.open(io.BytesIO(png))
            dpr  = driver.execute_script("return window.devicePixelRatio || 1")
            x, y = int(rect["x"] * dpr), int(rect["y"] * dpr)
            w, h = int(rect["w"] * dpr), int(rect["h"] * dpr)
            img  = img.crop((x, y, x + w, y + h))
            buf  = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()
    except Exception:
        pass

    # ── Intento 3: screenshot completo ────────────────────────────────────────
    return driver.get_screenshot_as_png()


def preprocesar(png_bytes: bytes, dst: Path):
    """Recibe bytes PNG, escala x2, escala de grises y normaliza contraste."""
    img = Image.open(io.BytesIO(png_bytes))
    img.save(str(dst))
    subprocess.run(
        ["convert", str(dst), "-resize", "200%", "-type", "Grayscale",
         "-normalize", str(dst)],
        check=True, capture_output=True
    )


def ocr(image_path: Path) -> str:
    r = subprocess.run(
        ["tesseract", str(image_path), "stdout", "--dpi", "300", "-l", "eng"],
        capture_output=True, text=True
    )
    return r.stdout.strip()


def traducir(texto: str) -> str:
    prompt = (
        "Traduce al español el siguiente texto de un libro, preservando "
        "el formato de párrafos. Responde solo con la traducción, sin "
        "comentarios ni encabezados:\n\n" + texto
    )
    r = subprocess.run(
        ["ollama", "run", MODELO],
        input=prompt, capture_output=True, text=True, timeout=240
    )
    return ANSI_RE.sub("", r.stdout).strip()


def esperar_carga(driver):
    """Espera hasta que las imágenes de las páginas estén completamente renderizadas."""
    deadline = time.time() + TIMEOUT_CARGA

    # 1. document.readyState === 'complete'
    while time.time() < deadline:
        if driver.execute_script("return document.readyState") == "complete":
            break
        time.sleep(0.3)

    # 2. Contenedor del BookReader presente y visible
    restante = max(3, deadline - time.time())
    try:
        WebDriverWait(driver, restante).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".BRcontainer, #BookReader")
            )
        )
    except Exception:
        print("  Aviso: contenedor del libro no visible")
        return

    # 3. Al menos una imagen de página cargada con contenido real
    js_imagenes_cargadas = """
        var imgs = document.querySelectorAll(
            '.BRcontainer img, .BRpagecontainer img, .BRtwoPageView img'
        );
        if (imgs.length === 0) return false;
        var cargadas = Array.from(imgs).filter(function(img) {
            return img.src && img.src !== '' &&
                   img.complete && img.naturalWidth > 0;
        });
        return cargadas.length > 0;
    """
    restante = max(3, deadline - time.time())
    try:
        WebDriverWait(driver, restante).until(
            lambda d: d.execute_script(js_imagenes_cargadas)
        )
    except Exception:
        print("  Aviso: timeout esperando imágenes, continuando igual")

    time.sleep(0.5)  # margen mínimo para el renderizado final


def ya_procesado(n: int) -> bool:
    """Permite reanudar una ejecución interrumpida."""
    return any(SALIDA.glob(f"*_n{n}.txt"))


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    tmp = Path("/tmp/digitalizador")
    tmp.mkdir(exist_ok=True)

    # ── Abrir Chrome ──────────────────────────────────────────────────────────
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts
    )

    # ── Login manual ──────────────────────────────────────────────────────────
    driver.get(url_pagina(PAGE_START))
    print(f"\nSe ha abierto el libro en el navegador.")
    print(f"Si no estás autenticado, inicia sesión ahora.")
    print(f"Tienes {LOGIN_TIME} segundos antes de que empiece la captura...\n")
    time.sleep(LOGIN_TIME)

    # ── Calcular páginas pendientes ───────────────────────────────────────────
    paginas = list(range(PAGE_START, PAGE_END + 1, PAGE_STEP))
    pendientes = [n for n in paginas if not ya_procesado(n)]
    print(f"Páginas totales: {len(paginas)} | Pendientes: {len(pendientes)}\n")

    pagina_num = 0
    for n in pendientes:
        pagina_num += 1
        pct = pagina_num / len(pendientes) * 100
        print(f"[{pct:5.1f}%] Página n{n} ({pagina_num}/{len(pendientes)})")

        # Navegar y esperar carga real
        driver.get(url_pagina(n))
        esperar_carga(driver)

        # Capturar y preprocesar
        png_bytes = capturar_pagina(driver)
        img_pre = tmp / f"p{n:04d}.png"
        preprocesar(png_bytes, img_pre)

        # OCR
        texto_ocr = ocr(img_pre)
        if len(texto_ocr.strip()) < 30:
            print("  Página vacía o sin texto, saltando.")
            continue
        print(f"  OCR: {len(texto_ocr)} chars → traduciendo...")

        # Traducir
        try:
            traduccion = traducir(texto_ocr)
        except subprocess.TimeoutExpired:
            print("  Timeout en Ollama, guardando solo el OCR.")
            traduccion = "[TRADUCCIÓN NO DISPONIBLE - timeout]\n\n" + texto_ocr

        # Guardar
        salida_file = SALIDA / f"pagina_{pagina_num:04d}_n{n}.txt"
        salida_file.write_text(
            f"{'─'*60}\n"
            f"PÁGINA {pagina_num}  (archive.org hoja n{n})\n"
            f"{'─'*60}\n\n"
            f"{traduccion}\n",
            encoding="utf-8"
        )
        print(f"  Guardado: {salida_file.name}")

    # ── Concatenar libro completo ─────────────────────────────────────────────
    print("\nGenerando libro_completo.txt...")
    completo = SALIDA / "libro_completo.txt"
    archivos = sorted(SALIDA.glob("pagina_*.txt"))
    with completo.open("w", encoding="utf-8") as f:
        for archivo in archivos:
            f.write(archivo.read_text(encoding="utf-8"))
            f.write("\n\n")
    print(f"Listo. {len(archivos)} páginas en: {completo.resolve()}")

    driver.quit()


if __name__ == "__main__":
    main()

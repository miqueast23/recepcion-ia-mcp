"""MCP para crear el video promocional de Recepción IA.
Genera escenas con fal.ai (modelo configurable) y las une con ffmpeg."""
import os, json, time, subprocess, pathlib, httpx
from mcp.server.fastmcp import FastMCP

FAL_KEY = os.environ.get("FAL_KEY", "")
MODELO = os.environ.get("FAL_MODEL", "fal-ai/veo3")
SALIDA = pathlib.Path(os.environ.get("VIDEO_DIR", pathlib.Path.home() / "Videos" / "RecepcionIA"))
SALIDA.mkdir(parents=True, exist_ok=True)
mcp = FastMCP("video-recepcion-ia")

ESTILO = ("Estilo comercial cinematográfico, personas latinoamericanas realistas, "
          "luz natural, 16:9, audio con voz en off en español de Venezuela. ")
GUION = [
 {"n": 1, "titulo": "El problema", "prompt": "Lobby de una torre corporativa moderna en Caracas con El Ávila al fondo por el ventanal. Un visitante de unos 35 años con traje espera impaciente frente a un mostrador vacío y mira el reloj. Voz en off: '¿Cuántas veces su visita esperó sin que nadie le avisara?'"},
 {"n": 2, "titulo": "El robot", "prompt": "Mismo lobby. Una mujer joven profesional se acerca a un robot recepcionista blanco con pantalla, toca el directorio y elige 'María Pérez, Finanzas, piso 8'. Aparece una confirmación verde. Planos cercanos de la mano y la sonrisa. Voz en off: 'Recepción IA la registra en segundos y avisa por WhatsApp, con confirmación.'"},
 {"n": 3, "titulo": "El anfitrión", "prompt": "Oficina en el piso 8. Una ejecutiva de unos 40 años recibe en su celular un WhatsApp 'Llegó su visita' y toca 'Bajo en 2 min'. Corte al visitante en el lobby recibiendo un café. Voz en off: 'Si el aviso no llega en 60 segundos, el sistema alerta a recepción. Ninguna visita se pierde.'"},
 {"n": 4, "titulo": "Cierre", "prompt": "Plano amplio del lobby con el robot al centro, gente saludándose y la pantalla del robot mostrando un anuncio. Cierra con el texto 'Recepción IA' en verde malaquita sobre negro. Voz en off: 'Cero avisos perdidos, cero respuestas inventadas. Recepción IA, la recepción que nunca falla.'"},
]

def _h():
    if not FAL_KEY:
        raise RuntimeError("Falta la variable FAL_KEY (clave de fal.ai).")
    return {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}

@mcp.tool()
def ver_guion() -> str:
    """Devuelve las 4 escenas del guion promocional."""
    return json.dumps(GUION, ensure_ascii=False, indent=2)

@mcp.tool()
def generar_escena(numero: int = 0, prompt: str = "", duracion: str = "8s") -> str:
    """Envía una escena a generar. Use numero (1-4) del guion o un prompt propio.
    Devuelve el request_id para consultar con estado_escena."""
    texto = prompt or next(e["prompt"] for e in GUION if e["n"] == numero)
    body = {"prompt": ESTILO + texto, "duration": duracion, "aspect_ratio": "16:9", "generate_audio": True}
    r = httpx.post(f"https://queue.fal.run/{MODELO}", headers=_h(), json=body, timeout=60)
    r.raise_for_status(); d = r.json()
    (SALIDA / f"job_{numero or 'libre'}.json").write_text(json.dumps(d))
    return json.dumps({"escena": numero, "request_id": d.get("request_id"),
                       "status_url": d.get("status_url"), "response_url": d.get("response_url")})

@mcp.tool()
def estado_escena(numero: int, esperar_seg: int = 0) -> str:
    """Consulta una escena enviada. Si terminó, descarga el MP4 a la carpeta de salida."""
    d = json.loads((SALIDA / f"job_{numero}.json").read_text())
    fin = time.time() + esperar_seg
    while True:
        s = httpx.get(d["status_url"], headers=_h(), timeout=60).json()
        if s.get("status") == "COMPLETED" or time.time() >= fin: break
        time.sleep(10)
    if s.get("status") != "COMPLETED":
        return json.dumps({"escena": numero, "estado": s.get("status")})
    res = httpx.get(d["response_url"], headers=_h(), timeout=60).json()
    url = res["video"]["url"]
    destino = SALIDA / f"escena_{numero}.mp4"
    destino.write_bytes(httpx.get(url, timeout=300).content)
    return json.dumps({"escena": numero, "estado": "listo", "archivo": str(destino)})

@mcp.tool()
def unir_video(nombre: str = "RecepcionIA_promo.mp4") -> str:
    """Une escena_1..4.mp4 en un solo video con ffmpeg."""
    partes = [SALIDA / f"escena_{i}.mp4" for i in range(1, 5)]
    faltan = [p.name for p in partes if not p.exists()]
    if faltan: return f"Faltan escenas: {', '.join(faltan)}"
    lista = SALIDA / "lista.txt"
    lista.write_text("\n".join(f"file '{p.as_posix()}'" for p in partes))
    final = SALIDA / nombre
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
                    "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", str(final)], check=True)
    return f"Video listo: {final}"

if __name__ == "__main__":
    mcp.run()

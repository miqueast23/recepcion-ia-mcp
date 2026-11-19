# Arma los videos de Recepción IA (promocional y explicativo) con tomas reales de Coverr,
# voces neuronales venezolanas (edge-tts es-VE), gráficos HTML (overlays.html) y música sintetizada.
# Uso: python build.py promo|explicativo <dirTrabajo>   (dirTrabajo sin acentos ni ñ: ffmpeg)
import asyncio, json, os, subprocess, sys, urllib.parse
import numpy as np
from scipy.io import wavfile
import edge_tts

AQUI = os.path.dirname(os.path.abspath(__file__))
CUAL, W = sys.argv[1], sys.argv[2]
RAW, OV, VO, SEG = (os.path.join(W, d) for d in ("raw", "ov_" + CUAL, "vo_" + CUAL, "seg_" + CUAL))
for d in (RAW, OV, VO, SEG):
    os.makedirs(d, exist_ok=True)
SR, FPS = 48000, 30
SEB, PAO = "es-VE-SebastianNeural", "es-VE-PaolaNeural"

GRADE = {
    "cool": "eq=saturation=0.55:contrast=1.08:brightness=-0.04,colorbalance=bs=0.07:bm=0.04",
    "clean": "eq=saturation=1.05:contrast=1.04",
    "warm": "eq=saturation=1.12:contrast=1.05,colorbalance=rs=0.07:bs=-0.05:rm=0.05:bm=-0.04",
}

# Segmento: fondo (id Coverr o None=negro), inicio, etalonaje, desenfoque, voces [(voz, texto)],
# gráficos [(nombre, desde, hasta) en fracción del segmento], duración mínima.
def S(bg, ss, g, vo=(), ov=(), blur=False, minimo=2.5):
    return dict(bg=bg, ss=ss, g=g, vo=list(vo), ov=list(ov), blur=blur, minimo=minimo)

GUIONES = {
 "promo": dict(rate="+0%", seg=[
  S("fizD2gjAlJ", 1, "cool", [(SEB, "Todos los días, su empresa recibe visitas.")], [("cap:Todos los días, su empresa recibe visitas.", .12, 1)]),
  S("AxSHgGwKa4", 2, "cool", [(SEB, "Pero... ¿cuántas esperaron sin que nadie les avisara?")], [("cap:¿Cuántas esperaron <b>sin que nadie avisara</b>?", .1, 1)]),
  S("S3rXHOHnGX", 2, "cool", [(SEB, "La recepción no da abasto.")], [("cap:La recepción no da abasto.", .1, 1)], minimo=2.2),
  S("uDybSbfx4A", 3, "cool", minimo=1.6),
  S("LzeclFTWXc", 1, "clean", [(SEB, "Con Recepción IA, su visita se registra en segundos.")], [("k1", 0, .4), ("k1t", .4, .68), ("k2", .68, 1)], blur=True, minimo=4.2),
  S("dz0tQvfu7Q", 2, "clean", [(SEB, "Y el anfitrión recibe el aviso por WhatsApp, con confirmación.")], [("p1", .05, .58), ("p2", .58, 1)], minimo=4.5),
  S("Tr44VDCeH0", 3, "clean", [(SEB, "La visita sabe al instante cuándo la van a atender.")], [("k3", 0, 1)], blur=True),
  S("N3b3gMWdGc", 3, "clean", [(SEB, "Si nadie responde en sesenta segundos, el sistema alerta a recepción.")], [("alert", .2, 1)]),
  S("skn2jzyNMZ", 3, "warm", [(SEB, "Ninguna visita se pierde.")], [("cap:Ninguna visita <b>se pierde</b>.", .1, 1)], minimo=2.8),
  S(None, 0, "clean", [(SEB, "Recepción IA. La recepción que nunca falla.")], [("end", 0, 1)], minimo=4.5),
 ]),
 "explicativo": dict(rate="-3%", seg=[
  S("fizD2gjAlJ", 1, "clean", [(PAO, "Así funciona Recepción IA: el recepcionista inteligente para el lobby de su empresa.")], [("step:CÓMO FUNCIONA|Recepción IA", .08, 1)]),
  S("EmgwSfLYHT", 1, "clean", [(PAO, "Paso uno. La visita llega y se acerca al robot de recepción."), (SEB, "Buenos días, vengo a ver a María Pérez.")], [("step:PASO 1|Llega la visita", .05, 1)]),
  S("LzeclFTWXc", 1, "clean", [(PAO, "En la pantalla toca el directorio, o escribe el nombre de la persona que viene a ver.")], [("k1", 0, .6), ("k1t", .6, 1), ("step:PASO 2|Se registra en la pantalla", 0, 1)], blur=True),
  S("LzeclFTWXc", 6, "clean", [(PAO, "Elige, por ejemplo, a María Pérez, de Finanzas, piso ocho. El registro toma segundos.")], [("k2", 0, 1), ("step:PASO 2|Se registra en la pantalla", 0, 1)], blur=True),
  S("zxmTMP7Z1z", 2, "clean", [(PAO, "Paso tres. María recibe un WhatsApp: llegó su visita, con el nombre y la hora.")], [("p1", .1, 1), ("step:PASO 3|Aviso por WhatsApp", 0, 1)]),
  S("dz0tQvfu7Q", 2, "clean", [(PAO, "Con un solo toque responde: bajo ya, bajo en dos minutos, o no puedo atender.")], [("p1", 0, .55), ("p2", .55, 1), ("step:PASO 3|Aviso por WhatsApp", 0, 1)]),
  S("Tr44VDCeH0", 3, "clean", [(PAO, "Paso cuatro. La visita ve la confirmación en la pantalla, y espera tranquila.")], [("k3", 0, 1), ("step:PASO 4|Confirmación al visitante", 0, 1)], blur=True),
  S("S3rXHOHnGX", 2, "clean", [(PAO, "Paso cinco. Si el aviso no tiene respuesta en sesenta segundos, el sistema alerta a recepción, y una persona toma el caso.")], [("alert", .25, 1), ("step:PASO 5|Respaldo humano", 0, 1)]),
  S("hFFNcSY1u5", 1, "clean", [(PAO, "Además, el robot responde las preguntas frecuentes, solo con la información que su empresa le carga. Si no sabe algo, no lo inventa: lo pasa a recepción.")], [("faq", 0, 1), ("step:EXTRA|Preguntas frecuentes", 0, 1)], blur=True),
  S("RMRP71nS2G", 1, "clean", [(PAO, "Y cuando no está atendiendo, su pantalla muestra los anuncios de la empresa.")], [("ad", 0, 1), ("step:EXTRA|Pantalla de anuncios", 0, 1)], blur=True),
  S("skn2jzyNMZ", 3, "warm", [(PAO, "El resultado: cero avisos perdidos, y cero respuestas inventadas.")], [("cap:Cero avisos perdidos. <b>Cero respuestas inventadas.</b>", .1, 1)]),
  S(None, 0, "clean", [(PAO, "Recepción IA. La recepción que nunca falla.")], [("end", 0, 1)], minimo=4.5),
 ]),
 # Fuente: "Recepción IA · Inversión.html" (flujo, modelo de robot, confiabilidad, piloto e inversión).
 "robot": dict(rate="-3%", seg=[
  S("fizD2gjAlJ", 1, "clean", [(PAO, "Recepción IA: la recepción que nunca falla un aviso.")], [("cap:La recepción que <b>nunca falla</b> un aviso.", .1, 1)], minimo=3.2),
  S("AxSHgGwKa4", 2, "cool", [(PAO, "Hoy, las recepciones pierden visitas, tiempo e imagen.")], [("cap:Las recepciones pierden visitas, tiempo e imagen.", .1, 1)]),
  S("S3rXHOHnGX", 2, "cool", [(PAO, "Avisos que no llegan, datos mal registrados, y respuestas que cambian según quién esté en recepción.")], [("cap:Avisos perdidos · datos mal registrados · <b>respuestas improvisadas</b>", .1, 1)]),
  S("LzeclFTWXc", 1, "clean", [(PAO, "La solución: un robot recepcionista con interfaz de app. Botones grandes para decidir, y voz para conversar.")], [("r0", 0, 1), ("step:EL MODELO|Robot Recepción IA", 0, 1)], blur=True),
  S("LzeclFTWXc", 6, "clean", [(PAO, "La visita elige a quién viene a ver en el directorio...")], [("r1", 0, 1), ("step:PASO 1|Elige a quién visita", 0, 1)], blur=True),
  S("EmgwSfLYHT", 2, "clean", [(PAO, "...y confirma con un sí. El kiosco genera un identificador único, y registra la visita sin duplicados.")], [("r2", 0, 1), ("step:PASO 2|Confirma y se registra", 0, 1)], blur=True),
  S("zxmTMP7Z1z", 2, "clean", [(PAO, "Al anfitrión le llega una plantilla de WhatsApp, y el sistema programa una revisión a los sesenta segundos.")], [("p1", .08, 1), ("step:PASO 3|Aviso por WhatsApp", 0, 1)]),
  S("Tr44VDCeH0", 3, "clean", [(PAO, "Meta confirma cada estado: enviado, entregado y leído. La visita lo ve en tiempo real en el robot, y mientras espera, pide su café con un toque.")], [("r3", 0, 1), ("step:PASO 4|Estado en tiempo real", 0, 1)], blur=True),
  S("N3b3gMWdGc", 3, "clean", [(PAO, "Si a los sesenta segundos no hay entrega, se crea una alerta en recepción, y sale un SMS de respaldo.")], [("alert2", .15, 1), ("step:PASO 5|Respaldo: alerta y SMS", 0, 1)]),
  S("hFFNcSY1u5", 1, "clean", [(PAO, "La inteligencia artificial no inventa. Nunca. Responde solo desde fichas aprobadas por una persona, y cita la fuente. Si no está segura, lo dice y escala a recepción. Cada respuesta queda auditada.")], [("r4", 0, 1), ("step:IA CONFIABLE|No inventa respuestas", 0, 1)], blur=True),
  S("LzeclFTWXc", 3, "clean", [(PAO, "El panel de recepción lo muestra todo en tiempo real: visitas en curso, avisos sin entregar con opción de llamar a la extensión, preguntas escaladas que se vuelven fichas nuevas, y pedidos de café.")], [("dash", 0, 1)], blur=True),
  S("RMRP71nS2G", 1, "clean", [(PAO, "La meta es exigente: menos de un error crítico cada diez mil eventos. Se prueba con cien mil eventos simulados, dos mil preguntas trampa, y ocho semanas de piloto real.")], [("metr", 0, 1)], blur=True),
  S("fizD2gjAlJ", 4, "clean", [(PAO, "El piloto toma diez semanas: flujos y directorio; luego la API, WhatsApp, la app del kiosco y la inteligencia artificial; la simulación; y la instalación con su informe.")], [("plan", 0, 1)], blur=True),
  S("hFFNcSY1u5", 4, "clean", [(PAO, "El costo operativo es de ciento diez a trescientos dólares al mes por robot. El desarrollo es un aporte en especie de los socios, y el costo del robot físico está por confirmar con el proveedor.")], [("cost", 0, 1)], blur=True),
  S("RMRP71nS2G", 5, "clean", [(PAO, "Cada robot tiene cuatro fuentes de ingreso: alquiler, servicio de software, publicidad en pantalla, y artículos promocionales.")], [("ing", 0, 1)], blur=True),
  S("fizD2gjAlJ", 8, "clean", [(PAO, "Con alquiler, publicidad y una promoción al mes, un robot podría generar unos mil quinientos cincuenta dólares mensuales. Son supuestos para discusión, que el piloto debe validar.")], [("rent", 0, 1)], blur=True),
  S("hFFNcSY1u5", 8, "clean", [(PAO, "La proyección: de un robot a cuarenta en Caracas, en tres años, en Chacao, Las Mercedes, El Rosal, Altamira y La Castellana.")], [("crec", 0, 1)], blur=True),
  S("skn2jzyNMZ", 3, "warm", [(PAO, "Cero avisos perdidos. Cero respuestas inventadas.")], [("cap:Cero avisos perdidos. <b>Cero respuestas inventadas.</b>", .1, 1)]),
  S(None, 0, "clean", [(PAO, "Cuando nuestra inteligencia artificial no sabe algo, lo dice, y le comunica con una persona. Recepción IA.")], [("end2", 0, 1)], minimo=6),
 ]),
}
G = GUIONES[CUAL]
LEAD, TAIL, GAP = 0.35, 0.55, 0.25


def run(args):
    subprocess.run(args, check=True)


def dur(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True)
    return float(r.stdout.strip())


# 1 · gráficos
q = lambda x: urllib.parse.quote(x, safe="")
specs = sorted({o[0] for s in G["seg"] for o in s["ov"]})
nombres, lista = {}, []
for i, sp in enumerate(specs):
    nm = "ov%02d" % i
    nombres[sp] = nm
    if sp.startswith("cap:"):
        h = "s=cap&t=" + q(sp[4:])
    elif sp.startswith("step:"):
        n, t = sp[5:].split("|")
        h = "s=step&n=" + q(n) + "&t=" + q(t)
    else:
        h = "s=" + sp
    lista.append({"nombre": nm, "hash": h})
json.dump(lista, open(os.path.join(OV, "lista.json"), "w", encoding="utf-8"), ensure_ascii=False)
run(["node", os.path.join(AQUI, "render.js"), os.path.join(OV, "lista.json"), OV])


# 2 · voces
async def tts(voz, texto, mp3):
    await edge_tts.Communicate(texto, voz, rate=G["rate"]).save(mp3)

voces = []  # por segmento: lista de (wav, dur)
for i, s in enumerate(G["seg"]):
    vs = []
    for j, (voz, texto) in enumerate(s["vo"]):
        base = os.path.join(VO, "s%02d_%d" % (i, j))
        if not os.path.exists(base + ".mp3"):
            asyncio.run(tts(voz, texto, base + ".mp3"))
        run(["ffmpeg", "-y", "-v", "error", "-i", base + ".mp3", "-af",
             "highpass=f=70,acompressor=threshold=-20dB:ratio=2.5,silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse,loudnorm=I=-16:TP=-1.5",
             "-ar", str(SR), "-ac", "1", base + ".wav"])
        vs.append((base + ".wav", dur(base + ".wav")))
    voces.append(vs)

# 3 · segmentos de video
tiempos, t = [], 0.0
for i, s in enumerate(G["seg"]):
    habla = sum(d for _, d in voces[i]) + GAP * max(0, len(voces[i]) - 1)
    D = round(max(s["minimo"], LEAD + habla + TAIL) * FPS) / FPS
    tiempos.append((t, D)); t += D
    out = os.path.join(SEG, "s%02d.mp4" % i)
    if s["bg"]:
        src = os.path.join(RAW, s["bg"] + ".mp4")
        ins = ["-stream_loop", "-1", "-ss", str(s["ss"]), "-i", src]
        base = (f"[0:v]scale=2112:1188:force_original_aspect_ratio=increase,crop=2112:1188,fps={FPS},"
                f"crop=1920:1080:x='96*t/{D}':y='54*t/{D}',{GRADE[s['g']]}")
        if s["blur"]:
            base += ",gblur=sigma=18,eq=brightness=-0.12"
    else:
        ins = ["-f", "lavfi", "-i", f"color=c=black:s=1920x1080:r={FPS}"]
        base = "[0:v]null"
    fc, last = [base + "[v0]"], "v0"
    for k, (sp, f0, f1) in enumerate(s["ov"]):
        ins += ["-loop", "1", "-t", str(D), "-i", os.path.join(OV, nombres[sp] + ".png")]
        a, b = f0 * D, f1 * D
        fc.append(f"[{k+1}:v]format=rgba,fade=in:st={a:.3f}:d=0.25:alpha=1[o{k}]")
        fc.append(f"[{last}][o{k}]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[v{k+1}]")
        last = f"v{k+1}"
    run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(fc), "-map", f"[{last}]",
         "-t", str(D), "-r", str(FPS), "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-an", out])
    print("seg", i, round(D, 2))
TOTAL = t

# 4 · audio: voz + música (atenuada bajo la voz)
N = int(SR * TOTAL)
voz = np.zeros(N)
for i, vs in enumerate(voces):
    at = tiempos[i][0] + LEAD
    for wav, d in vs:
        _, x = wavfile.read(wav)
        x = x.astype(np.float64) / 32768.0
        j = int(at * SR); voz[j:j + len(x)] += x[: max(0, N - j)]
        at += d + GAP

rng = np.random.default_rng(3)
BPM = 100; beat = 60 / BPM
nota = lambda m: 440 * 2 ** ((m - 69) / 12)
acordes = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
mus = np.zeros(N); tt = np.arange(N) / SR
compas = 4 * beat
for c in range(int(TOTAL / compas) + 1):
    t0 = c * compas; ac = acordes[c % 4]
    i0, i1 = int(t0 * SR), min(N, int((t0 + compas + 0.3) * SR))
    if i0 >= N: break
    x = tt[i0:i1] - t0
    env = np.minimum(1, x / 0.4) * np.exp(-x / 3.5)
    for m in ac:  # colchón
        f = nota(m)
        mus[i0:i1] += 0.05 * env * (np.sin(2 * np.pi * f * x) + 0.3 * np.sin(2 * np.pi * 2.003 * f * x))
    f = nota(ac[0] - 24)  # bajo
    mus[i0:i1] += 0.09 * np.exp(-x / 1.2) * np.sin(2 * np.pi * f * x)
    for k in range(8):  # pulso arpegiado en corcheas
        ts = t0 + k * beat / 2; j = int(ts * SR)
        if j >= N: break
        L = min(N - j, int(0.35 * SR)); y = np.arange(L) / SR
        mus[j:j + L] += 0.035 * np.exp(-y / 0.09) * np.sin(2 * np.pi * nota(ac[k % 3] + 12) * y)
    if c % 2 == 0:  # golpe suave
        L = min(N - i0, int(0.25 * SR)); y = np.arange(L) / SR
        mus[i0:i0 + L] += 0.12 * np.exp(-y / 0.06) * np.sin(2 * np.pi * (90 - 40 * y) * y)
# atenuación bajo la voz
K = int(0.25 * SR)  # media móvil por suma acumulada (np.convolve directo tarda minutos)
cs = np.concatenate([[0], np.cumsum(np.abs(voz))])
idx = np.arange(N)
venv = (cs[np.minimum(N, idx + K // 2)] - cs[np.maximum(0, idx - K // 2)]) / K
duck = 1 - 0.6 * np.clip(venv * 12, 0, 1)
mus *= duck * np.clip((TOTAL - tt) / 1.5, 0, 1) * np.clip(tt / 0.8, 0, 1)
mix = voz + mus
mix /= max(1.0, np.abs(mix).max() / 0.95)
wavfile.write(os.path.join(W, CUAL + "_mix.wav"), SR, (mix * 32767).astype(np.int16))

# 5 · unir
lista = os.path.join(SEG, "lista.txt")
open(lista, "w").write("\n".join(f"file 's{i:02d}.mp4'" for i in range(len(G["seg"]))))
final = os.path.join(W, f"RecepcionIA_{CUAL}.mp4")
run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lista, "-i", os.path.join(W, CUAL + "_mix.wav"),
     "-vf", f"fade=in:st=0:d=0.5,fade=out:st={TOTAL-0.6:.2f}:d=0.6", "-c:v", "libx264", "-crf", "19", "-preset", "medium",
     "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final])
json.dump({"total": round(TOTAL, 2), "segmentos": [[round(a, 2), round(b, 2)] for a, b in tiempos]},
          open(os.path.join(W, CUAL + "_tiempos.json"), "w"), indent=1)
print("LISTO", final, round(TOTAL, 1), "s")

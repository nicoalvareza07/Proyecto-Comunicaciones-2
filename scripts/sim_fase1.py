"""Simulación numérica del flujograma Grupo03_S4_{QPSK,16QAM}_AWGN.grc.

Reproduce la misma cadena del GRC del curso:
  bits aleatorios -> agrupación en k=log2(M) bits (MSB primero) -> tabla de constelación
  -> interpolación rectangular (h=[1]*Sps) -> + ruido complejo gaussiano de amplitud noise_amp
y genera las figuras de PSD, constelación y envolvente compleja para las 4 pruebas,
además de la tabla de pruebas y la curva BER teórica/simulada.
Uso: python3 sim_fase1.py <carpeta_repo>
"""
import sys, os, csv, math
import numpy as np
from scipy import signal, special
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = sys.argv[1]
FIG = os.path.join(REPO, "figures")
DATA = os.path.join(REPO, "data", "tablas_de_pruebas")

Rs, Sps = 32000, 8
fs = Rs * Sps
C_Q, C_16, INK, INK2, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.6, "axes.titleweight": "bold",
                     "figure.dpi": 150, "savefig.bbox": "tight"})

QPSK = np.array([1+0j, 0+1j, 0-1j, -1+0j])
QAM16 = np.array([-3-3j, -3-1j, -3+3j, -3+1j, -1-3j, -1-1j, -1+3j, -1+1j,
                  3-3j, 3-1j, 3+3j, 3+1j, 1-3j, 1-1j, 1+3j, 1+1j]) / math.sqrt(10)
MODS = {"QPSK": (QPSK, C_Q), "16QAM": (QAM16, C_16)}
TESTS = [("A", "Referencia", 0.0), ("B", "Suave", 0.10), ("C", "Media", 0.25), ("D", "Fuerte", 0.50)]


def tx(table, nsym, rng):
    k = int(math.log2(len(table)))
    bits = rng.integers(0, 2, nsym * k)
    idx = bits.reshape(-1, k) @ (1 << np.arange(k - 1, -1, -1))  # MSB primero
    sym = table[idx]
    return bits, idx, np.repeat(sym, Sps)                          # pulso rectangular


def noise(n, amp, rng):
    # Igual que analog.noise_source_c: potencia total = amp^2
    return amp * (rng.standard_normal(n) + 1j * rng.standard_normal(n)) / math.sqrt(2)


def detect(table, y):
    # Receptor ideal: integrar-y-descargar (filtro acoplado rectangular) + mínima distancia
    z = y.reshape(-1, Sps).mean(axis=1)
    return np.argmin(np.abs(z[:, None] - table[None, :]) ** 2, axis=1)


def bits_of(idx, k):
    return ((idx[:, None] >> np.arange(k - 1, -1, -1)) & 1).ravel()


def ber_theory(mod, ebn0_db):
    g = 10 ** (np.asarray(ebn0_db) / 10)
    Q = lambda x: 0.5 * special.erfc(x / math.sqrt(2))
    if mod == "QPSK":
        return Q(np.sqrt(2 * g))
    return 0.75 * Q(np.sqrt(0.8 * g)) * 1  # 16QAM Gray (aprox. vecinos más cercanos), mismo término dominante


def main():
    rng = np.random.default_rng(2026)
    rows = []
    sim = {}
    for mod, (table, col) in MODS.items():
        k = int(math.log2(len(table)))
        for code, name, a in TESTS:
            bits, idx, s = tx(table, 200000, rng)
            y = s + noise(len(s), a, rng)
            sim[(mod, code)] = y[:200000]
            Ps = float(np.mean(np.abs(s) ** 2))
            if a > 0:
                snr_s = 10 * math.log10(Ps / a ** 2)
                esn0 = 10 * math.log10(Ps * Sps / a ** 2)
                ebn0 = esn0 - 10 * math.log10(k)
            else:
                snr_s = esn0 = ebn0 = float("inf")
            rx = detect(table, y)
            ser = float(np.mean(rx != idx))
            ber = float(np.mean(bits_of(rx, k) != bits))
            # decisión muestra a muestra (lo que "se ve" en el Constellation Sink)
            yi = y[::1][:400000]
            si = np.repeat(idx, Sps)[:400000]
            ser_raw = float(np.mean(np.argmin(np.abs(yi[:, None] - table[None, :]) ** 2, axis=1) != si))
            rows.append(dict(prueba=code, severidad=name, modulacion=mod, M=len(table), k=k, Rs_sym_s=Rs,
                             Sps=Sps, fs_S_s=fs, Rb_b_s=Rs * k, pulso="rectangular h=[1]*Sps", noise_amp=a,
                             P_senal=round(Ps, 4), SNR_muestra_dB=round(snr_s, 2), EsN0_dB=round(esn0, 2),
                             EbN0_dB=round(ebn0, 2), SER_muestra_a_muestra=round(ser_raw, 5),
                             SER_filtro_acoplado=ser, BER_filtro_acoplado=ber,
                             BER_teorica=float(ber_theory(mod, ebn0)) if a > 0 else 0.0,
                             bits_simulados=len(bits)))
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "tabla_pruebas_QPSK_vs_16QAM.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    # ---------- Constelaciones: rejilla 2x4 ----------
    fig, ax = plt.subplots(2, 4, figsize=(13, 6.6))
    for r, (mod, (table, col)) in enumerate(MODS.items()):
        for c, (code, name, a) in enumerate(TESTS):
            y = sim[(mod, code)][:2048]  # mismo tamaño del QT GUI Constellation Sink
            A = ax[r, c]
            A.scatter(y.real, y.imag, s=4, color=col, alpha=0.55, linewidths=0)
            A.scatter(table.real, table.imag, s=26, facecolors="none", edgecolors=INK, linewidths=0.9)
            A.set_xlim(-1.5, 1.5); A.set_ylim(-1.5, 1.5); A.set_aspect("equal")
            A.set_title(f"{mod} · Prueba {code} ({name})\nnoise_amp = {a:.2f}", fontsize=9)
            if c == 0: A.set_ylabel("Cuadratura Q [V]")
            if r == 1: A.set_xlabel("En fase I [V]")
    fig.suptitle("Constelación recibida (2048 muestras, igual al QT GUI Constellation Sink) — Rs = 32 ksym/s, Sps = 8",
                 fontsize=11, fontweight="bold")
    fig.savefig(os.path.join(FIG, "constelacion_o_fsk", "constelaciones_QPSK_vs_16QAM_4pruebas.png")); plt.close(fig)
    for mod, (table, col) in MODS.items():
        for code, name, a in TESTS:
            y = sim[(mod, code)][:2048]
            fig, A = plt.subplots(figsize=(4.4, 4.4))
            A.scatter(y.real, y.imag, s=5, color=col, alpha=0.6, linewidths=0, label="Muestras recibidas")
            A.scatter(table.real, table.imag, s=34, facecolors="none", edgecolors=INK, linewidths=1, label="Punto ideal")
            A.set_xlim(-1.5, 1.5); A.set_ylim(-1.5, 1.5); A.set_aspect("equal")
            A.set_xlabel("En fase I [V]"); A.set_ylabel("Cuadratura Q [V]")
            A.set_title(f"Constelación {mod} — Prueba {code} ({name}), noise_amp = {a:.2f}", fontsize=9)
            A.legend(loc="upper right", fontsize=7, framealpha=0.9)
            fig.savefig(os.path.join(FIG, "constelacion_o_fsk", f"constelacion_{mod}_prueba{code}_{name}.png")); plt.close(fig)

    # ---------- PSD ----------
    def psd(y):
        f, P = signal.welch(y[:200000], fs=fs, window="blackmanharris", nperseg=1024, return_onesided=False)
        f = np.fft.fftshift(f); P = np.fft.fftshift(P)
        return f / 1e3, 10 * np.log10(P / P.max() + 1e-14)
    fig, ax = plt.subplots(1, 4, figsize=(15, 3.8), sharey=True)
    for c, (code, name, a) in enumerate(TESTS):
        for mod, (table, col) in MODS.items():
            f, P = psd(sim[(mod, code)])
            ax[c].plot(f, P, color=col, lw=1.4, label=mod)
        ax[c].set_title(f"Prueba {code} ({name}) — noise_amp = {a:.2f}", fontsize=9)
        ax[c].set_xlabel("Frecuencia [kHz]"); ax[c].set_ylim(-80, 3); ax[c].set_xlim(-128, 128)
        for x in (-Rs/1e3, Rs/1e3):
            ax[c].axvline(x, color=INK2, lw=0.8, ls="--")
    ax[0].set_ylabel("PSD relativa [dB]"); ax[0].legend(loc="lower left", fontsize=8)
    ax[0].annotate("nulos en ±Rs = ±32 kHz", xy=(32, -40), xytext=(40, -12), fontsize=7, color=INK2,
                   arrowprops=dict(arrowstyle="->", color=INK2, lw=0.7))
    fig.suptitle("PSD de la señal recibida: QPSK y 16QAM ocupan el mismo ancho de banda (lóbulo principal 2·Rs = 64 kHz)",
                 fontsize=11, fontweight="bold")
    fig.savefig(os.path.join(FIG, "psd", "psd_QPSK_vs_16QAM_4pruebas.png")); plt.close(fig)
    for mod, (table, col) in MODS.items():
        for code, name, a in TESTS:
            f, P = psd(sim[(mod, code)])
            fig, A = plt.subplots(figsize=(6.4, 3.4))
            A.plot(f, P, color=col, lw=1.4)
            A.set_xlim(-128, 128); A.set_ylim(-80, 3)
            A.set_xlabel("Frecuencia [kHz]"); A.set_ylabel("PSD relativa [dB]")
            A.set_title(f"PSD {mod} — Prueba {code} ({name}), noise_amp = {a:.2f}", fontsize=9)
            fig.savefig(os.path.join(FIG, "psd", f"psd_{mod}_prueba{code}_{name}.png")); plt.close(fig)

    # ---------- Señal temporal ----------
    t = np.arange(Sps * 16) / fs * 1e3
    fig, ax = plt.subplots(2, 2, figsize=(12, 5.6), sharex=True)
    for r, (mod, (table, col)) in enumerate(MODS.items()):
        for c, code in enumerate(["A", "C"]):
            name, a = {x[0]: (x[1], x[2]) for x in TESTS}[code]
            y = sim[(mod, code)][:len(t)]
            A = ax[r, c]
            A.plot(t, y.real, color=col, lw=1.3, label="I(t)")
            A.plot(t, y.imag, color=INK2, lw=1.1, ls="--", label="Q(t)")
            A.set_ylim(-1.6, 1.6)
            A.set_title(f"{mod} — Prueba {code} ({name}), noise_amp = {a:.2f}", fontsize=9)
            if c == 0: A.set_ylabel("Amplitud [V]")
            if r == 1: A.set_xlabel("Tiempo [ms]")
            A.legend(loc="upper right", fontsize=7, ncol=2)
    fig.suptitle("Envolvente compleja (16 símbolos, Ts = 31.25 µs): QPSK toma 4 estados de fase (±1 en I o en Q), 16QAM usa 4 niveles por eje",
                 fontsize=11, fontweight="bold")
    fig.savefig(os.path.join(FIG, "senal_temporal", "envolvente_QPSK_vs_16QAM.png")); plt.close(fig)

    # ---------- Curva BER ----------
    eb = np.arange(0, 16.01, 0.25)
    fig, A = plt.subplots(figsize=(7.2, 4.6))
    for mod, (table, col) in MODS.items():
        A.semilogy(eb, ber_theory(mod, eb), color=col, lw=2, label=f"{mod} teórica")
    # Monte Carlo del mismo modelo (filtro acoplado)
    for mod, (table, col) in MODS.items():
        k = int(math.log2(len(table)))
        pts = []
        for e in range(0, 15, 2):
            a = math.sqrt(Sps / (k * 10 ** (e / 10)))
            bits, idx, s = tx(table, 120000, rng)
            rx = detect(table, s + noise(len(s), a, rng))
            b = np.mean(bits_of(rx, k) != bits)
            if b > 0: pts.append((e, b))
        pts = np.array(pts)
        A.semilogy(pts[:, 0], pts[:, 1], "o", ms=7, color=col, mec="white", mew=1.5, label=f"{mod} simulada")
    A.axhline(1e-3, color=INK2, lw=0.8, ls=":")
    for mod, x in (("QPSK", 6.79), ("16QAM", 10.5)):
        A.annotate(f"{mod}: {x:.1f} dB", xy=(x, 1e-3), xytext=(x - 0.2, 2.2e-5), fontsize=8, color=INK,
                   ha="center", arrowprops=dict(arrowstyle="->", color=INK2, lw=0.7))
    A.text(0.3, 1.25e-3, "BER = 10⁻³ (criterio del proyecto)", fontsize=8, color=INK2)
    A.set_ylim(1e-6, 0.5); A.set_xlim(0, 16)
    A.set_xlabel("Eb/N0 [dB]"); A.set_ylabel("BER")
    A.set_title("BER vs Eb/N0: 16QAM necesita ≈3.7 dB más que QPSK para la misma BER", fontsize=10)
    A.legend(fontsize=8, loc="lower left")
    fig.savefig(os.path.join(FIG, "diagramas_tecnicos", "curva_BER_teorica_QPSK_vs_16QAM.png")); plt.close(fig)

    for r in rows:
        print(r["modulacion"], r["prueba"], r["noise_amp"], r["EbN0_dB"], "SERraw=%.4f" % r["SER_muestra_a_muestra"],
              "BER=%.2e" % r["BER_filtro_acoplado"], "teo=%.2e" % r["BER_teorica"])


if __name__ == "__main__":
    main()

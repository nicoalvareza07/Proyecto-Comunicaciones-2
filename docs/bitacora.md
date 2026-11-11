# Bitácora del proyecto · Grupo 3 · Escenario S4

Registro de decisiones, cambios, dificultades y soluciones, en orden cronológico.

## 8 de octubre de 2026 · Inicio
- Se recibe la guía del Proyecto Integrador. El equipo revisa los seis escenarios.

## 15 de octubre de 2026 · Decisión técnica ciega
- **Escenario:** S4, aumentar la tasa de datos sin aumentar la tasa de símbolos.
- **Problema:** P1, aumentar Rb manteniendo aproximadamente Rs y BW.
- **Estrategia:** comparar QPSK y 16QAM con la misma Rs, usando `Modulaciones_basadas_en_constelaciones_AWGN.grc`.
- **Parámetros:** paquete A, Rs = 32 ksym/s, Sps = 8, fs = 256 kS/s. Se comprobó que fs = Rs·Sps = 32 000 × 8 = 256 000.
- **Perturbación:** solo AWGN. **Variable:** nivel de ruido común en 4 pruebas.
- **Observables:** PSD, constelación y Rb/Rs/BW calculados.
- **Hipótesis H1:** con la misma Rs, 16QAM transporta más bits/s, pero es visualmente más sensible al mismo ruido.
- Se entregan la ficha (PDF) y el JSON en el aula virtual.

## Fase 1–2 · Simulación en GNU Radio
- Se copia el GRC base dos veces: `Grupo03_S4_QPSK_AWGN.grc` y `Grupo03_S4_16QAM_AWGN.grc`. El original se conserva sin cambios.
- **Decisión: normalizar la energía.** La tabla 16QAM de la guía (±1, ±3) tiene energía promedio 10, mientras que la de QPSK tiene 1. Si no se normaliza, con el mismo `noise_amp` 16QAM parecería más robusta, lo cual es falso. Se divide la tabla 16QAM entre √10 para que Es = 1 en las dos.
- **Decisión: mapeo Gray en 16QAM.** Se usa el mismo orden de la tabla del laboratorio de HackRF (Fase 4), donde símbolos vecinos difieren en un solo bit. Así la simulación y el hardware usan la misma constelación.
- **Decisión: niveles de ruido.** 0, 0.10, 0.25 y 0.50 (dentro del rango del control del GRC, 0–0.5). Con 0.50, 16QAM ya presenta errores (BER ≈ 4·10⁻³) y QPSK todavía no, lo que muestra el compromiso del escenario.
- Se fijan los ejes del Constellation Sink en ±1.5 para que las capturas sean comparables entre pruebas.
- **Dificultad:** la constelación del GRC muestra todas las muestras (8 por símbolo) y no las decisiones del receptor. Por eso a la vista parece peor que la BER real. Se explicó la diferencia entre la SNR por muestra (1/noise_amp²) y la Es/N0 después del filtro acoplado (Sps/noise_amp²), que es 9 dB mayor.
- Se calculó la BER con un receptor ideal (integrar y descargar) en Python para cuantificar lo que se ve en las constelaciones. Los resultados coinciden con la teoría: 16QAM en la prueba D da 4.25·10⁻³ simulada frente a 4.29·10⁻³ teórica.

## Guía 2 · Transmisor conformado y receptor
- La Guía 2 introduce el filtro RRC (β = 0.35, span = 11) en transmisión y pide diseñar el receptor: filtro acoplado RRC, diagrama de ojo, muestreo (Keep One in N / Symbol Sync) y decisión (Constellation Decoder).
- Con RRC, el ancho de banda baja de 64 kHz (lóbulo principal rectangular) a (1+β)·Rs ≈ 43.2 kHz.

## 5 de noviembre de 2026 · Laboratorio con HackRF One
- TX en el PC #1 y RX en el PC #3, enlace por antenas a 960 MHz, con `LAB_TX/RX_16QAM_HackRF_MEJORADO.grc`.
- Parámetros del laboratorio: Rs = 8 ksym/s, Sps = 8, bb_rate = 64 kS/s, β = 0.5, radio a 2 MS/s con desplazamiento digital de 200 kHz. **Decisión:** en hardware se usa una Rs menor que en la simulación, para que el HackRF recupere el enlace de forma estable. Se documenta como un cambio respecto a la ficha.
- **Resultado:** BER ≈ 0.34 %, EVM ≈ 7.4 %, 81 % de tramas con CRC correcto. El receptor corrige rotaciones de 90°, 180° y 270° de la constelación usando el preámbulo.
- **Comportamiento inesperado:** en otra captura el receptor decodificó un mensaje distinto ("PONGAN BBY WOW"), con BER ≈ 29 % y EVM ≈ 143 %. Probablemente se enganchó con la señal de otro grupo en la misma frecuencia, o se cambió el mensaje en el TX. Esto muestra la importancia del preámbulo y del CRC para validar las tramas.

## Fase 4 · Curva BER vs Eb/N0
- _[PENDIENTE] Integrar `e_EbN0_Sweep` (después del remuestreo a 64 kS/s) y `e_BER_Curve`, con Rb = 32 000 y bb_rate = 64 000._
- _[PENDIENTE] Alinear los bits Tx/Rx, obtener `curva_BER.csv` y comparar con la curva teórica de 16QAM en BER = 10⁻³ (criterio: penalización ≤ 2 dB)._

## Uso de IA
- Herramienta: Claude (asistente de IA).
- Propósito: organizar el repositorio, programar la simulación en Python que reproduce el GRC, dibujar el escenario y el diagrama de bloques, y redactar borradores.
- Validación humana: _[PENDIENTE: describir cómo el equipo revisó cada resultado]_.

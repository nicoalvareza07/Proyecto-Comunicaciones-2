# Preguntas previas (Guía, sección 1.2) · Grupo 3 · Escenario S4

**1. ¿Qué situación profesional representa el escenario?**
Un nodo de inspección en una planta (cámara y sensores sobre una banda transportadora) envía datos a la sala de control por un canal inalámbrico de ancho fijo. La planta necesita enviar más información, por ejemplo más imágenes o más variables, pero no puede pedir más espectro. La salida es meter más bits en cada símbolo.

**2. ¿Cuál es el fenómeno físico que puede degradar la comunicación?**
El ruido térmico del receptor y del entorno, modelado como ruido aditivo blanco gaussiano (AWGN). Desplaza aleatoriamente los puntos de la constelación. Si el desplazamiento supera la mitad de la distancia entre puntos vecinos, el receptor decide mal el símbolo.

**3. ¿Qué información se quiere transmitir?**
Datos digitales del proceso. En simulación son bits aleatorios equiprobables. En hardware es una trama conocida (preámbulo + "LAB GNU RADIO 16QAM HACKRF 2026" + CRC32), que permite medir la BER.

**4. ¿Qué modulación se selecciona y por qué?**
16QAM, porque transporta k = 4 bits por símbolo. Con la misma Rs entrega el doble de bits que QPSK sin aumentar el ancho de banda.

**5. ¿Qué otra modulación se consideró y por qué no se escogió?**
QPSK (k = 2). Es más robusta, porque su distancia mínima es 1.41 frente a 0.63 de 16QAM con Es = 1. Pero con la misma Rs solo alcanza la mitad de la tasa de bits, así que no resuelve el problema del escenario. Se mantiene como referencia de comparación.

**6. ¿Cuál es la tasa de símbolos Rs?**
32 000 símbolos/s en simulación. En el enlace con HackRF se usó 8 000 símbolos/s.

**7. ¿Cuál es la tasa de bits Rb?**
Rb = Rs · k. QPSK: 32 000 × 2 = 64 kb/s. 16QAM: 32 000 × 4 = 128 kb/s. En HackRF: 8 000 × 4 = 32 kb/s.

**8. ¿Cuál es el número de muestras por símbolo (SPS)?**
Sps = 8.

**9. ¿Cuál es la tasa de muestreo fs y cómo se obtiene?**
fs = Rs · Sps = 32 000 × 8 = 256 000 muestras/s, igual a `samp_rate` en el GRC. En HackRF: 8 000 × 8 = 64 000 muestras/s en banda base.

**10. ¿Cuál es el ancho de banda esperado?**
Es el mismo para las dos modulaciones, porque depende de Rs y del pulso, no de M. Con pulso rectangular, el lóbulo principal mide 2·Rs = 64 kHz (nulos en ±32 kHz). Con RRC β = 0.35 (Guía 2), BW ≈ (1+β)·Rs ≈ 43.2 kHz. En HackRF (β = 0.5, Rs = 8 k): BW ≈ 12 kHz.

**11. ¿Qué variable se modificará en el experimento?**
Solo `noise_amp`, la amplitud del ruido gaussiano complejo: 0 (referencia), 0.10 (suave), 0.25 (media) y 0.50 (fuerte). Se aplica el mismo valor a QPSK y a 16QAM.

**12. ¿Qué gráfica o evidencia permitirá observar el fenómeno?**
- La constelación muestra la dispersión de los puntos.
- La PSD muestra el mismo ancho de banda y el piso de ruido.
- La envolvente compleja muestra los niveles de I y Q.
- La tabla Rb/Rs/BW y la BER calculada cuantifican el resultado.
- En la Fase 4, la curva BER vs Eb/N0 medida con HackRF.

**13. ¿Qué se espera que ocurra antes de hacer la simulación?**
Las dos PSD tendrán la misma forma y el mismo ancho, pero 16QAM llevará el doble de bits. Con el mismo ruido, las nubes de 16QAM se tocarán antes, porque sus puntos están más cerca. Por teoría, para BER = 10⁻³ QPSK necesita Eb/N0 ≈ 6.8 dB y 16QAM ≈ 10.5 dB, unos 3.7 dB más.

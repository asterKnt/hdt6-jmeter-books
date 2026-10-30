# Resultados de Pruebas de Carga - HDT 6

Pruebas de rendimiento y carga ejecutadas contra el API de libros utilizando Apache JMeter 5.6.3 en modo no grafico (CLI), con tiempos de 10 segundos de ramp-up y 60 segundos de carga sostenida por cada nivel.

---

## Tabla Comparativa de Resultados

| Usuarios | Muestras | Solicitudes por segundo | p50 | p95 | p99 | Errores | Código de salida de la puerta |
|---|---|---|---|---|---|---|---|
| 10 | 39268 | 561.32 | 23.00 ms | 44.00 ms | 58.00 ms | 0.00% | 0 |
| 50 | 35853 | 511.18 | 123.00 ms | 173.00 ms | 197.00 ms | 0.00% | 1 |
| 100 | 34867 | 495.09 | 242.00 ms | 343.00 ms | 398.99 ms | 0.00% | 1 |
| 200 | 32741 | 461.86 | 526.00 ms | 686.00 ms | 810.98 ms | 0.00% | 1 |
| 500 | 31415 | 434.25 | 1404.00 ms | 1699.00 ms | 3023.00 ms | 0.00% | 1 |

---

## Respuestas al Análisis de Rendimiento

### 1. ¿En qué nivel de usuarios el p95 pasó de 100 ms por primera vez?
El percentil 95 superó los 100 ms por primera vez en el nivel de **50 usuarios**. 

- En el nivel de **10 usuarios**, el p95 se mantuvo en **44.00 ms**, satisfaciendo holgadamente la política de calidad (`p95 <= 100 ms`, `errores <= 1.0%`) y arrojando código de salida `0` en la puerta.
- Al incrementar la concurrencia a **50 usuarios**, el p95 ascendió a **173.00 ms**, superando el umbral permitido en un 73% y provocando que la puerta de calidad terminara con código de error `1`.

### 2. ¿Qué pasó con las solicitudes por segundo entre 200 y 500 usuarios?
Entre 200 y 500 usuarios, el rendimiento del sistema (*throughput*) no aumentó; por el contrario, se degradó ligeramente pasando de **461.86 solicitudes/s** (con 200 usuarios) a **434.25 solicitudes/s** (con 500 usuarios), a pesar de multiplicar la concurrencia por 2.5 veces.

Simultáneamente, la latencia mediana (p50) creció de forma lineal/cuadrática de **526.00 ms** a **1404.00 ms**, y el p95 pasó de **686.00 ms** a **1699.00 ms**. Este comportamiento describe el punto de **saturación y contención** (*thrashing* y encolamiento de sockets TCP) del servidor: el servicio alcanzó su techo de procesamiento en el bucle de eventos, de modo que inyectar más usuarios concurrentes no produjo mayor volumen de trabajo útil por segundo, sino únicamente retrasos por tiempo de espera en cola de conexión.

### 3. ¿Cuánto CPU usaron el API y JMeter durante la corrida de 500 usuarios, cuántos núcleos tiene la máquina, y cuál de los dos procesos puso el límite?
- **Especificaciones del hardware:** La máquina cuenta con un procesador **13th Gen Intel(R) Core(TM) i7-1355U** con **12 núcleos lógicos** (10 núcleos físicos: 2 núcleos de alto rendimiento P-Cores con Hyper-Threading y 8 núcleos de eficiencia E-Cores).
- **Consumo de CPU del API (`api.py` / Uvicorn):** Promedió un **91.4%** de utilización de un núcleo lógico, manteniendo picos sostenidos de entre **92.0% y 94.0%**.
- **Consumo de CPU de JMeter (JVM / Java):** Promedió un **116.5%** de CPU (distribuido a través de múltiples hilos en varios núcleos), con picos de hasta **313.0%** (equivalente a ~3.1 núcleos lógicos).
- **Proceso limitante (cuello de botella):** El proceso que impuso el límite en la prueba fue el **API**. Debido a que el servidor FastAPI/Uvicorn se ejecuta como un proceso monolítico de CPython sujeto al Global Interpreter Lock (GIL) y atado a un único event loop asíncrono, saturó por completo la capacidad de cómputo de 1 núcleo lógico (~92-94%), impidiendo atender las solicitudes con mayor celeridad. En contraste, JMeter operando sobre OpenJDK 21 escaló de manera multihilo sin dificultad y el sistema anfitrión aún disponía de holgura en los restantes 11 núcleos lógicos.

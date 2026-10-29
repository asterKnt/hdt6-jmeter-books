<div align="center">

<h1>HDT 6: pruebas de carga con JMeter</h1>

<p><b>Un plan de JMeter contra el API de libros de la clase, corrido a cinco niveles de usuarios, y una puerta que decide si cada corrida pasa.</b></p>

<p>
<img alt="Curso" src="https://img.shields.io/badge/UFM-Calidad%20y%20Automatizaci%C3%B3n-2E5D4B">
<img alt="JMeter" src="https://img.shields.io/badge/JMeter-5.6.3-D22128">
<img alt="Python" src="https://img.shields.io/badge/Python-3.12-545A4E">
<img alt="Entrega" src="https://img.shields.io/badge/entrega-jue%205%20nov%2C%2023%3A59-234838">
</p>

<p>
<a href="https://danihrndzld.github.io/hdt6-jmeter-books/">Guía de instalación</a> &nbsp;|&nbsp;
<a href="#el-api">El API</a> &nbsp;|&nbsp;
<a href="#qué-se-pide">Qué se pide</a> &nbsp;|&nbsp;
<a href="#entrega">Entrega</a>
</p>

</div>

<details open>
<summary>Contenido</summary>

- [Acerca de](#acerca-de)
- [Requisitos](#requisitos)
- [El API](#el-api)
- [Qué se pide](#qué-se-pide)
  - [1. Plugins](#1-plugins)
  - [2. El plan](#2-el-plan)
  - [3. Corridas](#3-corridas)
  - [4. La puerta](#4-la-puerta)
  - [5. Resultados](#5-resultados)
- [Entrega](#entrega)

</details>

---

## Acerca de

Este repositorio trae el API de libros que se usó en clase con curl, Bruno y JMeter, y un archivo `books.csv` con libros para crear. La hoja pide instalar dos plugins de JMeter, armar un plan de carga, correrlo sin interfaz gráfica a cinco niveles de usuarios y escribir la puerta que un pipeline usaría para decidir si el resultado pasa, porque JMeter termina con código 0 aunque todas las solicitudes fallen.

## Requisitos

| Herramienta | Versión | Para |
|---|---|---|
| Apache JMeter | 5.6.3 | generar la carga |
| Java | la que pide JMeter 5.6.3 | correr JMeter |
| uv | cualquiera reciente | correr el API sin instalar nada más |
| jq o Python | cualquiera | leer los resultados en la puerta |

## El API

```bash
uv run api.py      # http://127.0.0.1:8000
```

El estado vive en memoria. `POST /reset` devuelve los datos a los tres libros iniciales, y apagar el API hace lo mismo.

| Método | Ruta | Éxito | Error |
|---|---|---|---|
| GET | `/health` | 200 | |
| GET | `/books` | 200 | |
| POST | `/books` | 201 | 422 |
| GET | `/books/{id}` | 200 | 404 |
| POST | `/reset` | 200 | |

El API rechaza con 422 un libro con `year` fuera del rango de 1450 a 2100. La columna `expected` de `books.csv` dice qué código debe devolver cada fila.

## Qué se pide

### 1. Plugins

Se instala el Plugins Manager en JMeter y, desde él, estos dos plugins. La [guía de instalación](https://danihrndzld.github.io/hdt6-jmeter-books/) cubre Java, JMeter, el Plugins Manager y los dos plugins en macOS, Windows y Linux.

| Plugin | Se usa para |
|---|---|
| Custom Thread Groups | el grupo de usuarios del plan, que es un Concurrency Thread Group |
| 3 Basic Graphs | los gráficos Active Threads Over Time, Response Times Over Time y Transactions per Second |

### 2. El plan

El plan se guarda como `plan.jmx` en la raíz del repositorio y parte de [`plantilla.jmx`](plantilla.jmx), que trae el Concurrency Thread Group y un `GET /books`. Cada usuario repite estos tres pasos mientras dura la prueba:

1. Pide `GET /books`.
2. Crea un libro con `POST /books`, tomando los datos de una fila de `books.csv`.
3. Pide `GET /books/{id}` del libro que acaba de crear, con el `id` que devolvió el POST. Si el POST devolvió 422, este paso no se hace.

Cada solicitud revisa su código de estado, y el POST revisa el de la columna `expected`. El último GET revisa además que el título sea el de la fila. La cantidad de usuarios, el ramp-up y el tiempo sostenido se cambian desde la línea de comandos, sin abrir ni editar el plan.

### 3. Corridas

Cada nivel de la tabla corre sin interfaz gráfica y genera el reporte HTML de JMeter. El API se resetea antes de cada corrida, porque cada POST agrega un libro y `GET /books` devuelve todos.

| Usuarios | Ramp-up | Sostenido |
|---|---|---|
| 10 | 10 s | 60 s |
| 50 | 10 s | 60 s |
| 100 | 10 s | 60 s |
| 200 | 10 s | 60 s |
| 500 | 10 s | 60 s |

De cada corrida se sube solo `statistics.json`, en `resultados/<usuarios>/statistics.json`. El resto del reporte no se sube.

Aparte, una corrida de 100 usuarios se hace en la interfaz gráfica con los tres gráficos del plugin abiertos. Su captura va en `evidencia/graficos.png`.

### 4. La puerta

Un script en la raíz, `gate.sh` o `gate.py`, recibe la carpeta de un reporte y termina con código distinto de 0 si cualquiera de los dos valores totales pasa su límite. Si los dos quedan dentro, termina con 0.

| Valor total del reporte | Límite |
|---|---|
| p95 | 100 ms |
| Errores | 1 % |

### 5. Resultados

`RESULTADOS.md` lleva una tabla con una fila por nivel:

| Usuarios | Muestras | Solicitudes por segundo | p50 | p95 | p99 | Errores | Código de salida de la puerta |
|---|---|---|---|---|---|---|---|

Debajo de la tabla van estas respuestas, cada una con los números de esta máquina:

- En qué nivel de usuarios el p95 pasó de 100 ms por primera vez.
- Qué pasó con las solicitudes por segundo entre 200 y 500 usuarios.
- Cuánto CPU usaron el API y JMeter durante la corrida de 500 usuarios, cuántos núcleos tiene la máquina, y cuál de los dos procesos puso el límite.

## Entrega

| Qué | Cuándo |
|---|---|
| Asignación | Jue 29 oct |
| Entrega individual en MiU | Jue 5 nov, 23:59 |

En MiU se sube el enlace a un fork público de este repositorio. El fork tiene estos archivos:

| Archivo | Contenido |
|---|---|
| `plan.jmx` | el plan |
| `gate.sh` o `gate.py` | la puerta |
| `resultados/` | un `statistics.json` por nivel |
| `RESULTADOS.md` | la tabla y las tres respuestas |
| `evidencia/plugins.png` | la pestaña Installed del Plugins Manager con los dos plugins |
| `evidencia/graficos.png` | los tres gráficos de la corrida de 100 usuarios |

Los números de `RESULTADOS.md` coinciden con los de `resultados/`.

# Prueba técnica — `hallpack`

**Tiempo:** 3 horas desde que recibes este correo.
**Entrega:** responde al correo con un `.zip` de tu carpeta de trabajo, **incluida la carpeta `.git`**.

> **Antes de empezar: lee este documento entero.** Te llevará unos 10 minutos
> y te ahorrará sorpresas.
>
> La entrega tiene dos partes y **las dos son obligatorias**:
>
> 1. **Código**: tareas 1, 2 y 3, en orden de prioridad. No esperamos que las
>    termines todas.
> 2. **Dos documentos escritos** (tarea 4, al final de este README):
>    `NOTES.md` y `DESIGN.md`. **Resérvate los últimos 30 minutos para ellos.**
>    Una entrega sin estos documentos se considera incompleta, aunque el
>    código esté muy avanzado.
>
> Te recomendamos crear `NOTES.md` desde el primer minuto e ir apuntando ahí
> las decisiones a medida que las tomas.

---

## Contexto

Somos el equipo que se encarga de **cerrar versiones y desplegarlas** en las
salas de juego de una empresa de máquinas de slots. Cada sala tiene un servidor
que gestiona varios *mixes* (un grupo de juegos que comparten plataforma y
versión de motor). Cada vez que se cierra una versión hay que:

1. saber de qué rama de release sale cada versión de motor,
2. comprobar que la herramienta que vamos a publicar está lista para cerrarse,
3. calcular qué hay que llevar a cada sala para actualizarla.

Hoy esto se hace a mano y con scripts de shell frágiles. Te pedimos que
empieces la herramienta que lo sustituya: un CLI en Python llamado `hallpack`.
Más adelante este CLI pasará a ser un servicio web.

Tienes los datos de ejemplo en `data/`. Son extractos reales en forma, pero
inventados en contenido. **Míralos con calma antes de escribir código.**

---

## Reglas del juego

- **Python 3.10 o superior.** Solo librería estándar. Para los tests puedes usar
  `pytest` o `unittest`.
- Debe poder ejecutarse con `python -m hallpack <comando> ...` desde la raíz de
  tu entrega. Explica cómo ejecutarlo y cómo lanzar los tests.
- Haz **commits pequeños y frecuentes** mientras trabajas. Queremos ver cómo
  avanzas, no solo el resultado.
- La prueba tiene **más trabajo del que cabe en 3 horas, a propósito**. Las
  tareas de código van en orden de prioridad. Preferimos poco, bien hecho y
  bien explicado, antes que todo a medias. La tarea 4 no es opcional.
- El enunciado **no cubre todos los casos**. Cuando encuentres uno que no está
  cubierto, decide algo razonable, déjalo escrito y sigue. Durante la prueba no
  hay nadie para resolver dudas. Si algo del enunciado no te cuadra, dilo.
- **Uso de IA:** puedes consultar documentación y buscadores. **No uses
  asistentes de IA generativa** (ChatGPT, Copilot, Claude, Gemini…) para
  escribir código ni texto. Si en algún momento lo usas, decláralo en
  `NOTES.md`: declararlo no penaliza, ocultarlo sí. Después de la prueba
  haremos una sesión de 30 minutos en la que modificarás tu propio código en
  directo.

---

## Tarea 1 — De tag a rama de release

Las versiones de motor se publican como tags con el formato
`<NOMBRE>_<versión>`, por ejemplo `ORION_4.12.3`, y pueden llevar un sufijo de
release candidate: `VEGA_2.7_RC2`. Cada tag sale de una rama de release.

Para encontrar la rama de un tag, se quita el sufijo de RC. Después se prueba
`releases/<NOMBRE>_<versión sin el último segmento>.X` y se van quitando
segmentos, de la rama más específica a la más general, hasta dar con una que
exista en el remoto. Si no existe ninguna, es un error.

| Tag            | Rama esperada            |
|----------------|--------------------------|
| `ORION_4.12.3` | `releases/ORION_4.12.X`  |
| `ORION_4.9.1`  | `releases/ORION_4.X`     |
| `VEGA_2.7_RC2` | `releases/VEGA_2.X`      |
| `LYRA_EDITOR_1.40.2.7` | `releases/LYRA_EDITOR_1.X_stable` |

Además, nuestras herramientas internas se versionan como `MM.mm.pp`, con dos
dígitos por campo (`03.04.00`). Al cerrar una versión hay que calcular la
siguiente: `patch`, `minor` o `major`.

**Se pide:**

- `python -m hallpack resolve-branch --branches data/tarea1/remote_branches.txt <tag>...`
- `python -m hallpack next-version <versión> <patch|minor|major>`
- Prueba los dos comandos con `data/tarea1/tags.txt` y
  `data/tarea1/versions_to_bump.txt`.

---

## Tarea 2 — ¿Está lista la herramienta para cerrar versión?

En `data/tarea2/hubsync/` tienes el estado de la rama de release de una de
nuestras herramientas justo antes de cerrar la versión:

- `CHANGELOG.ver`: el changelog que se edita a mano en cada cambio. El release
  lo lee para generar las notas de la versión.
- `versions.txt`: histórico de versiones publicadas.
- `build.sh` y `pyproject.toml`: dos sitios más donde vive la versión.
- `git_log.txt`: salida de `git log --oneline --decorate` de la rama.

Cada cambio en la rama corresponde a un ticket (`XHUB-123`), y el ticket tiene
que constar en el changelog. Hace unos meses renombramos las claves de los
tickets. La tabla de renombrados está en `data/tarea2/key_renames.json`.

**Se pide:** `python -m hallpack audit data/tarea2/hubsync` debe decir si la
herramienta está lista para cerrar versión y, si no lo está, **todo** lo que
hay que arreglar antes. La salida la va a leer una persona, y también un job de
CI que debe poder saber si falla.

---

## Tarea 3 — Plan de actualización de una sala

En `data/tarea3/` tienes:

- `hall_state.json`: lo que hay instalado ahora en la sala `H-0412`.
- `target.json`: lo que tiene que haber después de la release.
- `index/`: el índice del repositorio de artefactos. La API real pagina los
  resultados: cada página trae `items` y un `continuationToken` que hay que
  pedir para obtener la siguiente. Aquí lo simulamos con ficheros: la primera
  página es `index/start.json` y el token `X` corresponde a `index/X.json`.
  Cuando no hay más páginas, el token es `null`.

Lo que sabemos del negocio:

- A una sala solo pueden ir artefactos del repositorio `releases`.
- Un juego declara la versión mínima de motor que necesita (`min_engine`).
- El `catalog_code` identifica a un juego en el servidor de la sala y no se
  puede repetir.
- Para instalar un artefacto hace falta espacio para el `.tar.gz` y para
  descomprimirlo, es decir, el doble de su tamaño.

**Se pide:**
`python -m hallpack plan --hall data/tarea3/hall_state.json --target data/tarea3/target.json --index data/tarea3/index`
debe generar el **plan de actualización**: qué hay que hacer en cada mix, qué
hay que descargar y de dónde, y si la actualización se puede lanzar o no (y por
qué). El formato de salida lo decides tú, pensando en quién lo va a usar.

---

## Tarea 4 — Escribe (obligatoria, reserva los últimos 30 minutos)

**`NOTES.md`**

- Decisiones que has tomado ante los casos que no cubre el enunciado.
- Qué has dejado sin hacer y por qué. Qué harías con más tiempo.
- Tiempo aproximado que has dedicado a cada tarea.
- Uso de IA, si lo ha habido.

**`DESIGN.md`** (máximo una página)

Otros equipos quieren lanzar el `plan` desde una web en lugar de desde la
terminal. El índice real es remoto y puede tardar minutos en recorrerse.
Cuéntanos cómo lo plantearías: qué API expondrías, qué cambiarías de tu código
para llegar ahí y qué te preocuparía de llevarlo a producción.

---

## Qué valoramos

- Que funcione con los datos que te damos y que sepas cuándo no funciona.
- Código claro y ordenado, que otra persona del equipo pueda mantener.
- Tests que demuestren comportamiento real.
- Criterio: qué detectas, qué decides y cómo lo explicas.

Suerte, y disfruta del problema.

# HallPack

HallPack es un proyecto personal para reunir en una herramienta de línea de
comandos algunas operaciones relacionadas con las releases de motores, juegos
y salas.

## Funcionalidades

- **Resolver ramas de release:** busca la rama que corresponde a uno o varios
  tags, desde la versión más específica hasta una rama más general.
- **Calcular la siguiente versión:** incrementa una versión `MM.mm.pp` como
  `patch`, `minor` o `major`.
- **Revisar una release:** comprueba la coherencia entre los archivos de
  versión, el changelog y el registro de Git.
- **Preparar una actualización de sala:** compara el estado actual con el
  objetivo, identifica cambios de motores y juegos, y busca los artefactos que
  habría que descargar del repositorio `releases`.

## Requisitos

- Python 3.10 o posterior.
- Ejecutar los comandos desde la raíz del repositorio.

No hace falta instalar el proyecto para usarlo localmente.

## Uso

Los comandos se ejecutan con `python -m hallpack`.

### Buscar la rama de un tag

```console
python -m hallpack resolve-branch --branches data/tarea1/remote_branches.txt ORION_4.12.3
```

Se pueden consultar varios tags en una misma ejecución:

```console
python -m hallpack resolve-branch --branches data/tarea1/remote_branches.txt ORION_4.12.3 VEGA_2.7_RC2
```

### Calcular la siguiente versión

```console
python -m hallpack next-version 03.04.00 patch
```

El tipo de incremento puede ser `patch`, `minor` o `major`.

### Revisar una release

```console
python -m hallpack audit data/tarea2/hubsync
```

El comando muestra `OK` si las comprobaciones pasan o los errores encontrados
si hay información que corregir.

### Preparar una actualización de sala

```console
python -m hallpack plan --hall data/tarea3/hall_state.json --target data/tarea3/target.json --index data/tarea3/index
```

El comando muestra notas sobre las diferencias entre la sala y el objetivo, y
los artefactos de `releases` necesarios para los cambios detectados. El índice
local simula la paginación: `start.json` contiene la primera página y cada
`continuationToken` indica el nombre del siguiente archivo JSON.

## Pruebas

Para ejecutar las pruebas automatizadas:

```console
python -m pytest
```

- 1. Que API expondria

Calcular el plan tarda minutos asi que la web no puede quedarse esperando la respuesta, daria timeout.
Por eso lo separaría en dos pasos:

- POST /plans: la web envia la sala y el target. La API no calcula en ese momento: guarda la petición
  y responde al instante con un identificador y el status
- GET /plans/42: la web pregunta cada pocos segundos como va. Responde pending, in_progress o
  done en JSON o error con el motivo

- 2. Que cambiaria de mi codigo

Ahora mismo todo se responde con prints y se leen ficheros en local.
Para una web, devolveria los datos en JSON como he mencionado antes, ademas moveria toda la logica del main a funciones que reciben y devuelven
datos.

- 3. Qué me preocuparía en producción

Me preocuparia el tema permisos, que solo pueda lanzar ordenes quien este autorizado.
Tambien, que falle a la mitad, hacer reintentos o devolver errores.

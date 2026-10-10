TAREA 1

Cara al resolve-branch:

Primero he dividido el comando en partes, para saber gestionar cada una gracias a args.
Lo primero que hago es leer y guardar las ramas linea a linea segun la ruta especificada en el comando, anteriormente esto lo hacia
en la etapa final y lo leia en cada bucle, mal.
Luego, para cada tag, lo primero que hago es una funcion aparte donde, usango regex, la cual, busco el \_rc, numeros (\d+) y al fianl del tal ($),
escribiendo esto me he dado cuenta de que me faltaba ignorar el case del texto, sino no funcionaava con \_rc en minuscula.
Por ahora nos queda: VEGA_2.7, posteriormente separo el nombre del juego con la version e itero cada version quitando el ultimo numero para buscar del release mas especifico
al mas general, he tenido en cuenta el \_stable al final.

Respecto a los casos de error, no he tenido en cuenta Releases con mayuscula porque para GIT es una rama distinta.
Tambien he priorizado la stable a las releases normales dentro del mismo nivel.
Las ramas \_old no las tengo en cuenta ya que considero que nunca deberian elegirse.

Tambien he visto que para LYRA_EDITOR_1.40.2.7 mi programa devuelve releases/LYRA_EDITOR_1.40.X pero deberia esperar releases/LYRA_EDITOR_1.X_stable,
a pesar de que priorizo las stable, he pensado seguir la regla escrita antes que la tabla. releases/LYRA_EDITOR_1.40.X es mas especifica.

Pendiente:
Queda pendiente revisar los tags sin formato valido.

Cara al next-version:

He dado por hecho que el formato estricto es el NN.NN.NN y que no se puede superar de 99 por los ejemplos del README.

Tiempo: 2:45

Para los tests he tenido que repasar como funcionan con pytest https://www.geeksforgeeks.org/python/pytest-tutorial-testing-python-application-using-pytest/
https://www.geeksforgeeks.org/python/python-subprocess-module/
Tambien habia tenido un problema con el nombre del archivo, tiene que empezar por test\_

TAREA 2

De momento, audit solo comprueba que las vresiones de build y changelog coincidan, ahora mismo sale OK pero no es fiable porque faltan mas comprobaciones
como la fecha, el tema de XHUB-123, etc.

Problemas encontrados:

Las fechas estan desordenadas y el .toml no respecta la estructura NN.NN.NN version = "3.4.0"

Uso de IA: unicamente para funciones especificas como la estructura de rsplit para definir solo 1 split como maximo o ignorar el case cosa que no recordaba

Cabe decir que solo he tenido tiempo de hacer un ejercicio y medio, he intentado dejar todo claro tanto en algun comentario
del codigo como en NOTES, normalmente comentaria mas el codigo pero he aprovechado mas NOTES.md para ello.
Con mas tiempo, creo que podria hacer algo mas optimo, mejor estructurado con funciones y mayor sostenibilidad.
En un futuro si tengo suerte y consigo el puesto, espero poder demostrar mis habilidades mucho mejor y completas en proyectos reales y con tiempo.

Muchas gracias!!!

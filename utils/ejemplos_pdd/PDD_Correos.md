Modificaciones

| **\#** | **Fecha**  | **Pág./Items** | **Motivo**             | **Autor**      | **Sector** |
|--------|------------|----------------|------------------------|----------------|------------|
| 0.00   | 21/04/2026 | Todas          | Creación del Documento | Sofia Gamboggi | RPA        |

Historial de Revisión

| **\#** | **Fecha** | **Validador** | **Comentarios** |
|--------|-----------|---------------|-----------------|

# Descripción General del Proceso

## Propósito del Proceso

El propósito es automatizar la gestión de correos electrónicos en
Outlook mediante la identificación dinámica de carpetas y la ejecución
de reglas de negocio específicas para cada correo, concluyendo con la
creación automática de reportes de cumplimiento basados en los datos
extraídos

## Diagrama de Flujo – High Level

## Diagrama de Flujo - Low Level

## Sistemas Involucrados

Los siguientes sistemas son los involucrados en el proceso

| Sistema                   | Descripción                                           | Detalle    |
|---------------------------|-------------------------------------------------------|------------|
| Carpeta compartida en red | Arquitectura de archivos Input/Output                 | Producción |
| Excel                     | Validación de datos                                   | Español    |
| SMTP                      | Envío de notificaciones/ revisión de mails en casilla | Office 365 |

## Salidas

\[Servidor\]\\Carpeta_red\]\RPA\Bot correos\Bot correos\3. Informes
(USUARIO)

# Descripción Paso a Paso

El bot deber ingresar a la carpeta compartida (\[Servidor\]\\\[Carpeta
RPA\]\Bot correos\\, en esta carpeta se encontraría toda la información
necesaria para que el analista pueda ver los resultados del Bot.

La estructura de la carpeta de RED seria la siguiente:

\\\[Servidor\]\\Carpeta_RPA\]\\ Bot Correos\Bot Correos \\

- 1\. Parámetros (USUARIO)

- 2\. Correos (USUARIO - BOT)

- 3\. Informes (USUARIO)

- 4\. Archivos Adjuntos (BOT)

Al iniciar la automatización el Bot tendrá que verificar que todas las
carpetas estén creadas. En el caso de que no estén, las deberá crear.

\\\[Servidor\]\\ \[Carpeta_RPA\]\Bot correos\BG003\\

- Template

## Pre-validación 

| N° Paso | Acción | Detalle | Error/ <br> Excepción |
| --- | --- | --- | --- |
|  | Verificar existencia | El Bot deberá verificar sí existen todas las carpetas que necesita para iniciar el proceso: <br> Sí no existen las carpetas, debe crearlas . <br> Sí no existen las carpetas, debe crearlas . <br> Sí existen las carpetas, el Bot deberá continuar con el siguiente paso. <br> Sí existen las carpetas, el Bot deberá continuar con el siguiente paso. |  |
|  | Verificar existencia | El Bot deberá verificar sí existe un archivo “.txt” en la carpeta “BG003”. <br> Sí existe un archivo con extensión “.txt” el Bot deberá ir al paso 3.2 Proceso 3.2.3 y continuar el proceso desde ahí. <br> Sí existe un archivo con extensión “.txt” el Bot deberá ir al paso 3.2 Proceso 3.2.3 y continuar el proceso desde ahí. <br> Sí no existe un archivo con extensión “.txt”, el Bot deberá continuar con el siguiente paso. <br> Sí no existe un archivo con extensión “.txt”, el Bot deberá continuar con el siguiente paso. |  |
|  | Verificar existencia | El Bot deberá verificar que el archivo template este en la carpeta “BG003\Template <br> Si está , debe continuar con el paso siguiente. <br> Si está , debe continuar con el paso siguiente. <br> Si no está, debe ejecutar la excepción y salir. <br> Si no está, debe ejecutar la excepción y salir. | Excepción de Negocio 3.6.1 |
|  | Copiar template | El Bot deberá copiar el template a la carpeta 3. Informes (USUARIO) <br> Nota: el formato de la fecha es YYYY-MM-DD hhmm |  |
|  | Abrir archivo “Parametros.xlsx”. | El bot deberá abrir el archivo “Parametros.xlsx” que se encuentra en la carpeta 1.Parametros (Usuarios). <br> Si el archivo no existe, deberá ejecutar la excepción y finalizar. <br> Si el archivo no existe, deberá ejecutar la excepción y finalizar. | Excepción de negocio 3.6.2 <br> Nota: abrir como sólo lectura. |
|  | Verificar cabeceras archivo parámetros. | El Bot deberá verificar que estén tanto las cabeceras como que haya parámetros para analizar. Deben estar las siguientes cabeceras: <br> A1 = Carpetas del Outlook a analizar. <br> B1 = Acciones a realizar. <br> C1 = Para (destinatarios en caso de reenvío). <br> Si no existe alguna cabecera o no hay parámetros, debe ejecutar la excepción y finalizar. <br> Si no existe alguna cabecera o no hay parámetros, debe ejecutar la excepción y finalizar. | Excepción de negocio 3.6.3 |
|  | Verificar que haya carpetas para analizar | El bot deberá verificar que hayan carpetas en “parámetros.xlsx” para analizar. <br> Si no hay carpetas para analizar, debe ejecutar excepción y finalizar. <br> Si no hay carpetas para analizar, debe ejecutar excepción y finalizar. | Excepcion de negocio <br> 3.6.4 |

## Proceso

|  | Abrir informe | El bot deberá abrir el archivo del informe “Bot correo yyyy-MM-dd hhmm.xlsx” |  |
| --- | --- | --- | --- |
|  | Copiar parámetros en hoja “Parametros” | El bot deberá copiar todas las columnas de la única hoja existente en el archivo “Parametros.xlsx” y pegarlo en la hoja “Parametros” en el archivo “Bot correo yyyy-MM-dd hhmm.xlsx” <br> Columna “A” carpetas de Outlook a analizar. <br> Columna “B” Acciones a realizar. <br> Columna “C” Para (en caso de que la opcion sea “Analizar y reenviar correo” | Nota: deberá pegar como valor. |
|  | Copiar parámetros en hoja “Resumen” | El bot deberá copiar las columnas “A” y “B” del archivo “Parametros.xlsx” y pegarlo en las columnas “A” y “B” del archivo “Bot correo yyyy-MM-dd hhmm.xlsx”, en la hoja resumen. <br> Columna “A” Carpetas de Outlook a analizar. <br> Columna “B” Acciones a realizar. | Nota: pegar como valor. <br> Nota II: luego debe cerrar el archivo parametros sin guardar. |
|  | Crear archivo | El Bot deberá crear el archivo flag en la carpeta “BG003”. |  |
| El bot deberá hacer los siguientes pasos para cada línea de la hoja parámetros. |  |  |  |
|  | Copiar parámetros | El Bot deberá copiar la columna A, columna B y columna C de la hoja “Parámetros”. <br> Nota: guardará los valores en una lista para que sea más fácil su manipulación. |  |
| El bot deberá ejecutar los pasos anteriores para cada línea de la hoja parámetros. |  |  |  |
|  | Conexión a Outlook | El bot deberá conectarse a la casilla de mail. <br> Nota I: es muy importante que la conexión sea por Outlook. <br> Nota II: no hace falta ingresar credenciales ni usar ninguna pre guardada. En la parte inferior en la configuración del bloque en Automation Anywhere, hay una lista desplegable que, cuando se actualizar, reconoce las casillas de correos abiertas en el dispositivo donde se correrá el bot. El desarrollador solo debe seleccionarla, sin ingresar credenciales adicionales. Por eso es muy importante seleccionar la opción “Outlook” mencionado en la nota I. |  |
|  | Delay | El Bot deberá tener un tiempo de espera de 3 minutos para que se actualice la casilla de correos. |  |
|  | Verificar existencia de una carpeta importante | El bot deberá verificar la existencia de la carpeta “Correos Analizados”. Es importante que esté y si no, alertar ya que el bot no puede crear carpetas por sí mismo en Outlook y si no está, necesitamos que sea creada manualmente por el usuario para poder usarla en el proceso. | Excepcion de negocio 3.6.5 |
| El bot deberá realizar los siguientes pasos por cada mail en cada carpeta. |  |  |  |
|  | Verificar existencia de carpetas en Outlook | El bot deberá verificar la existencia de las carpetas deseadas en el correo. <br> Si no existe, debe completar la columna “B” en la pagina “Analisis” del informe con “ Error- carpeta no encontrada ” <br> Si no existe, debe completar la columna “B” en la pagina “Analisis” del informe con “ Error- carpeta no encontrada ” |  |
|  | Obtener datos de cada correo. | El Bot deberá obtener la siguiente información de cada mail que procesa y guardarlo en las columnas del Excel de la hoja “ Análisis ”. <br> Carpeta Columna “A”. <br> Asunto columna “C”. Numero 1 <br> Remitente columna “D”. Numero 2 <br> Copia columna “E”. Numero 3 <br> Fecha del correo columna “F”. Numero 4 <br> Hora del correo columna “G”. Numero 5 <br> Cuerpo del correo columna “H”. Numero 6 <br> Contiene adjuntos [SI/NO] Columna “I”. Numero 7 | Nota: el cuerpo del correo debe pegarlo como texto plano. |
|  | Descargar correo en carpeta | El bot deberá descargar el correo como archivo y guardarlo en la carpeta “ 2. Correos (USUARIO - BOT) ” . En esta carpeta se encuentran las mismas carpetas que en la hoja Parametros. <br> Si la carpeta donde se debe guardar el mail no existe, el bot debe crearla. <br> Si la carpeta donde se debe guardar el mail no existe, el bot debe crearla. <br> Si la carpeta donde se debe guardar el mail existe, debe guardar cada mail en su carpeta correspondiente. <br> Si la carpeta donde se debe guardar el mail existe, debe guardar cada mail en su carpeta correspondiente. <br> Nota: el correo debe ser descargado con la fecha y la hora COMPLETA (horas/minutos/ segundos) para evitar que un correo enviado en el mismo día o en la misma hora lo pise y se pierdan correos. <br> Nota: el correo debe ser descargado con la fecha y la hora COMPLETA (horas/minutos/ segundos) para evitar que un correo enviado en el mismo día o en la misma hora lo pise y se pierdan correos. |  |
| Caso Analizar y reenviar |  |  |  |
|  | Envíar correo a destinatarios | Si la acción a realizar (segunda columna de la tabla traída de parámetros) es “Analizar y reenviar correo”, el Bot deberá reenviarlos. Deberá enviarlos a/los destinatarios de la columna “K” de la hoja “ Analisis ”. <br> En la columna “K” se encuentran el o los destinatarios para reenviar. Los mismos están separados por una coma (,) , por lo que es fundamental hacer la separación previa al uso en la acción “Reenviar” del paquete mail. |  |
|  | Completar columna “L” | Una vez reenvíado, el bot deberá completar la columna “L” (“Correo Enviado”) con un “Ok” en la hoja “Análisis”. |  |
|  | Delay | El Bot deberá tener un tiempo de espera de dos minutos para que los mails se reenvíen correctamente. |  |
|  | Verificación de envío exitoso | El bot deberá verificar en la bandeja de entrada general si hubo alguna notificación por correo no enviado por no encontrar al destinatario. <br> Si se encuentra el error, debe completar la columna “M” en la hoja “Analisis” (Casillas con error) con: Error no existe la casilla [DIRECCION_CASILLA]. <br> Si se encuentra el error, debe completar la columna “M” en la hoja “Analisis” (Casillas con error) con: Error no existe la casilla [DIRECCION_CASILLA]. |  |
| Fin caso Analizar y reenviar |  |  |  |
| Caso Analizar y descargar archivos adjuntos |  |  |  |
|  | Descargar archivos adjuntos | Si la acción a realizar (segunda columna de la tabla traída de parámetros), es “Analizar y Descargar Adjuntos”, el bot deberá descargar todos los archivos adjuntos del correo analizado y guardarlos en la carpeta 4. Archivos Adjuntos (BOT). <br> Dentro de esta carpeta se encuentran las carpetas correspondientes de todas las carpetas que se encuentran en el bot. <br> Si no existen, el bot debe crearlas. <br> Si no existen, el bot debe crearlas. <br> El bot guardará los archivos adjuntos dentro de una subcarpeta con la fecha del día y la hora de ejecución. <br> El bot guardará los archivos adjuntos dentro de una subcarpeta con la fecha del día y la hora de ejecución. |  |
| Fin caso Analizar y descargar archivos adjuntos |  |  |  |
|  | Mover correo analizado | El Bot deberá mover el correó que analizó a la carpeta “Correos analizados” en la casilla de mail. |  |
| El bot debe realizar todos los pasos anteriores por cada correo en cada carpeta |  |  |  |
|  | Eliminar archivo | El bot deberá eliminar el archivo flag creado en la carpeta “BG003”. |  |
|  | Crear archivo | El Bot deberá crear un nuevo archivo flag en la carpeta “BG003”. |  |
|  | Simulacion ERP | Se realizarán los pasos detallados en la sección 3.3 donde se simula la carga a un ERP, modificable en cada caso. |  |
|  | Eliminar archivo | El Bot deberá eliminar el segundo archivo flag que creo en la carpeta “BG003”. |  |

##  Simulación ERP

|  |  | El bot deberá realizar los siguientes pasos por cada fila en la hoja “Analisis”. |  |
| --- | --- | --- | --- |
|  | Mostrar información obtenida | El Bot deberá mostrar con un cuadro de mensaje, los datos obtenidos de cada mail analizado. Esto sirve para imitar la carga a un ERP. |  |
|  | Completar celda | Una vez que muestra el Message box, escribe OK en la columna N “Carga ERP” |  |
| El bot deberá realizar los pasos anteriores por cada fila en la hoja “Analsis”. |  |  |  |
|  | Eliminar archivo | El Bot deberá eliminar el segundo archivo flag que creo en la carpeta “BG003”. |  |

## Finalización del proceso

| N° Paso | Acción | Detalle | Error/ <br> Excepción |
| --- | --- | --- | --- |
|  | Guardar archivo de informe | El Bot deberá guardar el archivo “Bot correo yyyy-MM-dd hhmm.xlsx” en la capreta “3.Informes (USUARIO). |  |
|  | Envío de mail de notificación final Exitosa sin Excepciones | Una vez finalizado el proceso, el Bot enviará por mail a los usuarios informando el detalle de la ejecución: <br> Asunto mail: BG003 \| Correos \| CORRECTO <br> [Adjunto informe] <br> Cuerpo mail: <br> Estimados, <br> Se les informa que ha finalizado el BG003 - Correos. El informe fue generado por el BOT con éxito y se encuentra en la ruta compartida: <br> [REPORT] <br> A continuación, se proporciona un reporte de los datos obtenidos el día de hoy: <br> [TABLA PÁGINA RESUMEN] <br> Para una información más detallada, se puede acceder a la siguiente ruta donde se encuentran los logs de ejecución: <br> [RUTA DE ACCESO A LOGS] <br> Cordialmente, <br> BG003 - Correos |  |
|  | Envío de mail de notificación final Erróneo con Excepciones Negocio | Asunto mail: BG003 \| Correos \| ADVERTENCIA <br> Cuerpo mail: <br> Estimados, <br> Se les informa que ha finalizado BG008 - Correos. Sin embargo, la ejecución presentó la siguiente excepción y no fue posible finalizar el proceso: <br> [Excepción de proceso] <br> [ACCION] <br> Para una información más detallada, se puede acceder a la siguiente ruta donde se encuentran los logs de ejecución: <br> [RUTA DE ACCESO A LOGS] <br> Cordialmente, <br> BG003 - Correos. |  |

## Excepciones de Sistema

| N° Exc. | Escenario | Acción |
| --- | --- | --- |
|  | En caso de no poder acceder al disco compartido. | El Bot enviará un email de Advertencia informando que no es posible procesar la información. |
|  | En caso de ocurrir algún error durante el proceso ajeno a las excepciones previamente contempladas. | Se notificará mediante un correo, indicando que la ejecución del Bot se detuvo debido a un problema técnico. <br> El detalle técnico del mismo se notificará a los desarrolladores para tratar el problema de manera eficaz. |

## Excepciones del Negocio

| N° Exc. | Escenario | Acción |
| --- | --- | --- |
|  | En el caso que el archivo template no este en la carpeta. | El Bot deberá enviar un mail informando que no pudo encontrar el template. |
|  | En el caso que el archivo de parámetros no se encuentre en la carpeta compartida. | El Bot deberá enviar un mail informando que el archivo no se encuentra en la carpeta. |
|  | En el caso de que las cabeceras y el contenido del archivo de parámetros no sea el esperado. | El bot deberá enviar un mail informando que las cabeceras y contenido no son las esperadas para desarrollar el proceso. |
|  | En el caso que no hayan carpetas para analizar en el archivo “parámetros.xlsx” | El bot deberá enviar un mail informando que no hay carpetas para analizar. |
|  | En el caso de que no exista la carpeta “Correos Analizados” en Outlook. | El bot deberá enviar un mail informando que la carpeta no se encuentra en Outlook. |

# Sign-off 

## Interno

|                  | **Sign-off** |           |          |
|------------------|--------------|-----------|----------|
|                  | **Nombre**   | **Fecha** | **Role** |
| **Revisado por** |              |           |          |

## Cliente

|                  | **Sign-off** |                |          |
|------------------|--------------|----------------|----------|
|                  | **Nombre**   | **Fecha mail** | **Role** |
| **Aprobado por** |              |                |          |

Modificaciones

| **\#** | **Date**   | **Page**              | **Reason**                                                                     | **Author**    | **Sector**    |
|--------|------------|-----------------------|--------------------------------------------------------------------------------|---------------|---------------|
| 0.0    | 27/08/2025 | All                   | Creación del documento                                                         | Garcia David  | RPA           |
| 1.0    | 02/03/2026 | 2.8.2 a 2.8.3         | Cambio de ruta: Sharepoint                                                     | Martin Sabate | Desarrollador |
| 1.1    | 02/03/2026 | 3.1.6 a 3.1.8         | Ajuste: Nuevo Input presentismo                                                | Martin Sabate | Desarrollador |
| 1.2    | 02/03/2026 | 3.1.3 a 3.1.5         | Ajuste: Nuevo Biometrico                                                       | Martin Sabate | Desarrollador |
| 1.3    | 02/03/2026 | 3.1.9 y 3.2.2 a 3.2.3 | Masterfile y Dias diferencias Renovado                                         | Martin Sabate | Desarrollador |
| 1.4    | 02/03/2026 | 3.2.4                 | Ajuste: Casos especiales                                                       | Martin Sabate | Desarrollador |
| 1.5    | 02/03/2026 | 3.5                   | Ajuste: Obtener Link                                                           | Martin Sabate | Desarrollador |
| 1.6    | 02/03/2026 | 3.2.1                 | Ajuste: Nueva nomenclatura el Reporte Horas Control                            | Martin Sabate | Desarrollador |
| 1.7    | 02/03/2026 | 3.2.2 y 3.2.3         | Ajuste: Nuevo desplegable en Aprobacion “SI – PRESENTISMO” y “NO – BIOMETRICO” | Martin Sabate | Desarrollador |
| 1.8    | 02/03/2026 | 3.4                   | MasterFile Configuraciones                                                     | Martin Sabate | Desarrollador |
| 1.8    | 02/03/2026 | 3.6                   | Ajuste: Agregar Nuevo destinario adicional en Masterfile                       | Martin Sabate | Desarrollador |
| 1.9    | 02/03/2026 | 3.7                   | Renovado : Nueva tabla de notificación final Control 1, Control 2 y Control 3  | Martin Sabate | Desarrollador |
| 1.10   | 25/03/2026 | 3.2.3                 | (Numero de cliente) Subterceros                                                | Martin Sabate | Desarrollador |
| 1.11   | 26/03/2026 | 3.4                   | Reiniciar el/los dias                                                          | Martin Sabate | Desarrollador |
Historial de revisión

| **\#** | **Date** | **Reviewer** | **Comments** |
|--------|----------|--------------|--------------|
# Descripción General del Proceso

## Propósito del Proceso

Con intención de hacer más eficiente y óptimo el proceso de control de
horas de seguridad. Se realizará la automatización de este comenzando,
partiendo desde masterfile de control con el área.

## Consideraciones adicionales

El proceso fue relevado y está basado en el actual sistema que generan
el reporte biométrico en VW, el mismo está siendo migrado, una vez este
sea migrado se deberá actualizar este documento con el nuevo formato del
reporte.

## Diagrama de flujo – Low level (Solución automatización)

## Business Case

## Sistemas Involucrados

*Los siguientes sistemas son los utilizados durante el proceso manual.*

| Sistema        | Descripción                               | Ambiente          |
|----------------|-------------------------------------------|-------------------|
| Excel          | Microsoft Excel                           | Dev. Y Productivo |
| SMTP           | Enviar para notificaciones.               | Dev. Y Productivo |
| Carpeta en red | Arquitectura de archivos Input’s/Output’s | Dev. y Productivo |

## Entradas

- Masterfile control

- Reporte presentismo

- Informe biométrico

## Salidas

- Masterfile control con los registros actualizados

- Reporte final

## Precondiciones

| N° | Precondición | Detalle |
| --- | --- | --- |
|  | Carpeta compartida de archivos del Bot | Se deberá proveer una carpeta compartida del Bot para que el mismo deje los archivos internos que genera. |
|  | Carpeta de Input | Se deberá proveer acceso a la carpeta compartida del del área para dejar los inputs del proceso <br> OneDrive Local: C:\Users\Usuario\Volkswagen AG\Seguridad de Grupo VWA - Bot HR010 – Control Horas Seguridad <br> Sharepoint: https://volkswagengroup.sharepoint.com/sites/SeguridadVWA/Documentos%20compartidos/Forms/AllItems.aspx?FolderCTID=0x012000E215C7E89D858B4CB50B0E5BE32644BD&id=%2Fsites%2FSeguridadVWA%2FDocumentos%20compartidos%2FProtecci%C3%B3n%20de%20Planta%2FPorter%C3%ADas%20y%20Puestos%20de%20Control%2FPacheco%2FEncargado%20de%20Seguridad%2FBot%20HR010%20%E2%80%93%20Control%20Horas%20Seguridad |
|  | Carpeta de output | Se deberá proveer acceso a la carpeta compartida del del área para dejar los outputs del proceso <br> OneDrive Local: C:\Users\Usuario\Volkswagen AG\Seguridad de Grupo VWA - Bot HR010 – Control Horas Seguridad <br> Sharepoint: https://volkswagengroup.sharepoint.com/sites/SeguridadVWA/Documentos%20compartidos/Forms/AllItems.aspx?FolderCTID=0x012000E215C7E89D858B4CB50B0E5BE32644BD&id=%2Fsites%2FSeguridadVWA%2FDocumentos%20compartidos%2FProtecci%C3%B3n%20de%20Planta%2FPorter%C3%ADas%20y%20Puestos%20de%20Control%2FPacheco%2FEncargado%20de%20Seguridad%2FBot%20HR010%20%E2%80%93%20Control%20Horas%20Seguridad |
|  | Contactos para notificar | Los contactos para notificar por si hay algún error de sistema/negocio del Bot son: <br> Responsables del Área: <br> Alejandro.Reinaldo@VW.COM.AR <br> Alejandro.Reinaldo@VW.COM.AR <br> Marcelo.Abete@VW.COM.AR <br> Marcelo.Abete@VW.COM.AR <br> Con copia: <br> rpa-vw@ataway.com <br> rpa-vw@ataway.com <br> rpa_support_argentina.vwar.r.cip@vw.com.ar <br> rpa_support_argentina.vwar.r.cip@vw.com.ar |
|  | Ejecuciones del Bot | Control 1 y 2 de lunes a viernes horario a definir, control mensual 5 de cada mes |

# Descripción paso a paso

## 1° Control

| N° | Acción | Detalle | Excepción |
| --- | --- | --- | --- |
|  | Periodicidad | El primer control debe realizarse todos los días (lunes a viernes) controlando el mes vigente desde el día 1 al 4 de próximo mes. <br> Ejemplo desde el 1ro de enero al 4 de febrero. Pero cuando estemos ejecutando de febrero en adelante solo se procesará el mes de enero como si fuera el último día del mes. Considerar tener una variable de input que permita activar/desactivar esto en caso de que los primeros días de un mes se quiera correr efectivamente el control de ese mes vigente. |  |
|  | Buscar los biométricos pendientes | Debemos procesar todos los archivos biométricos del mes actual (tener en cuenta la posibilidad de ingresar el mes como una variable de input). <br> Se deberá tener un registro de los informes biométricos procesados de forma correcta durante el mes |  |
|  | Tomamos informe biométrico | Desde el OneDrive: 1_Biometric Report <br> Nomenclatura: yyyy_mm_dd.BIO.xlsx <br> Es un archivo por día, se baja 10:00 am aproximadamente, a día vencido, es decir que se baja el reporte de ayer el día de hoy. | 4.2.5 No existen informes biométricos a procesar <br> 4.2.1 No existe archivo input o no hay acceso a ruta compartida <br> 4.2.6 No existen informes biométricos o mano de obra de la ejecución o días anteriores |
|  | Registros informes | Identificamos y tomamos cada registro del informe biométrico <br> Cada línea desde la fila N° 2 corresponden a un registro que debemos tomar | 4.2.4 Duplicados en reporte biométrico |
|  | Tomamos valores de cada registro | Campos del informe <br> ID Usuario : ID empleado <br> Nombre y Apellido : Nombre empleado <br> Departamento : Categorias <br> Entrada : Hora ingreso <br> Salida : Hora salida <br> Total horas trabajdas : Cantidad de horas trabajadas <br> Tomamos todos los registros <br> El más 1 significa que entro ayer y salió hoy |  |
|  | Verificamos que exista el informe de presentismos | A cada reporte biométrico le debe corresponder un informe de presentismo (mano de obra \| MO), se debe tener un registro con los informes de presentismo pendientes, de tal forma que, si por ejemplo tenemos reportes biométricos los cuales no tienen su informe de presentismo correspondiente, en cada ejecución deberemos validar si ya están disponibles estos informes los cuales son generados con delay respecto a los reportes biométricos. | 4.2.1 No existe archivo input o no hay acceso a ruta compartida <br> 4.2.6 No existen informes biométricos o mano de obra de la ejecución o días anteriores |
|  | Tomamos reporte presentismo MO | En este reporte tenemos los parámetros y datos que corresponden a cada empleado. <br> Desde el OneDrive: 1_Presentismo Diario. <br> Nomenclatura: yyyy_MM_dd.MO.xlsx <br> Este informe de genera de forma manual, por lo cual podemos tener delay entre le informe biométrico y este reporte. <br> Cada informe biométrico debe tener un reporte de presentismo (MO Mano de obra) |  |
|  | Inicio cruce de información | 1° Para identificar los registros debemos cruzarlo entre el campo ID del informe biométrico y el campo “Empleado” <br> 2° Identificamos estos campos para cada registro <br> 3° Se valida que cada registro del biométrico tomado en el paso “ 3.1.3 Tomamos informe biométrico ” tenga la misma cantidad de horas, es decir el valor de la columna STD Trabajador del Reporte de presentismo vs el valor del campo horario de trabajo del informe biométrico deben ser iguales. <br> 4° En el próximo paso se registrará si el caso fue validado de forma correcta o incorrecta | 4.2.3 Cliente con más de un registro |
|  | Pasamos registros a Máster File | Tomamos los registros cruzados en el paso previo y los pasamos a un nuevo reporte de horas, creando un nuevo Excel para el mes en el OneDrive 3_Control Horas (BOT) <br> Nomenclatura: Reporte Control Horas Seguridad MM.xlsx <br> 1° Creamos un registro nuevo por cada uno de los identificados en el paso “biométrico”. <br> 1° Completamos los datos Des Cliente, Des Subtercero, Des Tipo Puesto, Empleado, Nombre Empleado provenientes del reporte de presentismo del paso “presentismo” y además agregamos los siguientes: <br> Fecha control: Correspondientes a la fecha del informe biométrico y mano de obra <br> Horas Presentismo: que es igual al valor de STD Trabajadas del reporte de presentismo <br> Horas informes bio: que es igual al valor de Horario de Trabajo del informe biométrico <br> 2° En caso de que en las horas del paso anterior SI se validen de forma correcta entonces setearemos “OK” en el campo Estado y aprobación igual a “SI \| PRESENTISMO” <br> 3° En caso de que en las horas del paso anterior NO se validen de forma correcta entonces setearemos “Verificar” en el campo Estado y aprobación igual a “NO \| BIOMETRICO” |  |

## 2° Control

| N° | Acción | Detalle | Excepción |
| --- | --- | --- | --- |
|  | Periodicidad | El primer control debe realizarse inmediatamente luego de la ejecución del control 1. Poner un input para que cuando se ejecute el control 1 ejecute también el control 2. Esto debe ser una variable donde el área de negocio pueda setear un booleano (si/no) para que se ejecute o no el segundo control del bot. <br> Este valor estará en una celda especifica con un valor SI/NO en el Masterfile del OneDrive <br> 0_Master_File <br> Nomenclatura : yyyy_MM_Reporte Control Horas Seguridad.xlsx |  |
|  | Verificamos horas aprobadas | 1° Para los registros aprobados que son aquellos con el estado aprobación igual a SI \| PRESENTISMO, tomaremos el valor Horas Informe PRESENTISMO <br> 2° Para los registros con estado aprobación igual a NO \| BIOMETRICO, tomaremos el valor Horas Biometrico <br> 3° Seteamos el valor según corresponda en el campo horas aprobadas. |  |
|  | Control diario acumulado | Tomando los registros del Master file verificamos que por día que por día y por Des Tipo Puesto se cumplan las horas, para esto: <br> 1° Filtramos por el campo fecha. <br> 2° Filtramos por cada una de las categorías del campo Des Tipo Puesto <br> 3° Sumamos el total de horas en función de lo aprobado/rechazado en el paso 3.2.2 “Verificamos horas aprobadas” <br> 4° Usando los parámetros del Masterfile en OneDrive 0_Master_File, verificamos que se cumplan las horas prestadas para cada una de estas categorías (techo diario por categoría) <br> Debe detectar que, si uno de los registros trae un subtercero que coincide con uno de la columna A en la hoja Techo de horarios, debe cambiar la categoría como corresponde. <br> también debe tenerse en cuenta el calendario que estará en una hora “Calendario anual” de este masterfile con los días que son considerados feriado, para así tomar el techo diario correcto. <br> 5° Sumamos el total de horas prestadas para el día filtrado. <br> 6° Verificamos si el Total de horas prestadas para el día filtrado corresponde al total de horas de la hoja “techo diario” del masterfile (siempre que sea menor o igual esta ok.) <br> 7° En caso obtener alguna diferencia, se genera un nuevo Excel en la ruta Bot HR010 – Control Horas Seguridad\4_Diferencias Diarias (BOT) \yyyy_MM <br> nomenclatura: Diferencia diaria control seguridad dd.mm. yyyy <br> Dentro de este Excel tendremos una tabla con las diferencias encontradas en la fecha en cuestión y en otra hoja todos los registros asociados para ese día. <br> 8° Dentro del creado en el paso anterior, generamos una tabla pívot con el resumen total de las horas. Las que tengan algún tipo de diferencia tendrán un estado igual a “pendiente” |  |

## Reporte mensual

| N° | Acción | Detalle | Excepción |
| --- | --- | --- | --- |
|  | Periodicidad | El primer control debe realizarse los días, debe ejecutarse el 5 de cada mes. Con lo cual se ejecutará a mes vencido. |  |
|  | Tomamos tabla pívot | Tomando los valores generados en la tabla pívot del paso 3.2.3 Control diario acumulado , generamos una tabla con el resumen mensual de las horas, filtrando todas las horas del mes vencido. <br> 1° Debemos procesar los casos de cada pívot diaria con las diferencias encontradas que estarán en la ruta Bot 4_Diferencias Diarias (BOT) \yyyy_MM <br> 2° Por defecto las horas que están OK se tomaran como están. <br> 3° Para los casos con estado igual a pendiente, deberemos buscar si en la columna aprobación tenemos el valor sí o no, en caso de que este en SI, tomaremos las horas de que están en la pívot, en el campo horas aprobadas se pondrá este valor y en campo estado “Aprobadas”. <br> 4° En el caso de que el campo aprobación sea igual a no, entonces el Bot deberá tomar las horas del techo diario, poner este valor en campo horas aprobadas y cambiar el estado a rechazadas. | 4.2.7 Estado aún pendiente |
|  | Controlamos techo horas mensual | Controlamos que las horas totales del techo mensual y por categoría (distinguiendo día normal de feriado) teniendo en cuenta el desvío de la hoja Techo diario del campo “Diferencia de horas mensuales aceptada” por categoría. |  |
|  | Generamos Excel mensual | Generamos un Excel con solo los datos del mes controlado con la nomenclatura: Reporte-Mensual MM en la ruta: <br> \5_Reporte Mensual Horas (BOT) \yyyy_MM |  |
|  | Envió de alerta | En caso de que exista diferencia se enviara la notificación de alerta del paso 3.4.3 CONTROL Mensual Envío de mail de notificación final Exitosa sin Excepciones Negocio Sin diferencias de horas <br> En caso de no exista diferencia se enviará la notificación del paso 3.4.6 CONTROL mensual Envío de mail de notificación final Exitosa sin Excepciones Negocio y con diferencias al momento de validar las horas |  |

## MasterFile Configuraciones

|  | MasterFile Configuraciones <br> Parametros | Nuevo MasterFile de configuraciones para que el área pueda modificarlo. <br> Antes de ejecutar Control 1, Control 2 y Control 3, el bot tomará los campos correspondientes según qué control se desee ejecutar (días, parámetros, etc.). |  |
| --- | --- | --- | --- |
|  | Reiniciar el/los Dias | Si ingresás los números, el bot toma ese valor; por ejemplo, 01. Luego filtra el día 01 y lo vacía, para después volver a generarlo con la información más actualizada. |  |

## Obtener Link Sharepoint

|  | Obtener Link Reporte control Horas seguridad | El bot debe abrir la carpeta 3_Control Horas (BOT) <br> Y se comenzará a escribir en el buscador, por ejemplo: ‘Reporte Control Horas Seguridad 01.xlsx’. <br> Se seleccionará la primera fila, luego se hará clic derecho y se seleccionará ‘ Copy Link’ . Se deberá esperar 5 segundos hasta que aparezca la ventana indicando que el enlace ya fue copiado. |  |
| --- | --- | --- | --- |

## Nuevo Destinario Adicional en MasterFile

|  | Destinario adicional | Dentro del MasterFile de Configuraciones, para que el área pueda modificar los correos que desee agregar o eliminar. <br> Para multiple direcciones, utilizar “;” como separador. <br> Ej : Ejemplo1@vw.com.ar;Ejemplo2@vw.com.ar |  |
| --- | --- | --- | --- |

## Notificación final del Bot

| N° | Acción | Detalle | Excepción |
| --- | --- | --- | --- |
|  | CONTROL 1 <br> Envío de mail de notificación final Exitosa sin Excepciones Negocio. | Para el caso donde no tengamos ningún que arroje el resultado “Verificar” enviaremos el siguiente mail: <br> Asunto mail: BOT HR010 \| Notificación de proceso del Bot \| CORRECTO <br> Cuerpo mail: El Bot HR010 terminó su procesamiento en el día de la fecha sin excepciones, <br> Para una información más detallada se muestra un resumen de los saldos. <br> Para una información más detallada se adjunta la ruta de acceso al Masterfile y reporte generado por el proceso: <br> Bot HR010 – Control Horas Seguridad |  |
|  | CONTROL 2 <br> Envío de mail de notificación final Exitosa sin Excepciones Negocio <br> Sin diferencias encontradas | Para el caso donde no tengamos ninguna diferencia encontrada posterior a ejecutar el proceso: <br> Asunto mail: BOT HR010 \| Notificación de proceso del Bot \| CORRECTO <br> Cuerpo mail: El Bot HR010 terminó su procesamiento en el día de la fecha sin excepciones, y sin diferencias encontradas. <br> Para una información más detallada se muestra de las horas validadas. <br> Bot HR010 – Control Horas Seguridad |  |
|  | CONTROL Mensual <br> Envío de mail de notificación final Exitosa sin Excepciones Negocio <br> Sin diferencias de horas | Asunto mail: BOT HR010 \| Notificación de proceso del Bot \| CORRECTO <br> Cuerpo mail: El Bot HR010 terminó su procesamiento en el día de la fecha sin excepciones, y sin diferencias encontradas en el control mensual. <br> Para una información más detallada se muestra de las horas validadas <br> Para una información más detallada se adjunta la ruta de acceso al reporte mensual generado por el proceso: <br> Enlace acceso : <br> [PATH ruta con el reporte mensual generado por el bot] <br> Cordialmente, <br> Bot HR010 – Control Horas Seguridad |  |
|  | CONTROL 1 <br> Envío de mail de notificación final Exitosa con Excepciones Negocio o diferencia entre | Asunto mail: BOT HR010 \| Notificación de proceso del Bot \| ADVERTENCIA <br> Cuerpo mail El BOT HR010 terminó la etapa de retenciones en el día de la fecha, sin embargo, se presentaron algunas excepciones <br> Para una información más detallada se adjunta la ruta de acceso al masterfile generado por el proceso: <br> Enlace acceso : <br> [PATH Ruta Master File] <br> Cordialmente, <br> Bot HR010 – Control Horas Seguridad. |  |
|  | CONTROL 2 <br> Envío de mail de notificación final Exitosa sin Excepciones Negocio y con diferencias al momento de validar las horas | En caso de que tengamos diferencias de horas y estas mismas no sean validadas de forma manual, debemos mandar el siguiente mail con todas las fechas del mes con esta situación: <br> Asunto mail: BOT HR010 \| Notificación de proceso del Bot \| ADVERTENCIA <br> Cuerpo mail El BOT HR010 terminó su procesamiento el día la fecha, sin embargo, se encontraron diferencias al validar las horas del informe biométrico. <br> Bot HR010 – Control Horas Seguridad. |  |
|  | CONTROL mensual <br> Envío de mail de notificación final Exitosa sin Excepciones Negocio y con diferencias al momento de validar las horas | Asunto mail: BOT HR010 \| Notificación de proceso del Bot \| ADVERTENCIA <br> Cuerpo mail El BOT HR010 terminó su procesamiento día de la fecha correspondiente al mes MMM (nombre del mes) con diferencias detectadas las cuales fueron validadas previamente: <br> Podrán tener acceder al reporte mensual generado por el Bot en el siguiente enlace. <br> Enlace de acceso: <br> [Link reporte mensual ] <br> Cordialmente, <br> Bot HR010 – Control Horas Seguridad. |  |
|  | Envío de mail de notificación final Errónea | Asunto mail: BOT HR010 \| Notificación de proceso del Bot \| ERROR TÉCNICO <br> Cuerpo mail: Se les informa que ha finalizado el proceso, sin embargo, se registraron excepciones técnicas, el equipo de soporte estará tomando el caso y se pondrá en contacto para brindarles más información. <br> Información técnica : <br> [LINEA ERROR] línea: 79 - Unable to find CLIENT. Search Criteria did not match . <br> [ PATHLOGS ] <br> Cordialmente <br> Bot HR010 – Control Horas Seguridad. |  |

## Criterios de Aceptación

|--------------------------------------------------------------------------------------------------------------------------------------|
| El Bot debe ejecutar el control 1 y cargar casos tanto con diferencias como sin ellas de forma correcta en el master files           |
| El Bot al ejecutar el control 2 debemos identificar al menos 5 casos con diferencias no aprobadas y 5 casos de diferencias aprobadas |
| El Bot debe realizar bien los controles basados en suma de “horas aprobadas “                                                        |
| El Bot debe generar de forma correcta el Excel con diferencias con casos de diferencias que sobrepasen el techo diario               |
| El Bot debe generar de forma correcta la tabla pívot con el resumen de los casos procesados                                          |
| El Bot debe enviar de forma correcta la notificación control 1                                                                       |
| El Bot debe generar de forma correcta el Excel con el resumen de ejecución mensual con los casos del mes controlado                  |
| El Bot debe enviar de forma correcta la notificación del control 2 para los casos con y sin diferencias                              |
| El Bot debe enviar de forma correcta la notificación del reporte mensual                                                             |

# Supuestos y Excepciones

## Suposiciones y Restricciones

*Detalle del listado de suposiciones y restricciones que se asumen para
abordar la automatización del proceso.*

| N° | Suposición / Restricción |
| --- | --- |
|  | Se asume que las rutas de la compartida estarán accesibles al Bot y tendrá permisos de escritura. |
|  | Se asume que el Bot utilizará como casilla de envío de mail la asignada al runner de este. |

## Excepciones

**Excepciones de Sistema:**

| N° | Escenario | Acción |
| --- | --- | --- |
|  | No existe archivo input o no hay acceso a ruta compartida | En el caso de que no haya acceso a ruta compartida o no se encuentra el archivo input, se notificará la detención del proceso e informará a los usuarios con el siguiente mail: <br> Ejemplo de mail : <br> Asunto mail: BOT HR010 \| Notificación de proceso del Bot \| ADVERTENCIA <br> Cuerpo mail: El Bot HR010 terminó su procesamiento en el día de la fecha debido a que no hay acceso a la ruta compartida. <br> Acción: ( completar con la acción por parte del usuario o el equipo de soporte) <br> Cordialmente <br> Bot HR010 – Control Horas Seguridad |
**Excepciones de negocio:**

|  | Cliente con más de un registro | Puede darse el caso que tengamos más de un registro en el reporte mano de obra, esto es debido a que una persona puede tener horas registradas en más de un cliente, para estos casos hay que sumar ambas horas del reporte de mano de obra y validar que correspondan con el reporte biométrico. <br> Luego en reporte de control de horas MM que se genera en el OneDrive 3_Control Horas (BOT) se registrarán uno por cada registro que se tenga en el informe de presentismo, replicando las horas totales del informe biométrico (el cual no acepta registros duplicados) y en caso de que la suma de las horas sea igual entre el reporte de presentimos y el biométrico se pondrá en el estado, “OK, suma total de horas de presentismo es correcta”. En caso contrario Verificar |
| --- | --- | --- |
|  | Duplicados en reporte biométrico | Debemos validar que no haya duplicados en el reporte del biométrico, si los hay se debe detener el proceso y enviar la notificación: <br> Ejemplo de mail : <br> Cuerpo mail: <br> El HR010 terminó su procesamiento en el día de la fecha debido a que existen más de un registro por persona en el reporte biométrico, por favor validar la información del reporte <br> Acción: ( El área de negocio debe validar el reporte biométrico generado) <br> Cordialmente <br> Bot HR010 – Control Horas Seguridad |
|  | No existen informes biométricos a procesar | Si en caso de que luego de que no existan ningún informe biométrico del mes se detendrá el bot y se enviara el siguiente mail <br> Ejemplo de mail : <br> Cuerpo mail: <br> El HR010 terminó su procesamiento en el día de la fecha debido a que no existen ningún informe biométrico del mes MM (mes de ejecución) para procesar, por favor revisar la ruta [Ruta donde deberían estar los biométricos] para verificar esta situación <br> Acción: ( El área de negocio debe validar el problema) <br> Cordialmente <br> Bot HR010 – Control Horas Seguridad |
|  | No existen informes biométricos o mano de obra de la ejecución o días anteriores | En caso de que al ejecutar el proceso no existan reportes biométricos o de mano de obra del día de la fecha de ejecución o anteriores, estos días se marcaran como “Falta reporte biométrico” y deberán ser informados en un Excel con la nomenclatura “estado existencia reportes” en la ruta pendiente donde estarán con el estado “pendiente” <br> Luego se agregará una tabla con todos los registros pendientes en el mail de notificación 3.4.4 CONTROL 1 <br> Envío de mail de notificación final Exitosa con Excepciones Negocio |
|  | Estado aún pendiente | En caso de que al tomar los valores de las pívots con las diferencias diarias están tengan diferencias sin validar es decir con el estado “pendiente” entonces el Bot, deberá detener sui ejecución e informar el mail de notificación final de advertencia de control mensual que existe diferencias que aún no han sido analizadas. <br> Asunto mail: BOT HR010 \| Notificación de proceso del Bot \| ADVERTENCIA <br> Cuerpo mail El BOT HR010 terminó su procesamiento día de la fecha, sin embargo, existen diferencias diarias que no han sido aprobadas/rechazadas por el área de negocio <br> Podrán tener acceder al reporte con pendientes por el Bot en el siguiente enlace. <br> Enlace de acceso: <br> [Link recurso compartido output] <br> Cordialmente, <br> Bot HR010 – Control Horas Seguridad. |

# Sign-off 

## Interno

|                 | **Sign-off**     |                |          |
|-----------------|------------------|----------------|----------|
|                 | **Name**         | **Date**       | **Role** |
| **Reviewed by** | **Garcia David** | **07/08/2025** | **FA**   |
| **Approved by** |                  |                |          |

## Cliente

|                 | **Sign-off** |                |          |
|-----------------|--------------|----------------|----------|
|                 | **Name**     | **Email date** | **Role** |
| **Reviewed by** |              |                |          |
| **Approved by** |              |                |          |

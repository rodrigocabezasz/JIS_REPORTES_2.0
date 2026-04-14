---
tipo: formulario
area: servicio_cliente
codigo: FORM-SC-002
version: 1.0
fecha_actualizacion: 2026-03-17
responsable: Encargados y Supervisores
tags: [formulario, siniestro, incidente, estacionamiento, cliente, daños, reclamo]
---

# Formulario de Registro de Siniestro

## INFORMACIÓN DEL FORMULARIO
- **Código**: FORM-SC-002
- **Tipo**: Formulario Oficial
- **Área**: Servicio de Estacionamiento
- **Empresa**: JIS Parking SpA
- **Criticidad**: 🔴 Alta
- **Formato**: Físico en carpeta de sucursal

## ALCANCE
**Aplica a**: 
- Todas las sucursales de JIS PARKING
- Incidentes que involucren daños a vehículos de clientes
- Robos o pérdidas de objetos dentro del estacionamiento
- Accidentes con lesiones personales en instalaciones
- Cualquier situación que genere responsabilidad de la empresa

**Uso del Formulario**:
- ✅ Cliente reporta daño a su vehículo
- ✅ Cliente reporta robo de objetos
- ✅ Accidentes con lesiones en instalaciones
- ✅ Reclamos por responsabilidad de la empresa
- ✅ Documentación para gestión con seguros

## OBJETIVO
Documentar formalmente cualquier siniestro o incidente reportado por un cliente mientras su vehículo se encuentra bajo custodia de JIS PARKING, registrando todos los datos necesarios para la investigación, gestión de seguros y resolución del caso.

## RELACIÓN CON OTROS DOCUMENTOS
Este formulario físico es el **complemento documental** del [Procedimiento de Registro de Siniestros (PROC-SC-001)](servicio_cliente_siniestros_registro_procedimiento.md), que detalla el proceso completo de registro en el sistema ERP JIS.

---

## INSTRUCCIONES DE LLENADO

### Datos Administrativos
- **Folio N°**: Número correlativo del formulario (asignado por sucursal)
- **Fecha**: Fecha de llenado del formulario (formato: DD/MM/AAAA)
- **Empresa**: JIS Parking SpA
- **Sucursal/Estacionamiento**: Nombre de la sucursal donde ocurrió el incidente
- **Dirección**: Dirección física de la sucursal

---

## SECCIONES DEL FORMULARIO

### 1. IDENTIFICACIÓN DEL CLIENTE

| Campo | Descripción | Obligatorio | Validación |
|-------|-------------|-------------|------------|
| **Nombre del usuario** | Nombre completo del cliente | ✅ Sí | Coincidir con documento |
| **RUT/Documento de identidad** | Cédula de identidad o pasaporte | ✅ Sí | Formato RUT: 12.345.678-9 |
| **Teléfono** | Número de contacto del cliente | ✅ Sí | Formato: +56912345678 |
| **Correo electrónico** | Email principal de contacto | ✅ Sí | Formato email válido |

**Instrucciones**:
- **OBLIGATORIO**: Solicitar cédula de identidad o pasaporte
- Fotografiar o fotocopiar documento de identidad
- Verificar que todos los datos coincidan
- Confirmar datos de contacto (teléfono y correo son críticos para seguimiento)

---

### 2. IDENTIFICACIÓN DEL VEHÍCULO

| Campo | Descripción | Obligatorio | Validación |
|-------|-------------|-------------|------------|
| **Patente** | Placa del vehículo | ✅ Sí | Formato: ABCD12 o AB1234 |
| **Marca** | Marca del vehículo | ✅ Sí | Ej: Toyota, Chevrolet, Mazda |
| **Modelo** | Modelo específico | ✅ Sí | Ej: Corolla, Spark, CX-5 |
| **Año** | Año de fabricación | ✅ Sí | Formato: AAAA |
| **Color** | Color principal del vehículo | ✅ Sí | Descripción exacta |
| **Permiso circulación al día** | Vigencia del permiso | ✅ Sí | Marcar: SI ( ) / NO ( ) |
| **Posee seguro** | Vehículo tiene seguro vigente | ✅ Sí | Marcar: SI ( ) / NO ( ) |

**Instrucciones**:
- Solicitar al cliente el **permiso de circulación**
- Fotografiar el permiso de circulación
- Si tiene seguro, solicitar datos de la compañía aseguradora
- Verificar datos del vehículo contra ingreso en sistema

### ⚠️ Preguntas Adicionales Importantes

#### Permiso de Circulación al Día
- **SI ( )**: Cliente presenta permiso vigente
- **NO ( )**: Anotar en observaciones y verificar

#### Posee Seguro
- **SI ( )**: Solicitar datos de aseguradora, número de póliza, contacto
- **NO ( )**: Anotar en observaciones (puede afectar proceso de indemnización)

---

### 3. INFORMACIÓN DEL ESTACIONAMIENTO

| Campo | Descripción | Fuente | Validación |
|-------|-------------|--------|------------|
| **Fecha de ingreso al estacionamiento** | Fecha de entrada del vehículo | Sistema ERP | Formato: DD/MM/AAAA |
| **Hora de ingreso registrada** | Hora exacta de ingreso | Sistema ERP | Formato: HH:MM |

**Instrucciones**:
- Buscar en sistema ERP JIS por patente del vehículo
- Confirmar fecha y hora de ingreso registrada en sistema
- Calcular tiempo de permanencia hasta el momento del reporte

---

### 4. DESCRIPCIÓN DEL SINIESTRO (Campo de Texto Libre)

**Instrucciones para el Encargado**:
Esta sección debe completarse detalladamente incluyendo:

#### Información Obligatoria a Registrar:

1. **Descripción del Incidente**
   - ¿Qué tipo de siniestro es? (daño, robo, accidente, etc.)
   - ¿Cuándo ocurrió o fue descubierto?
   - ¿Dónde ocurrió dentro del estacionamiento?

2. **Daños Reportados**
   - Descripción exacta de los daños visibles
   - Ubicación específica del daño en el vehículo
   - Gravedad estimada (leve, moderado, grave)

3. **Versión del Cliente**
   - Relato completo según el cliente
   - Registrar textualmente las declaraciones importantes

4. **Evidencias Inmediatas**
   - ¿Se tomaron fotografías? (SI/NO)
   - ¿Se revisaron cámaras? (SI/NO)
   - ¿Hay testigos? (SI/NO - registrar datos)

5. **Acciones Tomadas**
   - Qué se hizo inmediatamente después del reporte
   - A quién se notificó (supervisor, gerencia, seguros)

**Ejemplo de Descripción Completa**:
```
Cliente reporta rayado profundo en puerta del lado del conductor del vehículo.
El daño fue descubierto al momento de retiro (17:45 hrs).
Cliente ingresó a las 09:15 hrs del mismo día.
Se revisaron cámaras: se observa vehículo ya con rayado al momento de ingreso
(verificado en grabación 09:20 hrs).
Se informó al cliente que el daño es previo al ingreso.
Cliente acepta y retira reclamo.
Fotografías tomadas: SI. Archivo: FOTO_SINIESTRO_001_2026-03-17.jpg
```

---

## PROCEDIMIENTO DE ATENCIÓN INMEDIATA

### ✅ Pasos Obligatorios al Recibir Reporte de Siniestro

#### PASO 1: Mantener la Calma
- Recibir al cliente con empatía
- Escuchar atentamente su relato
- No asumir responsabilidad inmediata

#### PASO 2: Verificar Identidad
- Solicitar cédula de identidad
- Confirmar que el cliente es propietario o conductor autorizado
- Fotografiar documento

#### PASO 3: Inspeccionar el Vehículo
- Solicitar al cliente que muestre los daños
- Registrar con fotografías TODOS los daños
- Fotografiar desde múltiples ángulos
- Incluir foto de patente en cada serie

#### PASO 4: Revisar Cámaras de Seguridad
- **CRÍTICO**: Revisar ANTES de comprometer a la empresa
- Buscar momento de ingreso del vehículo
- Verificar si daño es pre-existente o nuevo
- Buscar momento exacto del incidente (si es posible)
- Grabar o capturar evidencia de cámaras

#### PASO 5: Completar Formulario
- Llenar todas las secciones con datos exactos
- No omitir información
- Ser objetivo en la descripción

#### PASO 6: Registro en Sistema ERP
- Ingresar siniestro en plataforma https://erpjis.web.app
- Seguir procedimiento PROC-SC-001
- Vincular formulario físico con registro digital

#### PASO 7: Notificar Supervisor
- Informar inmediatamente a supervisor
- Enviar copia digital del formulario
- Esperar instrucciones para gestión del caso

---

## CLASIFICACIÓN DE SINIESTROS

### 🔴 Siniestro Full (Con Deducible)
**Definición**: Incidentes de alto valor cubiertos por seguro de la empresa

**Ejemplos**:
- Choque entre vehículos dentro del estacionamiento
- Daño estructural grave causado por falla de infraestructura
- Incendio de vehículo por causas del estacionamiento
- Robo total del vehículo

**Gestión**:
- Notificar a gerencia INMEDIATAMENTE
- Contactar a compañía de seguros JIS
- No comprometer pagos sin autorización gerencial
- Documentar exhaustivamente

---

### 🟡 Siniestro Regular
**Definición**: Incidentes menores o de responsabilidad no cubierta por seguro

**Ejemplos**:
- Rayones o rozaduras menores
- Robo de objetos dentro del vehículo (sin forzamiento)
- Daños menores por estacionamiento inadecuado de terceros
- Pérdida de objetos personales

**Gestión**:
- Documentar según procedimiento
- Evaluar caso por caso
- Resolver con supervisor de sucursal
- Puede no requerir escalamiento a gerencia

---

## CASOS ESPECIALES

### ⚠️ Si el Cliente se Niega a Esperar Revisión de Cámaras
- Explicar que es necesario para proteger sus derechos
- Ofrecer revisar cámaras mientras el cliente espera
- No dejar salir el vehículo sin documentar
- Si insiste en retirarse, hacer constar en formulario

### ⚠️ Si el Daño es Claramente Pre-Existente
- Mostrar al cliente evidencia de cámaras de ingreso
- Explicar con empatía que la empresa no es responsable
- Completar formulario y marcar como "daño pre-existente"
- Ofrecer copia del registro para el cliente

### ⚠️ Si Hay Lesiones Personales
- Priorizar atención médica del cliente
- Llamar ambulancia si es necesario
- Notificar INMEDIATAMENTE a gerencia
- Aislar zona del incidente
- No mover evidencias
- Tomar fotografías exhaustivas

### 🔴 Escalamiento URGENTE a Gerencia
Notificar inmediatamente si:
- Lesiones personales graves
- Robo con violencia o amenazas
- Incendio o explosión
- Daño estructural al edificio
- Situación de riesgo inminente
- Cliente amenaza con acciones legales

---

## ARCHIVO Y RETENCIÓN

### Archivo del Formulario
- **Ubicación física**: Carpeta "Siniestros" en caja fuerte de sucursal
- **Orden**: Por número de folio correlativo
- **Clasificación**: Por tipo de siniestro
- **Tiempo de retención**: 5 años mínimo (requisito legal)

### Respaldo Digital
- **Obligatorio**: Escanear formulario completado + fotografías
- **Ubicación**: `JIS_Cloud/Sucursal_[nombre]/Siniestros/[año]/`
- **Nombre archivo**: `FORM-SC-002_[Folio]_[Patente]_[Fecha].pdf`
- **Fotografías**: Carpeta separada con mismo código de folio

### Documentación Complementaria
- Copia de cédula de identidad del cliente
- Fotografías de daños (mínimo 5 fotos desde distintos ángulos)
- Captura de pantalla o video de cámaras de seguridad
- Permiso de circulación (copia)
- Datos de seguro (si aplica)
- Cualquier otro documento aportado por el cliente

---

## REFERENCIAS LEGALES Y NORMATIVAS

### Base Legal
- **Ley 19.496**: Protección de Derechos del Consumidor - Responsabilidad del proveedor
- **Código Civil Chileno**: Responsabilidad por culpa o negligencia
- **Contrato de Estacionamiento**: Límites de responsabilidad

### Documentos Relacionados
- **Procedimiento asociado**: [PROC-SC-001 - Procedimiento de Registro de Siniestros](servicio_cliente_siniestros_registro_procedimiento.md)
- **Normativa legal**: [Ley 19.496 - Protección del Consumidor](../legal/legal_ley_19496_proteccion_consumidor.md)

---

## PREGUNTAS FRECUENTES (FAQ)

### ¿Qué hacer si el cliente exige indemnización inmediata?
- Explicar que todos los siniestros deben investigarse
- No comprometer montos sin autorización
- Ofrecer proceso de evaluación rápido
- Escalar a supervisor para gestión

### ¿Puedo aceptar responsabilidad de la empresa?
- **NO**. Solo el gerente o representante legal puede hacerlo
- Registrar el caso objetivamente
- No opinar sobre culpas o responsabilidades
- Remitir decisiones a niveles superiores

### ¿Qué hacer si el cliente se niega a firmar el formulario?
- Explicar que es para proteger sus derechos
- Hacer constar en el formulario: "Cliente se niega a firmar"
- Solicitar a testigo (otro empleado) que firme como observador
- Foto o video del momento del registro

### ¿Qué hacer si no hay cámaras funcionando?
- Documentar que no hay evidencia de video
- Realizar investigación por otros medios
- Entrevistar a personal que estaba presente
- Escalar a gerencia para decisión

---

## HISTORIAL DE CAMBIOS

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | 2026-03-17 | Creación inicial basada en formulario físico oficial |

---

## ANEXO: PLANTILLA DE FORMULARIO

```
═══════════════════════════════════════════════════════════════

         FORMULARIO DE REGISTRO DE SINIESTRO
              SERVICIO DE ESTACIONAMIENTO

═══════════════════════════════════════════════════════════════

Folio Nº: _____                            Fecha: ___/___/_____

Empresa: JIS Parking SpA
Sucursal/Estacionamiento: _______________________________________
Dirección: ______________________________________________________

───────────────────────────────────────────────────────────────

1. IDENTIFICACIÓN DEL CLIENTE

Nombre del usuario: _____________________________________________

RUT/Documento de identidad: _____________________________________

Teléfono: _______________________________________________________

Correo electrónico: _____________________________________________

───────────────────────────────────────────────────────────────

2. IDENTIFICACIÓN DEL VEHÍCULO

Patente: ________________________________________________________

Marca: __________________________________________________________

Modelo: _________________________________________________________

Año: ____________________________________________________________

Color: __________________________________________________________

Permiso circulación al día:  SI ( ) / NO ( )

Posee seguro:  SI ( ) / NO ( )

  Si posee seguro, indicar:
  Compañía: _____________________________________________________
  Póliza N°: ____________________________________________________
  Contacto: _____________________________________________________

───────────────────────────────────────────────────────────────

3. INFORMACIÓN DEL ESTACIONAMIENTO

Fecha de ingreso al estacionamiento: ___/___/_____

Hora de ingreso registrada: __________

───────────────────────────────────────────────────────────────

4. DESCRIPCIÓN DEL SINIESTRO

Tipo de incidente: _______________________________________________

Fecha y hora del reporte: ___/___/_____ a las _____

Descripción detallada:
________________________________________________________________
________________________________________________________________
________________________________________________________________
________________________________________________________________
________________________________________________________________
________________________________________________________________
________________________________________________________________
________________________________________________________________

Daños observados:
________________________________________________________________
________________________________________________________________
________________________________________________________________

Se revisaron cámaras:  SI ( ) / NO ( )
Se tomaron fotografías:  SI ( ) / NO ( )
Hay testigos:  SI ( ) / NO ( )

Testigos (nombre y contacto):
________________________________________________________________
________________________________________________________________

───────────────────────────────────────────────────────────────

ACCIONES INMEDIATAS TOMADAS:
________________________________________________________________
________________________________________________________________
________________________________________________________________

EVALUACIÓN PRELIMINAR:
________________________________________________________________
________________________________________________________________

───────────────────────────────────────────────────────────────

Firma del Cliente: __________________  Fecha: ___/___/_____

Firma del Encargado: ________________  Fecha: ___/___/_____

Nombre Encargado: _______________________________________________

═══════════════════════════════════════════════════════════════

PARA USO EXCLUSIVO DE GERENCIA:

Clasificación: FULL ( )  REGULAR ( )

Resolución:
________________________________________________________________
________________________________________________________________

Autorizado por: _____________________  Fecha: ___/___/_____

═══════════════════════════════════════════════════════════════
```

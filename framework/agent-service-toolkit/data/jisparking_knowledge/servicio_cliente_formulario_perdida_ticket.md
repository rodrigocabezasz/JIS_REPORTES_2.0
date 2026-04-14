---
tipo: formulario
area: servicio_cliente
codigo: FORM-SC-001
version: 1.0
fecha_actualizacion: 2026-03-17
responsable: Encargados y Supervisores
tags: [formulario, perdida_ticket, ticket, estacionamiento, registro, cliente]
---

# Formulario Oficial - Registro por Pérdida de Ticket

## INFORMACIÓN DEL FORMULARIO
- **Código**: FORM-SC-001
- **Tipo**: Formulario Oficial
- **Área**: Servicio de Estacionamiento
- **Empresa**: JIS Parking SpA
- **Criticidad**: 🟡 Media
- **Formato**: Físico en carpeta de sucursal

## ALCANCE
**Aplica a**: 
- Todas las sucursales de JIS PARKING
- Casos donde el cliente extravió su ticket de estacionamiento
- Registro manual cuando el sistema requiere documentación física

**Uso del Formulario**:
- ✅ Cliente perdió su ticket de ingreso
- ✅ Ticket dañado o ilegible
- ✅ Sistema requiere validación manual de salida
- ✅ Registro de información para cobro por pérdida

## OBJETIVO
Documentar formalmente la pérdida de ticket de estacionamiento por parte del cliente, registrando todos los datos necesarios para validar su ingreso y procesar su salida según las políticas de la empresa.

## INSTRUCCIONES DE LLENADO

### Datos Administrativos
- **Folio N°**: Número correlativo del formulario (asignado por sucursal)
- **Fecha**: Fecha de llenado del formulario (formato: DD/MM/AAAA)
- **Empresa Administradora**: JIS Parking SpA
- **Sucursal/Estacionamiento**: Nombre de la sucursal donde ocurre la pérdida
- **Dirección**: Dirección física de la sucursal

---

## SECCIONES DEL FORMULARIO

### 1. IDENTIFICACIÓN DEL USUARIO

| Campo | Descripción | Obligatorio | Validación |
|-------|-------------|-------------|------------|
| **Nombre del usuario** | Nombre completo del cliente | ✅ Sí | Coincidir con documento |
| **RUT/Documento (opcional)** | Cédula de identidad o pasaporte | ⚪ Opcional | Formato RUT: 12.345.678-9 |
| **Teléfono** | Número de contacto del cliente | ✅ Sí | Formato: +56912345678 |
| **Correo electrónico** | Email de contacto | ✅ Sí | Formato email válido |

**Instrucciones**:
- Solicitar documento de identidad al cliente (cedula, pasaporte, licencia)
- Verificar que los datos coincidan con el documento
- Si el cliente no desea proporcionar RUT, dejar en blanco (campo opcional)
- Teléfono y correo son OBLIGATORIOS para seguimiento

---

### 2. IDENTIFICACIÓN DEL VEHÍCULO

| Campo | Descripción | Obligatorio | Validación |
|-------|-------------|-------------|------------|
| **Patente** | Placa del vehículo | ✅ Sí | Formato: ABCD12 o AB1234 |
| **Marca** | Marca del vehículo | ✅ Sí | Ej: Toyota, Chevrolet, Mazda |
| **Modelo** | Modelo específico | ✅ Sí | Ej: Corolla, Spark, CX-5 |
| **Color** | Color principal del vehículo | ✅ Sí | Descripción simple |
| **Año** | Año de fabricación | ⚪ Opcional | Formato: AAAA |

**Instrucciones**:
- CRÍTICO: Verificar la patente con el sistema de ingreso
- Solicitar al cliente que describa su vehículo
- Validar datos del vehículo contra registro de entrada en cámaras
- Si hay discrepancia, escalar a supervisor

---

### 3. INFORMACIÓN REGISTRADA EN EL SISTEMA

| Campo | Descripción | Fuente | Validación |
|-------|-------------|--------|------------|
| **Fecha de ingreso** | Fecha en que ingresó el vehículo | Sistema ERP | Formato: DD/MM/AAAA |
| **Hora de ingreso registrada** | Hora exacta de ingreso | Sistema ERP | Formato: HH:MM |
| **Fecha de salida** | Fecha de procesamiento de salida | Sistema ERP | Formato: DD/MM/AAAA |

**Instrucciones**:
- Buscar en el sistema ERP JIS por patente del vehículo
- Registrar fecha y hora de ingreso según sistema
- Calcular el tiempo de permanencia
- Aplicar tarifa correspondiente según reglamento

---

## PROCEDIMIENTO DE VERIFICACIÓN

### ✅ Pasos de Validación Obligatorios

1. **Verificar Identidad del Cliente**
   - Solicitar documento de identidad
   - Confirmar nombre y datos coinciden

2. **Buscar Vehículo en Sistema**
   - Ingresar patente en ERP JIS
   - Verificar que existe registro de ingreso activo
   - Confirmar fecha y hora de ingreso

3. **Validar con Cámaras de Seguridad**
   - Revisar video del ingreso según hora registrada
   - Confirmar que patente, marca, modelo y color coinciden
   - Verificar presencia del vehículo en zona de estacionamiento

4. **Calcular Tarifa**
   - Calcular tiempo de permanencia
   - Aplicar tarifa por pérdida de ticket según política
   - Informar monto al cliente

5. **Completar Formulario**
   - Llenar todos los campos obligatorios
   - Solicitar firma del cliente
   - Firma del encargado responsable

---

## POLÍTICA DE COBRO POR PÉRDIDA DE TICKET

### Tarifa Aplicable
- **Cobro estándar**: Tarifa máxima diaria del estacionamiento
- **Descuento**: Si se puede verificar hora de ingreso y permanencia menor a 1 día, aplicar tarifa real + recargo administrativo

### ⚠️ Casos Especiales

#### Si NO se encuentra registro de ingreso:
1. Solicitar al cliente prueba adicional (recibo, mensaje, etc.)
2. Revisar manualmente cámaras de las últimas 48 horas
3. Si no se encuentra evidencia, escalar a supervisor
4. Considerar no permitir el retiro del vehículo hasta verificación

#### Si el vehículo lleva más de 7 días:
1. Aplicar tarifa máxima acumulada
2. Verificar con cámaras si el vehículo está abandonado
3. Informar a gerencia para evaluación
4. Considerar proceso de denuncia si aplica

---

## ARCHIVO Y RETENCIÓN

### Archivo del Formulario
- **Ubicación física**: Carpeta "Pérdida de Tickets" en oficina de sucursal
- **Orden**: Por número de folio correlativo
- **Tiempo de retención**: 3 años mínimo

### Respaldo Digital
- Escanear o fotografiar formulario completado
- Guardar en carpeta compartida: `JIS_Cloud/Sucursal_[nombre]/Perdidas_Ticket/[año]/`
- Nombrar archivo: `FORM-SC-001_[Folio]_[Patente]_[Fecha].pdf`

---

## CASOS DE ESCALAMIENTO

### ⚠️ Escalar a Supervisor si:
- Cliente disputa la tarifa cobrada
- No se encuentra registro del vehículo en sistema
- Vehículo lleva más de 7 días estacionado
- Cliente no puede acreditar identidad
- Datos del vehículo no coinciden con sistema
- Cliente se niega a pagar la tarifa por pérdida

### 🔴 Escalar a Gerencia si:
- Situación de potencial fraude
- Cliente amenaza con acciones legales
- Vehículo abandonado por más de 30 días

---

## REFERENCIAS LEGALES Y NORMATIVAS

### Base Legal
- **Ley 19.496**: Protección de Derechos del Consumidor
- **Contrato de Estacionamiento**: Cláusula de pérdida de ticket
- **Reglamento Interno JIS**: Política de cobros por pérdida

### Documentos Relacionados
- Ver: [servicio_cliente_siniestros_registro_procedimiento.md](servicio_cliente_siniestros_registro_procedimiento.md)
- Ver: [legal_ley_19496_proteccion_consumidor.md](../legal/legal_ley_19496_proteccion_consumidor.md)

---

## PREGUNTAS FRECUENTES (FAQ)

### ¿Qué hacer si el cliente no recuerda cuándo ingresó?
- Solicitar al cliente un rango aproximado (día, horario)
- Buscar en cámaras de seguridad por patente
- Si no se encuentra, aplicar tarifa máxima

### ¿Puedo permitir que el cliente salga sin pagar?
- **NO**. El pago es requisito obligatorio antes de liberar el vehículo
- Si el cliente no puede pagar, ofrecer métodos de pago alternativos
- En caso de conflicto, escalar a supervisor

### ¿Qué hacer si el ticket apareció después de completar el formulario?
- Validar ticket original
- Si es válido, cobrar tarifa del ticket
- Conservar formulario para registro
- Anotar en observaciones que ticket fue encontrado

---

## HISTORIAL DE CAMBIOS

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | 2026-03-17 | Creación inicial basada en formulario físico oficial |

---

## ANEXO: PLANTILLA DE FORMULARIO

```
═══════════════════════════════════════════════════════════════

         FORMULARIO OFICIAL - REGISTRO POR PÉRDIDA DE TICKET
              SERVICIO DE ESTACIONAMIENTO

═══════════════════════════════════════════════════════════════

Folio Nº: _____                            Fecha: ___/___/_____

Empresa Administradora: JIS Parking SpA
Sucursal/Estacionamiento: Filtro
Dirección: Automático al registrar el filtro "sucursal"

───────────────────────────────────────────────────────────────

1. IDENTIFICACIÓN DEL USUARIO

Nombre del usuario: _____________________________________________

RUT/Documento (opcional): _______________________________________

Teléfono: _______________________________________________________

Correo electrónico: _____________________________________________

───────────────────────────────────────────────────────────────

2. IDENTIFICACIÓN DEL VEHÍCULO

Patente: ________________________________________________________

Marca: __________________________________________________________

Modelo: _________________________________________________________

Color: __________________________________________________________

Año: ____________________________________________________________

───────────────────────────────────────────────────────────────

3. INFORMACIÓN REGISTRADA EN EL SISTEMA

Fecha de ingreso: ___/___/_____

Hora de ingreso registrada: __________

Fecha de salida: ___/___/_____

───────────────────────────────────────────────────────────────

TARIFA APLICADA: $_________________

FORMA DE PAGO: _____________________

───────────────────────────────────────────────────────────────

Firma del Cliente: __________________  Fecha: ___/___/_____

Firma del Encargado: ________________  Fecha: ___/___/_____

═══════════════════════════════════════════════════════════════
```

# RTX-LEGAL-002 · Contrato de Servicio SaaS Roustix

| Campo | Valor |
|-------|-------|
| **Código** | RTX-LEGAL-002 |
| **Versión** | **0.1.0** |
| **Estado** | 🟡 Borrador · no firmar sin revisión jurídica |
| **Fecha** | 2026-08-03 |
| **Sustituye** | SAA-LEG-001 (plantilla piloto) |
| **Acepta / firma** | Empresa cliente (representante autorizado) |
| **Referencias** | [COM-01](../com/COM-01-planes-licenciamiento.md) · [RTX-SUP-001](RTX-SUP-001-politica-soporte.md) · [RTX-SLA-001](RTX-SLA-001-acuerdo-nivel-servicio.md) · [RTX-PRIV-001](RTX-PRIV-001-politica-privacidad.md) |

> **Aviso:** Este modelo no fija todavía topes de responsabilidad, jurisdicción definitiva, régimen tributario ni compromisos SLA. Esos puntos requieren decisión de los socios y asesoría profesional.

---

## Capítulo I · Partes y definiciones

### 1. Partes

**EL PRESTADOR** (en adelante, «Roustix» o «el Prestador»):

| Campo | Diligenciar |
|-------|-------------|
| Nombre / razón social | `[PENDIENTE · identidad jurídica]` |
| Tipo de persona | ☐ Persona jurídica  ☐ Personas naturales |
| Identificación / NIT | `[PENDIENTE]` |
| Domicilio | `[PENDIENTE]` |
| Correo contractual | `[PENDIENTE]` |
| Representante | `[PENDIENTE]` |

**EL CLIENTE** (en adelante, «el Cliente»):

| Campo | Diligenciar |
|-------|-------------|
| Razón social | ______________________________ |
| NIT | ______________________________ |
| Domicilio | ______________________________ |
| Representante autorizado | ______________________________ |
| Correo contractual | ______________________________ |
| Correo de facturación | ______________________________ |
| Tenant / slug | ______________________________ |

### 2. Definiciones

| Término | Significado |
|---------|-------------|
| **Plataforma** | Software Roustix ofrecido en modalidad SaaS (mantenimiento, inventario y módulos habilitados). |
| **Plan** | Start, Business, Enterprise u otro pactado en la Orden, según COM-01 vigente o condiciones especiales firmadas. |
| **Orden** | Acta de Servicio, propuesta aceptada u orden comercial que concreta plan, cupos, precio, vigencia y anexos. |
| **Usuario** | Persona natural autorizada por el Cliente para acceder al tenant. |
| **Datos del Cliente** | Información que el Cliente o sus Usuarios cargan o generan en la Plataforma. |
| **SLA** | Documento RTX-SLA-001, aplicable **solo** si se anexa expresamente a este Contrato. |
| **Política de Soporte** | Documento RTX-SUP-001, que describe canales y alcance del soporte. |
| **Documentos de Privacidad** | RTX-PRIV-001 y anexos aplicables, y acuerdo de transmisión de datos cuando se firme. |

---

## Capítulo II · Objeto

### 3. Objeto

El Prestador habilita al Cliente el acceso no exclusivo, no transferible y revocable a la Plataforma bajo modalidad **Software as a Service (SaaS)**, para los módulos, usuarios, sedes, almacenamiento y período definidos en la Orden.

Este Contrato **no** transfiere propiedad intelectual de la Plataforma ni convierte al Cliente en licenciatario de código fuente.

---

## Capítulo III · Licencia SaaS

### 4. Licencia de uso

Durante la vigencia y mientras el Cliente esté al día en sus obligaciones:

1. El Prestador otorga una licencia de uso remoto de la Plataforma limitada al alcance de la Orden.
2. El acceso se realiza por Internet, mediante cuentas individuales y controles de la Plataforma.
3. Queda prohibido: sublicenciar, revender el acceso, eludir controles multi-tenant, realizar ingeniería inversa salvo lo permitido por ley, o usar la Plataforma para fines ilícitos.
4. El Cliente es responsable del uso que hagan sus Usuarios.

---

## Capítulo IV · Plan contratado

### 5. Plan y cupos

El plan, precio, usuarios, sedes, módulos y almacenamiento quedan fijados en la **Orden**. La matriz comercial de referencia es COM-01; cualquier condición especial prevalece solo si está firmada en la Orden.

| Plan | Referencia comercial |
|------|----------------------|
| ☐ Start | COM-01 |
| ☐ Business | COM-01 |
| ☐ Enterprise | COM-01 · cotización |
| ☐ Personalizado | Orden |

Add-ons recurrentes o servicios profesionales se rigen por COM-02 y/o la Orden.

---

## Capítulo V · Servicios incluidos

### 6. Servicios base

Durante la vigencia, y según el plan contratado, el servicio incluye de forma general:

| Servicio | Condición |
|----------|-----------|
| Acceso a módulos habilitados | Según Orden |
| Actualizaciones generales de la Plataforma | Incluidas |
| Respaldos y recuperación | Conforme a controles operativos vigentes |
| HTTPS y controles de acceso por rol | Incluidos |
| Aislamiento lógico entre empresas (tenants) | Incluido |
| Soporte | Según plan · detalle en RTX-SUP-001 |
| Disponibilidad objetivo / créditos | **Solo** si se anexa RTX-SLA-001 |

El Prestador podrá modificar características no esenciales de la Plataforma para mejorar seguridad, estabilidad o funcionalidad, sin reducir el alcance material contratado sin aviso razonable.

---

## Capítulo VI · Obligaciones de Roustix

### 7. El Prestador se obliga a

1. Habilitar el acceso contratado en los plazos de la Orden.
2. Mantener controles razonables de seguridad, autenticación, permisos, cifrado en tránsito, auditoría, monitoreo y respaldo.
3. Prestar soporte conforme a RTX-SUP-001 y, si aplica, RTX-SLA-001.
4. Tratar los datos personales como encargado cuando corresponda, según los Documentos de Privacidad e instrucciones documentadas del Cliente.
5. Notificar incidentes de seguridad relevantes según la política y la ley aplicable.
6. Facilitar la exportación de Datos del Cliente al terminar, en los plazos de la Orden o política vigente.
7. No usar los Datos del Cliente para fines ajenos al servicio, salvo obligación legal o instrucción del Cliente.

---

## Capítulo VII · Obligaciones del Cliente

### 8. El Cliente se obliga a

1. Proporcionar información veraz para la contratación y facturación.
2. Designar administradores, gestionar Usuarios y roles, y proteger credenciales.
3. Usar la Plataforma de forma lícita y conforme a RTX-LEGAL-001 (cuando esté vigente).
4. Responder por la licitud, calidad y minimización de los Datos del Cliente que incorpore (incluido el tratamiento de datos personales de terceros).
5. No cargar datos especiales o sensibles sin base legal y, si aplica, anexo específico.
6. Pagar oportunamente los valores de la Orden.
7. Disponer de conectividad, equipos y navegadores compatibles.
8. Cooperar en la investigación de incidentes y en la exportación/eliminación al cierre.

---

## Capítulo VIII · Facturación

### 9. Precio y pago

1. El Cliente pagará los valores expresamente pactados en la Orden (mensualidad, add-ons, servicios profesionales).
2. **Impuestos, retenciones y facturación electrónica** se aplicarán según la situación jurídica y tributaria del Prestador `[PENDIENTE DE VALIDACIÓN CONTABLE]`.
3. Periodicidad por defecto: mensual anticipada, salvo pacto distinto.
4. La mora podrá dar lugar a suspensión proporcional del acceso, previo aviso cuando sea viable.
5. Los precios de referencia COM pueden actualizarse; los cambios aplican al Cliente según lo pactado en renovación o preaviso.

---

## Capítulo IX · Renovación

### 10. Vigencia y renovación

| Campo | Valor en Orden |
|-------|----------------|
| Fecha de inicio | ____ / ____ / ______ |
| Vigencia inicial | ________ meses |
| Renovación | ☐ Automática  ☐ Por acuerdo expreso |
| Preaviso de no renovación | ________ días calendario |

Si la renovación es automática, el plan y condiciones vigentes al momento de la renovación aplicarán salvo notificación en contrario dentro del preaviso.

---

## Capítulo X · Terminación

### 11. Terminación

El Contrato termina por:

1. Vencimiento sin renovación.
2. Mutuo acuerdo.
3. Incumplimiento material no subsanado en el plazo que se pacte (sugerido: 15 días calendario tras aviso escrito).
4. Mora reiterada o uso ilícito que haga inviable la continuidad.
5. Imposibilidad legal o fuerza mayor prolongada.

### 12. Efectos

Al terminar:

1. Se revocan los accesos.
2. El Cliente podrá exportar Datos del Cliente en el plazo de la Orden.
3. Se aplicará conservación residual y eliminación conforme a RTX-PRIV-001 / matriz de conservación y constancia de salida.
4. Sobreviven: confidencialidad, propiedad intelectual, obligaciones de datos, y cláusulas que por naturaleza deban sobrevivir.

---

## Capítulo XI · Confidencialidad

### 13. Confidencialidad

Cada parte protegerá la información no pública de la otra con medidas razonables, la usará solo para ejecutar este Contrato y no la divulgará salvo: (a) consentimiento; (b) obligación legal; (c) asesores bajo deber de confidencialidad. La obligación sobrevivirá mientras la información conserve carácter confidencial.

---

## Capítulo XII · Protección de datos

### 14. Protección de datos

1. Las partes cumplirán la Ley 1581 de 2012, Decreto 1074 de 2015 y normas complementarias, así como RTX-PRIV-001 y anexos.
2. Respecto de los datos cargados por el Cliente en el tenant, el Cliente actúa normalmente como **Responsable** y el Prestador como **Encargado**, salvo que la ley o el contexto indiquen otra cosa.
3. El Prestador podrá usar subencargados de infraestructura necesarios (lista en RTX-PRIV-ANX-001), manteniendo las obligaciones aplicables.
4. Un acuerdo de transmisión / encargo (DPA) podrá anexarse cuando el Cliente lo requiera.

---

## Capítulo XIII · Propiedad intelectual

### 15. Propiedad intelectual

1. La Plataforma, marca Roustix, código, documentación y materiales del Prestador permanecen en cabeza de sus titulares.
2. El Cliente conserva la propiedad de sus Datos del Cliente y contenidos.
3. El feedback genérico podrá usarse para mejorar el producto sin identificar al Cliente, salvo pacto en contrario.
4. Ninguna cláusula transfiere marcas, código fuente o documentación salvo licencia expresa por escrito.

---

## Capítulo XIV · Jurisdicción

### 16. Ley aplicable y controversias

| Campo | Estado |
|-------|--------|
| Ley aplicable | `[PENDIENTE · revisión jurídica · presumiblemente República de Colombia]` |
| Mecanismo | ☐ Negociación directa → ☐ Conciliación → ☐ Jurisdicción ordinaria / otro |
| Ciudad / autoridad | `[PENDIENTE]` |

Hasta completar este capítulo con asesoría jurídica, **no se firma** versión Vigente.

---

## Capítulo XV · Disposiciones generales

### 17. Suspensión

El Prestador podrá suspender el acceso de forma proporcional para: contener riesgos de seguridad, cumplir autoridad, atender uso ilícito, o mora pactada; procurando aviso y oportunidad de subsanar cuando sea viable.

### 18. Fuerza mayor

Ninguna parte responde por incumplimientos causados exclusivamente por eventos irresistibles e imprevisibles en los términos legales, siempre que mitigue y comunique oportunamente.

### 19. Documentos que integran el Contrato

En este orden de prevalencia ante conflicto (salvo norma imperativa):

1. Addenda firmadas posteriores  
2. Este Contrato (RTX-LEGAL-002)  
3. Orden / Acta de Servicio  
4. RTX-SLA-001 (si se anexa)  
5. RTX-PRIV-001 y anexos / DPA  
6. RTX-SUP-001  

### 20. Notificaciones

Las direcciones de la carátula (Capítulo I) son canales autorizados. Los cambios se notifican por medio verificable.

### 21. Integridad

Este Contrato y sus anexos constituyen el acuerdo completo sobre su objeto. Las modificaciones requieren forma verificable y aceptación de representantes autorizados.

### 22. Firmas

| Cliente | Prestador |
|---------|-----------|
| Nombre: | Nombre: |
| Cargo: | Cargo: |
| Fecha: | Fecha: |
| Firma: | Firma: |

---

## Anexo A · Checklist antes de firmar (interno)

| Tema | Decisión | Revisión |
|------|----------|----------|
| Identidad jurídica del Prestador | | Jurídica |
| Facturación e impuestos | | Contable / tributaria |
| Topes de responsabilidad y seguros | | Jurídica / comercial |
| Anexar o no RTX-SLA-001 | | Operación / comercial |
| Ley y controversias | | Jurídica |
| Conservación y eliminación | | Datos / jurídica |
| Correo corporativo de soporte | | Operación |

---

*RTX-LEGAL-002 · v0.1.0 · Borrador · 2026-08-03*

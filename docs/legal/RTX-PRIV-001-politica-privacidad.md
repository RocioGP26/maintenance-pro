# RTX-PRIV-001 · Política de Privacidad y Tratamiento de Datos

| Campo | Valor |
|-------|-------|
| **Código** | RTX-PRIV-001 |
| **Versión** | **0.2.0** |
| **Estado** | 🟡 Borrador · no publicar sin revisión jurídica |
| **Fecha** | 2026-08-03 |
| **Marco** | Constitución Política art. 15 · Ley 1581 de 2012 · Decreto 1074 de 2015 |
| **URL prevista** | `/privacidad` · publicada como borrador (`noindex`) |
| **Base piloto** | PIL-LEG-002 (Parte A · B · C) |
| **Anexos** | [ANX-001](anexos/RTX-PRIV-ANX-001-subencargados.md) · [ANX-002](anexos/RTX-PRIV-ANX-002-matriz-conservacion.md) · [ANX-003](anexos/RTX-PRIV-ANX-003-flujos-internacionales.md) |

> Completar identidad del Responsable, canal de titulares y anexos antes de publicar.  
> No versionar en Git datos personales de socios; usar placeholders hasta firma / almacenamiento privado.

---

# Parte A · Política de Tratamiento

## 1 · Responsable

| Campo | Valor |
|-------|-------|
| Nombre comercial | Roustix |
| Identidad jurídica | `[PENDIENTE · personas naturales operadoras o sociedad]` |
| Identificación / NIT | `[PENDIENTE]` |
| Domicilio | `[PENDIENTE]` |
| Sitio | [https://roustix.com](https://roustix.com) |
| Canal titulares | `[PENDIENTE]` · provisional operativo: `soporte.roustix@hotmail.com` |

Mientras no se constituya sociedad, los responsables serán las personas naturales operadoras identificadas en la versión firmada / publicada definitiva. Si se constituye la sociedad operadora, se actualizará esta sección.

---

## 2 · Alcance

Esta Política aplica a datos personales recolectados o tratados en:

- Registro y cuentas de la Plataforma  
- Uso del SaaS (módulos, auditoría, archivos)  
- Sitio público y formularios de contacto / demo  
- Soporte y comunicaciones operativas  
- Facturación y relación contractual  
- Programa piloto, cuando aplique  

**Rol dual:**

| Contexto | Rol típico de Roustix |
|----------|------------------------|
| Datos de cuentas, facturación, marketing propio, seguridad de la Plataforma | Responsable (o corresponsable, según el caso) |
| Datos que una empresa Cliente carga en su Tenant (empleados, técnicos, activos con datos de personas, etc.) | **Encargado**; el Cliente es normalmente el **Responsable** |

---

## 3 · Categorías de datos

Según el flujo, pueden tratarse:

| Categoría | Ejemplos |
|-----------|----------|
| Identificación y contacto | Nombre, correo, teléfono, documento |
| Laborales / organización | Cargo, área, empresa, sede |
| Autenticación y seguridad | Credenciales (hash), sesiones, IP, dispositivos, logs |
| Contractuales y soporte | Plan, tickets, comunicaciones de ayuda |
| Operativos del Tenant | Registros de mantenimiento, activos, inventarios, evidencias, fotos, informes |
| Facturación | Datos de pago / facturación del Cliente (según medio usado) |

No se solicita de forma ordinaria el tratamiento de datos sensibles o de niños, niñas y adolescentes. Si un Cliente necesita cargarlos, requiere base jurídica, evaluación de riesgos y, cuando corresponda, anexo específico.

---

## 4 · Finalidades

1. Crear, autenticar y proteger cuentas  
2. Prestar los módulos de la Plataforma  
3. Administrar permisos, roles y Tenants  
4. Enviar comunicaciones necesarias del servicio  
5. Atender soporte y ejercer / cooperar en derechos de titulares  
6. Respaldar, recuperar y asegurar continuidad  
7. Auditar, prevenir abuso y mejorar seguridad / rendimiento  
8. Cumplir obligaciones legales, regulatorias y contractuales  
9. Facturar y gestionar la relación comercial con el Cliente  
10. Comunicaciones comerciales **solo** con autorización separable (§5 y Parte C)

---

## 5 · Autorización

1. Cuando la autorización sea necesaria, será **previa, expresa e informada**.  
2. Se conservará evidencia de versión de política, fecha, identidad y medio.  
3. Las casillas electrónicas **no** estarán premarcadas.  
4. La autorización para marketing será **separable** de las finalidades esenciales del servicio.  
5. La negativa a finalidades no esenciales no impedirá el uso de funciones que no dependan de ellas.  
6. Respecto de datos del Tenant bajo encargo, el Cliente garantiza contar con la base jurídica frente a sus titulares.

---

## 6 · Derechos de los titulares

Conforme a la ley aplicable, el titular puede:

- Conocer, actualizar, rectificar y acceder a sus datos  
- Solicitar prueba de la autorización otorgada  
- Ser informado del uso que se ha dado a sus datos  
- Presentar consultas o reclamos  
- Revocar la autorización y/o solicitar la supresión cuando proceda  
- Acudir a la Superintendencia de Industria y Comercio (SIC) después del trámite aplicable ante el Responsable  

---

## 7 · Consultas, reclamos y canal

1. Se verificará la identidad del solicitante antes de revelar o modificar datos.  
2. **Consultas:** hasta **10 días hábiles**, prorrogables por **5**, conforme al régimen aplicable.  
3. **Reclamos:** hasta **15 días hábiles**, prorrogables por **8**, conforme al régimen aplicable.  
4. Canal: el indicado en §1 (titulares). Si el dato fue cargado por un Cliente en su Tenant, el titular puede dirigirse primero al Cliente como Responsable; Roustix cooperará como Encargado.

---

## 8 · Encargo (Cliente Responsable · Roustix Encargado)

Cuando Roustix trate datos por cuenta del Cliente:

1. Tratará solo conforme a instrucciones documentadas, configuración del Tenant y el contrato / DPA aplicable.  
2. No venderá datos ni determinará finalidades incompatibles.  
3. Cooperará en derechos, incidentes, exportación y eliminación.  
4. Usará subencargados según [RTX-PRIV-ANX-001](anexos/RTX-PRIV-ANX-001-subencargados.md).  
5. El detalle del encargo puede formalizarse en un Acuerdo de Transmisión (p. ej. base PIL-LEG-003) anexado al Contrato SaaS.

---

## 9 · Seguridad

Se aplican controles proporcionales, entre otros:

- Autenticación y control de acceso por roles  
- Aislamiento lógico entre Tenants  
- Cifrado en tránsito (HTTPS)  
- Protección de credenciales  
- Almacenamiento de objetos con controles de acceso  
- Auditoría y monitoreo  
- Respaldos y gestión de incidentes  

Ningún sistema es 100 % invulnerable; el Prestador mantiene un enfoque de mejora continua.

---

## 10 · Cookies y tecnologías similares

1. Se contemplan cookies / almacenamiento local **necesarios** para sesión, autenticación, seguridad y preferencias básicas.  
2. Analítica o publicidad no esencial requerirá evaluación previa y, cuando corresponda, consentimiento.  
3. El Usuario puede configurar su navegador; bloquear cookies esenciales puede impedir el uso de la Plataforma.

---

## 11 · Conservación

Los datos se conservan durante la relación y por los plazos necesarios para finalidades, obligaciones legales, seguridad, respaldo o defensa de derechos. Después se eliminan o anonimizan de forma segura.

**Detalle por categoría:** [RTX-PRIV-ANX-002 · Matriz de Conservación](anexos/RTX-PRIV-ANX-002-matriz-conservacion.md).

---

## 12 · Subencargados

Roustix puede apoyarse en proveedores de alojamiento, base de datos, almacenamiento, correo y observabilidad.

**Lista vigente:** [RTX-PRIV-ANX-001](anexos/RTX-PRIV-ANX-001-subencargados.md).

Los cambios relevantes se gestionarán conforme a la política / DPA y se informarán cuando corresponda.

---

## 13 · Flujos internacionales

Si hay transmisión o transferencia internacional de datos, se registra en:

[RTX-PRIV-ANX-003 · Registro de Flujos Internacionales](anexos/RTX-PRIV-ANX-003-flujos-internacionales.md).

---

## 14 · Vigencia y cambios

1. Esta versión **0.2.0** es borrador interno; la fecha de entrada en vigor se indicará al pasar a **Vigente**.  
2. Los cambios sustanciales se comunicarán por medio razonable.  
3. La versión aplicable constará en [RTX-DOC-000](RTX-DOC-000-control-versiones.md).

---

## 15 · Contacto titulares

| Campo | Valor |
|-------|-------|
| Correo | `[PENDIENTE]` |
| Provisional | `soporte.roustix@hotmail.com` |
| Autoridad de control | Superintendencia de Industria y Comercio (SIC) |

---

# Parte B · Aviso de Privacidad

*Texto corto para formularios (registro, contacto, demo).*

> Roustix tratará los datos suministrados para registrar y proteger la cuenta, prestar la plataforma, gestionar usuarios y permisos, enviar comunicaciones necesarias del servicio, brindar soporte, mantener seguridad y auditoría, y administrar la relación contractual. El titular puede ejercer sus derechos mediante el canal informado en la Política de Privacidad. La política completa estará disponible en: `/privacidad`.

Cuando se soliciten comunicaciones comerciales, se usará una casilla **separada y no premarcada**.

---

# Parte C · Autorización del titular

*Formato de evidencia (click-wrap, firma o equivalente).*

Declaro que recibí información clara sobre el Responsable, las finalidades, el carácter facultativo de respuestas sobre datos sensibles (cuando aplique), mis derechos y el canal para ejercerlos. Cuando la autorización sea necesaria, autorizo el tratamiento descrito en la versión de política identificada abajo.

| Campo | Valor |
|-------|-------|
| Titular | ______________________________ |
| Identificación | ______________________________ |
| Correo / contacto | ______________________________ |
| Finalidades aceptadas | ☐ Cuenta y servicio  ☐ Soporte  ☐ Seguridad  ☐ Comunicaciones comerciales (separada) |
| Versión de política y aviso | RTX-PRIV-001 v______ |
| Medio | ☐ Firma  ☐ Casilla electrónica no premarcada  ☐ Otro: ________ |
| Fecha, hora y evidencia | ______________________________ |

La autorización para comunicaciones comerciales es separable y revocable; su negativa no debe impedir funciones esenciales que no dependan de esa finalidad.

---

## Antes de publicar

- [ ] Identidad legal completa del Responsable  
- [ ] Canal definitivo de titulares  
- [ ] Anexos 001–003 diligenciados y revisados  
- [ ] Revisión jurídica colombiana  
- [x] Rutas públicas `/privacidad` y `/terminos` (borrador · `noindex`)  
- [x] Enlaces en footer (sustituye «Privacidad · próximamente»)  
- [ ] Quitar `noindex` y banner de borrador al pasar a **Vigente**

---

## Control de cambios

| Versión | Fecha | Cambio |
|---------|-------|--------|
| **0.1.0** | 2026-08-03 | Esqueleto LEG |
| **0.2.0** | 2026-08-03 | Consolidación PIL-LEG-002 · Partes A/B/C · remisión a anexos |

---

*RTX-PRIV-001 · v0.2.0 · Borrador · 2026-08-03*

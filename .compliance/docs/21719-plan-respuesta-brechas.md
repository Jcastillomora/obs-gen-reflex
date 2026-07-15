# Plan de Respuesta a Brechas de Datos Personales
## Universidad de La Frontera — OCDE Observatorio de Ciencia y Educación

**Empresa:** Universidad de La Frontera · **RUT:** 87.912.900-1
**Responsable del plan:** Jorge Castillo Mora — Gestor en Infraestructura Digital
**Contacto:** jorge.castillo@ufrontera.cl
**Fecha:** 2026-07-10 · **Revisión anual o ante incidentes**

> **Plazo legal (Art. 14 sexies, Ley 21.719):** Notificar a la Agencia de Protección de Datos **sin dilaciones indebidas** (la ley chilena NO fija 72 horas como GDPR; el estándar es "lo antes razonablemente posible"). Mantener además el **registro de vulneraciones** independientemente de si se notifican o no (ver docs/21719-registro-vulneraciones.md).

---

## Roles y responsabilidades

| Rol | Persona | Contacto |
|---|---|---|
| **Coordinador de incidente** | Jorge Castillo Mora | jorge.castillo@ufrontera.cl |
| **Equipo técnico** | Jorge Castillo Mora (responsable técnico del sistema) | jorge.castillo@ufrontera.cl |
| **Contacto de datos** | genero.ciencia@ufrontera.cl | genero.ciencia@ufrontera.cl |
| **Apoyo legal** | Asesoría jurídica UFRO | [COMPLETAR: correo/teléfono de la Dirección Jurídica UFRO] |
| **Comunicaciones** | [COMPLETAR: área de comunicaciones UFRO si aplica] | [COMPLETAR] |

---

## Clasificación de brechas en este sistema

Los activos con datos personales son:
1. **Archivos Excel** en el servidor: `academicas.xlsx`, `publicaciones_total.xlsx`, `proyectos_total.xlsx` (contienen RUT, nombre, email, grado, proyectos, publicaciones de investigadoras UFRO).
2. **Base de datos SQLite** (`data/ocde.db`): tabla `documento` (metadatos de PDFs del repositorio; no contiene datos de investigadoras directamente).
3. **API Anthropic:** consultas de visitantes en texto libre (no persistidas localmente).
4. **Clerk:** sesiones de los 2 administradores.
5. **Assets/uploads/**: PDFs del repositorio institucional.

---

## Fase 1 — Detección y contención (0–4 horas)

1. **Registrar inmediatamente:**
   - Fecha y hora exacta de detección.
   - Quién detecta y cómo (log, alerta, reporte externo, etc.).
   - Sistema o componente involucrado.

2. **Contención:**
   - Si es compromiso del servidor: aislar el servidor (desconectar de red si es necesario).
   - Si son credenciales comprometidas (ANTHROPIC_API_KEY, CLERK_SECRET_KEY): revocarlas y regenerarlas inmediatamente en los respectivos portales.
   - Si es la base de datos: revocar accesos de BD y evaluar restaurar desde backup.
   - Si es el panel admin (Clerk): suspender las sesiones activas en el dashboard de Clerk.

3. **Abrir bitácora del incidente:** correo o documento con timestamp de cada acción.

4. **Avisar al Coordinador de incidente** si quien detecta no es él mismo.

---

## Fase 2 — Evaluación (4–24 horas)

1. **Alcance:**
   - ¿Qué datos fueron afectados? (RUT, nombre, email de investigadoras; datos de visitantes; credenciales de admin).
   - ¿Cuántos titulares están afectados? (número aproximado de investigadoras en la BD o archivos Excel).
   - ¿Cuál es la naturaleza de la brecha? (destrucción, pérdida, alteración, acceso no autorizado, divulgación).

2. **Evaluación de riesgo para los titulares:**
   - **Riesgo alto:** El RUT de investigadoras está expuesto → notificación a la Agencia y a las titulares.
   - **Riesgo alto:** Datos de menores (no aplica actualmente en este sistema).
   - **Riesgo alto:** Datos financieros o bancarios (no aplica actualmente en este sistema).
   - **Riesgo bajo:** Solo metadatos de documentos (sin datos personales sensibles) → notificar a Agencia sin aviso a titulares.
   - Los datos de visitantes (consultas IA, chats) no se almacenan → riesgo bajo en ese componente.

3. **Si hay proveedor involucrado** (Anthropic, Clerk, Google, Microsoft): contactarlos para obtener su informe de incidente y qué datos específicos afectó.

---

## Fase 3 — Notificación (sin dilaciones indebidas)

### 3.1 A la Agencia de Protección de Datos Personales

**Cuándo:** Sin dilaciones indebidas desde que se tiene la evaluación (Fase 2). No esperar a tener toda la información; se puede notificar por etapas y complementar.

**Qué informar:**
- Naturaleza de la brecha (acceso, fuga, pérdida, etc.)
- Categorías y volumen aproximado de datos y titulares afectados
- Posibles consecuencias para los titulares
- Medidas adoptadas o en curso para contener y remediar
- Datos de contacto del responsable: Jorge Castillo Mora, jorge.castillo@ufrontera.cl

**Canal:** Portal de la Agencia de Protección de Datos Personales de Chile (cuando esté disponible) o por correo al organismo regulador correspondiente mientras la Agencia no esté operativa.

### 3.2 A los titulares afectados

**Cuándo notificar a titulares (Art. 14 sexies):** Si hay **riesgo alto** para sus derechos e intereses, o si los datos afectados incluyen datos sensibles, datos económicos/financieros/bancarios, o datos de niños/niñas/adolescentes.

**En este sistema:** Si el RUT de las investigadoras está expuesto → riesgo alto → notificar a las investigadoras afectadas por correo o medio oficial de UFRO.

**Plantilla de aviso a titulares:**

> Estimada [Nombre]:
>
> El [FECHA] detectamos un incidente de seguridad en el Observatorio de Ciencia y Educación de la Universidad de La Frontera que puede haber afectado sus datos personales.
>
> **Qué pasó:** [DESCRIPCIÓN BREVE, ej. "acceso no autorizado a los archivos de datos del sistema"].
>
> **Datos potencialmente afectados:** [CATEGORÍAS, ej. "nombre, RUT, grado académico y datos de proyectos"].
>
> **Medidas adoptadas:** [ej. "hemos aislado el sistema, regenerado las credenciales y reforzado los controles de acceso"].
>
> **Qué puede hacer usted:** [ej. "Le recomendamos estar atenta a cualquier uso indebido de su información; puede contactarnos si tiene consultas"].
>
> Para consultas: jorge.castillo@ufrontera.cl
>
> Universidad de La Frontera

---

## Fase 4 — Cierre y mejora

1. **Causa raíz:** documentar qué falló (ej. secreto expuesto, falta de cifrado, configuración incorrecta).
2. **Medidas correctivas:** implementar los controles faltantes identificados en la auditoría de compliance (ver .compliance/state.json y RESUMEN.md).
3. **Actualizar:**
   - El registro de vulneraciones (docs/21719-registro-vulneraciones.md).
   - El RAT si el incidente revela flujos no documentados.
   - Este plan si el procedimiento requiere ajustes.
4. **Comunicar internamente** a la Dirección de UFRO y, si aplica, a la comunidad de investigadoras.

---

*Borrador generado con compliance-cl (pack ley-21719). No constituye asesoría legal; revisar con un abogado.*

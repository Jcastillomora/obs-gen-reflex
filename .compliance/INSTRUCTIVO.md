# Instructivo de Situaciones — OCDE / Universidad de La Frontera

**Sistema:** OCDE — Observatorio de Ciencia y Educación
**Responsable:** Jorge Castillo Mora — jorge.castillo@ufrontera.cl
**Fecha:** 2026-07-10

---

## 1. Alguien pide ejercer sus derechos (ARCO)

**Canal:** jorge.castillo@ufrontera.cl (o arco@ufrontera.cl si lo creas)

**Pasos:**
1. Recibir solicitud → anotar en hoja de seguimiento: titular, derecho solicitado, fecha.
2. Verificar identidad (RUT o correo institucional).
3. Responder dentro de **30 días corridos** (prorrogable una sola vez por 30 días más con aviso).
4. Ejecutar: acceso → entregar datos en CSV; rectificación → corregir en Excel y recargar DataCache; supresión → eliminar de Excel; oposición → evaluar base legal para continuar.
5. Guardar evidencia del correo de respuesta.

**Ver detalle:** docs/21719-canal-derechos.md

---

## 2. Se detecta una brecha de seguridad

**Primer respondiente:** Jorge Castillo Mora

**Pasos inmediatos (0-4h):**
1. Registrar: qué pasó, cuándo, quién detectó.
2. Contener: revocar credenciales comprometidas, aislar sistema si es necesario.
3. Abrir bitácora del incidente.

**Pasos siguientes (4-24h):**
1. Evaluar alcance: qué datos, cuántos titulares, tipo de brecha.
2. Si hay riesgo alto (RUT expuesto, datos sensibles, menores): notificar a la Agencia sin dilaciones y a las titulares afectadas.

**Notificar siempre:** Registrar en docs/21719-registro-vulneraciones.md aunque no se notifique a la Agencia.

**Ver detalle:** docs/21719-plan-respuesta-brechas.md

---

## 3. Llega una notificación de fiscalización de la Agencia

1. **No responder sin coordinar** con la Dirección Jurídica de UFRO.
2. Reunir evidencia: este directorio `.compliance/`, el RAT, los DPA firmados, logs del sistema.
3. Contactar abogado externo especializado en datos personales.
4. El plazo para responder lo indica la Agencia en la notificación.

---

## 4. Ingresa un nuevo proveedor tecnológico

Antes de integrar cualquier proveedor que procese datos personales:
1. Identificar qué datos recibirá y si está en Chile o en el extranjero.
2. Si está fuera de Chile: firmar DPA + Cláusulas Contractuales Modelo antes de activar en producción.
3. Actualizar el RAT (docs/21719-rat.md) con el nuevo proveedor.
4. Actualizar el anexo de transferencias si es internacional (docs/21719-anexo-transferencias.md).

---

## 5. Una investigadora sale de UFRO

1. Aplicar la política de retención: conservar sus datos 1 año adicional desde la fecha de cese.
2. Al cumplirse el año: anonimizar o eliminar del directorio, los Excel y la BD.
3. Si la investigadora solicita supresión antes del año: evaluar si existe obligación legal de conservar (registros históricos de investigación); si no, eliminar.

---

## 6. Re-correr la auditoría de compliance

Para re-evaluar el estado de compliance (detectar drift o verificar avances):
- Volver a invocar el skill `/compliance-cl` en este mismo repo.
- La skill leerá el `state.json` existente y comparará contra la nueva evaluación.
- Commitear los cambios: `git add .compliance && git commit -m "compliance: snapshot YYYY-MM-DD"`

**Periodicidad recomendada:** Anual, o ante cambios significativos de infraestructura o proveedores.

---

## 7. Calendario regulatorio clave

| Fecha | Hito |
|---|---|
| **1-dic-2026** | Vigencia Ley 21.719. Todos los controles deben estar implementados. |
| **1-dic-2027** | Fin del período de gracia MIPYME (no aplica a UFRO — es grande). |
| **Anual** | Revisar y actualizar el RAT. |
| **Anual** | Re-correr auditoría de compliance (este instructivo, paso 6). |
| **Anual** | Revisar DPAs con proveedores (¿siguen vigentes? ¿cambiaron términos?). |

---

*Generado con compliance-cl · 2026-07-10*
*No constituye asesoría legal.*

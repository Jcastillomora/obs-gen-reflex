# Resumen de Postura de Compliance — Ley 21.719
## Universidad de La Frontera · OCDE Observatorio de Ciencia y Educación

**Corrida:** 2026-07-10 · Commit: `8359f28` · Primera evaluación (sin baseline anterior)
**Responsable:** Jorge Castillo Mora — jorge.castillo@ufrontera.cl
**Pack activo:** ley-21719 (vigencia 1-dic-2026)

---

## Postura global

```
Ley 21.719 — Score: 30% (7/23 puntos)

██░░░░░░░░░░░░░░░░░░  30%

✅ Cumple  (4):  gov-responsable, sec-tls, sec-passwords, sec-tenant
⚠️ Parcial (6):  gov-denuncias, data-licitud, data-minimizacion, data-eipd,
                 data-privacy-by-design, sec-backups
❌ Falta   (12): gov-registro, gov-politicas, data-consent-text, data-derechos,
                 data-info, data-dpa, data-transfer, data-pseudonym,
                 sec-rest, sec-logs, sec-secrets, inc-brechas
❓ Incierto (1): sec-mfa (verificar en dashboard Clerk)
```

---

## Brechas críticas (actuar antes del 1-dic-2026)

### 🔴 CRÍTICO — Secreto expuesto

**`sec-secrets`** — El archivo `.env` contiene `ANTHROPIC_API_KEY` real en disco. Aunque `.gitignore` lo lista, verificar si fue commiteado alguna vez.

```bash
# Verificar si .env fue commiteado
git log --all --full-history -- .env
```

**Acción inmediata:**
1. Regenerar la API key en https://console.anthropic.com
2. Regenerar CLERK_SECRET_KEY en el dashboard de Clerk si también fue expuesta
3. Actualizar el `.env` local y las variables de entorno de producción

---

### 🔴 CRÍTICO — Transferencias internacionales sin amparo legal

**`data-transfer`** — Los datos se envían a 4 proveedores en EE.UU. (Anthropic, Clerk, Google, Microsoft) sin Cláusulas Contractuales Modelo suscritas.

**Acción requerida antes del 1-dic-2026:**
- [ ] Suscribir/aceptar DPA con Anthropic (ver docs/21719-dpa.md)
- [ ] Suscribir/aceptar DPA con Clerk (ver docs/21719-dpa.md)
- [ ] Verificar DPA de Google Workspace institucional UFRO (ver docs/21719-dpa.md)
- [ ] Verificar Microsoft DPA para la licencia institucional UFRO (ver docs/21719-dpa.md)

---

### 🔴 ALTO — Sin documentación de privacidad publicada

**`gov-politicas` + `data-info` + `data-consent-text`** — No existe política de privacidad, aviso de privacidad ni texto de consentimiento en el sitio.

**Acción:**
- [ ] Publicar `docs/21719-politica-privacidad.md` como página del sitio (ruta `/privacidad`)
- [ ] Agregar enlace en el footer de todas las páginas
- [ ] Agregar aviso antes del iframe de Google Forms (ver docs/21719-consentimiento.md)

---

### 🔴 ALTO — Sin canal ARCO ni procedimiento de derechos

**`data-derechos`** — No hay canal explícito para que los titulares ejerzan sus derechos (acceso, rectificación, supresión, oposición, portabilidad, bloqueo).

**Acción:**
- [ ] Habilitar `jorge.castillo@ufrontera.cl` como canal oficial de derechos (o crear `arco@ufrontera.cl`)
- [ ] Publicar el procedimiento en la política de privacidad
- [ ] Implementar el procedimiento interno de docs/21719-canal-derechos.md

---

### 🔴 ALTO — Sin auditoría ni logs de acceso a datos

**`sec-logs`** — Solo hay logging básico a stdout. No existe registro de quién accedió a qué dato, cuándo, ni qué cambios realizó el admin.

**Acción:** Implementar tabla `audit_log` en la BD con campos: `user_email`, `action`, `resource`, `timestamp`, `ip_address`.

---

### 🟠 MEDIO — Base de datos y Excel sin cifrar

**`sec-rest`** — SQLite (`data/ocde.db`) en texto plano. Los Excel con RUT de investigadoras en disco sin cifrar.

**Acción:**
- Opción A: Cifrar SQLite con sqlcipher
- Opción B: Migrar a PostgreSQL con cifrado de columnas
- Excel: mover a almacenamiento seguro fuera del directorio de la aplicación, o cifrar con herramienta de cifrado de archivos

---

### 🟠 MEDIO — Sin Registro de Actividades de Tratamiento formal

**`gov-registro`** — El RAT es nuevo (generado ahora). Debe mantenerse actualizado.

**Acción:** El RAT en docs/21719-rat.md está completo; completar los campos marcados con `[COMPLETAR]` y firmarlo formalmente.

---

### 🟠 MEDIO — DPO no designado formalmente

**Nota adicional:** UFRO es organismo público → DPO obligatorio (Art. 50, Ley 21.719). Jorge Castillo Mora puede asumir este rol con designación formal.

**Acción:** Emitir Resolución de la Rectoría designando a Jorge Castillo Mora como Delegado de Protección de Datos (DPO) del sistema OCDE.

---

### 🟡 BAJO — RUT sin seudonimizar

**`data-pseudonym`** — El RUT se usa como clave de vinculación interna pero podría reemplazarse por un ID anónimo.

**Acción (largo plazo):** Generar un `investigador_id` interno y usar el RUT solo en una tabla de correspondencia cifrada.

---

## Cambios vs última corrida

*Primera corrida — sin baseline anterior.*

---

## Plan de acción por fecha

### Inmediato (esta semana)
- [ ] Verificar historial git del .env y regenerar ANTHROPIC_API_KEY
- [ ] Habilitar canal ARCO en jorge.castillo@ufrontera.cl
- [ ] Completar campos `[COMPLETAR]` en el RAT (número de investigadoras, contacto jurídico UFRO)

### Antes del 1-dic-2026 (crítico para compliance)
- [ ] Publicar política de privacidad en el sitio
- [ ] Suscribir DPA con Anthropic
- [ ] Aceptar DPA de Clerk (dashboard)
- [ ] Verificar DPA Google Workspace UFRO
- [ ] Habilitar MFA obligatorio en Clerk para los 2 admins
- [ ] Emitir Resolución de Rectoría para base legal del directorio y designación de DPO

### 1-3 meses
- [ ] Implementar audit log en la BD
- [ ] Cifrar en reposo (SQLite o PostgreSQL)
- [ ] Agregar aviso de privacidad al footer del sitio (1 línea de código Reflex)

### 3-6 meses
- [ ] Seudonimizar RUT → ID interno
- [ ] Servir Google Fonts localmente (eliminar transferencia de IP a Google)
- [ ] Definir política formal de retención y backups

---

## Único insumo externo no self-service

La **supervisión externa del Modelo de Prevención de Infracciones (MPI)** por la Agencia (Arts. 49-53, Ley 21.719) es voluntaria y la realiza la propia Agencia. Si UFRO decide certificar su MPI ante la Agencia, ese proceso requiere un auditor externo acreditado.

---

*Generado con compliance-cl · 2026-07-10 · Commit 8359f28*
*No constituye asesoría legal.*

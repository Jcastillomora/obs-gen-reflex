# Anexo de Transferencia Internacional de Datos — Universidad de La Frontera

**Sistema:** OCDE — Observatorio de Ciencia y Educación
**RUT:** 87.912.900-1
**Fecha:** 2026-07-10

> Mecanismo de transferencia: **Cláusulas Contractuales Modelo** aprobadas por el Ministerio de Economía de Chile (Resolución RAEX202503748, Diario Oficial 19-12-2025), conforme al Art. 28 de la Ley 21.719.
>
> **Nota:** Las Cláusulas Contractuales Modelo deben incorporarse íntegramente en el contrato con cada proveedor o anexarse por referencia. El texto oficial está disponible en el Diario Oficial y debe adjuntarse a cada DPA (ver docs/21719-dpa.md).

---

## Transferencia 1 — Anthropic, Inc. (EE.UU.)

**Exportador de datos:** Universidad de La Frontera, RUT 87.912.900-1, Av Francisco Salazar 01145, Temuco, Chile.
**Importador de datos:** Anthropic, Inc., San Francisco, California, EE.UU.

**Categorías de datos:** Texto libre de consultas de búsqueda y preguntas al chatbot ingresadas por visitantes del Observatorio OCDE (puede incluir datos personales si el visitante los incluye espontáneamente).
**Finalidad:** Procesamiento de lenguaje natural para la función de búsqueda semántica y chatbot de documentos.
**Frecuencia:** Continua (cada consulta de usuario en tiempo real).
**País destino:** Estados Unidos de América.
**Mecanismo de garantía:** Cláusulas Contractuales Modelo del Ministerio de Economía (pendiente de suscripción formal con Anthropic).

**Compromisos del importador (Anthropic):**
- Tratar los datos solo según instrucciones de la Universidad.
- Aplicar medidas de seguridad equivalentes a las exigidas por la Ley 21.719 (TLS, control de acceso, cifrado en reposo).
- No transferir a terceros sin garantías equivalentes.
- Colaborar ante solicitudes de los titulares y de la Agencia de Protección de Datos de Chile.
- Notificar brechas sin dilación.

---

## Transferencia 2 — Clerk, Inc. (EE.UU.)

**Exportador de datos:** Universidad de La Frontera, RUT 87.912.900-1, Chile.
**Importador de datos:** Clerk, Inc., EE.UU.

**Categorías de datos:** Correo electrónico institucional y tokens JWT de los 2 administradores autorizados del sistema.
**Finalidad:** Autenticación OAuth para el acceso al panel de administración del Observatorio.
**Frecuencia:** Cada inicio de sesión de los administradores.
**País destino:** Estados Unidos de América.
**Mecanismo de garantía:** Cláusulas Contractuales Modelo (pendiente de suscripción formal con Clerk).

---

## Transferencia 3 — Google LLC (EE.UU.)

**Exportador de datos:** Universidad de La Frontera, RUT 87.912.900-1, Chile.
**Importador de datos:** Google LLC, Mountain View, California, EE.UU.

**Categorías de datos:**
- Datos ingresados por visitantes en los formularios de contacto (nombre, correo, mensaje u otros campos).
- Dirección IP y datos técnicos de navegación al cargar Google Fonts (si se sigue usando CDN externo).

**Finalidad:** Gestión del formulario de contacto del Observatorio; tipografía del sitio web.
**Frecuencia:** Continua (cada visita al formulario; cada carga del sitio para fuentes).
**País destino:** Estados Unidos de América.
**Mecanismo de garantía:** DPA de Google Workspace (verificar si está vigente para la cuenta institucional UFRO) + Cláusulas Contractuales Modelo de Google.

**Medida de mitigación recomendada (Google Fonts):** Servir las fuentes localmente desde `/assets/` para eliminar esta transferencia. Esto es mejor práctica de privacy by design y elimina la necesidad de incluir Google Fonts en este anexo.

---

## Transferencia 4 — Microsoft Corporation (EE.UU.)

**Exportador de datos:** Universidad de La Frontera, RUT 87.912.900-1, Chile.
**Importador de datos:** Microsoft Corporation, Redmond, Washington, EE.UU.

**Categorías de datos:** Datos técnicos de navegación (posibles cookies de sesión de Power BI, IP del visitante al cargar el iframe).
**Finalidad:** Visualización de dashboards de indicadores de investigación mediante Power BI embebido.
**Frecuencia:** Cada visita a la sección `/obs_indicadores`.
**País destino:** Estados Unidos de América.
**Mecanismo de garantía:** Microsoft Products and Services Data Protection Addendum (verificar si está vigente para la licencia institucional UFRO).

---

## Declaración general

Esta transferencia se declara en la **Política de Privacidad** del Observatorio OCDE (docs/21719-politica-privacidad.md), sección "Con quién compartimos los datos".

Las Cláusulas Contractuales Modelo del Ministerio de Economía deben incorporarse en los contratos con cada proveedor antes del 1 de diciembre de 2026 (fecha de vigencia de la Ley 21.719).

---

*Borrador generado con compliance-cl (pack ley-21719). No constituye asesoría legal; revisar con un abogado antes de firmar.*

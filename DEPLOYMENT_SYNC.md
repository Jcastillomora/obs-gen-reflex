# Instrucciones de Deployment - Sincronización de Publicaciones

Este documento describe cómo desplegar los cambios para habilitar la sincronización semanal de publicaciones en producción (Docker).

## Cambios Realizados

1. ✅ **compose.yaml**: Modificado para permitir escritura en `publicaciones_total.xlsx` y montar `.last_sync.json`
2. ✅ **scripts/docker_sync.sh**: Script helper para ejecutar sync dentro del contenedor (Linux/Ubuntu)
3. ✅ **scripts/docker_sync.bat**: Script helper para ejecutar sync dentro del contenedor (Windows)
4. ✅ **scripts/setup_cron_docker.sh**: Script para configurar cron automáticamente en producción
5. ✅ **CLAUDE.md**: Documentación actualizada con instrucciones de Docker

## Pasos para Desplegar en Producción

### 1. Hacer commit y push de los cambios

```bash
# En tu máquina local (Windows)
git add compose.yaml scripts/docker_sync.sh scripts/docker_sync.bat scripts/setup_cron_docker.sh CLAUDE.md DEPLOYMENT_SYNC.md
git commit -m "agregar soporte para sync de publicaciones en Docker

- Modificar compose.yaml para permitir escritura en publicaciones_total.xlsx
- Montar OCDE/.last_sync.json para persistir fecha de último sync
- Agregar scripts helper para ejecutar sync en contenedor Docker
- Documentar configuración en CLAUDE.md"
git push
```

### 2. Conectar al servidor de producción

```bash
ssh admobge@srv-obsgenero
```

### 3. Actualizar el código

El GitHub Actions runner debería desplegar automáticamente. Si no está activo, ejecutar manualmente:

```bash
cd ~/obs-gen-reflex
git pull origin main
```

### 4. Crear el archivo .last_sync.json (primera vez)

```bash
# Crear archivo vacío para que Docker pueda montarlo
touch ~/obs-gen-reflex/OCDE/.last_sync.json
```

### 5. Reiniciar los contenedores con la nueva configuración

```bash
cd ~/obs-gen-reflex
docker compose down
docker compose up -d
```

Verificar que los contenedores estén corriendo:

```bash
docker compose ps
```

### 6. Ejecutar el sync por primera vez (IMPORTANTE)

Esto generará el archivo `.last_sync.json` con la fecha actual:

```bash
cd ~/obs-gen-reflex

# Primero, prueba en modo dry-run
bash scripts/docker_sync.sh --dry-run

# Si todo se ve bien, ejecutar el sync real
bash scripts/docker_sync.sh
```

**Tiempo estimado**: 5-15 minutos dependiendo del número de investigadoras.

### 7. Verificar que se creó el archivo .last_sync.json

```bash
cat ~/obs-gen-reflex/OCDE/.last_sync.json
```

Deberías ver algo como:

```json
{
  "last_sync": "2024-11-06T18:30:00",
  "publicaciones_nuevas": 0
}
```

### 8. Verificar la página web

Visita: https://observatoriogeneroyciencia.ufro.cl/investigadoras

Deberías ver en la parte superior:

```
Última actualización de publicaciones: 06/11/2024 18:30
```

### 9. Configurar el cron para sync automático semanal

```bash
cd ~/obs-gen-reflex
bash scripts/setup_cron_docker.sh
```

Esto configurará el cron para ejecutar el sync **cada viernes a las 2:00 AM**.

Verificar que el cron se configuró correctamente:

```bash
crontab -l | grep sync_publicaciones
```

Deberías ver:

```
0 2 * * 5 cd /home/admobge/obs-gen-reflex && docker compose exec -T app python scripts/sync_publicaciones_to_db.py >> /var/log/ocde_sync.log 2>&1
```

### 10. Monitorear logs del cron (opcional)

Para ver los logs del sync:

```bash
# Ver logs en tiempo real
tail -f /var/log/ocde_sync.log

# Ver últimas 50 líneas
tail -n 50 /var/log/ocde_sync.log
```

## Troubleshooting

### El archivo .last_sync.json no se crea

**Problema**: El script se ejecuta pero no genera el archivo.

**Solución**:
```bash
# Verificar que el archivo existe en el host
ls -la ~/obs-gen-reflex/OCDE/.last_sync.json

# Si no existe, crearlo
touch ~/obs-gen-reflex/OCDE/.last_sync.json

# Darle permisos de escritura
chmod 666 ~/obs-gen-reflex/OCDE/.last_sync.json

# Ejecutar el sync nuevamente
bash scripts/docker_sync.sh
```

### No se puede escribir en publicaciones_total.xlsx

**Problema**: Error "Permission denied" al intentar modificar `publicaciones_total.xlsx`.

**Solución**:
```bash
# Verificar permisos
ls -la ~/obs-gen-reflex/publicaciones_total.xlsx

# Darle permisos de escritura
chmod 666 ~/obs-gen-reflex/publicaciones_total.xlsx

# Ejecutar el sync nuevamente
bash scripts/docker_sync.sh
```

### El cron no se ejecuta

**Problema**: El viernes pasó y el sync no se ejecutó.

**Solución**:
```bash
# Verificar que el cron está configurado
crontab -l | grep sync_publicaciones

# Verificar logs del sistema (errores de cron)
grep CRON /var/log/syslog | grep sync_publicaciones

# Ejecutar manualmente para verificar que funciona
cd ~/obs-gen-reflex && docker compose exec -T app python scripts/sync_publicaciones_to_db.py
```

### La página no muestra la fecha de actualización

**Problema**: La página `/investigadoras` no muestra el mensaje de última actualización.

**Solución**:
```bash
# Verificar que el archivo .last_sync.json existe y tiene contenido
cat ~/obs-gen-reflex/OCDE/.last_sync.json

# Verificar que el contenedor está montando el archivo correctamente
docker compose exec app cat /app/OCDE/.last_sync.json

# Si el archivo está vacío o no existe dentro del contenedor, reiniciar:
docker compose restart app
```

## Comandos Útiles

```bash
# Ejecutar sync manualmente
cd ~/obs-gen-reflex
bash scripts/docker_sync.sh

# Ejecutar sync en modo dry-run (sin modificar archivos)
bash scripts/docker_sync.sh --dry-run

# Ver logs del último sync
tail -f /var/log/ocde_sync.log

# Ver contenido del .last_sync.json
cat ~/obs-gen-reflex/OCDE/.last_sync.json

# Reiniciar el contenedor de la app
docker compose restart app

# Ver logs del contenedor
docker compose logs app -f
```

## Verificación Final

1. ✅ El archivo `.last_sync.json` existe en el servidor
2. ✅ La página web muestra la fecha de última actualización
3. ✅ El cron está configurado (`crontab -l`)
4. ✅ El script se ejecuta correctamente con `bash scripts/docker_sync.sh`
5. ✅ Los logs del cron están funcionando (`/var/log/ocde_sync.log`)

## Próximos Pasos (Opcional)

- Implementar notificaciones por email cuando el sync falla
- Implementar recarga de `DataCache` sin reiniciar la app
- Agregar métricas de monitoreo del sync (Prometheus/Grafana)

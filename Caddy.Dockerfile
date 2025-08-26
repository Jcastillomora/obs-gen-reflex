FROM caddy:latest

COPY --from=local/reflex-app /app/.web/build/client /srv
ADD Caddyfile /etc/caddy/Caddyfile
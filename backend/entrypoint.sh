#!/bin/sh
set -e

# Si existe manage.py, ejecutar migraciones y collectstatic
if [ -f "./manage.py" ]; then
echo "manage.py encontrado: ejecutando migrate y collectstatic"
python manage.py migrate --noinput || true
python manage.py collectstatic --noinput --clear || true
else
echo "manage.py no encontrado: se omiten migrate y collectstatic"
fi

# Ejecutar el comando pasado al contenedor
exec "$@"
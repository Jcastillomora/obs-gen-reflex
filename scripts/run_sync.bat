@echo off
cd /d "C:\Users\Ufro\OneDrive\Escritorio\OCDE"
call env\Scripts\activate
python scripts\sync_publicaciones.py >> scripts\sync.log 2>&1

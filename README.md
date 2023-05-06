# Schnällschte Jegenstorfer :runner:

### Sprintwettkampf über 60m  
- 3 Vorläufe pro TeilnehmerIn  
- Die besten 4 pro Kategorie kommen in den Final  

### ToDo
- [ ] Testen des Druckers: TM-T88II

## Drucker
Getestet mit:  
 - EPSON TM-T20II

## Installation
- Getestet mit Python 3.10.6

Python virtual enviroment erstellen
```bash
sudo apt install python3.10-venv
python3 -m venv env
```

Python virtual enviroment aktivieren
```bash
cd env
soure bin activate
```

Django installieren [Offizielle Webseite] (https://docs.djangoproject.com/en/4.2/topics/install/#installing-official-release)
```bash
pip install --upgrade pip
python -m pip install Django
```

Git clonen
```bash
git clone git@github.com:fPBunxGKv/sj-github.git
```

*requirements.txt installieren*
```bash
pip install -r sj-github/requirements.txt
```

DB migrations durchführen
 - erstellt die DB db.sqlite3 mit allen benötigten Tabellen
```bash
cd sj-github
python manage.py migrate
```

Admin User erstellen
```bash
python manage.py createsuperuser
```

Django test Server starten
```bash
python manage.py runserver
```

Einloggen und ein Event erstellen
http://localhost:8000/admin/

Ausloggen
- jetzt solltest du auf der "Homepage" vom SJ sein.
- einloggen mit dem erstellten Admin user
---
# Notizen
### Port 8000 Proxy
Um mit FQDN auf WSL zuzugreifen
```bash
ssh -fN -R 8000:localhost:8000 $(hostname).local
```

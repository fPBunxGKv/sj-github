# Schnällschte Jegenstorfer :runner:

### Sprintwettkampf über 60m  
- 3 Vorläufe pro TeilnehmerIn  
- Die besten 4 pro Kategorie kommen in den Final  

### ToDo
[ToDo.md](ToDo.md)

### Ideen
[ideas.md](ideas.md)

## Installation mit Docker
Ubuntu 24.04.3 LTS

Docker installieren (via snap)
```bash
sudo snap install docker
```

Verzeichnis erstellen
```bash
mkdir projects
cd projects
```
Proxynetzwerk erstellen
```bash
sudo docker network create --subnet=172.20.60.0/24 -d=bridge proxynet
```
Volume erstellen
```bash
sudo docker volume create static_sj_prd
```
Nginx Proxy Manager installieren
https://nginxproxymanager.com/setup/

docker-compose.yml vom Proxy Manager erweitern
```bash
    volumes:
      ...
      - static_sj_prd:/static_sj_prd

    networks:
      - proxynet


volumes:
  static_sj_prd:
    external: true

networks:
  proxynet:
    name: proxynet
    external: true
```


Falls das Repo nicht public ist, ssh-keygen und den public-key im Repo einpflegen.
Repo clonen
```bash
git clone git@github.com:fPBunxGKv/sj-github.git
```
.env Datei erstellen/anpassen

```bash
cp example.env.prd .env
vi .env
```
Datenverzeichnis erstellen
```bash
projects/
├── data
│   └── sj_prd
└── sj-github
...
```

Dockercontainer starten
```bash
sudo docker compose -f docker-compose-prd.yml up --build --force-recreate
```


## Installation
- Getestet mit Python 3.10.6

Python virtual enviroment erstellen
```bash
sudo apt install python3.10-venv
python3 -m venv env
```

Python virtual enviroment aktivieren
```bash
source env/bin/activate
```

Django installieren [Offizielle Webseite] (https://docs.djangoproject.com/en/4.2/topics/install/#installing-official-release)
```bash
pip install --upgrade pip
python -m pip install Django==4.2

-- ODER --

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

Initialer Event in die DB laden
```bash
python manage.py loaddata sj_events.json
```

Dummy Teilnehmer in die DB laden
```bash
python manage.py loaddata sj_users_demo.json 
```

Django test Server starten
```bash
python manage.py runserver
```

http://localhost:8000/

- jetzt solltest du auf der "Homepage" vom SJ sein.
- einloggen mit dem erstellten Admin user
---
# Notizen
### Port 8000 Proxy
Um mit FQDN auf WSL zuzugreifen
```bash
ssh -fN -R 8000:localhost:8000 $(hostname).local
```

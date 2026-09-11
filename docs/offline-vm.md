# Setup guide for the SJ project

This document explains how to install and run this repository on an Ubuntu server. It is written for a normal IT person who wants a clear step-by-step setup without guessing missing details.

This project is a Django web application. The recommended production setup is:

- Ubuntu server
- Docker and Docker Compose
- Nginx Proxy Manager as reverse proxy
- A Docker bridge network called `proxynet`
- A Docker volume called `static_sj_prd`
- The application runs as Docker containers from a dedicated repo directory under `/srv/docker`

The repository includes a production compose file at [docker-compose-prd.yml](../docker-compose-prd.yml), a sample production environment file at [example.env.prd](../example.env.prd), and the Django settings in [sj/settings.py](../sj/settings.py).

Important note:
- This project uses SQLite as its database backend.
- The database files are stored in a host data directory, not only inside the container.
- Static files are served via Docker volume `static_sj_prd`.

For this project, use this layout:

```text
/srv/docker/
├── sj-github/          # Git repo
├── sj-github/data/     # app-specific data directory
├── npm/                # reverse proxy stack
├── docker/             # shared docker config, if needed
└── ...
```

This keeps each app isolated and makes it clear which repo and which data directory belong together.

---

## 1. Server requirements

Recommended minimum VM setup:

- 2 CPU
- 4 GB RAM
- 40 GB disk
- Ubuntu 24.04 LTS or newer

---

## 2. Install required software

On the server, install:

- Git
- Docker
- Docker Compose
- OpenSSH

Example:

```bash
sudo apt update
sudo apt install -y git docker.io docker-compose-plugin openssh-server
```

Enable Docker and make sure it starts automatically:

```bash
sudo systemctl enable docker
sudo systemctl start docker
sudo systemctl status docker
```

Check that Docker is working:

```bash
docker --version
docker compose version
```

---

## 3. Configure the network

### Option A: use a fixed IP address
If the server should always use the same IP, configure netplan.

Example configuration:

```bash
cd /etc/netplan
sudo nano 50-cloud-init.yaml
```

Use something like this:

```yaml
network:
  version: 2
  ethernets:
    ens33:
      addresses:
        - "192.168.175.100/24"
      nameservers:
        addresses:
          - 192.168.175.1
        search: []
      routes:
        - to: "default"
          via: "192.168.175.1"
```

Then apply it:

```bash
sudo netplan try
sudo systemctl restart systemd-networkd
```

### Option B: use DHCP
If you prefer DHCP, set:

```yaml
network:
  version: 2
  ethernets:
    ens33:
      dhcp4: true
```

Then apply:

```bash
sudo netplan try
```

---

## 4. Create the base structure under /srv/docker

Use a single root for all Docker-related services and apps:

```bash
sudo mkdir -p /srv/docker
sudo mkdir -p /srv/docker/npm
sudo mkdir -p /srv/docker/sj-github
sudo mkdir -p /srv/docker/sj-github/data
```

This gives you a clear structure:

```text
/srv/docker/
├── sj-github/
│   ├── .git/
│   ├── .env
│   ├── docker-compose-prd.yml
│   ├── data/
│   └── ...
├── npm/
│   ├── docker-compose.yml
│   ├── data/
│   └── letsencrypt/
└── ...
```

This is the preferred location for service and app data on a Linux server.

---

## 5. Prepare Docker network and volume

Create the Docker network used by the application and proxy:

```bash
sudo docker network create --subnet=172.20.60.0/24 -d=bridge proxynet
```

Create the static file volume:

```bash
sudo docker volume create static_sj_prd
```

This volume is referenced by the project and is required for static files.

---

## 6. Install Nginx Proxy Manager

Create the reverse proxy directory and compose file:

```bash
cd /srv/docker/npm
nano docker-compose.yml
```

Use this content:

```yaml
services:
  app:
    image: 'jc21/nginx-proxy-manager:latest'
    restart: unless-stopped
    ports:
      - '80:80'
      - '443:443'
      - '81:81'
    volumes:
      - ./data:/data
      - ./letsencrypt:/etc/letsencrypt
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

Start the proxy manager:

```bash
docker compose up -d
```

Open the admin web interface:

```text
http://SERVER_IP:81
```

Log in with the default Nginx Proxy Manager credentials and change the password.

---

## 7. Clone the git repo under /srv/docker

If the repo is private, you must add your SSH key to GitHub first.

```bash
cd /srv/docker
git clone git@github.com:fPBunxGKv/sj-github.git sj-github
```

This keeps the repo under the app-specific directory and matches the naming convention used in this setup.

If you do not use SSH, use HTTPS instead.

---

## 8. Prepare the environment file

Copy the sample production environment file:

```bash
cd /srv/docker/sj-github
cp example.env.prd .env
nano .env
```

Edit the file to match your environment:

- `DJANGO_SECRET_KEY`: change it to a real secret
- `DJANGO_ALLOWED_HOSTS`: set the real hostnames or domain names
- `DJANGO_CSRF_TRUSTED_ORIGINS`: set the public HTTPS origin(s)
- `DJANGO_SESSION_COOKIE_SECURE`: usually `True` in production
- `DATABASE_NAME`: name of the SQLite database file
- `EMAIL_*`: SMTP values for sending emails
- `PRINTER_RUN_IP` and `PRINTER_REG_IP`: printer addresses if needed
- `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND`: Redis addresses

The project expects the environment file to be present before the Docker containers start. A working example is in [example.env.prd](../example.env.prd).

---

## 9. Prepare the app data directory

The application stores its SQLite database in a host folder under the repo directory. For this project, keep the app data in a dedicated folder:

```bash
mkdir -p /srv/docker/sj-github/data
```

This matches the bind mount structure used by the project. The compose file is intended to mount a host path like this:

```yaml
- /srv/docker/sj-github/data:/app/data
```

If you use a different folder name, keep the same pattern: `app-name/data` under `/srv/docker`.

---

## 10. Adjust the compose file for the final path

Open [docker-compose-prd.yml](../docker-compose-prd.yml) and confirm the host database path matches the layout above.

The production file currently uses a hostname-specific path, such as:

```yaml
- /home/admsqline/projects/data/sj_prd:/app/data
```

Change it to the standard layout used here:

```yaml
- /srv/docker/sj-github/data:/app/data
```

Do the same for any host path that should live under the app-specific data directory.

---

## 11. Build and start the app containers

From the project root:

```bash
cd /srv/docker/sj-github
sudo docker compose -f docker-compose-prd.yml up --build --force-recreate -d
```

This will start:

- `sj-prd-web` — Django app
- `sj-prd-worker` — Celery background worker
- `sj-prd-redis` — Redis for Celery

The Docker image is built from [docker/Dockerfile](../docker/Dockerfile) and the web container runs the script in [docker/server-entrypoint.sh](../docker/server-entrypoint.sh).

---

## 12. Check whether the app is running

Check the running containers:

```bash
sudo docker ps
```

Look for:

- `sj-prd`
- `sj-prd-worker`
- `sj-prd-redis`

Check logs if needed:

```bash
sudo docker logs sj-prd
sudo docker logs sj-prd-worker
```

If everything is fine, the app should be reachable through your reverse proxy.

---

## 13. Configure the reverse proxy in Nginx Proxy Manager

In the Nginx Proxy Manager UI:

1. Add a new proxy host
2. Set the domain name, for example `sj.example.com`
3. Set the target host to the Docker container name or internal network address, depending on your network setup
4. Set the scheme to `http`
5. Point the upstream to the app container port `8000`
6. Enable SSL if you have a certificate or upload a self-signed one for testing
7. Save the configuration

Example backend target:

```text
http://sj-prd:8000
```

The web app listens on port `8000` inside the Docker network.

---

## 14. Create an SSL certificate

For local or internal testing, you can generate a self-signed certificate:

```bash
openssl req -newkey rsa:4096 \
  -x509 \
  -sha256 \
  -days 3650 \
  -nodes \
  -out sj1.crt \
  -keyout sj1.key
```

Fill in the prompts, for example:

```text
Country Name: CH
State or Province: Bern
Locality: Jegenstorf
Organization: Turnverein Jegenstorf
Common Name: sj1.squareline.ch
```

This is only for local or test usage; production should normally use a real certificate from Let’s Encrypt or an internal PKI.

---

## 15. Create the Django admin user

After the app is up, create the first superuser:

```bash
docker exec -it sj-prd python manage.py createsuperuser
```

Then log in to the application via the web UI.

---

## 16. Load initial data

The repository contains demo and test data files in the project root:

- `sj_events.json`
- `sj_users_demo.json`
- `sj_users_test_w05_w16_m05_m16.json`

Load event data:

```bash
docker exec -it sj-prd python manage.py loaddata sj_events.json
```

Load demo users:

```bash
docker exec -it sj-prd python manage.py loaddata sj_users_demo.json
```

Optional test data:

```bash
docker exec -it sj-prd python manage.py loaddata sj_users_test_w05_w16_m05_16.json
```

---

## 17. Local development option

If you want to run the app directly on your machine instead of only in Docker, this is also possible.

Requirements:

- Python 3.13 or compatible version
- Virtual environment

Example:

```bash
cd /srv/docker
python3 -m venv env
source env/bin/activate
pip install -r sj-github/requirements.txt
cd sj-github
cp example.env.dev .env
source .env
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata sj_events.json
python manage.py runserver
```

Then open:

```text
http://localhost:8000/
```

---

## 18. Common troubleshooting

### The app does not start
Check container logs:

```bash
sudo docker logs sj-prd
```

Common reasons:

- `.env` file missing or invalid
- incorrect host path for the database folder
- Docker network `proxynet` does not exist
- static volume missing

### Database error
Make sure the database directory exists and is writable:

```bash
ls -ld /srv/docker/sj-github/data
```

### 502 or reverse proxy issue
Verify that the backend target points to the correct internal address and port.

Usually this is:

```text
http://sj-prd:8000
```

### Static files are not loading
Check that the volume exists and is mounted correctly:

```bash
sudo docker volume ls
sudo docker inspect static_sj_prd
```

---

## 19. Final result

When the setup is complete, you should have:

- the application running as Docker containers
- a reverse proxy in front of it
- SSL configured through Nginx Proxy Manager or a certificate you added
- a configured `.env` file in `/srv/docker/sj-github`
- a data directory at `/srv/docker/sj-github/data`
- a working Django admin user
- the initial event and user data loaded

At that point, anyone with the correct URL can open the system and use it.

---

## 20. Quick summary

If you want the shortest possible setup path, do this:

```bash
sudo apt update
sudo apt install -y git docker.io docker-compose-plugin openssh-server
sudo systemctl enable docker
sudo systemctl start docker
sudo mkdir -p /srv/docker/npm /srv/docker/sj-github /srv/docker/sj-github/data
sudo docker network create --subnet=172.20.60.0/24 -d=bridge proxynet
sudo docker volume create static_sj_prd
cd /srv/docker
git clone git@github.com:fPBunxGKv/sj-github.git sj-github
cd /srv/docker/sj-github
cp example.env.prd .env
# edit .env
cd /srv/docker/npm
# create docker-compose.yml with Nginx Proxy Manager content
sudo docker compose up -d
cd /srv/docker/sj-github
sudo docker compose -f docker-compose-prd.yml up --build --force-recreate -d
sudo docker exec -it sj-prd python manage.py createsuperuser
```

After that, configure the domain in Nginx Proxy Manager and open the site in your browser.

---

## 21. Notes

This file is a practical installation guide, not an exhaustive developer guide. For app-specific behavior, check the project source files and the Django admin pages.

If the repository is private, make sure the server's SSH key is registered with GitHub before cloning.

```bash
cd ~/projects/sj-github
sudo docker compose -f docker-compose-prd.yml up --build --force-recreate -d
```

This will start:

- `sj-prd-web` — Django app
- `sj-prd-worker` — Celery background worker
- `sj-prd-redis` — Redis for Celery

The Docker image is built from [docker/Dockerfile](../docker/Dockerfile) and the web container runs the script in [docker/server-entrypoint.sh](../docker/server-entrypoint.sh).

---

## 10. Check whether the app is running

Check the running containers:

```bash
sudo docker ps
```

Look for:

- `sj-prd`
- `sj-prd-worker`
- `sj-prd-redis`

Check logs if needed:

```bash
sudo docker logs sj-prd
sudo docker logs sj-prd-worker
```

If everything is fine, the app should be reachable through your reverse proxy.

---

## 11. Configure the reverse proxy in Nginx Proxy Manager

In the Nginx Proxy Manager UI:

1. Add a new proxy host
2. Set the domain name, for example `sj.example.com`
3. Set the target host to the Docker container name or internal network address, depending on your network setup
4. Set the scheme to `http`
5. Point the upstream to the app container port `8000`
6. Enable SSL if you have a certificate or upload a self-signed one for testing
7. Save the configuration

Example backend target:

```text
http://sj-prd:8000
```

The web app listens on port `8000` inside the Docker network.

---

## 12. Create an SSL certificate

For local or internal testing, you can generate a self-signed certificate:

```bash
openssl req -newkey rsa:4096 \
  -x509 \
  -sha256 \
  -days 3650 \
  -nodes \
  -out sj1.crt \
  -keyout sj1.key
```

Fill in the prompts, for example:

```text
Country Name: CH
State or Province: Bern
Locality: Jegenstorf
Organization: Turnverein Jegenstorf
Common Name: sj1.squareline.ch
```

This is only for local or test usage; production should normally use a real certificate from Let’s Encrypt or an internal PKI.

---

## 13. Create the Django admin user

After the app is up, create the first superuser:

```bash
docker exec -it sj-prd python manage.py createsuperuser
```

Then log in to the application via the web UI.

---

## 14. Load initial data

The repository contains demo and test data files in the project root:

- `sj_events.json`
- `sj_users_demo.json`
- `sj_users_test_w05_w16_m05_m16.json`

Load event data:

```bash
docker exec -it sj-prd python manage.py loaddata sj_events.json
```

Load demo users:

```bash
docker exec -it sj-prd python manage.py loaddata sj_users_demo.json
```

Optional test data:

```bash
docker exec -it sj-prd python manage.py loaddata sj_users_test_w05_w16_m05_m16.json
```

---

## 15. Local development option

If you want to run the app directly on your machine instead of only in Docker, this is also possible.

Requirements:

- Python 3.13 or compatible version
- Virtual environment

Example:

```bash
cd ~/projects
python3 -m venv env
source env/bin/activate
pip install -r sj-github/requirements.txt
cd sj-github
cp example.env.dev .env
source .env
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata sj_events.json
python manage.py runserver
```

Then open:

```text
http://localhost:8000/
```

---

## 16. Common troubleshooting

### The app does not start
Check container logs:

```bash
sudo docker logs sj-prd
```

Common reasons:

- `.env` file missing or invalid
- incorrect host path for the database folder
- Docker network `proxynet` does not exist
- static volume missing

### Database error
Make sure the database directory exists and is writable.

```bash
ls -ld ~/projects/data/sj_prd
```

### 502 or reverse proxy issue
Verify that the backend target points to the correct internal address and port.

Usually this is:

```text
http://sj-prd:8000
```

### Static files are not loading
Check that the volume exists and is mounted correctly:

```bash
sudo docker volume ls
sudo docker inspect static_sj_prd
```

---

## 17. Final result

When the setup is complete, you should have:

- the application running as Docker containers
- a reverse proxy in front of it
- SSL configured through Nginx Proxy Manager or a certificate you added
- a configured `.env` file
- a working Django admin user
- the initial event and user data loaded

At that point, anyone with the correct URL can open the system and use it.

---

## 18. Quick summary

If you want the shortest possible setup path, do this:

```bash
sudo apt update
sudo apt install -y git docker.io docker-compose-plugin openssh-server
sudo systemctl enable docker
sudo systemctl start docker
sudo docker network create --subnet=172.20.60.0/24 -d=bridge proxynet
sudo docker volume create static_sj_prd
mkdir -p ~/projects/npm && cd ~/projects/npm
# create docker-compose.yml with Nginx Proxy Manager content
sudo docker compose up -d
cd ~/projects
git clone git@github.com:fPBunxGKv/sj-github.git
cd sj-github
cp example.env.prd .env
# edit .env
mkdir -p ~/projects/data/sj_prd
sudo docker compose -f docker-compose-prd.yml up --build --force-recreate -d
sudo docker exec -it sj-prd python manage.py createsuperuser
```

After that, configure the domain in Nginx Proxy Manager and open the site in your browser.

---

## 19. Notes

This file is a practical installation guide, not an exhaustive developer guide. For app-specific behavior, check the project source files and the Django admin pages.

If the repository is private, make sure the server's SSH key is registered with GitHub before cloning.

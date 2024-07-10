# Server config

- git clone https://github.com/GaetanDesrues/Mongo_FastAPI_Docker_APP.git
- Create `.env` file
- DNS record
- Proxy + TLS certificate
- nginx reverse proxy
- docker compose up

```bash
sudo nano /etc/nginx/sites-available/qr.kerga.fr
sudo ln -s /etc/nginx/sites-available/qr.kerga.fr /etc/nginx/sites-enabled/qr.kerga.fr
sudo nginx -s reload
sudo service nginx status

server {
  server_name qr.kerga.fr;
  location / {
        proxy_pass http://127.0.0.1:8086;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }
}
```

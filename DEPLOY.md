# Feroz ko chalane ke 2 tareeqe

## A) Sirf apne computer par (local) — sab se aasan
`start.bat` (Windows) ya `./start.sh` (Mac/Linux) chalao. Details README.md me hain.
Ye har waqt kaam karta hai, internet na bhi ho (sirf AI/search/social ke liye internet chahiye, app khud local hai).

## B) Kisi server par (host) — taake apne phone/kahin se bhi khul sake

Koi bhi normal VPS (DigitalOcean, Hetzner, AWS EC2 waghaira) ya PaaS (Railway, Render) chalega.
Neeche VPS (Ubuntu) ka tareeqa hai:

### 1. Backend
```bash
sudo apt update && sudo apt install -y python3-venv nginx
git clone <apka-repo-ya-zip-nikalo> feroz && cd feroz/backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # nano .env se keys aur ACCESS_KEY (zaroor bharo, server public hai!) bharo
```
`systemd` service banao (`/etc/systemd/system/feroz-backend.service`):
```ini
[Unit]
Description=Feroz backend
After=network.target

[Service]
WorkingDirectory=/home/USER/feroz/backend
ExecStart=/home/USER/feroz/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
User=USER

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable --now feroz-backend
```

### 2. Frontend (build karke static files banao)
```bash
cd ../frontend
npm install && npm run build     # dist/ folder banega
```

### 3. Nginx (dono ko ek domain par serve karo)
`/etc/nginx/sites-available/feroz`:
```nginx
server {
    listen 80;
    server_name apka-domain.com;

    location / {
        root /home/USER/feroz/frontend/dist;
        try_files $uri /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        client_max_body_size 20m;
    }
}
```
```bash
sudo ln -s /etc/nginx/sites-available/feroz /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d apka-domain.com   # free HTTPS (Let's Encrypt)
```

### 4. Zaroori hifazat jab hosted ho
- `ACCESS_KEY` **zaroor** set karo (khali mat chhoro) - warna koi bhi internet se aapka Copilot use kar sakta hai.
- HTTPS zaroor lagao (mic sirf https/localhost par chalta hai; certbot upar diya hai).
- `CORS_ORIGINS` me apna asal domain likho (`.env` me).
- Server ka firewall sirf 80/443 khula rakho, 8000 seedha public na ho (Nginx proxy karta hai).

Doosra aasan tareeqa: **Railway.app** ya **Render.com** par backend ko "Python/FastAPI" service ki tarah, aur frontend ko "Static Site" (build command `npm run build`, publish dir `dist`) ki tarah deploy karo — dono free tier dete hain. Unke dashboard me hi environment variables (`.env` wale) daal do.

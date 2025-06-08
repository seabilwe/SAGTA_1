# Y-Flip Tile Proxy

A lightweight Flask-based proxy that converts XYZ tile requests with positive Y coordinates into TMS-compatible URLs (flipping the Y value).  
Useful for serving old TMS tile servers (like the South African NGI maps) via modern web clients (Lizmap, OpenLayers, QGIS) that only understand XYZ.

---

## 🧰 Features

- Converts `{z}/{x}/{y}.png` to `{z}/{x}/{2^z - 1 - y}.png`
- Supports dynamic upstream via URL
- Can be deployed via Docker and proxied via Nginx
- Minimal dependencies (Flask + Requests)

---

## 🔧 How to Run (Docker Compose)

This will run the proxy on port **8088** by default.

```bash
docker compose up -d
```

Once started, it is available at:

```bash
http://localhost:8088/proxy/<tile_server>/<z>/<x>/<y>.png
```

### Example:

```bash
http://localhost:8088/proxy/htonl.dev.openstreetmap.org/ngi-tiles/tiles/50k/6/30/22.png
```

This will fetch:

```bash
https://htonl.dev.openstreetmap.org/ngi-tiles/tiles/50k/6/30/41.png
```

(using 2^6 - 1 - 22 = 41)

---

## 🔨 How to Build

If you want to build the image manually:

```bash
docker build -t yflip-proxy .
```

Run it:

```bash
docker run --rm -p 8088:5000 yflip-proxy
```

---

## 📁 Project Structure

```
.
├── app.py               # Flask proxy logic
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker image build
├── docker-compose.yml   # Compose setup for port 8088
└── README.md
```

---

## ✅ Requirements

	•	Docker + Docker Compose
	•	Python 3.11+ if running outside Docker



# Regjistri i Gjendjes Civile 2008

Kërkimi dhe shfletimi i të dhënave të Regjistrit të Gjendjes Civile të Republikës së Shqipërisë (Nëntor 2008).

Mbi **4.2 milionë** të dhëna, **41 mijë** mbiemra unikë, **119 mijë** emra unikë.

## Veçoritë

- **Kërkim** sipas emrit, mbiemrit, emrit të babait ose ID-së
- **Shfletim familjar** — shfaq anëtarët e familjes, prindërit, gjyshërit
- **Lidhje të klikueshme** — navigim midis anëtarëve të familjes
- **Dizajn Swiss Minimalism** — i pastër, profesional, me ngjyrat e korporatës blu të errët
- **Responsive** — funksionon në desktop dhe pajisje mobile

## Teknologjitë

- **Backend**: Python 3 + SQLite
- **Frontend**: HTML + CSS + JavaScript vanilla
- **Database**: SQLite me optimizime (WAL mode, indekse, cache 64 MB)
- **Hosting**: Render (Web Service)

## Instalimi Lokal

```bash
git clone https://github.com/DeFrag01/GjendjaCiv2008Remake.git
cd GjendjaCiv2008Remake
pip install -r requirements.txt
python3 server.py
```

Hapni [http://127.0.0.1:8080](http://127.0.0.1:8080) në browser.

## API

| Endpoint | Parametra | Përshkrimi |
|----------|-----------|-----------|
| `GET /api/search?q=term&page=1` | `q` — termi i kërkimit, `page` — faqja | Kërkim i personave |
| `GET /api/person?id=123` | `id` — ID e personit | Detajet e personit + familja |
| `GET /api/stats` | — | Statistikat e përgjithshme |
| `GET /api/suggest?q=term` | `q` — termi i kërkimit | Sugjerime mbiemrash |

## Licensa

MIT

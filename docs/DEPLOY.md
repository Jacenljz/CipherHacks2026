# Deploying Chaff with a Real Cowrie Honeypot

This turns the simulated globe into **real, live attacks**: deploy a Cowrie
honeypot on a public VPS and point Chaff at its log. Works on any Ubuntu
22.04/24.04 host.

## 0. Pick a host

| Option | Free? | Notes |
|---|---|---|
| **Oracle Cloud — Always Free** | Yes (best) | Up to 4 ARM cores / 24 GB, or 2 AMD micro VMs. Must open ports in BOTH the Security List **and** the instance's OS firewall (Oracle gotcha). |
| **Google Cloud — Free Tier** | Yes | 1 always-free `e2-micro` in `us-west1`/`us-central1`/`us-east1` (1 GB RAM) + $300/90-day credit. Needs a card to verify. |
| **AWS Free Tier** | 12 months | `t2.micro`/`t3.micro`, not always-free. |
| **Hetzner / DigitalOcean / Vultr** | ~$4–6/mo | Simplest, no free-tier quirks. |

Any of these is plenty — Cowrie is lightweight.

## 1. ⚠️ Move your admin SSH off port 22 FIRST

The honeypot will take over port 22. Before that, move your real SSH so you
don't lock yourself out:

```bash
sudo sed -i 's/^#\?Port 22$/Port 22022/' /etc/ssh/sshd_config
sudo systemctl restart ssh
```

Open 22022 in the firewall (next step), then **reconnect on 22022 and confirm
it works before continuing**:

```bash
ssh -p 22022 youruser@YOUR_VPS_IP
```

## 2. Open firewall / security-group ports

Allow inbound TCP: **22** (honeypot SSH), **23** (honeypot Telnet), **22022**
(your admin SSH), **8000** (Chaff UI, if you serve it from the VPS).

- **GCP:** VPC Network → Firewall → rule allowing `tcp:22,23,8000,22022`.
- **Oracle:** add ingress rules in the Security List **and**
  `sudo iptables -I INPUT -p tcp --dport <port> -j ACCEPT` for each.
- **Hetzner/DO/Vultr:** the Cloud Firewall UI.

## 3. Install Cowrie

```bash
sudo apt update && sudo apt install -y git python3-venv python3-pip \
  libssl-dev libffi-dev build-essential
sudo adduser --disabled-password --gecos "" cowrie
sudo su - cowrie

git clone https://github.com/cowrie/cowrie
cd cowrie
python3 -m venv cowrie-env
source cowrie-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp etc/cowrie.cfg.dist etc/cowrie.cfg
```

(Optional, more attacks) enable Telnet — in `etc/cowrie.cfg`, under `[telnet]`
set `enabled = true`.

Start it:

```bash
bin/cowrie start
```

Cowrie listens on **2222** (SSH) and **2223** (Telnet); its JSON log is at
`/home/cowrie/cowrie/var/log/cowrie/cowrie.json`.

## 4. Redirect 22 → 2222 and 23 → 2223

Cowrie runs unprivileged, so redirect the low ports (run as your sudo user;
`exit` the cowrie shell first):

```bash
exit   # leave the cowrie user
sudo iptables -t nat -A PREROUTING -p tcp --dport 22 -j REDIRECT --to-port 2222
sudo iptables -t nat -A PREROUTING -p tcp --dport 23 -j REDIRECT --to-port 2223
sudo apt install -y iptables-persistent && sudo netfilter-persistent save
```

Real bots hitting `:22`/`:23` now land in the honeypot. Within minutes you'll
see login attempts in `cowrie.json`.

## 5. Point Chaff at the log

**Option A — run Chaff on the VPS (simplest):** clone this repo, build the
frontend (`npm --prefix frontend run build`), then:

```bash
export CHAFF_COWRIE_LOG=/home/cowrie/cowrie/var/log/cowrie/cowrie.json
backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend \
  --host 0.0.0.0 --port 8000
```

Open `http://YOUR_VPS_IP:8000` — the globe now shows real attacks.

**Option B — run Chaff on your laptop, sync the log (more robust for a live
demo):**

```bash
# from Git Bash on Windows, or any unix shell
scp -P 22022 cowrie@YOUR_VPS_IP:/home/cowrie/cowrie/var/log/cowrie/cowrie.json ./cowrie.json
export CHAFF_COWRIE_LOG="$PWD/cowrie.json"
# re-run scp every minute or two to pull fresh attacks
```

The adapter tails the file incrementally, so re-syncing just appends new events.

## 6. (Recommended) Accurate geolocation

Without a GeoIP database Chaff maps IPs to a deterministic fallback location.
For true coordinates:

```bash
backend/.venv/bin/pip install geoip2
# Download a free MaxMind GeoLite2-City.mmdb (free account at maxmind.com)
export CHAFF_GEOIP_DB=/path/to/GeoLite2-City.mmdb
```

Every real attacker IP now resolves to its actual location.

## Safety & ethics

- A honeypot only **passively receives** unsolicited traffic — legal. Never
  attack back.
- Cowrie is medium-interaction (an emulated shell); attackers never reach your
  real system.
- Keep admin SSH key-only and on the moved port.
- **Deploy a few days before the event** so you accumulate a rich dataset.
- Tear it down afterward.
```


# 🚀 Raj Leads Generator - Run Instructions

# Running the Raj Leads Generator

## Prerequisites

### 1. Python and Playwright
Ensure you have Python 3 installed and Playwright browsers set up:
```bash
pip install playwright
playwright install
```

### 2. Web Server

#### Option A: Nginx + PHP-FPM (Recommended for Production)
For multi-user support with concurrent access:
```bash
sudo apt update
sudo apt install -y nginx php-fpm
```

**Advantages:**
- ✅ Handles multiple concurrent users
- ✅ Better performance under load
- ✅ Production-ready
- ✅ Auto-starts on system boot

#### Option B: PHP Development Server (Fallback)
For single-user testing:
```bash
php --version
```

**Limitations:**
- ⚠️ Single-threaded (1-2 concurrent users max)
- ⚠️ Not suitable for production
- ⚠️ May timeout under heavy load

---

## Running Locally

### Option 1: Using the Start Script (Recommended)
The simplest way to run the application:

```bash
./start.sh
```

This will:
- Auto-detect and use Nginx if installed, or fallback to PHP dev server
- Start services on port 8005
- Open the app at `http://localhost:8005/`
- Automatically attempt to start a Cloudflare Tunnel (if `cloudflared` is installed)

**To stop the application:**
```bash
./stop.sh
```

### Option 2: Manual Start

#### With Nginx:
```bash
sudo systemctl start nginx php8.4-fpm
# App will be available at http://localhost:8005/
```

#### With PHP Dev Server:
```bash
cd /path/to/raj_leadar_generator_playwrite
php -S localhost:8005
```

Then open `http://localhost:8005/` in your browser.

---

## Verifying Services

### Check Nginx Status:
```bash
sudo systemctl status nginx
```

### Check PHP-FPM Status:
```bash
sudo systemctl status php8.4-fpm
```

### Check Port 8005:
```bash
curl http://localhost:8005/
```

---

## Exposing to the Internet (Cloudflare Tunnel)

To make your local app accessible from the internet, use Cloudflare Tunnel.

### Prerequisites
1.  Download `cloudflared` from [Cloudflare Downloads](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/)
2.  Install it on your system.

### Command to Expose
Run this command in a **new terminal** window while your app is running:

```bash
cloudflared tunnel --url http://localhost:8005
```

### What happens next?
1.  Cloudflare will generate a unique link (e.g., `https://random-name.trycloudflare.com`).
2.  Copy that link.
3.  Open the link directly in any browser (e.g., `https://random-name.trycloudflare.com`).
4.  **Note**: This is a temporary link. For a permanent domain, you'll need to configure a defined tunnel via Cloudflare Dashboard.

---

## ⚠️ Important Notes
*   **Keep the Terminal Open**: The PHP server must remain running for the tool to work.
*   **Python Path**: Ensure `python3` is available in your system path.

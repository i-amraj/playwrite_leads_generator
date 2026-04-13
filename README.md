# 🚀 Raj Leads Generator Pro

**Raj Leads Generator Pro** is a high-performance, automated business lead extraction tool that scrapes real-time business data from Google Maps. Built with a modern tech stack (Python FastAPI + Playwright), it offers a seamless experience for discovering potential clients, extracting their contact details, and exporting them directly to Excel.

---

## ✨ Features

- **Real-time Extraction**: Scrape business names, ratings, review counts, phone numbers, websites, and addresses directly from Google Maps.
- **Location-based Search**: Advanced filtering by Country, State, City, and specific Areas.
- **Unified Web Interface**: A premium, glassmorphic dashboard for managing your searches and leads.
- **Excel Export**: Download your results in clean, professional Excel spreadsheets with a single click.
- **Session History**: Automatically saves your search history so you never lose your progress.
- **Terminal-style Live Log**: Watch the scraper work in real-time with a terminal log integrated into the UI.
- **Multi-OS Support**: Unified startup script (`start.bat`) that works on both Windows and Linux.

---

## 📸 Screenshots

### 🖥️ Dashboard & Search
![Main Dashboard Interface](assets/screenshots/Screenshot%20from%202026-04-13%2017-13-45.png)

### 📊 extraction Process
![Live Scraping Terminal](assets/screenshots/Screenshot%20from%202026-04-13%2017-12-41.png)

### 📂 Search Results & History
![Results Table View](assets/screenshots/Screenshot%20from%202026-04-13%2017-12-48.png)

### ⚙️ Minimalist Design
![Settings and UI Details](assets/screenshots/Screenshot%20from%202026-04-13%2017-21-14.png)

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, FastAPI (Asynchronous Framework)
- **Search Engine**: Playwright (Headless Browser Automation)
- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism), JavaScript (ES6+)
- **Data Handling**: Pandas, OpenPyXL
- **Static Serving**: FastAPI StaticFiles

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10 or higher** installed on your system.
- **Pip** (Python package manager).

### Installation & Execution (The Simple Way)

We have provided a unified startup script that handles dependency installation and server startup in one go.

#### **On Windows / Linux:**
Simply run the `start.bat` file.

**On Linux (Terminal):**
```bash
chmod +x start.bat
./start.bat
```

**On Windows:**
Double-click `start.bat`.

### What This Does:
1.  **Installs/Updates Dependencies**: Automatically installs `fastapi`, `uvicorn`, `playwright`, `pandas`, etc.
2.  **Sets up Playwright**: Downloads the necessary Chromium browser binaries.
3.  **Starts Unified server**: Launches the backend and frontend on **http://localhost:8000**.
4.  **Auto-Open**: Automatically launches the application in your default web browser.

---

## 📂 Project Structure

```text
raj_leadar_generator/
├── assets/                 # CSS, JS, and UI Assets
├── backend/
│   └── python/             # Python Backend Logic
│       ├── api_main.py     # Main Entry Point (Unified Server)
│       ├── core/           # Scraper Core Modules
│       └── data/           # Stored sessions and exports
├── public/                 # Location JSON data
├── index.html              # Main UI
├── history.html            # Search History Page
├── start.bat               # Polyglot Startup Script
└── README.md               # You are here!
```

---

## ⚠️ Important Notes

- **Human-like Behavior**: The scraper is designed with built-in delays to mimic human behavior and avoid being blocked by Google Maps.
- **Keep Terminal Open**: Ensure the terminal window remains open while using the application.
- **Network Required**: An active internet connection is required for scraping and setup.

---

## 👤 Author

Developed by **Raj** 🚀

> [!TIP]
> This tool is intended for research and business networking purposes. Please use it responsibly and in accordance with the terms of service of the sites being accessed.

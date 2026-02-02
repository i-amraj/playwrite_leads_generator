# 🚀 Google Maps Lead Generator - Python Scraper

यह Python script Google Maps से business data scrape करती है।

## 📋 Requirements

```bash
cd backend/python
pip install -r requirements.txt
playwright install chromium
```

## 🎯 Usage

### Basic Usage (Fast - No Details)
```bash
python3 main.py --keyword "gym" --location "lucknow" --limit 10
```

### With Full Details (Name, Phone, Website, Address)
```bash
python3 main.py --keyword "gym" --location "lucknow" --limit 10 --details
```

### Headless Mode (No Browser Window)
```bash
python3 main.py --keyword "restaurant" --location "delhi" --limit 20 --details --headless
```

### Save to File
```bash
python3 main.py --keyword "hotel" --location "mumbai" --limit 15 --details --output ../data/exports/hotels_mumbai.json
```

## 🔧 All Options

| Option | Description | Default |
|--------|-------------|---------|
| `--keyword` | Business type (gym, restaurant, hotel, etc.) | Required |
| `--location` | City/Area name | Required |
| `--limit` | Maximum results to scrape | 10 |
| `--details` | Extract full details (phone, website) | No |
| `--headless` | Run browser without UI | No |
| `--output` | Save JSON to file | None |
| `--scroll-times` | Number of scrolls before extracting | 5 |

## 📊 Output Format

```json
{
  "success": true,
  "message": "Successfully extracted 5 businesses",
  "data": [
    {
      "index": 0,
      "name": "Business Name",
      "rating": "4.5",
      "review_count": "123",
      "category": "Gym",
      "address": "Full Address Here",
      "phone": "9876543210",
      "website": "https://example.com",
      "place_id": "0x390d1d3ff605d8a1:0"
    }
  ],
  "error": null,
  "timestamp": "2026-01-24 13:13:24"
}
```

## 📁 File Structure

```
backend/python/
├── main.py              # CLI entry point
├── requirements.txt     # Dependencies
├── core/
│   ├── __init__.py
│   ├── browser.py      # Browser launch & management
│   ├── search.py       # Google Maps search logic
│   ├── extractor.py    # Data extraction
│   └── stealth.py      # Anti-detection
└── config/
    ├── settings.json   # Timeouts, delays
    └── selectors.json  # CSS selectors
```

## ⚠️ Important Notes

1. **Rate Limiting**: Don't scrape more than 300-500 records per day to avoid Google bans
2. **Delays**: Built-in random delays (2-5 seconds) for human-like behavior
3. **Headless**: Use `--headless` for production, remove for debugging
4. **Details Mode**: Takes longer but gives phone, website, full address

## 🧪 Test Commands

```bash
# Quick test (basic info only)
python3 main.py --keyword "cafe" --location "jaipur" --limit 5 --headless

# Full test (with details)
python3 main.py --keyword "gym" --location "lucknow" --limit 3 --details --headless
```

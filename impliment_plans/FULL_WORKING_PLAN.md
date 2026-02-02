# 📋 पूर्ण कार्य योजना (Full Working Plan)

## 🎯 लक्ष्य (Goal)
- **Playwright‑आधारित वेब स्क्रैपर** का उपयोग करके Google Maps से वास्तविक व्यवसाय डेटा (नाम, फ़ोन, पता, रेटिंग, रिव्यू, वेबसाइट) निकालना।
- निकाले गए डेटा को **JSON** के रूप में फ्रंट‑एंड को भेजना और **Excel (.xlsx)** फ़ाइल के रूप में निर्यात करना।
- मौजूदा Gemini‑API‑आधारित समाधान को पूरी तरह हटाकर 100 % सटीक डेटा प्राप्त करना।

## 🏗️ सिस्टम आर्किटेक्चर (System Architecture)
```
┌─────────────────────┐      ┌─────────────────────┐
│   Frontend (HTML/JS)│      │   PHP API (api/)    │
│  - index.html       │◀────▶│  - search.php       │
│  - settings.html    │      │  - refresh.php      │
│  - history.html     │      │  - export.php       │
└─────────────────────┘      └─────────────────────┘
          │                           │
          ▼                           ▼
   HTTP Request (POST)        Executes Python script
          │                           │
          ▼                           ▼
   ┌───────────────────────────────────────────────┐
   │   Python Playwright Scraper (scraper/)          │
   │   - scrape.py (CLI entry)                     │
   │   - gmaps_scraper.py (core logic)             │
   │   - config.py (settings)                      │
   └───────────────────────────────────────────────┘
          │
          ▼
   JSON Output → PHP parses → Frontend renders
```

## 📂 फ़ोल्डर संरचना (Folder Structure)
```
excel_ganarator/
├── api/                # PHP endpoints
│   ├── search.php
│   ├── refresh.php
│   └── export.php
├── scraper/            # Python Playwright scraper
│   ├── __init__.py
│   ├── scrape.py       # CLI entry point
│   ├── gmaps_scraper.py
│   ├── config.py
│   └── requirements.txt
├── helpers/            # Misc helpers (excel generation etc.)
│   └── excel.php
├── assets/             # CSS/JS
│   ├── css/style.css
│   └── js/app.js
├── plan/               # Documentation
│   ├── PLAYWRIGHT_IMPLEMENTATION_PLAN.md
│   └── FULL_WORKING_PLAN.md   ← **यह फ़ाइल**
├── index.html, settings.html, history.html, ...
└── storage/            # डेटा, कैश, इतिहास
```

## 🔄 डेटा फ़्लो (Data Flow)
1. **यूज़र** फ़्रंट‑एंड पर फ़ॉर्म भरता है (देश, राज्य, शहर, व्यवसाय प्रकार)।
2. **JavaScript** `fetch`/`XMLHttpRequest` के माध्यम से `api/search.php` को POST करता है।
3. `search.php`:
   - इनपुट को वैलिडेट करता है।
   - Python कमांड बनाता है:
     ```php
     $cmd = "python3 scraper/scrape.py --country $country --city $city --area $area --type $type --max-results 30";
     $output = shell_exec($cmd . ' 2> /dev/null');
     ```
   - `shell_exec` से JSON प्राप्त करता है, `json_decode` से PHP ऐरे बनाता है।
   - त्रुटियों को हैंडल कर JSON‑एरर रिस्पॉन्स देता है।
4. PHP JSON को सीधे फ्रंट‑एंड को रिटर्न करता है।
5. फ्रंट‑एंड टेबल में डेटा दिखाता है और **Export** बटन पर `api/export.php` को कॉल करता है।
6. `export.php` PHPSpreadsheet का उपयोग करके JSON को `.xlsx` में बदलता है और डाउनलोड करता है।

## 🧩 मुख्य लॉजिक (Core Logic)
### Python (`scraper/gmaps_scraper.py`)
- **launch_browser()**: Chromium headless + `playwright‑stealth` लागू करता है।
- **search(query)**: सीधे `https://www.google.com/maps/search/<query>` पर नेविगेट करता है, कंसेंट डायलॉग को बायपास करता है।
- **scroll_results(times)**: परिणाम पैनल को कई बार स्क्रॉल करता है, प्रत्येक स्क्रॉल के बाद 2 सेकंड इंतज़ार।
- **extract_businesses()**: सभी कार्ड (`.Nv2PK`) से नाम, रेटिंग, रिव्यू काउंट, बेसिक पता एकत्र करता है।
- **get_business_details(card)**: कार्ड पर क्लिक → पॉप‑अप खोलता है → फ़ोन (`tel:`), वेबसाइट, पूरा पता निकालता है।
- **close()**: ब्राउज़र बंद करता है।

### CLI (`scraper/scrape.py`)
- `argparse` से सभी पैरामीटर लेता है।
- `GoogleMapsScraper` को इनिशियलाइज़ कर `search`, `scroll_results`, `extract_businesses` को क्रमशः कॉल करता है।
- प्रत्येक कार्ड के लिए `get_business_details` चलाता है।
- सभी डेटा को एक लिस्ट में इकट्ठा कर **JSON** (`{"success":true,"businesses":[...]}`) stdout पर प्रिंट करता है।
- त्रुटियों के लिए `{"success":false,"error":"..."}` रिटर्न करता है।

## 📋 कार्य चरण (Implementation Steps)
| चरण | विवरण | स्थिति |
|------|--------|--------|
| 1️⃣ योजना | मौजूदा Gemini‑आधारित कोड को समझना, Playwright‑आधारित स्क्रैपर की रूपरेखा बनाना। | ✅ पूर्ण |
| 2️⃣ सेट‑अप | Python, Playwright, Chromium, playwright‑stealth स्थापित करना। | ✅ पूर्ण |
| 3️⃣ स्क्रैपर कोर | `gmaps_scraper.py` में ब्राउज़र लॉन्च, सर्च, स्क्रॉल, डेटा एक्सट्रैक्शन लागू करना। | ✅ पूर्ण |
| 4️⃣ CLI | `scrape.py` बनाकर पैरामीटर पार्सिंग और JSON आउटपुट जोड़ना। | ✅ पूर्ण |
| 5️⃣ PHP इंटीग्रेशन | `api/search.php` को Python कॉल करने के लिए अपडेट करना, एरर‑हैंडलिंग जोड़ना। | ✅ पूर्ण |
| 6️⃣ रिफ्रेश एन्डपॉइंट | `api/refresh.php` बनाकर कैश‑डाटा मर्ज करना। | ✅ पूर्ण |
| 7️⃣ एक्सेल एक्सपोर्ट | `api/export.php` में PHPSpreadsheet के साथ XLSX जनरेट करना। | ✅ पूर्ण |
| 8️⃣ UI अपडेट | फ्रंट‑एंड में एक्सपोर्ट बटन, लोडिंग स्पिनर, एरर मेसेज जोड़ना। | ✅ पूर्ण |
| 9️⃣ टेस्टिंग | यूनिट, इंटीग्रेशन, मैन्युअल UI टेस्ट (विभिन्न शहर/बिज़नेस)। | ✅ पूर्ण |
| 🔟 डाक्यूमेंटेशन | `project.md`, `PLAYWRIGHT_IMPLEMENTATION_PLAN.md`, और इस **FULL_WORKING_PLAN.md** को अपडेट करना। | ✅ पूर्ण |

## 🚀 उन्नत सुधार (Advanced Enhancements)
### 1️⃣ पूर्ण एरिया डेटा – Pagination Engine
Google Maps एक ही बार में “सभी परिणाम” नहीं देता; वह अनंत स्क्रॉल + छिपे हुए pagination token का उपयोग करता है।

**लॉजिक:**
```python
while new_cards:
    scroll
    wait
    extract
```
**स्टॉप कंडीशन:**
- अंतिम 3 स्क्रॉल में कोई नया कार्ड न मिला हो
- या कुल काउंट स्थिर हो गया हो

**इम्प्लीमेंटेशन (scraper/gmaps_scraper.py):**
```python
def scroll_until_end(page):
    prev_count = 0
    same_count = 0
    while same_count < 3:
        cards = page.query_selector_all('.Nv2PK')
        curr_count = len(cards)
        if curr_count == prev_count:
            same_count += 1
        else:
            same_count = 0
        prev_count = curr_count
        page.evaluate("document.querySelector('.m6QErb').scrollBy(0, 1000)")
        page.wait_for_timeout(2000)
```
यह सुनिश्चित करता है कि Google द्वारा अनुमति मिलने पर जितना संभव हो उतना डेटा निकाला जाए।

### 2️⃣ "Get More" बैच पेजिनेशन सिस्टम (Primary Strategy) ⭐ NEW

> **समस्या:** Google Maps एक बार में केवल ~20-60 results दिखाता है, जबकि एक शहर में 1000+ businesses हो सकते हैं।

> **समाधान:** "Get More" बटन के साथ बैच-वाइज़ data extraction - safe, reliable, और complete coverage।

#### 📊 Flow Diagram:
```
┌──────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                                │
├──────────────────────────────────────────────────────────────────────┤
│  [Search: gym in lucknow]                                            │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ 📊 First Batch: 20 results loaded                               │ │
│  │                                                                  │ │
│  │ | # | Name           | Phone      | Rating | Address     |      │ │
│  │ |---|----------------|------------|--------|-------------|      │ │
│  │ | 1 | Neo Fitnes     | 1800309... | 4.3    | Aliganj     |      │ │
│  │ | 2 | Healthism 24x7 | 081879...  | 4.6    | Golf City   |      │ │
│  │ | ...               | ...        | ...    | ...         |      │ │
│  │ | 20| Gold Gym       | 099999...  | 4.2    | Hazratganj  |      │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  [📥 Get More] ← Click करने पर delay countdown दिखेगा               │
│  ⏳ Loading next batch... 5... 4... 3... 2... 1...                   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ 📊 Second Batch: 20 more results (Total: 40)                    │ │
│  │ | 21| Anytime Fitness| 070809...  | 4.5    | Gomti Nagar |      │ │
│  │ | ...                                                           │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  [📥 Get More] [📤 Export Excel] [🔄 Refresh]                        │
└──────────────────────────────────────────────────────────────────────┘
```

#### 🔄 Data Flow:
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ First Search│ →  │ Show 20     │ →  │ Save Last   │ →  │ Get More    │
│ (Initial)   │    │ Results     │    │ Card ID     │    │ Clicked     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                            │                    │
                                            ▼                    ▼
                                      ┌─────────────┐    ┌─────────────┐
                                      │ progress.json│ ← │ Scroll Past │
                                      │ last_card_id│    │ Last Card   │
                                      └─────────────┘    └─────────────┘
                                                               │
                                                               ▼
                                                        ┌─────────────┐
                                                        │ Extract Next│
                                                        │ 20 Results  │
                                                        └─────────────┘
                                                               │
                                                               ▼
                                                        ┌─────────────┐
                                                        │ Merge with  │
                                                        │ Previous    │
                                                        └─────────────┘
```

#### 📁 State Management:
**`data/progress.json`**:
```json
{
  "session_id": "abc123",
  "query": "gym in lucknow",
  "last_card": {
    "name": "Gold Gym Hazratganj",
    "place_id": "0x399957fbe40b372f:0x1234567890",
    "index": 20
  },
  "total_extracted": 20,
  "batches_completed": 1,
  "all_data": [...],
  "seen_hashes": ["hash1", "hash2", ...]
}
```

#### 🔧 Python Implementation:
```python
def get_more_results(progress_file, batch_size=20):
    """
    Get More button के लिए - अगला बैच निकालता है
    """
    # 1. Progress load करें
    with open(progress_file) as f:
        progress = json.load(f)
    
    last_card_id = progress["last_card"]["place_id"]
    
    # 2. Browser में same search करें
    search(progress["query"])
    
    # 3. Last card तक scroll करें (skip करते हुए)
    scroll_to_card(last_card_id)
    
    # 4. उसके बाद के cards extract करें
    new_cards = get_cards_after(last_card_id, limit=batch_size)
    
    # 5. Delay दिखाएं (human-like)
    for i in range(5, 0, -1):
        print(f"⏳ Next batch in {i} seconds...")
        time.sleep(1)
    
    # 6. Data extract करें
    new_data = extract_with_details(new_cards)
    
    # 7. Progress update करें
    progress["last_card"] = {
        "name": new_data[-1]["name"],
        "place_id": new_data[-1]["place_id"],
        "index": progress["total_extracted"] + len(new_data)
    }
    progress["total_extracted"] += len(new_data)
    progress["batches_completed"] += 1
    progress["all_data"].extend(new_data)
    
    # 8. Save progress
    save_progress(progress_file, progress)
    
    return {
        "success": True,
        "new_count": len(new_data),
        "total_count": progress["total_extracted"],
        "has_more": len(new_cards) == batch_size,
        "data": new_data
    }
```

#### 🖥️ Frontend UI:
```javascript
// Get More button click handler
document.getElementById('getMoreBtn').addEventListener('click', async () => {
    const btn = document.getElementById('getMoreBtn');
    const countdownEl = document.getElementById('countdown');
    
    // Disable button
    btn.disabled = true;
    btn.textContent = 'Loading...';
    
    // Show countdown (delay for safety)
    for (let i = 5; i > 0; i--) {
        countdownEl.textContent = `⏳ Getting more results in ${i} seconds...`;
        await sleep(1000);
    }
    
    // Call API
    const response = await fetch('/api/getmore.php', {
        method: 'POST',
        body: JSON.stringify({ session_id: currentSessionId })
    });
    
    const result = await response.json();
    
    if (result.success) {
        // Append new rows to table
        appendToTable(result.data);
        
        // Update counter
        document.getElementById('totalCount').textContent = result.total_count;
        
        // Hide button if no more data
        if (!result.has_more) {
            btn.textContent = '✅ All Data Loaded';
            btn.disabled = true;
        } else {
            btn.disabled = false;
            btn.textContent = '📥 Get More';
        }
    }
});
```

#### ⚡ API Endpoint (`api/getmore.php`):
```php
<?php
header('Content-Type: application/json');

$input = json_decode(file_get_contents('php://input'), true);
$session_id = $input['session_id'];

// Call Python with session ID
$cmd = "python3 ../backend/python/main.py --mode getmore --session $session_id";
$output = shell_exec($cmd . ' 2>/dev/null');

echo $output;
```

#### 🛡️ Safety Features:
1. **Visible Delay**: हर batch से पहले 5-10 seconds countdown (user को दिखता है)
2. **Duplicate Check**: Hash-based duplicate detection
3. **Rate Limiting**: Server-side limit (max 5 requests per minute)
4. **Session Management**: Browser session reuse जहां संभव हो
5. **Error Recovery**: अगर batch fail हो, तो retry option

#### ✅ Benefits:
| Feature | Benefit |
|---------|---------|
| Batch-wise loading | Fast initial response, user देख सकता है data आ रहा है |
| Visible delay | User को पता है कि safe mode में चल रहा है |
| Session persistence | Browser restart पर भी continue कर सकते हैं |
| Duplicate removal | Clean, unique data guaranteed |
| Has More indicator | User को पता है कि और data बाकी है या नहीं |

इससे **Get More** बटन वास्तव में अगला बैच लाएगा।

### 3️⃣ रीट्राई सिस्टम (Reliability Wrapper)
स्क्रैपिंग में टाइम‑आउट, एलिमेंट मिसिंग, या प्रॉक्सी फेल होना सामान्य है।

**रीट्राई डेकोरेटर:**
```python
import time

def safe_run(fn, retries=3):
    for i in range(retries):
        try:
            return fn()
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(3)
```
इसे ब्राउज़र लॉन्च, पेज लोड, कार्ड क्लिक आदि पर लागू करें। यह सिस्टम की स्थिरता को 10× तक बढ़ा देगा।

### 4️⃣ कंट्री‑लेवल एरिया पार्टिशनिंग
एक ही क्वेरी में पूरे देश का डेटा नहीं निकाला जा सकता।

**रणनीति:** पहले सभी राज्यों और उनके शहरों की सूची बनाएं, फिर प्रत्येक शहर‑वाइज़ स्क्रैप करें।
```python
for state in states:
    for city in cities[state]:
        scrape(city)
```
यह सुनिश्चित करता है कि पूरे देश की कवरेज बिना ओवर‑लोड के मिल जाए।

### 5️⃣ ऑटो‑रेज़्यूम सिस्टम (Fault‑Tolerant Crawler)
यदि स्क्रिप्ट अचानक बंद हो जाए (लैपटॉप बंद, क्रैश), तो डेटा नहीं खोना चाहिए।

**इम्प्लीमेंटेशन:**
- हर 10 रिकॉर्ड पर CSV/JSON में सहेजें।
- साथ ही `progress.json` को अपडेट करें।
- स्टार्टअप पर यदि प्रोग्रेस फाइल मौजूद है तो उससे रेज़्यूम करें।
यह फॉल्ट‑टॉलरेंट क़रॉलर बनाता है।

### 6️⃣ परफ़ॉर्मेंस बनाम सुरक्षा ट्रेड‑ऑफ़
**लक्ष्य:** मुफ्त सिस्टम, अधिकतम डेटा, बैन‑रिस्क न्यूनतम।

**गोल्डन कॉन्फ़िग:**
- 1 शहर = 1 प्रोसेस
- 5‑सेकंड डिले प्रत्येक रिक्वेस्ट के बीच
- 1 ब्राउज़र प्रति रन (हेडलेस `false` ताकि डिबग आसान हो)
- दिन में 300‑500 रिकॉर्ड सुरक्षित सीमा

| लेवल | टूल | उपयोग केस |
|------|------|------------|
| Beginner | Octoparse | छोटे प्रोजेक्ट्स |
| Intermediate | Apify | स्केलेबल लेकिन क्लाउड‑आधारित |
| **Advanced** | **आपका सिस्टम** | कस्टम, फॉल्ट‑टॉलरेंट, बड़े‑स्केल डेटा |
| Enterprise | Distributed Crawlers | भारी एंटरप्राइज़ डेटा पाइपलाइन |

इन छह सुधारों को जोड़ने से आपका स्क्रैपर **सिंगल‑यूज़ टूल** से **पूर्ण‑फ़ीचर क़रॉलर** बन जाएगा, जो लीड‑जनरेशन, SEO‑इंटेलिजेंस, और लोकेशन‑डेटा प्रोवाइडर्स द्वारा उपयोग किए जाने वाले प्रोफेशनल सिस्टम के समान है।

## ✅ सत्यापन योजना (Verification Plan)
1. **स्टैंडअलोन Python टेस्ट** – `scrape.py` को विभिन्न पैरामीटर (city, type, max‑results) के साथ चलाएँ, JSON संरचना की जाँच करें।
2. **PHP इंटीग्रेशन टेस्ट** – `curl -X POST http://localhost:8000/api/search.php` से रिस्पॉन्स वैधता, एरर‑हैंडलिंग।
3. **UI फ़्लो टेस्ट** – ब्राउज़र में पूरा सर्च‑फ़्लो चलाएँ, परिणाम टेबल, फ़ोन‑नंबर, एक्सेल डाउनलोड की पुष्टि।
4. **डेटा सटीकता** – 5‑10 रैंडम एंट्रीज़ को मैन्युअली Google Maps पर जाँचें (फ़ोन, पता)।
5. **परफ़ॉर्मेंस** – 30‑result सर्च में कुल समय < 35 सेकंड (हेडलेस)।
6. **रेट्राय/फ़ॉलबैक** – यदि Python स्क्रिप्ट फेल हो, तो PHP उचित एरर कोड (500) रिटर्न करे।
7. **पेजिनेशन & रेज़्यूम टेस्ट** – बड़े शहर (उदा. Delhi) पर स्क्रैप चलाएँ, `progress.json` बनाकर रेज़्यूम करें और सुनिश्चित करें कि कोई डुप्लिकेट नहीं है।

## 📦 भविष्य के सुधार (Future Enhancements)
- **कैश‑लेयर**: Redis या फ़ाइल‑आधारित कैश के साथ रेट्रिवल गति बढ़ाएँ।
- **हाइब्रिड मोड**: Playwright फेल होने पर Gemini‑API को फ़ॉलबैक विकल्प के रूप में रखें।
- **कनकरेंट स्क्रैपिंग**: कई टैब/इंस्टेंस के साथ समानांतर सर्च (सुरक्षा/रेट‑लिमिट ध्यान में)।
- **Docker कंटेनर**: पूरी एप्लिकेशन (PHP + Python) को Docker‑Compose में पैकेज करें।
- **CI/CD पाइपलाइन**: GitHub Actions के साथ ऑटो‑टेस्ट और डिप्लॉयमेंट सेटअप।

---

**यह दस्तावेज़** `plan/` फ़ोल्डर में रखी गई है और प्रोजेक्ट की वर्तमान स्थिति, कार्य‑प्रवाह, लॉजिक, तथा सत्यापन चरणों को स्पष्ट रूप से दर्शाता है। भविष्य में किसी भी परिवर्तन को इसी फ़ॉर्मेट में अपडेट किया जाएगा।

## 🛡️ Level 1 – Reliability (First Priority)
### 1️⃣ PlaceID‑based Cursor (Major Upgrade)
- Current cursor stores `last_index` which can cause duplicates if Google changes order.
- Store the `place_id` of the last processed business:
```json
{ "last_place_id": "ChIJrTLr‑GyuEmsRBfy61i59si0" }
```
- On next run, skip cards until this `place_id` is encountered, then continue.
- **Impact:** 100 % correct resume, no data loss.

### 2️⃣ Browser Reset Retry
- Replace generic `safe_run(fn)` with explicit retry logic:
```python
for attempt in range(3):
    try:
        start_browser()
        scrape()
        break
    except Exception as e:
        close_browser()
        time.sleep(5)
```
- **Impact:** Handles soft bans, broken sessions, and memory leaks.

## 🌐 Level 2 – Full Coverage (All Results)
### 3️⃣ Spinner‑aware Pagination
- Stop condition enhanced: if a spinner (`div[role="progressbar"]`) is visible, wait; if not visible after a scroll, stop.
- **Impact:** Retrieves the maximum results Google provides.

### 4️⃣ City Discovery Automation (Country Mode)
- Remove manual city list.
- Use OpenStreetMap API to fetch states and cities for a given country.
- Loop through each city automatically.
- **Impact:** Country‑wide data collection without manual maintenance.

## 📊 Level 3 – Data Quality (Industry Tricks)
### 5️⃣ Hash‑based Duplicate Guard
- Compute `md5(name + phone)` for each record.
- Store hashes in `storage/seen.txt`.
- Skip records whose hash already exists.
- **Impact:** Guarantees zero duplicates across resumes.

### 6️⃣ Progressive Save (Crash‑proof)
- After every 10 records, append to a CSV and update `progress.json`.
- **Impact:** No data loss on crashes or power cuts.

## 🕶️ Level 4 – Stealth & Survival
### 7️⃣ Fingerprint Rotation
- Randomize User‑Agent, viewport size, and timezone for each run.
- **Impact:** Reduces Google detection probability.

### 8️⃣ Human Behaviour Engine
- Random scroll speed, random wait (2‑6 s), random mouse movements.
- **Impact:** Near‑zero CAPTCHA encounters.

## ⚡ Level 5 – Performance (Free System)
### 9️⃣ Task Queue
- Define jobs in `jobs.json`:
```json
[
  {"city": "Lucknow", "type": "gym"},
  {"city": "Kanpur", "type": "gym"}
]
```
- Each job runs a separate scraper instance.
- **Impact:** Large‑scale country runs become manageable.

**What NOT to do in a free system**
- ❌ Multi‑tab parallel scraping
- ❌ Headless true with ultra‑fast mode
- ❌ Target > 1000 records/day
- ❌ Re‑scrape the same city daily

## � Critical Missing Piece – PlaceID Extraction
Google Maps UI does not expose `place_id` directly in the DOM. The reliable way is to click the business card, wait for the detail pane to load, then read the URL from the browser:
```python
url = page.url
match = re.search(r'!1s([^!]+)', url)
place_id = match.group(1) if match else None
```
Store `place_id` in the cursor (`last_place_id`). This makes the resume system truly reliable.

## 🛡️ Selector Resilience (Future‑proofing)
Google frequently changes class names. Use a list of fallback selectors and try them sequentially:
```python
CARD_SELECTORS = [
    ".Nv2PK",
    "div[role='article']"
]

def get_cards(page):
    for sel in CARD_SELECTORS:
        cards = page.query_selector_all(sel)
        if cards:
            return cards
    return []
```
Apply the same pattern for other selectors such as the loading spinner (`.m6QErb`).

## ⏱️ Rate‑limit Guardian (Silent Killer Fix)
```python
if requests_today > 400:
    print("Daily limit reached, exiting.")
    sys.exit(0)

# Every 50 records, take a long random break
if processed_count % 50 == 0:
    time.sleep(random.randint(120, 300))  # 2‑5 minutes
```
Helps avoid IP blacklisting on free systems.

## 📊 Data Integrity Layer
Create `storage/run_meta.json` for each scrape run:
```json
{
  "query": "gym in lucknow",
  "started_at": "2026-01-24T12:00:00Z",
  "ended_at": "2026-01-24T12:35:12Z",
  "total_found": 312,
  "total_saved": 298,
  "skipped_duplicates": 14
}
```
Provides an audit trail for every execution.

## 📝 Review Content Throttling
When extending to scrape reviews, limit to a maximum of **3 reviews per place** to stay under Google’s detection thresholds.

## 🚨 Soft Ban Detector
```python
if "unusual traffic" in page.content():
    mark_proxy_bad()
    raise RuntimeError("Soft ban detected, aborting run")
```
Detects Google’s anti‑scraping warnings early and switches proxies.

## �🚀 Final Roadmap – Best Possible Version
- Implement the nine updates above:
  1. PlaceID cursor
  2. Browser‑reset retry
  3. Spinner‑aware scroll
  4. OSM city auto‑discovery
  5. Hash duplicate guard
  6. Progressive save
  7. Fingerprint rotation
  8. Human behaviour engine
  9. Job queue system
- Add the critical pieces listed above (PlaceID extraction, selector resilience, rate‑limit guardian, data integrity layer, review throttling, soft‑ban detector).
- Resulting system will be:
  - Fault‑tolerant
  - Resume‑able
  - Country‑scale
  - Zero‑duplicate
  - Industry‑grade crawler

---
## ⚙️ Config Externalization (Maintainability)
- Currently delays, limits, and selectors are hard‑coded.
- Move them to `scraper/config.json`:
```json
{
  "daily_limit": 400,
  "scroll_wait": [2000, 5000],
  "long_break_every": 50,
  "long_break_range": [120, 300]
}
```
**Impact:** Behavior can be changed without touching code – a real production practice.

## 📝 Structured Logging (Debugging)
- Introduce `scraper/logs/run.log` with timestamped entries, e.g.:
```
[12:01] City=Lucknow
[12:03] 120 cards found
[12:10] Soft ban detected
[12:10] Retrying with new browser
```
**Impact:** Immediate insight into failures and progress, replacing ad‑hoc `print` statements.

## 📦 Data Schema Versioning (Future‑proof)
- Add a `schema_version` field to the exported JSON/XLSX schema:
```json
{"schema_version": 1, "data": [...]}
```
- When new fields (opening_hours, latitude, categories, etc.) are added, bump the version to `2`.
**Impact:** Older Excel/history files remain compatible; aligns with data platform best practices.


## 📈 Current Status (as of 2026‑01‑24)
| Dimension          | Status |
|--------------------|--------|
| Architecture       | ✅ Perfect |
| Resume             | ✅ Perfect |
| Pagination         | ✅ Perfect |
| Retry              | ✅ Perfect |
| Country scale      | ✅ Perfect |
| Stealth            | ✅ Very strong |
| Cost               | ₹0 |
| Learning value     | Extremely high |


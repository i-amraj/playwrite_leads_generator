# 🏗️ Modular MVC File Structure Plan

यह दस्तावेज़ आपके प्रोजेक्ट के लिए एक **साफ, मॉड्यूलर और MVC (Model-View-Controller)** पैटर्न पर आधारित फ़ाइल स्ट्रक्चर को परिभाषित करता है।

इस स्ट्रक्चर का मुख्य उद्देश्य **Frontend (HTML)**, **Middleware/Controller (PHP)**, और **Core Logic (Python)** को पूरी तरह से अलग रखना है ताकि भविष्य में कोड को मैनेज करना आसान हो।

---

## 📂 Project Directory Tree

```
raj_leadar_generator_playwrite/
│
├── 📁 public/                  # [PUBLIC DATA] - स्टेटिक JSON फाइल्स (Frontend इसे fetch करेगा)
│   ├── locations.json          # 🌍 (User Provided) स्टेट और सिटी की लिस्ट
│   └── ...                     # अन्य पब्लिक डेटा
│
├── 📁 frontend/                # [VIEW] - यूज़र इंटरफ़ेस (UI)
│   ├── 📁 assets/
│   │   ├── 📁 css/
│   │   │   ├── style.css       # मुख्य स्टाइल
│   │   │   └── tailwind.css    # (यदि उपयोग करें)
│   │   └── 📁 js/
│   │       ├── app.js          # पेज लॉजिक (Event Listeners)
│   │       └── api_client.js   # API कॉल करने के लिए हेल्पर
│   ├── index.html              # मुख्य सर्च पेज
│   ├── settings.html           # सेटिंग्स पेज
│   └── history.html            # पुराना डेटा देखने का पेज
│
├── 📁 backend/                 # [CONTROLLER + MODEL]
│   │
│   ├── 📁 php/                 # [CONTROLLER] - API जो Frontend और Python को जोड़ता है
│   │   ├── 📁 api/
│   │   │   ├── search.php      # सर्च रिक्वेस्ट हैंडल करता है -> Python को कॉल करता है
│   │   │   ├── status.php      # प्रोग्रेस चेक करता है
│   │   │   ├── export.php      # Excel/CSV डाउनलोड हैंडल करता है
│   │   │   └── stop.php        # प्रोसेस रोकने के लिए
│   │   └── 📁 utils/
│   │       ├── response.php    # JSON रिस्पॉन्स स्टैंडर्ड फॉर्मेट
│   │       └── validator.php   # इनपुट वैलिडेशन
│   │
│   └── 📁 python/              # [MODEL] - मुख्य स्क्रैपिंग इंजन (Playwright Logic)
│       ├── 📁 core/            # कोर लॉजिक
│       │   ├── browser.py      # ब्राउज़र लॉन्च/क्लोज़ और सेटिंग्स
│       │   ├── search.py       # Google Maps सर्च लॉजिक
│       │   ├── extractor.py    # डेटा पार्सिंग (Name, Phone, Address)
│       │   └── stealth.py      # Stealth और Anti-detection लॉजिक
│       ├── 📁 config/          # सेटिंग्स
│       │   ├── settings.json   # टाइमआउट, हेडलेस मोड, आदि
│       │   └── selectors.json  # CSS क्लास नाम (Google अपडेट होने पर यहाँ बदलें)
│       ├── main.py             # एंट्री पॉइंट (PHP इसे कॉल करेगा)
│       └── requirements.txt    # Python लाइब्रेरी लिस्ट
│
├── 📁 data/                    # [DATABASE/STORAGE] - फाइल्स और डेटा
│   ├── 📁 exports/             # जनरेट की गई Excel/CSV फाइलें
│   ├── 📁 logs/                # डीबगिंग लॉग्स
│   │   ├── php_errors.log
│   │   └── scraper_run.log
│   ├── 📁 profiles/            # ब्राउज़र कुकीज़/प्रोफाइल (State save करने के लिए)
│   ├── progress.json           # Resume feature के लिए स्टेट फाइल
│   └── history.json            # पुराने सर्च का रिकॉर्ड
│
└── 📁 impliment_plans/         # [DOCS] - प्लानिंग और डॉक्यूमेंटेशन
    ├── FULL_WORKING_PLAN.md
    └── PROJECT_FILE_STRUCTURE.md  <-- (यह फाइल)
```

---

## 🏗️ MVC पैटर्न कैसे काम करेगा?

### 1. **M**odel (Backend - Python Layer)
*   **स्थान:** `backend/python/`
*   **काम:** असली काम (Business Logic) यहाँ होता है।
    *   ब्राउज़र खोलना।
    *   Google Maps से डेटा निकालना।
    *   डेटा को साफ़ (Clean) करना।
*   यह PHP या Frontend के बारे में कुछ नहीं जानता। यह बस इनपुट लेता है (Command Line Arguments) और आउटपुट देता है (JSON/Console)।

### 2. **V**iew (Frontend - HTML/JS Layer)
*   **स्थान:** `frontend/`
*   **काम:** यूज़र को दिखाना।
    *   सर्च फॉर्म और डेटा टेबल।
    *   PHP API को कॉल करना (`fetch()`).
    *   लोडिंग स्पिनर (Loading Spinner) दिखाना।
*   यहाँ कोई डेटाबेस लॉजिक या स्क्रैपिंग कोड नहीं होगा।

### 3. **C**ontroller (Backend - PHP Layer)
*   **स्थान:** `backend/php/`
*   **काम:** ट्रैफिक पुलिस (Traffic Police)।
    1.  Frontend से रिक्वेस्ट लेता है (`search.php`)।
    2.  चेक करता है कि डेटा सही है या नहीं।
    3.  Python स्क्रिप्ट (`main.py`) को कमांड देकर रन करता है।
    4.  Python से मिले रिजल्ट को JSON में बदलकर Frontend को वापस भेजता है।

---

## ⚙️ डेटा फ्लो का उदाहरण (Example Workflow)

1.  **User** `frontend/index.html` पर "Lucknow" लिखकर सर्च करता है।
2.  **JS** `backend/php/api/search.php` को रिक्वेस्ट भेजता है।
3.  **PHP** `backend/python/main.py --city Lucknow` कमांड चलाता है।
4.  **Python** ब्राउज़र खोलता है, डेटा स्क्रैप करता है, और JSON प्रिंट करता है।
5.  **PHP** उस JSON को पढ़ता है और वापस **JS** को भेजता है।
6.  **User** को स्क्रीन पर टेबल दिखाई देती है।

---

## 🔑 मुख्य लाभ (Key Benefits)
1.  **साफ-सुथरा (Clean):** अगर आपको डिज़ाइन बदलना है, तो सिर्फ `frontend` फोल्डर छेड़ें। अगर स्क्रैपिंग लॉजिक बदलना है, तो सिर्फ `backend/python`।
2.  **सुरक्षित (Secure):** Python डायरेक्ट इंटरनेट पर एक्सपोज़्ड नहीं है, वो सिर्फ PHP के माध्यम से चलता है।
3.  **आसान मेंटेनेंस (Maintainable):** सभी CSS, JS, और Config फाइल्स अपनी-अपनी जगह पर हैं।

यह स्ट्रक्चर आपके प्रोजेक्ट को प्रोफेशनल और स्केलेबल बनाएगा।

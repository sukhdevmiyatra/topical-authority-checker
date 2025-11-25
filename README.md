# 🚀 Topical Authority Checker

> **Calculate SEO market share and organic traffic potential for any topic using real-time SERP data**

A powerful Streamlit web application that analyzes keyword rankings and estimates domain authority within specific topic clusters. Built with the DataForSEO API for accurate, real-time search data.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Table of Contents

- [What is Topical Authority?](#what-is-topical-authority)
- [Features](#features)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [API Costs](#api-costs)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## 🎯 What is Topical Authority?

**Topical Authority** measures how well a domain dominates a specific topic or niche in organic search results. It's calculated by analyzing a domain's visibility across all relevant keywords within a topic cluster.

This tool helps you:
- **Identify market leaders** in your niche
- **Discover content gaps** and opportunities
- **Benchmark your SEO performance** against competitors
- **Estimate traffic potential** for topic clusters
- **Make data-driven content strategy** decisions

---

## ✨ Features

### 🔍 **Multi-Source Keyword Research**
- **Keywords for Keywords**: Semantically related terms from Google Ads
- **Keyword Ideas**: Broader topic suggestions from DataForSEO Labs
- **Google Autocomplete**: Real autocomplete suggestions for long-tail keywords
- **Smart Deduplication**: Automatically merges and deduplicates keywords across sources

### 🚫 **Advanced Filtering**
- **Negative Keywords**: Exclude irrelevant terms (e.g., "login", "free download", "crack")
- **Negative Domains**: Filter out specific competitors or high-authority sites (e.g., Wikipedia, Amazon)
- **Server-Side Filtering**: API-level filtering for cost efficiency
- **Client-Side Safety Net**: Fallback filtering for unsupported endpoints

### 🎛️ **Dynamic Analysis Controls**
- **Flexible Keyword Selection**: Analyze anywhere from 10 to 100% of fetched keywords
- **SERP Depth Options**: Choose between 10, 20, 50, or 100 organic results per keyword
- **Real-Time Cost Estimation**: See estimated API costs before running analysis
- **Cost Safeguards**: Set maximum spending limits to prevent overages

### ✏️ **Interactive Keyword Management**
- **Preview & Edit**: Review all fetched keywords before analysis
- **Manual Removal**: Checkbox-based keyword deletion
- **Volume Sorting**: Keywords automatically sorted by search volume
- **CSV Export**: Download keyword lists at any stage

### 📊 **Comprehensive Visualizations**
- **Market Share Chart**: Top 15 domains by traffic share (Altair interactive chart)
- **Concentration Metrics**: Top 3, Top 5, Top 10 market concentration
- **Market Type Classification**: Monopolistic, Concentrated, or Fragmented
- **Detailed Results Table**: Full breakdown with rankings and traffic estimates

### 💾 **Export Options**
- **Summary CSV**: Domain rankings, traffic, and market share
- **Detailed SERP CSV**: Keyword-level data with URLs, positions, CTR, and traffic
- **One-Click Downloads**: Base64-encoded instant downloads

### 🛡️ **Security & Privacy**
- **No Credential Storage**: API keys never logged or stored
- **Session-Only State**: Credentials cleared on app restart
- **Cost Protection**: Multiple safeguards against accidental overspending

---

## ⚙️ How It Works

### **Step 1: Keyword Discovery**
1. Enter seed keywords (comma-separated)
2. Select data sources (Keywords for Keywords, Keyword Ideas, Autocomplete)
3. Configure location and language targeting
4. Apply negative keyword filters
5. Fetch keywords from selected sources

### **Step 2: Keyword Refinement**
1. Review fetched keywords in interactive table
2. Manually remove irrelevant terms using checkboxes
3. Export keyword list if needed
4. Configure analysis settings (number of keywords, SERP depth)

### **Step 3: SERP Analysis**
1. App fetches real-time organic search results for each keyword
2. Extracts domain data from top ranking URLs
3. Applies negative domain filters
4. Calculates estimated traffic using industry-standard CTR curves:
   - **Position 1**: ~30% CTR
   - **Position 2**: ~15% CTR
   - **Position 3**: ~10% CTR
   - And so on...

### **Step 4: Market Share Calculation**
1. Aggregates total traffic per domain across all keywords
2. Calculates share: `Domain Share = Domain Traffic / Total Market Traffic`
3. Generates visualizations and detailed reports
4. Provides export options for further analysis

---

## 🚀 Installation

### **Prerequisites**
- Python 3.8 or higher
- DataForSEO API account ([Sign up here](https://dataforseo.com/) - $1 free trial)

### **Setup**

1. **Clone the repository**
   ```bash
   git clone https://github.com/sukhdevmiyatra/topical-authority-checker.git
   cd topical-authority-checker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   streamlit run app.py
   ```

4. **Open in browser**
   - The app will automatically open at `http://localhost:8501`
   - If not, navigate to the URL shown in your terminal

---

## 📖 Usage

### **Quick Start**

1. **Enter API Credentials**
   - Get your credentials from [DataForSEO API Access](https://app.dataforseo.com/api-access)
   - Enter your login and password in the sidebar
   - Verify connection (balance will be displayed)

2. **Configure Analysis**
   - Enter seed keywords (e.g., "ecommerce, online shopping")
   - Select location (2840 = US, 2826 = UK, 2356 = India)
   - Choose keyword sources
   - Set negative keywords/domains (optional)
   - Set maximum cost limit

3. **Fetch Keywords**
   - Click "🔍 Fetch Keywords"
   - Review results in the preview table
   - Remove unwanted keywords if needed

4. **Run SERP Analysis**
   - Configure keywords to analyze and SERP depth
   - Review estimated cost
   - Confirm and click "💸 Run SERP Analysis"

5. **Analyze Results**
   - View market share visualization
   - Review concentration metrics
   - Export data as CSV

---

## ⚙️ Configuration

### **Location Codes** (Common Examples)
- `2840` - United States
- `2826` - United Kingdom
- `2356` - India
- `2124` - Canada
- `2036` - Australia

[Full list of location codes](https://docs.dataforseo.com/v3/appendix/locations/)

### **Language Codes**
- `en` - English
- `es` - Spanish
- `fr` - French
- `de` - German
- `pt` - Portuguese

### **Default Negative Keywords**
```
google, login, sign up, sign in, free download, crack, torrent
```

### **Default Negative Domains**
```
wikipedia.org, amazon.com, youtube.com, pinterest.com, reddit.com
```

---

## 💰 API Costs

### **Keyword Data**
- **Keywords for Keywords**: ~$0.01 per 700 keywords
- **Keyword Ideas**: ~$0.01 per 700 keywords
- **Autocomplete**: ~$0.0002 per request

### **SERP Data**
- **10 results**: $0.0006 per keyword
- **20 results**: $0.0012 per keyword
- **50 results**: $0.0030 per keyword
- **100 results**: $0.0060 per keyword

### **Example Costs**
- Fetching 700 keywords from 2 sources: **$0.02**
- Analyzing 100 keywords (10 results each): **$0.06**
- **Total for typical analysis**: **$0.08 - $0.20**

---

## 📸 Screenshots

### Main Dashboard
![Dashboard](https://via.placeholder.com/800x400?text=Dashboard+Screenshot)

### Keyword Preview & Editing
![Keyword Preview](https://via.placeholder.com/800x400?text=Keyword+Preview+Screenshot)

### Market Share Visualization
![Market Share](https://via.placeholder.com/800x400?text=Market+Share+Chart)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📧 Contact

**Sukhdev Miyatra**

- 🔗 LinkedIn: [linkedin.com/in/sukhdevmiyatra](https://www.linkedin.com/in/sukhdevmiyatra/)
- 🐦 Twitter/X: [@miyatrasukhdev](https://x.com/miyatrasukhdev)
- ✉️ Email: sukhdevmiyatra2@gmail.com
- 💻 GitHub: [@sukhdevmiyatra](https://github.com/sukhdevmiyatra)

---

## 🙏 Acknowledgments

- **DataForSEO** for providing the API infrastructure
- **Streamlit** for the amazing web framework
- **Altair** for beautiful data visualizations

---

## ⚠️ Disclaimer

This tool provides **estimated** traffic data based on industry-standard CTR curves. Actual traffic may vary based on:
- Brand searches
- Featured snippets and SERP features
- Seasonal trends
- User intent variations

Use this tool for **relative comparisons** and **strategic insights**, not absolute traffic predictions.

---

**Built with ❤️ by Sukhdev Miyatra**

import streamlit as st
import pandas as pd
import requests
import altair as alt
import base64
import time
import math

# ==========================================
# SEO & PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Topic Authority Checker - SEO Market Share Calculator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Topic Authority Engine - Calculate organic market share and traffic potential using DataForSEO API."
    }
)

# Custom CSS for Premium UI
st.markdown("""
<style>
    /* Main Container */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Cards */
    .card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-left: 3px solid #FF4B4B;
    }
    
    /* Metrics */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }
    
    /* Headers */
    h1 { 
        color: #1a1a1a; 
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    h2 { 
        color: #2d2d2d;
        font-weight: 600;
        font-size: 1.3rem;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    h3 { 
        color: #2d2d2d;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Buttons */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 2px solid #f0f0f0;
    }
    
    /* Cost Badge */
    .cost-badge {
        background-color: #667eea;
        color: white;
        padding: 8px 15px;
        border-radius: 6px;
        display: inline-block;
        font-weight: 600;
        font-size: 14px;
        margin: 5px 0;
    }
    
    /* Success Messages */
    .success-msg {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# SEO Meta Tags (for when deployed)
st.markdown("""
<meta name="description" content="Calculate SEO market share and organic traffic potential for any topic using DataForSEO API. Analyze keyword rankings, SERP data, and competitor traffic share.">
<meta name="keywords" content="SEO, market share, topic authority, SERP analysis, keyword research, organic traffic, DataForSEO">
<meta name="author" content="Sukhdev Miyatra">
<meta property="og:title" content="Topic Authority Score Checker - SEO Market Share Calculator">
<meta property="og:description" content="Calculate organic market share and traffic potential for any topic using real SERP data.">
<meta property="og:type" content="website">
""", unsafe_allow_html=True)

API_BASE_URL = "https://api.dataforseo.com/v3"

# Standard CTR Curve (Position 1-20)
CTR_CURVE = {
    1: 0.30, 2: 0.15, 3: 0.10, 4: 0.06, 5: 0.04,
    6: 0.03, 7: 0.025, 8: 0.02, 9: 0.015, 10: 0.01,
    11: 0.009, 12: 0.008, 13: 0.007, 14: 0.006, 15: 0.005,
    16: 0.004, 17: 0.003, 18: 0.002, 19: 0.001, 20: 0.001
}

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_auth(username, password):
    """Returns auth tuple without storing globally."""
    if not username or not password:
        return None
    return (username, password)

def fetch_balance(auth):
    """Fetches current API balance."""
    try:
        response = requests.get(f"{API_BASE_URL}/appendix/user_data", auth=auth)
        if response.status_code == 200:
            data = response.json()
            return data['tasks'][0]['result'][0]['money']['balance']
    except:
        pass
    return None

def estimate_total_cost(num_keywords_to_fetch, num_keywords_to_analyze, serp_depth):
    """Calculates total estimated cost for the entire operation."""
    # Keyword fetch cost: $0.01 per 700 keywords
    keyword_requests = math.ceil(num_keywords_to_fetch / 700)
    keyword_cost = keyword_requests * 0.01
    
    # SERP cost: $0.0006 base (for 10 results) * multiplier
    serp_multiplier = serp_depth / 10
    serp_cost_per_kw = 0.0006 * serp_multiplier
    total_serp_cost = num_keywords_to_analyze * serp_cost_per_kw
    
    total = keyword_cost + total_serp_cost
    
    return {
        'keyword_cost': keyword_cost,
        'serp_cost': total_serp_cost,
        'serp_cost_per_kw': serp_cost_per_kw,
        'total': total
    }

def build_filters(negatives):
    """Constructs DataForSEO filter array for negative keywords."""
    if not negatives:
        return None
    
    filters = []
    for i, neg in enumerate(negatives):
        filters.append(["keyword", "not_like", f"%{neg}%"])
        if i < len(negatives) - 1:
            filters.append("and")
            
    # If only one filter, return it directly
    if len(negatives) == 1:
        return filters[0]
    return filters

def fetch_keywords_data(seed_keyword, location, language, limit, auth, negatives=None):
    """Fetches related keywords from DataForSEO with filtering."""
    endpoint = f"{API_BASE_URL}/keywords_data/google_ads/keywords_for_keywords/live"
    
    task = {
        "keywords": [seed_keyword],
        "location_code": int(location),
        "language_code": language,
        "sort_by": "search_volume",
        "limit": limit
    }
    
    # Add filters if negatives exist
    api_filters = build_filters(negatives)
    if api_filters:
        task["filters"] = api_filters
        
    payload = [task]
    
    try:
        response = requests.post(endpoint, json=payload, auth=auth)
        response.raise_for_status()
        data = response.json()
        
        if 'tasks' in data and data['tasks'] and data['tasks'][0]['result']:
            return data['tasks'][0]['result']
    except Exception as e:
        st.error(f"❌ API Error (Keywords for Keywords): {str(e)}")
    return []

def fetch_keyword_ideas(seed_keyword, location, language, limit, auth, negatives=None):
    """Fetches keyword ideas from DataForSEO Labs with filtering."""
    endpoint = f"{API_BASE_URL}/dataforseo_labs/google/keyword_ideas/live"
    
    task = {
        "keywords": [seed_keyword],
        "location_code": int(location),
        "language_code": language,
        "include_seed_keyword": True,
        "include_serp_info": False,
        "limit": limit
    }
    
    # Add filters if negatives exist
    api_filters = build_filters(negatives)
    if api_filters:
        task["filters"] = api_filters
        
    payload = [task]
    
    try:
        response = requests.post(endpoint, json=payload, auth=auth)
        response.raise_for_status()
        data = response.json()
        
        if 'tasks' in data and data['tasks'] and data['tasks'][0]['result']:
            # DataForSEO Labs returns items in a different structure
            items = data['tasks'][0]['result'][0].get('items', [])
            # Convert to same format as keywords_for_keywords
            result = []
            for item in items:
                result.append({
                    'keyword': item.get('keyword'),
                    'search_volume': item.get('keyword_info', {}).get('search_volume', 0)
                })
            return result
    except Exception as e:
        st.error(f"❌ API Error (Keyword Ideas): {str(e)}")
    return []

def fetch_autocomplete(seed_keyword, location, language, auth):
    """Fetches autocomplete suggestions from DataForSEO."""
    endpoint = f"{API_BASE_URL}/keywords_data/google/autocomplete/live"
    payload = [{
        "keyword": seed_keyword,
        "location_code": int(location),
        "language_code": language
    }]
    
    try:
        response = requests.post(endpoint, json=payload, auth=auth)
        response.raise_for_status()
        data = response.json()
        
        if 'tasks' in data and data['tasks'] and data['tasks'][0]['result']:
            # Autocomplete returns items without search volume, we'll need to get that separately
            # For now, return the keywords and we'll filter by volume later
            return data['tasks'][0]['result']
    except Exception as e:
        st.error(f"❌ API Error (Autocomplete): {str(e)}")
    return []

def fetch_serp_batch(keywords, location, language, depth, auth):
    """Fetches SERP data for a batch of keywords."""
    endpoint = f"{API_BASE_URL}/serp/google/organic/live/advanced"
    payload = []
    for kw in keywords:
        payload.append({
            "keyword": kw,
            "location_code": int(location),
            "language_code": language,
            "depth": depth
        })
    
    try:
        response = requests.post(endpoint, json=payload, auth=auth)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"❌ API Error: {str(e)}")
    return None

# ==========================================
# MAIN APP
# ==========================================

def main():
    # --- H1 FIRST (for proper HTML hierarchy) ---
    st.title("Topic Authority Score Checker - SEO Market Share Calculator")
    
    # --- SIDEBAR: Authentication ---
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/rocket.png", width=80)
        
        st.markdown("**🔐 DataForSEO API Credentials**")
        st.caption("Get your API credentials at [DataForSEO API Access](https://app.dataforseo.com/api-access)")
        
        # Use session state values if available to ensure persistence
        default_user = st.session_state.get('user', '')
        default_pass = st.session_state.get('pass', '')
        
        dfs_user = st.text_input("API Login", type="password", value=default_user, key="user_input", placeholder="your-email@example.com")
        dfs_pass = st.text_input("API Password", type="password", value=default_pass, key="pass_input")
        
        # Update session state with input values
        if dfs_user: st.session_state['user'] = dfs_user
        if dfs_pass: st.session_state['pass'] = dfs_pass
        
        auth = get_auth(dfs_user, dfs_pass)
        
        if auth:
            balance = fetch_balance(auth)
            if balance is not None:
                st.success(f"✅ Connected")
                st.metric("💰 API Balance", f"${balance:.2f}")
            else:
                st.error("❌ Invalid credentials")
        else:
            st.info("🔒 Enter credentials to start. We do not store or log your API credentials.")
        
        st.divider()
        
        # Contact & Source Code (side by side)
        st.markdown("**👤 Contact & Social**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <a href="https://www.linkedin.com/in/sukhdevmiyatra/" target="_blank" style="
                display: inline-block;
                padding: 8px;
                background-color: #0077B5;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: 600;
                text-align: center;
                width: 100%;
                font-size: 12px;
                margin-bottom: 5px;
            ">
                🔗 LinkedIn
            </a>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <a href="mailto:sukhdevmiyatra2@gmail.com" style="
                display: inline-block;
                padding: 8px;
                background-color: #EA4335;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: 600;
                text-align: center;
                width: 100%;
                font-size: 12px;
            ">
                ✉️ Email
            </a>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <a href="https://github.com/sukhdevmiyatra/topic-authority" target="_blank" style="
                display: inline-block;
                padding: 8px;
                background-color: #24292e;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: 600;
                text-align: center;
                width: 100%;
                font-size: 12px;
                margin-bottom: 5px;
            ">
                ⭐ Source Code
            </a>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <a href="https://x.com/miyatrasukhdev" target="_blank" style="
                display: inline-block;
                padding: 8px;
                background-color: #000000;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: 600;
                text-align: center;
                width: 100%;
                font-size: 12px;
            ">
                𝕏 Twitter/X
            </a>
            """, unsafe_allow_html=True)

    # --- MAIN CONTENT ---
    

    
    # Help Box - Explanation
    with st.expander("ℹ️ What is Topic Authority & How Does This Work?", expanded=False):
        st.markdown("""
        ## What is Topic Authority?
        
        **Topic Authority** measures how well a domain dominates a specific topic or niche in organic search results. 
        It's calculated by analyzing a domain's visibility across all relevant keywords within a topic cluster.
        
        ### How This Calculator Works:
        
        **Step 1: Keyword Discovery**
        - We fetch related keywords for your seed topic using Google Ads data
        - Filter keywords by search volume (minimum 10 searches/month)
        - Sort by relevance and volume
        
        **Step 2: SERP Analysis**
        - Fetch real-time organic search results for each keyword
        - Analyze ranking positions (top 10-100 results)
        - Extract domain data from each ranking URL
        
        **Step 3: Traffic Estimation**
        - Apply Click-Through-Rate (CTR) curves based on position
        - Calculate estimated traffic: `Traffic = Search Volume × CTR`
        - Position 1 ≈ 30% CTR, Position 2 ≈ 15% CTR, etc.
        
        **Step 4: Market Share Calculation**
        - Aggregate total traffic per domain across all keywords
        - Calculate share: `Domain Share = Domain Traffic / Total Market Traffic`
        
        ### Use Cases:
        - **Competitive Analysis**: See who dominates your niche
        - **Market Opportunity**: Identify underserved topics
        - **Content Strategy**: Understand traffic potential
        - **SEO Benchmarking**: Track your domain's authority over time
        
        ### Accuracy Notes:
        - Traffic estimates use industry-standard CTR curves
        - Actual traffic may vary based on brand searches, featured snippets, etc.
        - Best used for relative comparisons, not absolute traffic numbers
        
        ---
        
        ### Data Source: DataForSEO API
        
        This tool uses the **[DataForSEO API](https://dataforseo.com/)** to fetch keyword and SERP data.
        
        **Why DataForSEO?**
        - Real-time organic search results from Google
        - Comprehensive keyword data from Google Ads
        - High accuracy and reliability
        - Location and language-specific targeting
        
        **API Costs:**
        - Keyword data: ~$0.01 per request (up to 700 keywords)
        - SERP data: ~$0.0006 per keyword (10 results)
        
        **Getting Started:**
        1. Sign up for free at [DataForSEO.com](https://dataforseo.com/)
        2. Get $1 free trial credit
        3. No credit card required for trial
        4. Pay-as-you-go pricing
        
        *This app does not store or share your API credentials.*
        """)
    
    if not auth:
        st.warning("⚠️ Please enter your DataForSEO credentials in the sidebar to begin.")
        st.info("""
        **How it works:**
        1. Enter your DataForSEO API credentials
        2. Configure your research parameters
        3. Fetch keyword data for your topic
        4. Analyze SERP rankings and calculate traffic share
        5. Export results and visualizations
        """)
        return
    
    st.divider()
    
    # --- STEP 1: Configuration ---
    st.markdown("## 1️⃣ Configuration")
    
    with st.expander("⚙️ Configure Analysis Parameters", expanded=True):
        
        # Section 1: Topic Input
        st.markdown("### 🎯 Topic & Keywords")
        seed_keyword = st.text_area(
            "Seed Keywords (comma-separated)", 
            value="ecommerce", 
            height=90,
            help="Enter one or more keywords separated by commas. Duplicates are automatically removed.",
            placeholder="e.g., ecommerce, online shopping, e-commerce"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            location_code = st.number_input("🌍 Location Code", value=2840, help="2840 = US, 2826 = UK, 2356 = India")
        with col2:
            language_code = st.text_input("🗣️ Language", value="en", help="en = English, es = Spanish, fr = French")
        
        # Negative Keywords & Domains
        col_neg1, col_neg2 = st.columns(2)
        
        with col_neg1:
            st.markdown("**🚫 Negative Keywords**")
            negative_keywords = st.text_area(
                "Exclude keywords (comma-separated)",
                value="google, login, sign up, sign in, free download, crack, torrent",
                height=100,
                help="Keywords containing these words will be removed.",
                label_visibility="collapsed",
                key="neg_kw"
            )
            
        with col_neg2:
            st.markdown("**🚫 Negative Domains**")
            negative_domains = st.text_area(
                "Exclude domains (comma-separated)",
                value="wikipedia.org, amazon.com, youtube.com, pinterest.com, reddit.com",
                height=100,
                help="These domains will be excluded from the final report.",
                label_visibility="collapsed",
                key="neg_dom"
            )
        
        st.markdown("---")
        
        # Section 2: Data Sources

        st.markdown("### 📊 Keyword Data Sources")
        st.caption("Select one or more sources. More sources = broader keyword coverage. **All keywords are merged and duplicates removed.**")
        
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1.2])
        
        with col1:
            use_keywords_for_keywords = st.checkbox(
                "**Keywords for Keywords**", 
                value=True,
                help="Fetches related keywords from Google Ads. Best for finding semantically related terms."
            )
            st.caption("💰 $0.01/700 kw")
        
        with col2:
            use_keyword_ideas = st.checkbox(
                "**Keyword Ideas**", 
                value=False,
                help="Broader keyword suggestions from Google Ads. Best for discovering new topic areas."
            )
            st.caption("💰 $0.01/700 kw")
        
        with col3:
            use_autocomplete = st.checkbox(
                "**Autocomplete**", 
                value=False,
                help="Real Google autocomplete suggestions. Best for long-tail and question-based keywords."
            )
            st.caption("💰 $0.0002/req")
        
        with col4:
            num_keywords_fetch = st.select_slider(
                "Keywords per source",
                options=[100, 300, 500, 700, 1000],
                value=700,
                help="How many keywords to fetch from EACH selected source. Total keywords = (sources × this number) minus duplicates."
            )
        
        st.markdown("---")
        
        # Section 3: Safety Settings
        st.markdown("### 🛡️ Safety Settings")
        
        max_cost = st.number_input(
            "Max Cost Limit ($)",
            min_value=0.0,
            max_value=100.0,
            value=5.0,
            step=0.5,
            help="Analysis will be blocked if estimated cost exceeds this amount"
        )
        
        # Cost Estimate - calculate based on selected sources
        selected_sources = sum([use_keywords_for_keywords, use_keyword_ideas, use_autocomplete])
        
        # Calculate keyword fetch costs
        keyword_cost = 0
        if use_keywords_for_keywords:
            keyword_cost += math.ceil(num_keywords_fetch / 700) * 0.01
        if use_keyword_ideas:
            keyword_cost += math.ceil(num_keywords_fetch / 700) * 0.01
        if use_autocomplete:
            keyword_cost += 0.0002 * len([kw.strip() for kw in seed_keyword.split(',') if kw.strip()])
        
        costs = {
            'keyword_cost': keyword_cost,
            'total': keyword_cost
        }
        
        # Cost Summary
        st.markdown("---")
        
        cost_col1, cost_col2, cost_col3 = st.columns(3)
        
        with cost_col1:
            st.metric("💰 Keyword Cost", f"${costs['keyword_cost']:.4f}")
        with cost_col2:
            st.metric("💰 **Total Cost**", f"${costs['total']:.4f}")
        with cost_col3:
            if costs['total'] > max_cost:
                st.metric("Status", "🚫 BLOCKED", delta="Over limit")
            else:
                st.metric("Status", "✅ Ready", delta="Within limit")
        
        if costs['total'] > max_cost:
            st.error(f"⚠️ Cost (${costs['total']:.4f}) exceeds limit (${max_cost:.2f}).")
    
    # Store config in session
    st.session_state['config'] = {
        'seed': seed_keyword,
        'location': location_code,
        'language': language_code,
        'fetch_limit': num_keywords_fetch,
        'max_cost': max_cost
    }
    
    st.divider()
    
    # --- STEP 2: Fetch Keywords ---
    st.markdown("## 2️⃣ Keyword Research")
    
    # Validate at least one source is selected
    if not any([use_keywords_for_keywords, use_keyword_ideas, use_autocomplete]):
        st.warning("⚠️ Please select at least one keyword source in Configuration.")
    
    if st.button(f"🔍 Fetch Keywords", type="primary", use_container_width=True):
        # Parse seed keywords
        seed_keywords = [kw.strip() for kw in seed_keyword.split(',') if kw.strip()]
        
        # Parse negative keywords
        negatives = [kw.strip().lower() for kw in negative_keywords.split(',') if kw.strip()]
        
        if not seed_keywords:
            st.error("Please enter at least one seed keyword.")
        elif not any([use_keywords_for_keywords, use_keyword_ideas, use_autocomplete]):
            st.error("Please select at least one keyword source.")
        else:
            with st.spinner(f"Fetching keywords from {selected_sources} source(s) for {len(seed_keywords)} seed keyword(s)..."):
                all_keywords = {}  # Use dict to deduplicate by keyword
                
                for idx, kw in enumerate(seed_keywords, 1):
                    st.caption(f"📍 Processing seed keyword {idx}/{len(seed_keywords)}: '{kw}'")
                    
                    # Helper to check negatives
                    def is_clean(text):
                        text = text.lower()
                        for neg in negatives:
                            if neg in text: # Partial match (e.g. 'google' matches 'google search')
                                return False
                        return True
                    
                    # Fetch from Keywords for Keywords
                    if use_keywords_for_keywords:
                        st.caption(f"  ↳ Fetching from Keywords for Keywords...")
                        # Pass negatives to API for server-side filtering
                        raw_data = fetch_keywords_data(kw, location_code, language_code, num_keywords_fetch, auth, negatives)
                        
                        if raw_data:
                            for item in raw_data:
                                keyword_text = item.get('keyword')
                                vol = item.get('search_volume', 0)
                                
                                # Still check is_clean as a safety net (and for autocomplete)
                                if vol and vol >= 10 and is_clean(keyword_text):
                                    if keyword_text not in all_keywords or vol > all_keywords[keyword_text]:
                                        all_keywords[keyword_text] = vol
                    
                    # Fetch from Keyword Ideas
                    if use_keyword_ideas:
                        st.caption(f"  ↳ Fetching from Keyword Ideas...")
                        # Pass negatives to API for server-side filtering
                        raw_data = fetch_keyword_ideas(kw, location_code, language_code, num_keywords_fetch, auth, negatives)
                        
                        if raw_data:
                            for item in raw_data:
                                keyword_text = item.get('keyword')
                                vol = item.get('search_volume', 0)
                                
                                if vol and vol >= 10 and is_clean(keyword_text):
                                    if keyword_text not in all_keywords or vol > all_keywords[keyword_text]:
                                        all_keywords[keyword_text] = vol
                    
                    # Fetch from Autocomplete
                    if use_autocomplete:
                        st.caption(f"  ↳ Fetching from Autocomplete...")
                        raw_data = fetch_autocomplete(kw, location_code, language_code, auth)
                        
                        if raw_data:
                            # Autocomplete returns just keywords, we need to add them to a list to get volumes
                            autocomplete_keywords = []
                            for item in raw_data:
                                if isinstance(item, dict) and 'keyword' in item:
                                    autocomplete_keywords.append(item['keyword'])
                                elif isinstance(item, str):
                                    autocomplete_keywords.append(item)
                            
                            # For autocomplete, we'll add them with volume 0 for now
                            for kw_text in autocomplete_keywords:
                                if kw_text and kw_text not in all_keywords and is_clean(kw_text):
                                    all_keywords[kw_text] = 0  # Placeholder, would need volume lookup
                
                if all_keywords:
                    # Convert to dataframe
                    # Keep keywords with volume >= 10 OR if they are from autocomplete (volume 0 but relevant)
                    # We'll treat 0 volume as "Unknown" in the UI
                    df = pd.DataFrame([
                        {'keyword': k, 'search_volume': v} 
                        for k, v in all_keywords.items()
                        if v >= 10 or (v == 0 and use_autocomplete)
                    ]).sort_values('search_volume', ascending=False)
                    
                    st.session_state['keywords_df'] = df
                    st.session_state['serp_results'] = None  # Reset
                    
                    sources_used = []
                    if use_keywords_for_keywords:
                        sources_used.append("Keywords for Keywords")
                    if use_keyword_ideas:
                        sources_used.append("Keyword Ideas")
                    if use_autocomplete:
                        sources_used.append("Autocomplete")
                    
                    st.success(f"✅ Found {len(df)} unique keywords from {len(seed_keywords)} seed(s) using: {', '.join(sources_used)}")
                else:
                    st.warning("No keywords found with volume ≥ 10")
    
    # --- STEP 3: Show Keywords & Confirm Analysis ---
    if st.session_state.get('keywords_df') is not None:
        df = st.session_state['keywords_df']
        config = st.session_state['config']
        
        st.divider()
        st.markdown("## 3️⃣ Configure & Run Analysis")
        
        # --- Dynamic Analysis Settings ---
        st.markdown("### ⚙️ Analysis Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            total_keywords = len(df)
            num_keywords_analyze = st.slider(
                "🔍 Keywords to Analyze",
                min_value=10,
                max_value=total_keywords,
                value=min(100, total_keywords),
                step=10,
                help=f"Select how many keywords to analyze (Max: {total_keywords})"
            )
            st.caption(f"Analyzing top {num_keywords_analyze} keywords by volume")
            
        with col2:
            serp_depth = st.select_slider(
                "📈 SERP Depth",
                options=[10, 20, 50, 100],
                value=10,
                help="Number of organic results to analyze per keyword"
            )
            st.caption(f"Analyzing positions 1-{serp_depth}")
            
        # Calculate SERP Cost
        serp_multiplier = serp_depth / 10
        serp_cost_per_kw = 0.0006 * serp_multiplier
        total_serp_cost = num_keywords_analyze * serp_cost_per_kw
        max_cost = config.get('max_cost', 5.0)
        
        # Compact Metrics
        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📋 Total Keywords", len(df))
        m2.metric("📊 Avg Volume", f"{int(df['search_volume'].mean()):,}")
        m3.metric("🎯 Analyzing", num_keywords_analyze)
        
        if total_serp_cost > max_cost:
            m4.metric("💰 SERP Cost", f"${total_serp_cost:.4f}", delta="Over Limit", delta_color="inverse")
        else:
            m4.metric("💰 SERP Cost", f"${total_serp_cost:.4f}", delta="Ready")
        
        # Preview & Edit
        with st.expander("📄 Preview & Edit Keyword List", expanded=True):
            st.caption("Select keywords to remove from analysis (e.g. irrelevant terms).")
            
            # Add 'Remove' column for selection
            if 'Remove' not in df.columns:
                df['Remove'] = False
                
            # Reorder columns to put Remove first
            cols = ['Remove'] + [c for c in df.columns if c != 'Remove']
            
            edited_df = st.data_editor(
                df[cols],
                column_config={
                    "Remove": st.column_config.CheckboxColumn(
                        "Remove?",
                        help="Check to remove this keyword",
                        default=False,
                    ),
                    "search_volume": st.column_config.NumberColumn(
                        "Volume",
                        format="%d",
                    ),
                    "keyword": st.column_config.TextColumn(
                        "Keyword",
                        width="large",
                    )
                },
                disabled=["keyword", "search_volume"],
                hide_index=True,
                use_container_width=True,
                height=400
            )
            
            col_del, col_exp = st.columns([1, 1])
            
            with col_del:
                if st.button("🗑️ Delete Selected Keywords", type="secondary", use_container_width=True):
                    # Filter out removed rows
                    rows_to_keep = edited_df[~edited_df['Remove']]
                    
                    # Drop the Remove column for storage
                    clean_df = rows_to_keep.drop(columns=['Remove'])
                    
                    # Update session state
                    st.session_state['keywords_df'] = clean_df
                    st.success(f"✅ Removed {len(df) - len(clean_df)} keywords!")
                    st.rerun()
            
            with col_exp:
                # Export Keywords
                keyword_csv = df.drop(columns=['Remove'], errors='ignore').to_csv(index=False)
                keyword_b64 = base64.b64encode(keyword_csv.encode()).decode()
                st.markdown(f"""
                <a href="data:file/csv;base64,{keyword_b64}" download="keywords_{config['seed']}.csv" style="
                    display: inline-block;
                    padding: 8px 16px;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: 600;
                    font-size: 14px;
                    width: 100%;
                    text-align: center;
                ">
                    📥 Download CSV
                </a>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # --- Run Analysis Button ---
        
        # Cost check
        if total_serp_cost > max_cost:
            st.error(f"🚫 **Analysis Blocked!** Cost (${total_serp_cost:.4f}) exceeds limit (${max_cost:.2f}). Reduce keywords/depth or increase limit in Config.")
        else:
            # Confirmation checkbox
            confirm = st.checkbox(f"✅ I confirm spending ${total_serp_cost:.4f} to analyze SERPs", key="confirm_serp")
            
            if st.button("💸 Run SERP Analysis", type="primary", use_container_width=True, disabled=not confirm):
                # Prepare
                target_df = df.head(num_keywords_analyze)
                keywords_list = target_df['keyword'].tolist()
                volume_map = dict(zip(target_df['keyword'], target_df['search_volume']))
                
                # Parse negative domains
                neg_doms = [d.strip().lower() for d in negative_domains.split(',') if d.strip()]
                
                all_domain_traffic = {}
                total_market_traffic = 0
                detailed_serp_data = []  # Store detailed SERP data for export
                
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                batch_size = 50
                total_batches = math.ceil(len(keywords_list) / batch_size)
                
                # Fetch SERPs
                for i in range(0, len(keywords_list), batch_size):
                    batch = keywords_list[i:i+batch_size]
                    batch_num = (i // batch_size) + 1
                    
                    status_text.text(f"🔄 Processing batch {batch_num}/{total_batches} ({len(batch)} keywords)...")
                    
                    serp_data = fetch_serp_batch(
                        batch,
                        config['location'],
                        config['language'],
                        serp_depth,
                        auth
                    )
                    
                    if serp_data and 'tasks' in serp_data:
                        for task in serp_data['tasks']:
                            if task['result']:
                                result = task['result'][0]
                                keyword = result['keyword']
                                volume = volume_map.get(keyword, 0)
                                
                                for item in result['items']:
                                    if item['type'] == 'organic':
                                        domain = item['domain']
                                        
                                        # Domain Filter: Skip if domain matches any negative domain
                                        # Strict check: exact match OR ends with .domain (subdomain)
                                        is_excluded = False
                                        for nd in neg_doms:
                                            if domain == nd or domain.endswith("." + nd):
                                                is_excluded = True
                                                break
                                        
                                        if is_excluded:
                                            continue
                                            
                                        rank = item['rank_group']
                                        url = item.get('url', '')
                                        title = item.get('title', '')
                                        ctr = CTR_CURVE.get(rank, 0)
                                        traffic = volume * ctr
                                        
                                        # Store detailed data
                                        detailed_serp_data.append({
                                            'keyword': keyword,
                                            'search_volume': volume,
                                            'domain': domain,
                                            'url': url,
                                            'title': title,
                                            'position': rank,
                                            'ctr': ctr,
                                            'estimated_traffic': traffic
                                        })
                                        
                                        all_domain_traffic[domain] = all_domain_traffic.get(domain, 0) + traffic
                                        total_market_traffic += traffic
                    
                    progress_bar.progress(min((i + len(batch)) / len(keywords_list), 1.0))
                    time.sleep(0.1)  # Rate limiting
                
                # Store results
                st.session_state['serp_results'] = all_domain_traffic
                st.session_state['total_traffic'] = total_market_traffic
                st.session_state['detailed_serp_data'] = detailed_serp_data  # Store for export
                
                status_text.success("✅ Analysis complete!")
                st.rerun()
    
    # --- STEP 5: Results & Visualization ---
    if st.session_state.get('serp_results'):
        st.divider()
        st.markdown("## 4️⃣ Results & Insights")
        
        traffic_data = st.session_state['serp_results']
        total_traffic = st.session_state['total_traffic']
        
        # Build results dataframe
        results_df = pd.DataFrame(
            list(traffic_data.items()),
            columns=['Domain', 'Estimated Traffic']
        )
        results_df['Share of Voice (%)'] = (results_df['Estimated Traffic'] / total_traffic) * 100
        results_df = results_df.sort_values('Estimated Traffic', ascending=False).reset_index(drop=True)
        results_df['Rank'] = range(1, len(results_df) + 1)
        results_df = results_df[['Rank', 'Domain', 'Estimated Traffic', 'Share of Voice (%)']]
        
        # Top Metrics
        winner = results_df.iloc[0]
        top5_share = results_df.head(5)['Share of Voice (%)'].sum()
        
        st.info("📊 **Important**: Traffic estimates shown below are for **this topic cluster only** (the keywords analyzed), not the domain's entire traffic.")
        
        st.markdown("")  # Spacing
        
        k1, k2, k3, k4, k5 = st.columns([1.5, 1, 1, 1, 1])  # Make first column wider
        k1.metric("🏆 Market Leader", winner['Domain'], help="Domain with highest estimated traffic")
        k2.metric("📈 Leader Traffic", f"{int(winner['Estimated Traffic']):,}", help="Estimated monthly traffic from these keywords only")
        k3.metric("📊 Leader Share", f"{winner['Share of Voice (%)']:.2f}%", help="% of total topic traffic")
        k4.metric("🌐 Total Domains", len(results_df), help="Unique domains ranking")
        k5.metric("🔝 Top 5 Share", f"{top5_share:.1f}%", help="Combined share of top 5 domains")
        
        st.markdown("")  # Spacing
        
        # Visualization
        st.markdown("### 📊 Market Share Visualization")
        
        # Prepare data for chart (clean names)
        chart_df = results_df.head(15).copy()
        chart_df['Share'] = chart_df['Share of Voice (%)']
        chart_df['Traffic'] = chart_df['Estimated Traffic']
        
        # Create the chart with explicit sorting
        chart = alt.Chart(chart_df).mark_bar(
            cornerRadiusTopRight=5,
            cornerRadiusBottomRight=5
        ).encode(
            x=alt.X('Share:Q', title='Share of Voice (%)'),
            y=alt.Y('Domain:N', sort='-x', title='Domain'),
            color=alt.Color(
                'Share:Q',
                scale=alt.Scale(scheme='blues'),
                legend=None
            ),
            tooltip=[
                alt.Tooltip('Domain:N', title='Domain'),
                alt.Tooltip('Traffic:Q', format=',.0f', title='Est. Traffic'),
                alt.Tooltip('Share:Q', format='.2f', title='Share %')
            ]
        ).properties(
            height=max(400, len(chart_df) * 30), # Dynamic height
            title='Top 15 Domains by Market Share'
        ).configure_title(
            fontSize=18,
            font='Inter',
            anchor='start'
        )
        
        st.altair_chart(chart, use_container_width=True)
        
        # Market Concentration Analysis
        st.markdown("### 📈 Market Concentration Analysis")
        
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown("**Top 3 Concentration**")
            top3 = results_df.head(3)['Share of Voice (%)'].sum()
            st.metric("Top 3 Share", f"{top3:.1f}%", help="Combined market share of top 3 domains", label_visibility="collapsed")
        
        with c2:
            st.markdown("**Top 10 Concentration**")
            top10 = results_df.head(10)['Share of Voice (%)'].sum()
            st.metric("Top 10 Share", f"{top10:.1f}%", help="Combined market share of top 10 domains", label_visibility="collapsed")
        
        with c3:
            st.markdown("**Market Type**")
            if top3 > 75:
                market_type = "Monopolistic"
                help_text = "Top 3 control >75% - highly concentrated market"
            elif top3 > 50:
                market_type = "Concentrated"
                help_text = "Top 3 control >50% - moderately concentrated"
            else:
                market_type = "Fragmented"
                help_text = "Top 3 control <50% - competitive, fragmented market"
            st.metric("Market Type", market_type, help=help_text, label_visibility="collapsed")
        
        # Data Table
        st.markdown("### 📋 Detailed Results")
        
        st.dataframe(
            results_df.style.format({
                'Estimated Traffic': '{:,.0f}',
                'Share of Voice (%)': '{:.2f}'
            }),
            use_container_width=True,
            height=400
        )
        
        # Export & Summary
        st.markdown("### 💾 Export & Insights Summary")
        
        col_a, col_b = st.columns([2, 1])
        
        with col_a:
            csv_data = results_df.to_csv(index=False)
            b64 = base64.b64encode(csv_data.encode()).decode()
            
            st.markdown(f"""
            <a href="data:file/csv;base64,{b64}" download="topic_authority_results.csv" style="
                display: inline-block;
                padding: 12px 24px;
                background-color: #FF4B4B;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                text-align: center;
                margin-right: 10px;
            ">
                📥 Download Summary CSV
            </a>
            """, unsafe_allow_html=True)
            
            # Detailed SERP Export
            if st.session_state.get('detailed_serp_data'):
                detailed_df = pd.DataFrame(st.session_state['detailed_serp_data'])
                detailed_csv = detailed_df.to_csv(index=False)
                detailed_b64 = base64.b64encode(detailed_csv.encode()).decode()
                
                st.markdown(f"""
                <a href="data:file/csv;base64,{detailed_b64}" download="detailed_serp_data.csv" style="
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #2196F3;
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                    text-align: center;
                ">
                    📊 Download Detailed SERP CSV
                </a>
                """, unsafe_allow_html=True)
                
                st.caption(f"Detailed CSV includes: keyword, volume, domain, URL, title, position, CTR, traffic ({len(detailed_df)} rows)")
        
        with col_b:
            st.markdown("**📊 Quick Stats**")
            st.caption(f"Total Domains Analyzed: {len(results_df)}")
            st.caption(f"Total Est. Traffic: {int(total_traffic):,}")
            st.caption(f"Keywords Analyzed: {len(st.session_state['keywords_df'])}")
        
        st.divider()
        
        # New Analysis Button
        if st.button("✨ Start New Analysis", type="secondary", use_container_width=True, help="Clear current results and start a new topic analysis"):
            # Clear all session state except credentials
            for key in list(st.session_state.keys()):
                if key not in ['user', 'pass']:
                    del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()

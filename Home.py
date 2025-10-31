import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Vadis Media - Product Placement AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Basic login gate
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🎬 Vadis Media - Login")
    st.markdown("### Please sign in to access the platform")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in", use_container_width=True)
    
    if submitted:
        if email.strip().lower() == "ai@vadis-media.com" and password == "movies2025":
            st.session_state.authenticated = True
            st.success("✅ Login successful! Redirecting...")
            st.rerun()
        else:
            st.error("❌ Invalid credentials. Please try again.")
    st.stop()

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Main content
st.markdown('<h1 class="main-header">🎬 Vadis Media Product Placement AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Script Generation & Revenue Forecasting Platform</p>', unsafe_allow_html=True)

# Introduction
st.markdown("""
Welcome to the **Vadis Media Product Placement AI Platform** - your comprehensive solution for 
intelligent script generation, product placement analysis, casting recommendations, and financial forecasting.
""")

# Company info
with st.expander("ℹ️ About Vadis Media"):
    st.markdown("""
    **Vadis Media** is a leading movie production company specializing in innovative content creation 
    and strategic product placement integration. Visit [vadis-media.com](https://www.vadis-media.com/) 
    to learn more about our services.
    """)

# Features overview
st.markdown("## 🚀 Platform Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h3>📝 AI Script Generation</h3>
        <p>Generate professional script outlines across multiple genres including thriller, comedy, 
        children's movies, rom-com, and crime using advanced AI technology.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-box">
        <h3>📤 Script Upload & Analysis</h3>
        <p>Upload your own scripts or use generated ones for comprehensive AI-powered analysis 
        and product placement opportunity identification.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <h3>🎭 AI Casting Match</h3>
        <p>Leverage TMDB data and AI to identify the most suitable actors by country and genre 
        for your script projects.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-box">
        <h3>💰 Financial Forecasting</h3>
        <p>Use AI and real-time market data to forecast revenue potential and maximize ROI 
        for different genre and product combinations.</p>
    </div>
    """, unsafe_allow_html=True)

# Quick start guide
st.markdown("## 🎯 Quick Start Guide")
st.markdown("""
1. **Generate a Script**: Navigate to the "AI Script Generation" page to create a new script outline
2. **Analyze Scripts**: Use the "Script Analysis" page to upload or analyze generated scripts
3. **Find Actors**: Explore the "AI Casting Match" page to discover suitable actors for your project
4. **Forecast Revenue**: Visit the "Financial Forecasting" page to estimate potential returns
5. **Manage APIs**: Configure and test API connections in the "API Management" page
""")

# Sidebar
with st.sidebar:
    st.markdown("### 🎬 Navigation")
    st.markdown("""
    Use the pages menu to navigate through different features:
    - **AI Script Generation**
    - **Script Upload & Analysis**
    - **Script Comparison**
    - **AI Casting Match**
    - **Financial Forecasting**
    - **API Management**
    """)
    
    st.markdown("---")
    st.markdown("### ⚙️ System Status")
    
    # Check API keys
    api_status = {
        "OpenAI": "✅" if os.getenv("OPENAI_API_KEY") else "❌",
        "TMDB": "✅" if os.getenv("TMDB_API_KEY") else "❌",
        "OMDB": "✅" if os.getenv("OMDB_API_KEY") else "❌",
        "Tavily": "✅" if os.getenv("TAVILY_API_KEY") else "❌"
    }
    
    for api, status in api_status.items():
        st.markdown(f"{status} {api}")
    
    st.markdown("---")
    st.markdown("### 📞 Support")
    st.markdown("[Visit Vadis Media](https://www.vadis-media.com/)")
    
    # Logout button
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>© 2025 Vadis Media. All rights reserved.</p>
    <p>Powered by OpenAI, LangChain, and Streamlit</p>
</div>
""", unsafe_allow_html=True)

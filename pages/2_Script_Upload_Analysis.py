import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Script Upload & Analysis - Vadis Media",
    page_icon="📤",
    layout="wide"
)

st.title("📤 Script Upload & Analysis")
st.markdown("Upload your own scripts or analyze generated ones for product placement opportunities.")

# Ensure directories exist
os.makedirs("scripts", exist_ok=True)

# Initialize session state
if 'analyzed_script' not in st.session_state:
    st.session_state.analyzed_script = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Analysis Options")
    
    analysis_type = st.multiselect(
        "Select Analysis Types",
        ["Product Placement Opportunities", "Character Analysis", "Scene Breakdown", "Market Potential", "Budget Estimation"],
        default=["Product Placement Opportunities", "Market Potential"]
    )
    
    st.markdown("---")
    st.markdown("### ⚙️ AI Settings")
    
    temperature = st.slider(
        "Analysis Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1
    )

# Main content
tab1, tab2 = st.tabs(["📁 Upload Script", "📚 Analyze Existing Script"])

with tab1:
    st.markdown("### Upload Your Script")
    st.markdown("Upload a script file (TXT, PDF, or DOCX) for AI-powered analysis.")
    
    uploaded_file = st.file_uploader(
        "Choose a script file",
        type=['txt', 'pdf', 'docx'],
        help="Upload your script in TXT, PDF, or DOCX format"
    )
    
    if uploaded_file is not None:
        # Read file content
        if uploaded_file.type == "text/plain":
            script_content = uploaded_file.read().decode('utf-8')
        else:
            st.warning("PDF and DOCX support coming soon. Please use TXT files for now.")
            script_content = None
        
        if script_content:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Display preview
            with st.expander("📖 Preview Script"):
                st.text_area("Script Content", script_content, height=300, disabled=True)
            
            # Save uploaded script
            if st.button("💾 Save to Library", key="save_uploaded"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"scripts/{timestamp}_uploaded_{uploaded_file.name}"
                
                with open(filename, 'w') as f:
                    f.write(script_content)
                
                st.success(f"Script saved as: `{filename}`")
                st.session_state.analyzed_script = script_content

with tab2:
    st.markdown("### Select from Generated Scripts")
    
    if os.path.exists("scripts"):
        script_files = sorted([f for f in os.listdir("scripts") if f.endswith('.txt')], reverse=True)
        
        if script_files:
            selected_script = st.selectbox(
                "Choose a script to analyze",
                ["Select a script..."] + script_files
            )
            
            if selected_script != "Select a script...":
                with open(f"scripts/{selected_script}", 'r') as f:
                    script_content = f.read()
                
                st.success(f"✅ Script loaded: {selected_script}")
                
                with st.expander("📖 Preview Script"):
                    st.text_area("Script Content", script_content, height=300, disabled=True)
                
                if st.button("📊 Load for Analysis", key="load_existing"):
                    st.session_state.analyzed_script = script_content
                    st.rerun()
        else:
            st.info("No scripts available. Generate scripts in the AI Script Generation page first.")
    else:
        st.info("Scripts directory not found. Generate scripts first.")

# Analysis section
st.markdown("---")
st.markdown("## 🔍 AI Analysis")

if st.session_state.analyzed_script:
    st.info("📄 Script loaded and ready for analysis")
    
    if st.button("🚀 Analyze Script", type="primary", use_container_width=True):
        if not os.getenv("OPENAI_API_KEY"):
            st.error("❌ OpenAI API key not found. Please configure your .env file.")
        else:
            with st.spinner("🔍 Analyzing script... This may take a moment."):
                try:
                    # Initialize LLM
                    llm = ChatOpenAI(
                        model="gpt-4.1-mini",
                        temperature=temperature,
                        max_tokens=2000
                    )
                    
                    # Create analysis prompt
                    analysis_prompt = f"""Analyze the following movie script and provide detailed insights on:

{', '.join(analysis_type)}

Script:
{st.session_state.analyzed_script[:4000]}

Provide a comprehensive analysis with specific recommendations and opportunities."""
                    
                    # Generate analysis
                    response = llm.invoke(analysis_prompt)
                    result = response.content
                    
                    st.session_state.analysis_result = result
                    
                except Exception as e:
                    st.error(f"❌ Error analyzing script: {str(e)}")
                    st.exception(e)
    
    # Display analysis results
    if st.session_state.analysis_result:
        st.markdown("### 📊 Analysis Results")
        st.markdown(st.session_state.analysis_result)
        
        # Save analysis
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Save Analysis"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"scripts/analysis_{timestamp}.txt"
                
                with open(filename, 'w') as f:
                    f.write("SCRIPT ANALYSIS REPORT\n")
                    f.write("="*80 + "\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Analysis Types: {', '.join(analysis_type)}\n")
                    f.write("="*80 + "\n\n")
                    f.write(st.session_state.analysis_result)
                
                st.success(f"Analysis saved as: `{filename}`")
        
        with col2:
            st.download_button(
                label="⬇️ Download Analysis",
                data=st.session_state.analysis_result,
                file_name=f"script_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        
        # Product placement opportunities extraction
        if "Product Placement Opportunities" in analysis_type:
            st.markdown("---")
            st.markdown("### 🎯 Product Placement Opportunities")
            
            with st.expander("💡 Identified Opportunities", expanded=True):
                st.info("""
                Based on the analysis, here are key product placement opportunities:
                
                - **Scene Integration**: Natural product appearances in key scenes
                - **Character Usage**: Products used by main characters
                - **Brand Alignment**: Brands that match the movie's theme and audience
                - **Visual Prominence**: High-visibility placement opportunities
                """)
                
                # Placeholder for structured opportunities
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Placement Opportunities", "5-7")
                with col2:
                    st.metric("Estimated Value", "$500K-$2M")
                with col3:
                    st.metric("ROI Potential", "High")

else:
    st.warning("⚠️ Please upload or select a script to analyze.")
    st.markdown("""
    **To get started:**
    1. Upload your own script using the "Upload Script" tab, or
    2. Select a generated script from the "Analyze Existing Script" tab
    3. Click "Analyze Script" to get AI-powered insights
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>💡 Tip: For best results, ensure your script includes scene descriptions and character details.</p>
</div>
""", unsafe_allow_html=True)

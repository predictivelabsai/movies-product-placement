import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.pdf_script_extractor import extract_pdf_text

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Script Upload & Analysis - Vadis Media",
    page_icon="📤",
    layout="wide"
)

st.title("📤 Script Upload & Analysis")
st.markdown("Upload PDF scripts or analyze existing ones for product placement opportunities using advanced AI.")

# Ensure directories exist
os.makedirs("scripts", exist_ok=True)

# Initialize session state
if 'analyzed_script' not in st.session_state:
    st.session_state.analyzed_script = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'current_script_name' not in st.session_state:
    st.session_state.current_script_name = None

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
    
    st.info("Using **Gemini 2.5 Flash** for enhanced analysis with larger context window")
    
    temperature = st.slider(
        "Analysis Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="Lower values = more focused, Higher values = more creative"
    )

# Main content
tab1, tab2 = st.tabs(["📁 Upload PDF Script", "📚 Analyze Existing Script"])

with tab1:
    st.markdown("### Upload Your PDF Script")
    st.markdown("Upload a screenplay in PDF format for AI-powered analysis.")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF script file",
        type=['pdf'],
        help="Upload your script in PDF format only"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Save uploaded PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"scripts/{timestamp}_uploaded_{uploaded_file.name}"
        
        with open(pdf_filename, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        st.info(f"📄 PDF saved as: `{pdf_filename}`")
        
        # Extract text from PDF
        with st.spinner("📖 Extracting text from PDF..."):
            try:
                result = extract_pdf_text(pdf_filename)
                
                if result['success']:
                    script_content = result['text']
                    metadata = result['metadata']
                    
                    st.success(f"✅ Text extracted successfully!")
                    
                    # Display metadata
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Pages", metadata.get('num_pages', 'N/A'))
                    with col2:
                        st.metric("Words", f"{metadata.get('word_count', 0):,}")
                    with col3:
                        st.metric("Characters", f"{metadata.get('char_count', 0):,}")
                    with col4:
                        file_size_mb = metadata.get('file_size', 0) / (1024 * 1024)
                        st.metric("Size", f"{file_size_mb:.1f} MB")
                    
                    # Display preview
                    with st.expander("📖 Preview Extracted Text"):
                        preview_text = script_content[:2000]
                        st.text_area("Script Content (First 2000 characters)", preview_text, height=300, disabled=True)
                    
                    # Load for analysis
                    if st.button("📊 Load for Analysis", key="load_uploaded", type="primary"):
                        st.session_state.analyzed_script = script_content
                        st.session_state.current_script_name = uploaded_file.name
                        st.success("✅ Script loaded for analysis!")
                        st.rerun()
                else:
                    st.error(f"❌ Failed to extract text: {result['error']}")
                    st.info("💡 The PDF might be image-based or encrypted. Try using a text-based PDF.")
            
            except Exception as e:
                st.error(f"❌ Error processing PDF: {str(e)}")
                st.exception(e)

with tab2:
    st.markdown("### Select from Existing Scripts")
    
    if os.path.exists("scripts"):
        # Get all PDF files
        pdf_files = sorted([f for f in os.listdir("scripts") if f.endswith('.pdf')], reverse=True)
        
        if pdf_files:
            selected_script = st.selectbox(
                "Choose a PDF script to analyze",
                ["Select a script..."] + pdf_files,
                help="Select from existing PDF scripts in the library"
            )
            
            if selected_script != "Select a script...":
                script_path = f"scripts/{selected_script}"
                
                # Extract text from selected PDF
                with st.spinner(f"📖 Loading {selected_script}..."):
                    try:
                        result = extract_pdf_text(script_path)
                        
                        if result['success']:
                            script_content = result['text']
                            metadata = result['metadata']
                            
                            st.success(f"✅ Script loaded: {selected_script}")
                            
                            # Display metadata
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Pages", metadata.get('num_pages', 'N/A'))
                            with col2:
                                st.metric("Words", f"{metadata.get('word_count', 0):,}")
                            with col3:
                                st.metric("Characters", f"{metadata.get('char_count', 0):,}")
                            with col4:
                                file_size_mb = metadata.get('file_size', 0) / (1024 * 1024)
                                st.metric("Size", f"{file_size_mb:.1f} MB")
                            
                            # Display preview
                            with st.expander("📖 Preview Script"):
                                preview_text = script_content[:2000]
                                st.text_area("Script Content (First 2000 characters)", preview_text, height=300, disabled=True)
                            
                            if st.button("📊 Load for Analysis", key="load_existing", type="primary"):
                                st.session_state.analyzed_script = script_content
                                st.session_state.current_script_name = selected_script
                                st.success("✅ Script loaded for analysis!")
                                st.rerun()
                        else:
                            st.error(f"❌ Failed to extract text: {result['error']}")
                    
                    except Exception as e:
                        st.error(f"❌ Error loading script: {str(e)}")
                        st.exception(e)
        else:
            st.info("📁 No PDF scripts available. Upload a PDF script in the 'Upload PDF Script' tab.")
    else:
        st.info("📁 Scripts directory not found.")

# Analysis section
st.markdown("---")
st.markdown("## 🔍 AI Analysis")

if st.session_state.analyzed_script:
    st.success(f"📄 Script loaded: **{st.session_state.current_script_name or 'Unknown'}**")
    
    # Show script stats
    word_count = len(st.session_state.analyzed_script.split())
    char_count = len(st.session_state.analyzed_script)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Words", f"{word_count:,}")
    with col2:
        st.metric("Total Characters", f"{char_count:,}")
    
    st.markdown("---")
    
    if st.button("🚀 Analyze Script with Gemini 2.5 Flash", type="primary", use_container_width=True):
        if not os.getenv("OPENAI_API_KEY"):
            st.error("❌ OpenAI API key not found. Please configure your .env file.")
        else:
            with st.spinner("🔍 Analyzing script with Gemini 2.5 Flash... This may take a moment due to the comprehensive analysis."):
                try:
                    # Initialize LLM with Gemini 2.5 Flash
                    llm = ChatOpenAI(
                        model="gemini-2.5-flash",
                        temperature=temperature,
                        max_tokens=4000  # Larger token limit for comprehensive analysis
                    )
                    
                    # Create comprehensive analysis prompt
                    analysis_prompt = f"""You are an expert screenplay analyst specializing in product placement opportunities and market analysis.

Analyze the following movie script and provide a detailed, structured analysis covering:

{', '.join(analysis_type)}

For each analysis type, provide:
1. Specific examples from the script
2. Actionable recommendations
3. Estimated value or impact where applicable

Script (truncated to fit context window):
{st.session_state.analyzed_script[:15000]}

Provide a comprehensive, well-structured analysis with clear sections and bullet points."""
                    
                    # Generate analysis
                    response = llm.invoke(analysis_prompt)
                    result = response.content
                    
                    st.session_state.analysis_result = result
                    st.success("✅ Analysis complete!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error analyzing script: {str(e)}")
                    st.exception(e)
    
    # Display analysis results
    if st.session_state.analysis_result:
        st.markdown("### 📊 Analysis Results")
        st.markdown(st.session_state.analysis_result)
        
        # Save and download options
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save Analysis", use_container_width=True):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"scripts/analysis_{timestamp}.txt"
                
                with open(filename, 'w') as f:
                    f.write("SCRIPT ANALYSIS REPORT\n")
                    f.write("="*80 + "\n")
                    f.write(f"Script: {st.session_state.current_script_name or 'Unknown'}\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Model: Gemini 2.5 Flash\n")
                    f.write(f"Analysis Types: {', '.join(analysis_type)}\n")
                    f.write("="*80 + "\n\n")
                    f.write(st.session_state.analysis_result)
                
                st.success(f"Analysis saved as: `{filename}`")
        
        with col2:
            st.download_button(
                label="⬇️ Download Analysis",
                data=st.session_state.analysis_result,
                file_name=f"script_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col3:
            if st.button("🔄 Clear Analysis", use_container_width=True):
                st.session_state.analysis_result = None
                st.session_state.analyzed_script = None
                st.session_state.current_script_name = None
                st.rerun()
        
        # Product placement opportunities section
        if "Product Placement Opportunities" in analysis_type:
            st.markdown("---")
            st.markdown("### 🎯 Next Steps for Product Placement")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("""
                **Integration Strategies:**
                - Review identified scenes for natural product integration
                - Match products with character demographics
                - Consider brand alignment with movie theme
                """)
            
            with col2:
                st.success("""
                **Recommended Actions:**
                - Contact brands for partnership opportunities
                - Estimate placement costs and ROI
                - Create detailed integration proposals
                """)
else:
    st.info("👆 Upload a PDF script or select an existing one to begin analysis")
    
    # Show available scripts
    if os.path.exists("scripts"):
        pdf_files = [f for f in os.listdir("scripts") if f.endswith('.pdf')]
        if pdf_files:
            st.markdown("### 📚 Available Scripts")
            for script in pdf_files[:5]:  # Show first 5
                st.markdown(f"- `{script}`")
            if len(pdf_files) > 5:
                st.markdown(f"*...and {len(pdf_files) - 5} more*")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <small>Powered by Gemini 2.5 Flash | Advanced AI Analysis for Product Placement</small>
</div>
""", unsafe_allow_html=True)

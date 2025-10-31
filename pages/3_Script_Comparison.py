import streamlit as st
import os
from difflib import HtmlDiff, unified_diff
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Script Comparison - Vadis Media",
    page_icon="🔄",
    layout="wide"
)

st.title("🔄 Script Comparison")
st.markdown("Compare original scripts with product placement integrated versions side-by-side.")

# Ensure directories exist
os.makedirs("scripts", exist_ok=True)

# Initialize session state
if 'original_script' not in st.session_state:
    st.session_state.original_script = None
if 'modified_script' not in st.session_state:
    st.session_state.modified_script = None

# Sidebar
with st.sidebar:
    st.markdown("### 🎨 Comparison Settings")
    
    comparison_mode = st.radio(
        "Comparison View",
        ["Side-by-Side", "Unified Diff", "Inline Diff"],
        help="Choose how to display the comparison"
    )
    
    show_line_numbers = st.checkbox("Show Line Numbers", value=True)
    
    highlight_changes = st.checkbox("Highlight Changes", value=True)
    
    st.markdown("---")
    st.markdown("### 📊 Statistics")
    
    if st.session_state.original_script and st.session_state.modified_script:
        original_lines = st.session_state.original_script.count('\n')
        modified_lines = st.session_state.modified_script.count('\n')
        
        st.metric("Original Lines", original_lines)
        st.metric("Modified Lines", modified_lines)
        st.metric("Difference", modified_lines - original_lines)

# Main content
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📄 Original Script")
    
    # Get list of scripts
    if os.path.exists("scripts"):
        script_files = sorted([f for f in os.listdir("scripts") if f.endswith('.txt')], reverse=True)
        
        if script_files:
            original_file = st.selectbox(
                "Select original script",
                ["Select a script..."] + script_files,
                key="original_select"
            )
            
            if original_file != "Select a script...":
                with open(f"scripts/{original_file}", 'r') as f:
                    st.session_state.original_script = f.read()
                
                st.success(f"✅ Loaded: {original_file}")
                
                with st.expander("📖 Preview Original"):
                    st.text_area(
                        "Original Content",
                        st.session_state.original_script,
                        height=300,
                        disabled=True,
                        key="original_preview"
                    )
        else:
            st.info("No scripts available. Generate scripts first.")
    
    # Manual input option
    with st.expander("✏️ Or Paste Original Script"):
        manual_original = st.text_area(
            "Paste original script here",
            height=200,
            key="manual_original"
        )
        
        if st.button("Load Manual Original", key="load_manual_original"):
            if manual_original:
                st.session_state.original_script = manual_original
                st.success("✅ Original script loaded from manual input")
                st.rerun()

with col2:
    st.markdown("### 📝 Modified Script (with Product Placement)")
    
    # Get list of scripts
    if os.path.exists("scripts"):
        script_files = sorted([f for f in os.listdir("scripts") if f.endswith('.txt')], reverse=True)
        
        if script_files:
            modified_file = st.selectbox(
                "Select modified script",
                ["Select a script..."] + script_files,
                key="modified_select"
            )
            
            if modified_file != "Select a script...":
                with open(f"scripts/{modified_file}", 'r') as f:
                    st.session_state.modified_script = f.read()
                
                st.success(f"✅ Loaded: {modified_file}")
                
                with st.expander("📖 Preview Modified"):
                    st.text_area(
                        "Modified Content",
                        st.session_state.modified_script,
                        height=300,
                        disabled=True,
                        key="modified_preview"
                    )
    
    # Manual input option
    with st.expander("✏️ Or Paste Modified Script"):
        manual_modified = st.text_area(
            "Paste modified script here",
            height=200,
            key="manual_modified"
        )
        
        if st.button("Load Manual Modified", key="load_manual_modified"):
            if manual_modified:
                st.session_state.modified_script = manual_modified
                st.success("✅ Modified script loaded from manual input")
                st.rerun()

# Comparison section
st.markdown("---")
st.markdown("## 🔍 Comparison Results")

if st.session_state.original_script and st.session_state.modified_script:
    
    if comparison_mode == "Side-by-Side":
        st.markdown("### Side-by-Side Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Original Script**")
            st.text_area(
                "Original",
                st.session_state.original_script,
                height=500,
                disabled=True,
                key="side_original",
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("**Modified Script (with Products)**")
            st.text_area(
                "Modified",
                st.session_state.modified_script,
                height=500,
                disabled=True,
                key="side_modified",
                label_visibility="collapsed"
            )
    
    elif comparison_mode == "Unified Diff":
        st.markdown("### Unified Diff View")
        
        original_lines = st.session_state.original_script.splitlines(keepends=True)
        modified_lines = st.session_state.modified_script.splitlines(keepends=True)
        
        diff = unified_diff(
            original_lines,
            modified_lines,
            fromfile='Original Script',
            tofile='Modified Script',
            lineterm=''
        )
        
        diff_text = '\n'.join(diff)
        
        st.code(diff_text, language='diff')
    
    elif comparison_mode == "Inline Diff":
        st.markdown("### Inline Diff View")
        
        original_lines = st.session_state.original_script.splitlines()
        modified_lines = st.session_state.modified_script.splitlines()
        
        # Create HTML diff
        differ = HtmlDiff()
        html_diff = differ.make_file(
            original_lines,
            modified_lines,
            fromdesc='Original Script',
            todesc='Modified Script (with Product Placement)',
            context=True,
            numlines=3
        )
        
        # Display HTML diff
        st.components.v1.html(html_diff, height=600, scrolling=True)
    
    # Analysis section
    st.markdown("---")
    st.markdown("### 📊 Change Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    original_words = len(st.session_state.original_script.split())
    modified_words = len(st.session_state.modified_script.split())
    original_chars = len(st.session_state.original_script)
    modified_chars = len(st.session_state.modified_script)
    
    with col1:
        st.metric("Original Words", original_words)
    with col2:
        st.metric("Modified Words", modified_words, delta=modified_words - original_words)
    with col3:
        st.metric("Original Characters", original_chars)
    with col4:
        st.metric("Modified Characters", modified_chars, delta=modified_chars - original_chars)
    
    # Product placement insights
    st.markdown("---")
    st.markdown("### 🎯 Product Placement Insights")
    
    with st.expander("💡 Key Changes", expanded=True):
        st.info("""
        **Product Integration Analysis:**
        
        - **Added Scenes**: Scenes where products were naturally integrated
        - **Character Interactions**: How characters interact with placed products
        - **Brand Mentions**: Direct and indirect brand references
        - **Visual Cues**: Descriptions added for visual product placement
        
        The comparison shows how product placement can be seamlessly integrated 
        without disrupting the narrative flow.
        """)
    
    # Export options
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="⬇️ Download Original",
            data=st.session_state.original_script,
            file_name="original_script.txt",
            mime="text/plain"
        )
    
    with col2:
        st.download_button(
            label="⬇️ Download Modified",
            data=st.session_state.modified_script,
            file_name="modified_script.txt",
            mime="text/plain"
        )
    
    with col3:
        # Create comparison report
        comparison_report = f"""SCRIPT COMPARISON REPORT
{'='*80}

STATISTICS:
-----------
Original Words: {original_words}
Modified Words: {modified_words}
Word Difference: {modified_words - original_words}

Original Characters: {original_chars}
Modified Characters: {modified_chars}
Character Difference: {modified_chars - original_chars}

{'='*80}

ORIGINAL SCRIPT:
{st.session_state.original_script}

{'='*80}

MODIFIED SCRIPT (WITH PRODUCT PLACEMENT):
{st.session_state.modified_script}
"""
        
        st.download_button(
            label="⬇️ Download Report",
            data=comparison_report,
            file_name="comparison_report.txt",
            mime="text/plain"
        )

else:
    st.warning("⚠️ Please select or paste both original and modified scripts to compare.")
    st.markdown("""
    **To get started:**
    1. Select or paste an original script in the left column
    2. Select or paste a modified script (with product placement) in the right column
    3. The comparison will be displayed automatically
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>💡 Tip: Use the comparison to see how product placement enhances your script naturally.</p>
</div>
""", unsafe_allow_html=True)

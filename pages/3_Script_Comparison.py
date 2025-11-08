import streamlit as st
import os
import sys
from datetime import datetime
from difflib import HtmlDiff, unified_diff
from dotenv import load_dotenv
from utils.langchain_util import compare_scripts, generate_modified_script
import pandas as pd
import json

# Make utils importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.pdf_script_extractor import extract_pdf_text

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Script Comparison - Vadis Media",
    page_icon="🔄",
    layout="wide"
)

st.title("🔄 Script Comparison")
st.markdown("Three-step workflow: 1) Upload Original, 2) Generate Modified, 3) Compare.")

# Ensure directories exist
os.makedirs("scripts", exist_ok=True)
os.makedirs("prompts", exist_ok=True)

# Initialize session state
if 'original_script' not in st.session_state:
    st.session_state.original_script = None
if 'modified_script' not in st.session_state:
    st.session_state.modified_script = None
if 'comparison_analysis' not in st.session_state:
    st.session_state.comparison_analysis = None
if 'compare_ready' not in st.session_state:
    st.session_state.compare_ready = False
if 'json_changes' not in st.session_state:
    st.session_state.json_changes = None

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
    st.markdown("### ⚙️ AI Settings")
    temperature = st.slider(
        "Analysis Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="Lower values = more focused, Higher values = more creative"
    )
    st.markdown("---")
    st.markdown("### 🤖 AI Model Selection")
    ai_model = st.selectbox(
        "Choose AI Model",
        [
            "Google Gemini 2.0 Flash (Default)",
            "Google Gemini 2.5 Flash",
            "OpenAI GPT-4.1 Mini",
            "OpenAI GPT-4.1 Nano",
            "XAI Grok 3"
        ],
        index=0,
        help="Select the AI model for generation and comparison"
    )
    model_mapping = {
        "Google Gemini 2.0 Flash (Default)": {"provider": "google", "model": "gemini-2.0-flash-exp"},
        "Google Gemini 2.5 Flash": {"provider": "openai", "model": "gemini-2.5-flash"},
        "OpenAI GPT-4.1 Mini": {"provider": "openai", "model": "gpt-4.1-mini"},
        "OpenAI GPT-4.1 Nano": {"provider": "openai", "model": "gpt-4.1-nano"},
        "XAI Grok 3": {"provider": "xai", "model": "grok-3"}
    }
    selected_model = model_mapping[ai_model]
    if selected_model["provider"] == "google":
        st.info(f"🔹 Using **{ai_model}** with large context window (up to 1M tokens)")
    elif selected_model["provider"] == "openai":
        st.info(f"🔹 Using **{ai_model}** with advanced reasoning capabilities")
    elif selected_model["provider"] == "xai":
        st.info(f"🔹 Using **{ai_model}** with real-time knowledge")

    st.markdown("---")
    st.markdown("### 📊 Statistics")
    
    if st.session_state.original_script and st.session_state.modified_script:
        original_lines = st.session_state.original_script.count('\n')
        modified_lines = st.session_state.modified_script.count('\n')
        
        st.metric("Original Lines", original_lines)
        st.metric("Modified Lines", modified_lines)
        st.metric("Difference", modified_lines - original_lines)

st.markdown("---")
st.markdown("## 1) 📄 Upload Original Script")
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("### Original Script")
    with st.expander("📥 Upload Original (PDF)"):
        uploaded_original_pdf = st.file_uploader(
            "Choose original script (PDF)",
            type=['pdf'],
            key="orig_pdf_uploader",
            help="Upload the original screenplay as a PDF"
        )
        if uploaded_original_pdf is not None:
            st.success(f"✅ File uploaded: {uploaded_original_pdf.name}")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"scripts/{timestamp}_original_{uploaded_original_pdf.name}"
            with open(pdf_filename, 'wb') as f:
                f.write(uploaded_original_pdf.getbuffer())
            st.info(f"📄 PDF saved as: `{pdf_filename}`")
            with st.spinner("📖 Extracting text from original PDF..."):
                result = extract_pdf_text(pdf_filename)
            if result.get('success'):
                meta = result.get('metadata', {})
                colm1, colm2, colm3, colm4 = st.columns(4)
                with colm1:
                    st.metric("Pages", meta.get('num_pages', 'N/A'))
                with colm2:
                    st.metric("Words", f"{meta.get('word_count', 0):,}")
                with colm3:
                    st.metric("Characters", f"{meta.get('char_count', 0):,}")
                with colm4:
                    size_mb = meta.get('file_size', 0) / (1024 * 1024)
                    st.metric("Size", f"{size_mb:.1f} MB")
                with st.expander("📖 Preview Extracted Text"):
                    st.text_area(
                        "Original (preview)",
                        result.get('text', '')[:2000],
                        height=300,
                        disabled=True
                    )
                if st.button("📊 Load as Original", key="load_uploaded_original", type="primary"):
                    st.session_state.original_script = result.get('text', '')
                    st.session_state.compare_ready = False
                    st.success("✅ Original script loaded from uploaded PDF")
                    st.rerun()
            else:
                st.error(f"❌ Failed to extract text: {result.get('error')}")
    
    # Get list of scripts
    if os.path.exists("scripts"):
        script_files = sorted(
            [f for f in os.listdir("scripts") if f.endswith('.txt') or f.endswith('.pdf')],
            reverse=True
        )
        
        if script_files:
            original_file = st.selectbox(
                "Select original script",
                ["Select a script..."] + script_files,
                key="original_select"
            )
            
            if original_file != "Select a script...":
                file_path = f"scripts/{original_file}"
                if original_file.lower().endswith(".pdf"):
                    with st.spinner(f"📖 Extracting text from {original_file}..."):
                        res = extract_pdf_text(file_path)
                    if res.get('success'):
                        st.session_state.original_script = res.get('text', '')
                    else:
                        st.error(f"❌ Failed to extract text: {res.get('error')}")
                        st.session_state.original_script = None
                else:
                    with open(file_path, 'r') as f:
                        st.session_state.original_script = f.read()
                
                st.success(f"✅ Loaded: {original_file}")
                st.session_state.compare_ready = False
                
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
                st.session_state.compare_ready = False
                st.success("✅ Original script loaded from manual input")
                st.rerun()

with col2:
    st.markdown("### Generation Options")
    st.info("You can still upload a modified PDF in Step 2 if you already have one.")
    subtlety = st.select_slider(
        "Integration Subtlety",
        options=["subtle", "balanced", "prominent"],
        value="balanced"
    )
    brands = st.text_input("Preferred Brands (optional, comma-separated)", value="")
    categories = st.text_input("Product Categories (optional, comma-separated)", value="smartphone, coffee, car")

st.markdown("---")
st.markdown("## 2) 🛠️ Generate Modified Script")
gen_col1, gen_col2 = st.columns([2, 3])
with gen_col1:
    st.markdown("Generate a modified version that integrates products without changing the story.")
    if st.button("🚀 Generate Modified Script", type="primary", use_container_width=True, disabled=not bool(st.session_state.original_script)):
        # Check API key based on selected provider
        api_key_missing = False
        if selected_model["provider"] == "google" and not os.getenv("GOOGLE_API_KEY"):
            st.error("❌ Google API key not found. Please configure your .env file.")
            api_key_missing = True
        elif selected_model["provider"] == "openai" and not os.getenv("OPENAI_API_KEY"):
            st.error("❌ OpenAI API key not found. Please configure your .env file.")
            api_key_missing = True
        elif selected_model["provider"] == "xai" and not os.getenv("XAI_API_KEY"):
            st.error("❌ XAI API key not found. Please configure your .env file.")
            api_key_missing = True
        if not api_key_missing:
            # Load modification template (.md preferred, fallback .txt)
            mod_template_path_md = "prompts/script_modification_template.md"
            mod_template_path_txt = "prompts/script_modification_template.txt"
            if os.path.exists(mod_template_path_md):
                with open(mod_template_path_md, 'r') as f:
                    base_template = f.read()
            elif os.path.exists(mod_template_path_txt):
                with open(mod_template_path_txt, 'r') as f:
                    base_template = f.read()
            else:
                base_template = (
                    "Modify the following script to include natural product placements and subtle cinematography cues.\n"
                    "Do not change story beats or character arcs. Output only the modified script.\n\n"
                    "{original_script}\n"
                )
            # Inject user options as preface
            preface = f"Parameters: subtlety={subtlety}; brands=[{brands}]; categories=[{categories}]\n\n"
            full_template = preface + base_template
            try:
                with st.spinner("✨ Generating modified script..."):
                    result = generate_modified_script(
                        original_script=st.session_state.original_script,
                        template_text=full_template,
                        provider=selected_model["provider"],
                        model=selected_model["model"],
                        temperature=temperature,
                        max_tokens=3500
                    )
                st.session_state.modified_script = result
                st.session_state.compare_ready = False
                st.success("✅ Modified script generated!")
                # Save to scripts
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"scripts/{timestamp}_modified_generated.txt"
                with open(filename, 'w') as f:
                    f.write(result)
                st.info(f"💾 Saved as: `{filename}`")
            except Exception as e:
                st.error(f"❌ Error generating modified script: {str(e)}")

with gen_col2:
    st.markdown("### Preview Modified Script")
    if st.session_state.modified_script:
        st.text_area(
            "Modified",
            st.session_state.modified_script,
            height=300,
            disabled=False,
            key="modified_preview_editable"
        )
        if st.button("💾 Update Modified From Editor"):
            st.session_state.modified_script = st.session_state.modified_script if isinstance(st.session_state.modified_script, str) else str(st.session_state.modified_script)
            st.success("✅ Modified script updated from editor.")
    else:
        st.info("No modified script yet. Generate one or upload in Step 2 below.")

with st.expander("📥 Or Upload Existing Modified (PDF)"):
    uploaded_modified_pdf = st.file_uploader(
        "Choose modified script (PDF)",
        type=['pdf'],
        key="mod_pdf_uploader_step2",
        help="Upload the modified screenplay as a PDF"
    )
    if uploaded_modified_pdf is not None:
        st.success(f"✅ File uploaded: {uploaded_modified_pdf.name}")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"scripts/{timestamp}_modified_{uploaded_modified_pdf.name}"
        with open(pdf_filename, 'wb') as f:
            f.write(uploaded_modified_pdf.getbuffer())
        st.info(f"📄 PDF saved as: `{pdf_filename}`")
        with st.spinner("📖 Extracting text from modified PDF..."):
            result = extract_pdf_text(pdf_filename)
        if result.get('success'):
            st.session_state.modified_script = result.get('text', '')
            st.session_state.compare_ready = False
            st.success("✅ Modified script loaded from uploaded PDF")
        else:
            st.error(f"❌ Failed to extract text: {result.get('error')}")

st.markdown("---")
st.markdown("## 3) 🧮 Compare & Navigate Changes")
compare_disabled = not (st.session_state.original_script and st.session_state.modified_script)
if st.button("🔎 Compare Now", type="primary", use_container_width=True, disabled=compare_disabled):
    st.session_state.compare_ready = True
    st.success("✅ Comparison ready below.")

if st.session_state.compare_ready and st.session_state.original_script and st.session_state.modified_script:
    # Structured JSON changes (primary view)
    st.markdown("## 🔍 Structured JSON Changes")
    col_json_btn, col_json_view = st.columns([1, 3])
    with col_json_btn:
        if st.button("🧠 Generate JSON Changes", type="primary", use_container_width=True):
            # Provider key checks
            api_key_missing = False
            if selected_model["provider"] == "google" and not os.getenv("GOOGLE_API_KEY"):
                st.error("❌ Google API key not found. Please configure your .env file.")
                api_key_missing = True
            elif selected_model["provider"] == "openai" and not os.getenv("OPENAI_API_KEY"):
                st.error("❌ OpenAI API key not found. Please configure your .env file.")
                api_key_missing = True
            elif selected_model["provider"] == "xai" and not os.getenv("XAI_API_KEY"):
                st.error("❌ XAI API key not found. Please configure your .env file.")
                api_key_missing = True
            if not api_key_missing:
                # Load JSON template
                json_tpl_md = "prompts/script_comparison_json_template.md"
                json_tpl_txt = "prompts/script_comparison_json_template.txt"
                if os.path.exists(json_tpl_md):
                    with open(json_tpl_md, "r") as f:
                        json_template = f.read()
                elif os.path.exists(json_tpl_txt):
                    with open(json_tpl_txt, "r") as f:
                        json_template = f.read()
                else:
                    json_template = "{ \"summary\": {\"newPlacementsCount\": 0, \"cinematographyChangesCount\": 0}, \"changes\": [] }"
                from utils.langchain_util import compare_scripts_json
                try:
                    with st.spinner("🔎 Generating structured changes..."):
                        js = compare_scripts_json(
                            original_script=st.session_state.original_script,
                            modified_script=st.session_state.modified_script,
                            template_text=json_template,
                            provider=selected_model["provider"],
                            model=selected_model["model"],
                            temperature=max(0.0, min(temperature, 0.5)),
                            max_tokens=1800
                        )
                    st.session_state.json_changes = js
                    st.success("✅ JSON changes generated.")
                except Exception as e:
                    st.error(f"❌ Failed to generate or parse JSON changes: {str(e)}")
    with col_json_view:
        if st.session_state.json_changes:
            js = st.session_state.json_changes
            st.markdown(f"**New Placements:** {js.get('summary',{}).get('newPlacementsCount','?')} | **Cinematography Changes:** {js.get('summary',{}).get('cinematographyChangesCount','?')}")
            rows = js.get("changes", [])
            if rows:
                df = pd.DataFrame([{
                    "id": r.get("id"),
                    "type": r.get("type"),
                    "sceneHint": r.get("sceneHint"),
                    "productMentions": ", ".join(r.get("productMentions", []) or []),
                    "cinematographyNotes": ", ".join(r.get("cinematographyNotes", []) or []),
                    "confidence": r.get("confidence")
                } for r in rows])
                st.dataframe(df, use_container_width=True)
                ids = ["Select..."] + [r.get("id") for r in rows if r.get("id")]
                sel = st.selectbox("Inspect change", ids)
                if sel != "Select...":
                    r = next((x for x in rows if x.get("id") == sel), None)
                    if r:
                        st.markdown(f"#### Change {r.get('id')} • {r.get('type')} • {r.get('sceneHint')}")
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("**Original Excerpt**")
                            st.text_area("orig", r.get("originalExcerpt",""), height=200, disabled=True, label_visibility="collapsed", key=f"orig_json_{sel}")
                        with c2:
                            st.markdown("**Modified Excerpt**")
                            st.text_area("mod", r.get("modifiedExcerpt",""), height=200, disabled=True, label_visibility="collapsed", key=f"mod_json_{sel}")
                        st.caption(f"Products: {', '.join(r.get('productMentions',[]) or [])} | Camera: {', '.join(r.get('cinematographyNotes',[]) or [])} | Confidence: {r.get('confidence')}")
                st.download_button(
                    "⬇️ Download JSON",
                    data=json.dumps(st.session_state.json_changes),
                    file_name="script_changes.json",
                    mime="application/json"
                )
            else:
                st.info("No structured changes found.")
        else:
            st.info("Click the button to generate JSON changes.")

    st.markdown("---")
    st.markdown("## 🔍 Comparison Results")
    
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

    # Quick navigation for modified sections
    st.markdown("---")
    st.markdown("### 🧭 Modified Sections Quick Access")
    import difflib
    original_lines_nav = st.session_state.original_script.splitlines()
    modified_lines_nav = st.session_state.modified_script.splitlines()
    sm = difflib.SequenceMatcher(a=original_lines_nav, b=modified_lines_nav)
    changes = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("replace", "insert", "delete"):
            orig_excerpt = "\n".join(original_lines_nav[max(0, i1-2):min(len(original_lines_nav), i2+2)])
            mod_excerpt = "\n".join(modified_lines_nav[max(0, j1-2):min(len(modified_lines_nav), j2+2)])
            changes.append({
                "tag": tag,
                "range_original": (i1, i2),
                "range_modified": (j1, j2),
                "original_excerpt": orig_excerpt,
                "modified_excerpt": mod_excerpt
            })
    if changes:
        labels = [f"Change {idx+1}: {c['tag']} (orig {c['range_original'][0]}:{c['range_original'][1]} → mod {c['range_modified'][0]}:{c['range_modified'][1]})" for idx,c in enumerate(changes)]
        selected = st.selectbox("Go to change", ["Select..."] + labels)
        if selected != "Select...":
            idx = labels.index(selected)
            c = changes[idx]
            st.markdown(f"#### {selected}")
            colA, colB = st.columns(2)
            with colA:
                st.markdown("**Original Excerpt**")
                st.text_area("Original Excerpt", c["original_excerpt"], height=200, disabled=True, label_visibility="collapsed", key=f"orig_ex_{idx}")
            with colB:
                st.markdown("**Modified Excerpt**")
                st.text_area("Modified Excerpt", c["modified_excerpt"], height=200, disabled=True, label_visibility="collapsed", key=f"mod_ex_{idx}")
        with st.expander("All Modified Sections"):
            for idx, c in enumerate(changes):
                st.markdown(f"**{labels[idx]}**")
                colA, colB = st.columns(2)
                with colA:
                    st.text_area("Original", c["original_excerpt"], height=150, disabled=True, label_visibility="collapsed", key=f"orig_list_{idx}")
                with colB:
                    st.text_area("Modified", c["modified_excerpt"], height=150, disabled=True, label_visibility="collapsed", key=f"mod_list_{idx}")
    else:
        st.info("No significant modified sections detected.")

    st.markdown("---")
    st.markdown("### 🤖 AI Comparison: Placement & Cinematography")
    if st.button("🔎 Analyze Product Placement & Cinematography", type="primary", use_container_width=True):
        if not (st.session_state.original_script and st.session_state.modified_script):
            st.warning("⚠️ Please load both original and modified scripts before analysis.")
        else:
            # Provider-specific API key check
            api_key_missing = False
            if selected_model["provider"] == "google" and not os.getenv("GOOGLE_API_KEY"):
                st.error("❌ Google API key not found. Please configure your .env file.")
                api_key_missing = True
            elif selected_model["provider"] == "openai" and not os.getenv("OPENAI_API_KEY"):
                st.error("❌ OpenAI API key not found. Please configure your .env file.")
                api_key_missing = True
            elif selected_model["provider"] == "xai" and not os.getenv("XAI_API_KEY"):
                st.error("❌ XAI API key not found. Please configure your .env file.")
                api_key_missing = True
            if api_key_missing:
                st.stop()
            # Load comparison prompt template (.md preferred, fallback .txt)
            prompt_path_md = "prompts/script_comparison_template.md"
            prompt_path_txt = "prompts/script_comparison_template.txt"
            if os.path.exists(prompt_path_md):
                with open(prompt_path_md, 'r') as f:
                    comparison_template = f.read()
            elif os.path.exists(prompt_path_txt):
                with open(prompt_path_txt, 'r') as f:
                    comparison_template = f.read()
            else:
                comparison_template = (
                    "You are a professional script supervisor specializing in product placement.\n\n"
                    "Compare the ORIGINAL script to the MODIFIED script. The modified script should keep the story the same.\n"
                    "Focus ONLY on changes related to:\n"
                    "1) New product placements and how cleverly they are integrated\n"
                    "2) Cinematography changes (camera angles, shot choices, blocking) that support placements\n\n"
                    "Do NOT suggest story changes. Do NOT change character arcs. Keep analysis tight and structured with sections:\n"
                    "## New Product Placements (Clever Integrations)\n"
                    "- [Scene/Location]: What changed, how product appears naturally, subtlety level\n\n"
                    "## Cinematography Changes (Angles & Camera Work)\n"
                    "- Shot framing, movement, composition that enhances visibility without breaking immersion\n\n"
                    "## Integration Techniques Used\n"
                    "- Examples: foreground props, reflective reveals, over-the-shoulder framing, rack focus, motivated camera moves\n\n"
                    "## Narrative Integrity\n"
                    "- Confirm story beats unchanged; note if any wording changes risk story drift\n\n"
                    "ORIGINAL:\n"
                    "{original_script}\n\n"
                    "MODIFIED:\n"
                    "{modified_script}\n"
                )
            try:
                with st.spinner("🔎 Analyzing differences..."):
                    result = compare_scripts(
                        original_script=st.session_state.original_script,
                        modified_script=st.session_state.modified_script,
                        template_text=comparison_template,
                        temperature=temperature,
                        model=selected_model["model"],
                        provider=selected_model["provider"],
                        max_tokens=1500
                    )
                st.session_state.comparison_analysis = result
                st.success("✅ Analysis complete!")
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")

    if st.session_state.comparison_analysis:
        st.markdown("#### 📘 Analysis Report")
        st.markdown(st.session_state.comparison_analysis)
        st.download_button(
            label="⬇️ Download Analysis",
            data=st.session_state.comparison_analysis,
            file_name="script_comparison_analysis.md",
            mime="text/markdown"
        )
    
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

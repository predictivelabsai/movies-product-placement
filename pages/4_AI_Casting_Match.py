import streamlit as st
import os
from dotenv import load_dotenv
from tmdbv3api import TMDb, Person, Movie
from langchain_openai import ChatOpenAI
import json

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Casting Match - Vadis Media",
    page_icon="🎭",
    layout="wide"
)

st.title("🎭 AI Casting Match")
st.markdown("Use TMDB data and AI to identify the most suitable actors for your script.")

# Initialize TMDB
tmdb = TMDb()
tmdb.api_key = os.getenv('TMDB_API_KEY')
tmdb.language = 'en'

person = Person()
movie = Movie()

# Initialize session state
if 'selected_actors' not in st.session_state:
    st.session_state.selected_actors = []
if 'script_genre' not in st.session_state:
    st.session_state.script_genre = None

# Sidebar
with st.sidebar:
    st.markdown("### 🎬 Casting Criteria")
    
    genre = st.selectbox(
        "Genre",
        ["Action", "Comedy", "Drama", "Thriller", "Romance", "Sci-Fi", "Horror", "Crime", "Children's"],
        help="Select the movie genre"
    )
    
    country = st.selectbox(
        "Primary Market",
        ["United States", "United Kingdom", "Canada", "Australia", "France", "Germany", "Spain", "Italy", "Japan", "South Korea", "India", "China"],
        help="Target market for casting"
    )
    
    age_range = st.select_slider(
        "Age Range",
        options=["18-25", "26-35", "36-45", "46-55", "56-65", "65+"],
        value="26-35"
    )
    
    gender = st.radio(
        "Gender",
        ["Any", "Male", "Female", "Non-binary"]
    )
    
    min_popularity = st.slider(
        "Minimum Popularity Score",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=5.0,
        help="TMDB popularity score threshold"
    )
    
    st.markdown("---")
    st.markdown("### 🎯 AI Matching")
    
    use_ai_matching = st.checkbox("Enable AI-Powered Matching", value=True)
    
    if use_ai_matching:
        matching_criteria = st.multiselect(
            "AI Criteria",
            ["Genre Fit", "Box Office Track Record", "Social Media Presence", "Award History", "Age Appropriateness"],
            default=["Genre Fit", "Box Office Track Record"]
        )

# Main content
tab1, tab2, tab3 = st.tabs(["🔍 Search Actors", "🎯 AI Recommendations", "📋 Selected Cast"])

with tab1:
    st.markdown("### Search TMDB Database")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "Search for actors",
            placeholder="Enter actor name...",
            help="Search TMDB database for actors"
        )
    
    with col2:
        search_button = st.button("🔍 Search", type="primary", use_container_width=True)
    
    if search_button and search_query:
        try:
            with st.spinner("Searching TMDB database..."):
                results = person.search(search_query)
                
                if results:
                    st.success(f"Found {len(results)} results")
                    
                    # Display results
                    for idx, actor in enumerate(results[:10]):
                        with st.expander(f"🎭 {actor.name} (Popularity: {actor.popularity:.1f})"):
                            col1, col2 = st.columns([1, 3])
                            
                            with col1:
                                if actor.profile_path:
                                    image_url = f"https://image.tmdb.org/t/p/w200{actor.profile_path}"
                                    st.image(image_url, use_container_width=True)
                                else:
                                    st.info("No image available")
                            
                            with col2:
                                st.markdown(f"**Name:** {actor.name}")
                                st.markdown(f"**Popularity:** {actor.popularity:.2f}")
                                st.markdown(f"**Known For:** {actor.known_for_department if hasattr(actor, 'known_for_department') else 'Acting'}")
                                
                                if hasattr(actor, 'known_for') and actor.known_for:
                                    known_titles = [item.title if hasattr(item, 'title') else item.name for item in actor.known_for[:3]]
                                    st.markdown(f"**Notable Works:** {', '.join(known_titles)}")
                                
                                if st.button(f"➕ Add to Cast", key=f"add_{actor.id}"):
                                    actor_data = {
                                        'id': actor.id,
                                        'name': actor.name,
                                        'popularity': actor.popularity,
                                        'profile_path': actor.profile_path,
                                        'genre': genre
                                    }
                                    
                                    if actor_data not in st.session_state.selected_actors:
                                        st.session_state.selected_actors.append(actor_data)
                                        st.success(f"Added {actor.name} to cast!")
                                        st.rerun()
                else:
                    st.warning("No results found. Try a different search term.")
        
        except Exception as e:
            st.error(f"Error searching TMDB: {str(e)}")
    
    # Popular actors by genre
    st.markdown("---")
    st.markdown("### 🌟 Popular Actors")
    
    if st.button("Show Popular Actors", key="show_popular"):
        try:
            with st.spinner("Fetching popular actors..."):
                popular_actors = person.popular()
                
                cols = st.columns(4)
                
                for idx, actor in enumerate(popular_actors[:8]):
                    with cols[idx % 4]:
                        if actor.profile_path:
                            image_url = f"https://image.tmdb.org/t/p/w200{actor.profile_path}"
                            st.image(image_url, use_container_width=True)
                        
                        st.markdown(f"**{actor.name}**")
                        st.markdown(f"⭐ {actor.popularity:.1f}")
                        
                        if st.button("➕", key=f"add_popular_{actor.id}"):
                            actor_data = {
                                'id': actor.id,
                                'name': actor.name,
                                'popularity': actor.popularity,
                                'profile_path': actor.profile_path,
                                'genre': genre
                            }
                            
                            if actor_data not in st.session_state.selected_actors:
                                st.session_state.selected_actors.append(actor_data)
                                st.success(f"Added {actor.name}!")
                                st.rerun()
        
        except Exception as e:
            st.error(f"Error fetching popular actors: {str(e)}")

with tab2:
    st.markdown("### 🤖 AI-Powered Actor Recommendations")
    
    # Load scripts for context
    script_context = ""
    if os.path.exists("scripts"):
        script_files = sorted([f for f in os.listdir("scripts") if f.endswith('.txt')], reverse=True)
        
        if script_files:
            selected_script = st.selectbox(
                "Select script for context",
                ["None"] + script_files
            )
            
            if selected_script != "None":
                with open(f"scripts/{selected_script}", 'r') as f:
                    script_context = f.read()[:2000]  # First 2000 chars
                
                st.success(f"✅ Using script context: {selected_script}")
    
    if st.button("🚀 Generate AI Recommendations", type="primary", use_container_width=True):
        if not os.getenv("OPENAI_API_KEY"):
            st.error("❌ OpenAI API key not found.")
        else:
            with st.spinner("🤖 AI is analyzing and generating recommendations..."):
                try:
                    llm = ChatOpenAI(model="gpt-4", temperature=0.7)
                    
                    prompt = f"""As a casting director, recommend 5 actors perfect for a {genre} movie targeting {country} market.

Genre: {genre}
Target Market: {country}
Age Range: {age_range}
Gender Preference: {gender}

{f"Script Context: {script_context[:1000]}" if script_context else ""}

For each actor, provide:
1. Name
2. Why they're a good fit (2-3 sentences)
3. Relevant past roles
4. Estimated popularity score (0-100)
5. Box office appeal

Format as a numbered list."""
                    
                    result = llm.predict(prompt)
                    
                    st.markdown("### 🎯 AI Recommendations")
                    st.markdown(result)
                    
                    # Save recommendations
                    if st.button("💾 Save Recommendations"):
                        from datetime import datetime
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"scripts/casting_recommendations_{timestamp}.txt"
                        
                        with open(filename, 'w') as f:
                            f.write(f"CASTING RECOMMENDATIONS\n")
                            f.write(f"{'='*80}\n")
                            f.write(f"Genre: {genre}\n")
                            f.write(f"Market: {country}\n")
                            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write(f"{'='*80}\n\n")
                            f.write(result)
                        
                        st.success(f"Saved as: {filename}")
                
                except Exception as e:
                    st.error(f"Error generating recommendations: {str(e)}")
    
    # Genre-specific insights
    st.markdown("---")
    st.markdown("### 📊 Genre Insights")
    
    genre_insights = {
        "Action": "Look for actors with physical presence, martial arts background, or stunt experience. Box office draw is crucial.",
        "Comedy": "Timing and charisma are key. Consider actors with stand-up or improv backgrounds.",
        "Drama": "Award-winning or critically acclaimed actors add prestige. Look for emotional range.",
        "Thriller": "Intensity and ability to convey tension. Previous thriller experience is valuable.",
        "Romance": "Chemistry is essential. Consider on-screen pairing history.",
        "Sci-Fi": "Actors comfortable with green screen and technical dialogue. Franchise experience helps.",
        "Horror": "Ability to convey fear and vulnerability. Scream queens/kings have dedicated fanbases.",
        "Crime": "Gritty, intense performances. Law enforcement or criminal role experience.",
        "Children's": "Family-friendly image essential. Voice acting experience valuable."
    }
    
    st.info(f"**{genre} Casting Tips:** {genre_insights.get(genre, 'Consider actors with relevant genre experience.')}")

with tab3:
    st.markdown("### 📋 Selected Cast")
    
    if st.session_state.selected_actors:
        st.success(f"✅ {len(st.session_state.selected_actors)} actors selected")
        
        # Display selected actors
        for idx, actor in enumerate(st.session_state.selected_actors):
            with st.expander(f"🎭 {actor['name']}", expanded=True):
                col1, col2, col3 = st.columns([1, 3, 1])
                
                with col1:
                    if actor.get('profile_path'):
                        image_url = f"https://image.tmdb.org/t/p/w200{actor['profile_path']}"
                        st.image(image_url, use_container_width=True)
                
                with col2:
                    st.markdown(f"**Name:** {actor['name']}")
                    st.markdown(f"**Popularity:** {actor['popularity']:.2f}")
                    st.markdown(f"**Genre:** {actor.get('genre', 'N/A')}")
                    st.markdown(f"**TMDB ID:** {actor['id']}")
                
                with col3:
                    if st.button("🗑️ Remove", key=f"remove_{actor['id']}"):
                        st.session_state.selected_actors.remove(actor)
                        st.rerun()
        
        # Export cast list
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Save Cast List", use_container_width=True):
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"scripts/cast_list_{timestamp}.json"
                
                with open(filename, 'w') as f:
                    json.dump(st.session_state.selected_actors, f, indent=2)
                
                st.success(f"Cast list saved as: {filename}")
        
        with col2:
            # Create text version for download
            cast_text = "CAST LIST\n" + "="*80 + "\n\n"
            for actor in st.session_state.selected_actors:
                cast_text += f"Name: {actor['name']}\n"
                cast_text += f"Popularity: {actor['popularity']:.2f}\n"
                cast_text += f"Genre: {actor.get('genre', 'N/A')}\n"
                cast_text += f"TMDB ID: {actor['id']}\n"
                cast_text += "-"*80 + "\n"
            
            st.download_button(
                label="⬇️ Download Cast List",
                data=cast_text,
                file_name="cast_list.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        # Clear all button
        if st.button("🗑️ Clear All", type="secondary"):
            st.session_state.selected_actors = []
            st.rerun()
    
    else:
        st.info("No actors selected yet. Search and add actors from the other tabs.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>💡 Tip: Use AI recommendations combined with TMDB search for the best casting decisions.</p>
</div>
""", unsafe_allow_html=True)

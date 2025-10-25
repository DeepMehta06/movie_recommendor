import streamlit as slt
import pickle
import pandas as pd
import re
import requests
from difflib import get_close_matches

# Page configuration
slt.set_page_config(
    page_title="Movie Recommender System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
slt.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    h1 {
        color: #667eea;
        text-align: center;
        font-size: 3em;
        margin-bottom: 10px;
    }
    .subtitle {
        text-align: center;
        color: #a0a0a0;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# Load pickled data
movies_df = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity_list.pkl', 'rb'))

# OMDb API configuration (Free - Get your key from: http://www.omdbapi.com/apikey.aspx)
OMDB_API_KEY = "8fadb753"  # Your API key
OMDB_API_URL = "http://www.omdbapi.com/"

# Title and subtitle
slt.markdown("<h1>🎬 Movie Recommender System</h1>", unsafe_allow_html=True)
slt.markdown("<p class='subtitle'>Discover your next favorite movie based on what you love!</p>", unsafe_allow_html=True)

# Cache for movie details
@slt.cache_data(ttl=3600)
def fetch_movie_poster_omdb(movie_title):
    """Fetch movie poster and details from OMDb API"""
    try:
        # Make request to OMDb
        params = {
            'apikey': OMDB_API_KEY,
            't': movie_title,  # Search by title
            'type': 'movie'
        }
        
        response = requests.get(OMDB_API_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('Response') == 'True':
            poster = data.get('Poster', 'N/A')
            
            # OMDb returns 'N/A' if no poster
            if poster == 'N/A' or not poster:
                poster = f"https://via.placeholder.com/300x450/667eea/ffffff?text={movie_title[:20]}"
            
            return {
                'poster': poster,
                'year': data.get('Year', 'N/A'),
                'rating': data.get('imdbRating', 'N/A'),
                'runtime': data.get('Runtime', 'N/A'),
                'genre': data.get('Genre', 'N/A'),
                'plot': data.get('Plot', 'No plot available'),
                'director': data.get('Director', 'N/A'),
                'actors': data.get('Actors', 'N/A'),
                'status': 'success'
            }
        else:
            # Movie not found in OMDb
            return {
                'poster': f"https://via.placeholder.com/300x450/667eea/ffffff?text={movie_title[:20]}",
                'year': 'N/A',
                'rating': 'N/A',
                'runtime': 'N/A',
                'genre': 'N/A',
                'plot': 'Details not available',
                'director': 'N/A',
                'actors': 'N/A',
                'status': 'not_found'
            }
            
    except Exception as e:
        return {
            'poster': f"https://via.placeholder.com/300x450/667eea/ffffff?text=Error",
            'year': 'N/A',
            'rating': 'N/A',
            'runtime': 'N/A',
            'genre': 'N/A',
            'plot': f'Error: {str(e)}',
            'director': 'N/A',
            'actors': 'N/A',
            'status': 'error'
        }

# Create normalized title column
def normalize_title(s: str) -> str:
    """Normalize title: lowercase, remove non-alphanumeric characters"""
    s = str(s).lower()
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s

movies_df['title_norm'] = movies_df['title'].apply(normalize_title)

def recommend(title_query: str, k: int = 20):
    """Recommend k similar movies"""
    q = normalize_title(title_query)
    matches = movies_df[movies_df['title_norm'] == q]
    
    if matches.empty:
        candidates = movies_df['title_norm'].tolist()
        close = get_close_matches(q, candidates, n=5, cutoff=0.6)
        
        if close:
            suggestions = []
            for c in close:
                suggestions.append(movies_df.loc[movies_df['title_norm'] == c, 'title'].iloc[0])
            return None, suggestions
        else:
            return None, []
    
    movie_index = matches.index[0]
    top = sorted(enumerate(similarity[movie_index]), key=lambda x: x[1], reverse=True)[1:k+1]
    
    recommendations = []
    for idx, score in top:
        movie_data = movies_df.iloc[idx]
        recommendations.append({
            'title': movie_data['title'],
            'similarity': score
        })
    
    return recommendations, None

# Sidebar
with slt.sidebar:
    slt.header("⚙️ Settings")
    num_recommendations = slt.slider(
        "Number of recommendations",
        min_value=5,
        max_value=25,
        value=20,
        step=5
    )
    
    slt.markdown("---")
    slt.markdown("### 🔍 API Test")
    if slt.button("Test OMDb API", use_container_width=True):
        with slt.spinner("Testing..."):
            test_result = fetch_movie_poster_omdb("Avatar")
            if test_result['status'] == 'success':
                slt.success("✅ API Working!")
                slt.image(test_result['poster'], width=150)
                slt.write(f"**Year:** {test_result['year']}")
                slt.write(f"**Rating:** {test_result['rating']}/10")
            else:
                slt.error(f"❌ API Error: {test_result['status']}")
    
    slt.markdown("---")
    slt.markdown("### About")
    slt.info(
        "This recommender uses **OMDb API** for movie posters and details. "
        "Get your free API key at http://www.omdbapi.com/"
    )
    slt.markdown("---")
    slt.markdown("Made with ❤️ using Streamlit")

# Main UI
col1, col2, col3 = slt.columns([1, 3, 1])
with col2:
    selected_movie_name = slt.selectbox(
        '🔍 Select a movie you like:',
        movies_df['title'].values,
        help="Choose a movie and we'll recommend similar ones!"
    )
    
    recommend_button = slt.button('🎬 Get Recommendations', use_container_width=True, type="primary")

if recommend_button:
    with slt.spinner('🎥 Finding perfect recommendations for you...'):
        recommendations, suggestions = recommend(selected_movie_name, k=num_recommendations)
    
    if recommendations:
        slt.markdown(f"### 🎯 Top {len(recommendations)} Movies Similar to '{selected_movie_name}'")
        slt.markdown("---")
        
        # Display in grid (4 columns for better poster display)
        for i in range(0, len(recommendations), 4):
            cols = slt.columns(4)
            for j, col in enumerate(cols):
                if i + j < len(recommendations):
                    movie = recommendations[i + j]
                    with col:
                        # Fetch movie details from OMDb
                        details = fetch_movie_poster_omdb(movie['title'])
                        
                        # Display poster
                        slt.image(details['poster'], use_container_width=True)
                        
                        # Movie title
                        slt.markdown(f"**{i+j+1}. {movie['title']}**")
                        
                        # Similarity score
                        similarity_percent = round(movie['similarity'] * 100, 1)
                        slt.progress(movie['similarity'])
                        slt.caption(f"🎯 Match: {similarity_percent}%")
                        
                        # Year and Rating
                        if details['year'] != 'N/A':
                            slt.caption(f"📅 {details['year']}")
                        
                        if details['rating'] != 'N/A':
                            slt.caption(f"⭐ {details['rating']}/10")
                        
                        # Genre
                        if details['genre'] != 'N/A':
                            slt.caption(f"🎭 {details['genre']}")
                        
                        # Expandable details
                        with slt.expander("📖 More Info"):
                            if details['plot'] != 'No plot available':
                                slt.write(f"**Plot:** {details['plot']}")
                            if details['director'] != 'N/A':
                                slt.write(f"**Director:** {details['director']}")
                            if details['runtime'] != 'N/A':
                                slt.write(f"**Runtime:** {details['runtime']}")
        
        slt.success(f"✨ Found {len(recommendations)} amazing recommendations for you!")
        
    elif suggestions:
        slt.warning(f"⚠️ Title not found: '{selected_movie_name}'. Did you mean:")
        for movie in suggestions:
            slt.write(f"• {movie}")
    else:
        slt.error(f"❌ No matches found for '{selected_movie_name}'. Try another title.")

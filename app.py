import streamlit as slt
import pickle
import pandas as pd
import re
from difflib import get_close_matches
import requests
from urllib.parse import quote

# Page configuration
slt.set_page_config(
    page_title="Movie Recommender System",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS for better UI with Lucide icons
slt.markdown("""
    <style>
    @import url('https://unpkg.com/lucide-static@latest/font/lucide.css');
    
    .main {
        background: linear-gradient(135deg, #0e1117 0%, #1a1d29 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1a1d29 100%);
    }
    h1 {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 3.5rem !important;
        margin-bottom: 2rem;
    }
    .movie-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
    }
    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        border-color: rgba(102, 126, 234, 0.5);
    }
    .movie-title {
        font-size: 1.1rem;
        font-weight: bold;
        color: #667eea;
        margin: 0.5rem 0;
        text-align: center;
        min-height: 2.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .movie-info {
        font-size: 0.85rem;
        color: #a0aec0;
        margin: 0.2rem 0;
        text-align: center;
    }
    .similarity-score {
        color: #48bb78;
        font-weight: bold;
        text-align: center;
    }
    .poster-container {
        width: 100%;
        height: 350px;
        overflow: hidden;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        background: rgba(0, 0, 0, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .poster-container img {
        width: 100%;
        height: 100%;
        object-fit: contain;
    }
    .info-row {
        display: flex;
        justify-content: space-around;
        margin: 0.5rem 0;
        gap: 0.5rem;
    }
    .info-badge {
        background: rgba(102, 126, 234, 0.2);
        padding: 0.3rem 0.6rem;
        border-radius: 8px;
        font-size: 0.85rem;
        flex: 1;
        text-align: center;
    }
    /* Lucide icon styles */
    .lucide-icon {
        display: inline-block;
        width: 1em;
        height: 1em;
        vertical-align: middle;
        margin-right: 0.25rem;
    }
    </style>
""", unsafe_allow_html=True)

# OMDb API Configuration
OMDB_API_KEY = "8fadb753"  # Your API key

# Load pickled data
movies_df = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity_list.pkl', 'rb'))

slt.title("Movie Recommender System")
slt.caption("Powered by Content-Based Filtering & Machine Learning")

# Create normalized title column for flexible matching
def normalize_title(s: str) -> str:
    """Normalize title: lowercase, remove non-alphanumeric characters"""
    s = str(s).lower()
    s = re.sub(r"[^a-z0-9]+", "", s)  # Keep only alphanumerics
    return s

# Add normalized titles to dataframe
movies_df['title_norm'] = movies_df['title'].apply(normalize_title)

def search_by_person(person_name: str, search_type: str = "both"):
    """
    Search for movies by actor or director name.
    
    Parameters:
    - person_name: Name of actor or director (e.g., "Tom Holland", "Christopher Nolan")
    - search_type: "actor", "director", or "both"
    
    Returns:
    - List of dictionaries with movie titles
    """
    # Normalize the search name (remove spaces, lowercase)
    normalized_name = normalize_title(person_name)
    
    results = []
    
    # Search in cast (actors)
    if search_type in ["actor", "both"]:
        for idx, row in movies_df.iterrows():
            if isinstance(row['cast'], list):
                # Check if any cast member matches
                for actor in row['cast']:
                    if normalized_name in normalize_title(actor):
                        results.append({
                            'title': row['title'],
                            'match_type': 'Actor',
                            'match_name': actor
                        })
                        break
    
    # Search in crew (directors)
    if search_type in ["director", "both"]:
        for idx, row in movies_df.iterrows():
            if isinstance(row['crew'], list):
                # Check if any crew member matches
                for director in row['crew']:
                    if normalized_name in normalize_title(director):
                        # Check if not already added
                        if not any(r['title'] == row['title'] for r in results):
                            results.append({
                                'title': row['title'],
                                'match_type': 'Director',
                                'match_name': director
                            })
                        break
    
    return results

@slt.cache_data(ttl=3600)
def fetch_movie_details(movie_title: str):
    """
    Fetch movie details from OMDb API including poster, rating, plot, director, and actors.
    Returns a dictionary with movie information.
    """
    try:
        encoded_title = quote(movie_title)
        url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={encoded_title}&type=movie"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('Response') == 'True':
                return {
                    'poster': data.get('Poster', 'N/A'),
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
                return {'status': 'not_found', 'error': data.get('Error', 'Movie not found')}
        else:
            return {'status': 'error', 'error': f'HTTP {response.status_code}'}
            
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def recommend(title_query: str, k: int = 20):
    """
    Recommend k similar movies based on the input title.
    
    Parameters:
    - title_query: Movie title (case-insensitive, flexible spelling)
    - k: Number of recommendations to return (default: 20)
    
    Returns:
    - List of dictionaries with movie titles and similarity scores
    """
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
        recommendations.append({
            'title': movies_df.iloc[idx]['title'],
            'similarity': round(score * 100, 1)
        })
    
    return recommendations, None

# Sidebar for settings
with slt.sidebar:
    slt.header("⚙ Settings")
    num_recommendations = slt.slider(
        "Number of recommendations:",
        min_value=5,
        max_value=25,
        value=20,
        step=5
    )
    
    slt.markdown("---")
    slt.markdown("### About")
    slt.info(
        "This movie recommender uses content-based filtering "
        "to suggest movies similar to your selection based on "
        "genres, cast, crew, and plot keywords."
    )

# Main content
slt.markdown("---")

# Mode selector
search_mode = slt.radio(
    "Choose search mode:",
    [":material/movie: Recommend Similar Movies", ":material/person: Search by Actor/Director"],
    horizontal=True
)

slt.markdown("---")

if search_mode == ":material/movie: Recommend Similar Movies":
    # Original movie recommendation interface
    selected_movie_name = slt.selectbox(
        'Select a movie you like:',
        movies_df['title'].values,
        help="Choose a movie to get similar recommendations"
    )

    if slt.button('Get Recommendations', type="primary", use_container_width=True, icon=":material/search:"):
        with slt.spinner(f"Finding movies similar to '{selected_movie_name}'..."):
            recommendations, suggestions = recommend(selected_movie_name, k=num_recommendations)
    
        if recommendations:
            slt.success(f"Found {len(recommendations)} movies similar to **'{selected_movie_name}'**")
            slt.markdown("---")
            
            # Display recommendations in a 4-column grid
            cols_per_row = 4
            for i in range(0, len(recommendations), cols_per_row):
                cols = slt.columns(cols_per_row)
                
                for j, col in enumerate(cols):
                    if i + j < len(recommendations):
                        rec = recommendations[i + j]
                        movie_title = rec['title']
                        similarity_score = rec['similarity']
                        
                        with col:
                            # Fetch movie details
                            details = fetch_movie_details(movie_title)
                            
                            # Container for the movie card
                            with slt.container():
                                # Display poster with fixed height
                                if details.get('status') == 'success' and details['poster'] != 'N/A':
                                    slt.markdown(
                                        f'<div class="poster-container"><img src="{details["poster"]}" alt="{movie_title}"></div>',
                                        unsafe_allow_html=True
                                    )
                                else:
                                    # Placeholder if no poster available
                                    slt.markdown(
                                        f"""
                                        <div class="poster-container" style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                                    display: flex; align-items: center; justify-content: center;'>
                                            <p style='color: white; text-align: center; font-size: 1rem; padding: 1rem; font-weight: bold;'>
                                                {movie_title}
                                            </p>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                                
                                # Movie title
                                slt.markdown(f'<div class="movie-title">{movie_title}</div>', unsafe_allow_html=True)
                                
                                if details.get('status') == 'success':
                                    # Year and Rating in a row
                                    slt.markdown(
                                        f'<div class="info-row">'
                                        f'<div class="info-badge"><i data-lucide="calendar" class="lucide-icon"></i> {details["year"]}</div>'
                                        f'<div class="info-badge"><i data-lucide="star" class="lucide-icon"></i> {details["rating"]}</div>'
                                        f'</div>'
                                        f'<script src="https://unpkg.com/lucide@latest"></script>'
                                        f'<script>lucide.createIcons();</script>',
                                        unsafe_allow_html=True
                                    )
                                    
                                    slt.progress(similarity_score / 100)
                                    slt.markdown(f'<p class="similarity-score"><i data-lucide="target" class="lucide-icon"></i> {similarity_score}% Match</p>', unsafe_allow_html=True)
                                    
                                    # View Details button with popover
                                    with slt.popover("View Details", use_container_width=True):
                                        slt.markdown(f"### {movie_title}")
                                        
                                        # Show poster in popover too
                                        if details['poster'] != 'N/A':
                                            slt.image(details['poster'], width=200)
                                        
                                        slt.markdown(f"**Year:** {details['year']}")
                                        slt.markdown(f"**IMDb Rating:** {details['rating']}/10")
                                        slt.markdown(f"**Runtime:** {details['runtime']}")
                                        slt.markdown(f"**Genre:** {details['genre']}")
                                        slt.markdown(f"**Match Score:** {similarity_score}%")
                                        
                                        slt.markdown("---")
                                        slt.markdown("**Plot Summary:**")
                                        slt.write(details['plot'])
                                        
                                        slt.markdown("---")
                                        slt.markdown(f"**Director:** {details['director']}")
                                        slt.markdown(f"**Cast:** {details['actors']}")
                                else:
                                    # Just show similarity if API fails
                                    slt.progress(similarity_score / 100)
                                    slt.markdown(f'<p class="similarity-score"><i data-lucide="target" class="lucide-icon"></i> {similarity_score}% Match</p>', unsafe_allow_html=True)
                                    slt.caption("Details unavailable")
                                
                                slt.markdown("<br>", unsafe_allow_html=True)
            
        elif suggestions:
            slt.warning(f"Title not found: '{selected_movie_name}'. Did you mean:")
            for movie in suggestions:
                slt.write(f"• {movie}")
        else:
            slt.error(f"No matches found for '{selected_movie_name}'. Try another title.")

else:
    # Person search interface
    slt.markdown("### Search for Movies by Actor or Director")
    
    col1, col2 = slt.columns([3, 1])
    with col1:
        person_name = slt.text_input(
            "Enter actor or director name:",
            placeholder="e.g., Tom Holland, Christopher Nolan, Scarlett Johansson"
        )
    with col2:
        search_type = slt.selectbox(
            "Search in:",
            ["Both", "Actors", "Directors"]
        )
    
    if slt.button('Search Movies', type="primary", use_container_width=True, icon=":material/search:"):
        if person_name.strip():
            with slt.spinner(f"Searching for movies with '{person_name}'..."):
                search_type_param = search_type.lower().rstrip('s') if search_type != "Both" else "both"
                results = search_by_person(person_name, search_type_param)
            
            if results:
                slt.success(f"Found **{len(results)}** movies with **{person_name}**")
                slt.markdown("---")
                
                # Display results in a 4-column grid
                cols_per_row = 4
                for i in range(0, len(results), cols_per_row):
                    cols = slt.columns(cols_per_row)
                    
                    for j, col in enumerate(cols):
                        if i + j < len(results):
                            result = results[i + j]
                            movie_title = result['title']
                            match_type = result['match_type']
                            match_name = result['match_name']
                            
                            with col:
                                # Fetch movie details
                                details = fetch_movie_details(movie_title)
                                
                                # Container for the movie card
                                with slt.container():
                                    # Display poster
                                    if details.get('status') == 'success' and details['poster'] != 'N/A':
                                        slt.markdown(
                                            f'<div class="poster-container"><img src="{details["poster"]}" alt="{movie_title}"></div>',
                                            unsafe_allow_html=True
                                        )
                                    else:
                                        # Placeholder
                                        slt.markdown(
                                            f"""
                                            <div class="poster-container" style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                                        display: flex; align-items: center; justify-content: center;'>
                                                <p style='color: white; text-align: center; font-size: 1rem; padding: 1rem; font-weight: bold;'>
                                                    {movie_title}
                                                </p>
                                            </div>
                                            """,
                                            unsafe_allow_html=True
                                        )
                                    
                                    # Movie title
                                    slt.markdown(f'<div class="movie-title">{movie_title}</div>', unsafe_allow_html=True)
                                    
                                    # Show match type badge
                                    match_icon = '<i data-lucide="user" class="lucide-icon"></i>' if match_type == "Actor" else '<i data-lucide="video" class="lucide-icon"></i>'
                                    slt.markdown(
                                        f'<div class="info-badge" style="width: 100%; background: rgba(102, 126, 234, 0.3);">'
                                        f'{match_icon} {match_type}: {match_name}'
                                        f'</div>'
                                        f'<script src="https://unpkg.com/lucide@latest"></script>'
                                        f'<script>lucide.createIcons();</script>',
                                        unsafe_allow_html=True
                                    )
                                    
                                    if details.get('status') == 'success':
                                        # Year and Rating
                                        slt.markdown(
                                            f'<div class="info-row">'
                                            f'<div class="info-badge"><i data-lucide="calendar" class="lucide-icon"></i> {details["year"]}</div>'
                                            f'<div class="info-badge"><i data-lucide="star" class="lucide-icon"></i> {details["rating"]}</div>'
                                            f'</div>'
                                            f'<script src="https://unpkg.com/lucide@latest"></script>'
                                            f'<script>lucide.createIcons();</script>',
                                            unsafe_allow_html=True
                                        )
                                        
                                        # View Details button with popover
                                        with slt.popover("View Details", use_container_width=True):
                                            slt.markdown(f"### {movie_title}")
                                            
                                            if details['poster'] != 'N/A':
                                                slt.image(details['poster'], width=200)
                                            
                                            slt.markdown(f"**Year:** {details['year']}")
                                            slt.markdown(f"**IMDb Rating:** {details['rating']}/10")
                                            slt.markdown(f"**Runtime:** {details['runtime']}")
                                            slt.markdown(f"**Genre:** {details['genre']}")
                                            
                                            slt.markdown("---")
                                            slt.markdown("**Plot Summary:**")
                                            slt.write(details['plot'])
                                            
                                            slt.markdown("---")
                                            slt.markdown(f"**Director:** {details['director']}")
                                            slt.markdown(f"**Cast:** {details['actors']}")
                                    else:
                                        slt.caption("Details unavailable")
                                    
                                    slt.markdown("<br>", unsafe_allow_html=True)
            else:
                slt.warning(f"No movies found with **{person_name}**. Try another name or check spelling.")
        else:
            slt.error("Please enter an actor or director name.")

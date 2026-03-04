import streamlit as st
import pandas as pd
import pickle
import requests
import bz2  # Compressed file handle karne ke liye

# 1. FULL ANIMATION & UI SETTINGS
st.set_page_config(page_title="Movie Recommender", layout="wide")

st.markdown("""
<style>
    /* Poster zoom animation */
    .stImage > img {
        border-radius: 10px;
        transition: transform 0.4s ease-in-out;
    }
    .stImage > img:hover {
        transform: scale(1.1);
        box-shadow: 0px 10px 20px rgba(0,0,0,0.5);
    }
    /* Smooth fade-in animation for page load */
    .main {
        animation: fadeIn 1.5s;
    }
    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
    /* Text styling */
    .movie-title {
        font-size: 14px;
        font-weight: bold;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

session = requests.Session()


# 2. POSTER FETCHING WITH CACHE (Lagging fix)
@st.cache_data
def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=440e7cb5492bf71984b3b0e73c198c4c&language=en-US".format(
        movie_id)
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = session.get(url, headers=headers, timeout=5)
        data = response.json()
        return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    except:
        return "https://via.placeholder.com/500x750?text=No+Poster"


# 3. LOADING FILES (Using .pbz2 to bypass GitHub size limits)
@st.cache_resource
def load_data():
    # Load movies dictionary
    movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)

    # Load compressed similarity file
    with bz2.BZ2File('similarity.pbz2', 'rb') as f:
        similarity = pickle.load(f)

    return movies, similarity


movies, similarity = load_data()


# 4. RECOMMENDATION LOGIC
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_poster = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_poster.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_poster


# 5. USER INTERFACE
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    'Search for a movie you like:',
    movies['title'].values
)

if st.button('Show Recommendation'):
    with st.spinner('Generating magic recommendations...'):
        names, posters = recommend(selected_movie_name)

    # Display in 5 columns
    col1, col2, col3, col4, col5 = st.columns(5)

    cols = [col1, col2, col3, col4, col5]
    for i in range(5):
        with cols[i]:
            st.markdown(f"<p class='movie-title'>{names[i]}</p>", unsafe_allow_html=True)
            st.image(posters[i])
import streamlit as st
import pandas as pd
from joblib import load
from sklearn.metrics.pairwise import cosine_similarity

# Set Streamlit page configuration
st.set_page_config(
    page_title="Moovie App",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded",
)
# title and intro
st.title("🎥 Movie Recommender by Moovie App")
st.markdown("""
Welcome to **Movie App**, your personal movie recommender! 🎥🍿  
Dive into a world of entertainment and discover movies tailored to your unique tastes.  
Here's how it works:  

- 🌟 **Select a Movie**: Pick a movie you love.  
- 🎯 **Set Recommendations**: Choose how many movie recommendations you'd like.  
- 🚀 **Explore**: Get personalized recommendations and explore new favorites!  

Sit back, relax, and let **Movie App** guide you to your next movie adventure!  
""")
st.markdown("""---""")

# Load model
df = load('df_model.joblib')
tftdf_model = load('movie_rec.joblib')

# title to index
title_to_index = pd.Series(df.index, index=df['title'].str.lower())

def recommend(title_data, count):
    lis = []
    for i in title_data:
        movie_id = title_to_index[i.lower()]
        lis.append(tftdf_model[movie_id])

    result = sum(lis) / len(title_data)
    scores = cosine_similarity(result, tftdf_model)
    df['scores'] = scores.flatten()

    recommended_movie_id = (-df['scores']).argsort()[len(title_data):count + len(title_data)]
    return df['title'].iloc[recommended_movie_id]

def movie_title_display(recommended_movie_titles):
    recommendations = []
    for i, movie_title in enumerate(recommended_movie_titles, start=1):
        recommended_movie = df[df['title'] == movie_title].iloc[0]

        recommendations.append({
            'Rank': i,
            'Title': movie_title,
            'Popularity': recommended_movie['popularity'],
            'Vote_avg': recommended_movie['vote_average'],
            'Score': recommended_movie['scores']
        })
    return recommendations

# Placeholder for selected movies
if 'movie_lis' not in st.session_state:
    st.session_state.movie_lis = []

# Create columns for selection
col1, col2 = st.columns(2)
selected_movie = col1.selectbox("Select a Movie", df['title'].values)
count = col2.number_input("Number of Recommendations", min_value=1, max_value=20, value=10)

# Buttons for movie management
col99, col6, col7, col8 = st.columns([1, 1, 1, 4])
if col99.button("⬇ Add Movie"):
    if selected_movie not in st.session_state.movie_lis:
        st.session_state.movie_lis.append(selected_movie)
        st.success(f"Added '{selected_movie}' successfully!")
    else:
        st.warning("Movie already in the list!")

if col6.button('⬆ Delete Last Movie'):
    if len(st.session_state.movie_lis) > 0:
        st.session_state.movie_lis.pop()
        st.success("Removed last movie!")
    else:
        st.warning("No movies to remove!")

if col7.button('🚫 Clear All Movies'):
    if len(st.session_state.movie_lis) > 0:
        st.session_state.movie_lis.clear()
        st.success("All movies cleared!")
    else:
        st.warning("No movies to remove!")

placeholder = st.empty()

# Placeholder for movie list display
if len(st.session_state.movie_lis) > 0 :
    st.markdown("""---""")
    col3, col4, col5 = st.columns([1, 2, 2])
    col3.write("Movies in your list")
    col3.dataframe(st.session_state.movie_lis[:10], width=300, height=400)

    # Show recommendations
    if st.button('💡 Show Recommendations'):
        recommended_movie_titles = recommend(st.session_state.movie_lis, count)
        df_recommend = pd.DataFrame(movie_title_display(recommended_movie_titles))

        # Display the recommendation message
        placeholder.success(f"Recommendations for {count} movies based on : {', '.join(st.session_state.movie_lis)}")

        # Show top recommended movies
        col4.write(f"Top {count} Recommended Movies")
        col4.dataframe(df_recommend.set_index('Rank'), width=600, height=400)

        # Show recommended movie scores
        col5.write(f"Recommended Movies Scores by Cosine Similarity")
        col5.bar_chart(df_recommend.set_index('Title')['Score'].sort_values(ascending=False), horizontal=True, width=600, height=400)

# Footer with additional information
st.markdown("""---
**🌟 Explore new worlds, one movie at a time!**  
💡 *Built with Streamlit* | 🚀 *Your predictive companion*
""")

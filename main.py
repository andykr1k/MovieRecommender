import streamlit as st
import recommend
import requests
import json
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from nltk.stem.porter import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity

def read():
    netflix_movies_df = pd.read_csv('./data/netflix_titles.csv')
    amazon_movies_df = pd.read_csv('./data/amazon_titles.csv')
    disney_movies_df = pd.read_csv('./data/disney_titles.csv')
    hbo_movies_df = pd.read_csv('./data/hbo_titles.csv')
    hulu_movies_df = pd.read_csv('./data/hulu_titles.csv')
    paramount_movies_df = pd.read_csv('./data/paramount_titles.csv')

    netflix_movies_df['platform'] = 'Netflix'
    disney_movies_df['platform'] = 'Disney Plus'
    paramount_movies_df['platform'] = 'Paramount Plus'
    hulu_movies_df['platform'] = 'Hulu'
    hbo_movies_df['platform'] = 'HBO Max'
    amazon_movies_df['platform'] = 'Amazon Prime'

    movies_df = netflix_movies_df._append(amazon_movies_df, ignore_index = True)._append(hulu_movies_df, ignore_index = True)._append(hbo_movies_df, ignore_index = True)._append(paramount_movies_df, ignore_index = True)._append(disney_movies_df, ignore_index = True)

    movies_df = movies_df[movies_df['production_countries'] == '[\'US\']']

    movies_df['production_countries'] = movies_df['production_countries'].str.replace('[', '')
    movies_df['production_countries'] = movies_df['production_countries'].str.replace(']', '')
    movies_df['production_countries'] = movies_df['production_countries'].str.replace('\'', '')

    movies_df = movies_df[['title', 'type', 'description', 'genres','release_year', 'imdb_score', 'tmdb_score', 'platform']]
    
    movies_df.dropna(inplace=True)

    movies_df = movies_df.groupby(['title', 'type', 'description', 'genres', 'release_year', 'tmdb_score', 'imdb_score'])['platform'].apply(', '.join).reset_index()

    return movies_df

def train(movies_df):
    cv = CountVectorizer(max_features=50000,stop_words='english')

    def combine_features(data):
        features=[]
        for i in range(0, data.shape[0]):
            features.append(data['description'][i] + ' ' + data['genres'][i] + ' ' + str(data['release_year'][i]))
        return features
    
    movies_df['combined'] = combine_features(movies_df)

    # ps = PorterStemmer()

    # def stem(text):
    #     y=[]
    #     for i in text.split():
    #         y.append(ps.stem(i))
    #     return " ".join(y)

    # movies_df['description'] = movies_df['description'].apply(stem)

    vectors = cv.fit_transform(movies_df['combined']).toarray()

    similarity = cosine_similarity(vectors)

    return similarity

def recommend_movie(similarity, movies_df, film_type, movie, platforms):
    movie_index = movies_df[movies_df['title']==movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:25]

    recommends = []
    count = 0

    for i in movie_list:
        if count != 5:
            if movies_df.iloc[i[0]].platform in platforms:
                if movies_df.iloc[i[0]].type == film_type:
                    recommends.append(movies_df.iloc[i[0]].title)
                    count += 1
        else:
            break
    return recommends

def recommendation_accuracy(recommends, movies_df, type, title, platforms):
    total = len(recommends)
    count = 0
    for x in recommends:
        if movies_df[movies_df['title']==x].type.values[0] == type:
            count += 0.5
        if movies_df[movies_df['title']==x].platform.values[0] in platforms:
            count += 0.5
    return "%.0f%%" % (100 * count/total)

def recommend_request(film_type, movie, platforms):
    movies_df = read()
    similarity = train(movies_df)

    platforms = platforms.split("-")

    recommends = recommend_movie(similarity, movies_df, str(film_type), str(movie), platforms)
    acc = recommendation_accuracy(recommends, movies_df, str(film_type), str(movie), platforms)
    return recommends, acc

def main():
    st.set_page_config(page_title="PictureLock", page_icon="🎞️", menu_items=None)
    st.header("🎞️ PictureLock")
    st.write("Sneak Peak of Our In-House Movie Recommender!")
    hide_streamlit_style = """
            <style>
            MainMenu {visibility: hidden;}
            </style>
            """
    ft = """
    <style>
    a:link , a:visited{
    color: #BFBFBF;  /* theme's text color hex code at 75 percent brightness*/
    background-color: transparent;
    text-decoration: none;
    }

    a:hover,  a:active {
    color: #0283C3; /* theme's primary color*/
    background-color: transparent;
    text-decoration: underline;
    }

    #page-container {
      position: relative;
      min-height: 0vh;
    }

    footer{
        visibility:hidden;
    }

    .footer {
    position: fixed;
    display: flex;
    justify-items: center;
    bottom: 0;
    width: 100%;
    background-color: transparent;
    color: #808080; /* theme's text color hex code at 50 percent brightness*/
    text-align: left; /* you can replace 'left' with 'center' or 'right' if you want*/
    }
    </style>

    <div id="page-container">

    <div class="footer">
    <p style='font-size: 0.875em;'>Made
    with <img src="https://em-content.zobj.net/source/skype/289/red-heart_2764-fe0f.png" alt="heart" height= "10"/>&nbsp;by <a style='display: inline; text-align: left;' href="https://github.com/andykr1k/Picturelock" target="_blank">PictureLock</a></p>
    </div>

    </div>
    """
    st.write(ft, unsafe_allow_html=True)
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    movies_df = recommend.read()

    film_type = st.selectbox('Movie or TV Show?', ['MOVIE', 'SHOW'])
    platforms = st.multiselect('What platforms do you have access to?', ['Amazon Prime', 'Disney Plus', 'HBO Max', 'Hulu', 'Netflix', 'Paramount Plus'])
    movie = st.selectbox('Select Similar Movie', movies_df['title'])

    if st.button('Recommend Movie'):
        recommends, acc = recommend_request(film_type, movie, platforms)
        df = pd.DataFrame(recommends, columns=['Recommended Movies'])
        df.index = np.arange(1, len(df) + 1)
        st.dataframe(df, use_container_width=True)
        st.write("Confidence: ", acc)

if __name__ == '__main__':
    main()
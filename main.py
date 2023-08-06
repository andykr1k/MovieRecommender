import streamlit as st
import recommend
import requests
import json
import pandas as pd
import numpy as np

def recommend_request(film_type, movie, platforms):
    base = 'http://ec2-52-14-147-22.us-east-2.compute.amazonaws.com:8080/recommend/'
    url = base + film_type + '/' + movie + '/'
    platforms_string = ''
    for platform in range(len(platforms)):
        platforms_string += platforms[platform]
        if platform != len(platforms) - 1:
            platforms_string += '-'
    url = url + platforms_string
    print("URL: " + url)
    r = requests.get(url)
    return r

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
        r = recommend_request(film_type, movie, platforms)
        j = json.loads(r.text)
        df = pd.DataFrame(j['recommendations'], columns=['Recommended Movies'])
        df.index = np.arange(1, len(df) + 1)
        st.dataframe(df, use_container_width=True)
        # st.write("Confidence: ", j['accuracy'])

if __name__ == '__main__':
    main()
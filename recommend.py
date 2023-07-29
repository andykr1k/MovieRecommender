
import numpy as np
import pandas as pd
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

    movies_df = movies_df[['id', 'title', 'type', 'description', 'genres', 'platform']]

    movies_df.dropna(inplace=True)

    movies_df = movies_df.groupby(['id', 'title', 'type', 'description', 'genres'])['platform'].apply(', '.join).reset_index()

    return movies_df

def train(movies_df):
    cv = CountVectorizer(max_features=50000,stop_words='english')

    cv.fit_transform(movies_df['description']).toarray().shape

    vectors = cv.fit_transform(movies_df['description']).toarray()

    ps = PorterStemmer()

    def stem(text):
        y=[]
        for i in text.split():
            y.append(ps.stem(i))
        return " ".join(y)

    movies_df['description'] = movies_df['description'].apply(stem)

    similarity = cosine_similarity(vectors)

    sorted(list(enumerate(similarity[0])), reverse=True, key=lambda x:x[1])[1:6]

    return similarity

def recommend(similarity, movies_df, film_type, movie, platforms):
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


def main(film_type, movie, platforms):
    movies_df = read()
    similarity = train(movies_df)
    recommends = recommend(similarity, movies_df, film_type, movie, platforms)
    acc = recommendation_accuracy(recommends, movies_df, film_type, movie, platforms)
    return recommends, acc

if __name__ == '__main__':
    main()
from heapq import nlargest

import numpy as np
from pyxdameraulevenshtein import damerau_levenshtein_distance
#
import pickle
#


class Recommender:
    def __init__(self):

        self.V = np.load('./V.npy')
        self.title_to_id = pickle.load(open('title_to_id.p', 'rb'))
        self.movieId_to_column = pickle.load(open('movieId_to_column.p', 'rb'))
        self.column_to_movieId = pickle.load(open('column_to_movieId.p', 'rb'))
        self.id_to_title = pickle.load(open('id_to_title.p', 'rb'))
        self.movies = pickle.load(open('movies.p', 'rb'))
        self.genre_dict = pickle.load(open('genre_dict.p', 'rb'))


    def make_recommendations(self, movie_ratings):
        query_ratings = []
        input_columns = []
        for movie, rating in movie_ratings.items():
            movieId = self.title_to_id[movie]
            movie_column = self.movieId_to_column[movieId]
            input_columns.append(movie_column)

        for j in range(self.V.shape[1]):
            v_query = self.V[:, j]
            query_rating = 0
            for movie, rating in movie_ratings.items():
                movieId = self.title_to_id[movie]
                movie_column = self.movieId_to_column[movieId]
                v_seen = self.V[:, movie_column]
                sim = self._get_similarity(v_query, v_seen, j, movie_column, rating)
                query_rating += rating*sim

            query_ratings.append(query_rating)

        recommended_columns = nlargest(
            15,
            [
                (rating, movie_column)
                for movie_column, rating in enumerate(query_ratings)
                if movie_column not in input_columns
            ],
        )

        recommended_movies = [self.column_to_movieId[r[1]] for r in recommended_columns]
        recommended_movies = [self.id_to_title[r] for r in recommended_movies]
        return recommended_movies

    def _get_similarity(self, v_query, v_seen, query_column, seen_column, rating):
        cos_dist = (
                v_query.dot(v_seen)
                / np.linalg.norm(v_query)
                / np.linalg.norm(v_seen)
        )
        if rating == 1:
            common_genres = self.genre_dict[query_column].intersection(
                self.genre_dict[seen_column]
            )
            scale = 0.7 + 0.3 * min((len(common_genres), 2))
            cos_dist *= scale

        return cos_dist

    #Should movie search into another module
    def find_movie_matches(self, input_str):
        input_str = input_str.lower()
        input_title = input_str.split('"')[1].strip()
        input_title_split = input_title.split()
        matches, edit1, edit2, edit3 = [], [], [], []
        for title in self.movies:
            no_date_title = title[:-7].lower().strip()
            readable_title = self.make_readable(no_date_title)
            if input_title in [no_date_title, readable_title]:
                return [title]
            flag = True
            for word in input_title_split:
                if word not in no_date_title:
                    flag = False
                    break
            if flag:
                matches.append(title)
            if "Terminator, The" in title:
                print(input_title, readable_title)
            edit_distance = damerau_levenshtein_distance(input_title, readable_title)
            if edit_distance==1:
                edit1.append(title)
            elif edit_distance==2:
                edit2.append(title)
            elif edit_distance==3:
                edit3.append(title)
        if len(matches)>0:
            return matches
        else:
            edit_distances = edit1 + edit2 + edit3
            return edit_distances[:6]

    def make_readable(self, input_str):
        """Transforms titles like 'Terminator, The' -> 'The Terminator'"""
        comma_split = input_str.split(',')
        if len(comma_split)>1 and ' ' not in comma_split[-1].strip():
            return "".join([comma_split[-1].strip(), ' ', *comma_split[:-1]])
        return input_str
        




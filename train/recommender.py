import random
import os
from os.path import isfile
from heapq import nlargest

import numpy as np
import pandas as pd
import scipy as sp
from scipy.sparse import coo_matrix
from scipy.sparse import linalg

#
import pickle
#


class Recommender:
    def __init__(
        self,
        rating_path,
        movie_path,
        train_path="./data/train.npz",
        val_path="./data/val.npz",
        test_path="./data/test.npz",
        V_load_path=None,
        U_save_path="./U.npy",
        V_save_path="./V.npy",
        seed=1,
    ):
        (
            train_dataset,
            val_dataset,
            test_dataset,
            column_to_movieId,
            movieId_to_column,
        ) = self._get_dataset(rating_path, train_path, val_path, test_path, seed)
        self.train_dataset = train_dataset
        self.val_dataset = val_dataset
        self.test_dataset = test_dataset
        self.num_train = len(self.train_dataset.nonzero()[0])
        self.num_val = len(self.val_dataset.nonzero()[0])
        self.num_test = len(self.test_dataset.nonzero()[0])
        self.column_to_movieId = column_to_movieId
        self.movieId_to_column = movieId_to_column

        id_to_title, title_to_id, genre_dict = self._get_movie_dicts(movie_path)
        self.id_to_title = id_to_title
        self.title_to_id = title_to_id
        self.genre_dict = genre_dict
        self.movies = id_to_title.values()

        if V_load_path is not None:
            self.V = np.load(V_load_path)
        else:
            __, self.V = self._get_UV(U_save_path, V_save_path)

        #
        pickle.dump(title_to_id, open('title_to_id.p', 'wb'))
        pickle.dump(movieId_to_column, open('movieId_to_column.p', 'wb'))
        pickle.dump(column_to_movieId, open('column_to_movieId.p', 'wb'))
        pickle.dump(id_to_title, open('id_to_title.p', 'wb'))
        pickle.dump(list(self.movies), open('movies.p', 'wb'))
        pickle.dump(self.genre_dict, open('genre_dict.p', 'wb'))
        



    def _get_movie_dicts(self, path):
        # list of tuples (user, item, rating)
        data = pd.read_csv(path)
        # Strips the newline character
        movies, titles = data["movieId"], data["title"]
        id_to_title = dict(zip(movies, titles))
        title_to_id = dict(zip(titles, movies))
        genre_dict = self._get_genre_dict(path)
        return id_to_title, title_to_id, genre_dict

    def _get_genre_dict(self, path):
        df = pd.read_csv(path)
        genre_dict = {}
        for __, row in df.iterrows():
            movieId = row["movieId"]
            if movieId in self.movieId_to_column:
                movie_column = self.movieId_to_column[movieId]
                genre_str = row["genres"]
                genres = set([s.lower() for s in genre_str.split("|")])
                genre_dict[movie_column] = genres
        return genre_dict

    def _get_dataset(self, rating_path, train_path, val_path, test_path, seed):
        data = pd.read_csv(rating_path)
        users, movies, ratings = data["userId"], data["movieId"], data["rating"]
        ratings = ratings - ratings.mean()
        users = users - 1
        unique_movieIds = movies.unique()
        movieId_to_column = dict(zip(unique_movieIds, range(len(unique_movieIds))))
        column_to_movieId = dict(zip(range(len(unique_movieIds)), unique_movieIds))
        movie_columns = [movieId_to_column[m] for m in movies]
        num_movies = len(unique_movieIds)
        num_users = len(users.unique())
        num_ratings = len(ratings)
        if isfile(train_path) and isfile(val_path) and isfile(test_path):
            print("loading train/val/test files")
            train_dataset = sp.sparse.load_npz(train_path)
            val_dataset = sp.sparse.load_npz(val_path)
            test_dataset = sp.sparse.load_npz(test_path)
        else:
            split_size = int(num_ratings * 0.01)
            inds = set(range(num_ratings))
            random.seed(seed)
            test_inds = set(
                random.sample(
                    inds, split_size
                )
            )
            inds = inds-test_inds
            val_inds = set(
                random.sample(
                    inds, split_size 
                )
            )
            inds = inds-val_inds
            train_inds = inds
            train_dataset, val_dataset, test_dataset = self._get_train_val_test_split(
                train_inds, val_inds, test_inds, ratings, users, movie_columns, num_movies, num_users
            )
            dirs = os.path.dirname(train_path)
            os.makedirs(dirs, exist_ok=True)
            sp.sparse.save_npz(train_path, train_dataset)
            sp.sparse.save_npz(val_path, val_dataset)
            sp.sparse.save_npz(test_path, test_dataset)
        return train_dataset, val_dataset, test_dataset, column_to_movieId, movieId_to_column

    def _get_train_val_test_split(
        self, train_inds, val_inds, test_inds, ratings, users, movie_columns, num_movies, num_users
    ):

        train_dataset = self._inds_to_dataset(
                train_inds, ratings, users, movie_columns, num_movies, num_users
        )
        val_dataset = self._inds_to_dataset(
                val_inds, ratings, users, movie_columns, num_movies, num_users
        )
        test_dataset = self._inds_to_dataset(
                test_inds, ratings, users, movie_columns, num_movies, num_users
        )
        return train_dataset, val_dataset, test_dataset

    def _inds_to_dataset(
            self, inds, ratings, users, movie_columns, num_movies, num_users
    ):
        ratings = [r for i, r in enumerate(ratings) if i in inds]
        users = [u for i, u in enumerate(users) if i in inds]
        movie_columns = [c for i, c in enumerate(movie_columns) if i in inds]
        dataset = coo_matrix((ratings, (users, movie_columns)))
        dataset.resize(num_users, num_movies)
        return dataset


    def _get_val_rmse(self, U, V):
        val_iX, val_iY = np.nonzero(self.val_dataset)
        val_values = np.sum(U[val_iX] * V[:, val_iY].T, axis=-1)  # batched dot product
        val_approx = coo_matrix(
            (val_values, (val_iX, val_iY)), shape=self.val_dataset.shape
        )
        val_diff = self.val_dataset - val_approx
        val_rmse = sp.sparse.linalg.norm(val_diff) / np.sqrt(self.num_val)

        return val_rmse

    def _get_approx(self, U, V, iX=None, iY=None):
        if iX is None:
            iX, iY = np.nonzero(self.train_dataset)
        values = np.sum(U[iX]*V[:, iY].T, axis=-1) #batched dot product
        approx = coo_matrix((values, (iX,iY)), shape=self.train_dataset.shape)
        return approx

    def _get_diff(self, U, V, iX, iY):
        approx = self._get_approx(U, V, iX, iY)
        diff = self.train_dataset - approx
        return diff

    def train(
        self,
        low_rank=115,
        max_epochs=1000,
        lr=0.00117,
        alpha=0.0765,
        print_every=10,
        verbose=False,
        pretrained=False,
    ):
        if verbose:
            print("Training")
        if not pretrained:
            U = np.random.randn(self.train_dataset.shape[0], low_rank) / np.sqrt(
                low_rank
            )
            V = np.random.randn(low_rank, self.train_dataset.shape[1]) / np.sqrt(
                low_rank
            )
        else:
            U, V = self.U, self.V
        iX, iY = np.nonzero(self.train_dataset)
        U_weight = np.unique(iX, return_counts=True)[1]
        U_weight = np.expand_dims(U_weight, axis=1)
        V_inds, V_weights = np.unique(iY, return_counts=True)
        V_weight = np.zeros(self.train_dataset.shape[1])
        for i, w in zip(V_inds, V_weights):
            V_weight[i] = w

        val_rmses = []
        early_stop = 0
        best_val_rmse = float('inf')
        best_U, best_V = None, None
        for epoch in range(max_epochs):
            # U step
            diff = self._get_diff(U, V, iX, iY)
            U += lr * (diff * V.T - alpha * U_weight * U)

            # V step
            diff = self._get_diff(U, V, iX, iY)
            V += lr * (U.T * diff - alpha * V_weight * V)
            val_rmse = self._get_val_rmse(U, V)
            if val_rmse < best_val_rmse:
                best_val_rmse = val_rmse
                best_U, best_V = np.copy(U), np.copy(V)
            val_rmses.append(val_rmse)
            if verbose and (epoch % print_every == 0):
                train_rmse = sp.sparse.linalg.norm(diff) / np.sqrt(self.num_train)
                print(
                    "Train RMSE: ",
                    round(train_rmse, 3),
                    "      Val RMSE: ",
                    round(val_rmse, 3)
                )
            if epoch%10==0 and len(val_rmses)>20:
                if sum(val_rmses[-10:]) >= sum(val_rmses[-20:-10]): #early stop
                    early_stop += 1
                else:
                    early_stop = 0
            if early_stop >= 5:
                break
        return best_U, best_V, best_val_rmse

    def _get_UV(self, U_save_path, V_save_path):
        U, V, __ = self.train(verbose=True)
        np.save(U_save_path, U)
        np.save(V_save_path, V)
        return U, V

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
                #sim = (
                #    v_query.dot(v_seen)
                #    / np.linalg.norm(v_query)
                #    / np.linalg.norm(v_seen)
                #)
                #add = sim * rating

                #common_genres = self.genre_dict[j].intersection(
                #    self.genre_dict[movie_column]
                #)
                #scale = 0.7 + 0.3 * min((len(common_genres), 2))
                #query_rating += scale * add
                sim = self._get_similarity(v_query, v_seen, j, movie_column, rating)
                query_rating += rating*sim

            query_ratings.append(query_rating)

        recommended_columns = nlargest(
            20,
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


    def eval_test(self, U_load_path, V_load_path):
        U, V = np.load(U_load_path), np.load(V_load_path)
        test_iX, test_iY = np.nonzero(self.test_dataset)
        test_values = np.sum(U[test_iX] * V[:, test_iY].T, axis=-1)  # batched dot product
        test_approx = coo_matrix(
            (test_values, (test_iX, test_iY)), shape=self.test_dataset.shape
        )
        test_diff = self.test_dataset - test_approx
        test_rmse = sp.sparse.linalg.norm(test_diff) / np.sqrt(self.num_test)
        return test_rmse



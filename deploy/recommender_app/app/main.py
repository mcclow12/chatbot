import os

import pickle
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Tuple
from app.recommender import Recommender
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Movie Recommendations")

#origins = [
#        "*"
#]
#
#app.add_middleware(
#    CORSMiddleware,
#    allow_origins=origins,
#    allow_credentials=True,
#    allow_methods=["*"],
#    allow_headers=["*"],
#)

class MatchString(BaseModel):
    match_string: str

class MovieRatings(BaseModel):
    ratings: List[Tuple[str, int]]

@app.on_event("startup")
def load_clf():
    # Load classifier from pickle file
    with open("./app/recommender.pickle", "rb") as file:
        global recommender
        recommender = pickle.load(file)

@app.post("/find_movie_matches")
def predict(match_string: MatchString):
    matches = recommender.find_movie_matches(match_string.match_string)
    #should handle this in the recommender
    matches = matches[:26]
    return {"matches": matches}

@app.post("/make_recommendations")
def predict(movie_ratings: MovieRatings):
    ratings = dict(movie_ratings.ratings)
    recommendations = recommender.make_recommendations(ratings)
    return {"recommendations": recommendations}

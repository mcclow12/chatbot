from app.recommender import Recommender
import pickle

r = Recommender();
pickle.dump(r, open('./app/recommender.pickle', 'wb'))

import pickle
import optuna
from recommender import Recommender

def objective(trial):
    low_rank = trial.suggest_int("low_rank", 90, 120)
    lr = trial.suggest_loguniform("lr", 5e-4, 5e-3)
    alpha = trial.suggest_loguniform("alpha", 0.01, 0.15)
    rating_path = './ml-latest-small/ratings.csv'
    movie_path = './ml-latest-small/movies.csv'
    V_load_path = 'V_good.npy'
    recommender = Recommender(
            rating_path, 
            movie_path,
            V_load_path=V_load_path,
            low_rank=low_rank,
    )
    __, __, val_rmse = recommender.train(
            low_rank,
            lr=lr,
            alpha=alpha,
            print_every=10,
            verbose=True,
            pretrained=False,
    )
    return val_rmse

if __name__ == '__main__':
    study = optuna.create_study()
    n_trials = 50
    study.optimize(objective, n_trials=n_trials)
    with open('optuna_study.pkl', 'wb') as study_file:
        pickle.dump(study, study_file)



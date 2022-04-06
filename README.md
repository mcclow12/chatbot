# chatbot

This repository contains the code for a movie chatbot web service deployed on AWS. The deployed chatbot can be found here: http://willsmoviechatbot.com/ (Currently, only Android is supported on mobile.)

The chatbot is deployed on a small Kubernetes cluster made up of three EC2 instances (one master, two workers). At this time, the cluster runs three services, each containing two pods. 

## System Design And Implementation
![Image](.img/k8s_cluster.png)

There are three services in the cluster: an NGINX service, a classifier service, and a recommender service. The NGINX service is exposed as type NodePort and an AWS Classic LoadBalancer is placed in front of the worker nodes. In a managed Kubernetes setting such as Amazon's EKS, the NGINX service would be exposed as type LoadBalancer, but achieving this configuration on bare EC2 instances is not straightforward. (I wanted to deploy on EC2 for the experience of installing k8s and interacting with the control plane directly.)

### NGINX Service
The NGINX service acts as a web server for the client and delivers the HTML and Javascript to the client upon visiting the web page. The light-weight component of the chatbot application is implemented in Javascript and runs client-side. When the chatbot needs to do sentiment analysis, movie lookup, or recommendation, the chatbot sends a POST request to the NGINX service. The NGINX service then acts as a reverse proxy (similar to an Ingress) for the classifier and recommender services.

### Classifier Service
The classifier service does sentiment analysis on movie reviews to determine whether the client liked the movie or not. The classifier uses a pretrained DistilBERT model fine-tuned on SST-2 and served with TorchServe. In order to satisfy compute requirements and improve latency, the model is quantized with minimal detriment to performance. In order to prevent movie titles from leaking into the sentiment analysis (e.g. "The Haunting" vs "Elf"), titles are replaced with an \<UNK\> token. (It is unclear to me whether an \<UNK\> token is a better choice than a \<PAD\> token.) Additionally, the model could be further fine-tuned on a dataset of movie reviews, but the model's performance is already very good for current requirements.

### Recommender Service
The recommender service does a spelling-insensitive movie title lookup and makes the final movie recommendations for the client. These two behaviors should be split into separate services and their combination into one module is a vestige from the original python implementation. (See future work below.) The lookup is done via substring matching for exact matches and Levenshtein distance for near matches on a dataset of movie titles. The recommendation algorithm is described next.
  
## Recommendation Algorithm
  
  Recommendations are done via genre-weighted item-item similarity between the Funk-MF matrix decomposition factors. The dataset we use is the MovieLens-latest-small dataset of 100,000 movie reviews from 600 users on 9,000 movies. Let R be the sparse 600x9000 utility matrix of reviews. We decompose the matrix R into a low rank product of matrices U and V by optimizing the following loss function:
  ![Image](.img/funk_mf_loss.png)
  
  
  To optimize the loss function, we perform the following alternating updates, where η is the learning rate.  
  
  
  ![Image](.img/gradient_step.png)
  
  A hyperparameter search using Optuna was performed over the hidden dimensions of U and V as well as over the learning rate and the regularization parameter. One percent of the reviews were held out for validation and testing respectively, and the model achieves a val RMSE of 0.8301 and a test RMSE of 0.8412. As a sanity check, these values compare favorably to the RMSEs of the Netflix Challenge. (Although of course that is a much different dataset.)
  
  In the context of a chatbot application, the naive recommendation method which takes the inner product of a user vector with a movie vector does not work for the following reasons: (1) The vector for a new user has to be learned in some way, perhaps by retraining on the whole dataset. (2) With only a handful of data points given by the chatbot, the naive recommendation algorithm performs poorly even when retraining the entire dataset. (3) The movie dataset is filled with 0.5 to 5 star ratings whereas the sentiment classifier only detects binary ratings.
  
  There are various ways to address these problems. We chose to perform item-item comparison using the latent factors found by the Funk MF matrix decomposition. Specifically, to score a movie j, we sum up the genre-weighted cosine similarities of the query vector and the observed rating vectors.
  
  ![Image](.img/score_formula.png)
  
  
  ![Image](.img/weights.png)
  
  This method allows for intelligent recommendations that make sense with as little as one data point. While the model performs well by observation, currently the weighting function is hand-tuned on a small number of query sets and is quite arbitrary, which makes it hard to improve. In order to compare recommendation methods, one could A/B test two different recommendation algorithms and determine which one optimizes some user engagement metric. However, there is probably some learning-to-rank cost function I could learn about that would be even more useful in this setting. (See future work.)
  
  

## Future Work / Improvements
  Plans for future work and improvements are listed here.
  
  - Include unit testing and integration testing.
  - Separate the lookup and the recommendation abstractions into two separate services.
  - Improve k8s update stability due to tight compute space constraints, likely by assigning pods to specific nodes.
  - Implement the matrix decomposition on the full 25M movie review dataset via Spark.
  - Build a full MLOPS CI/CD pipeline from training to automatic deployment and model monitoring (Jenkins, AirFlow, etc).
  - Separate the movie database from the pods.
  - Find an objective way to compare recommendation algorithms for the chatbot.
  
  ### Small fixes
  - Change pickled dictionaries to JSON for security reasons.
  - Chat greeting after reset is missing a space.

#!/bin/bash
docker rm -v -f $(docker ps -qa)
sudo docker build -t mcclow12/chatbot:nginx-web-local ./nginx_app
sudo docker build -t mcclow12/chatbot:classifier-local ./classifier_app
sudo docker build -t mcclow12/chatbot:recommender-local ./recommender_app
konsole --noclose -e sudo docker run -it --rm --net=host -p 80:80 mcclow12/chatbot:nginx-web-local &
konsole --noclose -e sudo docker run -it --rm -p 0.0.0.0:100:100 mcclow12/chatbot:recommender-local &
konsole --noclose -e sudo docker run -it --rm -p 8080:8080 mcclow12/chatbot:classifier-local
#change proxy_pass

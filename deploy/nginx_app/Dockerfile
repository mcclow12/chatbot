FROM nginx:latest

RUN rm /usr/share/nginx/html/*

COPY classifier.js \
    recommender.js \
    chat-handler.js \
    chatbot.js \
    favicon.ico \
    index.html \
    movie_background.jpg \
    styles.css \
    /usr/share/nginx/html/

COPY nginx.conf /etc/nginx/

EXPOSE 80

WORKDIR /

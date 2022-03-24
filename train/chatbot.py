from utils import *

from transformers import pipeline


class Chatbot:
    def __init__(self, recommender):

        self.rec = recommender
        self.state = "greeting"
        self.movie_matches = None  # for disambiguation
        self.rating = None  # for disambiguation
        self.classifier = pipeline(
            task="sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
        )
        self.movie_ratings = {}

    def greet(self):
        greeting = (
            "I know a lot about movies. Tell me your thoughts on some \n"
            "movies you've watched and I'll be happy to give you some great "
            "recommendations!"
        )
        self.state = "get_input"
        return greeting

    def get_info(self):
        info = (
            "-------------------------------------------------------\n"
            "------------------INSTRUCTIONS-------------------------\n"
            "------------------------------------------------------- \n"
            "Type exit to exit. Type reset to reset. Give one movie \n"
            "at a time and put the movie title in quotation \n"
            "marks, e.g. 'I liked \"The Wizard of Oz\"' \n"
            "The more information you give, the better recommendations "
            "you will recieve. \nWhen you are ready to recieve "
            "recommendations, simply say 'Recommendations please!'"
            "\n--------------------------------------------------"
        )
        return info

    def chat(self, input_str):
        if input_str.lower() == "recommendations please!":  #'Recommendations please!'
            if len(self.movie_ratings) > 0:
                return self._recommend_string()
            else:
                return utils_min_required()
        if self.state == "get_input":
            return self._get_input(input_str)
        elif self.state == "disambiguate":
            return self._disambiguate(input_str)
        response = "Error: something went wrong."
        return response

    def _get_input(self, input_str):
        if input_str == "reset":
            self._reset()
            return (
                "Okay let's start over. \nNice to meet you for the first "
                "time! " + self.greet()
            )
        if input_str.count('"') != 2:
            return utils_quotations()
        matches = self._find_movie_matches(input_str)
        if len(matches) == 0:
            return utils_new_movie()
        elif len(matches) == 1:
            rating, score = self._get_rating(input_str)
            if score < 0.8:
                return utils_low_confidence()
            self.movie_ratings[matches[0]] = rating
            if rating == 1:
                return utils_liked()
            else:
                return utils_disliked()
        elif 1 <= len(matches) < 25:
            rating, score = self._get_rating(input_str)
            if score < 0.8:
                return utils_low_confidence()
            response = "Which movie in particular are you thinking of?"
            response += "".join(["\n" + f"{i}. " + m for i, m in enumerate(matches)])
            response += (
                "\nOr reply 'None' if the movie you were thinking "
                "of isn't listed here."
            )
            self.movie_matches = matches
            self.rating = rating
            self.state = "disambiguate"
            return response
        else:
            return (
                "Hmmm there are so many movies that sound "
                "like that one. Are you sure you typed it correctly?"
            )

    def _disambiguate(self, input_str):
        if input_str.lower() == "none":
            self.state = "get_input"
            self.movie_matches = None
            self.rating = None
            return "Sounds good! Let's hear about some other movies then."

        if input_str.isdigit():
            selection = int(input_str)
            if 0 <= selection < len(self.movie_matches):
                match = self.movie_matches[selection]
                rating = self.rating
                self.movie_ratings[match] = rating
                match = match[:-7]  # remove date
                self.state = "get_input"
                self.movie_matches = None
                self.rating = None
                if rating == 1:
                    response = utils_liked_match(match)
                else:
                    response = utils_disliked_match(match)
                    response += utils_more_opinions()
                return response

        num_matches = len(self.movie_matches) - 1
        return (
            "Sorry, I didn't get that. Please pick a number "
            f"between 0 and {num_matches}. Or reply 'None' to move on."
        )

    def _get_rating(self, input_str):
        sp = input_str.split('"')
        input_str = sp[0] + " 字 "  # movie name --> <unk>
        if len(sp) > 2:
            input_str = input_str + sp[2]
        result = self.classifier(input_str)[0]
        label, score = result["label"], result["score"]
        if label == "POSITIVE":
            return 1, score
        else:
            return -1, score

    def _find_movie_matches(self, input_str):
        input_str = input_str.lower()
        input_title = input_str.split('"')[1].strip()
        input_title_split = input_title.split()
        matches = []
        for title in self.rec.movies:
            if input_title == title[:-7].lower().strip():
                return [title]
            flag = True
            for word in input_title_split:
                if word not in title[:-7].lower():
                    flag = False
                    break
            if flag:
                matches.append(title)
        return matches

    def _recommend_string(self):
        recommended_movies = self.rec.make_recommendations(self.movie_ratings)

        answer = (
            "Okay, after some thought I think you should check some "
            "of these movies out: "
        )
        answer += "".join(
            [f"\n{i+1}. " + movie for i, movie in enumerate(recommended_movies)]
        )
        answer += (
            "\nTell me about more movies if you want to improve your "
            "recommendations! Otherwise type 'reset' to start over."
        )
        return answer

    def _reset(self):
        self.movie_matches = None
        self.rating = None
        self.movie_ratings = {}

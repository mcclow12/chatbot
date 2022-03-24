import random

def utils_min_required():
    responses = [
            "Sorry, I need your opinion on a movie "\
            "before I can give you quality recommendations.",
            "Sorry, I don't have enough information yet "\
            "to make a good recommendation.",
            "I can't give a good recommendation yet. Please "\
            "tell me about some movies you've watched first.",
            "It's gonna be hard for me to give you some good "\
            "recommendations if I don't know anything about your tastes.",
            "I don't think I'm ready to give a recommendation yet. "\
            "How about you tell me about some movies you've watched?",
            "Please tell me about some movies you watched first. "\
            "Then I'll be able to give you some great recommendations"
    ]
    return random.choice(responses)


def utils_quotations():
    responses = [
            "Hmm seems like you messed up your quotation marks. " \
            "Try again.",
            "Uh oh, I don't think your quotation marks are correct. ",
            "It's hard for me to understand which movie you're talking about.",
            "To help me understand, please put quotation marks around the " \
            "movie like this \"The Wizard of Oz\"",
            "It's hard for me to understand with your quotation marks.",
            "Oops, seems like your quotation marks aren't quite right.",
            "Please re-check your quotation marks. There should be two "\
            "in your response surrounding the movie title.",
            "I'm having trouble reading your sentence because of the "\
            "quotation marks. Can you please try again? ",
    ]
    return random.choice(responses)

def utils_new_movie():
    responses = [
            "Interesting, I haven't heard of that movie.",
            "Hmm I haven't heard of that movie.",
            "Wow that movie is new to me. I don't know much about it.",
            "I've actually never heard of that movie before! Unfortunately "\
            "that means \nI can't give you some good recommendations based "\
            "on that one.",
            "That movie is actually unfamiliar to me.",
            "To be honest, I haven't seen that movie before, so it'll "\
            "be hard to recommend you a movie based on that one."
    ]
    return random.choice(responses)

def utils_liked():
    responses1 = [
        "Great, glad you liked that one.",
        "Okay got it that was a good movie.",
        "Nice, sounds like that movie was right up your alley."
        "Wow so you like those kinds of movies. "\
        "I think you'll like my recommendations.",
        "Glad you liked the movie.",
        "Sounds like you enjoyed that one.",
        "Good, glad you enjoyed it.",
        "Okay, got it, I think I have some other ones that you'll like as well.",
        "Awesome, glad you liked it."
    ]
    responses2 = [
            " Now feel free to tell me about some more movies or say "\
            "'Recommendations please!' to hear my recommendations. ",
            " Any more movies you've seen? ",
            " You're giving me some great feedback.",
            " What other movies have you seen? ",
            " Any other movies you've seen? ",
            " Any more movie opinions I should know?",
            " Anything else you want to tell me before I give my recommendations?"
    ]
    response1 = random.choice(responses1)
    response2 = ''
    if random.uniform(0, 1) < 0.3:
        response2 = random.choice(responses2)
    return response1 + response2

def utils_disliked():
    responses1 = [
            "Okay got it you didn't like that one.",
            "Gotcha so that wasn't the movie for you.",
            "Okay you didn't like that one.",
            "Yeah I've heard other people didn't like that one as well.",
            "So you didn't like that one got it.",
            "That really wasn't your movie huh.",
            "That movie wasn't for you then. I'll keep that in mind.",
            "Okay so you did not like that one.",
    ]
    responses2 = [
            " Now feel free to tell me about some more movies or say "\
            "'Recommendations please!' to hear my recommendations. ",
            " Any more movies you've seen? ",
            " You're giving me some great feedback.",
            " What other movies have you seen?",
            " Any other movies you've seen?",
            " Got any more hot takes?",
            " Any more movie opinions I should know?",
            " Anything else you want to tell me before I give my recommendations?"
    ]
    response1 = random.choice(responses1)
    response2 = ''
    if random.uniform(0, 1) < 0.3:
        response2 = random.choice(responses2)
    return response1 + response2

def utils_more_opinions():
    responses = [
            " Now feel free to tell me about some more movies or say "\
            "'Recommendations please!' to hear my recommendations.",
            " Any more movies you've seen? ",
            " You're giving me some great feedback.",
            " What other movies have you seen?",
            " Any other movies you've seen?",
            " Got any more opinions on movies you've seen?",
            " Any more movie opinions I should know?",
            " Anything else you want to tell me before I give my recommendations?"
    ]
    return random.choice(responses)

def utils_liked_match(match):
    responses = [
            f"Got it! So you liked {match}.",
            f"Okay so {match} was your type of movie.",
            f"Gotcha so {match} was a good fit for you.",
            f"Okay got it you liked {match}.",
            f"Sounds like {match} was right up your alley.",
            f"Okay so your tastes align with {match}, got it."
    ]
    return random.choice(responses)

def utils_disliked_match(match):
    responses = [
            f"Okay sounds like {match} wasn't the " \
                            "movie for you.",
            f"Okay got it {match} wasn't your cup of tea.",
            f"So you did not like {match}. Got it.",
            f"Gotcha so you didn't like {match}.",
            f"Okay so {match} was the movie you didn't like.",
            f"{match} wasn't the movie for you then.",
            f"Got it you didn't like {match}."
    ]
    return random.choice(responses)

def utils_low_confidence():
    responses = [
            "Sorry, I couldn't tell if you liked that " \
                                "movie or not.",
            "Sorry I'm not sure if you liked that one.",
            "I can't quite tell what you think about that movie.",
            "I'm not quite sure if you liked that movie or not.",
            "Wait.. did you like or dislike that movie?",
            "I think I need some more information to tell whether you "\
            "liked that movie or not.",
            "Hang on, I couldn't tell if you liked that movie or not."

    ]
    return random.choice(responses)


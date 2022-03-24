class Chatbot {
     constructor(recommender, classifier) {
        this.rec = recommender;
        this.state = "get_input";
        this.movie_matches;
        this.rating;
        this.classifier = classifier;
        this.movie_ratings = new Map();
        this.ready = true
        var greeting1 = "I know quite a bit about movies. Tell me your thoughts on some movies you've watched and I'll be happy to give you some great recommendations!";
        var greeting2 = "To make it easy on me, please tell me about one movie at a time and put your movie in double quotation marks. For example 'I really loved \"Shrek\". ";
        greeting2 += "When you're ready for your recommendations, say 'Recommendations please!'. To start over, just say 'reset'.";
        this.greet = [greeting1, greeting2];
    }

    async chat(input_str) {
        //gets user input input_str and returns a response string
        //if (input_str.toLowerCase() === "recommendations please!") {
        if ((levenshtein_weighted(input_str, "recommendations please") < 4) ||
            (levenshtein_weighted(input_str, "recommendations") < 4)) {
            if (this.movie_ratings.size > 0) {
                return await this._recommend_string();
            } else {
                return utils_min_required();
            }
        }
        //change all double quotes to '"'
        var regex = /\u201E|\u201C|\u201F|\u201D|\u0022|\u275D|\u275e|\u2E42|\u301d|\u301E|\u301F/g;
        input_str = input_str.replaceAll(regex, '"');
        if (this.state === "get_input") {
            return this._get_input(input_str);
        } else if (this.state === "disambiguate") {
            return this._disambiguate(input_str);
        }
        var response = "Error: something went wrong.";
        return response;
    }

    async _get_input(input_str) {
        if (input_str === "reset") {
            this._reset();
            return ["Okay let's start over. Nice to meet you for the first time!<br>", this.greet.join()];
        }
        if (input_str.split('"').length-1 != 2) {
            return utils_quotations();
        }
        var matches = await this._find_movie_matches(input_str)
        
        if (matches.length === 0) {
            return utils_new_movie();
        } 
        var rat = await this._get_rating(input_str)
        var rating = rat.at(0);
        var score = rat.at(1);
        if (score < 0.95) {
            return utils_low_confidence();
        }

        if (matches.length === 1) {
            this.movie_ratings.set(matches.at(0), rating);
            if (rating === 1) { 
                return utils_liked();
            } else {
                return utils_disliked()
            }
        } else if (1 <= matches.length && matches.length < 25) {
            var response = "Which movie in particular are you thinking of?";
            for (const [index, match] of matches.entries()) {
                response += "<br>" + index.toString() + ". " + match
            }
            response += "<br>Or reply 'None' if the movie you were thinking " +
                "of isn't listed here.";
            this.movie_matches = matches;
            this.rating = rating;
            this.state = "disambiguate";
            return response;
        } else {
            return "Hmmm there are so many movies that sound " +
                "like that one. Are you sure you typed it correctly?";
            
        }
    }

    _disambiguate(input_str) {
        if (input_str.toLowerCase() === "none") {
            this.state = "get_input";
            this.movie_matches = null;
            this.rating = null;
            return "Sounds good! Let's hear about some other movies then.";
        }

        if (/^\d+$/.test(input_str)) {
            var selection = parseInt(input_str);
            if (0 <= selection && selection < this.movie_matches.length) {
                var match = this.movie_matches.at(selection);
                var rating = this.rating;
                this.movie_ratings.set(match, rating);
                match = match.slice(0, -7);
                match = this.make_readable(match);
                this.state = "get_input";
                this.movie_matches = null;
                this.rating = null;
                if (rating === 1) {
                    var response = utils_liked_match(match);
                } else {
                    var response = utils_disliked_match(match);
                    response += utils_more_opinions();
                }
                return response;
            }
        }

        var num_matches = this.movie_matches.length - 1;
        return "Sorry, I didn't get that. Please pick a number between 0 and " + 
                num_matches.toString() + " . Or reply 'None' to move on.";
    }

    async _get_rating(input_str) {
        var sp = input_str.split('"');
        input_str = sp.at(0) + " 字 ";
        if (sp.length > 2) {
            input_str = input_str + sp.at(2);
        }
        var result = await this.classifier.classify(input_str);
        var label = result.at(0);
        var score = result.at(1);
        if (label === "Accepted") {
            return [1, score];
        } else {
            return [-1, score];
        }
    }

    async _find_movie_matches(input_str) {
        var result = await this.rec._find_movie_matches(input_str);
        return result
    }

    async _recommend_string() {
        var recommended_movies = await this.rec.make_recommendations(this.movie_ratings);
        var answer = "Okay, after some thought I think you should check some " +
            "of these movies out: "
        for(const [i, movie] of recommended_movies.entries()) {
            answer += "<br>" + (i+1).toString() + ". " + movie;
        }
        answer = [answer, "Tell me about more movies if you want to improve your " +
            "recommendations! Otherwise type 'reset' to start over."];
        return answer
    }


    make_readable(input_str) {
        //Transforms titles like 'Terminator, The' -> 'The Terminator'
        var comma_split = input_str.split(',');
        if ((comma_split.length>1) && !(comma_split.at(-1).trim().includes(' '))) {
            return comma_split.at(-1).trim() + ' ' + comma_split.slice(0, -1).join();
        }
        return input_str
    }


    _reset() {
        this.movie_matches = null;
        this.rating = null;
        this.movie_ratings = new Map();
    }
}

//stackoverflow for now
function levenshtein_weighted(seq1,seq2)
{
    var len1=seq1.length;
    var len2=seq2.length;
    var i, j;
    var dist;
    var ic, dc, rc;
    var last, old, column;

    var weighter={
        insert:function(c) { return 1.; },
        delete:function(c) { return 0.5; },
        replace:function(c, d) { return 0.3; }
    };

    /* don't swap the sequences, or this is gonna be painful */
    if (len1 == 0 || len2 == 0) {
        dist = 0;
        while (len1)
            dist += weighter.delete(seq1[--len1]);
        while (len2)
            dist += weighter.insert(seq2[--len2]);
        return dist;
    }

    column = []; // malloc((len2 + 1) * sizeof(double));
    //if (!column) return -1;

    column[0] = 0;
    for (j = 1; j <= len2; ++j)
        column[j] = column[j - 1] + weighter.insert(seq2[j - 1]);

    for (i = 1; i <= len1; ++i) {
        last = column[0]; /* m[i-1][0] */
        column[0] += weighter.delete(seq1[i - 1]); /* m[i][0] */
        for (j = 1; j <= len2; ++j) {
            old = column[j];
            if (seq1[i - 1] == seq2[j - 1]) {
                column[j] = last; /* m[i-1][j-1] */
            } else {
                ic = column[j - 1] + weighter.insert(seq2[j - 1]);      /* m[i][j-1] */
                dc = column[j] + weighter.delete(seq1[i - 1]);          /* m[i-1][j] */
                rc = last + weighter.replace(seq1[i - 1], seq2[j - 1]); /* m[i-1][j-1] */
                column[j] = ic < dc ? ic : (dc < rc ? dc : rc);
            }
            last = old;
        }
    }

    dist = column[len2];
    return dist;
}

function choice(array) {
    var randomElement = array[Math.floor(Math.random() * array.length)];
    return randomElement;
}

function utils_min_required() {
    var responses = [
            "Sorry, I need your opinion on a movie " +
            "before I can give you quality recommendations.",
            "Sorry, I don't have enough information yet " +
            "to make a good recommendation.",
            "I can't give a good recommendation yet. Please " +
            "tell me about some movies you've watched first.",
            "It's gonna be hard for me to give you some good " +
            "recommendations if I don't know anything about your tastes.",
            "I don't think I'm ready to give a recommendation yet. " +
            "How about you tell me about some movies you've watched?",
            "Please tell me about some movies you watched first. " +
            "Then I'll be able to give you some great recommendations"
    ];
    return choice(responses);
}

function utils_quotations() {
    var responses = [
            "Hmm seems like you messed up your quotation marks. " +
            "Try again.",
            "Uh oh, I don't think your quotation marks are correct. ",
            "It's hard for me to understand which movie you're talking about.",
            "To help me understand, please put quotation marks around the " +
            "movie like this \"The Wizard of Oz\"",
            "It's hard for me to understand with your quotation marks.",
            "Oops, seems like your quotation marks aren't quite right.",
            "Please re-check your quotation marks. There should be two " +
            "in your response surrounding the movie title.",
            "I'm having trouble reading your sentence because of the " +
            "quotation marks. Can you please try again? ",
    ];
    return choice(responses);
}

function utils_new_movie() {
    var responses = [
            "Interesting, I haven't heard of that movie.",
            "Hmm I haven't heard of that movie.",
            "Wow that movie is new to me. I don't know much about it.",
            "I've actually never heard of that movie before! Unfortunately " +
            "that means I can't give you some good recommendations based " +
            "on that one.",
            "That movie is actually unfamiliar to me.",
            "To be honest, I haven't seen that movie before, so it'll " +
            "be hard to recommend you a movie based on that one."
    ];
    return choice(responses);
}

function utils_liked() {
    var responses1 = [
        "Great, glad you liked that one.",
        "Okay got it that was a good movie.",
        "Nice, sounds like that movie was right up your alley.",
        "Wow so you like those kinds of movies. " +
        "I think you'll like my recommendations.",
        "Glad you liked the movie.",
        "Sounds like you enjoyed that one.",
        "Good, glad you enjoyed it.",
        "Okay, got it, I think I have some other ones that you'll like as well.",
        "Awesome, glad you liked it."
    ];
    var responses2 = [
            " Now feel free to tell me about some more movies or say " +
            "'Recommendations please!' to hear my recommendations. ",
            " Any more movies you've seen? ",
            " You're giving me some great feedback.",
            " What other movies have you seen? ",
            " Any other movies you've seen? ",
            " Any more movie opinions I should know?",
            " Anything else you want to tell me before I give my recommendations?"
    ];
    var response1 = choice(responses1);
    var response2 = '';
    if (Math.random() < 0.3) {
        response2 = choice(responses2);
    }
    return response1 + response2;
}

function utils_disliked() {
    var responses1 = [
            "Okay got it you didn't like that one.",
            "Gotcha so that wasn't the movie for you.",
            "Okay you didn't like that one.",
            "Yeah I've heard other people didn't like that one as well.",
            "So you didn't like that one got it.",
            "That really wasn't your movie huh.",
            "That movie wasn't for you then. I'll keep that in mind.",
            "Okay so you did not like that one.",
    ];
    var responses2 = [
            " Now feel free to tell me about some more movies or say " +
            "'Recommendations please!' to hear my recommendations. ",
            " Any more movies you've seen? ",
            " You're giving me some great feedback.",
            " What other movies have you seen?",
            " Any other movies you've seen?",
            " Got any more hot takes?",
            " Any more movie opinions I should know?",
            " Anything else you want to tell me before I give my recommendations?"
    ];
    var response1 = choice(responses1);
    var response2 = '';
    if (Math.random() < 0.3) {
        response2 = choice(responses2);
    }
    return response1 + response2;
}    

function utils_more_opinions() {
    var responses = [
            " Now feel free to tell me about some more movies or say " +
            "'Recommendations please!' to hear my recommendations.",
            " Any more movies you've seen? ",
            " You're giving me some great feedback.",
            " What other movies have you seen?",
            " Any other movies you've seen?",
            " Got any more opinions on movies you've seen?",
            " Any more movie opinions I should know?",
            " Anything else you want to tell me before I give my recommendations?"
    ];
    return choice(responses);
}

function utils_liked_match(match) {
    var responses = [
            "Got it! So you liked " + match + ".",
            "Okay so " + match + " was your type of movie.",
            "Gotcha so " + match + " was a good fit for you.",
            "Okay got it you liked " + match + ".",
            "Sounds like " + match + " was right up your alley.",
            "Okay so your tastes align with " + match + ", got it."
    ];
    return choice(responses);
}

function utils_disliked_match(match) {
    var responses = [
            "Okay sounds like " + match + " wasn't the " +
                            "movie for you.",
            "Okay got it " + match + " wasn't your cup of tea.",
            "So you did not like " + match + ". Got it.",
            "Gotcha so you didn't like " + match + ".",
            "Okay so " + match + " was the movie you didn't like.",
            match + " wasn't the movie for you then.",
            "Got it you didn't like " + match + "."
    ];
    return choice(responses);
}

function utils_low_confidence() {
    var responses = [
            "Sorry, I couldn't tell if you liked that " +
                                "movie or not.",
            "Sorry I'm not sure if you liked that one.",
            "I can't quite tell what you think about that movie.",
            "I'm not quite sure if you liked that movie or not.",
            "Wait.. did you like or dislike that movie?",
            "I think I need some more information to tell whether you " +
            "liked that movie or not.",
            "Hang on, I couldn't tell if you liked that movie or not."
    ];
    return choice(responses);
}

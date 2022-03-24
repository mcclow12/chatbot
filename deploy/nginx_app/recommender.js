class Recommender {
    constructor() {
        //this.url = "http://movie-chatbot-1217778750.us-east-1.elb.amazonaws.com/recommend";
        this.url = window.location.origin + "/recommend";
    }
    
    async make_recommendations(ratings) {
        const response = await fetch(this.url + "/make_recommendations", {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              "accept": "application/json"
            },
            body: JSON.stringify({ratings : Array.from(ratings.entries())}) // body data type must match "Content-Type" header
          });
        var recommendations = await response.json();
        return recommendations["recommendations"];
    }

    async _find_movie_matches(input_str) {
        const response = await fetch(this.url + "/find_movie_matches", {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({match_string: input_str})
        });
        var matches = await response.json();
        return matches["matches"];
    }
}

class SentimentClassifier {
    constructor() {
        //this.url = "http://movie-chatbot-1217778750.us-east-1.elb.amazonaws.com/classify";
        this.url = window.location.origin + "/classify";
    }
    
    async classify(input_str) {
        const response = await fetch(this.url, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              "accept": "application/json"
            },
            body: JSON.stringify({"text": input_str}) 
          });
        var classification = await response.json();
        return classification;
    }
}

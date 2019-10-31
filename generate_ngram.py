from movie_reviews import Review
from stemmer import Stemmer
import json

if __name__ == "__main__":
    stemmer = Stemmer("root_dict.json")
    
    f = open("reviews_dict.json", "r")
    json_reviews = json.loads(f.read())
    f.close()
    
    reviews = []

    for review in json_reviews:
        reviews.append(Review.from_json(json_reviews[review]))

    stop_list = [".", ","]

    for i, review in enumerate(reviews):
        temp = review.text.lower()
        
        for i in range(100):
            temp = temp.replace("  ", " ")

        for element in stop_list:
            temp = temp.replace(element, "")

        temp = temp.split(" ")
        stemmed_text = ""
        for word in temp:
            found = stemmer.find(word) 
            print(word, found)
            if found:
                stemmed_text += found
            else:
                stemmed_text += word
            stemmed_text += " "

        reviews[i].text = stemmed_text

    print(reviews[0].text)
        




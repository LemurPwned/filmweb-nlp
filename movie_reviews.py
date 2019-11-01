import urllib.request
from bs4 import BeautifulSoup
from lxml import html
import json
import pandas as pd 


class Review:
    def __init__(self, title, text, rating, title_href=None):
        self.title = title
        self.text = text
        self.rating = rating
        self.title_href = title_href

    @classmethod
    def from_json(cls, json_obj):
        return cls(
            json_obj['title'],
            json_obj['text'],
            json_obj['rating']
        )

    def __str__(self):
        return f"{self.title}: {self.rating}: {self.text}"


class FilmReview:
    def __init__(self):
        self.filmweb_api_server = 'http://filmweb.pl'
        self.weird_text = 'waitingModule.runWhenReady("FOOTER",function(){rodo.canProfileVisitor(function(a){var b=getKeywords(a);sas.cmd.push(function(){sas.call("std",{siteId:smartSiteId,pageId:smartPageId,formatId:46596,target:b})})})});'

    def parse_move_review_pages(self, page):
        url = f"https://www.filmweb.pl/reviews?page={page}"
        # review_json = {}
        parsed_num = 0
        review_list = []
        with urllib.request.urlopen(url) as url_handl:
            html_code = url_handl.read()
            soup = BeautifulSoup(html_code, 'html.parser')
            reviews_on_page = soup.findAll(
                'h3', {'class': 'review__title'})
            for review in reviews_on_page:
                parsed_num += 1
                rev_href = review.find('a').attrs['href']
                parsed_review = self.get_long_movie_review(rev_href)
                if parsed_review is not None:
                    review_list.append(parsed_review)
                    # review_json[parsed_review.title] = parsed_review.__dict__
        return parsed_num, review_list


    def get_user_reviews(self, user_id):
        # https://www.filmweb.pl/user/michalwalkiewicz/reviews
        url = f"{self.filmweb_api_server}/user/{user_id}/reviews"
        with urllib.request.urlopen(url) as url_handl:
            html_code = url_handl.read()
            soup = BeautifulSoup(html_code, 'html.parser')
            reviews_on_page = soup.find(
                'section', {'class': 'section filmTopReviews page__section'})
            print(reviews_on_page)
        return 0

    def get_long_movie_review(self, review_link):
        url = f"{self.filmweb_api_server}{review_link}"

        with urllib.request.urlopen(url) as url_handl:
            html_code = url_handl.read()
            soup = BeautifulSoup(html_code, 'html.parser')
            review_title = soup.find("span", {"itemprop": "name"})
            review_text = soup.find("div", {"class": "newsContent"}).text
            review_text = review_text.replace(self.weird_text, '')
            review_rating = soup.find("span", {"itemprop": "ratingValue"})
            # print(review_title, review_rating)
        try:
            return Review(title=review_title.text,
                          text=review_text, rating=review_rating.text)
        except AttributeError:
            return None

    def parse_reviews_as_dataframe(self, start_page=1, review_pages=200):
        total_parsed = 0
        review_titles, review_ratings, review_texts = [], [], []
        for i in range(start_page, start_page+review_pages):
            parsed, reviews = fr.parse_move_review_pages(i)
            for review in reviews:
                review_titles.append(review.title)
                review_ratings.append(review.rating)
                review_texts.append(review.text)
            total_parsed += parsed
            print(f"Parsed: {total_parsed}...")
        print(f"Parsing done... Dumping")
        df = pd.DataFrame.from_dict({
            'title': review_titles,
            'rating': review_ratings,
            'content': review_texts
        })

        df.to_csv(f'reviews_for_bert_{start_page}_{review_pages}.csv', index=False)

if __name__ == "__main__":
    fr = FilmReview()
    fr.parse_reviews_as_dataframe(start_page=300, review_pages=150)
    # print(fr.get_movie_review('Zielona.Mila', 1))
    # rev_links = fr.get_user_reviews('michalwalkiewicz')
    # rew = fr.get_long_movie_review(rev_links[0])
    # print(rew)


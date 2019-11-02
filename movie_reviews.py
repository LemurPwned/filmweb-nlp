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
        return cls(json_obj['title'], json_obj['text'], json_obj['rating'])

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
            reviews_on_page = soup.findAll('h3', {'class': 'review__title'})
            for review in reviews_on_page:
                parsed_num += 1
                rev_href = review.find('a').attrs['href']
                parsed_review = self.get_long_movie_review(rev_href)
                if parsed_review is not None:
                    review_list.append(parsed_review)
                    # review_json[parsed_review.title] = parsed_review.__dict__
        return parsed_num, review_list

    def get_short_user_reviews(self, movie_id, page):
        url = f"https://www.filmweb.pl{movie_id}/discussion?page={page}"
        with urllib.request.urlopen(url) as url_handl:
            html_code = url_handl.read()
            soup = BeautifulSoup(html_code, 'html.parser')
            reviews_on_page = soup.findAll('li', {'class': 'filmCategory'})
            reviews, ratings = [], []
            parsed = 0
            for short_review in reviews_on_page:
                # print(short_review)
                rating = None
                rating_cands = short_review.findAll('li')
                for plausible_rating in rating_cands:
                    if 'oceni' in plausible_rating.text:
                        rating_str = plausible_rating.text.replace(" ", "").replace('\n','').replace('\t','')
                        try:
                            rating = int(
                                rating_str.replace(
                                    'ocenił(a)tenfilmna:', ''))
                        except ValueError:
                            pass 
                if rating is not None:
                    # print(short_review)
                    try:
                        review_content = short_review.find('p', {'class': 'text normal'}).text
                        if 'Uwaga Spoiler!' in review_content:
                            print("FOUND")
                        review_content = review_content.replace('\t', '').replace('\n', '').replace('\r', '').strip()
                        if len(review_content) > 50:
                            reviews.append(review_content)
                            ratings.append(rating)
                            parsed += 1
                    except AttributeError:
                        pass 
        return parsed, reviews, ratings

    def iterate_movies(self, pages, sub_reviews, start_page=1):
        total_reviews, total_ratings = [], []
        total_parsed = 0
        for page in range(start_page, start_page + pages):
            url = f"https://www.filmweb.pl/films/search?orderBy=popularity&descending=true&page={page}"
            with urllib.request.urlopen(url) as url_handl:
                html_code = url_handl.read()
                soup = BeautifulSoup(html_code, 'html.parser')
                movie_links = soup.findAll('a', {'class': 'filmPreview__link'})
                for movie_link in movie_links:
                    movie_id = movie_link.attrs['href']
                    print(f"Parsing... {movie_id}")
                    for sub_page in range(sub_reviews):
                        try:
                            parsed, reviews, ratings = self.get_short_user_reviews(
                                movie_id, sub_page)
                            if parsed:
                                total_parsed += parsed
                                total_ratings.extend(ratings)
                                total_reviews.extend(reviews)
                        except urllib.error.HTTPError:
                            print("Bad url")

                print(f"Parsed {total_parsed} reviews")
        df = pd.DataFrame.from_dict({
            'content': total_reviews,
            'rating': total_ratings
        })
        df.to_csv(f"short_reviews_bert_{sub_reviews}_{start_page}_{pages}.csv",
                  index=False)

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
                          text=review_text,
                          rating=review_rating.text)
        except AttributeError:
            return None

    def parse_long_reviews_as_dataframe(self, start_page=1, review_pages=200):
        total_parsed = 0
        review_titles, review_ratings, review_texts = [], [], []
        for i in range(start_page, start_page + review_pages):
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

        df.to_csv(f'reviews_for_bert_{start_page}_{review_pages}.csv',
                  index=False)


if __name__ == "__main__":
    fr = FilmReview()
    # fr.parse_reviews_as_dataframe(start_page=300, review_pages=150)
    fr.iterate_movies(50, 10, 1)

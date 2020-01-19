import urllib.request
from bs4 import BeautifulSoup
from lxml import html
import json
import pandas as pd
import os


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
        self.save_dir = './movie_reviews'
        os.makedirs(self.save_dir, exist_ok=True)

    def parse_move_review_pages(self, page):
        url = f"https://www.filmweb.pl/reviews?page={page}"
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

    def parse_single_short_user_review(self, movie_id, link, parsed, page):
        lnk = link.split('/discussion')[-1]
        url = f"https://www.filmweb.pl{movie_id}/discussion{lnk}"
        with urllib.request.urlopen(url) as url_handl:
            html_code = url_handl.read()
            with open(
                    os.path.join(
                        self.holder,
                        movie_id.replace('.', '').replace(',', '').replace(
                            '/', '') + f'_parsed_{parsed}_page{page}.html'), 'wb') as f:
                f.write(html_code)
            soup = BeautifulSoup(html_code, 'html.parser')
            review = soup.find(
                'li', {'class': 'forumTopicSection__item i_0 filmCategory'})
            if not review:
                review = soup.find('li', {
                    'class':
                    'forumTopicSection__item i_0 filmCategory spoiler'
                })
            actual_first_review = review.find(
                'p', {
                    'class': 'forumTopicSection__topicText'
                }).text
            try:
                review_stars = review.find(
                    'span', {
                        'class': 'forumTopicSection__starsNo'
                    }).text
            except AttributeError:
                review_stars = -1
            actual_first_review = actual_first_review.replace('\t', '').replace('\n', '').replace('\r', '').strip()
        return actual_first_review, review_stars

    def get_short_user_reviews(self, movie_id, page):
        url = f"https://www.filmweb.pl{movie_id}/discussion?page={page}"
        with urllib.request.urlopen(url) as url_handl:
            html_code = url_handl.read()
            soup = BeautifulSoup(html_code, 'html.parser')
            reviews_on_page = soup.findAll('a',
                                           {'class': 'forumSection__itemLink'})
            reviews, ratings = [], []
            parsed = 0
            for short_review in reviews_on_page:
                rating = None
                review_content, rating = self.parse_single_short_user_review(
                    movie_id, short_review['href'],
                    parsed=parsed, page=page)  # parsed is for saving
                if len(review_content) > 50:
                    ratings.append(rating)
                    reviews.append(review_content)
                    parsed += 1
        return parsed, reviews, ratings

    def iterate_movies(self, pages, sub_reviews, start_page=1):
        total_reviews, total_ratings = [], []
        total_parsed = 0
        self.holder = os.path.join(self.save_dir, 'short_reviews')
        os.makedirs(self.holder, exist_ok=True)
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
                        except (urllib.error.HTTPError, AttributeError):
                            print("Bad url")

                print(f"Parsed {total_parsed} reviews")
        df = pd.DataFrame.from_dict({
            'content': total_reviews,
            'rating': total_ratings
        })
        savepath = os.path.join(
            self.save_dir,
            f"short_reviews_bert_{sub_reviews}_{start_page}_{pages}.csv")
        df.to_csv(savepath, index=False)

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
    fr.iterate_movies(
        pages=10,
        sub_reviews=10,
        start_page=21
    )

import urllib.request
from bs4 import BeautifulSoup
from lxml import html
import json


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
        review_json = {}
        parsed_num = 0
        with urllib.request.urlopen(url) as url_handl:
            html_code = url_handl.read()
            soup = BeautifulSoup(html_code, 'html.parser')
            reviews_on_page = soup.find(
                'section', {'class': 'section filmTopReviews page__section'})
            for review_el in reviews[0].iter(r"*"):
                if review_el.tag == 'a':
                    href = review_el.attrib['href']
                    if href.startswith('/review'):
                        parsed_num += 1
                        parsed_review = self.get_long_movie_review(href)
                        review_json[parsed_review.title] = parsed_review.__dict__
        return parsed_num, review_json

    def get_movie_review(self, movie_id, page):
        url = rf"{self.filmweb_api_server}/{movie_id}/discussion?page={page}"
        with urllib.request.urlopen(url) as url_handl:
            html_code = url_handl.read()
            tree = html.fromstring(html_code)
            rating_xpath = '/html/body/div[5]/div/div/div[2]/div/div/div/ul/li[5]/div[2]/div[1]/ul/li[3]/text()'
            rating = tree.xpath(rating_xpath)
            rating = rating[0].replace('ocenił(a) ten film na:', '')
            review_text = '/html/body/div[5]/div/div/div[2]/div/div/div/ul/li[5]/div[2]/p/text()'
            text = tree.xpath(
                review_text
            )
            return Review(title=movie_id, text=text[0], rating=int(rating))

    def get_user_reviews_xpath(self, user_id):
        # https://www.filmweb.pl/user/michalwalkiewicz/reviews
        url = f"{self.filmweb_api_server}/user/{user_id}/reviews"
        review_list_xpath = "/html/body/div[2]/div[4]/div/section[2]/section/div/ul"
        with urllib.request.urlopen(url) as url_handl:
            html_code = url_handl.read()
            tree = html.fromstring(html_code)
            review_list = tree.xpath(review_list_xpath)
            review_links = []
            for element in review_list[0].iter(r'*'):
                if element.tag == 'a':
                    try:
                        rev_link = element.attrib['href']
                        if rev_link.startswith('/review'):
                            review_links.append(rev_link)
                    except KeyError:
                        pass
        return review_links

    def get_user_reviews_xpath(self, user_id):
        # https://www.filmweb.pl/user/michalwalkiewicz/reviews
        url = f"{self.filmweb_api_server}/user/{user_id}/reviews"
        with urllib.request.urlopen(url) as url_handl:
            html_code = url_handl.read()
            soup = BeautifulSoup(html_code, 'html.parser')
            reviews_on_page = soup.find(
                'section', {'class': 'section filmTopReviews page__section'})
            print(reviews_on_page)
        return 0

    def get_long_movie_review_xpath(self, review_link):
        url = f"{self.filmweb_api_server}{review_link}"
        title_xpath = '/html/body/div[5]/div/div/div[1]/div/div[1]/div[1]/div[2]/div[2]/div[2]/ul/li[2]/a'
        full_review_xpath = '/html/body/div[5]/div/div/div[1]/div/div[1]/div[2]/div[1]/div'
        rating_xpath = '/html/body/div[5]/div/div/div[1]/div/div[1]/div[3]/div/div[2]/span/span[3]'
        with urllib.request.urlopen(url) as url_handl:
            html_code = url_handl.read()
            tree = html.fromstring(html_code)
            full_review = tree.xpath(
                full_review_xpath
            )[0]
            full_review = full_review.text_content().strip().replace(
                self.weird_text, '')
            title = tree.xpath(
                title_xpath)[0]
            rating = tree.xpath(
                rating_xpath
            )[0]
        return Review(title=title.text_content(), title_href=title.attrib['href'],
                      text=full_review, rating=int(rating.text_content()))

    def get_long_movie_review(self, review_link):
        url = f"{self.filmweb_api_server}{review_link}"

        with urllib.request.urlopen(url) as url_handl:
            html_code = url_handl.read()
            soup = BeautifulSoup(html_code, 'html.parser')
            review_title = soup.find("span", {"itemprop": "name"})
            review_text = soup.find("div", {"class": "newsContent"})
            review_rating = soup.find("span", {"itemprop": "ratingValue"})
        return Review(title=review_title.text,
                      text=review_text.text, rating=review_rating.text)


if __name__ == "__main__":
    fr = FilmReview()
    # print(fr.get_movie_review('Zielona.Mila', 1))
    # rev_links = fr.get_user_reviews('michalwalkiewicz')
    # rew = fr.get_long_movie_review(rev_links[0])
    # print(rew)
    # total_parsed = 0
    # review_json = {}
    fr.parse_move_review_pages(1)
    # for i in range(1, 20):
    #     parsed, rev_subjsn = fr.parse_move_review_pages(i)
    #     review_json = {**review_json, **rev_subjsn}
    #     total_parsed += parsed
    #     print(f"Parsed: {total_parsed}...")
    # print(f"Parsing done... Dumping")
    # json.dump(review_json, open(f'reviews_dict.json', 'w'))

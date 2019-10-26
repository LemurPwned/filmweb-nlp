import requests
import urllib.request
from bs4 import BeautifulSoup
from lxml import html


class Review:
    def __init__(self, text, rating):
        self.text = text
        self.rating = rating

    def __str__(self):
        return f"{self.rating}: {self.text}"


class FilmReview:
    def __init__(self):
        self.filmweb_api_server = 'http://filmweb.pl'
        self.weird_text = 'waitingModule.runWhenReady("FOOTER",function(){rodo.canProfileVisitor(function(a){var b=getKeywords(a);sas.cmd.push(function(){sas.call("std",{siteId:smartSiteId,pageId:smartPageId,formatId:46596,target:b})})})});'

    def get_movie_review(self, movie_id, page):
        url = rf"{self.filmweb_api_server}/{movie_id}/discussion?page={page}"
        print(url)
        with urllib.request.urlopen(url) as url_handl:
            html_code = url_handl.read()
            tree = html.fromstring(html_code)
            rating = tree.xpath(
                '/html/body/div[6]/div/div/div[2]/div/div[1]/div/ul/li[2]/div[2]/div[1]/ul/li[3]/text()'
            )
            rating = rating[0].replace('ocenił(a) ten film na:', '')
            text = tree.xpath(
                '/html/body/div[6]/div/div/div[2]/div/div[1]/div/ul/li[2]/div[2]/p/text()'
            )
            return Review(text=text[0], rating=int(rating))

    def get_user_reviews(self, user_id):
        # https://www.filmweb.pl/user/michalwalkiewicz/reviews
        url = f"{self.filmweb_api_server}/user/{user_id}/reviews"
        with urllib.request.urlopen(url) as url_handl:
            html_code = url_handl.read()
            tree = html.fromstring(html_code)
            review_list = tree.xpath(
                '/html/body/div[3]/div[4]/div/section[2]/section/div/ul')
            review_links = []
            for element in review_list[0].iter(r'*'):
                if element.tag == 'a':
                    # print(dir(element))
                    # print(element.label)
                    # print(element.items())
                    try:
                        rev_link = element.attrib['href']
                        if rev_link.startswith('/review'):
                            review_links.append(rev_link)
                    except KeyError:
                        pass
        return review_links

    def get_long_movie_review(self, review_link):
        url = f"{self.filmweb_api_server}{review_link}"
        with urllib.request.urlopen(url) as url_handl:
            html_code = url_handl.read()
            tree = html.fromstring(html_code)
            full_review = tree.xpath(
                '/html/body/div[6]/div/div/div[1]/div/div[1]/div[2]/div[1]/div'
            )[0]
            full_review = full_review.text_content().strip().replace(
                self.weird_text, '')
            print(full_review)
            rating = tree.xpath(
                '/html/body/div[6]/div/div/div[1]/div/div[1]/div[3]/div/div[2]/span/span[3]'
            )[0]
        return Review(text=full_review, rating=int(rating.text_content()))


if __name__ == "__main__":
    fr = FilmReview()
    print(fr.get_movie_review('Zielona.Mila', 1))
    rev_links = fr.get_user_reviews('michalwalkiewicz')
    fr.get_long_movie_review(rev_links[0])
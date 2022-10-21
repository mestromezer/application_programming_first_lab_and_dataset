from os import mkdir
from time import sleep

import requests
from bs4 import BeautifulSoup as BS


class Comment:
    def __init__(self, name, comment, mark):
        if name != "":
            self.name = name
        if name == None:
            print("Некорректное название")
            exit()
        if comment == None:
            print("Некоррректное содержимое комментария")
            exit()
        self.comment = comment
        if mark <= 5 and mark >= 0:
            self.mark = mark

    def get_mark(self):
        return self.mark

    def get_name(self):
        return self.name

    def get_comment(self):
        return self.comment


def create_repo():
    mkdir("dataset")
    for i in range(1, 6):
        mkdir("dataset/" + str(i))


headers = {
    'Connection':'keep-alive',
    'Cookie':"__ll_tum=1654684410; __ll_ab_mp=1; __ll_unreg_session=6189823623b7232cd200d40713ea3c9d; __ll_unreg_sessions_count=3; __llutmz=0; __llutmf=0; __ll_fv=1666111952; __ll_dv=1666151708; __ll_cp=3; iwatchyou=3fcd1d453fb01ff2f05aae874e144193; __r=pc3319c2_; LiveLibId=6189823623b7232cd200d40713ea3c9d; promoLLid=7jcp65jk7c78q3t6kc8gpj2430; ll_asid=1050121097; __ll_dvs=5; __utnt=g0_y0_a15721_u0_c0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0"
    }


def get_page(url):
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return BS(r.content, "html.parser")
        else:
            print("Page not found")
            exit()
    except:
        print("Ошибка соединения")
        return -1


def get_marks(articles):
    marks = list()
    for article in articles:
        try:
            lenta_card = article.find("div", class_="lenta-card")
            h3 = lenta_card.find("h3", class_="lenta-card__title")
            mark = h3.find("span", class_="lenta-card__mymark").text.strip()
            marks.append(mark)
        except AttributeError as e:
            print("Не найдена оценка")
            return -1
    return marks


def get_names(articles):
    names = list()
    for article in articles:
        try:
            lenta_card = article.find("div", class_="lenta-card")
            lenta_card_book_wrapper = lenta_card.find(
                "div", class_="lenta-card-book__wrapper"
            )
            name = lenta_card_book_wrapper.find(
                "a", class_="lenta-card__book-title"
            ).text.strip()
            names.append(name)
        except AttributeError as e:
            print("Не найдено название")
            return -1
    return names


def get_comments_texts(articles):
    comments_texts = list()
    for article in articles:
        try:
            lenta_card = article.find("div", class_="lenta-card")
            text_without_readmore = lenta_card.find(
                "div", class_="lenta-card__text without-readmore"
            )
            comment = text_without_readmore.find(
                id="lenta-card__text-review-escaped"
            ).text
            comments_texts.append(comment)
        except AttributeError as e:
            print("Не найден комментарий")
            return -1

    return comments_texts


def save_comments(data, filename):
    for i in range(0, len(data)):
        file = open(filename + f"/{(i+1):04}" + ".txt", "w", encoding="utf-8")
        file.write(data[i].get_name())
        file.write("\n\n\n")
        file.write(data[i].get_comment())
        file.close

def get_articles(soup):
    try:
            articles = (
                soup.find("main", class_="main-body page-content")
                .find("section", class_="lenta__content")
                .find_all("article", class_="review-card lenta__item")
            )
            return articles
    except AttributeError as e:
        print('Не удалось загрузить страницу')
        return -1


def check_capcha(soup):
    if (
            soup.find("h1").text
            == "Пожалуйста, подождите пару секунд, идет перенаправление на сайт..."
        ):
            print("Вылезла капча")
            return -1
    else: return None


def check_if_enough(one, two, three, four, five):
    if (
            one >= least_num_of_marks
            and two >= least_num_of_marks
            and three >= least_num_of_marks
            and four >= least_num_of_marks
            and five >= least_num_of_marks
        ):
            return 1
    else: return 0



def parse_pages(max_num_of_requests, least_num_of_marks):

    dataset = list()

    one = 0
    two = 0
    three = 0
    four = 0
    five = 0

    for i in range(1, max_num_of_requests):

        print(f"Страница: {i}")

        soup = get_page(url + "~" + str(i) + "#reviews")
        if soup == -1: continue

        if check_capcha(soup) == -1: continue

        articles = get_articles(soup)
        if articles == -1: continue

        # marks
        marks = get_marks(articles)
        if marks == -1: continue

        # names
        names = get_names(articles)
        if names == -1: continue

        # texts
        comments_texts = get_comments_texts(articles)
        if comments_texts == -1: continue

        for j in range(len(marks)):
            condidate = Comment(names[j], comments_texts[j], float(marks[j]))

            if condidate.mark < 2.0:
                one += 1

            if condidate.mark < 3.0:
                two += 1

            if condidate.mark < 4.0:
                three += 1

            elif condidate.mark < 5.0:
                four += 1

            elif condidate.mark == 5.0:
                five += 1

            dataset.append(condidate)
            
        print(
            f"One = {one}, Two = {two} ,Three = {three}, Four = {four}, Five = {five}"
        )
        if check_if_enough(one, two, three, four, five): return dataset#check if amount is big enough


if __name__ == "__main__":

    url = "https://www.livelib.ru/reviews/"

    least_num_of_marks = 1000 
    max_num_of_requests = 9000

    dataset = parse_pages(max_num_of_requests, least_num_of_marks)

    create_repo()

    # dataset.sort(key = lambda comment: comment.mark)

    one_data = [el for el in dataset if el.get_mark() < 2.0]
    save_comments(one_data, "./dataset/1")

    two_data = [el for el in dataset if el.get_mark() < 3.0 and el.get_mark() >= 2.0]
    save_comments(two_data, "./dataset/2")

    three_data = [el for el in dataset if el.get_mark() < 4.0 and el.get_mark() >= 3.0]
    save_comments(three_data, "./dataset/3")

    four_data = [el for el in dataset if el.get_mark() < 5.0 and el.get_mark() >= 4.0]
    save_comments(four_data, "./dataset/4")

    five_data = [el for el in dataset if el.get_mark() == 5.0]
    save_comments(five_data, "./dataset/5")

    print("Работа окончена")
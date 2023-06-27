import datetime
import csv
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
from lxml import etree
from time import sleep


ua = UserAgent()  # Fake user-agent to avoid ip block
base_url = "https://999.md"

months = ['янв', 'фев', 'мар', 'апр', 'мая', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
months = dict(zip(months, list(range(1, 13))))  # Create a dict with {'month': num}


def get_soup(link, get_response=None):
    sleep(2)  # To avoid ip block because of too often request to the site
    response = requests.get(link, headers={'User-Agent': ua.random})
    while '//m.' in response.url:  # check '//m.' in url because ua.random sometimes generate mobile user-agent
        response = requests.get(link, headers={'User-Agent': ua.random})
    soup = BeautifulSoup(response.text, 'html.parser')
    if get_response:
        return soup, response
    return soup


def get_page_link():
    """This func() parse and create/return link for each page of the category '/cars'"""

    category_url = "https://999.md/ru/list/transport/cars"
    soup = get_soup(category_url)
    total_page = soup.find('nav', class_='paginator cf').find('li', class_='is-last-page'
                                                              ).next.get('href').split('=')[-1]  # Take num of last page
    for num in range(1, int(total_page) + 1):
        yield f'https://999.md/ru/list/transport/cars?page={num}'  # return link of each page


def get_car_link():
    """This func() parse each card/car on the page and retrieve link for each car"""

    for page_url in get_page_link():
        soup = get_soup(page_url)

        cars_links = soup.find_all('div', class_="ads-list-photo-item-title")
        for link in cars_links:
            try:
                if '/booster' in link.find('a', class_="js-item-ad").get('href'):
                    continue
                yield base_url + link.find('a', class_="js-item-ad").get('href')
            except AttributeError:  #
                pass


def is_valid_time(str_time):
    """This func() create a datetime object out of wrong format, e.g. 16 iun. 2023, 16:18.
    For the next comparison with hardcoded datetime"""

    str_date = list((map(lambda x: x.strip(',.'), str_time)))
    day = str_date[0]
    month = months[str_date[1][:3]]
    year = str_date[2]
    hour = str_date[3]
    publication_date = datetime.datetime.strptime(f"{day} {str(month)} {year} {hour}", '%d %m %Y %H:%M')
    stop_time = datetime.datetime.today() - datetime.timedelta(hours=24)  # Yesterday datetime obj
    if publication_date > stop_time:
        return True
    raise StopIteration


def get_car_data(link):
    """Pass"""

    soup, response = get_soup(link, get_response=True)
    dom = etree.HTML(str(soup))

    unformated_date = dom.xpath('//*[@id="container"]/div/section/aside/div[1]/div/div[2]')[0].text.split()[-4:]
    if is_valid_time(unformated_date):
        brand = dom.xpath('//*[@id="js-item-page"]/div[1]/div[5]/div[1]/ul[1]/li[2]/span[2]/a')[0].text.strip()
        year = dom.xpath('//*[@id="js-item-page"]/div[1]/div[5]/div[2]/ul/li[2]/span[2]')[0].text.strip()
        mileage = dom.xpath('//*[@id="js-item-page"]/div[1]/div[5]/div[2]/ul/li[7]/span[2]')[0].text.strip()
        eng_volume = dom.xpath('//*[@id="js-item-page"]/div[1]/div[5]/div[2]/ul/li[8]/span[2]')[0].text.strip()
        fuel_type = dom.xpath('//*[@id="js-item-page"]/div[1]/div[5]/div[2]/ul/li[10]/span[2]/a')[0].text.strip()
        price = dom.xpath('//*[@id="js-item-page"]/div[1]/div[7]/div/div/div[1]/ul/li[1]/span[1]')[0].text.strip()
        car_link = response.url

        return {"brand": brand, 'year': year, 'mileage': mileage.replace(' ', ''),
                'eng_volume': eng_volume.replace(' ', ''),
                'fuel_type': fuel_type, 'price': price, 'car_link': car_link}


def check_black_list(link):
    car_id = link.split('/')[-1]
    with open('black_list.csv', mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        return any(map(lambda x: car_id in x, csv_reader))


def add_to_blacklist(link):
    car_id = link.split('/')[-1]
    with open('black_list.csv', mode='a+') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([car_id])


with open('today_cars.csv', mode='w') as csv_file:
    field_names = ['brand', 'year', 'mileage', 'eng_volume', 'fuel_type', 'price', 'car_link']
    csv_writer = csv.DictWriter(csv_file, field_names)
    csv_writer.writeheader()
    for link in get_car_link():
        if check_black_list(link):  # True if link in black list
            continue
        try:
            car_data = get_car_data(link)
            csv_writer.writerow(car_data)
            add_to_blacklist(link)
        except (IndexError, KeyError):  # Errors bellow is expected from the callable function above
            continue
        except StopIteration:
            break

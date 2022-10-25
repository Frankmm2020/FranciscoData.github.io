from distutils.log import info
from bs4 import BeautifulSoup
import requests
from csv import writer

url = "https://inmuebles.metroscubicos.com/casas/venta/chihuahua/chihuahua/#applied_filter_id%3Dcity%26applied_filter_name%3DCiudades%26applied_filter_order%3D2%26applied_value_id%3DTUxNQ0NISTQwOTM%26applied_value_name%3DChihuahua%26applied_value_order%3D5%26applied_value_results%3D1088%26is_custom%3Dfalse"


def get_data(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def write_csv(soup):
    lists = soup.find_all('div', class_="ui-search-result__content-wrapper shops__result-content-wrapper")
    with open('housing.csv', 'a', encoding='utf16', newline='') as f:
        writer1 = writer(f)
        for list in lists:
            title = list.find('h2', class_="ui-search-item__title ui-search-item__group__element shops__items-group-details shops__item-title").text
            location = list.find('span', class_="ui-search-item__group__element ui-search-item__location shops__items-group-details").text
            price = list.find('span', class_="price-tag-text-sr-only").text
            area = list.find('li', class_="ui-search-card-attributes__attribute").text
            info = [title, location, price, area]
            writer1.writerow(info)



def get_next_page(soup):
    page = soup.find('ul', 'ui-search-pagination andes-pagination shops__pagination')
    if page.find('li','andes-pagination__button andes-pagination__button--next shops__pagination-button'):
        url = (page.find('li','andes-pagination__button andes-pagination__button--next shops__pagination-button')).find('a')['href']
        return url
    else:
        return


with open('housing.csv', 'w', encoding='utf16', newline='') as f:
        writer1 = writer(f)
        header = ['Title', 'Location', 'Price', 'Area']
        writer1.writerow(header)
while True:
    soup = get_data(url)
    write_csv(soup)
    url = get_next_page(soup)
    if not url:
        break
    print(url)
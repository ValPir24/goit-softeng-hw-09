import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

# Функція для отримання даних зі сторінки з цитатами та запису їх у файли JSON
def scrape_quotes(url, quotes_file, authors_file):
    quotes = []
    authors = {}

    while url:
        # Отримуємо сторінку
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Знаходимо всі цитати на сторінці
        quote_elements = soup.find_all('div', class_='quote')
        for quote_element in quote_elements:
            text = quote_element.find('span', class_='text').text
            # Знаходимо автора за допомогою більш точних селекторів
            author_elem = quote_element.find('small', class_='author')
            author_name = author_elem.text.strip() if author_elem else "Unknown"
            # Знаходимо теги
            tags = [tag.text for tag in quote_element.find_all('a', class_='tag')]
            # Додавання цитати в список
            quotes.append({'tags': tags, 'author': author_name, 'quote': text})
            # Перевірка чи автор вже є в списку авторів
            if author_name not in authors:
                # Отримуємо посилання на сторінку автора
                author_url = urljoin(url, author_elem.find_next('a')['href'])
                # Отримуємо дані про автора
                author_data = scrape_author(author_url)
                authors[author_name] = author_data

        # Знаходимо посилання на наступну сторінку
        next_page = soup.find('li', class_='next')
        if next_page:
            url = urljoin(url, next_page.find('a')['href'])
        else:
            url = None

    # Зберігаємо цитати у файл quotes.json
    with open(quotes_file, 'w', encoding='utf-8') as f:
        json.dump(quotes, f, ensure_ascii=False, indent=4)

    # Зберігаємо авторів у файл authors.json
    with open(authors_file, 'w', encoding='utf-8') as f:
        # Перетворюємо словник на список перед збереженням
        authors_list = list(authors.values())
        json.dump(authors_list, f, ensure_ascii=False, indent=4)

# Функція для отримання даних про автора з його сторінки
def scrape_author(author_url):
    response = requests.get(author_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    fullname = soup.find('h3', class_='author-title').text.strip()
    born_date = soup.find('span', class_='author-born-date').text.strip()
    born_location = soup.find('span', class_='author-born-location').text.strip()
    description = soup.find('div', class_='author-description').text.strip()

    author_data = {
        'fullname': fullname,
        'born_date': born_date,
        'born_location': born_location,
        'description': description
    }

    return author_data

# Початкова URL-адреса сторінки з цитатами
starting_url = 'https://quotes.toscrape.com/'
# Назви файлів
quotes_file = 'quotes.json'
authors_file = 'authors.json'

# Виклик функції скрапінгу
scrape_quotes(starting_url, quotes_file, authors_file)

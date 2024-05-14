from mongoengine import connect, Document, StringField, ReferenceField, ListField, DoesNotExist, disconnect_all
import configparser
import json

config = configparser.ConfigParser()
config.read('config.ini')

mongo_user = config.get('DB', 'user')
mongodb_pass = config.get('DB', 'pass')
db_name = config.get('DB', 'db_name')
domain = config.get('DB', 'domain')

# Підключення до кластеру AtlasDB
connect(host=f"""mongodb+srv://{mongo_user}:{mongodb_pass}@{domain}.utwip5n.mongodb.net/{db_name}?retryWrites=true&w=majority""", ssl=True)

# Модель для авторів
class Author(Document):
    fullname = StringField(required=True)
    born_date = StringField()
    born_location = StringField()
    description = StringField()

# Модель для цитат
class Quote(Document):
    tags = ListField(StringField())
    author = ReferenceField(Author)
    quote = StringField(required=True)


# Відкриємо та завантажимо дані з файлів JSON
# Відкриваємо файл авторів
with open('authors.json', 'r') as f:
    authors_data = json.load(f)

# Зберігаємо авторів в базі даних
for author_data in authors_data:
    author = Author(
        fullname=author_data['fullname'],
        born_date=author_data.get('born_date'),
        born_location=author_data.get('born_location'),
        description=author_data.get('description')
    )
    author.save()

# Завантажуємо дані цитат
with open('quotes.json', 'r') as f:
    quotes_data = json.load(f)

# Зберігаємо цитати в базі даних
for quote_data in quotes_data:
    author_name = quote_data.get('author')
    author = Author.objects(fullname=author_name).first()
    if author:
        quote = Quote(
            tags=quote_data.get('tags'),
            author=author,
            quote=quote_data['quote']
        )
        quote.save()
    else:
        print(f"Автор '{author_name}' не знайдений в базі даних. Цитата не буде збережена.")

# Функція для пошуку цитат
def search_quotes(query):
    if query.startswith("name:"):
        author_name = query.split("name:")[1].strip()
        try:
            author = Author.objects.get(fullname=author_name)
            quotes = Quote.objects(author=author)
            print_quotes(quotes)
        except DoesNotExist:
            print("Автор не знайдений")
    elif query.startswith("tag:"):
        tag = query.split("tag:")[1].strip()
        quotes = Quote.objects(tags=tag)
        print_quotes(quotes)
    elif query.startswith("tags:"):
        tags = query.split("tags:")[1].strip().split(",")
        quotes = Quote.objects(tags__in=tags)
        print_quotes(quotes)
    elif query == "exit":
        print("До побачення!")
        disconnect_all()
        exit()
    else:
        print("Неправильний формат запиту")

# Функція для виведення цитат
def print_quotes(quotes):
    for quote in quotes:
        print(f"Цитата: {quote.quote}")
        try:
            print(f"Автор: {quote.author.fullname}")
        except DoesNotExist:
            print(f"Автор: Не визначений")
        print(f"Теги: {', '.join(quote.tags)}")
        print("-" * 50)

# Нескінченний цикл для пошуку цитат
while True:
    query = input("Введіть команду (або 'exit' для завершення): ").strip()
    search_quotes(query)
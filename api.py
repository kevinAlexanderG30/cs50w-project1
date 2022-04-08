import requests

def api1(isbn):
    isbn= isbn
    response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json()
    return response
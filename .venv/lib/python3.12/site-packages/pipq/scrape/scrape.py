import requests
from bs4 import BeautifulSoup
from pipq.display import display

def getSearchData(URL):
    try:
        page = requests.get(URL)
        soup = BeautifulSoup(page.content,'html.parser')
        pkglist = soup.find_all(class_='package-snippet')
        return pkglist
    except:
        display.ErrorPage()

def getPkgData(URL):
    page = requests.get(URL)
    if page.status_code == 404:
        display.ErrorPage()
    else:
        soup = BeautifulSoup(page.content,'html.parser')
        return soup

def githubData(URL):
    try:
        page = requests.get(URL)
        if page.status_code == 404:
            display.ErrorPage()
        else:
            soup = BeautifulSoup(page.content,'html.parser')
            conflict  = soup.find_all('a',{"class":"social-count"})
            stars = conflict[0]
            forks = conflict[1]
            return stars.text.strip(), forks.text.strip()
    except:
        display.ErrorPage()
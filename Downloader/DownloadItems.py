#Base url https://stationeers-wiki.com/index.php?title=Category:Items
from bs4 import BeautifulSoup
import requests

def ParsePage(Link):
    #Should return the item links and the next page links
    Source=requests.get(Link).content
    Parsed=BeautifulSoup(Source)
    
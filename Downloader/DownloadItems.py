#Base url https://stationeers-wiki.com/index.php?title=Category:Items

"""
GetLinks (First is for the next page):
#mw-pages a


"""


from bs4 import BeautifulSoup
import requests

def ParsePage(Link):
    #Should return the item links and the next page links
    Source=requests.get(Link).content
    Parsed=BeautifulSoup(Source)
    
from requests import get
from bs4 import BeautifulSoup
from re import compile
from dateparser import parse
from pandas import DataFrame

lijnen = []

base = "https://www.vlaamsparlement.be"

commissie_url = base + "/commissies/1053503/vergaderingen"
r = get(commissie_url)
html = r.text

soup = BeautifulSoup(html, "html5lib")

vergaderingen = soup.find_all("a", attrs={"href": compile(r'/commissies/commissievergaderingen/\d+')})

for vergadering in vergaderingen:
    vergadering_url = vergadering["href"]
    vergadering_datum = parse("/".join(vergadering.text.split(" ")[1:4]).rstrip(","))
    print(vergadering_datum)
    r = get(base + vergadering_url + "#volledige-agenda")
    vergaderhtml = r.text
    vergadersoup = BeautifulSoup(vergaderhtml, "html5lib")
    vragen = vergadersoup.find_all("a", attrs={"href": compile(r'/parlementaire-documenten/vragen-en-interpellaties/\d+')})
    for vraag in vragen:
        vraag_url = vraag["href"]
        vraag = vraag.text
        r = get(base + vraag_url)
        vraaghtml = r.text
        vraagsoup = BeautifulSoup(vraaghtml, "html5lib")
        dossierveld = vraagsoup.find("div", attrs={"class": "field--name-thema"})
        if dossierveld:
            dossier = dossierveld.find("div", attrs={"class": "field__item"}).a.text
            if dossier == "Cultuur":
                lijn = {"bron": "vlaams parlement", "date": vergadering_datum, "discipline": dossier, "full_text": None, "titel": vraag}
                print(lijn)
                lijnen.append(lijn)

df = DataFrame(lijnen, columns=["bron", "date", "discipline", "full_text", "titel"])
df.to_excel("parlementaire vragen.xlsx")

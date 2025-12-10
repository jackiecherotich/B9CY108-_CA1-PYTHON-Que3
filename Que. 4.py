# Web scrapping to csv

from bs4 import BeautifulSoup
import requests
import pandas as pd

url_2 = "https://booking-hotels2.tiiny.site/"
url_1 ="https://hotel1.tiiny.site/"


soup_2 = BeautifulSoup(requests.get(url_2).content, "html.parser")
soup_1 = BeautifulSoup(requests.get(url_1).content, "html.parser")


print(soup_2.prettify())
print(soup_1.prettify())

hotel2_cards = soup_2.find_all("div" ,class_="hotel-card")
print(hotel2_cards)
destination = soup_2.find("input", {"type": "text"})["value"]

hotel2_rooms = []

for card in hotel2_cards:

    # hotel info section
    card2_info = card.find("div", class_="hotel-info")

    name = card2_info.find("div", class_="hotel-name").text
    location = card2_info.find("div", class_="hotel-location").text
    distance_from_downtown = card2_info.find("div", class_="hotel-distance").get_text(strip=True).replace("from downtown", "")
    description = card2_info.find("div", class_="hotel-description").get_text(strip=True)

    # price section
    prices_section = card.find("div", class_="hotel-pricing")

    # rating
    rating = prices_section.find("div", class_="rating-score").text

    # price
    current_price = prices_section.find("div", class_="current-price").text
    current_price= float(current_price[2:])

    # nights info
    more_information = prices_section.find("div", class_="nights-info").text


    # To append on the list and then convert to csv using Pandas

    hotel2_rooms.append({
        'Name': name,
        'Location': location,
        'Distance from downtown': distance_from_downtown,
        'Description': description,
        'Current price (€)': current_price,
        'More information': more_information,
    })

# Panda DataFrame
hotel2_rooms  = pd.DataFrame(hotel2_rooms)
with open("Second Hotel Rooms Details.csv", "w") as f:
    f.write("Dublin Hotels Details \n")
    hotel2_rooms.to_csv(" Hotel Rooms Details.csv", index=False)







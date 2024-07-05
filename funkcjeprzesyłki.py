from bs4 import BeautifulSoup
import requests
import folium
import webbrowser
import os

def get_coords(shipment_location):
    adres_url = f'https://pl.wikipedia.org/wiki/{shipment_location}'
    response = requests.get(adres_url)
    response_html = BeautifulSoup(response.text, 'html.parser')
    latitude = float(response_html.select('.latitude')[1].text.replace(',', '.'))
    longitude = float(response_html.select('.longitude')[1].text.replace(',', '.'))
    print([latitude, longitude])
    return [latitude, longitude]


def show_shipments(shipments):
    # Wyświetla listę przesyłek firmy
    company_name = input("Podaj nazwę firmy, której lista przesyłek ma zostać wyświetlona: ")
    company_found = False

    # Sprawdzenie, czy firma istnieje wśród przesyłek
    for shipment in shipments:
        if shipment['shipment_company'] == company_name:
            company_found = True
            break

    # Wyświetlenie listy przesyłek, jeśli firma została znaleziona
    if company_found:
        print(f"Lista przesyłek firmy {company_name}:")
        for shipment in shipments:
            if shipment['shipment_company'] == company_name:
                print(f" - {shipment['shipment_name']}")
    else:
        print(f"{company_name} nie znaleziono takiej firmy na liście.")



def add_shipment(shipments, companies):
    # Dodaje nowegą przesyłkę do firmy
    company_name = input("Podaj nazwę firmy, do której chcesz dodać przesyłkę: ")
    company_found = False
    for company in companies:
        if company["company_name"] == company_name:
            shipment_name = input(f"Podaj nazwę przesyłki do dodania do {company_name}: ")
            shipment_location = input(f"Podaj lokalizację przesyłki (miasto): ")
            company_name=input(f"Podaj firmę, której {shipment_name} jest przesyłką: ")
            shipments.append({
                "shipment_name": shipment_name,
                "shipment_company": company_name,
                "shipment_location": shipment_location
            })
            print(f"{shipment_name} został(a) dodany(a) do listy przesyłek firmy {company_name}.")
            company_found = True
            break
    if not company_found:
        print(f"{company_name} nie znaleziono takiej firmy na liście.")


def remove_shipment(companies, shipments):
    # Usuwa przesyłkę z firmy
    company_name = input("Podaj nazwę firmy, z której chcesz usunąć przesyłkę: ")
    company_found = False

    # Sprawdzenie, czy firma istnieje wśród firm
    for company in companies:
        if company["company_name"] == company_name:
            company_found = True
            shipment_name = input(f"Podaj nazwę przesyłki do usunięcia z {company_name}: ")
            shipment_found = False

            # Przeszukiwanie listy przesyłek, aby znaleźć i usunąć przesyłkę
            for shipment in shipments:
                if shipment['shipment_name'] == shipment_name and shipment['shipment_company'] == company_name:
                    shipments.remove(shipment)
                    print(f"{shipment_name} został(a) usunięty(a) z listy przesyłek firmy {company_name}.")
                    shipment_found = True
                    break

            if not shipment_found:
                print(f"{shipment_name} nie znaleziono na liście przesyłek firmy {company_name}.")
            break

    if not company_found:
        print(f"{company_name} nie znaleziono takiej firmy na liście.")


def update_shipment(companies, shipments):
    # Aktualizuje dane przesyłki
    company_name = input("Podaj nazwę firmy, w której chcesz zaktualizować dane przesyłki: ")
    company_found = False

    # Sprawdzenie, czy firma istnieje wśród firm
    for company in companies:
        if company['company_name'] == company_name:
            company_found = True
            old_shipment_name = input(f"Podaj nazwę przesyłki do zaktualizowania w {company_name}: ")
            shipment_found = False

            # Przeszukiwanie listy przesyłek, aby znaleźć i zaktualizować przesyłkę
            for shipment in shipments:
                if shipment['shipment_name'] == old_shipment_name and shipment['shipment_company'] == company_name:
                    new_shipment_name = input(
                        f"Podaj nową nazwę dla {old_shipment_name} (pozostaw puste, aby nie zmieniać): ")
                    new_shipment_location = input(
                        f"Podaj nową lokalizację dla {old_shipment_name} (pozostaw puste, aby nie zmieniać): ")

                    # Aktualizacja przesyłki
                    if new_shipment_name:
                        shipment['shipment_name'] = new_shipment_name
                        print(f"Dane przesyłki zostały zmienione z {old_shipment_name} na {new_shipment_name}.")
                    # Aktualizacja lokalizacji, jeśli została podana
                    if new_shipment_location:
                        shipment['shipment_location'] = new_shipment_location
                        print(f"Lokalizacja przesyłki {old_shipment_name} została zmieniona na {new_shipment_location}.")

                    shipment_found = True
                    break

            if not shipment_found:
                print(f"{old_shipment_name} nie znaleziono na liście przesyłek firmy {company_name}.")
            break

    if not company_found:
        print(f"{company_name} nie znaleziono takiej firmy na liście.")



def dms_to_decimal(dms):
    parts = dms.split('°')
    degrees = float(parts[0])
    parts = parts[1].split('′')
    minutes = float(parts[0])
    parts = parts[1].split('″')
    seconds = float(parts[0])
    direction = parts[1].strip()

    decimal_degrees = degrees + minutes / 60 + seconds / 3600

    if direction in ['S', 'W']:
        decimal_degrees *= -1

    return decimal_degrees


def shipments_map(shipments):
    map = folium.Map(location=[52, 20], zoom_start=7)
    for shipment in shipments:
        shipment_name = shipment['shipment_name']
        shipment_location = shipment['shipment_location']
        url = f"https://pl.wikipedia.org/wiki/{shipment_location}"

        response = requests.get(url)
        response_html = BeautifulSoup(response.text, 'html.parser')

        latitude_tag = response_html.find('span', {'class': 'latitude'})
        longitude_tag = response_html.find('span', {'class': 'longitude'})

        if latitude_tag and longitude_tag:
            latitude = dms_to_decimal(latitude_tag.text)
            longitude = dms_to_decimal(longitude_tag.text)
            print(
                f"Przesyłka: {shipment_name}, Lokalizacja: {shipment_location}, Szerokość geograficzna: {latitude}, Długość geograficzna: {longitude}")
            folium.Marker(
                location=[latitude, longitude],
                popup=f"{shipment_name},\n{shipment_location}",
                icon=folium.Icon(color='red')
            ).add_to(map)
        else:
            print(f"Nie udało się znaleźć współrzędnych dla lokalizacji: {shipment_location}")

    map_dir = 'models/maps'
    os.makedirs(map_dir, exist_ok=True)

    map_file = os.path.join(map_dir, 'map_companies.html')
    map.save(map_file)
    webbrowser.open(map_file)
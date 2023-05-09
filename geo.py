import requests
from geopy import distance


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']
    #found_address=response.json()['response']['GeoObjectCollection']['featureMember']
    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def fetch_address(apikey, longitude,latitude, ):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": f'{longitude},{latitude}',
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    street=most_relevant['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['formatted']


    return street


def calculate_distance(user_coordinates, calculated_distance_pizzerias):
    for pizza in calculated_distance_pizzerias:
        latitude = pizza['Latitude']
        longitude = pizza['Longitude']
        pizza_distance = distance.distance(user_coordinates, (latitude, longitude)).km
        pizza["pizza_distance"] = pizza_distance

    return calculated_distance_pizzerias


def get_nearest_pizzeria(calculated_distance_pizzerias):
    return min(calculated_distance_pizzerias, key=lambda distance_pizza: distance_pizza["pizza_distance"])



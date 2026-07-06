from incremental_generator.config.constants import (LOCATION_MAP, COUNTRIES_WEIGHTS)
import numpy as np

def get_location_distribution(num_of_users):
    possible_countries = list(LOCATION_MAP.keys())
    countries = np.random.choice(possible_countries, size = num_of_users, p=COUNTRIES_WEIGHTS)

    regions = np.empty(num_of_users, dtype=object)
    cities = np.empty(num_of_users, dtype=object)

    for i in range(num_of_users):
        selected_country = countries[i]

        possible_regions = LOCATION_MAP[selected_country]["regions"]
        region_names = list(possible_regions.keys())

        possible_region_weights = [
            possible_regions[region]["region_weight"] for region in region_names
        ]

        selected_region = np.random.choice(region_names, p=possible_region_weights)

        possible_cities = LOCATION_MAP[selected_country]["regions"][selected_region]["cities"]
        city_names = possible_cities

        possible_city_weights = LOCATION_MAP[selected_country]["regions"][selected_region]["weights"]
        city_weights = list(possible_city_weights)

        selected_city = np.random.choice(city_names, p=city_weights)

        regions[i] = selected_region
        cities[i] = selected_city


    return {"regions": regions, "cities": cities, "countries": countries}

        
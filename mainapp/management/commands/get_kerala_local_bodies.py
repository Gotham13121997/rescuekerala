import os

from django.core.management.base import BaseCommand
from django.conf import settings

import requests
from bs4 import BeautifulSoup


url = "http://lsgelection.kerala.gov.in/public/search/voterlist"
headers = {
    'Content-Type': "application/x-www-form-urlencoded",
}

districts = {
    "1": "KASARAGOD",
    "2": "KANNUR",
    "3": "WAYANAD",
    "4": "KOZHIKODE",
    "5": "MALAPPURAM",
    "6": "PALAKKAD",
    "7": "THRISSUR",
    "8": "ERNAKULAM",
    "9": "IDUKKI",
    "10": "KOTTAYAM",
    "11": "ALAPPUZHA",
    "12": "PATHANAMTHITTA",
    "13": "KOLLAM",
    "14": "THIRUVANANTHAPURAM",
}


def get_wards_from_lsg_code(lsg_code):
    payload = "form%5BlocalBody%5D={0}".format(lsg_code)
    response = requests.request("POST", url, data=payload, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    ward_names_options = soup.find(id="form_ward")
    ward_names_dict = {
        ward['value']: ward.text
        for ward in ward_names_options.find_all('option')
        if ward['value']
    }
    return ward_names_dict


def get_lsg_details_for_district(district_key):
    payload = "form%5Bdistrict%5D={0}".format(district_key)
    response = requests.request("POST", url, data=payload, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    lsg_names_options = soup.find(id="form_localBody")
    lsg_names_dict = {
        lsg['value']: {"name": lsg.text, "wards": {}}
        for lsg in lsg_names_options.find_all('option')
        if lsg['value']
    }
    return lsg_names_dict


def get_govt_local_bodies():
    districts_mapping = {}

    for distr_key, distr_name in districts.items():
        print("--------------------> DISTRICT: ", distr_key, distr_name)
        lsg_names_dict = get_lsg_details_for_district(distr_key)

        for lsg_code, lsg_dict in lsg_names_dict.items():
            ward_names_dict = get_wards_from_lsg_code(lsg_code)
            lsg_names_dict[lsg_code]['wards'] = ward_names_dict
            print("-------------------> LSG: ", lsg_code)

        districts_mapping[distr_name] = lsg_names_dict

    return districts_mapping


class Command(BaseCommand):
    help = (
        'Read Kerala govt. local bodies from official website' 
        '(http://lsgelection.kerala.gov.in/) and save in a json file.'
    )

    def handle(self, *args, **options):
        """
        output format:

        local_bodies = {
            "ALAPPUZHA": {
                # lsg code
                "G04001": {
                  "name": "G04001 - Arookutty", # lsg name
                  "wards": {
                    "G04001001": "001 - MATHANAM",
                    "G04001002": "002 - OFFICE",
                    "G04001003": "003 - ST ANTONYS ",
                    ...
                  }
                },
                ...
        }
        """
        local_bodies = get_govt_local_bodies()
        file_path = os.path.join(settings.BASE_DIR + '/static/js/kerala_local_bodies.json')
        with open(file_path, 'w') as f:
            f.write(str(local_bodies))

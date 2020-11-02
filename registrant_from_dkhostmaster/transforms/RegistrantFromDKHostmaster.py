import requests

from typing import Dict

from maltego_trx.entities import Location, PhoneNumber, Person
from maltego_trx.transform import DiscoverableTransform


class RegistrantFromDKHostmaster(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request, response):

        website = request.Value
        registrant = cls.get_registrant(website=website)
        if registrant is None:
            return None

        if registrant['phone'] is not None:
            ent = response.addEntity(PhoneNumber, registrant['phone'])
            ent.addProperty('Phone type', 'Phone', 'loose', 'Phone')
        if 'mobilephone' in registrant and registrant['mobilephone'] is not None:
            ent = response.addEntity(PhoneNumber, registrant['mobilephone'])
            ent.addProperty('Phone type', 'Mobile Phone', 'loose', 'Mobile Phone')
        if 'telefax' in registrant and registrant['telefax'] is not None:
            ent = response.addEntity(PhoneNumber, registrant['telefax'])
            ent.addProperty('Phone type', 'Telefax', 'loose', 'Telefax')
        if registrant['attention'] is not None:
            response.addEntity(Person, registrant['attention'])

        if cls.has_location(registrant):

            entity = cls.create_location(registrant, response)
            if registrant['city'] is not None:
                entity.addProperty('city', registrant['city'], 'strict', registrant['city'])
            if registrant['countryregionid'] is not None:
                entity.addProperty('countrycode', registrant['countryregionid'], 'strict', registrant['countryregionid'])
                entity.addProperty('country', registrant['countryregionid'], 'strict', registrant['countryregionid'])
            if registrant['street1'] is not None:
                entity.addProperty('streetaddress', registrant['street1'], 'strict', registrant['street1'])
            if registrant['zipcode'] is not None:
                entity.addProperty('location.areacode', registrant['zipcode'], 'strict', registrant['zipcode'])
            if registrant['street2'] is not None:
                entity.addProperty('street2', registrant['street2'], 'strict', registrant['street2'])
            if registrant['street3'] is not None:
                entity.addProperty('street3', registrant['street3'], 'strict', registrant['street3'])

    @staticmethod
    def create_location(registrant: Dict, response):
        def create_entity(label):
            return response.addEntity(Location, label)
        label = None
        if registrant['name'] is not None:

            label = registrant['name']
        elif registrant['street1'] is not None:
            label = registrant['street1']
        elif registrant['street2'] is not None:
            label = registrant['street2']
        elif registrant['street3'] is not None:
            label = registrant['street3']
        elif registrant['countryregionid'] is not None:
            label = registrant['countryregionid']
        elif registrant['zipcode'] is not None:
            label = registrant['zipcode']
        else:
            response.addUIMessage(f'No location information found')

        entity = create_entity(label=label)
        return entity

    @staticmethod
    def has_location(registrant: Dict) -> bool:
        r = registrant
        return  r['city'] is not None or r['countryregionid'] is not None \
             or r['street1'] is not None or r['street2'] is not None \
             or r['street3'] is not None or r['zipcode'] is not None


    @staticmethod
    def get_registrant(website):

        dk_host_url = f'https://whois-api.dk-hostmaster.dk/domain/{website}'
        res = requests.get(dk_host_url, headers={'Accept': 'application/json'})

        if res.status_code == requests.status_codes.codes.ok:
            dk_info = res.json()
            if 'registrant' in dk_info:
                return dk_info['registrant']

        return None

if __name__ == "__main__":
    print(RegistrantFromDKHostmaster.get_registrant("nine.dk"))

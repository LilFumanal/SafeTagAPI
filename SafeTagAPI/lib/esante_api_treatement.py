import asyncio
import requests
from django.db import transaction
from django.core.cache import cache
from bs4 import BeautifulSoup
import aiohttp
import logging
logger = logging.getLogger(__name__)

# Définir l'URL et les en-têtes d'authentification
esante_api_url = "https://gateway.api.esante.gouv.fr/fhir"
headers = {"ESANTE-API-KEY": "inserercode"}
role=["10","93"] #https://mos.esante.gouv.fr/NOS/TRE_G15-ProfessionSante/TRE_G15-ProfessionSante.pdf
mental_health_specialties = [ #https://mos.esante.gouv.fr/NOS/TRE_R38-SpecialiteOrdinale/FHIR/TRE-R38-SpecialiteOrdinale/TRE_R38-SpecialiteOrdinale-FHIR.json
    "SM33",
    "SM42",
    "SM43",
    "SM92",
    "SM93"
]#
specialty_filter = "specialty=" + ",".join(mental_health_specialties)
role_filter = "role=" + ",".join(role)
inclusions = "?_include=PractitionerRole:organization"

base_url = f"{esante_api_url}/PractitionerRole?{role_filter}&{specialty_filter}"

# Envoyer la requête
async def get_all_practitioners(url = base_url):
    cache.clear()
    next_page = ""
    logger.info("We'll search the practitioners soon")
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.debug(f"Response received!")
                    practitioners_list = []
                    if "entry" in data:
                        for entry in data["entry"]:
                            practitioner_data = process_practitioner_entry(entry)
                            practitioners_list.append(practitioner_data)
                    if 'link' in data:
                        for link in data['link']:
                            if link['relation'] == 'next':
                                next_page_url = link['url']
                                break
                    return practitioners_list, next_page
                else:
                    logger.error(f"Failed requests: {response.status}: {response.text}")
                    return f"Erreur {response.status} : {response.text}", None
    except aiohttp.ClientError as e:
        logger.error(f"Request failed: {e}")
        return f"Request failed: {e}", None
    except asyncio.TimeoutError:
        logger.error("Request timeout")
        return "Request timeout", None

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return f"Unexpected error: {e}", None


def process_practitioner_entry(entry):
    practitioner_role = entry.get("resource", {})
    api_id = practitioner_role.get("id")

    name, surname = extract_name_and_surname(practitioner_role.get("extension", []))
    organization_reference = practitioner_role.get("organization", {}).get(
        "reference", "N/A"
    )
    organization_info, org_addresses = get_organization_info(organization_reference)
    if not organization_info or not org_addresses:
        return None
    specialties = get_specialities(practitioner_role.get("specialty", []))
    sector = get_speciality_reimboursement_sector(practitioner_role.get("code", []))

    practitioner_data = {
        "name": name,
        "surname": surname,
        "specialities": specialties,
        "accessibilities": {"LSF": "Unknown", "Visio": "Unknown"},
        "reimboursement_sector": sector,
        "addresses": org_addresses,
        "organizations": [organization_info],
        "api_id": api_id,
    }
    return practitioner_data


def extract_name_and_surname(extensions):
    name = "N/A"
    surname = "N/A"
    for extension in extensions:
        if (
            extension.get("url")
            == "https://annuaire.sante.gouv.fr/fhir/StructureDefinition/PractitionerRole-Name"
        ):
            human_name = extension.get("valueHumanName", {})
            name = human_name.get("family", "")
            given = " ".join(human_name.get("given", []))
            surname = f"{given}".strip()
    return name, surname


def get_organization_info(org_reference):
    org_url = f"{esante_api_url}/{org_reference}"
    cached_result = cache.get(org_url)
    if cached_result is not None:
        return cached_result
    try:
        response = requests.get(org_url, headers=headers)
        if response.status_code == 200:
            org_data = response.json()
            if org_data.get("address", []) is None:
                return None, None
            else:
                org_addresses = collect_addresses(org_data.get("address", []))
                api_organization_id = org_data.get("id")
                organization_info = {
                    "name": org_data.get("name", "N/A"),
                    "api_organization_id": api_organization_id,
                    "addresses": org_addresses,
                }
                cache.set(org_url, (organization_info, org_addresses), timeout=24*60*60)
            return organization_info, org_addresses
        else:
            return None, None
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur de requête : {e}")
        return None, None


def get_specialities(specialties):
    specialities_list = []
    for specialty in specialties:
        for coding in specialty.get("coding", []):
            code = coding.get("code", "N/A")
            lien = coding.get("system")
            if lien == 'https://mos.esante.gouv.fr/NOS/TRE_R04-TypeSavoirFaire/FHIR/TRE-R04-TypeSavoirFaire':
                continue
            else:
                description = get_speciality_description(lien, code)
                if description:  # Ensure we only add valid descriptions
                    specialities_list.append(description)
                    logger.debug(description)
                else:
                    logger.debug("No description found for code: %s, lien: %s", code, lien)
    return specialities_list


def get_speciality_description(lien, code):
    # Generate a cache key based on the parameters
    cache_key = f"specialty_{lien}_{code}"
    # Try to get the result from the cache
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    try:
        response_dir=requests.get(str(lien), timeout = 30)
        soup = BeautifulSoup(response_dir.text, "html.parser")
        json_files = [
            a["href"]
            for a in soup.find_all("a", href=True)                
            if a["href"].endswith(".json")
        ]
        json_url = lien + '/' + json_files[0]
        logger.debug("Url JSON %s", json_url)
        json_response = requests.get(json_url)
        json_response.raise_for_status()
        json_data = json_response.json()            
        if 'concept' in json_data:
            logger.debug("OUIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII")
            concepts = json_data['concept']
            descriptions = []
            for concept in concepts:
                if code == concept.get('code'):
                    description = concept.get('display') or concept.get('description')
                    cache.set(cache_key, description)
                    logger.debug("UN RESULTAT A ETE AJOUTE MAIS MON DIEU MAIS C'EST INCROYABLE")
                    logger.debug(description)
                    descriptions.append(description)
            return description
        else:
            return "Description non trouvée"
    except requests.exceptions.RequestException as e:
        logger.error("Request exception: %s", {e})
        return f"Request failed: {e}"
    
    except Exception as e:
        logger.error("Unexpected error: %s ",{e}, exc_info=True)
        return f"Unexpected error: {e}"

def get_speciality_reimboursement_sector(codes):
    # Pour trouver les secteurs de remboursement, nous devons visiblement passer par une api tierce. Par soucis de temps, nous le ferons plus tard .
    # https://interop.esante.gouv.fr/ig/fhir/ror/mapping.html
    return "Aucun secteur renseigné"


def collect_addresses(addresses):
    address_list = []
    house_number = ""
    street_name_type = ""
    street_name_base = ""
    for address in addresses:
        # Check if '_line' extensions exist and are not empty
        if "_line" in address and address["_line"]:
            # Extract extensions from '_line'
            line_extensions = address["_line"][0].get("extension", [])
            for ext in line_extensions:
                if (
                    ext.get("url")
                    == "http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-houseNumber"
                ):
                    house_number = ext.get("valueString", "")
                elif (
                    ext.get("url")
                    == "http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-streetNameType"
                ):
                    street_name_type = ext.get("valueString", "")
                elif (
                    ext.get("url")
                    == "http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-streetNameBase"
                ):
                    street_name_base = ext.get("valueString", "")

        # Combine components into a full address line
        line = f"{house_number} {street_name_type} {street_name_base}".strip()
        city = address.get("city", "N/A")
        postal_code = address.get("postalCode", "N/A")
        department = get_department(postal_code)
        # Here would be implemented the call function to convert entire addresses in location datas
        latitude = address.get("latitude", None)
        longitude = address.get("longitude", None)
        address_list.append(
            {
                "line": line,
                "city": city,
                "department": department,
                "latitude": latitude,
                "longitude": longitude,
            }
        )
    return address_list


def get_map_coordinates(address):
    pass


def get_department(postal_code):
    if not postal_code:
        return "N/A"
    postal_code = str(postal_code)
    if postal_code.startswith("97") or postal_code.startswith("98"):
        if postal_code[:3] == "971":
            return "971"  # Guadeloupe
        elif postal_code[:3] == "972":
            return "972"  # Martinique
        elif postal_code[:3] == "973":
            return "973"  # French Guiana
        elif postal_code[:3] == "974":
            return "974"  # Réunion
        elif postal_code[:3] == "975":
            return "975"  # Saint Pierre and Miquelon
        elif postal_code[:3] == "976":
            return "976"  # Mayotte
        elif postal_code[:3] == "977":
            return "977"  # Saint Barthélemy
        elif postal_code[:3] == "978":
            return "978"  # Saint Martin
        elif postal_code[:3] == "984":
            return "984"  # French Southern Territories
        elif postal_code[:3] == "986":
            return "986"  # Wallis and Futuna
        elif postal_code[:3] == "987":
            return "987"  # French Polynesia
        elif postal_code[:3] == "988":
            return "988"  # New Caledonia
        elif postal_code[:3] == "989":
            return "989"  # Clipperton Island
        else:
            return postal_code[:3]  # Default to the first three digits
    # For metropolitan France, use the first two digits
    return postal_code[:2]


async def get_practitioner_details(api_practitioner_id):
    try:
        url = f"{esante_api_url}/PractitionerRole/{api_practitioner_id}"
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    practitioner_data = await response.json()
                    extensions = practitioner_data.get("extension", [])
                    name, surname = extract_name_and_surname(extensions)
                    organization_reference = practitioner_data.get("organization", {}).get(
                        "reference", None
                    )
                    organization_info, org_addresses = get_organization_info(
                        organization_reference
                    )
                    if not org_addresses:
                        logger.error("There isn't any address valid for this practitioner, so we can't register them in our database.")
                        return None
                    specialties = get_specialities(practitioner_data.get("specialty", []))
                    sector = get_speciality_reimboursement_sector(
                        practitioner_data.get("code", [])
                    )
                    api_id = practitioner_data.get("id")
                        # Prepare the data for serialization
                    data_for_serializer = {
                        "name": name,
                        "surname": surname,
                        "specialities": specialties,
                        "accessibilities": {"LSF": "Unknown", "Visio": "Unknown"},
                        "reimboursement_sector": sector,
                        "addresses": org_addresses,
                        "organizations": [organization_info],
                        "api_id": api_id,
                    }
                        # Serialize and save the practitioner data

                    return data_for_serializer
                else:
                    return f"Error {response.status} : {await response.text()}"
    except aiohttp.ClientError as e:
        return f"Request failed: {e}"

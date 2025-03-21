import asyncio
import os
from pathlib import Path
from socket import timeout
from aiocache import cached
import requests
from bs4 import BeautifulSoup
import aiohttp
import logging
import environ

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))
logger = logging.getLogger(__name__)


# Définir l'URL et les en-têtes d'authentification
ESANTE_API_URL = "https://gateway.api.esante.gouv.fr/fhir"
HEADERS = {"ESANTE-API-KEY": env.str('ESANTE_API_KEY')}
ROLE = ["10", "93"]  # https://mos.esante.gouv.fr/NOS/TRE_G15-ProfessionSante/TRE_G15-ProfessionSante.pdf
MENTAL_HEALTH_SPECIALTIES = [  # https://mos.esante.gouv.fr/NOS/TRE_R38-SpecialiteOrdinale/FHIR/TRE-R38-SpecialiteOrdinale/TRE_R38-SpecialiteOrdinale-FHIR.json
    "SM33",
    "SM42",
    "SM43",
    "SM92",
    "SM93"
]
SPECIALTY_FILTER = "specialty=" + ",".join(MENTAL_HEALTH_SPECIALTIES)
ROLE_FILTER = "role=" + ",".join(ROLE)
INCLUSIONS = "?_include=PractitionerRole:organization"

BASE_URL = f"{ESANTE_API_URL}/PractitionerRole?{ROLE_FILTER}&{SPECIALTY_FILTER}"

# Envoyer la requête
@cached(ttl=7*24*60*60)
async def get_all_practitioners(url = BASE_URL):
    next_page = ""
    timeout = aiohttp.ClientTimeout(total=60)
    logger.info("We'll search the practitioners soon")
    try:
        async with aiohttp.ClientSession(headers=HEADERS, timeout=timeout) as session:
            async with session.get(url) as response:
                data = await response.json()
                logger.debug("Response received: %s", response.status)
                practitioners_list = []
                if "entry" in data:
                    for entry in data["entry"]:
                        practitioner_data = await process_practitioner_entry(entry)
                        practitioners_list.append(practitioner_data)
                if 'link' in data:  
                    for link in data['link']:
                        if link['relation'] == 'next':
                            next_page = link['url']
                            break
                return practitioners_list, next_page
                
    except aiohttp.ClientError as e:
        logger.error("Request failed: %s", e)
        return f"Request failed: {e}", None
    except asyncio.TimeoutError:
        logger.error("Request timeout")
        return "Request timeout", None
    except Exception as e:
        logger.error("Unexpected error: %s", e, exc_info=True)
        return f"Unexpected error: {e}", None


async def process_practitioner_entry(entry):
    practitioner_role = entry.get("resource", {})
    api_id = practitioner_role.get("id")

    name, surname = extract_name_and_surname(practitioner_role.get("extension", []))
    organization_reference = practitioner_role.get("organization", {}).get(
        "reference", "N/A"
    )
    organization_info, org_addresses = await get_organization_info(organization_reference)
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


@cached(ttl=7*24*60*60)
async def get_organization_info(org_reference):
    org_url = f"{ESANTE_API_URL}/{org_reference}"
    try:
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.get(org_url) as response:
                if response.status == 200:
                    org_data = await response.json()
                    if org_data.get("address", []) is None:
                        return None, None
                    else:
                        org_addresses = await collect_addresses(org_data.get("address", []))
                        api_organization_id = org_data.get("id")
                        organization_info = {
                            "name": org_data.get("name", "N/A"),
                            "api_organization_id": api_organization_id,
                            "addresses": org_addresses,
                        }
                    return organization_info, org_addresses
                else:
                    return None, None
    except aiohttp.ClientError as e:
        logger.error("Erreur de requête : %s", e)
        return None, None


@cached(ttl=30*24*60*60)
async def get_specialities(specialities):
    specialities_list = []
    for specialty in specialities:
        for coding in specialty.get("coding", []):
            code = coding.get("code", "N/A")
            lien = coding.get("system")
            if lien == 'https://mos.esante.gouv.fr/NOS/TRE_R04-TypeSavoirFaire/FHIR/TRE-R04-TypeSavoirFaire':
                continue
            else:
                description = await get_speciality_description(lien, code)
                if description:  # Ensure we only add valid descriptions
                    specialities_list.append(description)
                    logger.debug(description)
                else:
                    logger.debug("No description found for code: %s, lien: %s", code, lien)
    return specialities_list

@cached(ttl=30*24*60*60)
async def get_speciality_description(lien, code):
    try:
        async with aiohttp.ClientSession() as session:
            response_dir = await session.get(lien, timeout=30)
            soup = BeautifulSoup(await response_dir.text(), "html.parser")
            json_files = [
                a["href"]
                for a in soup.find_all("a", href=True)                
                if a["href"].endswith(".json")
            ]
            json_url = lien + '/' + json_files[0]
            logger.debug("Url found : %s", json_url)
            json_response = await session.get(json_url, timeout=30)
            json_response.raise_for_status()
            json_data = await json_response.json()            
            if 'concept' in json_data:
                concepts = json_data['concept']
                descriptions = []
                for concept in concepts:
                    if code == concept.get('code'):
                        description = concept.get('display') or concept.get('description')
                        descriptions.append(description)
                return description
            else:
                return "Description non trouvée"
    except aiohttp.ClientError as e:
        logger.error("Request exception: %s", {e})
        return f"Request failed: {e}"
    
    except Exception as e:
        logger.error("Unexpected error: %s ",{e}, exc_info=True)
        return f"Unexpected error: {e}"

def get_speciality_reimboursement_sector(codes):
    # Il n'est pour l'instant poas possible de récupérer ces informations.
    # https://interop.esante.gouv.fr/ig/fhir/ror/mapping.html
    return "Aucun secteur renseigné"


async def collect_addresses(addresses):
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
        if postal_code.startswith("971"):
            return "971"  # Guadeloupe
        if postal_code.startswith("972"):
            return "972"  # Martinique
        if postal_code.startswith("973"):
            return "973"  # French Guiana
        if postal_code.startswith("974"):
            return "974"  # Réunion
        if postal_code.startswith("975"):
            return "975"  # Saint Pierre and Miquelon
        if postal_code.startswith("976"):
            return "976"  # Mayotte
        if postal_code.startswith("977"):
            return "977"  # Saint Barthélemy
        if postal_code.startswith("978"):
            return "978"  # Saint Martin
        if postal_code.startswith("984"):
            return "984"  # French Southern Territories
        if postal_code.startswith("986"):
            return "986"  # Wallis and Futuna
        if postal_code.startswith("987"):
            return "987"  # French Polynesia
        if postal_code.startswith("988"):
            return "988"  # New Caledonia
        if postal_code.startswith("989"):
            return "989"  # Clipperton Island
        else:
            return postal_code[:3]  # Default to the first three digits
    # For metropolitan France, use the first two digits
    return postal_code[:2]


async def get_practitioner_details(api_practitioner_id):
    timeout = aiohttp.ClientTimeout(total=30)
    try:
        url = f"{ESANTE_API_URL}/PractitionerRole/{api_practitioner_id}"
        async with aiohttp.ClientSession(headers=HEADERS, timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    practitioner_data = await response.json()
                    extensions = practitioner_data.get("extension", [])
                    name, surname = extract_name_and_surname(extensions)
                    organization_reference = practitioner_data.get("organization", {}).get(
                        "reference", None
                    )
                    organization_info, org_addresses = await get_organization_info(
                        organization_reference
                    )
                    if not org_addresses:
                        logger.error("There isn't any address valid for this practitioner, so we can't register them in our database.")
                        return None
                    specialties = await get_specialities(practitioner_data.get("specialty", []))
                    api_id = practitioner_data.get("id")
                        # Prepare the data for serialization
                    data_for_serializer = {
                        "name": name,
                        "surname": surname,
                        "specialities": specialties,
                        "accessibilities": {"LSF": "Unknown", "Visio": "Unknown"},
                        "reimboursement_sector": None,
                        "organizations": [organization_info],
                        "api_id": api_id,
                    }
                        # Serialize and save the practitioner data
                    return data_for_serializer
                else:
                    return {"error": f"HTTP error {response.status}", "details": await response.text()}
    except aiohttp.ClientError as e:
        return {"error": "Request failed", "details": str(e)}
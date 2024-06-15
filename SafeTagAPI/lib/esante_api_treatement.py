from collections import defaultdict
from celery import shared_task
from django.core.cache import cache
import requests
from bs4 import BeautifulSoup
from SafeTagAPI.serializers.practitioner_serializer import PractitionerSerializer, Practitioners

# Définir l'URL et les en-têtes d'authentification
esante_api_url = "https://gateway.api.esante.gouv.fr/fhir"
headers = {"ESANTE-API-KEY": "628abf0c-223d-4584-bf65-9455453f79af", "specialty": "17"}
inclusions = "?_include=PractitionerRole:organization"
mos_api_url = "https://mos.esante.gouv.fr/NOS"


# Envoyer la requête
def get_all_practitioners():
    url = f"{esante_api_url}/PractitionerRole"
    response = requests.get(url, headers=headers)
    # Check if the request was successful
    try:
        if response.status_code == 200:
            data = response.json()
            if "entry" in data:
                for entry in data["entry"]:
                    practitioner_role = entry.get("resource", {})
                    api_id= entry.get('id')

                    # Extraire le nom complet du praticien
                    extensions = practitioner_role.get("extension", [])
                    name = "N/A"
                    for extension in extensions:
                        if (
                            extension.get("url")
                            == "https://annuaire.sante.gouv.fr/fhir/StructureDefinition/PractitionerRole-Name"
                        ):
                            human_name = extension.get("valueHumanName", {})
                            family = human_name.get("family", "")
                            given = " ".join(human_name.get("given", []))
                            suffix = " ".join(human_name.get("suffix", []))
                            name = f"{given} {family} {suffix}".strip()

                    # Afficher les informations extraites
                    print(f"Nom du praticien : {name}")
                    organization_reference = practitioner_role.get("organization", {}).get(
                        "reference", "N/A"
                    )
                    get_organization_info(organization_reference)
                    codes = practitioner_role.get("code", [])
                    sector = get_speciality_reimboursement_sector(codes)
                    print(f"Secteur de remboursement: {sector}")
                    # Afficher toutes les spécialités
                    specialties = practitioner_role.get("specialty", [])
                    print("Spécialités :")
                    for specialty in specialties:
                        for coding in specialty.get("coding", []):
                            code = coding.get("code", "N/A")
                            system = coding.get("system")
                            description = get_specialty_description(system, code)
                            print(
                                f" - Code : {code}, Description : {description}, System: {system}"
                            )
                    print("\n")
            else:
                print("Aucune entrée trouvée dans la réponse.")
        else:
            print(f"Erreur {response.status_code} : {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

# Fonction pour obtenir la description d'une spécialité via son code et système
def get_specialty_description(system, code):
    try:
        response_dir = requests.get(system, timeout=30)
        # Charger le fichier JSON à partir de l'URL du système
        soup = BeautifulSoup(response_dir.text, "html.parser")
        json_files = [
            a["href"]
            for a in soup.find_all("a", href=True)
            if a["href"].endswith(".json")
        ]
        json_url = f"{system}/{json_files[0]}"
        response = requests.get(json_url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            concepts = data.get("concept", [])
            # Parcourir les concepts pour trouver le code correspondant
            for concept in concepts:
                if concept.get("code") == code:
                    return concept.get("display", "Description non trouvée")
        else:
            return response.status_code
    except requests.exceptions.RequestException as e:
        return f"Erreur de requête : {e}"


def get_speciality_reimboursement_sector(codes):
    sector = "Aucun secteur renseigné"
    for code_entry in codes:
        for coding in code_entry.get("coding", []):
            if (
                coding.get("system")
                == "https://mos.esante.gouv.fr/NOS/TRE_R23-ModeExercice/FHIR/TRE-R23-ModeExercice"
            ):
                sector = coding.get("code")
    return sector


def get_organization_info(org_reference):
    org_url = f"{esante_api_url}/{org_reference}"
    response = requests.get(org_url, headers=headers)
    if response.status_code == 200:
        org_data = response.json()
        display_organization_details(org_data)
    else:
        print(response.status_code)


def display_organization_details(org_data):
    # Display organization name
    name = org_data.get("name", "N/A")
    print(f"Organization Name: {name}")

    # Display organization identifiers
    identifiers = org_data.get("identifier", [])
    print("Identifiers:")
    for identifier in identifiers:
        id_type = identifier.get("type", {}).get("coding", [{}])[0].get("code", "N/A")
        id_value = identifier.get("value", "N/A")
        print(f" - Type: {id_type}, Value: {id_value}")

    # Display contact details
    telecom = org_data.get("telecom", [])
    print("Contact Details:")
    for contact in telecom:
        system = contact.get("system", "N/A")
        value = contact.get("value", "N/A")
        rank = contact.get("rank", "N/A")
        print(f" - {system.capitalize()}: {value} (Rank: {rank})")

    # Display address details
    addresses = org_data.get("address", [])
    print("Addresses:")
    for address in addresses:
        line = address.get("line", ["N/A"])
        city = address.get("city", "N/A")
        postal_code = address.get("postalCode", "N/A")
        extensions = address.get("extension", [])
        print(
            f" - Address: {', '.join(filter(None, line))}, City: {city}, Postal Code: {postal_code}"
        )
        for extension in extensions:
            ext_url = extension.get("url")
            ext_value = extension.get("valueCoding", {}).get("code", "N/A")
            print(f"   - Extension URL: {ext_url}, Value: {ext_value}")

    # Display parent organization reference
    parent_org = org_data.get("partOf", {}).get("reference", "N/A")
    print(f"Parent Organization: {parent_org}")

    
def get_practitioner_details(api_practitioner_id):
    try:
        # Fetch from API if not in cache
        url = f"{esante_api_url}/PractitionerRole/{api_practitioner_id}"
        response = requests.get(url, headers=headers) 
        if response.status_code == 200:
            practitioner_data = response.json()
            cache_key = f"practitioner_{api_practitioner_id}"
            cache.set(cache_key, practitioner_data, timeout=60 * 60 * 24)
            serializer = PractitionerSerializer(data=practitioner_data)
            if serializer.is_valid():
                practitioner = serializer.save()
                return practitioner
            else:
                print("Validation error:", serializer.errors)
                return None
        else:
            print(f"Error {response.status_code} : {response.text}")
            return None
    except requests.RequestException:
        return None
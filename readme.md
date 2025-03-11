# SafeTag API

Welcome on the SafeTag API, where you can access every mentalhealth practitioners practicing in France through the [https://gateway.api.esante.gouv.fr/fhir](Esante API datas), but also the comments of former patients they had.
Users will be able to anonymously leave a comprehensive review of their experience with a practitioner, regarding their attitude towards discrimination issues that anyone might face, as well as the families of pathologies mentioned, in order to reassure and inform future patients about the practitioners around them.
In accordance with French legislation on the use of this data, any practitioner can request to be removed from this list by contacting us at "safetagadmin.fr".

## API Usage and Rights

### Terms of Use

The use of the API is only dedicated to learning projects. Every other use is prohibited.

### Access to the API

To access the API, users must:

1. **Register for an API Key**: Users must register and obtain an API key to access the API. The API key must be included in all requests to authenticate the user.
2. **Use the API Key Responsibly**: Users are responsible for keeping their API key secure and must not share it with others. If an API key is compromised, users must notify the API provider immediately.

### Contact Information

For any questions or concerns regarding the use of this API, or to request commercial access, please contact us at:

- Email: safetagadmin.fr

### Disclaimer

The API provider reserves the right to modify or discontinue the API at any time without notice. The API provider is not liable for any damages or losses resulting from the use of the API.

## Dependencies

For this project, the following file has to list the python dependencies of your project.

- **requirements.txt** set your app dependencies here and set version requirements if needed.
- To ensure a better handling, make sure to also activate a **redis server** to cache the datas.

## About environment

The file named **.env-template** list the required environnement variables that your project need, but **does not** contains any citical informations such as credentials. It can contains **example values**. It's purpose is to show how to build the **.env** file.
The **.env** needs to be listed in the **.gitignore**, it's **not versionned**, it's **only in your system**.

---

## Configuration

- You need to have access to a PostgresQL database.
- You should use **python 3.12.2**
- Install the dependencies from requirements.txt (maybe in a virtual environment)
- Create you .env file based on .env-template.
- Run a [https://redis.io/downloads/](redis server). **If you don't cache the datas, your requests would be denied.**

## How to use

Run the following command to launch the Django server :

- `python manage.py migrate`
- `python manage.py createsuperuser`
- `python manage.py pathologies`
- `python manage.py tags`
- `python manage.py runserver`

## API Endpoints

### Reviews

- **Create a Review**: `POST /reviews/`

  - Custom create method to handle fetching practitioner data from the API if not present.
  - Example request body:
    ```json
    {
      "id_practitioner": "practitioner_api_id",
      "tags": ["tag1", "tag2"],
      "pathologies": ["pathology1", "pathology2"],
      "id_address": 1,
      "comment": "This is a review comment."
    }
    ```

- **Get Reviews for a Practitioner**: `GET /reviews/{practitioner_id}/practitioner_reviews/`
  - Retrieves all reviews for a specific practitioner.

### Practitioners

- **Get Practitioner Details**: `GET /practitioner/{id}/`

  - Retrieves details of a specific practitioner, including tag averages.

- **Get Reviews for a Practitioner**: `GET /practitioner/{id}/reviews/`

  - Retrieves all reviews for a specific practitioner.

- **Update Practitioner Accessibilities**: `POST /practitioner/update_accessibilities/`
  - Allows users to update accessibility details for a practitioner.
  - Example request body:
    ```json
    {
      "api_id": "practitioner_api_id",
      "accessibilities": { "LSF": "Yes", "Visio": "No" }
    }
    ```

### Practitioner Addresses

- **List Practitioner Addresses**: `GET /practitioner_addresses/`

  - Retrieves a list of practitioner addresses.

- **Retrieve a Practitioner Address**: `GET /practitioner_addresses/{id}/`

  - Retrieves details of a specific practitioner address.

- **Update Wheelchair Accessibility**: `PATCH /practitioner_addresses/{id}/`
  - Allows updating only the `wheelchair_accessibility` field.
  - Example request body:
    ```json
    {
      "wheelchair_accessibility": true
    }
    ```

### Organizations

- **List Organizations**: `GET /organizations/`

  - Retrieves a list of organizations.

- **Retrieve an Organization**: `GET /organizations/{id}/`
  - Retrieves details of a specific organization.

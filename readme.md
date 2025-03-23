# SafeTag API

Welcome on the SafeTag API, where you can access every mentalhealth practitioners practicing in France through the [Esante API datas](https://gateway.api.esante.gouv.fr/fhir), but also the comments of former patients they had.
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
- Run a [redis server](https://redis.io/downloads/). **If you don't cache the datas, your requests would be denied.**

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

### Practitioners

- **Get Practitioner List**: `GET /practitioners/`

  - Retrieves the list of practitioners from the esante api.

- **Get Practitioner Details**: `GET /practitioner/{api-id}/`

  - Retrieves details of a specific practitioner, with him being registered in our database or not.

- **Post Practitioner Details**: `POST /practitioner/{api-id}/`

  - Register a practitioner in database. For testing purpoose only. Automatically triggered by the creation of a review.

- **Get Reviews for a Practitioner**: `GET /practitioner/{api_id}/reviews/`

  - Retrieves all reviews for a specific practitioner.

- **Update Practitioner Accessibilities**: `PATCH /practitioner/{api_id}`
  - Allows users to update accessibility details for a practitioner.
  - Example request body:
    ```json
    {
      "api_id": "practitioner_api_id",
      "accessibilities": { "LSF": "Yes", "Visio": "No" }
    }
    ```

### Practitioner Addresses

- **List Practitioner Addresses**: `GET /addresses/`

  - Retrieves a list of practitioner addresses.

- **Retrieve a Practitioner Address**: `GET /addresses/{id}/`

  - Retrieves details of a specific practitioner address.

- **Update Wheelchair Accessibility**: `PATCH /addresses/{id}/`
  - Allows updating only the `wheelchair_accessibility` field.
  - Example request body:
    ```json
    {
      "wheelchair_accessibility": true
    }
    ```

### User Registration and Authentication

- **Register**: `/register/`
  - This will handle user registration.
- **Obtain JWT** : `/api/token/`
  - This will handle obtaining JWT tokens.
- **Refresh JWT** `/api/token/refresh/`
  - This will handle refreshing JWT tokens.

## Testing

### Unit-test

For now, it seems certains tests won't pass when launched by groups, but will pass when launch manually. It's more a test problem than a website problem. I can't fix it yet.

### The celery task

You should have notice we also had to configure celery. Its tasks will allow us to automatically check, every 30 days, the changes in the esante.gateway api about the practitioners.
The update of theses datas will also happen within 30 days if a practitionner has been consulted.

In order to trigger this task to know it's working, you can, after launching your redis server, try to launch

```
celery -A SafeTag worker --loglevel=info
celery -A SafeTag beat --loglevel=info
```

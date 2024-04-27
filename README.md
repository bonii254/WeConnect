# WECONNECT
[![Coverage Status](https://badge.coveralls.io/repos/github/bonii254/WeConnect/badge.svg?branch=master)](https://badge.coveralls.io/github/bonii254/WeConnect?branch=master)

WeConnect provides a platform that brings businesses and individuals together CreatING awareness for businesses and gives the users the ability to write reviews about the businesses they have interacted with.


## Features

- **User Authentication:**
  - Users can easily create an account with a username and password.
  - Registered users can securely log in to access the platform's features.

- **Business Registration:**
  - Authenticated users can conveniently register a business by providing essential details such as name, location, and category.

- **Business Management:**
  - Only the user who initially creates a business has the authority to update or delete it, ensuring data integrity and ownership.

- **View Businesses:**
  - Users have access to a comprehensive list of businesses registered on the platform, facilitating seamless exploration.

- **Review Businesses:**
  - Authenticated users can share their experiences by providing reviews for businesses they have interacted with, fostering transparency and community engagement.

- **Search Businesses:**
  - Users can effortlessly search for businesses based on location or category, empowering them to find relevant businesses efficiently.
  - The search functionality employs filters to refine results based on specified location or category criteria, enhancing user experience.
## Installation

To run this project locally, ensure you have the following prerequisites installed on your system:

- [Python](https://www.python.org/downloads/) (version 3.x)
- [pip](https://pip.pypa.io/en/stable/installation/) (Python package installer)
- [MySQL](https://dev.mysql.com/downloads/) or [PostgreSQL](https://www.postgresql.org/download/) database server
- [Redis](https://redis.io/download) server

Once you have Python and pip installed, follow these steps to set up the project:

1. **Clone the Repository:**
    ```sh
    git clone https://github.com/bonii254/WeConnect
    ```

2. **Navigate to the Project Directory:**
    ```sh
    cd WeConnect
    ```

3. **Set Up a Virtual Environment**
    - It's recommended to create a virtual environment to isolate project dependencies. Run the following command to create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate      # Windows
    ```

4. **Install Dependencies:**
    - Use pip to install the required Python packages specified in the `requirements.txt` file:
    ```sh
    pip install -r requirements.txt
    ```

5. **Set Up Environment Variables:**
    - Create a `.env` file in the project root and define the following environment variables:
      - `SECRET_KEY`: Sets the application's secret key.
      - `APP_SETTINGS`: Sets the environment to either `development`, `testing`, or `production`.
      - `DATABASE_URI`: Sets the application database URL. For MySQL or PostgreSQL databases, the URL format will be:
        - MySQL: `mysql://username:password@hostname/database_name`
        - PostgreSQL: `postgresql://username:password@hostname/database_name`
      - `CELERY_BROKER_URL`: Sets the URL for the Celery broker, which is Redis in this case. Example: `redis://localhost:6379/0`.
      - `CELERY_RESULT_BACKEND`: Sets the URL for the Celery result backend, which is also Redis. Example: `redis://localhost:6379/0`.
      - `FLASK_APP`: Exports flask app. Set it to `run.py`.


6. **Run the Application:**
    - Start the Flask server by running:
    ```sh
    flask -m run
    ```

7. **Access the Application:**
    - Once the server is running, you can access the application in your web browser at `http://localhost:5000`.
    
## Usage & Examples
**Access the API:**
    - Once the server is running, you can access the API endpoints using tools like cURL, Postman, or by making HTTP requests from your frontend application.
```bash
curl -X POST \
  http://localhost:5000/api/v2/auth/register \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "bonface",
    "password": "password123",
    "email": "test@gmail.com",
    "first_name": "bonface",
    "last_name": "murangiri"
  }'
```
8. **Test the Application:**
```bash
coverage run -m pytest tests
```








## API Endpoints

| Method | Endpoint                                     | Description                           |
|--------|----------------------------------------------|---------------------------------------|
| POST   | `/api/v2/auth/register`                      | Creates a user account                |
| POST   | `/api/v2/auth/login`                         | Logs in a user                        |
| POST   | `/api/v2/auth/logout`                        | Logout a user                         |
| PUT    | `/api/v2/auth/reset-password`                | Resets user password                  |
|        |                                              |                                       |
|        | **Businesses Endpoints:**                   |                                       |
| POST   | `/api/v2/businesses`                         | Register a new business               |
| GET    | `/api/v2/businesses`                         | List all registered businesses        |
| GET    | `/api/v2/businesses/user`                    | Gets all businesses for the current logged in user |
| PUT    | `/api/v2/businesses/<businessId>`            | Update business                       |
| DELETE | `/api/v2/businesses/<businessId>`            | Deletes a business                    |
|        |                                              |                                       |
|        | **Reviews Endpoints:**                      |                                       |
| POST   | `/api/v2/businesses/<businessId>/reviews`    | Create a new review                   |
| GET    | `/api/v2/businesses/<businessId>/reviews`    | Get reviews                           |
| PUT    | `/api/v2/businesses/<businessId>/reviews/<reviewId>` | Updates a review            |
| DELETE | `/api/v2/businesses/<businessId>/reviews/<reviewId>` | Deletes a review            |


## Authors

- [@Bonface Murangiri](https://www.github.com/bonii254)


## License
This project is released as unlicensed. You are free to use, modify, and distribute the code in any way you see fit. See the [UNLICENSE](UNLICENSE) file for more details.




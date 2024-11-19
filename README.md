
# Momo Card Settlement Project 🚀

Welcome to the **Momo Card Settlement Project**! This project provides a financial data API service designed for managing card transactions, processing large CSV files, and storing the data in a MySQL database with Redis caching. It also includes JWT authentication for secure access.

---

## Table of Contents 📚

1. [Features](#features-⚡)
2. [Technologies Used](#technologies-used-🛠️)
3. [Installation Guide](#installation-guide-📝)
4. [Running the Project](#running-the-project-🚀)
5. [API Endpoints](#api-endpoints-🧑‍💻)
6. [Usage Tutorial for Frontend](#usage-tutorial-for-frontend-🎨)
7. [How the Project Works](#how-the-project-works-🔍)
8. [Contributing](#contributing-🤝)
9. [License](#license-📜)

---

## Features ⚡

- **Fetch & Process CSV Data**: Periodically fetches card transaction data from a specified file and loads it into the database.
- **Transaction Management**: Stores card transaction data in a MySQL database with advanced query capabilities (filtering, sorting, pagination).
- **Caching**: Redis cache is used to speed up frequently requested data.
- **Asynchronous Data Operations**: Optimized for non-blocking database operations using SQLAlchemy's async API.
- **Secure Authentication**: JWT token-based authentication for users to interact with the API.

---

## Technologies Used 🛠️

- **Python 3.9+**
- **FastAPI**: Web framework for building APIs
- **SQLAlchemy**: ORM for interacting with MySQL
- **MySQL** (aiomysql driver): Database for storing transactions
- **Redis**: Caching frequently accessed data
- **Pandas**: Data manipulation and cleaning
- **JWT** (JSON Web Tokens): Authentication
- **Uvicorn**: ASGI server to run FastAPI
- **Asyncio**: Handling background tasks

---

## Installation Guide 📝

### Prerequisites

1. Python 3.9+ installed on your system.
2. MySQL running locally or remotely.
3. Redis running locally or remotely.

### Step-by-Step Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/momo-card-settlement.git
   cd momo-card-settlement
   ```

2. **Create a Virtual Environment (optional but recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**: Create a `.env` file in the root directory with the following configuration:
   ```env
   DATABASE_URL=mysql+aiomysql://root:password@127.0.0.1:3306/momo_card_settlement
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

5. **Run MySQL Database**: Ensure that your MySQL database is running, and create the `momo_card_settlement` database:
   ```sql
   CREATE DATABASE momo_card_settlement;
   ```

6. **Run Redis**: If you haven't installed Redis yet, you can [download it here](https://redis.io/download). Make sure Redis is running on `localhost:6379`.

---

## Running the Project 🚀

1. **Start the Application**:
   ```bash
   uvicorn main:app --reload
   ```

2. **Open the API Docs**: Once the server is running, visit the automatic Swagger UI at:
   [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

3. **Start the Periodic Background Task**: The background task will fetch and process the files every hour automatically.

---

## API Endpoints 🧑‍💻

1. **POST `/api/token`: Authentication**
   - Generates a JWT token using the username and password provided.
   - **Request**:
     ```json
     {
       "username": "your_username",
       "password": "your_password"
     }
     ```
   - **Response**:
     ```json
     {
       "access_token": "jwt_token_here",
       "token_type": "bearer"
     }
     ```

2. **GET `/api/transactions`: Fetch Transactions**
   - Fetches transaction data from the database with support for pagination, filtering, and sorting.
   - **Query Parameters**:
     - `skip` (int): The number of transactions to skip (default: 0).
     - `limit` (int): The number of transactions to return (default: 10).
     - `filter_by` (str): Filter by column name (optional).
     - `filter_value` (str): The value to filter by (optional).
     - `sort_by` (str): Column to sort by (optional).
     - `sort_order` (str): "asc" or "desc" (optional, default: "asc").
   - **Example**:
     ```bash
     GET /api/transactions?skip=0&limit=10&sort_by=AMOUNT&sort_order=desc
     ```
   - **Response**:
     ```json
     {
       "transactions": [
         {
           "DOC_IDT": "12345",
           "AMOUNT": 100.00,
           "TRANS_DATE": "2024-10-31"
         },
         ...
       ]
     }
     ```

3. **GET `/`: Welcome Message**
   - Displays a welcome message and a sample of the most recent transactions.

---

## Usage Tutorial for Frontend 🎨

1. **Get the Authentication Token**:
   Use a POST request to `/api/token` with your username and password.
   ```javascript
   const getToken = async () => {
     const response = await fetch('/api/token', {
       method: 'POST',
       body: new URLSearchParams({
         'username': 'your_username',
         'password': 'your_password',
       }),
     });
     const data = await response.json();
     return data.access_token;
   };
   ```

2. **Use the Token for API Requests**:
   Include the token in the `Authorization` header for authenticated API calls.
   ```javascript
   const fetchTransactions = async () => {
     const token = await getToken();
     const response = await fetch('/api/transactions?skip=0&limit=10', {
       headers: {
         'Authorization': `Bearer ${token}`,
       },
     });
     const data = await response.json();
     console.log(data.transactions);
   };
   ```

---

## How the Project Works 🔍

1. **Fetching Files**: The `fetch_files.py` script periodically fetches transaction data files (in CSV format) and stores them in a local directory.
2. **Parsing & Transforming**: The `parse_transform.py` script parses these CSV files using pandas, cleans the data, and ensures it is in a format suitable for storage in the database.
3. **Storing Data**: The cleaned data is then inserted into a MySQL database using SQLAlchemy's asynchronous API (`db_operations.py`).
4. **Caching**: Frequently accessed data is stored in Redis to improve API response times.
5. **Background Task**: The periodic task runs every hour, fetching new files and processing them automatically.

---

## Contributing 🤝

We welcome contributions! Follow these steps to contribute:

1. Fork the repository.
2. Clone your fork to your local machine.
3. Create a new branch:
   ```bash
   git checkout -b feature/your-feature
   ```
4. Make your changes.
5. Push to your branch:
   ```bash
   git push origin feature/your-feature
   ```
6. Create a Pull Request to the main repository.

---

## License 📜

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Happy coding! 💻

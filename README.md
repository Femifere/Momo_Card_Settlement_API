
# Momo Card Transaction & Settlement Project 🚀

Welcome to the **Momo Card Transaction & Settlement Project**! This project offers a robust financial data API service for managing card transactions, processing large datasets from CSV files, and storing the results in a scalable database system. Featuring a secure API, caching with Redis, and seamless deployment using Docker, this project is optimized for high performance and reliability.

---

## Table of Contents 📚

1. [Features](#features-⚡)
2. [Technologies Used](#technologies-used-🛠️)
3. [Installation Guide](#installation-guide-📝)
4. [Running the Project](#running-the-project-🚀)
5. [Environment Variables](#environment-variables-🔑)
6. [API Endpoints](#api-endpoints-🧑‍💻)
7. [How the Project Works](#how-the-project-works-🔍)
8. [Docker Setup](#docker-setup-🐋)
9. [Testing](#testing-✅)
10. [Usage Tutorial for Frontend](#usage-tutorial-for-frontend-🎨)
11. [Contributing](#contributing-🤝)
12. [License](#license-📜)

---

## Features ⚡

- **Fetch & Process Data**: Periodically fetches card transaction data from CSV files and processes them for database insertion.
- **Database Management**: Stores transaction data in MySQL with advanced query features (filtering, sorting, pagination).
- **Caching**: Frequently accessed data is cached in Redis for faster API responses.
- **Asynchronous Tasks**: Background tasks powered by asyncio for efficient data processing.
- **Secure API**: JWT-based token authentication for user access control.
- **Comprehensive API Documentation**: Interactive docs with Swagger and ReDoc for ease of integration.

---

## Technologies Used 🛠️

- **Python 3.10+**  
- **FastAPI**: High-performance web framework for APIs.  
- **SQLAlchemy**: ORM for managing MySQL interactions.  
- **MySQL**: Relational database for storing transactions.  
- **Redis**: In-memory caching for fast data retrieval.  
- **Pandas**: For data manipulation and transformation.  
- **JWT (JSON Web Tokens)**: Secure authentication.  
- **Uvicorn**: ASGI server for FastAPI.  
- **Docker**: Containerized deployment.

---

## Installation Guide 📝

### Prerequisites

1. **Python**: Ensure Python 3.10+ is installed.
2. **MySQL**: A running MySQL instance (local or cloud).
3. **Redis**: A running Redis instance (local or cloud).
4. **Docker & Docker Compose**: For containerized deployment (optional).

### Step-by-Step Setup

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:  
   Create a `.env` file with the following structure:
   ```plaintext
   DATABASE_URL=mysql+aiomysql://<user>:<password>@<host>:<port>/<database>
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

5. **Initialize MySQL Database**:  
   Log in to your MySQL server and create the database:
   ```sql
   CREATE DATABASE momo_card_transactions;
   ```

6. **Run the Application**:
   ```bash
   uvicorn main:app --reload
   ```

7. **Access API Documentation**:  
   Open the interactive API docs at:  
   - Swagger UI: `http://127.0.0.1:8000/docs`  
   - ReDoc: `http://127.0.0.1:8000/redoc`

---

## Environment Variables 🔑

Ensure the following variables are configured in your `.env` file:

```plaintext
DATABASE_URL=mysql+aiomysql://<USER>:<PASSWORD>@<HOST>:<PORT>/<DATABASE>
REDIS_HOST=localhost
REDIS_PORT=6379
LOG_LEVEL=info
```

---

## Running the Project 🚀

1. **Start MySQL and Redis**: Ensure both services are running.
2. **Run the Application**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

---

## API Endpoints 🧑‍💻

### **Authentication**
- **POST `/api/token`**: Generates a JWT token for authentication.

### **Transactions**
- **GET `/api/transactions`**: Fetch transaction data with optional filtering, sorting, and pagination.
- **POST `/api/transactions`**: Add new transaction data.

### **Home**
- **GET `/`**: Returns a welcome message and a sample of recent transactions.

Refer to `/docs` for detailed request/response structures.

---

## How the Project Works 🔍

1. **File Fetching**: CSV files are periodically fetched and stored locally.
2. **Data Processing**: Files are parsed and validated using pandas.
3. **Database Storage**: Validated data is saved into MySQL using SQLAlchemy's async API.
4. **Caching**: Frequently queried data is cached in Redis for faster response times.
5. **Background Task**: Periodic tasks ensure new files are processed automatically.

---

## Docker Setup 🐋

1. **Build and Start Containers**:
   ```bash
   docker-compose up --build
   ```

2. **Stop Containers**:
   ```bash
   docker-compose down
   ```

3. **Access API**:
   Visit `http://127.0.0.1:8000`.

---

## Testing ✅

1. **Install Testing Tools**:
   ```bash
   pip install pytest pytest-asyncio
   ```

2. **Run Tests**:
   ```bash
   pytest
   ```

3. **Test Coverage**:
   Ensure all modules are covered.

---

## Usage Tutorial for Frontend 🎨

1. **Authenticate**:
   Obtain a JWT token using the `/api/token` endpoint.

2. **Fetch Data**:
   Use the token to fetch transactions from the `/api/transactions` endpoint.

   Example using JavaScript Fetch API:
   ```javascript
   const fetchTransactions = async (token) => {
       const response = await fetch('/api/transactions', {
           headers: { Authorization: `Bearer ${token}` },
       });
       const data = await response.json();
       console.log(data.transactions);
   };
   ```

---

## Contributing 🤝

Contributions are welcome! Follow these steps:

1. Fork the repository.
2. Create a new feature branch:
   ```bash
   git checkout -b feature/new-feature
   ```
3. Commit changes and push:
   ```bash
   git push origin feature/new-feature
   ```
4. Open a pull request to the main branch.

---

## License 📜

This project is licensed under the MIT License.  
© 2024 MOMO PSB LTD.  

---

Happy coding! 💻

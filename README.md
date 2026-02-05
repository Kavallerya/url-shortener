# 🔗 Scalable URL Shortener

A microservices-based URL shortening application built with **Python (Flask)**, **Vue.js**, **Redis**, **RabbitMQ**, and **PostgreSQL**.

The project demonstrates a modern architecture designed for high performance and scalability using Docker containers.

## 🚀 Features

* **URL Shortening:** Generate unique short codes for long URLs.
* **High Performance Redirection:** Uses **Redis** caching to redirect users instantly without querying the primary database.
* **Asynchronous Analytics:** Uses **RabbitMQ** and a background **Worker** to log detailed click statistics (timestamp, user-agent) to PostgreSQL without blocking the user request.
* **Real-time Counter:** Immediate click counting stored in Redis.
* **Containerization:** Fully dockerized environment using `docker-compose`.

---

## 🛠 Tech Stack

| Component | Technology | Description |
|-----------|------------|-------------|
| **Frontend** | Vue.js + Nginx | Simple UI for creating links and viewing stats. |
| **Backend** | Python (Flask) | REST API for business logic. |
| **Database** | PostgreSQL | Persistent storage for links and detailed logs. |
| **Cache** | Redis | High-speed counter and caching layer. |
| **Message Broker** | RabbitMQ | Queues tasks for asynchronous processing. |
| **Worker** | Python | Consumes messages from RabbitMQ to write logs to DB. |

---

## 🏗 Architecture

The system uses an asynchronous pattern to handle high traffic:

1.  **User Click:** User accesses a short link.
2.  **Redis (Cache):** The backend immediately increments the click counter in Redis and redirects the user.
3.  **RabbitMQ (Queue):** Simultaneously, the backend sends a "click event" message to the queue.
4.  **Worker:** A separate background process picks up the message and saves detailed logs (time, IP, browser) to **PostgreSQL**.

This ensures that writing to the hard drive (Database) never slows down the user redirection.

---

## ⚙️ Installation & Running

### Prerequisites
* Docker & Docker Compose installed.

### Steps to Run

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/url-shortener.git](https://github.com/YOUR_USERNAME/url-shortener.git)
    cd url-shortener
    ```

2.  **Start the application:**
    ```bash
    docker-compose up --build
    ```

3.  **Access the application:**
    * **Web Interface:** [http://localhost:8080](http://localhost:8080)
    * **RabbitMQ Management:** [http://localhost:15672](http://localhost:15672) (Login: `guest` / `guest`)
    * **API:** [http://localhost:5000](http://localhost:5000)

---

## 🧪 How to Test

### 1. Shorten a Link
Open [http://localhost:8080](http://localhost:8080), paste a long URL (e.g., `https://google.com`), and click **Shorten**.

### 2. Generate Traffic
Open the generated short link. You will be redirected to the original site.

### 3. Verify Queues (RabbitMQ)
To see the asynchronous processing in action:
1.  Go to [http://localhost:15672](http://localhost:15672).
2.  Navigate to the **Queues** tab.
3.  Click your short link multiple times.
4.  Observe the **"Message rates"** graph spiking, indicating that messages are flowing through the system.

### 4. Check Logs
View the worker logs to see data being saved to the database:
```bash
docker-compose logs -f worker
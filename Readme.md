# Project Documentation: HealthAssist

## 1. Introduction

HealthAssist is an AI-powered medical consultation application designed to provide users with preliminary health insights based on their symptoms. It leverages a combination of natural language processing, medical knowledge bases (Infermedica), and large language models (OpenAI) to offer an interactive and informative experience.

### 1.1. Purpose

The purpose of HealthAssist is to:

*   Provide users with an initial understanding of their symptoms.
*   Offer potential causes and related information.
*   Guide users on the next steps, such as consulting a healthcare professional.

### 1.2. Target Audience

This documentation is intended for:

*   Developers contributing to the project.
*   System administrators deploying the application.
*   End-users seeking information about the application's functionality.

## 2. Setup and Installation

### 2.1. Prerequisites

Before setting up HealthAssist, ensure you have the following installed:

*   Python 3.10+
*   pip package manager
*   PostgreSQL database
*   Streamlit

### 2.2. Installation Steps

1.  **Clone the repository:**

    ```sh
    git clone <repository_url>
    cd my-app
    ```

2.  **Create a virtual environment:**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**

    *   Create a `.env` file in the root directory.
    *   Add the following variables, replacing the placeholders with your actual values:

        ```
        BACKEND_URL=http://127.0.0.1:5000
        DATABASE_URL=postgresql://super_user:jm32@localhost:5432/medical_assistant1
        JWT_SECRET=jwt_secret
        OPENAI_API_KEY=sk-...
        INFERMEDICA_APP_ID=ab2dfd58
        INFERMEDICA_APP_KEY=09d416c605ec80d5060c5379d683c6cd
        ```

5.  **Database setup:**

    *   Ensure PostgreSQL is running.
    *   Create a database named `medical_assistant1`.
    *   Run the database migrations:

        ```sh
        cd backend
        flask db init
        flask db migrate -m "Initial migration"
        flask db upgrade
        ```

### 2.3. Running the Application

1.  **Start the backend:**

    ```sh
    cd backend
    python app.py
    ```

2.  **Start the frontend:**

    ```sh
    cd frontend
    streamlit run app.py
    ```

## 3. Backend Documentation

The backend is built using Flask and provides the API endpoints for user authentication, chat management, and integration with Infermedica and OpenAI.

### 3.1. Core Components

*   **app.py:** Main Flask application, defines API routes, and handles authentication and authorization.
*   **models.py:** Defines the database models using Flask-SQLAlchemy (User, Chat, ChatMessage).
*   **database.py:** Initializes the database connection.
*   **db.py:** Contains database connection details.
*   **infermedica_client.py:** Handles communication with the Infermedica API for symptom analysis and diagnosis.
*   **openai_client.py:** Integrates with the OpenAI API for generating conversational responses.
*   **infermedica_conversation.py:** Manages the conversational flow using the Infermedica API.
*   **utils.py:** Provides utility functions for audio processing, image captioning, language detection, and translation.
*   **migrations/:** Contains Alembic migration scripts for managing database schema changes.

### 3.2. Key Endpoints

*   `/api/auth/register`: Registers a new user.
*   `/api/auth/login`: Authenticates a user and returns a JWT token.
*   `/api/chats`:
    *   `POST`: Creates a new chat.
    *   `GET`: Lists all chats for the authenticated user.
*   `/api/chats/<chat_id>`:
    *   `GET`: Retrieves a specific chat with its messages.
    *   `PATCH`: Updates the title of a specific chat.
*   `/api/chats/<chat_id>/message`: `POST`: Sends a new message to a specific chat.
*   `/api/health`: Returns the health status of the API.

### 3.3. Authentication

The backend uses JWT (JSON Web Tokens) for authentication.  The `JWTManager` extension handles the creation, verification, and management of tokens.

### 3.4. Database Migrations

Alembic is used for managing database migrations. The migration scripts are located in the `migrations/` directory.

## 4. Frontend Documentation

The frontend is built using Streamlit and provides the user interface for interacting with the HealthAssist application.

### 4.1. Core Components

*   **app.py:** Main Streamlit application, defines the overall layout, handles routing, and manages user authentication.
*   **pages/home_page.py:** Renders the home page with features, statistics, and testimonials.
*   **pages/chat_page.py:** Implements the chat interface for interacting with the AI assistant.
*   **pages/diagnosis_wizard.py:** Implements a step-by-step diagnosis wizard.
*   **pages/auth_page.py:** Handles user login and registration.
*   **components/navigation.py:** Renders the navigation bar.
*   **components/message_bubble.py:** Renders individual chat messages.
*   **components/file_upload.py:** Implements file uploading functionality.
*   **components/stat_card.py:** Renders statistic cards.

### 4.2. Key Features

*   **User Authentication:**  Users can register and log in to access the application's features.
*   **Chat Interface:**  Users can interact with the AI assistant through a conversational interface.
*   **Symptom Checker:**  The application analyzes user-provided symptoms to provide potential causes.
*   **Diagnosis Wizard:**  A guided process for collecting user information and providing a preliminary diagnosis.
*   **File Upload:** Users can upload images and documents to provide additional context.
*   **Voice Input:** Users can use their microphone to provide voice input.

### 4.3. State Management

Streamlit's session state is used to manage the application's state, including the current page, authentication token, user information, and chat history.

## 5. API Documentation

### 5.1. Authentication

All API endpoints (except for user registration and login) require a valid JWT token in the `Authorization` header.

### 5.2. Endpoints

| Method | Endpoint                      | Description                                                                                                |
|---|---|---|
| `POST` | `/api/auth/register` | Registers a new user. |
| `POST` | `/api/auth/login` | Authenticates a user and returns a JWT token. |
| `POST` | `/api/chats` | Creates a new chat. |
| `GET` | `/api/chats` | Lists all chats for the authenticated user. |
| `GET` | `/api/chats/<chat_id>` | Retrieves a specific chat with its messages. |
| `PATCH` | `/api/chats/<chat_id>` | Updates the title of a specific chat. |
| `POST` | `/api/chats/<chat_id>/message` | Sends a new message to a specific chat. |
| `GET` | `/api/health` | Returns the health status of the API. |

## 6. Potential Improvements

*   **Enhanced symptom analysis:** Implement more sophisticated algorithms for symptom analysis, potentially incorporating machine learning models.
*   **Improved conversational flow:** Refine the conversational flow to handle more complex user queries and provide more personalized responses.
*   **Integration with other medical APIs:** Integrate with additional medical APIs to provide more comprehensive information and services.
*   **User interface enhancements:** Improve the user interface with features such as customizable themes, user profiles, and chat history management.
*   **Mobile app development:** Develop native mobile apps for iOS and Android to provide a more seamless user experience.
*   **Enhanced security:** Implement additional security measures to protect user data and prevent unauthorized access.

## 7. Conclusion

HealthAssist is a promising AI-powered medical consultation application with the potential to provide valuable health insights to users. By following this documentation and contributing to the project's development, you can help make HealthAssist an even more powerful and user-friendly tool.

This documentation provides a high-level overview of the HealthAssist project. Further details can be found in the source code and related documentation files.
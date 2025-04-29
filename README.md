# TalkTrace: Building a WhatsApp-Integrated RAG Chatbot with Speech Recognition

## Introduction

In today's digital landscape, businesses are constantly seeking innovative ways to engage with their customers. Messaging platforms like WhatsApp have become essential communication channels, with over 2 billion users worldwide. Integrating artificial intelligence into these platforms can significantly enhance customer experience by providing instant, personalized responses.

In this comprehensive tutorial, we'll walk through building TalkTrace - a sophisticated WhatsApp-integrated chatbot that leverages Retrieval-Augmented Generation (RAG) and speech recognition capabilities. This powerful application allows businesses to:

- Automatically respond to customer inquiries via WhatsApp
- Process both text and voice messages
- Maintain conversation history for context
- Allow human agents to take over conversations when needed
- Monitor and manage all customer interactions through a clean admin interface

TalkTrace combines several cutting-edge technologies:

1. **WhatsApp Business API** for messaging
2. **FastAPI** for the backend server
3. **Streamlit** for the admin dashboard
4. **SQLite** for data persistence
5. **Dashscope** (Alibaba Cloud's AI service) for natural language processing
6. **Speech recognition** for audio message processing
7. **Docker** for containerization and deployment

By the end of this tutorial, you'll have a fully functional WhatsApp chatbot system that can handle customer inquiries, process voice messages, and allow seamless human takeover when necessary. Whether you're looking to enhance customer support, automate FAQ responses, or simply explore the integration of AI with messaging platforms, this project provides a solid foundation to build upon.

Let's dive in and explore how TalkTrace works, its architecture, and how you can deploy it for your own use case.

## Project Architecture Overview

TalkTrace is built with a modern, containerized architecture that separates concerns between the backend API server and the frontend admin interface. Let's explore the overall architecture before diving into each component in detail.

### High-Level Architecture

TalkTrace follows a client-server architecture with these main components:

1. **WhatsApp Business API Integration**: Connects to WhatsApp's messaging platform
2. **Backend Server**: Handles message processing, AI integration, and database operations
3. **Frontend Admin Dashboard**: Provides an interface for human agents to monitor and intervene
4. **Database**: Stores conversation history and contact information
5. **AI Services**: Processes natural language and speech recognition

The application is containerized using Docker, making it easy to deploy and scale. Let's examine each component in more detail.

### System Flow

Here's how the system processes messages:

1. A customer sends a message (text or voice) via WhatsApp
2. WhatsApp forwards this message to our backend webhook
3. The backend processes the message:
   - For text messages: Directly passes to the AI service
   - For voice messages: Transcribes audio to text first
4. The AI service (Dashscope) generates a response
5. The response is sent back to the customer via WhatsApp
6. All interactions are stored in the database
7. Human agents can view conversations and take over when needed

This architecture allows for seamless handling of customer inquiries with the option for human intervention when the AI cannot adequately address complex issues.

### Directory Structure

The project is organized into two main directories:

```
TalkTrace/
├── backend/           # FastAPI server
│   ├── app.py         # Main application entry point
│   ├── database/      # Database models and operations
│   ├── services/      # AI and speech recognition services
│   ├── utils/         # Utility functions for WhatsApp
│   └── decorators/    # Security and configuration
├── frontend/          # Streamlit admin dashboard
│   ├── app.py         # Dashboard application
│   └── utils/         # API communication utilities
└── docker-compose.yml # Container orchestration
```

This separation of concerns makes the codebase maintainable and allows for independent scaling of the frontend and backend components as needed.

## Backend Implementation

The backend of TalkTrace is built with FastAPI, a modern, high-performance web framework for building APIs with Python. Let's explore the key components of the backend implementation.

### Core Components

#### 1. FastAPI Application (app.py)

The main application file (`app.py`) sets up the FastAPI server and defines the API endpoints. Here are the key endpoints:

- **GET /webhook**: Verifies the WhatsApp webhook during initial setup
- **POST /webhook**: Handles incoming WhatsApp messages and events
- **POST /history**: Retrieves conversation history for a specific user
- **POST /sending**: Allows human agents to send messages to users
- **POST /toggle-human-chat**: Toggles between AI and human chat modes
- **GET /contacts**: Retrieves a list of all contacts

The application uses CORS middleware to allow cross-origin requests from the frontend, making it possible for the admin dashboard to communicate with the backend.

#### 2. Database Models

TalkTrace uses SQLAlchemy ORM with SQLite for data persistence. The database has two main tables:

- **CHAT_HISTO**: Stores message history with fields for sender, receiver, message content, and timestamp
- **CONTACT**: Stores contact information with fields for phone number, AI active status, and account status

The database models are defined in `database/sqlite/pros_model.py`, while the database connection is configured in `database/sqlite/database.py`.

#### 3. CRUD Operations

The CRUD (Create, Read, Update, Delete) operations for the database are implemented in `database/sqlite/crud.py`. There are two main CRUD classes:

- **ContactCRUD**: Handles operations related to contacts, such as adding, updating, and retrieving contacts
- **ChatHistoCRUD**: Handles operations related to chat history, such as adding messages and retrieving conversations

These classes provide a clean interface for interacting with the database, abstracting away the SQL queries.

#### 4. WhatsApp Integration

The WhatsApp integration is handled by the `utils/whatsapp_utils.py` module. This module provides functions for:

- Validating incoming WhatsApp messages
- Processing text and audio messages
- Downloading and handling audio files
- Sending responses back to WhatsApp

The integration uses the WhatsApp Business API to send and receive messages. Authentication is handled through environment variables that store the necessary API keys and tokens.

#### 5. AI Integration

The AI integration is implemented in `services/dashscope_service.py`. This module uses the Dashscope API (via OpenAI-compatible interface) to generate responses to user messages. The key features include:

- Maintaining conversation history for context
- Generating responses based on user messages
- Storing chat history in a persistent storage

#### 6. Speech Recognition

The speech recognition functionality is implemented in `services/speech_recognition.py`. This module provides functions for:

- Converting audio files from OGG to WAV format
- Transcribing audio using Google Speech Recognition
- Handling different languages (including Arabic)

This allows the chatbot to process voice messages sent by users, expanding its accessibility.

#### 7. Security

Security is implemented through the `decorators/security.py` module, which provides a decorator for verifying the signature of incoming WhatsApp webhook requests. This ensures that only legitimate requests from WhatsApp are processed.

### Environment Configuration

The backend uses environment variables for configuration, which are loaded from a `.env` file. These variables include:

- WhatsApp API credentials
- Dashscope API key
- Phone number IDs
- Verification tokens

This approach keeps sensitive information out of the codebase and allows for easy configuration changes without modifying the code.

## Frontend Implementation

The frontend of TalkTrace is built with Streamlit, a powerful Python library for creating web applications with minimal code. The admin dashboard provides a clean interface for human agents to monitor conversations and intervene when necessary.

### Core Components

#### 1. Streamlit Application (app.py)

The main application file (`app.py`) sets up the Streamlit dashboard with the following features:

- Auto-refresh functionality to keep conversations up-to-date
- Contact selection dropdown to choose which customer to view
- Human chat toggle to switch between AI and human modes
- Conversation display showing the full message history
- Message input box for human agents to send messages

The application uses Streamlit's chat interface components to create a familiar messaging experience for agents.

#### 2. API Communication

The frontend communicates with the backend through a set of utility functions defined in `utils/headers.py`. These functions include:

- **fetch_contacts()**: Retrieves a list of all contacts
- **fetch_conversation(wa_id)**: Retrieves the conversation history for a specific contact
- **toggle_human_chat(wa_id, activate)**: Toggles between AI and human chat modes
- **send_user_message(wa_id, message)**: Sends a message to a user

These functions make HTTP requests to the backend API endpoints, handling any errors that might occur during communication.

#### 3. Auto-Refresh Functionality

One key feature of the dashboard is the auto-refresh functionality, which periodically reruns the Streamlit script to update the conversation display. This ensures that agents always see the latest messages without having to manually refresh the page.

```python
st_autorefresh(interval=POLLING_INTERVAL, key="chat_refresh")
```

The polling interval is set to 5000 milliseconds (5 seconds), providing a good balance between responsiveness and server load.

#### 4. Human Chat Mode

When an agent activates human chat mode for a specific contact, the AI is disabled for that conversation, and all messages from the user are routed to the dashboard. The agent can then respond directly to the user through the message input box.

```python
human_access = st.sidebar.checkbox("Activate Human Chat", False)
toggle_human_chat(wa_id, human_access)
```

This feature is essential for handling complex inquiries that the AI might not be able to address adequately.

### User Interface Design

The Streamlit dashboard is designed to be intuitive and easy to use. The layout includes:

- A sidebar for contact selection and human chat toggle
- A main area for displaying the conversation
- A message input box at the bottom for sending messages

The conversation display uses Streamlit's chat message components, which visually distinguish between user and assistant messages, making it easy to follow the conversation flow.

The dashboard is responsive and works well on both desktop and mobile devices, allowing agents to monitor conversations from anywhere.

## Setup and Installation

Setting up TalkTrace involves several steps, from configuring the WhatsApp Business API to deploying the application with Docker. This section will guide you through the entire process.

### Prerequisites

Before you begin, make sure you have the following:

1. **Docker and Docker Compose**: For containerizing and running the application
2. **WhatsApp Business API access**: You'll need to register with Meta for WhatsApp Business API access
3. **Dashscope API key**: For the AI language model integration
4. **A server with a public IP address**: For receiving webhook events from WhatsApp

### Environment Configuration

First, you'll need to set up the environment variables for the backend. Create a `.env` file in the `backend` directory with the following variables:

```
# WhatsApp API credentials
VERIFY_TOKEN=your_verification_token
APP_SECRET=your_app_secret
ACCESS_TOKEN=your_access_token
VERSION=v17.0
PHONE_NUMBER_ID=your_phone_number_id
RECIPIENT_WAID=your_recipient_waid

# Dashscope API key
DASHSCOPE_API_KEY=your_dashscope_api_key
```

Replace the placeholder values with your actual credentials:

- `VERIFY_TOKEN`: A custom token you create for webhook verification
- `APP_SECRET`: Your WhatsApp Business API app secret
- `ACCESS_TOKEN`: Your WhatsApp Business API access token
- `PHONE_NUMBER_ID`: Your WhatsApp Business phone number ID
- `RECIPIENT_WAID`: Default recipient WhatsApp ID (optional)
- `DASHSCOPE_API_KEY`: Your Dashscope API key

### WhatsApp Business API Setup

To set up the WhatsApp Business API:

1. Create a Meta Developer account at [developers.facebook.com](https://developers.facebook.com/)
2. Create a new app and select "Business" as the app type
3. Add the "WhatsApp" product to your app
4. Set up a business account and connect your phone number
5. Configure the webhook URL to point to your server's `/webhook` endpoint
6. Use the `VERIFY_TOKEN` you defined in your `.env` file for webhook verification

### Docker Deployment

TalkTrace uses Docker Compose for easy deployment. The `docker-compose.yml` file defines two services:

1. **backend**: The FastAPI server that handles WhatsApp messages and AI integration
2. **frontend**: The Streamlit dashboard for human agents

To deploy the application:

1. Clone the TalkTrace repository to your server
2. Navigate to the project directory
3. Run the following command:

```bash
docker-compose up -d
```

This will build and start the containers in detached mode. The backend will be available on port 8080, and the frontend will be available on port 9090.

### Webhook Configuration

For WhatsApp to send messages to your application, you need to configure the webhook URL in the Meta Developer Portal. The URL should be:

```
https://your-server-domain/webhook
```

Make sure your server has HTTPS enabled, as WhatsApp requires secure connections for webhooks.

### Database Setup

The SQLite database will be automatically created when the application starts. The database file is stored in the `backend/data/db/sqlite` directory, which is mounted as a volume in the Docker container.

### Verifying the Setup

To verify that everything is working correctly:

1. Access the frontend dashboard at `http://your-server-ip:9090`
2. Check if you can see the contacts list (it may be empty if no one has messaged you yet)
3. Send a test message to your WhatsApp Business number
4. Verify that the message appears in the dashboard

If everything is working correctly, you should see the message in the dashboard, and the AI should automatically respond to it.

## Using TalkTrace

Now that you have TalkTrace up and running, let's explore how to use it effectively for managing customer conversations. This section will cover both the customer experience and the agent dashboard functionality.

### Customer Experience

From the customer's perspective, interacting with TalkTrace is as simple as sending a message to your WhatsApp Business number. Here's what customers can do:

1. **Send text messages**: Customers can send regular text messages to ask questions or request assistance.
2. **Send voice messages**: Customers can send voice recordings, which will be automatically transcribed and processed.
3. **Receive AI responses**: The AI will automatically respond to customer inquiries based on the conversation context.
4. **Interact with human agents**: When a human agent takes over, customers continue the conversation as normal, but now they're talking to a real person.

The transition between AI and human agent is seamless from the customer's perspective, ensuring a smooth experience throughout the conversation.

### Agent Dashboard

The agent dashboard is where human agents monitor and manage conversations. Here's how to use it effectively:

#### Viewing Conversations

1. Access the dashboard at `http://your-server-ip:9090`
2. Use the dropdown menu in the sidebar to select a contact
3. View the full conversation history for that contact

The conversation display shows all messages exchanged between the customer and the system, including both AI-generated responses and messages sent by human agents.

#### Taking Over a Conversation

When a customer inquiry requires human intervention:

1. Select the customer from the dropdown menu
2. Check the "Activate Human Chat" box in the sidebar
3. The AI will be disabled for this conversation, and all messages will be routed to the dashboard
4. Use the message input box at the bottom of the screen to respond to the customer

When human chat mode is activated, the AI will not respond to the customer's messages, allowing the human agent to take full control of the conversation.

#### Returning to AI Mode

Once the complex inquiry has been resolved:

1. Uncheck the "Activate Human Chat" box in the sidebar
2. The AI will be reactivated for this conversation
3. The AI will resume responding to the customer's messages

This allows agents to handle multiple conversations efficiently, focusing on complex inquiries while letting the AI handle routine questions.

#### Monitoring Multiple Conversations

The dashboard automatically refreshes every 5 seconds, allowing agents to monitor multiple conversations by switching between contacts. This ensures that agents can keep track of all ongoing conversations without missing any messages.

### Best Practices

To get the most out of TalkTrace, consider these best practices:

1. **Train your AI model**: The more data you provide to your AI model, the better it will understand your business and customer inquiries.
2. **Set clear handoff criteria**: Establish guidelines for when human agents should take over conversations.
3. **Monitor AI responses**: Regularly review AI-generated responses to ensure they meet your quality standards.
4. **Collect feedback**: Ask customers for feedback on their experience to identify areas for improvement.
5. **Backup your database**: Regularly backup your SQLite database to prevent data loss.

### Handling Special Cases

#### Handling Unsupported Message Types

TalkTrace currently supports text and voice messages. If a customer sends other types of messages (like images or documents), the system will ignore them. Consider adding custom handling for these message types based on your business needs.

#### Handling Multiple Languages

The speech recognition service supports multiple languages, including English and Arabic. To add support for additional languages, you would need to modify the `transcribe_audio` function in `speech_recognition.py`.

#### Scaling for High Volume

If you're handling a high volume of conversations, you might need to scale the application. Consider:

1. Moving from SQLite to a more robust database like PostgreSQL
2. Implementing a message queue for processing incoming messages
3. Deploying multiple instances of the backend service behind a load balancer

## Extending and Customizing TalkTrace

One of the strengths of TalkTrace is its flexibility and extensibility. In this section, we'll explore how you can extend and customize the application to meet your specific business needs.

### Adding New Features

#### Implementing Message Templates

WhatsApp Business API supports message templates for sending structured messages. To implement this feature:

1. Create message templates in the Meta Business Manager
2. Add a new function in `whatsapp_utils.py` to send template messages
3. Extend the frontend to allow agents to select and send templates

#### Adding Media Support

To support media messages (images, documents, etc.):

1. Extend the webhook handler in `app.py` to process different message types
2. Add functions in `whatsapp_utils.py` to download and process media files
3. Update the frontend to display media messages

#### Implementing Analytics

To gain insights into your conversations:

1. Add analytics tracking to the database models
2. Create a new endpoint in the backend for retrieving analytics data
3. Add an analytics dashboard to the frontend

### Integrating with Other Systems

#### CRM Integration

To connect TalkTrace with your CRM system:

1. Add API client code for your CRM in a new service module
2. Extend the contact model to include CRM identifiers
3. Implement synchronization between TalkTrace and your CRM

#### Knowledge Base Integration

To enhance the AI with your knowledge base:

1. Implement a document retrieval system using vector databases
2. Extend the AI service to include retrieved information in prompts
3. Add a management interface for the knowledge base

### Performance Optimization

#### Database Optimization

If you're handling a large volume of conversations:

1. Implement database indexing for frequently queried fields
2. Add pagination to conversation retrieval
3. Consider migrating to a more scalable database system

#### AI Response Optimization

To improve AI response quality and speed:

1. Implement prompt engineering techniques
2. Add caching for common queries
3. Consider using a more powerful AI model for complex inquiries

### Security Enhancements

#### Implementing User Authentication

To secure the admin dashboard:

1. Add user authentication to the frontend
2. Implement role-based access control
3. Add audit logging for agent actions

#### Enhancing Data Protection

To protect sensitive customer data:

1. Implement data encryption for the database
2. Add data retention policies
3. Implement compliance features for regulations like GDPR

## Conclusion

TalkTrace provides a solid foundation for building a WhatsApp-integrated chatbot with AI capabilities. By extending and customizing the application, you can create a solution that perfectly fits your business needs.

Remember that the key to a successful chatbot implementation is continuous improvement. Monitor your system's performance, collect feedback from customers and agents, and iterate on your implementation to provide the best possible experience.

With the knowledge gained from this tutorial, you're well-equipped to build and deploy your own WhatsApp chatbot solution. Happy building!

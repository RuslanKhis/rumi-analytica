# rumi-analytica
![Logo](/images/rumi-analytica-logo.png)
Multi-agent analytics platform powered by Gemini and deployed on Cloud Run.

## Core Problem

The modern digital analytics landscape presents a series of disconnected, highly specialized challenges that prevent organizations from moving quickly from data to decision. While raw data is more accessible than ever (e.g., GA4 exports to BigQuery), the path to actionable insight is fragmented by significant skill gaps:

*   **The SQL Barrier:** The people who need data most—marketers, product managers, and digital analysts—often lack the specialized SQL skills required to query complex, nested schemas like GA4's BigQuery export. This creates a dependency on data teams, leading to bottlenecks and delays.
*   **The Data Science Gap:** Extracting data is only the first step. Performing exploratory analysis, generating visualizations, or running statistical models requires proficiency in languages like Python and its data science libraries. This skill set is typically distinct from that of a traditional analyst.
*   **The Experimentation Hurdle:** An insight or correlation found in the data is not a validated conclusion. Designing and interpreting statistically sound experiments (like A/B tests) requires knowledge of econometrics and causal inference, a discipline that is often siloed within specialized research or data science teams.
*   **The Implementation Chasm:** For developers and architects, tutorials and examples for building sophisticated, agent-based systems are often fragmented. There is a lack of comprehensive, end-to-end blueprints that demonstrate how to integrate a multi-agent framework with a backend, connect it to a frontend, and deploy the entire system robustly on a cloud platform like GCP with a full CI/CD pipeline.

These gaps force a slow, linear, and handed-off process where a single business question requires coordination across multiple teams, stifling curiosity and agility.

## Solution

Rumi-Analytica is a self-deploying, multi-agent analytics platform that provides a unified solution to these fragmented challenges. It deploys a secure, conversational application on Google Cloud that empowers a single user to navigate the entire analytics workflow—from data retrieval to experimental design—through one intuitive chat interface.

The solution is built on a hierarchical agent architecture where a central orchestrator, "Rumi," intelligently routes tasks to a team of specialized agents:

1.  **Unified Natural Language Interface:** A user asks a question in plain English, such as *"What were our top 10 landing pages last month?"* or *"Can you run a regression on this user data?"*
2.  **Intelligent Orchestration & Delegation:** The root agent (Rumi) analyzes the user's intent and delegates the task to the appropriate expert sub-agent:
    *   **GA4 & BigQuery Agents (Astra & Hiroshi):** For questions about analytics data, these agents convert the request into precise, reliable SQL, execute it against your BigQuery database, and return the exact data.
    *   **Data Science Agent (Ginger):** If the user wants to analyze or visualize the retrieved data, the task is passed to this agent, which writes and executes Python code to perform the analysis, generating tables or plots.
    *   **Econometrics Agent (Persephone):** To validate an insight, the user can ask this agent to design an experiment. It provides a guided, step-by-step process for hypothesis formulation, power analysis, and statistical testing.
3.  **Synthesized, Actionable Output:** The results from each agent—whether raw data, a Python-generated chart, or a detailed experimental plan—are synthesized and delivered back to the user in a single, coherent conversation.

By integrating these distinct specializations into a single, conversational tool, Rumi-Analytica empowers business users and analysts to self-serve their most complex data needs with confidence. It collapses the time from question to validated insight from weeks to minutes, eliminating organizational bottlenecks. Furthermore, the repository itself serves as a production-grade, end-to-end reference architecture for building and deploying complex agentic solutions on Google Cloud.

## Tech Stack

This solution is built with a modern, scalable stack, leveraging Google Cloud's managed services and popular open-source frameworks for a robust, end-to-end deployment.

### Backend

*   **Python:** The core programming language for the application logic.
*   **FastAPI:** A high-performance web framework used to build the secure, RESTful API backend.
*   **Google Agent Development Kit (ADK):** The foundational framework for creating the hierarchical, multi-agent system, managing agent state, and orchestrating tool use.
*   **Gemini (via Vertex AI):** The intelligent engine powering the agents. It is used for natural language understanding, routing, code generation, and synthesizing responses.
*   **Vertex AI Tools:** The backend leverages a suite of Vertex AI tools, including **Vertex AI Search** for document retrieval and the **Vertex AI Code Executor** for running Python data science and econometrics code.

### Frontend

*   **React 18 & TypeScript:** The foundation for building a modern, type-safe, and interactive user interface.
*   **Vite:** A next-generation frontend tooling that provides an extremely fast development server and optimized build process.
*   **Tailwind CSS & shadcn/ui:** A utility-first CSS framework combined with a set of beautifully designed, accessible, and customizable components for a polished user experience.
*   **TanStack Query:** Manages server state, handling data fetching, caching, and synchronization with the backend API.

### Cloud & DevOps

*   **Google Cloud Platform (GCP):** The entire application is designed to run on GCP.
*   **Google Cloud Run:** Provides the serverless, scalable, and fully managed hosting environment for both the frontend and backend containerized services.
*   **Google BigQuery:** The data warehouse that stores analytics data and serves as the primary query engine for the database agents.
*   **Google Cloud Build:** The service that executes the automated CI/CD pipeline defined in `cloudbuild.yaml`.
*   **Google Artifact Registry:** A secure, private repository for storing and managing the Docker images for both services.
*   **Google Secret Manager:** Securely stores and manages sensitive information like API keys, database credentials, and JWT secrets.
*   **Docker:** Used to package the frontend and backend applications and their dependencies into portable container images, ensuring consistent execution across all environments.

## Contributors
**Main Contributor & Project Creator:**  
[Russ Khissami](https://www.linkedin.com/in/russ-k-b6a48a1a6/) - *Analytics Engineer*

Feel free to connect if you have questions about the implementation or want to discuss AI solutions!

## Architecture

The application's architecture is designed for modularity, security, and scalability. It is composed of two primary workflows: the real-time **User Interaction Flow**, which handles the conversational experience, and the automated **CI/CD Deployment Flow**, which manages code deployment.

### User Interaction Flow

![User Interaction Flow Diagram](/images/architecture_rumi-analytics.png)

The user interaction process is orchestrated to translate natural language into complex, multi-step analytical tasks.

1.  **Authentication:** The user navigates to the frontend URL and logs in via the `/login` page. The React frontend sends the credentials to the FastAPI backend's `/token` endpoint. Upon successful validation, the backend issues a JWT, which is stored in the browser and sent with all subsequent API requests.
2.  **Application Interface:** The authenticated user interacts with the **React** single-page application, which is served from a container on **Cloud Run**. The user submits a message through the chat interface.
3.  **Backend Request:** The frontend sends the user's message in a POST request to the `/api/chat` endpoint on the **FastAPI** backend, which is also running as a separate service on **Cloud Run**.
4.  **Agent Orchestration:**
    *   The FastAPI backend receives the request and invokes the **Root Agent (Rumi)** using the Google Agent Development Kit (ADK).
    *   Rumi, powered by **Gemini**, analyzes the user's intent and uses its configured tools to delegate the task to the appropriate specialized sub-agent.
5.  **Sub-Agent Execution:**
    *   The selected sub-agent executes its specific logic. For example:
        *   The **GA4 Agent** might match the request to a predefined SQL template, populate it with parameters, and execute a query against **BigQuery**.
        *   The **Data Science Agent** might receive data from a previous step and use the **Vertex AI Code Executor** to run Python code, generating a plot which it saves as an image file (`generated_plot.png`) in its runtime environment.
        *   The **Web Search Agent** might use the Google Search API to find information on current events.
6.  **Response Synthesis & Delivery:**
    *   The sub-agent returns its result (e.g., JSON data, a success message, or an error) to the Root Agent.
    *   The FastAPI backend intercepts the final response. If it detects that an image artifact was created, it reads the image file, encodes it into Base64, and packages it into a JSON payload along with the text response.
    *   The backend sends this JSON object back to the React frontend.
    *   The frontend dynamically renders the response, displaying the text as markdown and rendering the Base64 string as an image if it is present.

### CI/CD Deployment Flow

![CI/CD Flow Diagram](/images/ci-cd_pipeline_rumi-analytica.png)

The deployment process is fully automated using a GitOps workflow managed by Google Cloud.

1.  **Code Push:** A developer commits and pushes code changes to the `main` branch of the GitHub repository.
2.  **Trigger Invocation:** The push automatically triggers the **Cloud Build** pipeline linked to the repository.
3.  **Pipeline Execution:** Cloud Build executes the steps defined in the `cloudbuild.yaml` file:
    *   **Build & Deploy Backend:** It builds the `backend/` Docker image, pushes it to **Artifact Registry**, and deploys the new version to the `rumi-analytica-backend` **Cloud Run** service, injecting all necessary environment variables and secrets from **Secret Manager**.
    *   **Build & Deploy Frontend:** It then builds the `frontend/` Docker image (injecting the backend's URL as a build argument), pushes it to **Artifact Registry**, and deploys the new version to the `rumi-analytica-frontend` **Cloud Run** service.
4.  **Service Update:** Once the pipeline completes successfully, the new versions of the frontend and backend services are live and begin serving traffic automatically.

***

## Key Architectural Decisions

The design of Rumi-Analytica is guided by several key architectural decisions that enable its power and serve as a reference for building production-grade agentic systems.

### 1. Integrating ADK with a Custom FastAPI Backend

A primary goal of this project is to demonstrate how to move beyond standalone agent scripts. While the Google Agent Development Kit (ADK) provides powerful tools for building agents, most tutorials demonstrate its use via the built-in `adk run` command, which launches a simple, self-contained UI. This leaves a significant gap for developers aiming to integrate agentic logic into a production-grade, custom API backend.

This application deliberately treats the ADK as a library within a standard FastAPI application. The key to this integration is the `google.adk.runtime.Runner` class. The architecture follows a clean separation of concerns, as illustrated in the `main.py` file.

**1. API Layer (FastAPI):** First, we define a standard FastAPI endpoint. It handles HTTP-specific concerns like routing, request validation (using Pydantic models), and security (using JWT-based dependency injection).

```python
# main.py

@app.post("/api/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    # Agent logic will be invoked here
    ...
```

**2. Programmatic Invocation:** Inside the endpoint, instead of serving a UI, we instantiate the `Runner` and programmatically execute the agent with the user's message. The user's identity is used to maintain a distinct conversational session.

```python
# main.py (inside the /api/chat endpoint)

    # Instantiate the Runner for the root agent
    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        session_id=current_user.username,  # Use username for session state
    )

    # Programmatically execute the agent workflow
    final_response = await runner.run(request.message)
```

**3. Post-Processing and Response Formatting:** The FastAPI endpoint receives the final result from the runner. This allows for powerful post-processing logic before sending a standard JSON response to the client. Here, we check if a sub-agent (like the Data Science agent) created an image artifact, encode it, and include it in the response.

```python
# mainpy (continued inside the /api/chat endpoint)

    response_text = final_response.output
    image_data = None
    image_mime_type = None

    # Check if an image artifact was created
    if os.path.exists("generated_plot.png"):
        with open("generated_plot.png", "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        image_mime_type = "image/png"
        os.remove("generated_plot.png") # Clean up the file

    # Return a standard JSON response to the client
    return {
        "response": response_text,
        "image_data": image_data,
        "image_mime_type": image_mime_type,
    }
```

This pattern provides several critical advantages:

*   **Decoupling and Control:** It cleanly separates the web framework (FastAPI) from the agent framework (ADK). The API layer handles all web-related concerns, while the ADK focuses purely on the conversational logic.
*   **Production-Ready Architecture:** It allows the agent system to be deployed as part of a robust, scalable backend with proper authentication, error handling, and logging.
*   **Frontend Agnostic:** By exposing the agent via a standard REST API, the system is not tied to any specific UI. It can be consumed by our React app, a mobile application, or any other client.
*   **Extensibility:** The FastAPI layer acts as a powerful intermediary. It can enrich requests before they reach the agent or, as demonstrated with image handling, process the agent's output before it's sent to the user.

TODO:
+ need to provide discovery Engine Viewer to service account & enable  Cloud Resource Manager API  on the project

## Deployment Guide

Follow these steps to deploy the application to your own Google Cloud project.

### Prerequisites

Before you begin, ensure you have the following:

1.  **GitHub Account**: To fork this repository.
2.  **Google Cloud Project**:
    *   A GCP project with **Billing enabled**.
    *   Your user account must have the `Owner` or `Editor` IAM role.

### Step 1: Fork and Clone the Repository

1. **Fork** this repository to your own GitHub account by clicking the "Fork" button at the top right of the page.


### Step 2: Connect GitHub to Google Cloud Build

This one-time setup authorizes your Google Cloud project to access your GitHub repository, which is required for the automated CI/CD pipeline.

**IMPORTANT:** Before accessing a link below, you might be redirected to enable the Cloud Build API. It is fine to enable that API, and then click on the link again.

1.  Navigate to the **[Cloud Build Repositories page](https://console.cloud.google.com/cloud-build/repositories)** in the GCP Console.
2.  Make sure you are in the correct GCP project, then click **Connect repository**.
3.  Select **GitHub (Cloud Build GitHub App)** as the source and click **Continue**.
4.  Authenticate with your GitHub account. You will be redirected to GitHub to **Authorize Google Cloud Build**.
5.  On the next screen, you may be prompted to **Install Google Cloud Build** if it's not already configured for your account. Click the install button and choose which repositories to grant access to (you can select just your forked repo).
6.  You will be redirected back to the GCP console. Select your **GitHub Account** and the forked **Repository** from the dropdown menus.
7.  Check the box to agree to the terms and click **Connect**.

### Step 3: Run the Automated Setup from Cloud Shell

This is the main setup step. You will use the Google Cloud Shell to clone your repository and run a script that provisions all the necessary cloud infrastructure and sets up the CI/CD pipeline.

1. **Activate Cloud Shell**
   In the Google Cloud Console, click the **Activate Cloud Shell** icon (`>_`) in the top-right corner. This will open a terminal pre-authenticated to your GCP account. You can also press **G** + **S**.

2. **Clone Your Repository into Cloud Shell**
   Run the following command in the Cloud Shell terminal:

   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   ```

3. **Navigate into the Project Directory**

   ```bash
   # Replace YOUR_REPO_NAME with the actual repository name
   cd YOUR_REPO_NAME
   ```

4. **Execute the Setup Script**
   The `setup.sh` script will now configure your GCP project.

   ```bash
   # First, make the script executable
   chmod +x setup.sh
   
   # Now, run the script
   ./setup.sh
   ```

5. **Follow the Prompts**
   The script will ask for the following information to configure your resources:

    > **Important:** Please make sure that you have the values below entered exactly as they appear, without any spaces, as this might cause the script to fail. Furthermore, I recommend creating a .txt file with these values to input as required.

The script will take several minutes to complete as it enables APIs, creates service accounts, builds the application, deploys it to Cloud Run, and configures the Cloud Build trigger.

Once the script completes successfully, your CI/CD pipeline is live. **You can now close Cloud Shell.** All future development can be done from your local machine; simply push code changes to your GitHub repository's `main` branch, and Cloud Build will automatically deploy them.


## Detailed Explanation of Components

## Frontend Documentation

#### Technology Stack

The frontend is built with modern web technologies:
- **React 18** - UI framework
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first styling with custom design system
- **shadcn/ui** - High-quality, customizable React components
- **React Router** - Client-side routing
- **TanStack Query** - Server state management

#### Project Structure

```
src/
├── assets/              # Static images (avatars, logos)
├── components/          # React components
│   ├── ui/             # shadcn/ui base components
│   ├── ChatInput.tsx   # Message input with typing indicator
│   ├── ChatMessage.tsx # Individual message display with markdown
│   ├── Header.tsx      # App header with user info and logout
│   └── WelcomeScreen.tsx # Initial chat screen
├── contexts/
│   └── AuthContext.tsx # Authentication state management
├── hooks/              # Custom React hooks
├── lib/
│   ├── api.ts         # Backend API communication
│   └── utils.ts       # Utility functions
├── pages/
│   ├── Index.tsx      # Main chat interface
│   ├── Login.tsx      # Authentication page
│   └── NotFound.tsx   # 404 error page
├── App.tsx            # Root component with routing
├── index.css          # Design system and global styles
└── main.tsx           # Application entry point
```

### Architecture

#### Design System
The application uses a comprehensive design system defined in `index.css` with:
- **Semantic color tokens** for consistent theming (light/dark mode support)
- **HSL color values** for all colors
- **Custom gradients and shadows** for visual depth
- **Smooth transitions** for interactive elements

All components use these semantic tokens rather than hardcoded colors, ensuring consistent styling across the application.

#### Component Architecture
- **Presentation components** in `src/components/` handle UI rendering
- **Page components** in `src/pages/` manage route-level logic
- **Context providers** manage global state (authentication)
- **Custom hooks** encapsulate reusable logic

### Authentication Flow

#### Implementation
Authentication is implemented using a React Context pattern (`AuthContext.tsx`) that provides:

```typescript
interface AuthContextType {
  token: string | null;
  username: string | null;
  login: (username: string, password: string) => Promise;
  logout: () => void;
  isAuthenticated: boolean;
}
```

#### Flow
1. **Login Process**:
   - User submits credentials via `/login` page
   - `AuthContext.login()` sends POST request to `/token` endpoint (OAuth2 password flow)
   - On success, stores `access_token` and `username` in localStorage
   - Updates context state and redirects to main app

2. **Session Persistence**:
   - On app load, `AuthContext` checks localStorage for existing token
   - Automatically restores session if valid token exists

3. **Protected Routes**:
   - `ProtectedRoute` component wraps private pages
   - Redirects unauthenticated users to `/login`
   - Authenticated users access main chat interface

4. **Logout**:
   - Clears token and username from localStorage
   - Resets context state
   - Redirects to login page

#### Token Management
- Access token stored in localStorage as `access_token`
- Token included in all API requests via `Authorization: Bearer ${token}` header
- Session expiration handled with error responses (401) triggering automatic logout

### Chat System

#### Message Flow

1. **User Input** (`ChatInput.tsx`):
   - Text area with submit button
   - Enter key sends message (Shift+Enter for new line)
   - Displays typing indicator while user types
   - Disabled during API response

2. **Message Handling** (`Index.tsx`):
   ```typescript
   interface Message {
     role: 'user' | 'assistant';
     content: string;
     imageData?: string | null;
     imageMimeType?: string | null;
   }
   ```

3. **API Communication** (`lib/api.ts`):
   - `sendChatMessage()` sends POST to `/api/chat`
   - Includes authentication token in headers
   - Returns response with text and optional image data

4. **Response Processing**:
   - Backend returns JSON with structure:
     ```typescript
     {
       response: string | null;
       image_data: string | null;  // Base64 encoded
       image_mime_type: string | null;  // e.g., "image/png"
     }
     ```
   - Frontend conditionally renders image if `image_data` is present
   - Text response rendered with markdown support

#### Message Display (`ChatMessage.tsx`)

**User Messages**:
- Right-aligned with unicorn avatar
- Plain text display
- Compact styling

**Assistant Messages**:
- Left-aligned with agent avatar (state-based: listening/thinking/responding)
- **Markdown rendering** via `react-markdown` with `remark-gfm`
- Enhanced readability with custom prose styling:
  - Syntax-highlighted code blocks
  - Proper heading hierarchy
  - Styled lists, blockquotes, and links
  - High-contrast inline code
- **Image support**: Base64 images rendered when provided by backend

#### Agent States
The agent displays different avatars based on activity:
- **Listening** - Default state, ready for input
- **Thinking** - Displayed during API call (loading state)
- **Responding** - Shows during message delivery

#### Error Handling
- Network errors display user-friendly toast notifications
- 401 errors trigger automatic logout and redirect
- Session expiration handled gracefully
- Backend errors (500) shown with error messages

### Key Features

#### Welcome Screen
- Displayed when no messages exist
- Shows agent in "listening" state
- Provides visual context for new users

#### Responsive Design
- Mobile-first approach with Tailwind utilities
- Adaptive layouts for different screen sizes
- Touch-friendly interactive elements

#### Loading States
- Skeleton loading for agent thinking state
- Disabled input during processing
- Visual feedback for all async operations

### API Integration

#### Backend Endpoints

**Authentication**:
- `POST /token` - Login with username/password (OAuth2 form data)
- Returns `{ access_token: string }`

**Chat**:
- `POST /api/chat` - Send message and receive response
- Headers: `Authorization: Bearer ${token}`, `Content-Type: application/json`
- Body: `{ message: string }`
- Response: `{ response: string, image_data?: string, image_mime_type?: string }`

#### Environment Configuration
Backend URL configured via environment variable:
```typescript
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
```

### Development

#### Running Locally
```bash
npm install
npm run dev
```

#### Building for Production
```bash
npm run build
```

#### Environment Variables
- `VITE_BACKEND_URL` - Backend API base URL (optional, defaults to localhost:8000)

## Backend Documentation
Rumi Analytica - Application Documentation

## 1. Project Overview

**Rumi Analytica** is a sophisticated, multi-agent application designed for advanced data analysis and insight generation. Built using the Google Agent Development Kit (ADK), it employs a hierarchical agent architecture where a central orchestrator, "Rumi," intelligently delegates tasks to a team of specialized sub-agents.

Each sub-agent is an expert in a specific domain, such as web search, database querying, data science, econometrics, document analysis, and Google Analytics. This modular design allows the system to handle a wide variety of user requests, from simple knowledge lookups to complex statistical modeling and data visualization.

The application is served via a secure FastAPI backend, providing a robust API for user interaction and handling both text and image-based outputs.

## 2. System Architecture

The application follows an orchestrator-worker pattern.

*   **Root Agent (Orchestrator):** The main agent, `rumi_analytica`, acts as the central router. It analyzes the user's initial request and, based on detailed instructions in its prompt, selects the appropriate sub-agent for the task. It is also responsible for synthesizing the final response to the user, often personalizing it based on which sub-agent was called.

*   **Sub-Agents (Workers):** A collection of specialized agents, each with a unique persona and a dedicated set of tools and instructions.

| Agent Name | Persona | Directory | Purpose |
| :--- | :--- | :--- | :--- |
| `root_agent` | Rumi | `agents/agent` | Orchestrates tasks and routes requests to the correct sub-agent. |
| `web_search_agent` | Meruferat | `sub_agents/web_search_agent` | Answers general knowledge and current events questions using Google Search. |
| `database_agent` | Hiroshi | `sub_agents/bigquery_agent` | A BigQuery SQL expert that converts natural language to SQL and queries the database. |
| `ga4_template_agent`| Astra | `sub_agents/ga4_bigquery_agent` | A Google Analytics 4 specialist that uses predefined query templates to answer GA4 questions. |
| `data_science_agent`| Ginger | `sub_agents/data_science_agent`| A Python data scientist that performs data analysis, manipulation, and visualization. |
| `document_agent` | Candy | `sub_agents/document_agent` | A document specialist that answers questions based on a specific corpus of text using Vertex AI Search. |
| `econometrics_agent`| Persephone | `sub_agents/econometrics_agent`| An econometrician that guides users through rigorous statistical analysis and experimentation. |

## 3. File Structure

The project is organized into a `backend` directory containing the FastAPI server and the agent logic.

```
RUMI-ANALYTICA/
├── backend/
│   ├── agents/
│   │   ├── agent/                 # Root Agent (Orchestrator)
│   │   │   ├── agent.py
│   │   │   ├── prompts.py
│   │   │   └── tools.py
│   │   └── sub_agents/            # Specialized Worker Agents
│   │       ├── bigquery_agent/
│   │       ├── data_science_agent/
│   │       ├── document_agent/
│   │       ├── econometrics_agent/
│   │       ├── ga4_bigquery_agent/
│   │       └── web_search_agent/
│   ├── utils/
│   │   └── utils.py
│   └── main.py                    # FastAPI Server Entrypoint
├── .env                           # Environment variables
├── .gitignore
├── Dockerfile
├── requirements.txt
└── ...
```

## 4. Core Components

### 4.1. FastAPI Backend (`main.py`)

This file is the main entry point for the application. It sets up a FastAPI server to handle user interactions.

*   **Authentication:** Implements JWT-based authentication. A `/token` endpoint validates user credentials (username and a bcrypt-hashed password) and issues an access token. All other API endpoints are protected.
*   **CORS:** Configured to allow requests from specified frontend origins.
*   **Session Management:** Uses `InMemorySessionService` from the ADK to maintain conversation history for each user.
*   **API Endpoints:**
    *   `POST /token`: Issues a JWT access token upon successful login.
    *   `POST /api/chat`: The main interaction endpoint. It receives a user's message, runs it through the `root_agent` using the ADK `Runner`, and processes the agent's response.
    *   `GET /health`: A simple health check endpoint.
*   **Artifact Handling:** The `/api/chat` endpoint is specifically designed to handle both text and image outputs. If a sub-agent (like the `data_science_agent`) generates a plot, it is saved as an artifact. The `main.py` file loads this artifact, encodes the image data in Base64, and includes it in the JSON response alongside the text.

### 4.2. Root Agent (`agents/agent/`)

This is the orchestrator agent that manages the entire workflow.

*   **`agent.py`**: Defines the `root_agent` using `google.adk.agents.Agent`. It is configured with its model, description, and a list of tools. These tools are Python functions that call the various sub-agents.
*   **`prompts.py`**: Contains `return_root_agent_prompt()`, which provides the core routing logic. This prompt instructs the agent on which tool (and therefore which sub-agent) to call based on keywords and the nature of the user's question (e.g., "If the user asks about GA4... call `call_ga4_template_agent`"). It also defines the agent's personality, "Rumi."
*   **`tools.py`**: Defines the wrapper functions (e.g., `call_data_science_agent`) that the `root_agent` uses as tools. Each function uses `AgentTool` to asynchronously run a specific sub-agent and pass the user's question to it.

## 5. Sub-Agents Deep Dive

### 5.1. BigQuery Agent (Hiroshi)

*   **Purpose:** Acts as a general-purpose Natural-Language-to-SQL agent for a BigQuery database.
*   **Directory:** `sub_agents/bigquery_agent/`
*   **Core Logic:**
    1.  It first uses the `initial_bq_nl2sql` tool to generate a "best-effort" SQL query from the user's question using an LLM. This tool fetches the database schema to provide context to the LLM.
    2.  It then uses the ADK's built-in `execute_sql` tool from the `BigQueryToolset` to validate and run the generated query.
    3.  The agent is instructed to iterate if the SQL fails, regenerating the query to fix the error.
    4.  The final output is a structured JSON object containing an explanation, the final SQL, the raw results, and a natural language summary.

### 5.2. GA4 BigQuery Agent (Astra)

*   **Purpose:** A highly specialized agent for answering questions about Google Analytics 4 data stored in BigQuery.
*   **Directory:** `sub_agents/ga4_bigquery_agent/`
*   **Core Logic:** This agent uses a template-based approach for reliability and precision.
    1.  **`query_template_library.py`**: Contains a dictionary (`QUERY_TEMPLATE_LIBRARY`) of predefined, parameterized SQL queries for common GA4 questions.
    2.  **`prompts.py`**: The prompt instructs the agent to match the user's question to one of the available templates and extract the necessary parameters (like dates or campaign names).
    3.  **`tools.py`**: Defines the `execute_ga4_template_query` tool. This tool takes the chosen template name and parameters, formats the corresponding SQL query from the library, and executes it using the ADK's `BigQueryToolset`.

### 5.3. Data Science Agent (Ginger)

*   **Purpose:** Executes Python code for general data analysis, manipulation, and visualization.
*   **Directory:** `sub_agents/data_science_agent/`
*   **Core Logic:**
    1.  Uses the `VertexAiCodeExecutor` to run Python code in a stateful environment.
    2.  The prompt instructs the agent to expect data to be passed in from the root agent (e.g., after being fetched by the `database_agent`). It should not generate dummy data unless explicitly asked.
    3.  **Visualization:** When creating a plot with `matplotlib`, the agent is instructed to save it to a specific file, `generated_plot.png`. This standardized filename allows the `main.py` backend to easily find, load, and return the image to the user.

### 5.4. Econometrics Agent (Persephone)

*   **Purpose:** A highly specialized agent for guiding users through rigorous econometric analysis, A/B testing, and causal inference.
*   **Directory:** `sub_agents/econometrics_agent/`
*   **Core Logic:**
    1.  This agent also uses the `VertexAiCodeExecutor` for statistical calculations.
    2.  The prompt is extremely detailed, defining a multi-step workflow for experimental design and analysis:
        *   Hypothesis Clarification
        *   Experimental Design (A/B test, control/treatment groups)
        *   Power Analysis & Sample Size Calculation
        *   Data Collection Instruction (by generating SQL for the user to run)
        *   Statistical Analysis (using Python to run z-tests or t-tests)
        *   Interpretation and Conclusion

### 5.5. Document Agent (Candy)

*   **Purpose:** Answers questions based on a private corpus of documents.
*   **Directory:** `sub_agents/document_agent/`
*   **Core Logic:**
    1.  Uses the `VertexAiSearchTool`, which is configured to point to a specific Vertex AI Search data store (`rumi-analytica-books_1761800267595`).
    2.  The prompt strictly instructs the agent to base its answers *exclusively* on the information returned by the search tool and to cite its sources.

### 5.6. Web Search Agent (Meruferat)

*   **Purpose:** Provides answers to general knowledge questions or queries about current events.
*   **Directory:** `sub_agents/web_search_agent/`
*   **Core Logic:**
    1.  This is the simplest agent, using the ADK's built-in `google_search` tool.
    2.  The prompt instructs it to use the tool and summarize the findings for the user.

## 6. Configuration & Dependencies

*   **Configuration:** The application relies heavily on environment variables, which should be stored in a `.env` file. These include `GOOGLE_CLOUD_PROJECT`, BigQuery project/dataset IDs, model names, and authentication secrets (`JWT_SECRET_KEY`, etc.). The `utils/utils.py` file provides a helper for loading these variables.
*   **Dependencies:** All required Python packages are listed in `requirements.txt`. Key dependencies include:
    *   `google-cloud-ai-agent-development-kit`
    *   `fastapi`
    *   `python-jose[cryptography]`
    *   `passlib[bcrypt]`
    *   `uvicorn`
    *   `python-dotenv`

    # Rumi-Analytica Automated Deployment Script

This documentation outlines the functionality of the `setup.sh` script, which automates the deployment of the Rumi-Analytica application to Google Cloud Platform.

---

## 1. Overview

The script performs a complete end-to-end setup, including:
*   Checking for prerequisite tools.
*   Gathering user configuration.
*   Provisioning necessary GCP resources (Service Accounts, APIs, Secrets).
*   Building and deploying the frontend and backend services to Cloud Run.
*   Configuring a CI/CD pipeline using Cloud Build for future deployments.

---

## 2. Prerequisites

Before running the script, you must have the following tools installed and authenticated:

*   `gcloud`: The Google Cloud SDK.
*   `docker`: The Docker engine, which must be running.
*   `python3`: Python 3 interpreter.
*   `pip`: Python package installer.

The script will verify their existence and exit if any are missing.

---

## 3. Execution

Run the script from your terminal:

```bash
./setup.sh
```

---

## 4. Script Workflow

### Step 1: Gather User Input

The script will prompt you for the following configuration details:

| Prompt | Description | Example |
| :--- | :--- | :--- |
| **GCP Project ID** | The target Google Cloud project for deployment. | `my-gcp-project-123` |
| **GCP Region** | The region for Cloud Run and other resources. | `us-central1` |
| **GitHub Username** | Your username on GitHub. | `my-github-user` |
| **GitHub Repository Name** | The name of your forked application repository. | `rumi-analytica-app` |
| **Simple Auth Username** | A username for the backend's basic authentication. | `admin` |
| **Simple Auth Password** | A password for the backend's basic authentication. | `(hidden input)` |
| **BigQuery DATA Project ID** | The GCP project where your BigQuery data resides. | `my-data-project` |
| **BigQuery Dataset ID** | The BigQuery dataset the application will query. | `analytics_dataset` |
| **BigQuery COMPUTE Project ID**| The GCP project to bill for BigQuery jobs. | `(defaults to main Project ID)` |

### Step 2: GCP Configuration & API Enablement

*   Sets the active `gcloud` configuration to use the specified `PROJECT_ID`.
*   Enables the following GCP APIs:
    *   Cloud Run API (`run.googleapis.com`)
    *   IAM API (`iam.googleapis.com`)
    *   Artifact Registry API (`artifactregistry.googleapis.com`)
    *   Cloud Build API (`cloudbuild.googleapis.com`)
    *   Secret Manager API (`secretmanager.googleapis.com`)
    *   Vertex AI API (`aiplatform.googleapis.com`)
    *   BigQuery API (`bigquery.googleapis.com`)

### Step 3: Service Accounts & Permissions

Two service accounts are created:

1.  **App Runner SA (`rumi-app-runner-sa`)**: The identity for the running Cloud Run services.
    *   **Permissions**: Access to Vertex AI, BigQuery, and secrets in Secret Manager.
2.  **Builder SA (`rumi-builder-sa`)**: The identity for the Cloud Build pipeline.
    *   **Permissions**: Admin access to Cloud Run, write access to Artifact Registry, access to secrets, and the ability to act as the App Runner SA.

### Step 4: Secret Creation

The script creates and populates two secrets in Secret Manager:

*   `RUMI_JWT_SECRET`: A randomly generated key for signing JSON Web Tokens.
*   `RUMI_PASSWORD_HASH`: A bcrypt hash of the user-provided password.
    *   *Note: The script temporarily installs `passlib` and `bcrypt` via `pip` to generate this hash securely.*

### Step 5: Artifact Registry & Docker

*   Creates a Docker repository named `rumi-analytica` in Artifact Registry.
*   Configures the local Docker client to authenticate with this repository.

### Step 6: Initial Deployment

The script performs a multi-stage initial deployment:

1.  **Backend Deploy**:
    *   Builds the `backend/` Docker image.
    *   Pushes the image to Artifact Registry.
    *   Deploys it as a Cloud Run service named `rumi-analytica-backend`.
    *   Injects environment variables and secrets.
    *   Captures the assigned service URL.

2.  **Frontend Deploy**:
    *   Builds the `frontend/` application, injecting the backend URL as `VITE_BACKEND_URL`.
    *   Builds the `frontend/` Docker image.
    *   Pushes the image to Artifact Registry.
    *   Deploys it as a Cloud Run service named `rumi-analytica-frontend`.
    *   Captures the assigned service URL.

3.  **Backend Update**:
    *   Updates the `rumi-analytica-backend` service to add the `FRONTEND_URL` environment variable, enabling proper CORS configuration.

### Step 7: Cloud Build Trigger

*   Creates a Cloud Build trigger named `deploy-rumi-analytica-main`.
*   Connects to the specified GitHub repository.
*   The trigger automatically runs the `cloudbuild.yaml` file upon pushes to the `main` branch that modify files in the `backend/` or `frontend/` directories.

---

## 5. Post-Deployment

Upon successful completion, the script will output:

*   The public URL for the frontend and backend services.
*   A confirmation that the CI/CD trigger has been created.
*   A reminder on how to update the application password by creating a new version of the `RUMI_PASSWORD_HASH` secret.


# Cloud Build CI/CD Pipeline (`cloudbuild.yaml`)

This file defines the continuous integration and deployment (CI/CD) pipeline for the Rumi-Analytica application. It is executed by a Cloud Build trigger whenever changes are pushed to the `main` branch.

---

## 1. Overview

The pipeline automates the process of building, testing, and deploying both the backend and frontend services to Cloud Run. It runs as a series of sequential steps, ensuring that the backend is deployed before the frontend build process begins.

---

## 2. Pipeline Steps

The pipeline is divided into two main stages: Backend Deployment and Frontend Deployment.

### Backend Steps

1.  **Build Backend Image**:
    *   Uses the standard Docker builder (`gcr.io/cloud-builders/docker`).
    *   Executes `docker build` within the `backend/` directory.
    *   Tags the resulting image for upload to Artifact Registry.

2.  **Push Backend Image**:
    *   Pushes the newly built backend image to the `rumi-analytica` repository in Artifact Registry.

3.  **Deploy Backend**:
    *   Uses the Google Cloud SDK builder (`gcr.io/google.com/cloudsdktool/cloud-sdk`).
    *   Executes `gcloud run deploy` to update the `rumi-analytica-backend` service.
    *   Deploys the image pushed in the previous step.
    *   Configures the service with environment variables and secrets using substitution variables provided by the trigger.

### Frontend Steps

1.  **Frontend NPM Install**:
    *   Uses a Node.js builder (`node:18`).
    *   Executes `npm ci` within the `frontend/` directory to install dependencies from the `package-lock.json` file.

2.  **Frontend Build**:
    *   Executes `npm run build` to create a production-ready build of the frontend application.
    *   Injects the `VITE_BACKEND_URL` environment variable into the build process, using the `_BACKEND_URL` substitution variable. This ensures the frontend knows how to communicate with the backend.

3.  **Build Frontend Image**:
    *   Builds the Docker image for the frontend, which serves the static files generated in the previous step.

4.  **Push Frontend Image**:
    *   Pushes the frontend image to Artifact Registry.

5.  **Deploy Frontend**:
    *   Executes `gcloud run deploy` to update the `rumi-analytica-frontend` service with the new image.

---

## 3. Configuration

### Substitutions

Substitution variables are used to pass dynamic values from the Cloud Build trigger to the pipeline at runtime.

| Variable | Description |
| :--- | :--- |
| `_BACKEND_URL` | The public URL of the deployed backend service. |
| `_FRONTEND_URL` | The public URL of the deployed frontend service. |
| `_SIMPLE_AUTH_USERNAME` | The username for the backend's simple authentication. |
| `_GOOGLE_CLOUD_PROJECT` | The GCP Project ID where resources are located. |
| `_GOOGLE_CLOUD_LOCATION`| The GCP region for the resources. |
| `_BQ_DATA_PROJECT_ID` | The Project ID where the BigQuery data is stored. |
| `_BQ_DATASET_ID` | The BigQuery Dataset ID to be queried. |
| `_BQ_COMPUTE_PROJECT_ID`| The Project ID to bill for BigQuery jobs. |
| `_BIGQUERY_AGENT_MODEL` | The Vertex AI model for the BigQuery agent (defaults to `gemini-1.5-flash`). |
| `_BASELINE_NL2SQL_MODEL`| The Vertex AI model for baseline NL2SQL tasks (defaults to `gemini-1.5-flash`). |

### Options

*   `logging: CLOUD_LOGGING_ONLY`: This option ensures that all build logs are sent directly to Google Cloud's operations suite (Cloud Logging) and are not stored on the build worker.
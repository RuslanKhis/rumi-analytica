# rumi-analytica
![Logo](/images/rumi-analytica-logo.png)
Multi-agent analytics platform powered by Gemini and deployed on Cloud Run.

TODO:
+ need to provide discovery Engine Viewer to service account & enable  Cloud Resource Manager API  on the project

## Deployment Guide

Follow these steps to deploy the application to your own Google Cloud project.

### Step 1: Fork and Clone the Repository

1. **Fork** this repository to your own GitHub account by clicking the "Fork" button at the top right of the page.


## Creating Cloud Build Triggers
### Connect GitHub to Google Cloud Build

This one-time setup authorizes your Google Cloud project to access your GitHub repository, which is required for the automated CI/CD pipeline.

**IMPORTANT:** Before accessing a link below, you might be redirected to enable the Cloud Build API. It is fine to enable that API, and then click on the link again.

1.  Navigate to the **[Cloud Build Repositories page](https://console.cloud.google.com/cloud-build/repositories)** in the GCP Console.
2.  Make sure you are in the correct GCP project, then click **Connect repository**.
3.  Select **GitHub (Cloud Build GitHub App)** as the source and click **Continue**.
4.  Authenticate with your GitHub account. You will be redirected to GitHub to **Authorize Google Cloud Build**.
5.  On the next screen, you may be prompted to **Install Google Cloud Build** if it's not already configured for your account. Click the install button and choose which repositories to grant access to (you can select just your forked repo).
6.  You will be redirected back to the GCP console. Select your **GitHub Account** and the forked **Repository** from the dropdown menus.
7.  Check the box to agree to the terms and click **Connect**.


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
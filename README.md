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

### Frontend Documentation

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
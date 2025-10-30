import os
import sys
import base64  # <-- MODIFIED: Added for encoding image data
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional  # <-- MODIFIED: Added Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part
from google.adk.artifacts import InMemoryArtifactService

# --- Your existing ADK agent definition ---
from agents.agent.agent import root_agent as agent

# --- Load Environment Variables ---
load_dotenv()

# Check if we are using Vertex AI via service account
USE_VERTEX_AI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() == "true"

# If not using Vertex, an API key is required.
if not USE_VERTEX_AI:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        print("❌ GOOGLE_API_KEY is not set and not using Vertex AI. Exiting.", file=sys.stderr)
        sys.exit(1)

# These are always required and loaded from the environment/secrets
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
SIMPLE_AUTH_PASSWORD_HASH = os.getenv("SIMPLE_AUTH_PASSWORD_HASH")
SIMPLE_AUTH_USERNAME = os.getenv("SIMPLE_AUTH_USERNAME")
ALGORITHM = "HS256"

if not all([JWT_SECRET_KEY, SIMPLE_AUTH_USERNAME, SIMPLE_AUTH_PASSWORD_HASH]):
    print("❌ Auth env vars are not set. Exiting.", file=sys.stderr); sys.exit(1)

# --- FastAPI App and Router Setup ---
app = FastAPI(title="Rumi-Analytica Backend")
router = APIRouter()

# --- CORS Middleware ---
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
]
FRONTEND_URL = os.getenv("FRONTEND_URL")
if FRONTEND_URL:
    print(f"INFO: Allowing CORS for deployed origin: {FRONTEND_URL}")
    origins.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Create a shared session service instance ---
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()
AGENT_APP_NAME = "agent"

# --- Authentication Helpers ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None or username != SIMPLE_AUTH_USERNAME: raise unauthorized
    except JWTError:
        raise unauthorized
    return {"username": username}

# --- API Models ---
class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class SimpleChatRequest(BaseModel):
    message: str

# Response model updated to include optional image data
class ChatApiResponse(BaseModel):
    response: Optional[str] = None
    image_data: Optional[str] = None  # Base64 encoded image string
    image_mime_type: Optional[str] = None

# --- API Routes ---
# Token endpoint
@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    if (form_data.username != SIMPLE_AUTH_USERNAME or not verify_password(form_data.password, SIMPLE_AUTH_PASSWORD_HASH)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}


# Chat endpoint updated to handle image artifacts
@router.post("/api/chat", response_model=ChatApiResponse)
async def simple_chat(
    chat_request: SimpleChatRequest,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["username"]
    session_id = f"{user_id}_default_session"

    session = await session_service.get_session(
        app_name=AGENT_APP_NAME, user_id=user_id, session_id=session_id
    )
    if session is None:
        session = await session_service.create_session(
            app_name=AGENT_APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )

    runner = Runner(
        agent=agent,
        session_service=session_service,
        app_name=AGENT_APP_NAME,
        artifact_service=artifact_service
    )

    adk_message = Content(role="user", parts=[Part(text=chat_request.message)])
    
    # Variables to store results from the agent run
    response_text: str | None = None
    image_data_b64: str | None = None
    image_mime_type: str | None = None

    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=adk_message
        ):
            # 1. Check for new artifacts (like images/plots)
            if event.actions and event.actions.artifact_delta:
                # Get the filename and version from the event
                filename, version = next(iter(event.actions.artifact_delta.items()))
                
                # Load the artifact using the shared service instance
                artifact = await artifact_service.load_artifact(
                    app_name=AGENT_APP_NAME,
                    user_id=user_id,
                    session_id=session.id,
                    filename=filename,
                    version=version
                )
                
                if artifact and artifact.inline_data:
                    # Encode binary data to a base64 string for JSON transport
                    image_data_b64 = base64.b64encode(artifact.inline_data.data).decode('utf-8')
                    image_mime_type = artifact.inline_data.mime_type
                    print(f"INFO: Loaded artifact '{filename}' (v{version}) with MIME type {image_mime_type}")

            # 2. Check for the final text response
            if event.is_final_response() and event.content.parts:
                if event.content.parts[0].text:
                    response_text = event.content.parts[0].text

    except Exception as e:
        print(f"Error during ADK run: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Error communicating with the agent.")

    # 3. Return a response if either text or an image was generated
    if not response_text and not image_data_b64:
        raise HTTPException(status_code=500, detail="Agent did not produce a final response or artifact.")

    return ChatApiResponse(
        response=response_text,
        image_data=image_data_b64,
        image_mime_type=image_mime_type
    )

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

# --- Include the router in the app ---
app.include_router(router)
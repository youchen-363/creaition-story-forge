from dotenv import load_dotenv
from supabase import create_client
import os

load_dotenv()  # load variables from .env into environment

API_URL = os.getenv("API_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")

ASSETS_FOLDER = "/assets/"
OUTPUT_FOLDER = "/output/"

# Create main client with anon key for general operations
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Create service client with service role key for storage operations (bypasses RLS)
supabase_service = None
if SUPABASE_SERVICE_KEY:
    supabase_service = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    print("✅ Supabase service client initialized for storage operations")
else:
    print("⚠️  Warning: SUPABASE_SERVICE_KEY not found - storage uploads may fail due to RLS policies")

# Safe import and initialization of genai
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    print("⚠️  Warning: google.genai not installed")
    GENAI_AVAILABLE = False

# Initialize Gemini client if possible
gemini_client = None
if GENAI_AVAILABLE and GEMINI_API_KEY:
    try:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        print("✅ Gemini client initialized")
    except Exception as e:
        print(f"⚠️  Failed to initialize Gemini client: {e}")
        gemini_client = None
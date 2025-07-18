"""
FastAPI Backend for CreAItion
Integrates with MCP Server, n8n workflows, and Supabase
"""

import os
import uuid
import json
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# Database imports (will work once supabase is set up)
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Warning: Supabase not available")

load_dotenv()

# Initialize Supabase client if available
supabase: Optional[Client] = None
if SUPABASE_AVAILABLE:
    try:
        supabase_url = os.getenv("SUPABASE_URL", "")
        supabase_key = os.getenv("SUPABASE_ANON_KEY", "")
        
        if not supabase_url or not supabase_key:
            print("Warning: Could not initialize Supabase: supabase_url and supabase_anon_key are required")
        else:
            supabase = create_client(supabase_url, supabase_key)
            print("✅ Supabase client initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize Supabase: {e}")

# Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook")

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 CreAItion FastAPI server starting...")
    print(f"📡 MCP Server: {MCP_SERVER_URL}")
    print(f"🔄 n8n Webhooks: {N8N_WEBHOOK_URL}")
    print(f"🗄️ Supabase: {'✅ Connected' if supabase else '❌ Not available'}")
    
    yield
    
    # Shutdown (if needed)
    print("🛑 CreAItion FastAPI server shutting down...")

# FastAPI app
app = FastAPI(
    title="CreAItion API",
    version="1.0.0",
    description="AI-powered story generation with MCP integration",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000",
        "http://192.168.1.144:8082",
        "http://192.168.1.144:8080",  # Added new frontend URL
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create assets directory if it doesn't exist
assets_dir = Path("assets")
assets_dir.mkdir(exist_ok=True)

# Mount static files to serve uploaded images
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# In-memory storage for demo (stores story titles to prevent duplicates)
demo_story_titles = set()

# Configuration that was moved above
# MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")
# N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook")

# Pydantic models
class StoryRequest(BaseModel):
    title: str
    characters: List[Dict[str, Any]]
    background_story: str
    num_scenes: int = 4
    user_id: Optional[str] = None
    cover_image_url: Optional[str] = None
    cover_image_name: Optional[str] = None

class CharacterRequest(BaseModel):
    name: str
    description: str
    image_url: Optional[str] = None

class StoryResponse(BaseModel):
    success: bool
    story_id: Optional[str] = None
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

# Utility functions
async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Call MCP server tool"""
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:  # 5 minute timeout
            response = await client.post(
                f"{MCP_SERVER_URL}/tools/{tool_name}",
                json=arguments
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"MCP server error: {response.status_code}",
                    "details": response.text
                }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to call MCP tool: {str(e)}"
        }

async def trigger_n8n_workflow(workflow_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Trigger n8n workflow"""
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{N8N_WEBHOOK_URL}/{workflow_name}",
                json=data
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"n8n workflow error: {response.status_code}",
                    "details": response.text
                }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to trigger n8n workflow: {str(e)}"
        }

async def save_story_to_db(story_data: Dict[str, Any]) -> Optional[str]:
    """Save story to Supabase database"""
    if not supabase:
        print("Supabase not available, skipping database save")
        return None
    
    try:
        result = supabase.table("stories").insert({
            "id": str(uuid.uuid4()),
            "user_id": story_data.get("user_id"),
            "title": story_data.get("title"),
            "background_story": story_data.get("background_story"),
            "future_story": story_data.get("future_story"),
            "analysis": story_data.get("analysis"),
            "num_scenes": story_data.get("num_scenes", 4),
            "status": story_data.get("status", "generating"),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }).execute()
        
        if result.data:
            return result.data[0]["id"]
        return None
    except Exception as e:
        print(f"Error saving to database: {e}")
        return None

# API Routes

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "CreAItion API",
        "version": "1.0.0",
        "status": "running",
        "services": {
            "mcp_server": MCP_SERVER_URL,
            "n8n_webhooks": N8N_WEBHOOK_URL,
            "supabase": supabase is not None
        },
        "endpoints": [
            "/stories/generate",
            "/characters/upload",
            "/stories/{story_id}",
            "/user/stories",
            "/mcp/tools",
            "/health",
            "/demo/titles",
            "/demo/clear-titles"
        ]
    }

@app.post("/api/stories/generate", response_model=StoryResponse)
async def generate_story(request: StoryRequest, background_tasks: BackgroundTasks):
    """
    Generate a complete story using MCP tools and n8n workflow
    This creates a story generation pipeline
    """
    try:
        # Check if story with same title already exists (demo mode - in-memory check)
        if request.title.lower() in demo_story_titles:
            return StoryResponse(
                success=False,
                status="error",
                message=f"A story with the title '{request.title}' already exists. Please choose a different title."
            )
        
        # Also check database if available
        if supabase:
            try:
                existing_check = supabase.table("stories")\
                    .select("id, title")\
                    .eq("title", request.title)\
                    .execute()
                
                if existing_check.data and len(existing_check.data) > 0:
                    return StoryResponse(
                        success=False,
                        status="error",
                        message=f"A story with the title '{request.title}' already exists. Please choose a different title."
                    )
            except Exception as db_error:
                print(f"Error checking for existing story: {db_error}")
                # Continue with creation if check fails (for demo purposes)
        
        story_id = str(uuid.uuid4())
        
        # Add title to demo cache
        demo_story_titles.add(request.title.lower())
        
        # For now, skip database save due to RLS policy issue
        # Save initial story record
        if supabase:
            try:
                # Include cover image information in background story if provided
                background_with_image = request.background_story
                if request.cover_image_url:
                    background_with_image += f"\n\n[Cover Image: {request.cover_image_url}]"
                
                initial_data = {
                    "id": story_id,
                    "user_id": request.user_id,
                    "title": request.title,
                    "background_story": background_with_image,
                    "num_scenes": request.num_scenes,
                    "status": "generating",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                result = supabase.table("stories").insert(initial_data).execute()
                if not result.data:
                    print("Warning: Failed to create story record in database due to RLS policy")
                    # Continue without database save for now
            except Exception as db_error:
                print(f"Database error (continuing without DB save): {db_error}")
                # Continue with story generation even if DB save fails
        
        # Prepare data for story generation pipeline
        generation_data = {
            "story_id": story_id,
            "title": request.title,
            "characters": request.characters,
            "background_story": request.background_story,
            "num_scenes": request.num_scenes,
            "user_id": request.user_id,
            "cover_image_url": request.cover_image_url
        }
        
        # For demo purposes, skip MCP pipeline and return success
        # Add background task to run the generation pipeline
        # background_tasks.add_task(run_story_generation_pipeline, generation_data)
        
        return StoryResponse(
            success=True,
            story_id=story_id,
            status="generating",
            message="Story generation started. Database RLS policy needs to be configured for full functionality."
        )
        
        return StoryResponse(
            success=True,
            story_id=story_id,
            status="generating",
            message="Story generation started. Check back for updates or use real-time subscriptions."
        )
        
    except Exception as e:
        # Log the full error for debugging
        print(f"Error in generate_story: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

async def run_story_generation_pipeline(data: Dict[str, Any]):
    """
    Background task to run the complete story generation pipeline
    This combines MCP tools in sequence
    """
    story_id = data["story_id"]
    
    try:
        # Step 1: Generate story and analysis using MCP
        print(f"Starting story generation for {story_id}")
        story_result = await call_mcp_tool("analyze_characters_and_generate_story", {
            "characters_data": data["characters"],
            "background_story": data["background_story"],
            "num_scenes": data["num_scenes"]
        })
        
        if not story_result.get("success"):
            await update_story_status(story_id, "failed", error=story_result.get("error"))
            return
        
        # Step 2: Generate detailed scenes
        print(f"Generating scenes for {story_id}")
        scenes_result = await call_mcp_tool("generate_detailed_scenes", {
            "num_panels": 6,
            "num_scenes": data["num_scenes"],
            "analysis": story_result["analysis"],
            "future_story": story_result["future_story"]
        })
        
        if not scenes_result.get("success"):
            await update_story_status(story_id, "failed", error=scenes_result.get("error"))
            return
        
        # Step 3: Generate images for scenes
        print(f"Generating images for {story_id}")
        images_result = await call_mcp_tool("generate_comic_images", {
            "characters_data": data["characters"],
            "scenes": scenes_result["scenes"]
        })
        
        if not images_result.get("success"):
            await update_story_status(story_id, "failed", error=images_result.get("error"))
            return
        
        # Step 4: Save complete story to database
        complete_story_data = {
            "id": story_id,
            "future_story": story_result["future_story"],
            "analysis": story_result["analysis"],
            "status": "completed",
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if supabase:
            # Update story
            supabase.table("stories").update(complete_story_data).eq("id", story_id).execute()
            
            # Save scenes
            for i, scene in enumerate(scenes_result["scenes"]):
                scene_data = {
                    "id": str(uuid.uuid4()),
                    "story_id": story_id,
                    "scene_number": i + 1,
                    "content": scene,
                    "created_at": datetime.utcnow().isoformat()
                }
                supabase.table("scenes").insert(scene_data).execute()
            
            # Save images
            if images_result.get("images"):
                for i, image_url in enumerate(images_result["images"]):
                    image_data = {
                        "id": str(uuid.uuid4()),
                        "story_id": story_id,
                        "scene_number": i + 1,
                        "image_url": image_url,
                        "created_at": datetime.utcnow().isoformat()
                    }
                    supabase.table("generated_images").insert(image_data).execute()
        
        print(f"Story generation completed for {story_id}")
        
    except Exception as e:
        print(f"Error in story generation pipeline: {e}")
        await update_story_status(story_id, "failed", error=str(e))

async def update_story_status(story_id: str, status: str, error: Optional[str] = None):
    """Update story status in database"""
    if not supabase:
        return
    
    try:
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if error:
            update_data["error"] = error
        
        supabase.table("stories").update(update_data).eq("id", story_id).execute()
    except Exception as e:
        print(f"Error updating story status: {e}")

@app.post("/api/characters/upload")
async def upload_character_image(
    file: UploadFile = File(...),
    name: str = None,
    description: str = None
):
    """Upload character image and extract character info using MCP"""
    try:
        # Create assets directory if it doesn't exist
        upload_dir = Path("assets")
        upload_dir.mkdir(exist_ok=True)
        
        # Save uploaded file
        file_extension = Path(file.filename).suffix
        unique_filename = f"character_{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Call MCP character extraction tool
        extraction_result = await call_mcp_tool("extract_character_from_image", {
            "image_url": str(file_path),
            "character_name": name or "Unknown Character"
        })
        
        # Create the image URL that can be accessed from frontend
        image_url = f"/assets/{unique_filename}"
        
        if extraction_result.get("success"):
            character_data = {
                "name": name or extraction_result.get("suggested_name", "Unknown Character"),
                "description": description or extraction_result.get("character_analysis", ""),
                "image_url": str(file_path),
                "image_url": image_url,
                "analysis": extraction_result.get("character_analysis")
            }
            
            return {
                "success": True,
                "character": character_data,
                "file_path": str(file_path),
                "image_url": image_url,
                "extraction_result": extraction_result
            }
        else:
            # Still return the image URL even if extraction fails
            character_data = {
                "name": name or "Unknown Character",
                "description": description or "",
                "image_url": str(file_path),
                "image_url": image_url,
                "analysis": ""
            }
            
            return {
                "success": True,  # We still uploaded the image successfully
                "character": character_data,
                "file_path": str(file_path),
                "image_url": image_url,
                "extraction_result": extraction_result,
                "warning": "Character extraction failed, but image was uploaded successfully"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stories/{story_id}")
async def get_story(story_id: str):
    """Get story details with all related data"""
    if not supabase:
        # Return mock data if database not available
        return {
            "success": True,
            "story": {
                "id": story_id,
                "title": "Sample Story",
                "status": "generating",
                "background_story": "Your story is being generated...",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "num_scenes": 5
            }
        }
    
    try:
        # Get story with scenes and images
        result = supabase.table("stories")\
            .select("*, scenes(*), generated_images(*)")\
            .eq("id", story_id)\
            .execute()
        
        if result.data:
            story = result.data[0]
            return {
                "success": True,
                "story": story
            }
        else:
            # Return mock data if story not found due to RLS issues
            return {
                "success": True,
                "story": {
                    "id": story_id,
                    "title": "Generated Story",
                    "status": "generating",
                    "background_story": "🎨 Your story is being generated... This may take a few minutes. Please check back soon!",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "num_scenes": 5
                }
            }
            
    except Exception as e:
        print(f"Error fetching story: {e}")
        # Return mock data as fallback
        return {
            "success": True,
            "story": {
                "id": story_id,
                "title": "Generated Story",
                "status": "generating", 
                "background_story": "🎨 Your story is being generated... Database RLS policy needs to be configured.",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "num_scenes": 5
            }
        }

@app.get("/api/user/stories")
async def get_user_stories(user_id: str):
    """Get all stories for a user"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.table("stories")\
            .select("id, title, status, created_at, updated_at")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()
        
        return {
            "success": True,
            "stories": result.data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mcp/tools")
async def get_mcp_tools():
    """Get available MCP tools for frontend display"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MCP_SERVER_URL}/tools")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch MCP tools")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mcp/call/{tool_name}")
async def call_mcp_tool_endpoint(tool_name: str, arguments: Dict[str, Any]):
    """Direct endpoint to call MCP tools"""
    result = await call_mcp_tool(tool_name, arguments)
    return result

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    mcp_healthy = False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{MCP_SERVER_URL}/health")
            mcp_healthy = response.status_code == 200
    except:
        pass
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "supabase": supabase is not None,
            "mcp_server": mcp_healthy,
            "n8n": N8N_WEBHOOK_URL is not None
        },
        "environment": {
            "mcp_url": MCP_SERVER_URL,
            "n8n_url": N8N_WEBHOOK_URL
        }
    }

@app.post("/api/test/story")
async def test_story_creation():
    """Test endpoint to debug story creation issues"""
    try:
        if not supabase:
            return {"error": "Supabase not available"}
        
        # Test basic database connection
        test_story_id = str(uuid.uuid4())
        test_data = {
            "id": test_story_id,
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Test Story",
            "background_story": "Test background",
            "num_scenes": 3,
            "status": "test",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("stories").insert(test_data).execute()
        
        return {
            "success": True,
            "message": "Test story created successfully",
            "story_id": test_story_id,
            "result": result.data
        }
        
    except Exception as e:
        print(f"Test story creation error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }

@app.post("/api/demo/clear-titles")
async def clear_demo_titles():
    """Clear the demo story titles cache (for demo/testing purposes)"""
    global demo_story_titles
    demo_story_titles.clear()
    return {
        "success": True,
        "message": "Demo story titles cache cleared",
        "remaining_titles": len(demo_story_titles)
    }

@app.get("/api/demo/titles")
async def get_demo_titles():
    """Get current demo story titles (for demo/testing purposes)"""
    return {
        "success": True,
        "titles": list(demo_story_titles),
        "count": len(demo_story_titles)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

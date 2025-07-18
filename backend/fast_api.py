"""
Simple FastAPI Backend for CreAItion
Direct integration with AI modules without MCP/n8n complexity
"""

import uuid
import traceback
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import zipfile
import io
import requests
import tempfile
import os

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from config import SUPABASE_URL, SUPABASE_ANON_KEY

# Database imports (will work once supabase is set up)
try:
    from config import supabase, ASSETS_FOLDER
    from supabase_storage import upload_to_supabase_storage
    from supabase import Client
    from dao import DAOFactory
    from User import User
    SUPABASE_AVAILABLE = True
except ImportError as e:
    SUPABASE_AVAILABLE = False
    print(f"Warning: Supabase not available: {e}")

from image_to_text import generate_narrative_scenes
from image_to_image import generate_images_with_updates
from User_Character import User_Character
from Story import Story
from config import gemini_client

# Import AI modules directly
try:
    from google import genai
    AI_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import AI modules: {e}")
    AI_MODULES_AVAILABLE = False

# Initialize DAO factory with imported supabase client
dao_factory: Optional[DAOFactory] = None

if SUPABASE_AVAILABLE:
    try:
        if SUPABASE_URL and SUPABASE_ANON_KEY and supabase:
            dao_factory = DAOFactory(supabase)
            print("✅ Supabase client and DAO factory initialized successfully")
        else:
            print("Warning: Supabase credentials not found or supabase client not available")
    except Exception as e:
        print(f"Warning: Could not initialize Supabase: {e}")

# FastAPI app
app = FastAPI(
    title="CreAItion Simple API",
    version="1.0.0",
    description="Simple AI-powered story generation API"
)

# CORS middleware - Permissive for local demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_all_story_titles():
    """Get all story titles from database"""
    if not dao_factory:
        return set()
    
    try:
        story_dao = dao_factory.get_story_dao()
        # Get all stories from database and extract titles
        all_stories = story_dao.get_all_stories()
        return {story.title.lower() for story in all_stories}
    except Exception as e:
        print(f"Error fetching story titles from database: {e}")
        return set()

# Pydantic models
class SimpleStoryRequest(BaseModel):
    """Simple story request for NewStory scene - minimal fields only"""
    title: str
    nb_scenes: int = 4
    nb_chars: int = 2
    story_mode: Optional[str] = None  # Made optional
    user_email: str  # Used to lookup user_id from users table
    cover_image_url: Optional[str] = None
    cover_image_name: Optional[str] = None
    background_story: Optional[str] = None  # Added background_story field

class StoryRequest(BaseModel):
    """Full story request for AI generation - includes all Story class attributes"""
    story_id: Optional[str] = None  # Add story_id to identify existing story
    title: str
    nb_scenes: int = 4
    nb_chars: int = 2
    story_mode: str
    user_id: Optional[str] = None
    cover_image_url: Optional[str] = None
    cover_image_name: Optional[str] = None
    background_story: str = ""
    future_story: str = ""
    characters: List[Dict[str, Any]] = []

class CharacterRequest(BaseModel):
    name: str
    desc: str
    image_url: Optional[str] = None

class StoryResponse(BaseModel):
    success: bool
    story_id: Optional[str] = None
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

class GenerateImagesRequest(BaseModel):
    story_id: str

class CreateUserRequest(BaseModel):
    username: str
    email: str
    credits: int = 999

class UpdateCreditsRequest(BaseModel):
    credits: int

# API Routes

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "CreAItion Simple API",
        "version": "1.0.0",
        "status": "running",
        "services": {
            "supabase": supabase is not None,
            "gemini": gemini_client is not None,
            "ai_modules": AI_MODULES_AVAILABLE
        },
        "endpoints": [
            "/api/stories/generate",
            "/api/characters/upload",
            "/api/stories/{story_id}/cover/upload",
            "/api/stories/{story_id}/characters/upload", 
            "/api/stories/{story_id}/characters",
            "/api/stories/{story_id}",
            "/api/stories/generate-story",
            "/api/stories/generate-images",
            "/health",
            "/demo/titles",
            "/demo/clear-titles"
        ]
    }

@app.post("/api/stories/generate-story")
async def generate_story_only(request: StoryRequest):
    """
    Generate only the future story using AI, update characters with analysis
    Returns the generated story for user approval
    """
    try:
        # Check if AI modules are available
        if not AI_MODULES_AVAILABLE or not gemini_client:
            return {
                "success": False,
                "error": "AI modules or Gemini client not available"
            }
        
        # Check if DAO factory is available
        if not dao_factory:
            return {
                "success": False,
                "error": "Database not available"
            }
        
        # Get existing story from database
        story_dao = dao_factory.get_story_dao()
        story = None
        
        if request.story_id:
            story = story_dao.get_story(request.story_id)
        
        if not story:
            # If story doesn't exist, create a new one
            story = Story(
                user_id=request.user_id,
                title=request.title,
                nb_scenes=request.nb_scenes,
                nb_chars=request.nb_chars,
                story_mode=request.story_mode,
                cover_image_url=request.cover_image_url,
                cover_image_name=request.cover_image_name
            )
            story.id = story_dao.create_story(story)
        
        # Update the background story
        story.background_story = request.background_story if request.background_story else f"A {request.story_mode} story with {request.nb_chars} characters spanning {request.nb_scenes} scenes."
        
        # Set updated_at timestamp
        from datetime import datetime
        story.updated_at = datetime.utcnow()
        
        # Save the updated story
        story_dao.update_story(story)
        
        # Convert character data to User_Character objects and save to DB
        characters = []
        character_dao = dao_factory.get_character_dao()
        
        for char_data in request.characters:
            if char_data.get("image_url"):
                character = User_Character(
                    story.id,  # story_id
                    char_data["image_url"],  # image_url
                    char_data.get("image_name", ""),  # image_name  
                    char_data["name"], 
                    char_data["description"]
                )
                characters.append(character)
                
                # Save character to database
                character_dao.create_character(character, story.id)
        
        # Generate story and analysis using AI
        print(f"🎭 Generating story for: {request.title}")
        analysis, scenes_paragraph, scenes_list = generate_narrative_scenes(
            gemini_client, 
            characters, 
            story.background_story, 
            request.nb_scenes
        )
        
        character_dao.update_characters_analysis(characters)
        scene_dao = dao_factory.get_scene_dao()
        
        # Save the scenes_paragraph to the story
        story.scenes_paragraph = scenes_paragraph
        story_dao.update_story(story)
        
        # Delete existing scenes before creating new ones to avoid constraint violations
        scene_dao.delete_story_scenes(story.id)
        
        # Save each scene to the database
        saved_scenes = []
        for scene in scenes_list:
            scene_id = scene_dao.create_scene(scene, story.id, scene.scene_number)
            if scene_id:
                saved_scenes.append({
                    "scene_id": scene_id,
                    "title": scene.title,
                    "scene_number": scene.scene_number
                })
        
        # Update story status to indicate scenes are generated
        story_dao.update_story_complete(story)
        
        return {
            "success": True,
            "story_id": story.id,
            "title": request.title,
            "scenes": saved_scenes,
            "scenes_paragraph": scenes_paragraph,
            "analysis": analysis,
            "total_scenes": len(saved_scenes),
            "status": "story_generated",
            "message": "Story and scenes generated successfully! Click the green tick to generate images."
        }
        
    except Exception as e:
        print(f"Error in generate_story_only: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@app.post("/api/stories/generate-images")
async def generate_story_images(request: GenerateImagesRequest):
    try:
        # Check if AI modules are available
        if not AI_MODULES_AVAILABLE or not gemini_client:
            return {
                "success": False,
                "error": "AI modules or Gemini client not available"
            }
        
        # Check if DAO factory is available
        if not dao_factory:
            return {
                "success": False,
                "error": "Database not available"
            }
        
        # Get DAOs
        story_dao = dao_factory.get_story_dao()
        character_dao = dao_factory.get_character_dao()
        scene_dao = dao_factory.get_scene_dao()
        
        # Get story from database
        story = story_dao.get_story(request.story_id)
        if not story:
            return {
                "success": False,
                "error": "Story not found"
            }
        
        # Get characters for this story
        characters = character_dao.get_story_characters(request.story_id)
        
        story_title = story.title
        scenes_paragraph = story.scenes_paragraph
        
        if not scenes_paragraph:
            return {
                "success": False,
                "error": "Story must be generated first before creating images"
            }
        
        # Get scenes from database (scenes were created in generate_story_only)
        print(f"🎬 Getting scenes from database for story: {story.title}")
        scenes = scene_dao.get_story_scenes(request.story_id)
        
        if not scenes:
            return {
                "success": False,
                "error": "No scenes found for this story. Please generate the story first."
            }
        
        print(f"💾 Found {len(scenes)} scenes in database")
        
        # Generate images with real-time database updates
        try:
            print(f"🎨 Generating images for story: {story.title}")
            generate_images_with_updates(gemini_client, story_title, characters, scenes, scene_dao, request.story_id)
        except Exception as image_error:
            print(f"Image generation failed: {image_error}")
            return {
                "success": False,
                "error": f"Image generation failed: {str(image_error)}"
            }
        
        # Mark story as completed and return results
        story_dao.update_story_complete(story)
        
        # Get updated scenes from database to return
        updated_scenes = scene_dao.get_story_scenes(request.story_id)
        scenes_created = []
        for scene in updated_scenes:
            scenes_created.append({
                "scene_number": scene.scene_number,
                "title": scene.title,
                "image_url": scene.image_url                
            })
        
        return {
            "success": True,
            "story_id": request.story_id,
            "title": story.title,
            "scenes": scenes_created,
            "total_scenes": len(scenes_created),
            "status": "completed",
            "message": "Story images generated and saved successfully!"
        }
        
    except Exception as e:
        print(f"Error in generate_story_images: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@app.post("/api/stories/generate", response_model=StoryResponse)
async def generate_story_simple(request: SimpleStoryRequest, background_tasks: BackgroundTasks):
    """
    Simple story generation - just creates the story record and returns immediately
    """
    try:
        print(f"Received story request: {request}")
        
        # Validate required fields
        if not request.title or not request.title.strip():
            return StoryResponse(
                success=False,
                status="error",
                message="Title is required and cannot be empty"
            )
        
        # Check if story with same title already exists
        existing_titles = get_all_story_titles()
        if request.title.lower() in existing_titles:
            return StoryResponse(
                success=False,
                status="error",
                message=f"A story with the title '{request.title}' already exists. Please choose a different title."
            )
        
        story_id = str(uuid.uuid4())
        
        # Look up user by email to get database user ID
        if not request.user_email or not request.user_email.strip():
            return StoryResponse(
                success=False,
                status="error", 
                message="User email is required"
            )
        
        # Get user from database using email
        user_dao = dao_factory.get_user_dao()
        user = user_dao.get_user_by_email(request.user_email)
        if not user:
            return StoryResponse(
                success=False,
                status="error",
                message="User not found. Please make sure you are logged in."
            )
        
        # Save basic story record to database if available
        if supabase:
            try:
                initial_data = {
                    "id": story_id,
                    "user_id": str(user.id),  # Only store user_id as foreign key
                    "title": request.title,
                    "story_mode": request.story_mode or "",  # Handle None values
                    "nb_scenes": request.nb_scenes,
                    "nb_chars": request.nb_chars,
                    "cover_image_url": request.cover_image_url,
                    "cover_image_name": request.cover_image_name,
                    "status": "created",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                result = supabase.table("stories").insert(initial_data).execute()
                if not result.data:
                    print("Warning: Failed to create story record in database")
                    return StoryResponse(
                        success=False,
                        status="error",
                        message="Failed to create story record in database"
                    )
            except Exception as db_error:
                print(f"Database error: {db_error}")
                return StoryResponse(
                    success=False,
                    status="error",
                    message=f"Database error: {str(db_error)}"
                )
        
        return StoryResponse(
            success=True,
            story_id=story_id,
            status="created",
            message="Story created successfully. Use /api/stories/generate-story to generate story content."
        )
        
    except Exception as e:
        print(f"Error in generate_story_simple: {str(e)}")
        return StoryResponse(
            success=False,
            status="error",
            message=f"Internal server error: {str(e)}"
        )

@app.post("/api/characters/upload")
async def upload_character_image(
    file: UploadFile = File(...),
    name: str = None,
    description: str = None
):
    """Upload character image to Supabase storage"""
    try:
        # Read file content
        content = await file.read()
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"character_{uuid.uuid4()}{file_extension}"
        
        # Upload to Supabase storage
        image_url = upload_to_supabase_storage(content, unique_filename, ASSETS_FOLDER)
        
        character_data = {
            "name": name or "Unknown Character",
            "description": description or "",
            "image_url": image_url
        }
        
        return {
            "success": True,
            "character": character_data,
            "image_url": image_url,
            "message": "Character image uploaded successfully to Supabase storage"
        }
            
    except Exception as e:
        print(f"Error uploading character image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stories/{story_id}/cover/upload")
async def upload_story_cover(
    story_id: str,
    file: UploadFile = File(...)
):
    """Upload story cover image to Supabase storage"""
    try:
        print(f"📸 Cover upload received - story_id: '{story_id}', filename: '{file.filename}'")
        
        # Read file content
        content = await file.read()
        
        # Generate filename based on story ID and original file extension
        file_extension = Path(file.filename).suffix.lower()
        # Ensure we have a valid extension
        if not file_extension:
            file_extension = '.jpg'  # Default to .jpg if no extension
        
        filename = f"story_{story_id}{file_extension}"
        
        print(f"📁 Generated filename: '{filename}'")
        
        # Upload to Supabase storage
        image_url = upload_to_supabase_storage(content, filename, ASSETS_FOLDER)
        
        print(f"✅ Upload successful - URL: {image_url}")
        
        return {
            "success": True,
            "image_url": image_url,
            "filename": filename,
            "message": "Story cover uploaded successfully to Supabase storage"
        }
            
    except Exception as e:
        print(f"Error uploading story cover: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stories/{story_id}/characters/upload")
async def upload_story_character(
    story_id: str,
    file: UploadFile = File(...),
    character_index: int = 0,
    name: str = None,
    description: str = None
):
    """Upload character image for a specific story to Supabase storage"""
    try:
        # Read file content
        content = await file.read()
        
        # Generate filename based on character index
        file_extension = Path(file.filename).suffix
        filename = f"char_{character_index}{file_extension}"
        
        # Upload to Supabase storage
        image_url = upload_to_supabase_storage(content, filename, ASSETS_FOLDER)
        
        character_data = {
            "name": name or f"Character {character_index + 1}",
            "description": description or "",
            "image_url": image_url,
            "filename": filename
        }
        
        return {
            "success": True,
            "character": character_data,
            "image_url": image_url,
            "filename": filename,
            "message": "Character image uploaded successfully to Supabase storage"
        }
            
    except Exception as e:
        print(f"Error uploading character image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stories/{story_id}/characters")
async def save_story_characters(story_id: str, request: dict):
    """Save/update characters for a specific story"""
    if not dao_factory:
        return {
            "success": False,
            "message": "Database not available"
        }
    
    try:
        characters_data = request.get("characters", [])
        if not characters_data:
            return {
                "success": False,
                "message": "No characters provided"
            }
        print(characters_data)
        character_dao = dao_factory.get_character_dao()
        saved_characters = []
        
        # Get existing characters for this story
        existing_characters = character_dao.get_story_characters(story_id)
        existing_char_map = {char.name: char for char in existing_characters}
        for char_data in characters_data:
            name = char_data.get("name", "").strip()
            if not name:
                continue
                
            # Create User_Character object
            character = User_Character(
                story_id=story_id,
                image_url=char_data.get("image_url"),
                image_name=char_data.get("image_name"),
                name=name,
                description=char_data.get("description", "")
            )
            print("instance : ", character)
            # Check if character already exists
            if name in existing_char_map:
                # Update existing character
                existing_char = existing_char_map[name]
                character.id = existing_char.id
                success = character_dao.update_character(character)
                if success:
                    saved_characters.append({
                        "id": character.id,
                        "name": character.name,
                        "action": "updated"
                    })
            else:
                # Create new character
                char_id = character_dao.create_character(character, story_id)
                if char_id:
                    saved_characters.append({
                        "id": char_id,
                        "name": character.name,
                        "action": "created"
                    })
        
        return {
            "success": True,
            "message": f"Successfully processed {len(saved_characters)} characters",
            "characters": saved_characters
        }
        
    except Exception as e:
        print(f"Error saving story characters: {e}")
        return {
            "success": False,
            "message": f"Error saving characters: {str(e)}"
        }

@app.get("/api/stories/{story_id}")
async def get_story(story_id: str):
    """Get story details using DAO pattern"""
    if not dao_factory:
        return {
            "success": True,
            "story": {
                "id": story_id,
                "title": "Sample Story",
                "status": "generating",
                "background_story": "Your story is being generated...",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "nb_scenes": 5
            }
        }
    
    try:
        # Get DAOs
        story_dao = dao_factory.get_story_dao()
        character_dao = dao_factory.get_character_dao()
        scene_dao = dao_factory.get_scene_dao()
        
        # Get story
        story = story_dao.get_story(story_id)
        
        if story:
            # Get characters and scenes
            characters = character_dao.get_story_characters(story_id)
            scenes = scene_dao.get_story_scenes(story_id)
            
            print(f"📖 Retrieved {len(scenes)} scenes for story {story_id}")
            for scene in scenes:
                print(f"   Scene {scene.scene_number}: image_url = '{scene.image_url}'")
            
            # Convert Story object to dictionary for JSON serialization
            story_dict = {
                "id": story.id,
                "user_id": story.user_id,
                "title": story.title,
                "nb_scenes": story.nb_scenes,
                "nb_chars": story.nb_chars,
                "story_mode": story.story_mode,
                "cover_image_url": story.cover_image_url,
                "cover_image_name": story.cover_image_name,
                "background_story": story.background_story,
                "future_story": story.future_story,
                "scenes_paragraph": getattr(story, "scenes_paragraph", ""),  # Include scenes_paragraph
                "created_at": story.created_at,
                "updated_at": story.updated_at,
                "status": "completed"  # Add status field
            }
            
            # Convert User_Character objects to dictionaries for JSON serialization
            characters_dict = []
            for char in characters:
                char_dict = {
                    "id": char.id,
                    "name": char.name,
                    "description": char.description,
                    "image_url": char.image_url,  # Use image_url consistently
                    "image_name": char.image_name,  # Include image_name as well
                    "analysis": getattr(char, "analysis", "")
                }
                characters_dict.append(char_dict)
            
            # Convert scene objects to dictionaries for JSON serialization
            scenes_dict = []
            for scene in scenes:
                scene_dict = {
                    "id": scene.id,
                    "title": scene.title,
                    "narrative_text": scene.narrative_text,
                    "scene_number": scene.scene_number,
                    "image_prompt": scene.image_prompt,
                    "image_url": scene.image_url,
                    "paragraph": scene.paragraph
                }
                scenes_dict.append(scene_dict)
            
            # Add characters and scenes to story data
            story_dict["characters"] = characters_dict
            story_dict["scenes"] = scenes_dict
            
            return {
                "success": True,
                "story": story_dict
            }
        else:
            return {
                "success": True,
                "story": {
                    "id": story_id,
                    "title": "Generated Story",
                    "status": "not_found",
                    "background_story": "Story not found in database",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "nb_scenes": 5
                }
            }
            
    except Exception as e:
        print(f"Error fetching story: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.put("/api/stories/{story_id}")
async def update_story(story_id: str, request: SimpleStoryRequest):
    """Update story details using DAO pattern"""
    if not dao_factory:
        return StoryResponse(
            success=False,
            status="error",
            message="Database not available"
        )
    
    try:
        """
        # Validate required fields
        if not request.title or not request.title.strip():
            return StoryResponse(
                success=False,
                status="error",
                message="Title is required and cannot be empty"
            )
        """    
        # Look up user by email to get database user ID
        if not request.user_email or not request.user_email.strip():
            return StoryResponse(
                success=False,
                status="error", 
                message="User email is required"
            )
        
        # Get user from database using email
        user_dao = dao_factory.get_user_dao()
        user = user_dao.get_user_by_email(request.user_email)
        if not user:
            return StoryResponse(
                success=False,
                status="error",
                message="User not found. Please make sure you are logged in."
            )
        
        # Get existing story to update
        story_dao = dao_factory.get_story_dao()
        existing_story = story_dao.get_story(story_id)
        if not existing_story:
            return StoryResponse(
                success=False,
                status="error",
                message="Story not found"
            )
        
        # Update story attributes
        existing_story.title = request.title
        existing_story.nb_scenes = request.nb_scenes
        existing_story.nb_chars = request.nb_chars
        existing_story.story_mode = request.story_mode or ""  # Handle None values
        existing_story.cover_image_url = request.cover_image_url
        existing_story.cover_image_name = request.cover_image_name
        existing_story.updated_at = datetime.utcnow()
        
        # Update background story if provided
        if request.background_story is not None:
            existing_story.background_story = request.background_story
        # Update story in database
        updated_story_id = story_dao.update_story(existing_story)
        
        if updated_story_id:
            return StoryResponse(
                success=True,
                story_id=story_id,
                status="updated",
                message="Story updated successfully"
            )
        else:
            return StoryResponse(
                success=False,
                status="error",
                message="Failed to update story in database"
            )
            
    except Exception as e:
        print(f"Error updating story: {e}")
        return StoryResponse(
            success=False,
            status="error",
            message=f"Error updating story: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "supabase": supabase is not None,
            "gemini": gemini_client is not None,
            "ai_modules": AI_MODULES_AVAILABLE
        }
    }

@app.post("/api/demo/clear-titles")
async def clear_demo_titles():
    """Clear all story titles from database"""
    try:
        # Delete all stories from the database
        result = supabase.table("stories").delete().neq("id", "").execute()
        return {
            "success": True,
            "message": "All story titles cleared from database",
            "deleted_count": len(result.data) if result.data else 0
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error clearing titles: {str(e)}"
        }

@app.get("/api/demo/titles")
async def get_demo_titles():
    """Get all story titles from database"""
    try:
        titles = get_all_story_titles()
        return {
            "success": True,
            "titles": list(titles),
            "count": len(titles)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error fetching titles: {str(e)}",
            "titles": [],
            "count": 0
        }


# User Management Endpoints
@app.get("/api/user/stories")
async def get_user_stories(user_id: Optional[str] = None, user_email: Optional[str] = None):
    """Get all stories for a user by user_id or user_email"""
    try:
        if not dao_factory:
            return {
                "success": False,
                "message": "Database not available"
            }
        
        user_dao = dao_factory.get_user_dao()
        story_dao = dao_factory.get_story_dao()
        
        # Get user by ID or email
        user = None
        if user_email:
            user = user_dao.get_user_by_email(user_email)
        elif user_id:
            user = user_dao.get_user(user_id)
        
        if not user:
            return {
                "success": False,
                "message": "User not found"
            }
        
        # Get user's stories
        stories = story_dao.get_user_stories(str(user.id))
        
        # Convert Story objects to dictionaries for JSON serialization
        stories_dict = []
        for story in stories:
            story_dict = {
                "id": story.id,
                "title": story.title,
                # "status": "completed" if story.future_story else "created",
                "status": story.status,
                "cover_image_url": story.cover_image_url,
                "created_at": story.created_at.isoformat() if hasattr(story.created_at, 'isoformat') else story.created_at,
                "updated_at": story.updated_at.isoformat() if hasattr(story.updated_at, 'isoformat') else story.updated_at,
                "nb_scenes": story.nb_scenes,
                "nb_chars": story.nb_chars,
                "story_mode": story.story_mode
            }
            stories_dict.append(story_dict)
        
        return {
            "success": True,
            "stories": stories_dict
        }
        
    except Exception as e:
        print(f"Error fetching user stories: {e}")
        return {
            "success": False,
            "message": f"Error fetching stories: {str(e)}"
        }

@app.get("/api/users/email/{email}")
async def get_user_by_email(email: str):
    """Get user data by email address"""
    try:
        user_dao = dao_factory.get_user_dao()
        user = user_dao.get_user_by_email(email)
        
        if user:
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "credits": user.credits
                }
            }
        else:
            return {
                "success": False,
                "message": "User not found"
            }
    except Exception as e:
        print(f"Error fetching user: {e}")
        return {
            "success": False,
            "message": f"Error fetching user: {str(e)}"
        }


@app.post("/api/users/create")
async def create_user(request: CreateUserRequest):
    """Create a new user in the database"""
    try:
        user_dao = dao_factory.get_user_dao()
        
        # Check if user already exists
        existing_user = user_dao.get_user_by_email(request.email)
        if existing_user:
            return {
                "success": True,
                "user": {
                    "id": existing_user.id,
                    "username": existing_user.username,
                    "email": existing_user.email,
                    "credits": existing_user.credits
                },
                "message": "User already exists"
            }
        
        # Create new User object
        user = User(
            username=request.username,
            email=request.email,
            credits=request.credits
        )
        
        user_id = user_dao.create_user(user)
        
        if user_id:
            # Get the created user data
            created_user = user_dao.get_user_by_email(request.email)
            return {
                "success": True,
                "user": {
                    "id": created_user.id,
                    "username": created_user.username,
                    "email": created_user.email,
                    "credits": created_user.credits
                }
            }
        else:
            return {
                "success": False,
                "message": "Failed to create user"
            }
    except Exception as e:
        print(f"Error creating user: {e}")
        return {
            "success": False,
            "message": f"Error creating user: {str(e)}"
        }


@app.post("/api/users/email/{email}/credits")
async def update_user_credits(email: str, request: UpdateCreditsRequest):
    """Update user credits by email"""
    try:
        user_dao = dao_factory.get_user_dao()
        success = user_dao.update_user_credits(email, request.credits)
        
        if success:
            return {
                "success": True,
                "message": "Credits updated successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to update credits"
            }
    except Exception as e:
        print(f"Error updating credits: {e}")
        return {
            "success": False,
            "message": f"Error updating credits: {str(e)}"
        }


@app.get("/api/stories/{story_id}/download")
async def download_story_package(story_id: str):
    """Download a complete story package as a ZIP file containing images and story text"""
    try:
        if not dao_factory:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Get story data
        story_dao = dao_factory.get_story_dao()
        story_data = story_dao.get_story(story_id)
        
        if not story_data:
            raise HTTPException(status_code=404, detail="Story not found")
        
        # Create a temporary directory for organizing files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create story text file
            story_title = story_data.title or 'Untitled Story'
            safe_title = "".join(c for c in story_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            
            story_content = f"""STORY TITLE: {story_title}\n

                BACKGROUND STORY:
                {story_data.background_story or 'No background story provided.'}

                STORY NARRATIVE:
                {story_data.scenes_paragraph or 'No narrative available.'}

                STORY DETAILS:
                - Number of Scenes: {story_data.nb_scenes or 'Unknown'}
                - Number of Characters: {story_data.nb_chars or 'Unknown'}
                - Story Mode: {story_data.story_mode or 'Unknown'}
                - Created: {story_data.created_at or 'Unknown'}
            """
            
            # Write story text file
            story_file_path = temp_path / f"{safe_title}_story.txt"
            with open(story_file_path, 'w', encoding='utf-8') as f:
                f.write(story_content)
            
            # Download scene images
            scene_dao = dao_factory.get_scene_dao()
            scenes = scene_dao.get_story_scenes(story_id)
            
            downloaded_files = [story_file_path]
            
            if scenes:
                # Create images directory
                images_dir = temp_path / "images"
                images_dir.mkdir(exist_ok=True)
                
                for scene in scenes:
                    if scene.image_url:
                        try:
                            # Download the image
                            response = requests.get(scene.image_url, timeout=30)
                            response.raise_for_status()
                            
                            # Determine file extension from URL or content type
                            scene_number = scene.scene_number or 'unknown'
                            scene_title = scene.title or f'Scene_{scene_number}'
                            safe_scene_title = "".join(c for c in scene_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                            
                            # Try to get extension from URL
                            url_path = scene.image_url.split('?')[0]  # Remove query parameters
                            if '.' in url_path:
                                extension = url_path.split('.')[-1].lower()
                                if extension not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                                    extension = 'jpg'  # Default fallback
                            else:
                                extension = 'jpg'  # Default fallback
                            
                            image_filename = f"scene_{scene_number:02d}_{safe_scene_title}.{extension}"
                            image_path = images_dir / image_filename
                            
                            # Save the image
                            with open(image_path, 'wb') as img_file:
                                img_file.write(response.content)
                            
                            downloaded_files.append(image_path)
                            print(f"✅ Downloaded scene image: {image_filename}")
                            
                        except Exception as e:
                            print(f"⚠️ Failed to download image for scene {scene.scene_number or 'unknown'}: {e}")
                            continue
            
            # Download cover image if available
            if story_data.cover_image_url:
                try:
                    response = requests.get(story_data.cover_image_url, timeout=30)
                    response.raise_for_status()
                    
                    # Get extension for cover image
                    url_path = story_data.cover_image_url.split('?')[0]
                    if '.' in url_path:
                        extension = url_path.split('.')[-1].lower()
                        if extension not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                            extension = 'jpg'
                    else:
                        extension = 'jpg'
                    
                    cover_filename = f"cover_image.{extension}"
                    cover_path = temp_path / cover_filename
                    
                    with open(cover_path, 'wb') as cover_file:
                        cover_file.write(response.content)
                    
                    downloaded_files.append(cover_path)
                    print(f"✅ Downloaded cover image: {cover_filename}")
                    
                except Exception as e:
                    print(f"⚠️ Failed to download cover image: {e}")
            
            # Create ZIP file in memory
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_path in downloaded_files:
                    # Get relative path within temp directory
                    arcname = file_path.relative_to(temp_path)
                    zip_file.write(file_path, arcname)
            
            zip_buffer.seek(0)
            
            # Create filename for ZIP
            zip_filename = f"{safe_title}_story_package.zip"
            
            # Return ZIP file as streaming response
            return StreamingResponse(
                io.BytesIO(zip_buffer.read()),
                media_type="application/zip",
                headers={"Content-Disposition": f"attachment; filename={zip_filename}"}
            )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating story package: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create story package: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting CreAItion DAO API server...")
    print("📍 This version uses DAO pattern with Story, Character, and scene classes")
    print("🔧 Endpoints:")
    print("   - POST /api/stories/generate (simple record creation)")
    print("   - POST /api/stories/generate-story (AI story generation)")
    print("   - POST /api/stories/generate-images (AI image generation)")
    print("   - POST /api/characters/upload")
    print("   - GET /api/stories/{story_id}")
    print("   - GET /api/stories/{story_id}/download (download story package)")
    print("   - PUT /api/stories/{story_id} (update story)")
    print("   - GET /health")
    uvicorn.run("fast_api:app", host="0.0.0.0", port=8002, reload=True)

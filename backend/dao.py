"""
Data Access Object (DAO) pattern implementation for CreAItion
Handles all database operations for Story, User_Character, and scene entities
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from supabase import Client
from User_Character import User_Character
from Story import Story
from Scene import Scene
from User import User


class StoryDAO:
    def __init__(self, supabase_client: Client):
        self.db = supabase_client
    
    def create_story(self, story: Story) -> str:
        """Create a new story in the database"""
        try:
            story_id = str(uuid.uuid4())
            story.id = story_id  # Set the ID on the story object
            story_data = {
                "id": story_id,
                "user_id": story.user_id,
                "title": story.title,
                "nb_scenes": story.nb_scenes,
                "nb_chars": story.nb_chars,
                "story_mode": story.story_mode,
                "cover_img_url": story.cover_img_url,
                "cover_img_name": story.cover_img_name,
                "status": "created",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.db.table("stories").insert(story_data).execute()
            if result.data:
                return story_id
            return None
        except Exception as e:
            print(f"Error creating story: {e}")
            return None
    
    def update_story_future_story(self, story: Story) -> bool:
        """Update story with the generated future story"""
        try:
            update_data = {
                "future_story": story.future_story,
                "status": "story_generated",
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.db.table("stories").update(update_data).eq("id", story.id).execute()
            return bool(result.data)
        except Exception as e:
            print(f"Error updating story future_story: {e}")
            return False
    
    def update_story_complete(self, story: Story) -> bool:
        """Mark story as complete with images"""
        try:
            update_data = {
                "status": "completed",
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.db.table("stories").update(update_data).eq("id", story.id).execute()
            return bool(result.data)
        except Exception as e:
            print(f"Error updating story to complete: {e}")
            return False
    
    def update_story(self, story: Story) -> str:
        """Update story with new details"""
        try:
            update_data = {
                "title": story.title,
                "nb_scenes": story.nb_scenes,
                "nb_chars": story.nb_chars,
                "story_mode": story.story_mode,
                "cover_img_url": story.cover_img_url,
                "cover_img_name": story.cover_img_name,
                "background_story": story.bg_story,
                "updated_at": story.updated_at.isoformat() if story.updated_at else None
            }
            
            result = self.db.table("stories").update(update_data).eq("id", story.id).execute()
            if result.data:
                return str(story.id)
            return None
        except Exception as e:
            print(f"Error updating story: {e}")
            return None
    
    def get_story(self, story_id: str) -> Optional[Story]:
        """Get story by ID"""
        try:
            result = self.db.table("stories")\
                .select("*")\
                .eq("id", story_id)\
                .execute()
            
            if result.data:
                story_data = result.data[0]
                story = Story(
                    user_id=story_data.get("user_id", ""),
                    title=story_data.get("title", ""),
                    nb_scenes=story_data.get("nb_scenes", 0),
                    nb_chars=story_data.get("nb_chars", 0),
                    story_mode=story_data.get("story_mode", ""),
                    cover_img_url=story_data.get("cover_img_url", ""),
                    cover_img_name=story_data.get("cover_img_name", "")
                )
                story.id = story_data.get("id")
                story.bg_story = story_data.get("bg_story", "")
                story.future_story = story_data.get("future_story", "")
                story.created_at = story_data.get("created_at")
                story.updated_at = story_data.get("updated_at")
                return story
            return None
        except Exception as e:
            print(f"Error fetching story: {e}")
            return None
    
    def get_user_stories(self, user_id: str) -> List[Story]:
        """Get all stories for a user"""
        try:
            result = self.db.table("stories")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .execute()
            
            stories = []
            if result.data:
                for story_data in result.data:
                    story = Story(
                        user_id=story_data.get("user_id", ""),
                        title=story_data.get("title", ""),
                        nb_scenes=story_data.get("nb_scenes", 0),
                        nb_chars=story_data.get("nb_chars", 0),
                        story_mode=story_data.get("story_mode", ""),
                        cover_img_url=story_data.get("cover_img_url", ""),
                        cover_img_name=story_data.get("cover_img_name", "")
                    )
                    story.id = story_data.get("id")
                    story.bg_story = story_data.get("bg_story", "")
                    story.future_story = story_data.get("future_story", "")
                    stories.append(story)
            
            return stories
        except Exception as e:
            print(f"Error fetching user stories: {e}")
            return []
    
    def get_all_stories(self) -> List[Story]:
        """Get all stories from all users"""
        try:
            result = self.db.table("stories")\
                .select("*")\
                .order("created_at", desc=True)\
                .execute()
            
            stories = []
            if result.data:
                for story_data in result.data:
                    story = Story(
                        user_id=story_data.get("user_id", ""),
                        title=story_data.get("title", ""),
                        nb_scenes=story_data.get("nb_scenes", 0),
                        nb_chars=story_data.get("nb_chars", 0),
                        story_mode=story_data.get("story_mode", ""),
                        cover_img_url=story_data.get("cover_img_url", ""),
                        cover_img_name=story_data.get("cover_img_name", "")
                    )
                    story.id = story_data.get("id")
                    story.bg_story = story_data.get("bg_story", "")
                    story.future_story = story_data.get("future_story", "")
                    stories.append(story)
            
            return stories
        except Exception as e:
            print(f"Error fetching all stories: {e}")
            return []


class CharacterDAO:
    def __init__(self, supabase_client: Client):
        self.db = supabase_client
    
    def create_character(self, character: User_Character, story_id: str) -> str:
        """Create a character and associate with story"""
        try:
            char_id = str(uuid.uuid4())
            character.id = char_id  # Set the ID on the character object
            # Use the story_id from the character object if available, otherwise use the parameter
            story_id_to_use = character.story_id if character.story_id else story_id
            char_data = {
                "id": char_id,
                "story_id": story_id_to_use,
                "name": character.name,
                "description": character.description,
                "img_path": character.img_url,  # Store img_url in img_path field
                "img_name": character.img_name,  # Store img_name in new field
                "analysis": character.analysis,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.db.table("user_characters").insert(char_data).execute()
            if result.data:
                return char_id
            return None
        except Exception as e:
            print(f"Error creating character: {e}")
            return None
    
    def update_character(self, character: User_Character) -> bool:
        """Update a single character"""
        try:
            update_data = {
                "story_id": character.story_id,  # Include story_id in updates
                "name": character.name,
                "description": character.description,
                "img_path": character.img_url,  # Store img_url in img_path field
                "img_name": character.img_name,  # Store img_name in new field
                "analysis": character.analysis,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.db.table("user_characters").update(update_data).eq("id", character.id).execute()
            return bool(result.data)
        except Exception as e:
            print(f"Error updating character: {e}")
            return False
    
    def update_characters(self, characters: List[User_Character]) -> bool:
        """Update multiple characters"""
        try:
            for character in characters:
                if not self.update_character(character):
                    return False
            return True
        except Exception as e:
            print(f"Error updating characters: {e}")
            return False
    
    def update_character_analysis(self, character: User_Character) -> bool:
        """Update character with AI analysis"""
        try:
            update_data = {
                "analysis": character.analysis,
                "updated_at": datetime.utcnow().isoformat()
            }
            result = self.db.table("user_characters").update(update_data).eq("id", character.id).execute()
            return bool(result.data)
        except Exception as e:
            print(f"Error updating character analysis: {e}")
            return False
    
    def update_characters_analysis(self, characters: List[User_Character]) -> bool:
        try:
            for character in characters:
                self.update_character_analysis(character)
        except Exception as e:
            print(f"Error updating characters analysis: {e}")
            return False
    
    def get_story_characters(self, story_id: str) -> List[User_Character]:
        """Get all characters for a story"""
        try:
            result = self.db.table("user_characters")\
                .select("*")\
                .eq("story_id", story_id)\
                .execute()
            
            characters = []
            if result.data:
                for char_data in result.data:
                    character = User_Character(
                        char_data.get("story_id", ""),  # story_id
                        char_data.get("img_path", ""),  # img_url
                        char_data.get("img_name", ""),  # img_name
                        char_data.get("name", ""),      # name
                        char_data.get("description", "")  # description
                    )
                    character.id = char_data.get("id")
                    # Add the analysis if it exists
                    if char_data.get("analysis"):
                        character.analysis = char_data.get("analysis")
                    characters.append(character)
            
            return characters
        except Exception as e:
            print(f"Error fetching story characters: {e}")
            return []

        

class SceneDAO:
    def __init__(self, supabase_client: Client):
        self.db = supabase_client
    
    def create_scene(self, scene: Scene, story_id: str, scene_number: int) -> str:
        """Create a scene for a story"""
        try:
            scene_id = str(uuid.uuid4())
            scene.id = scene_id  # Set the ID on the scene object
            scene_data = {
                "id": scene_id,
                "story_id": story_id,
                "scene_number": scene_number,
                "img_url": scene.img_url,
                "paragraph": scene.paragraph,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.db.table("scenes").insert(scene_data).execute()
            if result.data:
                return scene_id
            return None
        except Exception as e:
            print(f"Error creating scene: {e}")
            return None
    
    def get_story_scenes(self, story_id: str) -> List[Scene]:
        """Get all scenes for a story, ordered by scene number"""
        try:
            result = self.db.table("scenes")\
                .select("*")\
                .eq("story_id", story_id)\
                .order("scene_number")\
                .execute()
            
            scenes = []
            if result.data:
                for scene_data in result.data:
                    # Create a scene object with the available data
                    scene = scene(
                        title=scene_data.get("title", ""),
                        narrative_text=scene_data.get("paragraph", ""),
                        scene_nb=scene_data.get("scene_number", 0),
                        img_prompt=scene_data.get("img_prompt", "")
                    )
                    scene.id = scene_data.get("id")
                    scene.img_url = scene_data.get("img_url", "")
                    scene.paragraph = scene_data.get("paragraph", "")
                    scenes.append(scene)
            
            return scenes
        except Exception as e:
            print(f"Error fetching story scenes: {e}")
            return []


class UserDAO:
    def __init__(self, supabase_client: Client):
        self.db = supabase_client
    
    def create_user(self, user: User) -> str:
        """Create a new user in the database"""
        try:
            user_id = str(uuid.uuid4())
            user.id = user_id
            user_data = {
                "id": user_id,
                "username": user.username,
                "email": user.email,
                "credits": 999,  # Default 999 credits
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.db.table("users").insert(user_data).execute()
            return user_id if result.data else None
                
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        try:
            result = self.db.table("users")\
                .select("*")\
                .eq("email", email)\
                .execute()
            
            if result.data and len(result.data) > 0:
                user_data = result.data[0]
                user = User(
                    id=user_data.get("id"),
                    username=user_data.get("username"),
                    email=user_data.get("email"),
                    credits=user_data.get("credits", 999),
                    created_at=user_data.get("created_at"),
                    updated_at=user_data.get("updated_at")
                )
                return user
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    def update_user(self, user: User) -> bool:
        """Update user information"""
        try:
            update_data = {
                "username": user.username,
                "email": user.email,
                "credits": user.credits,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.db.table("users").update(update_data).eq("id", user.id).execute()
            return bool(result.data)
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    def update_user_credits(self, email: str, credits: int) -> bool:
        """Update user credits by email"""
        try:
            update_data = {
                "credits": credits,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.db.table("users").update(update_data).eq("email", email).execute()
            return bool(result.data)
        except Exception as e:
            print(f"Error updating user credits: {e}")
            return False


class DAOFactory:
    """Factory class to create DAO instances"""
    
    def __init__(self, supabase_client: Client):
        self.supabase_client = supabase_client
    
    def get_story_dao(self) -> StoryDAO:
        return StoryDAO(self.supabase_client)
    
    def get_character_dao(self) -> CharacterDAO:
        return CharacterDAO(self.supabase_client)
    
    def get_scene_dao(self) -> SceneDAO:
        return SceneDAO(self.supabase_client)
    
    def get_user_dao(self) -> UserDAO:
        return UserDAO(self.supabase_client)

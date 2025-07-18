from config import supabase, supabase_service, ASSETS_FOLDER, OUTPUT_FOLDER, BUCKET_NAME

# Helper functions for Supabase Storage
def upload_to_supabase_storage(file_content: bytes, file_name: str, folder: str = ASSETS_FOLDER) -> str:
    """Upload file to Supabase storage and return public URL"""
    try:
        # Use service client for storage operations to bypass RLS
        storage_client = supabase_service if supabase_service else supabase
        
        file_path = f"{folder.strip('/')}/{file_name}"
        
        # Upload file to Supabase storage with proper options
        result = storage_client.storage.from_(BUCKET_NAME).upload(
            file_path, 
            file_content,
            {"upsert": "true"}  # Use string value instead of boolean
        )
        
        if result:
            # Get public URL (can use either client for this)
            public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_path)
            return public_url
        else:
            raise Exception("Failed to upload to Supabase storage")
            
    except Exception as e:
        print(f"Error uploading to Supabase storage: {e}")
        raise e

def get_supabase_storage_url(file_name: str, folder: str = ASSETS_FOLDER) -> str:
    """Get public URL for a file in Supabase storage"""
    file_path = f"{folder}/{file_name}"
    return supabase.storage.from_(BUCKET_NAME).get_public_url(file_path)

def upload_generated_image_to_supabase(image_bytes: bytes, story_name: str, scene_number: int) -> str:
    """Upload generated scene image to Supabase storage and return public URL"""
    try:
        # Create safe filename
        safe_story_name = story_name.replace(" ", "_")
        filename = f"{safe_story_name}_{scene_number}.png"
        
        # Upload to output folder in Supabase storage
        image_url = upload_to_supabase_storage(image_bytes, filename, OUTPUT_FOLDER)
        
        print(f"✅ Uploaded scene image to Supabase: {filename}")
        return image_url
        
    except Exception as e:
        print(f"❌ Failed to upload scene image to Supabase: {e}")
        raise e

def download_image_from_supabase(image_url: str) -> bytes:
    """Download image from Supabase storage URL for processing"""
    try:
        import requests
        response = requests.get(image_url)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"❌ Failed to download image from Supabase: {e}")
        raise e

def save_temp_image_for_upload(image_url: str) -> str:
    """Download image from Supabase and save temporarily for Gemini upload"""
    try:
        import tempfile
        
        # Download image content
        image_content = download_image_from_supabase(image_url)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(image_content)
            return temp_file.name
            
    except Exception as e:
        print(f"❌ Failed to create temp file for image: {e}")
        raise e

def upload_story_cover_to_supabase(image_bytes: bytes, story_title: str, file_extension: str) -> str:
    """Upload story cover image to Supabase storage and return public URL"""
    try:
        # Create safe filename
        safe_title = story_title.replace(" ", "_").replace("/", "_")
        filename = f"{safe_title}{file_extension}"
        
        # Upload to assets folder in Supabase storage
        image_url = upload_to_supabase_storage(image_bytes, filename, ASSETS_FOLDER)
        
        print(f"✅ Uploaded story cover to Supabase: {filename}")
        return image_url
        
    except Exception as e:
        print(f"❌ Failed to upload story cover to Supabase: {e}")
        raise e

def upload_character_image_to_supabase(image_bytes: bytes, character_index: int, file_extension: str) -> str:
    """Upload character image to Supabase storage and return public URL"""
    try:
        # Create character filename
        filename = f"char_{character_index}{file_extension}"
        
        # Upload to assets folder in Supabase storage
        image_url = upload_to_supabase_storage(image_bytes, filename, ASSETS_FOLDER)
        
        print(f"✅ Uploaded character image to Supabase: {filename}")
        return image_url
        
    except Exception as e:
        print(f"❌ Failed to upload character image to Supabase: {e}")
        raise e

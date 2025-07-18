from datetime import datetime

class Story:
    def __init__(self, user_id, title, nb_scenes, nb_chars, story_mode, cover_image_url, cover_image_name):
        self.id = None  # Will be set when saved to database
        self.user_id = user_id
        self.title = title
        self.status = "created"  # Default status
        self.nb_scenes = nb_scenes
        self.nb_chars = nb_chars
        self.story_mode = story_mode
        self.cover_image_url = cover_image_url
        self.cover_image_name = cover_image_name
        self.chars = []
        self.background_story = ""
        self.future_story = ""
        self.scenes_paragraph = ""  # Add scenes_paragraph field to store the storyline
        self.scenes = []
        self.created_at = None  # Will be set when saved to database
        self.updated_at = None  # Will be set when updated
        
        
from datetime import datetime

class Story:
    def __init__(self, user_id, title, nb_scenes, nb_chars, story_mode, cover_img_url, cover_img_name):
        self.id = None  # Will be set when saved to database
        self.user_id = user_id
        self.title = title
        self.nb_scenes = nb_scenes
        self.nb_chars = nb_chars
        self.story_mode = story_mode
        self.cover_img_url = cover_img_url
        self.cover_img_name = cover_img_name
        self.chars = []
        self.bg_story = ""
        self.future_story = ""
        self.scenes = []
        self.created_at = None  # Will be set when saved to database
        self.updated_at = None  # Will be set when updated
        
        
class User_Character:
    def __init__(self, story_id, image_url, name, description):
        self.id = None  # Will be set when saved to database
        self.story_id = story_id
        self.image_url = image_url
        self.name = name
        self.description = description
        self.analysis = "" # Will be set when generate_narrative_scenes() called 
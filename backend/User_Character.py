class User_Character:
    def __init__(self, story_id, image_url, image_name, name, description):
        self.id = None  # Will be set when saved to database
        self.story_id = story_id
        self.image_url = image_url
        self.image_name = image_name
        self.name = name
        self.description = description
        self.analysis = "" # Will be set when generate_future_story() called 
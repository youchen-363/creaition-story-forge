class User_Character:
    def __init__(self, story_id, img_url, img_name, name, description):
        self.id = None  # Will be set when saved to database
        self.story_id = story_id
        self.img_url = img_url
        self.img_name = img_name
        self.name = name
        self.description = description
        self.analysis = "" # Will be set when generate_future_story() called 
class Scene:
    def __init__(self, title, narrative_text, scene_number, image_prompt):
        self.id = None  # Will be set when saved to database
        self.image_url = ""
        self.paragraph = ""
        self.title = title
        self.narrative_text = narrative_text
        self.scene_number = scene_number
        self.image_prompt = image_prompt
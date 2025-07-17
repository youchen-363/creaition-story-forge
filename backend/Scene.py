class Scene:
    def __init__(self, title, narrative_text, scene_nb, image_prompt):
        self.id = None  # Will be set when saved to database
        self.image_url = ""
        self.paragraph = ""
        self.title = title
        self.narrative_text = narrative_text
        self.scene_nb = scene_nb
        self.image_prompt = image_prompt
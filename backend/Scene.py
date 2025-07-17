class Scene:
    def __init__(self, title, narrative_text, scene_nb, img_prompt):
        self.id = None  # Will be set when saved to database
        self.img_url = ""
        self.paragraph = ""
        self.title = title
        self.narrative_text = narrative_text
        self.scene_nb = scene_nb
        self.img_prompt = img_prompt
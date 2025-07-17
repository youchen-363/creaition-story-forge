from google import genai 
from image_to_text import generate_narrative_scenes
from text_to_text import generate_scenes
from image_to_image import generate_images
import os
from dotenv import load_dotenv
from User_Character import User_Character
import datetime

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

char1 = User_Character("demo_story_1", "assets/joker.jpeg", "jocker.jpeg", "Dorry", "Dorry is a mysterious jester with a disturbing, split black and white face. He loves riddles and chaos, always appearing where he's least expected, leaving behind a chilling laugh. He's very theatrical.")
char2 = User_Character("demo_story_1", "assets/police.jpg", "police.jpg", "Matte", "Matte is a cop.")
chars = [char1, char2]

background_story = """
The city of Veridia was once known for its gleaming towers and vibrant arts scene, a beacon of progress. However, in recent months, a sinister shadow has fallen. A series of bizarre, highly theatrical crimes, dubbed the "Crimson Jesters," have terrorized the populace. These aren't just robberies; they're elaborate performances leaving behind cryptic clues and a distinct, unsettling calling card: a single, blood-red joker playing card. The police force, overwhelmed and under pressure, scrambles for answers, but the perpetrator always seems one step ahead, mocking their every move. Fear is slowly replacing freedom in Veridia's glittering streets.
"""
nb_scenes = 4

start_story = datetime.datetime.now()

analysis, scenes_para, scenes = generate_narrative_scenes(client, chars, background_story, nb_scenes)
print(analysis)
print(scenes_para)

end_story = datetime.datetime.now()
start = datetime.datetime.now()
images = generate_images(client, "Joker_officer", chars, scenes)
end = datetime.datetime.now()
print(images)
story_time = end_story - start_story
image_time = end - start
print(f'scenes: {story_time}')
print(f'image: {image_time}')
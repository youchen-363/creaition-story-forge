from google import genai 
from image_to_text import generate_future_story
from text_to_text import generate_scenes
from image_to_image import generate_images
import os
from dotenv import load_dotenv
from User_Character import User_Character
import datetime

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

char1 = User_Character("demo_story_1", "assets/jocker.jpeg", "jocker.jpeg", "Dorry", "He is a serial killer. He is born in Muar, Johor, Malaysia. He likes to kill people and be criminal. He enjoys the moment when a guy shouts and begs him to let him survive. He feels that he is the god in this way.")
char2 = User_Character("demo_story_1", "assets/police.jpg", "police.jpg", "Mathieu", "He is a police, keep the safety of Muar. He wants to catch Dorry but Dorry always escape from him. He won't endure the crimes.")
chars = [char1, char2]

background_story = """
In the quiet town of Muar, Johor, the shadows of fear and justice wage an unending war. Dorry, a cold-blooded serial killer who thrives on the desperation of his victims, stalks the streets with a twisted sense of divinity, leaving chaos in his wake. Opposing him is Mathieu, a relentless police officer sworn to protect the town’s fragile peace. For years, Mathieu has pursued Dorry through bloodstained alleys and sleepless nights, but the killer always slips away like a ghost. Their deadly game of cat and mouse has become the heartbeat of Muar — a battle between darkness and the last flicker of light.
"""
nb_scenes = 4

start_story = datetime.datetime.now()

analysis, future_story = generate_future_story(client, chars, background_story, nb_scenes)
print(analysis)
print(future_story)

end_story = datetime.datetime.now()

scenes = generate_scenes(client, 6, nb_scenes, analysis, future_story)
end_scene = datetime.datetime.now()

print(scenes)

image_paths = []
for char_data in chars:
    image_paths.append(char_data.image_path + "/" + char_data.image_name)

start = datetime.datetime.now()
images = generate_images(client, chars, scenes)
end = datetime.datetime.now()
print(images)
story_time = end_story - start_story
scene_time = end_scene - start_story
image_time = end - start
print(f'future story: {story_time}')
print(f'scenes: {scene_time}')
print(f'image: {image_time}')
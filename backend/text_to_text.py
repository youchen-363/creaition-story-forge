from google import genai
import json
import re
from Scene import Scene
from User_Character import User_Character

def generate_scenes(client: genai.Client, chars_data: User_Character, nb_scenes: int, story: str) -> list:
    analysis = []
    for char_data in chars_data:
        if char_data.analysis != "":
            analysis.append(char_data.analysis)
    analysis = "\n".join(analysis)
    prompt = f"""
    
    You are a highly skilled **Visual Narrative Creative Director and Prompt Engineer** for an AI image generation system. Your primary task is to transform a given future story into a dynamic visual novel, formatted as a sequence of scenes where **each scene consists of a single image on the left and a paragraph of text on the right.** The visual novel must not contain any inappropriate or NSFW content.

    ---
    ### Crucial Context for Consistency (Derived from prior analysis and MUST be used)

    -   **Character & Art Analysis (Raw String Input for Multiple Characters):**
        ```
        {analysis}
        ```
        *(**IMPORTANT:** This is a **long string** containing detailed textual analysis for multiple characters. You must parse and extract the individual character details from this string. For each character (e.g., "Dorry", "Mathieu"), identify their `character_name`, `character_description` (their role and key personality traits), `visual_characteristics` (physical appearance, clothing, unique features, art style nuances like line work, shading, specific color palette, texture, mood/atmosphere), and any `recurring_motifs`. **Ensure these extracted details are rigorously applied, depicting each character consistently (using their exact names and specific visual descriptions) and accurately reflecting their interactions as required by the story. Each character MUST appear visually at least once across all generated scenes.**)*

    ---
    ### Input for scene Generation

    -   **Future Story:** {story}
    -   **Number of scenes Desired:** {nb_scenes}

    ---
    ### Task for Each scene

    For each of the {nb_scenes} desired visual novel scenes:

    1.  **Determine scene Content (Multi-Character Focus):** Divide the given `Future Story` into {nb_scenes} logical segments, each representing a distinct scene. For each scene, identify the specific action, **explicitly state *which* characters are present (by their exact names as extracted from the analysis)**, describe their individual poses, expressions, and any necessary environmental details. Ensure character interactions, relative positioning, and emotional states are clearly defined, drawing directly from their analyzed personalities and visual traits. **Ensure that each character appears visually at least once throughout the entire set of {nb_scenes} scenes.**
    2.  **Generate Narrative Paragraph:** From the story segment, extract or synthesize a concise paragraph of narrative text (approx. 3-5 sentences) that describes the scene and any character actions or thoughts. This paragraph will be displayed separately to the right of the image. **Do NOT include any character speech within this paragraph; all speech should be presented as dialogue, not integrated into the main narrative paragraph.**
    3.  **Detailed Image Generation Prompt (for a single image representing the entire scene):** Generate a highly detailed, comprehensive text prompt (suitable for an AI like Imagen 4 or DALL-E 3) that describes the entire visual novel scene's image content. This prompt MUST rigorously ensure:
        * **Visual Content (Explicit Character Detailing):** Describe the specific action and environment for this scene's single image. **Crucially, for every character present in this scene, explicitly name them (e.g., "Dorry," "Mathieu") and then concisely describe their key visual characteristics and any relevant art style nuances (e.g., "Dorry with his split white and black jester face, unnerving grin, and sharp-pointed hat," "Mathieu in his dark blue police uniform, confident smile, and dark sunglasses").** Detail their pose, expression, relative positioning, and any essential environmental elements. **Do NOT include any text, speech bubbles, or captions within this image prompt. The image must be purely visual.** Ensure the narrative flows sequentially from one image to the next across all scenes, emphasizing character placement, interaction, and emotional arcs.
        * **Character Consistency Across scenes:** **Strictly maintain the consistent appearance and artistic style (including color palette, line work, shading, etc.) for each character across ALL generated scenes, referencing the details you extracted from the 'Character & Art Analysis' string.**
        * **Art Style Enforcement (Consistent Across All scenes):** Explicitly state the desired **overarching art style**, specific color palette, line work, shading, texture, and mood/atmosphere **derived from the combined 'ARTISTIC STYLE ANALYSIS' sections of all characters relevant to the story** (e.g., 'in the style of a gritty graphic novel with stark black, white, and red tones from Dorry, and vibrant urban comic book elements from Mathieu', 'with high-contrast colors and bold lines'). This style must apply uniformly across all scenes.
        * **Lighting & Atmosphere:** Detail the lighting and overall atmosphere for the entire scene's image, consistent with the characters' themes and the story's mood.

    ---
    ### Output Format

    Your final output MUST be a single JSON object structured as follows. Ensure all string values are properly escaped and the JSON is valid. You should generate exactly the 'Number of scenes Desired' as specified in the input.

    ```json
    {{
    "scenes": [
        {{
        "scene_number": 1,
        "scene_title": "[Brief, descriptive title for scene 1, mentioning key characters present, e.g., 'Mathieu's Grim Discovery']",
        "scene_narrative_text": "[Concise narrative paragraph for scene 1, 3-5 sentences, describing the scene and character actions without speech. Explicitly name primary characters involved, e.g., 'Mathieu, the seasoned detective, arrived at the desolate town square just as dawn broke. A gruesome discovery awaited him: a victim, chillingly displayed, with a single, twisted joker card pinned to their chest. The air hung heavy with a sense of dread and unanswered questions.']",
        "image_generation_prompt": "[Highly detailed text prompt for AI image generation, describing a *single image* that represents the entire scene. **Example based on your input: 'A gritty graphic novel style visual, with stark black, white, and red elements combined with vibrant urban comic book flair. Mathieu, in a dark blue police uniform with a confident yet grim expression beneath his sunglasses, inspects a victim displayed ominously in the center of Muar town square at dawn. A 'Joker' playing card, identical to Dorry's visual motifs, is prominently pinned to the victim's chest with a bloody dagger. The overall mood is ominous, challenging, and resolute. No text or speech bubbles.'**]"
        }},
        {{
        "scene_number": 2,
        "scene_title": "[Brief, descriptive title for scene 2, mentioning key characters present]",
        "scene_narrative_text": "[Concise narrative paragraph for scene 2, 3-5 sentences, describing the scene and character actions without speech. Explicitly name primary characters involved.]",
        "image_generation_prompt": "[Highly detailed text prompt for AI image generation, describing a *single image* representing scene 2, adhering to character consistency and art style... No text or speech bubbles.]"
        }}
        // ... up to {nb_scenes} visual novel scene objects
    ]
    }}
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt
    )
    
    # Parse the JSON response and return the scenes list
    return parse_scenes(response.text)

def parse_scenes(raw_response: str) -> list:
    """
    Parse the JSON response and return the scenes list directly
    """
    try:
        # Remove markdown code blocks if present
        cleaned_response = raw_response.strip()
        
        # Check if response is wrapped in markdown code blocks
        if cleaned_response.startswith('```json'):
            # Extract JSON from markdown code blocks
            start_marker = '```json'
            end_marker = '```'
            start_index = cleaned_response.find(start_marker) + len(start_marker)
            end_index = cleaned_response.rfind(end_marker)
            
            if start_index > len(start_marker) - 1 and end_index > start_index:
                cleaned_response = cleaned_response[start_index:end_index].strip()
        elif cleaned_response.startswith('```'):
            # Handle cases where it's just ``` without json specifier
            start_marker = '```'
            end_marker = '```'
            start_index = cleaned_response.find(start_marker) + len(start_marker)
            end_index = cleaned_response.rfind(end_marker)
            
            if start_index > len(start_marker) - 1 and end_index > start_index:
                cleaned_response = cleaned_response[start_index:end_index].strip()
        
        # Parse the JSON response
        data = json.loads(cleaned_response)
        
        # Extract scenes array
        raw_scenes = data.get("scenes", [])
        
        # Validate and clean each scene according to new format
        scenes = []
        for scene_data in raw_scenes:
            if isinstance(scene_data, dict) and "scene_number" in scene_data:
                scene = Scene(
                    title=scene_data.get("scene_title", "Untitled"),
                    narrative_text=scene_data.get("scene_narrative_text", ""),
                    scene_number=scene_data.get("scene_number", 0),
                    image_prompt=scene_data.get("image_generation_prompt", "")
                )
                scenes.append(scene)
        return scenes
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {e}")
        print(f"Raw response: {raw_response[:200]}...")
        print(f"Cleaned response: {cleaned_response[:200] if 'cleaned_response' in locals() else 'N/A'}...")
        return []
    except Exception as e:
        print(f"Error parsing comic scenes: {e}")
        return []


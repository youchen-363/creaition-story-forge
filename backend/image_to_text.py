from google import genai
import json
import re
from User_Character import User_Character
from Scene import Scene
from supabase_storage import save_temp_image_for_upload

def generate_narrative_scenes(client: genai.Client, chars_data: User_Character, background_story: str, nb_scenes: int) -> tuple[str, str, list]:
    # Upload multiple files
    uploaded_files = []        
    all_characters_context = []
    temp_files = []  # Track temporary files for cleanup
    
    for char_data in chars_data:
        all_characters_context.append(f"Character Name: {char_data.name}\nCharacter Description: {char_data.description}")
        
        # All character images are now stored in Supabase storage
        # Download to temporary file for Gemini upload
        temp_file_path = save_temp_image_for_upload(char_data.image_url)
        temp_files.append(temp_file_path)
        uploaded_file = client.files.upload(file=temp_file_path)
        uploaded_files.append(uploaded_file)
    
    dynamic_character_section = "\n".join(all_characters_context)
    
    prompt = f"""
        You are a highly skilled **Visual Narrative Creative Director and Prompt Engineer** for an AI image generation system. Your ultimate goal is to help build visual narratives by turning user-owned characters and art and the personalized illustrated stories into dynamic visual narratives. To achieve this, you need to deeply analyze all provided inputs and then generate a series of interconnected scenes that form a coherent and personalized story.
        ---
        ### Background Story Analysis Task:
        First, thoroughly analyze the `BACKGROUND_STORY_PLACEHOLDER` provided by the user. Understand its core plot, themes, existing characters (if any), conflicts, and the established world. This analysis will form the foundational context for the personalized scenes.

        ---
        ### Character Analysis Task (for each character provided):
        For EACH set of character images and descriptions provided, perform the following:
        1.  **Name Consistency:** Use the character names exactly as provided. Do not replace them with other labels like 'the jester' or 'the officer'. You may add descriptive roles (e.g., 'the officer, Matte') but always keep their given name. Mention their names consistently.
        2.  **Physical & Expressive Description:** Describe the character's physical appearance, facial expression, clothing, and posture across all provided images for that specific character.
        3.  **Inferred Traits:** Infer the character's possible personality, role (e.g., hero, villain, traveler, inventor), and emotional tone from their images.
        4.  **Symbolic & Unique Features:** Mention any symbolic elements or unique art features present in any of the images for that character.
        5.  **Consistency & Variations:** If multiple images show the same character in different poses/situations, analyze the consistency and variations of *that character's visual representation*.
        6.  **Artistic Style Analysis:** Synthesize the artistic style from the images for each individual character, detailing:
            * **Overarching Style:** (e.g., 'digital fantasy painting', 'gritty graphic novel')
            * **Color Palette:** (e.g., 'vibrant saturated greens and browns')
            * **Line Work:** (e.g., 'dynamic brushstrokes', 'bold lines')
            * **Shading:** (e.g., 'focus on natural textures', 'high-contrast')
            * **Texture:** (e.g., 'worn leather, gnarled trees')
            * **Mood/Atmosphere:** (e.g., 'hopeful exploration')
            * **Recurring Motifs:** (e.g., 'dappled sunlight, ancient runes')
        7.  **Synthesized Analysis:** Synthesize all this information into a structured analysis for each individual character.

        ---
        ### Personalized Scenes Generation Task:
        Based on the **thorough analysis of the background story** and the **combined and detailed analysis** of ALL the characters and their artwork, write a compelling, imaginative **series of approximately {nb_scenes} interconnected scenes** that form a personalized narrative. Each scene should directly reflect the characters' personalities, visual characteristics, and the overarching artistic style.

        -   **Integrate all characters:** Ensure all provided characters coexist and interact in a meaningful way within the narrative across the scenes. **Crucially, every single character provided must appear visually in at least one scene throughout the entire set of {nb_scenes} scenes.**
        -   **Preserve Personality and Art Style Tone:** The story's tone, settings, and events should naturally arise from and consistently match or expand upon the inferred personality traits and the combined artistic styles of all characters. This includes the collective art style elements (color palette, line work, shading, texture, mood/atmosphere) derived from the character analyses.
        -   **Build Directly Upon Background Story:** Use the provided `BACKGROUND_STORY_PLACEHOLDER` as the direct starting point and foundational premise for the narrative. Expand upon its themes, existing conflicts, and established world within the context of the generated scenes.
        -   **Be Creative & Dynamic:** Introduce new events, settings, challenges, conflicts, alliances, or rivalries that naturally arise from the characters' combined traits and the existing background story. Each scene should advance the plot.
        -   **Scene Content Detailing:** For each scene, clearly describe the action, identify which characters are present (by their exact names), detail their individual poses, expressions, and any necessary environmental details. Ensure character interactions, relative positioning, and emotional states are clearly defined, drawing directly from their analyzed personalities and visual traits.
        -   **No Future Story Text Output:** Do NOT output a single block of "future_story" text. Instead, the narrative should be expressed *through* the generated scenes.

        ---
        ### Background Story:
        {background_story}

        ### Characters for Analysis and Scene Generation:
        # Start dynamic character context here
        {dynamic_character_section}
        # End dynamic character context here

        ---
        ### Output Format:

        Your final output MUST be a single JSON object structured as follows. Ensure all string values are properly escaped and the JSON is valid.

        ```json
        {{
        "analysis": [
            {{
            "character_name": "[Character 1 Name]",
            "character_description": "[Character 1 Description - their role and key personality traits]",
            "image_analysis_summary": "[Your summary of the provided image analysis input for Character 1]",
            "detailed_character_analysis": {{
                "personality_traits": "[Detailed description of personality and traits based on analysis for Character 1]",
                "visual_characteristics": "[Detailed description of physical appearance based on analysis for Character 1]",
                "artistic_style_analysis": {{
                    "overarching_style": "[e.g., 'digital fantasy painting']",
                    "color_palette": "[e.g., 'vibrant saturated greens and browns']",
                    "line_work": "[e.g., 'dynamic brushstrokes']",
                    "shading": "[e.g., 'focus on natural textures']",
                    "texture": "[e.g., 'worn leather, gnarled trees']",
                    "mood_atmosphere": "[e.g., 'hopeful exploration']",
                    "recurring_motifs": "[e.g., 'dappled sunlight, ancient runes']"
                }},
                "potential_narrative_themes": "[e.g., 'heroic quest, mystical discovery']"
            }}
            }},
            {{
            "character_name": "[Character 2 Name]",
            "character_description": "[Character 2 Description]",
            "image_analysis_summary": "[Your summary of the provided image analysis input for Character 2]",
            "detailed_character_analysis": {{
                "personality_traits": "[Detailed description of personality and traits based on analysis for Character 2]",
                "visual_characteristics": "[Detailed description of physical appearance based on analysis for Character 2]",
                "artistic_style_analysis": {{
                    "overarching_style": "[e.g., 'digital fantasy painting']",
                    "color_palette": "[e.g., 'vibrant saturated greens and browns']",
                    "line_work": "[e.g., 'dynamic brushstrokes']",
                    "shading": "[e.g., 'focus on natural textures']",
                    "texture": "[e.g., 'worn leather, gnarled trees']",
                    "mood_atmosphere": "[e.g., 'hopeful exploration']",
                    "recurring_motifs": "[e.g., 'dappled sunlight, ancient runes']"
                }},
                "potential_narrative_themes": "[e.g., 'heroic quest, mystical discovery']"
            }}
            }}
            // ... Add more character analysis objects as needed for each character
        ],
        "scenes": [
            {{
            "scene_number": 1,
            "scene_title": "[Single, one-word title for scene 1, e.g., 'Discovery', 'Pursuit', 'Chaos']",
            "scene_narrative_text": "[Concise narrative paragraph for scene 1, 3-5 sentences, describing the scene and character actions without speech. Explicitly name primary characters involved, e.g., 'Mathieu, the seasoned detective, arrived at the desolate town square just as dawn broke. A gruesome discovery awaited him: a victim, chillingly displayed, with a single, twisted joker card pinned to their chest. The air hung heavy with a sense of dread and unanswered questions.']",
            "image_generation_prompt": "Generate a high-quality visual narrative image for this scene. CRITICAL: The image MUST have a perfectly square (1:1) aspect ratio with equal width and height. The image must contain no inappropriate/NSFW content, text, speech bubbles, or captions. Depict the complete storytelling moment, including all relevant characters, their interactions, expressions, poses, and the environment as described: [Highly detailed text prompt for AI image generation, describing a *single image* that represents the entire scene. **Example: 'A gritty graphic novel style visual, with stark black, white, and red elements combined with vibrant urban comic book flair. Mathieu, in a dark blue police uniform with a confident yet grim expression beneath his sunglasses, inspects a victim displayed ominously in the center of Muar town square at dawn. A 'Joker' playing card, identical to Dorry's visual motifs, is prominently pinned to the victim's chest with a bloody dagger. The overall mood is ominous, challenging, and resolute.'**] ASPECT RATIO: Generate square image only - width equals height."
            }},
            {{
            "scene_number": 2,
            "scene_title": "[Single, one-word title for scene 2]",
            "scene_narrative_text": "[Concise narrative paragraph for scene 2, 3-5 sentences, describing the scene and character actions without speech. Explicitly name primary characters involved.]",
            "image_generation_prompt": "Generate a high-quality visual narrative image for this scene. CRITICAL: The image MUST have a perfectly square (1:1) aspect ratio with equal width and height. The image must contain no inappropriate/NSFW content, text, speech bubbles, or captions. Depict the complete storytelling moment, including all relevant characters, their interactions, expressions, poses, and the environment as described: [Highly detailed text prompt for AI image generation, describing a *single image* representing scene 2, adhering to character consistency and art style... **No text or speech bubbles.**] ASPECT RATIO: Generate square image only - width equals height."
            }}
            // ... up to {nb_scenes} visual novel scene objects
        ]
        }}
        """
    # Inject the dynamic context
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=uploaded_files + [prompt]
    )
    
    # Parse and format the response
    return format_response(chars_data, response.text)

def format_response(chars_data: User_Character, raw_response: str) -> tuple[str, str, list]:
    """
    Parse the JSON response and format it into readable paragraphs
    Returns: (analysis_paragraph, scenes_paragraph, scenes_list)
    """
    try:
        # Clean the response text to remove invalid control characters
        cleaned_response = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', raw_response)
        
        # Extract JSON from the response (in case there's extra text)
        json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            # Additional cleaning for common JSON issues
            json_str = json_str.replace('\n', ' ')  # Replace newlines with spaces
            json_str = re.sub(r'\s+', ' ', json_str)  # Replace multiple spaces with single space
            json_str = json_str.strip()
            
            # Try to fix common JSON formatting issues
            json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
            json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
            
            data = json.loads(json_str)
        else:
            # If no JSON found, try to extract content manually
            return extract_content_manually(cleaned_response)
        
        # Format the output
        formatted_output = []
        
        # Header
        formatted_output.append("=" * 80)
        formatted_output.append(f"CHARACTER ANALYSIS")
        formatted_output.append("=" * 80)
        formatted_output.append("")
        
        # Character Information - now handling multiple characters
        analysis_data = data.get("analysis", [])
        
        # Handle both old format (single character object) and new format (array of characters)
        if isinstance(analysis_data, dict):
            # Old format - single character
            characters = [analysis_data]
        else:
            # New format - array of characters
            characters = analysis_data
        
        for i, character in enumerate(characters):
            """
            if i > 0:
                formatted_output.append("\n" + "=" * 60)
                formatted_output.append("")
            """
            char_analysis = []
            char_analysis.append(f"📖 CHARACTER {i+1}: {character.get('character_name', 'Unknown')}")
            char_analysis.append(f"📝 DESCRIPTION: {character.get('character_description', 'No description provided')}")
            char_analysis.append("")
            
            # Image Analysis Summary
            if character.get('image_analysis_summary'):
                char_analysis.append("🔍 IMAGE ANALYSIS SUMMARY:")
                char_analysis.append("-" * 40)
                char_analysis.append(character['image_analysis_summary'])
                char_analysis.append("")
            
            # Detailed Character Analysis
            detailed_analysis = character.get('detailed_character_analysis', {})
            if detailed_analysis:
                char_analysis.append("👤 DETAILED CHARACTER ANALYSIS:")
                char_analysis.append("-" * 40)
                
                if detailed_analysis.get('personality_traits'):
                    char_analysis.append(f"Personality Traits: {detailed_analysis['personality_traits']}")
                    char_analysis.append("")
                
                if detailed_analysis.get('visual_characteristics'):
                    char_analysis.append(f"Visual Characteristics: {detailed_analysis['visual_characteristics']}")
                    char_analysis.append("")
                
                # Artistic Style Analysis
                style_analysis = detailed_analysis.get('artistic_style_analysis', {})
                if style_analysis:
                    char_analysis.append("🎨 ARTISTIC STYLE ANALYSIS:")
                    for key, value in style_analysis.items():
                        if value and value.strip():
                            char_analysis.append(f"  • {key.replace('_', ' ').title()}: {value}")
                    char_analysis.append("")
                
                if detailed_analysis.get('potential_narrative_themes'):
                    char_analysis.append(f"📚 Narrative Themes: {detailed_analysis['potential_narrative_themes']}")
                    char_analysis.append("")
            
            analysis = "\n".join(char_analysis)
            formatted_output.append(analysis)
            chars_data[i].analysis = analysis
        
        analysis = "\n".join(formatted_output)
        
        # Parse Scenes and create Scene objects
        scenes_data = data.get('scenes', [])
        scenes_list = []
        scenes_paragraph_parts = []
        
        for scene_data in scenes_data:
            print(f"DEBUG: Processing scene_data: {scene_data}")
            # Create Scene object with additional null safety
            title = scene_data.get("scene_title", "") if scene_data else ""
            narrative_text = scene_data.get("scene_narrative_text", "") if scene_data else ""
            scene_number = scene_data.get("scene_number", 0) if scene_data else 0
            image_prompt = scene_data.get("image_generation_prompt", "") if scene_data else ""
            
            # Ensure values are not None
            title = title if title is not None else ""
            narrative_text = narrative_text if narrative_text is not None else ""
            image_prompt = image_prompt if image_prompt is not None else ""
            
            scene = Scene(
                title=title,
                narrative_text=narrative_text,
                scene_number=scene_number,
                image_prompt=image_prompt
            )
            print(f"DEBUG: Created scene {scene_number}: title='{title}', narrative_length={len(narrative_text)}, prompt_length={len(image_prompt)}")
            scenes_list.append(scene)
            
            # Add to scenes paragraph
            scenes_paragraph_parts.append(f"🎬 SCENE {scene.scene_number}: {scene.title}. ")
            scenes_paragraph_parts.append("")
            scenes_paragraph_parts.append(f"{scene.narrative_text}")
            scenes_paragraph_parts.append("")
        
        scenes_paragraph = "\n".join(scenes_paragraph_parts)
        
        return analysis, scenes_paragraph, scenes_list
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {e}")
        # Fallback to manual extraction
        return extract_content_manually(raw_response)
    except Exception as e:
        error_msg = f"Error formatting response: {e}\n\nRaw Response:\n{raw_response}"
        return error_msg, "Error generating scenes", [] 

def clean_story_text(story_text: str) -> str:
    """
    Clean up story text by removing duplicate sentences and formatting issues
    """
    # Remove extra whitespace
    story_text = re.sub(r'\s+', ' ', story_text).strip()
    
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', story_text)
    
    # Remove duplicate or very similar sentences
    unique_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and not any(sentence in existing or existing in sentence for existing in unique_sentences):
            unique_sentences.append(sentence)
    
    # Join sentences back with proper spacing
    cleaned_text = ' '.join(unique_sentences)
    
    # Add paragraph breaks for better readability
    paragraphs = cleaned_text.split('. ')
    formatted_paragraphs = []
    current_paragraph = []
    
    for i, part in enumerate(paragraphs):
        current_paragraph.append(part if part.endswith('.') else part + '.')
        
        # Create new paragraph every 3-4 sentences
        if len(current_paragraph) >= 3 or i == len(paragraphs) - 1:
            formatted_paragraphs.append(' '.join(current_paragraph).strip())
            current_paragraph = []
    
    return '\n\n'.join(formatted_paragraphs)

def extract_content_manually(raw_response: str) -> tuple[str, str, list]:
    """
    Manually extract content when JSON parsing fails
    Returns: (analysis_paragraph, scenes_paragraph, scenes_list)
    """
    analysis_output = []
    scenes_list = []
    
    # Analysis Header
    analysis_output.append("=" * 80)
    analysis_output.append("CHARACTER ANALYSIS")
    analysis_output.append("=" * 80)
    analysis_output.append("")
    
    # Try to extract character name and description
    name_match = re.search(r'"character_name":\s*"([^"]*)"', raw_response)
    desc_match = re.search(r'"character_description":\s*"([^"]*)"', raw_response)
    
    if name_match:
        analysis_output.append(f"📖 CHARACTER: {name_match.group(1)}")
    if desc_match:
        analysis_output.append(f"📝 DESCRIPTION: {desc_match.group(1)}")
    analysis_output.append("")
    
    analysis_output.append("Raw Response (for debugging):")
    analysis_output.append("-" * 40)
    analysis_output.append(raw_response[:500] + "..." if len(raw_response) > 500 else raw_response)
    analysis_output.append("=" * 80)
    
    # Try to extract scenes manually and create Scene objects
    scene_pattern = r'"scene_number":\s*(\d+).*?"scene_title":\s*"([^"]*)".*?"scene_narrative_text":\s*"([^"]*)".*?"image_generation_prompt":\s*"([^"]*)"'
    scene_matches = re.findall(scene_pattern, raw_response, re.DOTALL)
    
    scenes_paragraph_parts = []
    scenes_paragraph_parts.append("=" * 80)
    scenes_paragraph_parts.append("GENERATED SCENES (Manual Extraction)")
    scenes_paragraph_parts.append("=" * 80)
    scenes_paragraph_parts.append("")
    
    for match in scene_matches:
        scene = Scene(
            title=match[1],
            narrative_text=match[2],
            scene_number=int(match[0]),
            image_prompt=match[3]
        )
        scenes_list.append(scene)
        
        # Add to scenes paragraph
        scenes_paragraph_parts.append(f"🎬 SCENE {scene.scene_number}: {scene.title}")
        scenes_paragraph_parts.append("-" * 50)
        scenes_paragraph_parts.append(f"📖 Narrative: {scene.narrative_text}")
        scenes_paragraph_parts.append("")
        scenes_paragraph_parts.append(f"🎨 Image Prompt: {scene.image_prompt}")
        scenes_paragraph_parts.append("")
        scenes_paragraph_parts.append("=" * 50)
        scenes_paragraph_parts.append("")
    
    if not scenes_list:
        # If no scenes found, create a default empty scene
        default_scene = Scene(
            title="Parse Error",
            narrative_text="Could not extract scenes from response",
            scene_number=1,
            image_prompt="Error extracting scene data"
        )
        scenes_list.append(default_scene)
        
        scenes_paragraph_parts.append("🎬 SCENE 1: Parse Error")
        scenes_paragraph_parts.append("-" * 50)
        scenes_paragraph_parts.append("📖 Narrative: Could not extract scenes from response")
        scenes_paragraph_parts.append("")
        scenes_paragraph_parts.append("🎨 Image Prompt: Error extracting scene data")
        scenes_paragraph_parts.append("")
    
    scenes_paragraph = "\n".join(scenes_paragraph_parts)
    
    return "\n".join(analysis_output), scenes_paragraph, scenes_list

def get_scenes_only(client: genai.Client, chars_data: User_Character, background_story: str, nb_scenes: int) -> list:
    """
    Helper function to get only the Scene objects
    Returns: scenes_list (list of Scene objects)
    """
    _, _, scenes_list = generate_narrative_scenes(client, chars_data, background_story, nb_scenes)
    return scenes_list


    
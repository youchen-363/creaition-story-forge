from google import genai
import json
import re
from User_Character import User_Character

def generate_future_story(client: genai.Client, chars_data: User_Character, background_story: str, nb_scenes: int) -> tuple[str, str]:
    # Upload multiple files
    uploaded_files = []        
    all_characters_context = []
    for char_data in chars_data:
        all_characters_context.append(f"Character Name: {char_data.name}\nCharacter Description: {char_data.description}")
        uploaded_file = client.files.upload(file=char_data.image_url)
        uploaded_files.append(uploaded_file)
    dynamic_character_section = "\n".join(all_characters_context)

    # Determine story length guidance based on nb_scenes
    story_length_guidance = ""
    future_story_paragraph_count = ""
    if nb_scenes <= 2: # 1-2 scenes
        story_length_guidance = "Aim for a very concise, impactful narrative of **1 paragraph (approx. 100-200 words)**."
        future_story_paragraph_count = "1 paragraph (approx. 100-200 words)" # For JSON description
    elif nb_scenes <= 4: # 3-4 scenes
        story_length_guidance = "Aim for a concise narrative of **2 paragraphs (approx. 200-400 words)**. Focus on essential plot points."
        future_story_paragraph_count = "2 paragraphs (approx. 200-400 words)" # For JSON description
    elif nb_scenes <= 6: # 5-6 scenes
        story_length_guidance = "Aim for a moderately detailed narrative of **3 paragraphs (approx. 400-600 words)**. Develop the plot with a clear progression."
        future_story_paragraph_count = "3 paragraphs (approx. 400-600 words)" # For JSON description
    else: # >6 scenes
        story_length_guidance = "Aim for a comprehensive mini-narrative of **4-6 paragraphs (approx. 600-900 words)**, allowing for richer plot development and character arcs."
        future_story_paragraph_count = "4-6 paragraphs (approx. 600-900 words)" # For JSON description


    prompt = f"""
        You are a visual storytelling AI assistant. Your ultimate goal is to help build the future of personalized illustrated stories by turning user-owned characters and art into dynamic visual narratives. To achieve this, you need to deeply analyze all provided inputs.

        **Background Story Analysis Task:**
        First, thoroughly analyze the `BACKGROUND_STORY_PLACEHOLDER` provided by the user. Understand its core plot, themes, existing characters (if any), conflicts, and the established world. This analysis will form the foundational context for the future story.

        **Character Analysis Task (for each character provided):**
        For EACH set of character images and descriptions provided, perform the following:
        1.  Use the character names exactly as provided. Do not replace them with other labels like 'the jester' or 'the officer'. You may add 'the officer' but still remain their name like 'the officer, Matte'. Mention their names consistently throughout the story. 
        2.  Describe the character's physical appearance, facial expression, clothing, posture, and art style across all provided images for that specific character.
        3.  Infer the character's possible personality, role (e.g., hero, villain, traveler, inventor), and emotional tone from their images.
        4.  Mention any symbolic elements or unique art features present in any of the images for that character.
        5.  If multiple images show the same character in different poses/situations, analyze the consistency and variations of *that character*.
        6.  Synthesize this information into a structured analysis for each individual character.

        **Scenes Generation Task:**
        Based on the **thorough analysis of the background story** and the **combined analysis** of ALL the characters and their artwork, write a compelling, imaginative **future story** where these characters are the main protagonists/antagonists or key players.
        -   **Integrate all characters:** Ensure all provided characters coexist and interact in a meaningful way within the narrative.
        -   **Preserve personality and art style tone:** The story's tone and settings should match or expand upon the inferred personality traits and artistic styles of all characters.
        -   **Build directly upon background story:** Use the provided BACKGROUND_STORY_PLACEHOLDER as the direct starting point and foundational premise for the narrative. Expand upon its themes, existing conflicts, and established world.
        -   **Be creative:** Introduce new events, settings, challenges, conflicts, alliances, or rivalries that naturally arise from their combined traits and the existing background.
        -   **Story Length Requirement:** This story is intended to be broken down into approximately {nb_scenes} visual scenes/scenes. Therefore, {story_length_guidance}
        

        **Background Story:**
        {background_story}

        **Characters for Analysis and Story Generation:**
        # Start dynamic character context here
        {dynamic_character_section}
        # End dynamic character context here

        **Output Format:**

        Your final output MUST be a single JSON object structured as follows. Ensure all string values are properly escaped and the JSON is valid.

        {{
        "analysis": [
            {{
            "character_name": "[Character 1 Name]",
            "character_description": "[Character 1 Description]",
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
        "future_story": "[The full future story text generated by the AI, {future_story_paragraph_count}, integrating all characters and building upon the background story]"
        }}
        """
    # Inject the dynamic context
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=uploaded_files + [prompt]
    )
    
    # Parse and format the response
    return format_response(chars_data, response.text)

def format_response(chars_data: User_Character, raw_response: str) -> tuple[str, str]:
    """
    Parse the JSON response and format it into readable paragraphs
    Returns: (analysis, future_story)
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
        
        # Future Story
        formatted_story = []
        
        # Header
        formatted_story.append("=" * 80)
        formatted_story.append(f"FUTURE STORY")
        formatted_story.append("=" * 80)
        formatted_story.append("")
        
        future_story_content = data.get('future_story', '')
        if future_story_content:
            formatted_story.append("🚀 FUTURE STORY:")
            formatted_story.append("=" * 40)
            # Clean up the future story text
            clean_story = clean_story_text(future_story_content)
            formatted_story.append(clean_story)
            formatted_story.append("")
        
        formatted_story.append("=" * 80)
        future_story = "\n".join(formatted_story)
        
        return analysis, future_story
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {e}")
        # Fallback to manual extraction
        return extract_content_manually(raw_response)
    except Exception as e:
        error_msg = f"Error formatting response: {e}\n\nRaw Response:\n{raw_response}"
        return error_msg, "" 

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

def extract_content_manually(raw_response: str) -> tuple[str, str]:
    """
    Manually extract content when JSON parsing fails
    Returns: (analysis, future_story)
    """
    analysis_output = []
    story_output = []
    
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
    
    # Story Header
    story_output.append("=" * 80)
    story_output.append("FUTURE STORY")
    story_output.append("=" * 80)
    story_output.append("")
    
    # Try to extract future story
    story_match = re.search(r'"future_story":\s*"([^"]*)"', raw_response, re.DOTALL)
    if story_match:
        story_text = story_match.group(1)
        clean_story = clean_story_text(story_text)
        story_output.append("🚀 FUTURE STORY:")
        story_output.append("=" * 40)
        story_output.append(clean_story)
        story_output.append("")
    else:
        story_output.append("❌ Could not extract future story from response")
        story_output.append("")
    
    story_output.append("=" * 80)
    
    return "\n".join(analysis_output), "\n".join(story_output)


    
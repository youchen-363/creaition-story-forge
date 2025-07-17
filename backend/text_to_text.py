from google import genai
import json
import re

def generate_scenes(client: genai.Client, nb_scenes: int, nb_panels: int, analysis: str, story: str) -> list:
    prompt = f"""
        You are a highly skilled **Visual Narrative Creative Director and Prompt Engineer** for an AI image generation system. Your primary task is to transform a given future story into a sequence of distinct, visually rich comic pages without any inappropriate or NSFW content. Each "page" should be conceptualized as a **single image that contains {nb_panels} "boxes" or "panels"**, illustrating sequential moments or different perspectives within that single scene/page. This output will be used to generate dynamic visual narratives based on the user's character art.

        ---
        ### Crucial Context for Consistency (Derived from prior analysis and MUST be used)

        -   **Character & Art Analysis (Raw String Input for Multiple Characters):**
            ```
            {analysis}
            ```
            *(**IMPORTANT:** This is a **long string** containing detailed textual analysis for multiple characters. You must parse and extract the individual character details from this string. For each character (e.g., "Dorry", "Mathieu"), identify their `character_name`, `character_description` (their role and key personality traits), `visual_characteristics` (physical appearance, clothing, unique features, art style nuances like line work, shading, specific color palette, texture, mood/atmosphere), and any `recurring_motifs`. **Ensure these extracted details are rigorously applied, depicting each character consistently (using their exact names and specific visual descriptions) and accurately reflecting their interactions as required by the story.**)*

        ---
        ### Input for Scene/Page Generation

        -   **Future Story:** {story}
        -   **Number of Scenes/Pages Desired:** {nb_scenes}
        -   **Number of Panels Per Page:** {nb_panels} (This should be an integer, e.g., 3, 4, 6)

        ---
        ### Task for Each Scene/Page

        For each of the {nb_scenes} desired comic pages:

        1.  **Determine Panel Content (Multi-Character Focus):** For each of the {nb_panels} panels on the current page, identify the specific action, **explicitly state *which* characters are present (by their exact names as extracted from the analysis)**, describe their individual poses, expressions, and any necessary environmental details. Ensure character interactions, relative positioning, and emotional states are clearly defined for each panel, drawing directly from their analyzed personalities and visual traits.
        2.  **Extract Dialogue (for separate processing):** Identify any crucial dialogue spoken by characters or narration for each panel. This dialogue will be stored separately and *not* directly embedded as text in the image generation prompt.
        3.  **Detailed Image Generation Prompt (for a single image representing the entire page):** Generate a highly detailed, comprehensive text prompt (suitable for an AI like Imagen 4 or DALL-E 3) that describes the entire comic page. This prompt MUST rigorously ensure:
            * **Multi-Panel Layout Description:** Explicitly describe the arrangement of **exactly {nb_panels} distinct "boxes" or "panels"** on this single page. Specify their arrangement (e.g., "a {nb_panels}-panel comic page, with a large top panel and two smaller panels below," "a grid of {nb_panels} equally sized panels").
            * **Visual Content Per Panel (Explicit Character Detailing):** For **each individual panel**, describe the specific action. **Crucially, for every character present in a panel, explicitly name them (e.g., "Dorry," "Mathieu") and then concisely describe their key visual characteristics and any relevant art style nuances (e.g., "Dorry with his split white and black jester face, unnerving grin, and sharp-pointed hat," "Mathieu in his dark blue police uniform, confident smile, and dark sunglasses").** Detail their pose, expression, and any essential environmental elements. **If a character speaks, describe the *visual presence of an empty speech bubble* (e.g., "with an empty circular speech bubble floating near Dorry's head," "a jagged, empty speech bubble indicating Mathieu shouting"). Do NOT include the dialogue text within this image prompt.** Ensure the narrative flows sequentially from one panel to the next within the page, emphasizing character placement, interaction, and emotional arcs.
            * **Character Consistency Across Panels:** **Strictly maintain the consistent appearance and artistic style (including color palette, line work, shading, etc.) for each character across all panels on the page, referencing the details you extracted from the 'Character & Art Analysis' string.**
            * **Art Style Enforcement (Consistent Across Page):** Explicitly state the desired **overarching art style**, specific color palette, line work, shading, texture, and mood/atmosphere **derived from the combined 'ARTISTIC STYLE ANALYSIS' sections of all characters relevant to the story** (e.g., 'in the style of a graphic novel with stark black, white, and red tones from Dorry, and vibrant urban comic book elements from Mathieu', 'with high-contrast colors and bold lines'). This style must apply uniformly across all panels on the page.
            * **Lighting & Atmosphere:** Detail the lighting and overall atmosphere for the entire page, or describe variations per panel if intentional, consistent with the characters' themes and the story's mood.

        ---
        ### Output Format

        Your final output MUST be a single JSON object structured as follows. Ensure all string values are properly escaped and the JSON is valid. You should generate exactly the 'Number of Scenes/Pages Desired' as specified in the input.

        ```json
        {{
        "comic_pages": [
            {{
            "page_number": 1,
            "page_title": "[Brief, descriptive title for Comic Page 1, mentioning key characters present, e.g., 'Dorry's Taunt in Muar Square']",
            "page_summary": "[1-2 sentences summarizing the overarching action/focus of Comic Page 1, explicitly naming primary characters involved, e.g., 'Mathieu discovers Dorry's latest gruesome performance in the town square, finding a Joker card pinned to a victim.']",
            "panels_dialogue": [
                {{
                "panel_number": 1,
                "character_speaking": "[Character Name or 'Narrator']",
                "dialogue": "[Full dialogue text for this panel, if any. Empty string if none.]"
                }},
                {{
                "panel_number": 2,
                "character_speaking": "[Character Name or 'Narrator']",
                "dialogue": "[Full dialogue text for this panel, if any.]"
                }},  
                // ... up to {nb_panels} dialogue entries
            ],
            "image_generation_prompt": "[Highly detailed text prompt for AI image generation, describing a *single image* that represents the entire comic page with its multiple panels/boxes. Ensure descriptions of empty speech bubbles where dialogue should go. **Example based on your input: 'A {nb_panels}-panel comic page in a stark graphic novel style with high-contrast black, white, and red elements, combined with vibrant urban comic book flair. Panel 1: Mathieu (dark blue police uniform, confident smile beneath sunglasses), jaw clenched, grimly inspecting a victim in Muar town square at dawn. A 'Joker' playing card, identical to Dorry's visual, is pinned to the victim's chest with a bloody dagger, an empty thought bubble above Mathieu's head. Panel 2: Close-up on the 'Joker' card and the dagger, emphasizing the blood and the twisted smile on the victim's face, conveying a chilling, unsettling mood. Panel 3: Mathieu (still in uniform), looking up with steely determination, the sun attempting to pierce the perpetual twilight, an empty resolve-bubble near his head. The overall mood is ominous, challenging, and resolute.'**]"
            }},
            {{
            "page_number": 2,
            "page_title": "[Brief, descriptive title for Comic Page 2, mentioning key characters present]",
            "page_summary": "[1-2 sentences summarizing the overarching action/focus of Comic Page 2, explicitly naming primary characters involved.]",
            "panels_dialogue": [
                {{
                "panel_number": 1,
                "character_speaking": "[Character Name or 'Narrator']",
                "dialogue": "[Full dialogue text for this panel, if any.]"
                }}
                // ... up to {nb_panels} dialogue entries
            ],
            "image_generation_prompt": "[Highly detailed text prompt for AI image generation, describing a *single image* representing Comic Page 2 with its multiple panels/boxes, adhering to character consistency and art style...]"
            }}
            // ... up to {nb_scenes} comic page objects
        ]
        }}
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt
    )
    
    # Parse the JSON response and return the comic_pages list
    return parse_comic_pages(response.text)

def parse_comic_pages(raw_response: str) -> list:
    """
    Parse the JSON response and return the comic_pages list directly
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
        
        # Extract comic_pages array
        comic_pages = data.get("comic_pages", [])
        
        # Validate and clean each page according to new format
        cleaned_pages = []
        for page in comic_pages:
            if isinstance(page, dict) and "page_number" in page:
                cleaned_page = {
                    "page_number": page.get("page_number", 0),
                    "page_title": page.get("page_title", "Untitled"),
                    "page_summary": page.get("page_summary", ""),
                    "panels_dialogue": page.get("panels_dialogue", []),
                    "image_generation_prompt": page.get("image_generation_prompt", "")
                }
                
                # Validate panels_dialogue structure
                validated_dialogue = []
                for panel_dialogue in cleaned_page["panels_dialogue"]:
                    if isinstance(panel_dialogue, dict):
                        validated_panel = {
                            "panel_number": panel_dialogue.get("panel_number", 1),
                            "character_speaking": panel_dialogue.get("character_speaking", ""),
                            "dialogue": panel_dialogue.get("dialogue", "")
                        }
                        validated_dialogue.append(validated_panel)
                
                cleaned_page["panels_dialogue"] = validated_dialogue
                cleaned_pages.append(cleaned_page)
        
        return cleaned_pages
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {e}")
        print(f"Raw response: {raw_response[:200]}...")
        print(f"Cleaned response: {cleaned_response[:200] if 'cleaned_response' in locals() else 'N/A'}...")
        return []
    except Exception as e:
        print(f"Error parsing comic pages: {e}")
        return []


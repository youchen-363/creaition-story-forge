from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from Scene import Scene 
from User_Character import User_Character

#load_dotenv()
#client = genai.Client(api_key=os.getenv("GEMINI_PAID_API_KEY"))

def generate_images_with_updates(client: genai.Client, story_name: str, chars_data: list[User_Character], scenes: list[Scene], scene_dao=None, story_id=None):
    generated_image_urls = []  # Changed to return list of file paths
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    uploaded_reference_images = []
    print(f"Processing {len(chars_data)} characters for reference images...")
    
    for char_data in chars_data:
        # Convert URL to local file path
        # URL format: http://localhost:8002/assets/character_xxx.jpeg
        # Local path: assets/character_xxx.jpeg
        print("link : ", char_data.image_url)
        
        # Skip characters without valid image URLs
        if not char_data.image_url or char_data.image_url.strip() in ['', '.', 'None', 'null']:
            print(f"Skipping character {char_data.name} - no valid image URL")
            continue
            
        if char_data.image_url.startswith('http://'):
            # Extract filename from URL
            filename = char_data.image_url.split('/assets/')[-1]
            local_file_path = Path("assets") / filename
        else:
            # Assume it's already a local path
            local_file_path = Path(char_data.image_url)
        
        # Check if the file actually exists
        if not local_file_path.exists():
            print(f"Warning: Character image file does not exist: {local_file_path}")
            continue
        
        uploaded_file = client.files.upload(file=str(local_file_path))
        uploaded_reference_images.append(uploaded_file)
        print(f"✅ Successfully uploaded reference image: {str(local_file_path)}")
    
    print(f"Total reference images uploaded: {len(uploaded_reference_images)}")
    print(f"Starting generation for {len(scenes)} scenes...")
    
    for i, scene in enumerate(scenes):
        scene_image_url = ""  # Default empty path for failed generations
        print(f"\n=== PROCESSING SCENE {scene.scene_number} ===")
        
        # Replace spaces with underscores to avoid URL encoding issues
        safe_story_name = story_name.replace(" ", "_")
        
        # --- THIS IS THE PROMPT YOU WOULD PASS TO THE IMAGEN API ---
        # It's the `image_generation_prompt` directly.
        # You can add a prefix if you want, but the detailed prompt is what matters.
        # imagen_prompt = scene.'image_generation_prompt']
        
        # You could also add more general framing like this, but the core is the detailed prompt:
        prompt = (
            f"Without any inappropriate or NSFW content, create an image."
            f"No text, speech bubbles, or captions should appear in the image."
            f"This is scene {scene.scene_number} of a dynamic visual narrative, titled '{scene.title}'."
            f"Here is the detailed visual description and art style guidance for this scene: {scene.image_prompt}"
            f"The narrative for this scene is: '{scene.narrative_text}'"
        )

        print(f"Generating image for scene {scene.scene_number}: '{scene.title}'")
        print(f"Scene {scene.scene_number} prompt length: {len(prompt)} characters")
        print(f"Scene {scene.scene_number} image_prompt: {scene.image_prompt[:100]}...")
        print(f"Scene {scene.scene_number} narrative_text: {scene.narrative_text[:100]}...")
        print(f"Using prompt:\n{prompt[:300]}...\n") # Print first 300 chars for brevity

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-preview-image-generation",
                contents=[prompt, uploaded_reference_images],
                config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
                )
            )
            
            # Debug: Print response structure
            print(f"DEBUG: Response type: {type(response)}")
            print(f"DEBUG: Has candidates: {hasattr(response, 'candidates')}")
            if hasattr(response, 'candidates') and response.candidates:
                print(f"DEBUG: Number of candidates: {len(response.candidates)}")
                candidate = response.candidates[0]
                print(f"DEBUG: Candidate content type: {type(candidate.content)}")
                print(f"DEBUG: Candidate content is None: {candidate.content is None}")
                
                if candidate.content is not None and hasattr(candidate.content, 'parts'):
                    print(f"DEBUG: Number of parts: {len(candidate.content.parts)}")
                    
                    for part_idx, part in enumerate(candidate.content.parts):
                        print(f"DEBUG: Part {part_idx} - has text: {part.text is not None}")
                        print(f"DEBUG: Part {part_idx} - has inline_data: {part.inline_data is not None}")
                        
                        if part.text is not None:
                            print(f"Model text response: {part.text}")
                        elif part.inline_data is not None:
                            try:
                                # The data is already binary, not base64 encoded!
                                print(f"DEBUG: Inline data mime_type: {part.inline_data.mime_type}")
                                print(f"DEBUG: Inline data length: {len(part.inline_data.data)}")
                                print(f"DEBUG: First 20 bytes as hex: {part.inline_data.data[:20].hex()}")
                                
                                # Use the data directly as binary bytes
                                image_bytes = part.inline_data.data
                                print(f"DEBUG: Using data directly - bytes length: {len(image_bytes)}")
                                
                                # Check for PNG/JPEG headers
                                png_header = b'\x89PNG\r\n\x1a\n'
                                jpeg_header = b'\xff\xd8\xff'
                                
                                if image_bytes.startswith(png_header):
                                    print("DEBUG: Valid PNG header detected")
                                elif image_bytes.startswith(jpeg_header):
                                    print("DEBUG: Valid JPEG header detected")
                                else:
                                    print(f"DEBUG: Unknown file format. First 20 bytes: {image_bytes[:20].hex()}")
                                
                                output_image = Image.open(BytesIO(image_bytes))
                                print(f"DEBUG: Successfully opened image: {output_image.size}")

                                # 2. Determine file extension from mime_type (or default to .png)
                                mime_type = part.inline_data.mime_type
                                extension = ".png" # Default
                                if "jpeg" in mime_type:
                                    extension = ".jpg"
                                elif "webp" in mime_type:
                                    extension = ".webp"

                                # 3. Construct the full file path
                                filename = f"{safe_story_name}_{scene.scene_number}{extension}"
                                file_path = os.path.join(output_dir, filename)

                                # 4. Save the image
                                output_image.save(file_path)
                                print(f"Image saved successfully to: {file_path}")

                                # Set the successful URL path (for web access)
                                scene_image_url = f"/output/{filename}"
                                
                                # Update the database immediately if DAO is provided
                                if scene_dao and story_id:
                                    success = scene_dao.update_scene_image_url(story_id, scene.scene_number, scene_image_url)
                                    if success:
                                        print(f"💾 Updated scene {scene.scene_number} in database with image URL: {scene_image_url}")
                                    else:
                                        print(f"❌ Failed to update scene {scene.scene_number} in database")
                                
                                break # Successfully processed an image
                                
                            except Exception as image_error:
                                print(f"Error processing image data: {image_error}")
                                print(f"Error type: {type(image_error)}")
                                # Save the problematic data for debugging
                                try:
                                    debug_filename = f"debug_failed_data_scene_{scene.scene_number}.bin"
                                    with open(debug_filename, 'wb') as f:
                                        f.write(part.inline_data.data)
                                    print(f"DEBUG: Saved binary data to {debug_filename}")
                                except:
                                    pass
                                import traceback
                                traceback.print_exc()
                                continue
                    else:
                        print(f"No valid image part found in response for scene {scene.scene_number}.")
                else:
                    print(f"No content or parts found in response for scene {scene.scene_number}.")
                    print(f"This might be due to content filtering or API issues.")
                    if hasattr(response, 'prompt_feedback'):
                        print(f"Prompt feedback: {response.prompt_feedback}")
                    
                    # Try once more with a simplified prompt for Scene 1 specifically
                    if scene.scene_number == 1:
                        print("🔄 Retrying Scene 1 with simplified prompt...")
                        simple_prompt = (
                            f"Create a graphic novel style image without text or speech bubbles. "
                            f"Show a police officer examining evidence in an office setting. "
                            f"Use dark blues and dramatic lighting."
                        )
                        try:
                            retry_response = client.models.generate_content(
                                model="gemini-2.0-flash-preview-image-generation",
                                contents=[simple_prompt, uploaded_reference_images],
                                config=types.GenerateContentConfig(
                                response_modalities=['TEXT', 'IMAGE']
                                )
                            )
                            print(f"RETRY: Response type: {type(retry_response)}")
                            if hasattr(retry_response, 'candidates') and retry_response.candidates and retry_response.candidates[0].content:
                                # Process the retry response the same way
                                candidate = retry_response.candidates[0]
                                if candidate.content and hasattr(candidate.content, 'parts'):
                                    for part in candidate.content.parts:
                                        if part.inline_data is not None:
                                            try:
                                                image_bytes = part.inline_data.data
                                                output_image = Image.open(BytesIO(image_bytes))
                                                filename = f"{safe_story_name}_{scene.scene_number}.png"
                                                file_path = os.path.join(output_dir, filename)
                                                output_image.save(file_path)
                                                scene_image_url = f"/output/{filename}"
                                                print(f"✅ RETRY SUCCESS: {file_path}")
                                                
                                                # Update the database immediately if DAO is provided
                                                if scene_dao and story_id:
                                                    success = scene_dao.update_scene_image_url(story_id, scene.scene_number, scene_image_url)
                                                    if success:
                                                        print(f"💾 Updated scene {scene.scene_number} in database with retry image URL: {scene_image_url}")
                                                    else:
                                                        print(f"❌ Failed to update scene {scene.scene_number} in database")
                                                
                                                break
                                            except Exception as retry_error:
                                                print(f"❌ RETRY FAILED: {retry_error}")
                        except Exception as retry_error:
                            print(f"❌ RETRY EXCEPTION: {retry_error}")
            else:
                print(f"No candidates found in response for scene {scene.scene_number}.")
                print(f"Full response: {response}")

        except Exception as e:
            print(f"Error generating or saving image for scene {scene.scene_number}: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
        
        # Always add a path (empty string if failed) to maintain scene-to-path correspondence
        generated_image_urls.append(scene_image_url)
        print(f"=== SCENE {scene.scene_number} RESULT: {'SUCCESS' if scene_image_url else 'FAILED'} ===")
        print(f"Generated path: {scene_image_url}")
        
        # Add a small delay between generations to avoid rate limiting
        if i < len(scenes) - 1:  # Don't delay after the last scene
            print("⏳ Waiting 2 seconds before next generation...")
            time.sleep(2)

    print(f"\n=== FINAL RESULTS ===")
    print(f"Total scenes: {len(scenes)}")
    print(f"Generated images: {len([url for url in generated_image_urls if url])}")
    print(f"Failed generations: {len([url for url in generated_image_urls if not url])}")
    print(f"Image paths: {generated_image_urls}")
    
    return generated_image_urls

def generate_images(client: genai.Client, story_name: str, chars_data: list[User_Character], scenes: list[Scene]):
    """Original function for backward compatibility"""
    return generate_images_with_updates(client, story_name, chars_data, scenes, None, None)


# Example usage:
# generated_images = generate_comic_images(example_scenes_list, client)
# print(f"\nGenerated {len(generated_images)} images.")
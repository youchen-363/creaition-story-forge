from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
import time
from Scene import Scene 
from User_Character import User_Character
from supabase_storage import upload_generated_image_to_supabase, save_temp_image_for_upload

def generate_images_with_updates(client: genai.Client, story_name: str, chars_data: list[User_Character], scenes: list[Scene], scene_dao=None, story_id=None):
    generated_image_urls = []  # Return list of Supabase URLs
    uploaded_reference_images = []
    print(f"Processing {len(chars_data)} characters for reference images...")
    
    for char_data in chars_data:
        print("link : ", char_data.image_url)
        
        # Skip characters without valid image URLs
        if not char_data.image_url or char_data.image_url.strip() in ['', '.', 'None', 'null']:
            print(f"Skipping character {char_data.name} - no valid image URL")
            continue
            
        # All character images are now stored in Supabase storage
        # Download to temporary file for Gemini upload
        try:
            temp_file_path = save_temp_image_for_upload(char_data.image_url)
            uploaded_file = client.files.upload(file=temp_file_path)
            uploaded_reference_images.append(uploaded_file)
            print(f"✅ Successfully uploaded reference image from Supabase: {char_data.image_url}")
            
            # Clean up temp file
            os.unlink(temp_file_path)
        except Exception as e:
            print(f"❌ Failed to process Supabase image for {char_data.name}: {e}")
            continue
    
    print(f"Total reference images uploaded: {len(uploaded_reference_images)}")
    print(f"Starting generation for {len(scenes)} scenes...")
    
    for i, scene in enumerate(scenes):
        scene_image_url = ""  # Default empty path for failed generations
        print(f"\n=== PROCESSING SCENE {scene.scene_number} ===")
        
        prompt = f""" 
            You are a highly skilled Visual Narrative AI Director and Prompt Engineer for an AI image generation system. 
            Your ultimate goal is to help build dynamic visual narratives by transforming story segments into compelling, high-quality illustrated scenes.

            Generate a high-quality visual narrative image for scene {scene.scene_number} of a dynamic story, titled '{scene.title}'. 
            IMPORTANT: The image MUST be perfectly square with a 1:1 aspect ratio (equal width and height). Generate a square image only.
            The image must contain no inappropriate/NSFW content, text, speech bubbles, or captions. 
            Depict the complete storytelling moment, including all relevant characters, their interactions, expressions, poses, and the environment as described: {scene.image_prompt}. 
            Consider the overarching narrative of this scene: '{scene.narrative_text}'
            
            ASPECT RATIO REQUIREMENT: Generate a square image with 1:1 aspect ratio. Width must equal height.
            """

        print(f"Generating image for scene {scene.scene_number}: '{scene.title or 'Untitled Scene'}'")
        print(f"Scene {scene.scene_number} prompt length: {len(prompt)} characters")
        print(f"Scene {scene.scene_number} image_prompt: {(scene.image_prompt or 'No prompt')[:100]}...")
        print(f"Scene {scene.scene_number} narrative_text: {(scene.narrative_text or 'No narrative')[:100]}...")
        print(f"Using prompt:\n{prompt[:300]}...\n") # Print first 300 chars for brevity

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-preview-image-generation",
                contents=[prompt, uploaded_reference_images],
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE'],
                    candidate_count=1,
                    max_output_tokens=4096,
                    temperature=0.7
                )
            )
            
            # Debug: Print response structure
            print(f"DEBUG: Response type: {type(response)}")
            print(f"DEBUG: Has candidates: {hasattr(response, 'candidates')}")
            print(f"DEBUG: Candidates value: {response.candidates if hasattr(response, 'candidates') else 'No candidates attr'}")
            
            if hasattr(response, 'candidates') and response.candidates is not None and len(response.candidates) > 0:
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

                                # Save image to Supabase storage instead of local file
                                try:
                                    # Upload to Supabase storage and get public URL
                                    scene_image_url = upload_generated_image_to_supabase(
                                        image_bytes, story_name, scene.scene_number
                                    )
                                    print(f"✅ Image uploaded to Supabase storage: {scene_image_url}")
                                    
                                    # Update the database immediately if DAO is provided
                                    if scene_dao and story_id:
                                        success = scene_dao.update_scene_image_url(story_id, scene.scene_number, scene_image_url)
                                        if success:
                                            print(f"💾 Updated scene {scene.scene_number} in database with image URL: {scene_image_url}")
                                        else:
                                            print(f"❌ Failed to update scene {scene.scene_number} in database")
                                    
                                    break # Successfully processed an image
                                    
                                except Exception as upload_error:
                                    print(f"❌ Failed to upload image to Supabase: {upload_error}")
                                    scene_image_url = ""  # Mark as failed
                                
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
                        try:
                            retry_response = client.models.generate_content(
                                model="gemini-2.0-flash-preview-image-generation",
                                contents=[prompt, uploaded_reference_images],
                                config=types.GenerateContentConfig(
                                    response_modalities=['TEXT', 'IMAGE'],
                                    candidate_count=1,
                                    max_output_tokens=4096,
                                    temperature=0.7
                                )
                            )
                            print(f"RETRY: Response type: {type(retry_response)}")
                            if (hasattr(retry_response, 'candidates') and 
                                retry_response.candidates is not None and 
                                len(retry_response.candidates) > 0 and 
                                retry_response.candidates[0].content):
                                # Process the retry response the same way
                                candidate = retry_response.candidates[0]
                                if candidate.content and hasattr(candidate.content, 'parts'):
                                    for part in candidate.content.parts:
                                        if part.inline_data is not None:
                                            try:
                                                image_bytes = part.inline_data.data
                                                output_image = Image.open(BytesIO(image_bytes))
                                                
                                                # Upload retry image to Supabase storage
                                                scene_image_url = upload_generated_image_to_supabase(
                                                    image_bytes, story_name, scene.scene_number
                                                )
                                                print(f"✅ RETRY SUCCESS - uploaded to Supabase: {scene_image_url}")
                                                
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
        print(f"Generated Supabase URL: {scene_image_url}")
        
        # Add a small delay between generations to avoid rate limiting
        if i < len(scenes) - 1:  # Don't delay after the last scene
            print("⏳ Waiting 2 seconds before next generation...")
            time.sleep(2)

    print(f"\n=== FINAL RESULTS ===")
    print(f"Total scenes: {len(scenes)}")
    print(f"Generated images: {len([url for url in generated_image_urls if url])}")
    print(f"Failed generations: {len([url for url in generated_image_urls if not url])}")
    print(f"Supabase URLs: {generated_image_urls}")
    
    return generated_image_urls

def generate_images(client: genai.Client, story_name: str, chars_data: list[User_Character], scenes: list[Scene]):
    """Original function for backward compatibility"""
    return generate_images_with_updates(client, story_name, chars_data, scenes, None, None)
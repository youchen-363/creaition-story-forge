from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import os
from dotenv import load_dotenv
from Scene import Scene 
from User_Character import User_Character

#load_dotenv()
#client = genai.Client(api_key=os.getenv("GEMINI_PAID_API_KEY"))

def generate_images(client: genai.Client, chars_data: list[User_Character], scenes: list[Scene]):
    generated_image_data = []
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True) # Creates 'assets' if it doesn't exist
    uploaded_reference_images = []
    for char_data in chars_data:
        uploaded_file = client.files.upload(file=f"{char_data.img_url}/{char_data.img_name}")
        uploaded_reference_images.append(uploaded_file)
        print(f"Pre-uploaded reference image for analysis: {char_data.img_url}")
    for i, scene in enumerate(scenes):
        # --- THIS IS THE PROMPT YOU WOULD PASS TO THE IMAGEN API ---
        # It's the `image_generation_prompt` directly.
        # You can add a prefix if you want, but the detailed prompt is what matters.
        # imagen_prompt = scene['image_generation_prompt']
        
        # You could also add more general framing like this, but the core is the detailed prompt:
        prompt = (
            f"Without any inappropriate or NSFW content, create an image."
            f"This is scene {scene.scene_nb} of a visual narrative novel."
            f"The scene title is '{scene.title}'. "
            f"Here is the narrative text of this scene '{scene.narrative_text}'"
            f"Here is the detailed visual description and art style guidance for this specific scene: "
            f"{scene.img_prompt}"
        )

        print(f"Generating image for scene {scene.scene_nb}: '{scene.title}'")
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
                                filename = f"scene_{scene.scene_nb}{extension}"
                                file_path = os.path.join(output_dir, filename)

                                # 4. Save the image
                                output_image.save(file_path)
                                print(f"Image saved successfully to: {file_path}")

                                # Store information about the saved image
                                generated_image_data.append({
                                    'scene_number': scene['scene_number'],
                                    'file_path': file_path,
                                    'mime_type': mime_type
                                })
                                break # Successfully processed an image
                                
                            except Exception as img_error:
                                print(f"Error processing image data: {img_error}")
                                print(f"Error type: {type(img_error)}")
                                # Save the problematic data for debugging
                                try:
                                    debug_filename = f"debug_failed_data_scene_{scene['scene_number']}.bin"
                                    with open(debug_filename, 'wb') as f:
                                        f.write(part.inline_data.data)
                                    print(f"DEBUG: Saved binary data to {debug_filename}")
                                except:
                                    pass
                                import traceback
                                traceback.print_exc()
                                continue
                    else:
                        print(f"No valid image part found in response for scene {scene['scene_number']}.")
                else:
                    print(f"No content or parts found in response for scene {scene['scene_number']}.")
                    if hasattr(response, 'prompt_feedback'):
                        print(f"Prompt feedback: {response.prompt_feedback}")
            else:
                print(f"No candidates found in response for scene {scene['scene_number']}.")
                print(f"Full response: {response}")

        except Exception as e:
            print(f"Error generating or saving image for scene {scene['scene_number']}: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()

    return generated_image_data

# Example usage:
# generated_images = generate_comic_images(example_scenes_list, client)
# print(f"\nGenerated {len(generated_images)} images.")
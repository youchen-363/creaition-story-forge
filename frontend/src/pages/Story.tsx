
import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import Header from "@/components/Header";
import { useAuth } from "@/contexts/AuthContext";
import { ChevronLeft, ChevronRight, RotateCcw, Check, Settings, Image, Plus, Coins, Loader2, AlertCircle, Upload } from "lucide-react";

interface StoryData {
  id: string;
  title: string;
  nb_scenes: number;
  nb_chars: number;
  story_mode: string;
  cover_image_url?: string;
  cover_image_name?: string;
  background_story: string;
  future_story: string;
  analysis: string;
  num_scenes: number;
  status: string;
  created_at: string;
  updated_at: string;
  scenes?: any[];
  generated_images?: any[];
}

const Story = () => {
  const { storyId } = useParams<{ storyId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");
  const [storyData, setStoryData] = useState<StoryData | null>(null);
  const [coverImageUrl, setCoverImageUrl] = useState<string>("");
  
  const [currentCharacter, setCurrentCharacter] = useState(0);
  const [characters, setCharacters] = useState([
    { name: "", description: "", image: null as File | null, imageUrl: "" },
    { name: "", description: "", image: null as File | null, imageUrl: "" }
  ]);
  const [storyText, setStoryText] = useState("The different scenes will be displayed here once you start writing...");
  const [backgroundStory, setBackgroundStory] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string>("");

  // Helper function to extract cover image URL from background story
  const extractCoverImageUrl = (backgroundStory: string): { cleanStory: string; imageUrl: string } => {
    const imageMatch = backgroundStory.match(/\[Cover Image: (.*?)\]/);
    if (imageMatch) {
      const imageUrl = imageMatch[1];
      const cleanStory = backgroundStory.replace(/\n\n\[Cover Image: .*?\]/, '');
      return { cleanStory, imageUrl };
    }
    return { cleanStory: backgroundStory, imageUrl: '' };
  };

  // Fetch story data when component mounts or storyId changes
  useEffect(() => {
    if (storyId) {
      fetchStoryData(storyId);
    } else {
      setLoading(false);
      setStoryText("No story selected. Please create a new story or select one from your history.");
    }
  }, [storyId]);

  const fetchStoryData = async (id: string) => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`http://localhost:8002/api/stories/${id}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error("Story not found");
        }
        throw new Error(`Failed to load story: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success && result.story) {
        console.log(result.story)
        setStoryData(result.story);
        
        // Extract cover image URL from background story
        if (result.story.background_story) {
          const { cleanStory, imageUrl } = extractCoverImageUrl(result.story.background_story);
          setCoverImageUrl(imageUrl);
          setBackgroundStory(cleanStory); // Set the background story
          // Update the story data with clean background story
          setStoryData(prev => prev ? { ...prev, background_story: cleanStory } : null);
        }
        
        // Update characters based on story data or initialize default
        if (result.story.characters && result.story.characters.length > 0) {
          // Load existing characters from story data
          const loadedCharacters = result.story.characters.map((char: any) => ({
            name: char.name || "",
            description: char.description || "",
            image: null as File | null,
            imageUrl: ""
          }));
          setCharacters(loadedCharacters);
        } else {
          // Initialize default characters based on nb_chars
          const numCharacters = result.story.nb_chars || 2;
          const initialCharacters = Array(numCharacters).fill(null).map(() => ({
            name: "",
            description: "",
            image: null as File | null,
            imageUrl: ""
          }));
          setCharacters(initialCharacters);
        }

        // Set story text based on status
        if (result.story.status === 'completed' && result.story.future_story) {
          setStoryText(result.story.future_story);
        } else if (result.story.status === 'generating') {
          setStoryText("🎨 Your story is being generated... This may take a few minutes. Please check back soon!");
        } else if (result.story.status === 'failed') {
          setStoryText("❌ Story generation failed. Please try creating the story again.");
        } else {
          const { cleanStory } = extractCoverImageUrl(result.story.background_story || "");
          setStoryText(cleanStory || "Your story will be displayed here once you start writing...");
        }
      } else {
        setError("Failed to load story data");
      }
    } catch (err: any) {
      console.error("Error fetching story:", err);
      setError(err.message || "Failed to load story");
    } finally {
      setLoading(false);
    }
  };

  const updateCharacter = (index: number, field: string, value: string) => {
    const updatedCharacters = [...characters];
    updatedCharacters[index] = { ...updatedCharacters[index], [field]: value };
    setCharacters(updatedCharacters);
  };

  const handleCharacterImageUpload = async (index: number, e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadError("");

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('name', 'Character Image');
      formData.append('description', 'Character image for the story');

      const response = await fetch('http://localhost:8002/api/characters/upload', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        const updatedCharacters = [...characters];
        updatedCharacters[index] = { 
          ...updatedCharacters[index], 
          image: file,
          imageUrl: `http://localhost:8002${result.image_url}`
        };
        setCharacters(updatedCharacters);
        console.log('Character image uploaded successfully:', result);
      } else {
        setUploadError(result.error || 'Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadError('Failed to upload image');
    } finally {
      setIsUploading(false);
    }
  };

  const removeCharacterImage = (index: number) => {
    const updatedCharacters = [...characters];
    updatedCharacters[index] = { 
      ...updatedCharacters[index], 
      image: null,
      imageUrl: ""
    };
    setCharacters(updatedCharacters);
    setUploadError("");
  };

  const handleWrite = async () => {
    if (!storyId) {
      console.error("No story ID available");
      return;
    }

    try {
      // Validate required fields
      if (!backgroundStory.trim()) {
        alert("Please write a background story before generating the narrative.");
        return;
      }
      
      // Check if ALL characters have complete information (name, description, and image)
      const expectedCharacterCount = storyData?.nb_chars || 2;
      const validCharacters = characters.filter(char => 
        char.name.trim() !== "" && 
        char.description.trim() !== "" && 
        char.imageUrl
      );
      
      if (validCharacters.length < expectedCharacterCount) {
        const missingCount = expectedCharacterCount - validCharacters.length;
        alert(`Please provide complete information (name, description, and image) for all ${expectedCharacterCount} characters. You are missing ${missingCount} character(s).`);
        return;
      }

      setStoryText("🎨 Generating your story... This may take a few minutes. Please wait...");

      // First, save the background story and characters to the story
      const storyUpdateData = {
        title: storyData?.title || "Untitled Story",
        nb_scenes: storyData?.nb_scenes || 4,
        nb_chars: storyData?.nb_chars || 2,
        story_mode: storyData?.story_mode || "adventure",
        user_email: user?.email || "test@example.com", // Use actual user email
        cover_image_url: storyData?.cover_image_url || null,
        cover_image_name: storyData?.cover_image_name || null,
        background_story: backgroundStory // Add background story to save to DB
      };
      
      // First, update the story with background story and basic info
      console.log(storyId)
      console.log(JSON.stringify(storyUpdateData))
      const updateResponse = await fetch(`http://localhost:8002/api/stories/${storyId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(storyUpdateData),
      });
      console.log(updateResponse)

      if (!updateResponse.ok) {
        throw new Error("Failed to save story data");
      }

      const updateResult = await updateResponse.json();
      if (!updateResult.success) {
        throw new Error(updateResult.message || "Failed to update story");
      }

      // Save/update characters for this story
      const charactersToSave = characters.filter(char => char.name.trim() !== "");
      
      if (charactersToSave.length > 0) {
        const charactersData = {
          story_id: storyId,
          characters: charactersToSave.map(char => ({
            name: char.name,
            description: char.description,
            img_url: char.imageUrl || null,
            img_name: char.image ? char.image.name : null
          }))
        };

        const updateCharsResponse = await fetch(`http://localhost:8002/api/stories/${storyId}/characters`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(charactersData),
        });

        if (!updateCharsResponse.ok) {
          console.warn("Failed to save characters, but continuing with story generation");
        } else {
          const charsResult = await updateCharsResponse.json();
          if (charsResult.success) {
            console.log("Characters saved successfully:", charsResult);
          } else {
            console.warn("Characters save returned error:", charsResult.message);
          }
        }
      }

      // Now call the AI generation API
      const generateData = {
        title: storyData?.title || "Untitled Story",
        nb_scenes: storyData?.nb_scenes || 4,
        nb_chars: storyData?.nb_chars || 2,
        story_mode: storyData?.story_mode || "adventure",
        user_id: storyId, // Use story ID as user ID for now
        cover_image_url: storyData?.cover_image_url || null,
        cover_image_name: storyData?.cover_image_name || null,
        background_story: backgroundStory,
        future_story: "",
        characters: validCharacters.map(char => ({
          name: char.name,
          desc: char.description,
          img_url: char.imageUrl || null,  // Send the image URL as img_url
          img_name: char.image ? char.image.name : null  // Send the image filename as img_name
        }))
      };

      console.log('Generating story with data:', generateData);

      const generateResponse = await fetch('http://localhost:8002/api/stories/generate-story', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(generateData),
      });

      const generateResult = await generateResponse.json();

      if (generateResult.success) {
        setStoryText("✅ Story generation started successfully! The AI is now creating your narrative. Please check back in a few minutes to see the results.");
        
        // Refresh story data after a short delay
        setTimeout(() => {
          fetchStoryData(storyId);
        }, 2000);
      } else {
        setStoryText("❌ Failed to generate story. Please try again.");
        console.error('Story generation failed:', generateResult);
      }

    } catch (error: any) {
      console.error('Error generating story:', error);
      setStoryText("❌ An error occurred while generating the story. Please try again.");
    }
  };

  const handleRewrite = () => {
    // Call handleWrite to regenerate the story with current data
    handleWrite();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
      <Header />
      
      <main className="pt-20 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Loading State */}
          {loading && (
            <div className="text-center py-12">
              <Loader2 className="w-16 h-16 text-purple-600 mx-auto mb-4 animate-spin" />
              <p className="text-gray-600">Loading your story...</p>
            </div>
          )}

          {/* Error State */}
          {error && !loading && (
            <div className="text-center py-12">
              <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md mx-auto">
                <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                <p className="text-red-600 mb-4">{error}</p>
                <div className="space-x-4">
                  <Button 
                    onClick={() => storyId && fetchStoryData(storyId)}
                    variant="outline"
                    className="border-red-300 text-red-600 hover:bg-red-50"
                  >
                    Try Again
                  </Button>
                  <Button 
                    onClick={() => navigate('/history')}
                    className="bg-purple-600 hover:bg-purple-700"
                  >
                    Back to History
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Story Content */}
          {!loading && !error && (
            <>
              <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 text-center">
                  {storyData?.title || "Untitled Story"}
                </h1>
              </div>

              {/* Cover Image Display */}
              {coverImageUrl && (
                <div className="mb-8 text-center">
                  <div className="inline-block rounded-lg overflow-hidden shadow-lg border-2 border-gray-200">
                    <img
                      src={coverImageUrl}
                      alt="Story Cover"
                      className="max-w-xs max-h-48 object-cover"
                    />
                  </div>
                  <p className="text-sm text-gray-500 mt-2">Story Cover Image</p>
                </div>
              )}

              {/* Background Story Section */}
              <div className="mb-8">
                <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
                  <CardContent className="p-6">
                    <div className="space-y-2">
                      <Label htmlFor="background-story">
                        Write the story that will set the foundation for your visual narrative
                      </Label>
                      <Textarea
                        id="background-story"
                        placeholder="Enter the story that will guide the AI in generating your visual narrative. Describe the setting, initial situation, and any key elements you want to include..."
                        value={backgroundStory}
                        onChange={(e) => setBackgroundStory(e.target.value)}
                        className="bg-white min-h-[120px] resize-none"
                      />
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Character Section */}
              <div className="mb-8">
            <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => setCurrentCharacter(Math.max(0, currentCharacter - 1))}
                    disabled={currentCharacter === 0}
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  
                  <h2 className="text-xl font-semibold">Character {currentCharacter + 1}</h2>
                  
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => setCurrentCharacter(Math.min(characters.length - 1, currentCharacter + 1))}
                    disabled={currentCharacter === characters.length - 1}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Character Image */}
                  <div className="space-y-2">
                    <div className="w-full max-w-[280px] mx-auto">
                      <Label className="block text-left">Character Image</Label>
                    </div>
                    <div className="w-full max-w-[280px] aspect-[4/5] border-2 border-dashed border-gray-300 rounded-lg p-4 bg-white hover:border-purple-400 transition-colors mx-auto">
                      <div className="text-center h-full">
                        {isUploading ? (
                          <div className="space-y-2 flex flex-col items-center justify-center h-full">
                            <Loader2 className="w-12 h-12 text-purple-600 animate-spin" />
                            <p className="text-sm text-gray-600">Uploading image...</p>
                          </div>
                        ) : characters[currentCharacter].imageUrl ? (
                          <div className="space-y-3 h-full flex flex-col">
                            <div className="flex-1 rounded-lg overflow-hidden border-2 border-gray-200">
                              <img
                                src={characters[currentCharacter].imageUrl}
                                alt="Character"
                                className="w-full h-full object-contain bg-gray-50"
                              />
                            </div>
                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              onClick={() => removeCharacterImage(currentCharacter)}
                            >
                              Remove
                            </Button>
                          </div>
                        ) : (
                          <div className="space-y-3 flex flex-col items-center justify-center h-full">
                            <Upload className="w-12 h-12 text-gray-400" />
                            <p className="text-gray-500 text-sm">Upload a character image</p>
                            <input
                              type="file"
                              accept="image/*"
                              onChange={(e) => handleCharacterImageUpload(currentCharacter, e)}
                              className="hidden"
                              id={`character-image-upload-${currentCharacter}`}
                            />
                            <Button
                              type="button"
                              variant="outline"
                              onClick={() => document.getElementById(`character-image-upload-${currentCharacter}`)?.click()}
                            >
                              Choose Image
                            </Button>
                          </div>
                        )}
                        {uploadError && (
                          <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                            <p className="text-red-600 text-sm">{uploadError}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Character Details */}
                  <div className="lg:col-span-2 space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="character-name">Name</Label>
                      <Input
                        id="character-name"
                        placeholder="Character name"
                        value={characters[currentCharacter].name}
                        onChange={(e) => updateCharacter(currentCharacter, 'name', e.target.value)}
                        className="bg-white"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="character-description">Description</Label>
                      <Textarea
                        id="character-description"
                        placeholder="Describe your character's appearance, personality, and background..."
                        value={characters[currentCharacter].description}
                        onChange={(e) => updateCharacter(currentCharacter, 'description', e.target.value)}
                        className="bg-white min-h-[200px] lg:min-h-[280px] resize-none"
                      />
                    </div>
                  </div>
                </div>

                <div className="mt-6 text-center">
                  <Button 
                    onClick={handleWrite}
                    className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 px-8"
                  >
                    Write
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Story Section */}
          <div className="space-y-8">
            {/* Storyline */}
            <div>
              <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold mb-4">Storyline</h3>
                  <div className="bg-gray-50 rounded-lg p-4 min-h-[200px] max-h-[300px] overflow-y-auto">
                    <p className="text-gray-700 leading-relaxed">{storyText}</p>
                  </div>
                  <div className="flex items-center justify-between mt-4">
                    <div className="flex space-x-2">
                      <Button 
                        variant="destructive"
                        onClick={handleRewrite}
                        className="flex items-center"
                      >
                        <RotateCcw className="w-4 h-4 mr-2" />
                        Rewrite
                      </Button>
                      <Button variant="default" className="bg-green-600 hover:bg-green-700">
                        <Check className="w-4 h-4" /> Draw
                      </Button>
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <Coins className="w-4 h-4 mr-1" />
                      {storyData?.nb_scenes || 4} credits/Draw ({storyData?.nb_scenes || 4} scenes × 1 credit/scene)
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Storybook View */}
            <div>
              <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
                <CardContent className="p-0">
                  <div className="grid grid-cols-4 gap-0">
                    {Array.from({ length: storyData?.nb_scenes || 4 }, (_, index) => (
                      <div key={index} className="flex flex-col">
                        {/* Square Image Box */}
                        <div className="aspect-square bg-gradient-to-br from-purple-100 to-blue-100 flex items-center justify-center border border-gray-300">
                          <div className="text-center">
                            <Image className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                            <p className="text-xs text-gray-500">Scene {index + 1}</p>
                          </div>
                        </div>
                        {/* Scene Name Below */}
                        <div className="p-2 bg-white">
                          <p className="text-xs text-gray-700 text-center font-medium">
                            Scene {index + 1}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Action Buttons */}
              <div className="flex justify-end space-x-2 mt-4">
                <Button variant="outline">
                  <RotateCcw className="w-4 h-4 mr-2" />
                  Redraw
                </Button>
                <Button variant="outline">
                  <Image className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
            </>
          )}
        </div>
      </main>

      {/* Floating Edit Parameters Button - Fixed to viewport */}
      <Button 
        className="fixed bottom-6 right-6 z-50 shadow-lg hover:shadow-xl transition-shadow bg-purple-600 hover:bg-purple-700 text-white rounded-full w-14 h-14 p-0"
        size="icon"
        title="Edit Parameters"
        onClick={() => navigate(`/story/${storyId}/edit`)}
      >
        <Settings className="w-5 h-5" />
      </Button>
    </div>
  );
};

export default Story;

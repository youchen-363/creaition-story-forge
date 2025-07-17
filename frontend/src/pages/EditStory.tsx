import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Loader2, Save, ArrowLeft, Upload, X, AlertCircle, Check, ChevronsUpDown } from "lucide-react";
import { cn } from "@/lib/utils";
import Header from "@/components/Header";
import { useAuth } from "@/contexts/AuthContext";

interface StoryData {
  id: string;
  title: string;
  nb_scenes: number;
  nb_chars: number;
  story_mode: string;
  cover_img_url?: string;
  cover_img_name?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

const EditStory = () => {
  const { storyId } = useParams<{ storyId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  // Form state
  const [title, setTitle] = useState("");
  const [numscenes, setNumscenes] = useState(4);
  const [numCharacters, setNumCharacters] = useState(2);
  const [storyMode, setStoryMode] = useState("");
  const [storyImage, setStoryImage] = useState<File | null>(null);
  const [uploadedImageUrl, setUploadedImageUrl] = useState<string>("");
  
  // UI state
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string>("");
  const [saveError, setSaveError] = useState<string>("");
  const [uploadError, setUploadError] = useState<string>("");
  const [open, setOpen] = useState(false);

  // Predefined story modes
  const storyModes = [
    { value: "horror", label: "Horror" },
    { value: "fantasy", label: "Fantasy" },
    { value: "sci-fi", label: "Sci-Fi" },
    { value: "comedy", label: "Comedy" },
    { value: "adventure", label: "Adventure" },
    { value: "romance", label: "Romance" },
    { value: "mystery", label: "Mystery" },
    { value: "drama", label: "Drama" },
    { value: "thriller", label: "Thriller" },
    { value: "western", label: "Western" },
    { value: "historical", label: "Historical" },
    { value: "biographical", label: "Biographical" }
  ];

  // Load story data when component mounts
  useEffect(() => {
    if (storyId) {
      fetchStoryData(storyId);
    } else {
      setError("No story ID provided");
      setLoading(false);
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
        const story = result.story;
        
        // Fill form with existing data
        setTitle(story.title || "");
        setNumscenes(story.nb_scenes || 4);
        setNumCharacters(story.nb_chars || 2);
        setStoryMode(story.story_mode || "");
        setUploadedImageUrl(story.cover_img_url || "");
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

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadError("");

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('name', 'Story Cover');
      formData.append('description', 'Cover image for the story');

      const response = await fetch('http://localhost:8002/api/characters/upload', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        setStoryImage(file);
        setUploadedImageUrl(`http://localhost:8002${result.image_url}`);
        console.log('Image uploaded successfully:', result);
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

  const removeImage = () => {
    setStoryImage(null);
    setUploadedImageUrl("");
    setUploadError("");
  };

  const handleSave = async () => {
    setSaving(true);
    setSaveError("");

    // Validate required fields
    if (!title.trim()) {
      setSaveError("Please enter a story title");
      setSaving(false);
      return;
    }

    try {
      // Prepare story data for backend
      const storyData = {
        title,
        nb_scenes: numscenes,
        nb_chars: numCharacters,
        story_mode: storyMode || null, // Allow empty story mode
        user_email: user?.email || "test@example.com",
        cover_img_url: uploadedImageUrl || null,
        cover_img_name: storyImage?.name || null
      };

      console.log('Updating story data:', storyData);

      // Call update API endpoint
      const response = await fetch(`http://localhost:8002/api/stories/${storyId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(storyData),
      });

      const result = await response.json();

      if (result.success) {
        console.log('Story updated successfully');
        // Navigate back to the story scene
        navigate(`/story/${storyId}`);
      } else {
        setSaveError(result.message || "Failed to update story");
      }
    } catch (error: any) {
      console.error('Error updating story:', error);
      setSaveError(error.message || "An error occurred while updating the story");
    } finally {
      setSaving(false);
    }
  };

  const handleBack = () => {
    navigate(`/story/${storyId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
        <Header />
        <main className="pt-20 pb-12">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center py-12">
              <Loader2 className="w-16 h-16 text-purple-600 mx-auto mb-4 animate-spin" />
              <p className="text-gray-600">Loading story data...</p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
        <Header />
        <main className="pt-20 pb-12">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center py-12">
              <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md mx-auto">
                <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                <p className="text-red-600 mb-4">{error}</p>
                <Button onClick={handleBack} className="bg-purple-600 hover:bg-purple-700">
                  Back to Story
                </Button>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
      <Header />
      
      <main className="pt-20 pb-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div 
                  onClick={handleBack}
                  className="p-2 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                >
                  <ArrowLeft className="w-5 h-5" />
                </div>
                <CardTitle className="text-2xl text-center text-purple-700 flex-1">
                  Update Your Story Details
                </CardTitle>
                <div className="w-9"></div> {/* Spacer to center the title */}
              </div>
            </CardHeader>
            <CardContent>
              <form className="space-y-6">
                {/* Error Message */}
                {saveError && (
                  <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
                    {saveError}
                  </div>
                )}

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Left Side - Story Details */}
                  <div className="lg:col-span-2 space-y-6">
                    <div className="space-y-2">
                      <Label htmlFor="title">Title <span className="text-red-500">*</span></Label>
                      <Input
                        id="title"
                        placeholder="Enter your story title"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        required
                        className="bg-white"
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="scenes">Number of scenes <span className="text-red-500">*</span></Label>
                        <Input
                          id="scenes"
                          type="number"
                          min="1"
                          max="50"
                          value={numscenes}
                          onChange={(e) => {
                            const newScenes = parseInt(e.target.value);
                            setNumscenes(newScenes);
                            // Auto-adjust characters to not exceed the new limit
                            const maxChars = newScenes * 2;
                            if (numCharacters > maxChars) {
                              setNumCharacters(maxChars);
                            }
                          }}
                          className="bg-white"
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="characters">Number of Characters (max {numscenes * 2}) <span className="text-red-500">*</span></Label>
                        <Input
                          id="characters"
                          type="number"
                          min="1"
                          max={numscenes * 2}
                          value={numCharacters}
                          onChange={(e) => setNumCharacters(parseInt(e.target.value))}
                          className="bg-white"
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label>Story Mode</Label>
                      <Popover open={open} onOpenChange={setOpen}>
                        <PopoverTrigger asChild>
                          <Button
                            variant="outline"
                            role="combobox"
                            aria-expanded={open}
                            className="w-full justify-between bg-white"
                          >
                            {storyMode
                              ? storyModes.find((mode) => mode.value === storyMode)?.label || storyMode
                              : "Choose your story genre or type a custom one..."}
                            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-full p-0">
                          <Command>
                            <CommandInput 
                              placeholder="Search story modes or type a custom one..." 
                              onValueChange={(value) => {
                                // Allow typing custom story modes
                                if (value && !storyModes.find(mode => mode.value === value)) {
                                  setStoryMode(value);
                                }
                              }}
                            />
                            <CommandList>
                              <CommandEmpty>
                                <div className="p-2">
                                  <p className="text-sm text-gray-500 mb-2">No predefined mode found.</p>
                                  <Button
                                    size="sm"
                                    className="w-full"
                                    onClick={() => {
                                      const input = document.querySelector('input[placeholder="Search story modes or type a custom one..."]') as HTMLInputElement;
                                      if (input?.value) {
                                        setStoryMode(input.value);
                                        setOpen(false);
                                      }
                                    }}
                                  >
                                    Use Custom Mode
                                  </Button>
                                </div>
                              </CommandEmpty>
                              <CommandGroup>
                                {storyModes.map((mode) => (
                                  <CommandItem
                                    key={mode.value}
                                    value={mode.value}
                                    onSelect={(currentValue) => {
                                      setStoryMode(currentValue === storyMode ? "" : currentValue);
                                      setOpen(false);
                                    }}
                                  >
                                    <Check
                                      className={cn(
                                        "mr-2 h-4 w-4",
                                        storyMode === mode.value ? "opacity-100" : "opacity-0"
                                      )}
                                    />
                                    {mode.label}
                                  </CommandItem>
                                ))}
                              </CommandGroup>
                            </CommandList>
                          </Command>
                        </PopoverContent>
                      </Popover>
                      {storyMode && !storyModes.find(mode => mode.value === storyMode) && (
                        <p className="text-sm text-blue-600">
                          ✨ Using custom story mode: "{storyMode}"
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Right Side - Story Cover Image */}
                  <div className="space-y-2">
                    <div className="w-full max-w-[280px] mx-auto lg:mx-0">
                      <Label className="block text-left">Story Cover Image</Label>
                    </div>
                    <div className="w-full max-w-[280px] aspect-[4/5] border-2 border-dashed border-gray-300 rounded-lg p-4 bg-white hover:border-purple-400 transition-colors mx-auto lg:mx-0">
                      <div className="text-center h-full">
                        {isUploading ? (
                          <div className="space-y-2 flex flex-col items-center justify-center h-full">
                            <Loader2 className="w-12 h-12 text-purple-600 animate-spin" />
                            <p className="text-sm text-gray-600">Uploading image...</p>
                          </div>
                        ) : uploadedImageUrl ? (
                          <div className="space-y-3 h-full flex flex-col">
                            <div className="flex-1 rounded-lg overflow-hidden border-2 border-gray-200">
                              <img
                                src={uploadedImageUrl}
                                alt="Uploaded story cover"
                                className="w-full h-full object-contain bg-gray-50"
                              />
                            </div>
                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              onClick={removeImage}
                            >
                              Remove
                            </Button>
                          </div>
                        ) : (
                          <div className="space-y-3 flex flex-col items-center justify-center h-full">
                            <Upload className="w-12 h-12 text-gray-400" />
                            <p className="text-gray-500 text-sm">Upload a story cover image</p>
                            <input
                              id="story-image"
                              type="file"
                              accept="image/*"
                              onChange={handleImageUpload}
                              className="hidden"
                            />
                            <Button
                              type="button"
                              variant="outline"
                              onClick={() => document.getElementById('story-image')?.click()}
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
                </div>

                <Button 
                  type="button"
                  onClick={handleSave}
                  disabled={saving || !title}
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 py-6 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Saving Changes...
                    </>
                  ) : (
                    <>
                      Save Changes
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default EditStory;

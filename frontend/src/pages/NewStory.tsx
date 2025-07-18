
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import Header from "@/components/Header";
import { Upload, Plus, Loader2, Check, ChevronsUpDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { API_URL } from '../lib/config';

const NewStory = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [title, setTitle] = useState("");
  const [numscenes, setNumscenes] = useState(4);
  const [numCharacters, setNumCharacters] = useState(2);
  const [storyMode, setStoryMode] = useState("");
  const [storyImage, setStoryImage] = useState<File | null>(null);
  const [uploadedImageUrl, setUploadedImageUrl] = useState<string>("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string>("");
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitError("");

    // Validate required fields
    if (!title.trim()) {
      setSubmitError("Please enter a story title");
      setIsSubmitting(false);
      return;
    }

    try {
      // First, create the story record without cover image
      const storyData = {
        title,
        nb_scenes: numscenes,
        nb_chars: numCharacters,
        story_mode: storyMode || null, // Allow empty story mode
        user_email: user?.email || "test@example.com", // Send email instead of user_id
        cover_image_url: null, // Will be updated after image upload
        cover_image_name: null
      };

      console.log('Creating story:', storyData);

      // Create the story record first
      const response = await fetch(`${API_URL}stories/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(storyData),
      });

      const result = await response.json();
      
      if (result.success && result.story_id) {
        console.log("Story created successfully:", result);
        
        // Now upload the cover image with the proper story ID if there's an image
        if (storyImage) {
          try {
            console.log("Uploading cover image with story ID:", result.story_id);
            const formData = new FormData();
            formData.append('file', storyImage);
            
            const uploadResponse = await fetch(`${API_URL}stories/${result.story_id}/cover/upload`, {
              method: 'POST',
              body: formData,
            });

            const uploadResult = await uploadResponse.json();
          
            if (uploadResult.success) {
              console.log("Cover image uploaded successfully:", uploadResult.filename);
              // Update the story with the new cover image URL
              const updateStoryData = {
                title,
                nb_scenes: numscenes,
                nb_chars: numCharacters,
                story_mode: storyMode || null,
                user_email: user?.email || "test@example.com",
                cover_image_url: uploadResult.image_url,
                cover_image_name: uploadResult.filename
              };
              
              // Update the story record with the new image URL
              const updateResponse = await fetch(`${API_URL}stories/${result.story_id}`, {
                method: 'PUT',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify(updateStoryData),
              });
              
              if (!updateResponse.ok) {
                console.warn("Failed to update story with new cover image URL");
              } else {
                console.log("Story updated with cover image URL");
              }
            } else {
              console.warn("Failed to upload cover image:", uploadResult.error);
            }
          } catch (uploadError) {
            console.warn("Error uploading cover image:", uploadError);
            // Don't fail the story creation for this
          }
        }
        
        // Always redirect to Story page for further processing
        navigate(`/story/${result.story_id}`);
      } else {
        // Handle specific database permission errors
        if (result.message && result.message.includes('row-level security policy')) {
          setSubmitError('Database permissions need to be configured. Please contact support or check your authentication.');
        } else {
          setSubmitError(result.message || 'Failed to create story');
        }
      }
    } catch (error) {
      console.error('Story creation error:', error);
      if (error instanceof Error && error.message.includes('row-level security')) {
        setSubmitError('Database permissions need to be configured. Please contact support.');
      } else {
        setSubmitError('Failed to create story. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadError("");

    try {
      // Just store the file locally and create a preview URL
      setStoryImage(file);
      const previewUrl = URL.createObjectURL(file);
      setUploadedImageUrl(previewUrl);
      console.log('Image selected for upload:', file.name);
    } catch (error) {
      console.error('Error handling image file:', error);
      setUploadError('Failed to process image');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
      <Header />
      
      <main className="pt-20 pb-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-2xl text-center text-purple-700">
                New Story
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Error Message */}
                {submitError && (
                  <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
                    {submitError}
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
                                onLoad={() => console.log(`🖼️ Image loaded: ${uploadedImageUrl}`)}
                                onError={(e) => console.error(`❌ Image failed to load: ${uploadedImageUrl}`, e)}
                              />
                            </div>
                            <div className="text-xs text-gray-500 text-center">
                              {storyImage?.name || 'Selected image'}
                            </div>
                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                // Clean up the preview URL if it's a blob URL
                                if (uploadedImageUrl.startsWith('blob:')) {
                                  URL.revokeObjectURL(uploadedImageUrl);
                                }
                                setStoryImage(null);
                                setUploadedImageUrl("");
                                setUploadError("");
                              }}
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
                  type="submit" 
                  disabled={isSubmitting || !title}
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 py-6 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Creating Story...
                    </>
                  ) : (
                    "Create Story"
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

export default NewStory;

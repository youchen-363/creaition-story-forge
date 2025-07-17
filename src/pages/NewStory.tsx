
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Header from "@/components/Header";
import { Upload, Plus } from "lucide-react";

const NewStory = () => {
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [numPages, setNumPages] = useState(5);
  const [numCharacters, setNumCharacters] = useState(2);
  const [storyMode, setStoryMode] = useState("");
  const [storyImage, setStoryImage] = useState<File | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real app, this would save the story data
    console.log("New story:", { title, numPages, numCharacters, storyMode, storyImage });
    navigate("/story");
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setStoryImage(file);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
      <Header isAuthenticated={true} username="Creator" credits={150} />
      
      <main className="pt-20 pb-12">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">New Story</h1>
            <p className="text-lg text-gray-600">Set up the foundation for your next creative masterpiece</p>
          </div>

          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl">Story Details</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="title">Title</Label>
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
                    <Label htmlFor="pages">Number of Pages</Label>
                    <Input
                      id="pages"
                      type="number"
                      min="1"
                      max="50"
                      value={numPages}
                      onChange={(e) => setNumPages(parseInt(e.target.value))}
                      className="bg-white"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="characters">Number of Characters</Label>
                    <Input
                      id="characters"
                      type="number"
                      min="1"
                      max="10"
                      value={numCharacters}
                      onChange={(e) => setNumCharacters(parseInt(e.target.value))}
                      className="bg-white"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Story Mode</Label>
                  <Select value={storyMode} onValueChange={setStoryMode} required>
                    <SelectTrigger className="bg-white">
                      <SelectValue placeholder="Choose your story genre" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="horror">Horror</SelectItem>
                      <SelectItem value="fantasy">Fantasy</SelectItem>
                      <SelectItem value="sci-fi">Sci-Fi</SelectItem>
                      <SelectItem value="comedy">Comedy</SelectItem>
                      <SelectItem value="adventure">Adventure</SelectItem>
                      <SelectItem value="romance">Romance</SelectItem>
                      <SelectItem value="mystery">Mystery</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Story Cover Image</Label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 bg-white hover:border-purple-400 transition-colors">
                    <div className="text-center">
                      {storyImage ? (
                        <div className="space-y-2">
                          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                            <span className="text-green-600 font-medium">✓</span>
                          </div>
                          <p className="text-sm text-gray-600">Image uploaded: {storyImage.name}</p>
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => setStoryImage(null)}
                          >
                            Remove
                          </Button>
                        </div>
                      ) : (
                        <div className="space-y-2">
                          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto">
                            <Plus className="w-8 h-8 text-gray-400" />
                          </div>
                          <div>
                            <label htmlFor="story-image" className="cursor-pointer">
                              <span className="text-purple-600 font-medium hover:text-purple-700">
                                Click to upload
                              </span>
                              <span className="text-gray-500"> or drag and drop</span>
                            </label>
                            <input
                              id="story-image"
                              type="file"
                              accept="image/*"
                              onChange={handleImageUpload}
                              className="hidden"
                            />
                          </div>
                          <p className="text-xs text-gray-400">PNG, JPG up to 5MB</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                <Button 
                  type="submit" 
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 py-6 text-lg"
                >
                  Start Creating
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

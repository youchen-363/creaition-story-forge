
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import Header from "@/components/Header";
import { ChevronLeft, ChevronRight, RotateCcw, Check, Settings, Image, Plus, Coins } from "lucide-react";

const Story = () => {
  const [currentCharacter, setCurrentCharacter] = useState(0);
  const [characters, setCharacters] = useState([
    { name: "", description: "", image: null as File | null },
    { name: "", description: "", image: null as File | null }
  ]);
  const [storyText, setStoryText] = useState("Your story will be displayed here once you start writing...");
  const [storyTitle] = useState("The Enchanted Quest"); // This would come from the new story form

  const updateCharacter = (index: number, field: string, value: string) => {
    const updatedCharacters = [...characters];
    updatedCharacters[index] = { ...updatedCharacters[index], [field]: value };
    setCharacters(updatedCharacters);
  };

  const handleCharacterImageUpload = (index: number, file: File) => {
    const updatedCharacters = [...characters];
    updatedCharacters[index] = { ...updatedCharacters[index], image: file };
    setCharacters(updatedCharacters);
  };

  const handleWrite = () => {
    setStoryText("Once upon a time, in a mystical realm where magic flowed through every living creature, there lived a young adventurer named Aria. She possessed an extraordinary gift that set her apart from others in her village...");
  };

  const handleRewrite = () => {
    setStoryText("In the distant lands of Aethermoor, where ancient secrets whispered through the winds, a brave soul embarked on a journey that would change the fate of two worlds. The story begins with our hero standing at the crossroads of destiny...");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
      <Header isAuthenticated={true} username="Creator" credits={145} />
      
      <main className="pt-20 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 text-center">{storyTitle}</h1>
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
                    <Label>Character Image</Label>
                    <div className="aspect-square border-2 border-dashed border-gray-300 rounded-lg p-4 bg-gray-50 hover:border-purple-400 transition-colors">
                      {characters[currentCharacter].image ? (
                        <div className="w-full h-full bg-gray-200 rounded-lg flex items-center justify-center">
                          <span className="text-gray-500">Image Uploaded</span>
                        </div>
                      ) : (
                        <div className="w-full h-full flex flex-col items-center justify-center cursor-pointer">
                          <Plus className="w-12 h-12 text-gray-400 mb-2" />
                          <span className="text-sm text-gray-500">Upload Image</span>
                          <input
                            type="file"
                            accept="image/*"
                            onChange={(e) => {
                              const file = e.target.files?.[0];
                              if (file) handleCharacterImageUpload(currentCharacter, file);
                            }}
                            className="hidden"
                          />
                        </div>
                      )}
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
                        className="bg-white h-32"
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
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Storyline */}
            <div className="space-y-6">
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
                        <Check className="w-4 h-4" />
                      </Button>
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <Coins className="w-4 h-4 mr-1" />
                      5 credits/Draw + ✓
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Storybook View */}
            <div className="space-y-6">
              <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm h-[400px]">
                <CardContent className="p-0 h-full">
                  <div className="grid grid-cols-2 h-full">
                    {/* Image Panel */}
                    <div className="bg-gradient-to-br from-purple-100 to-blue-100 flex items-center justify-center border-r">
                      <div className="text-center">
                        <Image className="w-16 h-16 text-gray-400 mx-auto mb-2" />
                        <p className="text-gray-500">Generated Image</p>
                      </div>
                    </div>
                    {/* Text Panel */}
                    <div className="p-4 overflow-y-auto">
                      <p className="text-sm text-gray-700 leading-relaxed">
                        The story page content will appear here once generated. This panel will contain the narrative text that corresponds to the image on the left.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Action Buttons */}
              <div className="flex justify-end space-x-2">
                <Button variant="outline">
                  <RotateCcw className="w-4 h-4 mr-2" />
                  Redraw
                </Button>
                <Button variant="outline">
                  <Image className="w-4 h-4" />
                </Button>
                <Button variant="outline">
                  <Settings className="w-4 h-4 mr-2" />
                  Edit Parameters
                </Button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Story;

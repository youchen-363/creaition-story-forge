
import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Header from "@/components/Header";
import { ChevronLeft, ChevronRight, BookOpen, Loader2 } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { API_URL } from '../lib/config';

interface Story {
  id: string;
  title: string;
  status: string;
  cover_image_url: string;
  created_at: string;
  updated_at: string;
  nb_scenes: number;
  nb_chars: number;
  story_mode: string;
}

const History = () => {
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");
  const { user } = useAuth();

  const fetchUserStories = async () => {
    try {
      setLoading(true);
      setError("");

      if (!user?.email) {
        setError("Please log in to view your stories");
        return;
      }

      const response = await fetch(`${API_URL}user/stories?user_email=${encodeURIComponent(user.email)}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch stories: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        setStories(result.stories || []);
      } else {
        setError(result.message || "Failed to load stories");
      }
    } catch (err) {
      console.error("Error fetching stories:", err);
      setError("Unable to load stories. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.email) {
      fetchUserStories();
    } else {
      setLoading(false);
      setError("Please log in to view your stories");
    }
  }, [user?.email]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'created':
        return 'text-blue-600';
      case 'failed':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'created':
        return 'Generating...';
      case 'failed':
        return 'Failed';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
      <Header />
      
      <main className="pt-20 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">History</h1>
            <p className="text-lg text-gray-600">Revisit your creative journey and continue your stories</p>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="text-center py-12">
              <Loader2 className="w-16 h-16 text-purple-600 mx-auto mb-4 animate-spin" />
              <p className="text-gray-600">Loading your stories...</p>
            </div>
          )}

          {/* Error State */}
          {error && !loading && (
            <div className="text-center py-12">
              <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md mx-auto">
                <p className="text-red-600 mb-4">{error}</p>
                <Button 
                  onClick={fetchUserStories}
                  variant="outline"
                  className="border-red-300 text-red-600 hover:bg-red-50"
                >
                  Try Again
                </Button>
              </div>
            </div>
          )}

          {/* Stories Container */}
          {!loading && !error && (
            <div className="relative">
              {stories.length > 0 && (
                <div className="flex items-center justify-between mb-6">
                  <Button variant="outline" size="icon" className="shrink-0">
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="icon" className="shrink-0">
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              )}

              {/* Story Cards Grid */}
              {stories.length > 0 && (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                  {stories.map((story) => (
                    <Link key={story.id} to={`/story/${story.id}`} className="group">
                      <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm hover:shadow-xl transition-all duration-300 transform hover:scale-105 cursor-pointer">
                        <CardContent className="p-0">
                          <div className="aspect-[3/4] bg-gradient-to-br from-purple-100 to-blue-100 rounded-t-lg flex items-center justify-center relative overflow-hidden">
                            {/* <BookOpen className="w-16 h-16 text-gray-400" /> */}
                            {/* <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" /> */}
                            {story.cover_image_url && (
                              <img
                                src={story.cover_image_url}
                                alt={story.title}
                                className="w-full h-full object-cover rounded-t-lg group-hover:scale-105 transition-transform duration-300"
                              />
                            )}
                            <div className="absolute top-2 right-2">
                              <span className={`text-xs px-2 py-1 rounded-full bg-white/80 ${getStatusColor(story.status)}`}>
                                {getStatusText(story.status)}
                              </span>
                            </div>
                          </div>
                          <div className="p-4">
                            <h3 className="font-semibold text-gray-900 group-hover:text-purple-600 transition-colors line-clamp-2">
                              {story.title}
                            </h3>
                            <p className="text-sm text-gray-500 mt-1">
                              Created {formatDate(story.created_at)}
                            </p>
                            {story.updated_at !== story.created_at && (
                              <p className="text-xs text-gray-400">
                                Updated {formatDate(story.updated_at)}
                              </p>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    </Link>
                  ))}
                </div>
              )}

              {/* Empty State - Only show when not loading and no stories */}
              {stories.length === 0 && !loading && !error && (
                <div className="text-center py-12">
                  <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-500 mb-2">No stories yet</h3>
                  <p className="text-gray-400 mb-6">Start creating your first story to see it here</p>
                  <Button asChild className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700">
                    <Link to="/new">Create New Story</Link>
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default History;

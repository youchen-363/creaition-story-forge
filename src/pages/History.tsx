
import { Link } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Header from "@/components/Header";
import { ChevronLeft, ChevronRight, BookOpen } from "lucide-react";

const History = () => {
  // Mock data - in a real app this would come from the backend
  const stories = [
    { id: 1, title: "The Enchanted Quest", image: "/api/placeholder/200/250", created: "2024-01-15" },
    { id: 2, title: "Space Adventures", image: "/api/placeholder/200/250", created: "2024-01-12" },
    { id: 3, title: "Mystery Manor", image: "/api/placeholder/200/250", created: "2024-01-10" },
    { id: 4, title: "Dragon's Tale", image: "/api/placeholder/200/250", created: "2024-01-08" },
    { id: 5, title: "Ocean Depths", image: "/api/placeholder/200/250", created: "2024-01-05" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
      <Header isAuthenticated={true} username="Creator" credits={145} />
      
      <main className="pt-20 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">History</h1>
            <p className="text-lg text-gray-600">Revisit your creative journey and continue your stories</p>
          </div>

          {/* Stories Container */}
          <div className="relative">
            <div className="flex items-center justify-between mb-6">
              <Button variant="outline" size="icon" className="shrink-0">
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="icon" className="shrink-0">
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>

            {/* Story Cards Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
              {stories.map((story) => (
                <Link key={story.id} to="/story" className="group">
                  <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm hover:shadow-xl transition-all duration-300 transform hover:scale-105 cursor-pointer">
                    <CardContent className="p-0">
                      <div className="aspect-[3/4] bg-gradient-to-br from-purple-100 to-blue-100 rounded-t-lg flex items-center justify-center relative overflow-hidden">
                        <BookOpen className="w-16 h-16 text-gray-400" />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
                      </div>
                      <div className="p-4">
                        <h3 className="font-semibold text-gray-900 group-hover:text-purple-600 transition-colors">
                          {story.title}
                        </h3>
                        <p className="text-sm text-gray-500 mt-1">
                          Created {new Date(story.created).toLocaleDateString()}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>

            {/* Empty State */}
            {stories.length === 0 && (
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
        </div>
      </main>
    </div>
  );
};

export default History;

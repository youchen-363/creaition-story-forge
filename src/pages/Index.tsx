
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import Header from "@/components/Header";
import { BookOpen, Paintbrush, Feather, Gamepad2, Sparkles, Star } from "lucide-react";

const Index = () => {
  // In a real app, this would come from authentication context
  const isAuthenticated = false;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
      <Header isAuthenticated={isAuthenticated} />
      
      {/* Main Content */}
      <main className="pt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] text-center relative">
            
            {/* Background Icons */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
              <Feather className="absolute top-20 left-10 w-8 h-8 text-purple-300 opacity-30 animate-pulse" />
              <BookOpen className="absolute top-32 right-16 w-6 h-6 text-blue-300 opacity-40" />
              <Paintbrush className="absolute bottom-40 left-20 w-7 h-7 text-indigo-300 opacity-35 rotate-12" />
              <Gamepad2 className="absolute bottom-32 right-12 w-6 h-6 text-purple-300 opacity-30" />
              <Sparkles className="absolute top-40 left-1/3 w-5 h-5 text-blue-400 opacity-40 animate-pulse" />
              <Star className="absolute bottom-48 right-1/3 w-6 h-6 text-indigo-400 opacity-35" />
            </div>

            {/* Hero Content */}
            <div className="max-w-4xl mx-auto z-10">
              <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
                Build your own{" "}
                <span className="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  stories
                </span>
              </h1>
              
              <p className="text-xl md:text-2xl text-gray-600 mb-12 max-w-2xl mx-auto leading-relaxed">
                Create visual narratives here by uploading images and letting AI bring your imagination to life
              </p>

              <Button 
                size="lg" 
                asChild
                className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-8 py-6 text-lg font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
              >
                <Link to={isAuthenticated ? "/new" : "/login"}>
                  Write New Story
                </Link>
              </Button>

              {/* Features Preview */}
              <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
                <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105">
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center mb-4 mx-auto">
                    <BookOpen className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">AI-Powered Writing</h3>
                  <p className="text-gray-600 text-sm">Generate compelling narratives with advanced AI assistance</p>
                </div>
                
                <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center mb-4 mx-auto">
                    <Paintbrush className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Visual Storytelling</h3>
                  <p className="text-gray-600 text-sm">Create stunning images that perfectly match your story</p>
                </div>
                
                <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105">
                  <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-xl flex items-center justify-center mb-4 mx-auto">
                    <Sparkles className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Easy to Use</h3>
                  <p className="text-gray-600 text-sm">Intuitive interface designed for creators of all levels</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;

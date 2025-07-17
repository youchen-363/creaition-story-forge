
import Header from "@/components/Header";
import { BookOpen, Users, Lightbulb } from "lucide-react";

const About = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
      <Header />
      
      <main className="pt-20 pb-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-6">About Us</h1>
            <h2 className="text-2xl font-semibold text-purple-600 mb-4">Unlock Your Imagination with CreAItion</h2>
          </div>

          <div className="space-y-12">
            {/* Mission Section */}
            <section className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg">
              <div className="flex items-center mb-6">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center mr-4">
                  <Lightbulb className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900">Our Mission: Empowering Every Storyteller</h3>
              </div>
              <p className="text-lg text-gray-700 leading-relaxed">
                At CreAItion, we believe that everyone has a story to tell. Our mission is to democratize creative storytelling by providing powerful, intuitive, and accessible AI tools that transform your ideas into captivating visual narratives. Whether you're a budding author, a passionate hobbyist, or simply someone with a vivid imagination, CreAItion is designed to be your ultimate co-creator, helping you visualize and share your unique tales with the world.
              </p>
            </section>

            {/* Who We Are Section */}
            <section className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg">
              <div className="flex items-center mb-6">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center mr-4">
                  <Users className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900">Who We Are: The Fusion of Creativity and AI</h3>
              </div>
              <p className="text-lg text-gray-700 leading-relaxed">
                We are a team of innovators, dreamers, and technologists passionate about pushing the boundaries of what's possible with artificial intelligence. We've harnessed the latest advancements in natural language processing and image generation to build a platform where your narrative concepts seamlessly evolve into rich, illustrated stories. Our focus is on user-friendly design, ensuring that the magic of AI is available to everyone, regardless of technical expertise.
              </p>
            </section>

            {/* Vision Section */}
            <section className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg">
              <div className="flex items-center mb-6">
                <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-xl flex items-center justify-center mr-4">
                  <BookOpen className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900">Our Vision: Stories Without Limits</h3>
              </div>
              <p className="text-lg text-gray-700 leading-relaxed">
                Imagine a world where the only limit to your story is your imagination. That's the future CreAItion is building. We envision a platform where collaboration between human creativity and artificial intelligence fosters an endless universe of diverse and engaging stories, brought to life with stunning visuals that truly capture the essence of your words. Join us on this exciting journey as we redefine storytelling for the digital age.
              </p>
            </section>
          </div>
        </div>
      </main>
    </div>
  );
};

export default About;

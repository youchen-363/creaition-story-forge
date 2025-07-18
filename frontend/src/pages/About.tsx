
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
                At CreAItion, we believe that everyone has a story to tell—whether it’s from childhood dreams, personal experiences, or pure imagination. Our mission is to democratize creative storytelling by providing intuitive, accessible AI tools that help transform your ideas into captivating visual narratives. By simply uploading a brief background story along with character images, names, and descriptions, anyone—regardless of artistic or technical skills—can co-create richly illustrated stories and bring their imagination to life. Even educators can use our platform to design engaging, story-based visuals for primary and secondary school textbooks, making learning more immersive and fun.
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
                We are a passionate team of dreamers, engineers, and creatives dedicated to redefining the storytelling process. At the heart of CreAItion is a seamless fusion of cutting-edge natural language processing and image generation technologies. Our platform allows users to submit their story concepts and character information, then uses AI to generate a coherent storyline and vivid scene-by-scene illustrations. Whether you're a hobbyist, an author, or a teacher designing curriculum content, our user-friendly platform empowers everyone to create impactful visual stories with ease.
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
                We envision a future where creativity knows no bounds—where storytellers around the world can effortlessly turn ideas into immersive visual experiences. CreAItion is building a universe where human imagination and artificial intelligence collaborate to unlock endless storytelling possibilities. From children’s books and webcomics to gamified learning modules and illustrated school materials, our platform enables stories that educate, entertain, and inspire. With CreAItion, the only limit is your imagination.              
              </p>
            </section>
          </div>
        </div>
      </main>
    </div>
  );
};

export default About;

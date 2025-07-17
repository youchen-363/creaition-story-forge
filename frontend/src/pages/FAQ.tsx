
import Header from "@/components/Header";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";
import { useState } from "react";

const FAQ = () => {
  const [searchTerm, setSearchTerm] = useState("");

  const faqs = [
    {
      category: "General",
      questions: [
        {
          q: "What is CreAItion?",
          a: "CreAItion is an innovative web application that leverages AI to help you create unique and visually engaging stories. You provide the core ideas, and our AI assists in generating narratives and accompanying images."
        },
        {
          q: "How does CreAItion work?",
          a: "You start by providing basic parameters for your story, such as title, number of scenes, characters, and a story mode. You can then define your characters and upload initial images. Our AI then generates the story text and corresponding visuals, which you can further refine."
        },
        {
          q: "Is CreAItion free to use?",
          a: "CreAItion offers different pricing plans, including a free tier with limited features and credits, as well as paid plans for more extensive story creation. Please refer to our Pricing scene for details."
        },
        {
          q: "Do I need to be a writer or artist to use CreAItion?",
          a: "Not at all! CreAItion is designed for everyone, regardless of their writing or artistic experience. Our AI tools simplify the creative process, allowing anyone to bring their stories to life."
        }
      ]
    },
    {
      category: "Account & Credits",
      questions: [
        {
          q: "How do I create an account?",
          a: "You can sign up on our Login scene using your email or by connecting with your GitHub account."
        },
        {
          q: "What are 'Credits' and how do I use them?",
          a: "Credits are used to power the AI generation processes within CreAItion, such as generating story scenes, rewriting text, or redrawing images. Each generation consumes a certain number of credits, which will be indicated next to the action."
        },
        {
          q: "How can I get more credits?",
          a: "You can purchase additional credits directly from your account by navigating to the 'Add Credit' section in your user dropdown menu. Our Pricing scene provides information on available credit packages."
        },
        {
          q: "How can I update my profile information?",
          a: "You can edit your username, email, password, and profile picture by visiting the 'Edit Profile' link in your user dropdown menu."
        }
      ]
    },
    {
      category: "Story Creation",
      questions: [
        {
          q: "Can I upload my own images for the story and characters?",
          a: "Yes! You can upload a cover image for your story and individual images for each character. This helps the AI better understand your vision and provides visual context."
        },
        {
          q: "What 'Story Modes' are available?",
          a: "We offer various story modes such as Horror, Fantasy, Sci-Fi, Comedy, and Adventure. Selecting a mode helps the AI tailor the narrative style and content."
        },
        {
          q: "Can I edit the AI-generated story text?",
          a: "While the main story text box is not directly editable, you can use the 'Rewrite' button to regenerate the text for a specific scene if you're not satisfied with the initial output."
        },
        {
          q: "What happens if I click 'Redraw' on a story scene?",
          a: "The 'Redraw' button generates a new image for the current story scene, consuming credits. This is useful if the initial image doesn't quite match your expectations."
        },
        {
          q: "Can I save my story at any point?",
          a: "Stories are automatically saved as you create them. You can access your saved stories from the History scene at any time."
        }
      ]
    },
    {
      category: "Troubleshooting & Support",
      questions: [
        {
          q: "I'm experiencing an issue. How can I get help?",
          a: "Please visit our Contact Us scene to send us a message directly, or reach out via email or phone."
        },
        {
          q: "My generated content doesn't make sense. What should I do?",
          a: "AI models can sometimes produce unexpected results. Try using the 'Rewrite' or 'Redraw' buttons. Providing more detailed and specific inputs in the 'New Story' scene and character descriptions can also improve results."
        },
        {
          q: "My image upload failed. What are the requirements?",
          a: "Please ensure your image is in a common format (e.g., JPG, PNG) and within reasonable file size limits (e.g., under 5MB). If the issue persists, try a different image or contact support."
        }
      ]
    }
  ];

  const filteredFaqs = faqs.map(category => ({
    ...category,
    questions: category.questions.filter(
      faq => 
        faq.q.toLowerCase().includes(searchTerm.toLowerCase()) ||
        faq.a.toLowerCase().includes(searchTerm.toLowerCase())
    )
  })).filter(category => category.questions.length > 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
      <Header />
      
      <main className="pt-20 pb-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">Frequently Asked Questions</h1>
            <p className="text-lg text-gray-600 mb-8">
              Find answers to common questions about CreAItion
            </p>

            {/* Search Bar */}
            <div className="relative max-w-md mx-auto">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                placeholder="Search FAQs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-white"
              />
            </div>
          </div>

          <div className="space-y-8">
            {filteredFaqs.map((category, categoryIndex) => (
              <div key={categoryIndex} className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">{category.category}</h2>
                <Accordion type="single" collapsible className="space-y-2">
                  {category.questions.map((faq, index) => (
                    <AccordionItem 
                      key={index} 
                      value={`${categoryIndex}-${index}`}
                      className="border border-gray-200 rounded-lg"
                    >
                      <AccordionTrigger className="px-4 py-3 text-left font-medium hover:bg-gray-50">
                        {faq.q}
                      </AccordionTrigger>
                      <AccordionContent className="px-4 pb-4 text-gray-700">
                        {faq.a}
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              </div>
            ))}
          </div>

          {filteredFaqs.length === 0 && searchTerm && (
            <div className="text-center py-12">
              <p className="text-gray-600">No FAQs found matching "{searchTerm}"</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default FAQ;


import Header from "@/components/Header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Check, Star, Zap, Crown } from "lucide-react";

const Pricing = () => {
  const plans = [
    {
      name: "Free",
      price: "$0",
      period: "month",
      icon: Zap,
      description: "Experimenting & casual use",
      credits: "50 Credits",
      features: [
        "50 Monthly Credits",
        "10 Credits/day limit",
        "Standard AI Model",
        "Standard Quality AI Images",
        "Limited Rewrite & Redraw",
        "1 Private Story",
        "Recent 3 Stories History",
        "Community Forum Support",
        "CreAItion Watermark"
      ],
      buttonText: "Get Started (Free)",
      buttonVariant: "outline" as const,
      popular: false
    },
    {
      name: "Creator",
      price: "$9",
      period: "month",
      icon: Star,
      description: "Passionate hobbyists & regular creators",
      credits: "500 Credits",
      features: [
        "500 Monthly Credits",
        "Unlimited Daily Usage",
        "Enhanced AI Model",
        "High Quality AI Images",
        "Full Rewrite & Redraw Access",
        "Unlimited Private Stories",
        "Full History Access",
        "Email Support",
        "Optional CreAItion Watermark"
      ],
      buttonText: "Choose Plan",
      buttonVariant: "default" as const,
      popular: true
    },
    {
      name: "Pro",
      price: "$29",
      period: "month",
      icon: Crown,
      description: "Professional storytellers & high-volume users",
      credits: "2000 Credits",
      features: [
        "2000 Monthly Credits",
        "Unlimited Daily Usage",
        "Premium AI Model",
        "Superior Quality AI Images",
        "Full Rewrite & Redraw Access",
        "Unlimited Private Stories",
        "Full History Access",
        "Priority Email & Chat Support",
        "No Watermark"
      ],
      buttonText: "Choose Plan",
      buttonVariant: "default" as const,
      popular: false
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
      <Header />
      
      <main className="pt-20 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-6">Pricing</h1>
            <h2 className="text-2xl font-semibold text-purple-600 mb-4">Choose Your Creative Journey</h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Unlock the full potential of your storytelling with CreAItion's flexible pricing plans. Whether you're just starting out or ready to dive deep into extensive narrative creation, we have a plan perfectly tailored for your needs.
            </p>
          </div>

          {/* Pricing Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            {plans.map((plan) => {
              const IconComponent = plan.icon;
              return (
                <Card 
                  key={plan.name} 
                  className={`relative shadow-xl border-0 bg-white/80 backdrop-blur-sm ${
                    plan.popular ? 'ring-2 ring-purple-500 transform scale-105' : ''
                  }`}
                >
                  {plan.popular && (
                    <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                      <span className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                        Most Popular
                      </span>
                    </div>
                  )}
                  
                  <CardHeader className="text-center pb-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                      <IconComponent className="w-6 h-6 text-white" />
                    </div>
                    <CardTitle className="text-2xl font-bold">{plan.name}</CardTitle>
                    <div className="mt-2">
                      <span className="text-4xl font-bold text-gray-900">{plan.price}</span>
                      <span className="text-gray-500">/{plan.period}</span>
                    </div>
                    <p className="text-sm text-gray-600 mt-2">{plan.description}</p>
                    <div className="mt-4 p-3 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg">
                      <div className="text-lg font-semibold text-purple-600">{plan.credits}</div>
                      <div className="text-sm text-gray-600">Monthly Credits</div>
                    </div>
                  </CardHeader>
                  
                  <CardContent className="pt-0">
                    <ul className="space-y-3 mb-6">
                      {plan.features.map((feature, index) => (
                        <li key={index} className="flex items-start">
                          <Check className="w-5 h-5 text-green-500 mr-3 mt-0.5 shrink-0" />
                          <span className="text-sm text-gray-700">{feature}</span>
                        </li>
                      ))}
                    </ul>
                    
                    <Button 
                      className={`w-full ${
                        plan.buttonVariant === 'default' 
                          ? 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700' 
                          : ''
                      }`}
                      variant={plan.buttonVariant}
                    >
                      {plan.buttonText}
                    </Button>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Additional Information */}
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Understanding Your Credits</h3>
            <p className="text-gray-700 mb-6">
              Credits are consumed when you generate story scenes, rewrite text, or redraw images. The cost per action may vary slightly depending on the complexity and the AI model used (higher tiers use more advanced models for better results).
            </p>

            <h3 className="text-xl font-bold text-gray-900 mb-4">A Note on AI Image Quality</h3>
            <p className="text-gray-700 mb-4">
              At CreAItion, we understand that visual impact is key to storytelling. Our paid tiers, <strong>Creator</strong> and <strong>Pro</strong>, utilize increasingly sophisticated AI image generation models:
            </p>
            <ul className="space-y-2 text-gray-700">
              <li><strong>Free Plan:</strong> Functional and imaginative visuals using our standard AI model.</li>
              <li><strong>Creator Plan:</strong> High Quality AI Images with better coherence, detail, and artistic flair.</li>
              <li><strong>Pro Plan:</strong> Superior Quality AI Images with unparalleled detail and photorealistic quality.</li>
            </ul>

            <div className="mt-8 text-center">
              <h4 className="text-lg font-semibold text-gray-900 mb-2">Ready to start your next chapter?</h4>
              <p className="text-gray-600">Choose the plan that fits your creative ambitions and begin crafting your incredible stories today!</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Pricing;

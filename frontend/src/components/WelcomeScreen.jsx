import React from 'react';
import { MessageSquare, Zap, Shield, TrendingUp } from 'lucide-react';

const WelcomeScreen = ({ onExampleClick }) => {
  const examples = [
    "What is Kubernetes?",
    "How does CI/CD work?",
    "Explain Docker containers",
    "Terraform vs Ansible?",
    "How to set up monitoring?",
    "Git branching strategies"
  ];

  const features = [
    { icon: Zap, title: "Fast Responses", desc: "<100ms inference time" },
    { icon: Shield, title: "96% Accuracy", desc: "Production-ready model" },
    { icon: TrendingUp, title: "Always Learning", desc: "Continuous improvement" },
  ];

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Welcome Section */}
        <div className="text-center space-y-4">
          <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full mx-auto flex items-center justify-center">
            <MessageSquare size={40} className="text-white" />
          </div>
          <h2 className="text-3xl font-bold text-gray-800">
            Welcome to DevOps Chatbot
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Get instant answers to your DevOps questions. Powered by DistilBERT fine-tuned on 2000+ DevOps FAQs.
          </p>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {features.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="p-4 bg-white rounded-xl border border-gray-200 hover:border-primary transition-colors">
              <Icon className="text-primary mb-2" size={24} />
              <h3 className="font-semibold text-gray-800">{title}</h3>
              <p className="text-sm text-gray-600">{desc}</p>
            </div>
          ))}
        </div>

        {/* Example Questions */}
        <div className="space-y-4">
          <h3 className="text-xl font-semibold text-gray-800 text-center">
            Try asking:
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {examples.map((example) => (
              <button
                key={example}
                onClick={() => onExampleClick(example)}
                className="p-4 text-left bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-xl transition-colors group"
              >
                <p className="text-gray-700 group-hover:text-primary transition-colors">
                  {example}
                </p>
              </button>
            ))}
          </div>
        </div>

        {/* Tech Stack */}
        <div className="text-center pt-8 border-t">
          <p className="text-sm text-gray-500">
            Built with React • FastAPI • DistilBERT • PyTorch
          </p>
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen;

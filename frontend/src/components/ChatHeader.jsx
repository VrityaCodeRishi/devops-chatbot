import React from 'react';
import { Bot, Github, Code2 } from 'lucide-react';

const ChatHeader = () => {
  return (
    <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 shadow-lg">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
              <Bot size={28} />
            </div>
            <div>
              <h1 className="text-2xl font-bold">DevOps Chatbot</h1>
              <p className="text-blue-100 text-sm">AI-powered DevOps assistant • 96% accuracy</p>
            </div>
          </div>
          
          <div className="flex gap-3">
            <a 
              href="https://github.com/VrityaCodeRishi/devops-chatbot" 
              target="_blank" 
              rel="noopener noreferrer"
              className="p-2 hover:bg-white/20 rounded-full transition-colors"
            >
              <Github size={24} />
            </a>
            <a 
              href="/api/docs" 
              target="_blank" 
              rel="noopener noreferrer"
              className="p-2 hover:bg-white/20 rounded-full transition-colors"
            >
              <Code2 size={24} />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatHeader;

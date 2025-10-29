import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ChatHeader from './components/ChatHeader';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import WelcomeScreen from './components/WelcomeScreen';
import { AlertCircle } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || '';

function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (question) => {
    // Add user message
    const userMessage = { text: question, isUser: true };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/predict`, {
        question: question,
        return_confidence: true
      });

      // Add bot response
      const botMessage = {
        text: response.data.answer,
        isUser: false,
        confidence: response.data.confidence,
        intent: response.data.intent
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setError('Failed to get response. Make sure the backend is running.');
      console.error('Error:', err);
      
      // Add error message
      const errorMessage = {
        text: "Sorry, I couldn't process your request. Please try again later.",
        isUser: false,
        confidence: 0
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExampleClick = (example) => {
    sendMessage(example);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <ChatHeader />

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border-b border-red-200 p-3">
          <div className="max-w-4xl mx-auto flex items-center gap-2 text-red-800">
            <AlertCircle size={20} />
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <WelcomeScreen onExampleClick={handleExampleClick} />
        ) : (
          <div className="max-w-4xl mx-auto p-6">
            {messages.map((msg, idx) => (
              <ChatMessage
                key={idx}
                message={msg.text}
                isUser={msg.isUser}
                confidence={msg.confidence}
              />
            ))}
            {isLoading && (
              <div className="flex gap-3 mb-4">
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <div className="w-2 h-2 bg-white rounded-full animate-bounce" />
                </div>
                <div className="px-4 py-3 bg-gray-100 rounded-2xl rounded-tl-none">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <ChatInput onSend={sendMessage} isLoading={isLoading} />
    </div>
  );
}

export default App;

import React from 'react';
import { motion } from 'framer-motion';
import { User, Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const ChatMessage = ({ message, isUser, confidence }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-3 mb-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
        isUser 
          ? 'bg-primary text-white' 
          : 'bg-gradient-to-br from-blue-500 to-purple-600 text-white'
      }`}>
        {isUser ? <User size={20} /> : <Bot size={20} />}
      </div>

      {/* Message Content */}
      <div className={`flex flex-col max-w-[70%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={`px-4 py-3 rounded-2xl ${
          isUser 
            ? 'bg-primary text-white rounded-tr-none' 
            : 'bg-gray-100 text-gray-800 rounded-tl-none'
        }`}>
          <div className="text-sm leading-relaxed">
            {isUser ? (
              <p>{message}</p>
            ) : (
              <ReactMarkdown>{message}</ReactMarkdown>
            )}
          </div>
        </div>

        {/* Confidence Badge for Bot Messages */}
        {!isUser && confidence && (
          <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
            <div className="flex items-center gap-1">
              <div className={`w-2 h-2 rounded-full ${
                confidence > 0.8 ? 'bg-green-500' : 
                confidence > 0.6 ? 'bg-yellow-500' : 'bg-red-500'
              }`} />
              <span>Confidence: {(confidence * 100).toFixed(1)}%</span>
            </div>
            {confidence > 0.8 && <span>• High confidence</span>}
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default ChatMessage;

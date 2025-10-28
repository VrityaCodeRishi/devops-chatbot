import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import json
from pathlib import Path

class DevOpsChatbot:
    def __init__(self, model_path='models/distilbert-devops-faq'):
        print(f"Loading model from {model_path}...")
        
        self.model = DistilBertForSequenceClassification.from_pretrained(model_path)
        self.tokenizer = DistilBertTokenizer.from_pretrained(model_path)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.model.eval()
        
        data_dir = 'data/processed'
        with open(f'{data_dir}/id_to_label.json', 'r') as f:
            self.id_to_label = {int(k): v for k, v in json.load(f).items()}
        
        with open(f'{data_dir}/answer_map.json', 'r') as f:
            self.answer_map = json.load(f)
        
        print(f"Model loaded on {self.device}")
    
    def predict(self, question, return_confidence=True):

        inputs = self.tokenizer(
            question,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=128
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
            predicted_class = torch.argmax(probabilities, dim=-1).item()
            confidence = probabilities[0][predicted_class].item()
        
        intent = self.id_to_label[predicted_class]
        answer = self.answer_map.get(intent, "I'm not sure how to answer that.")
        
        result = {
            'question': question,
            'intent': intent,
            'answer': answer,
            'confidence': confidence
        }
        
        if return_confidence:
            return result
        else:
            return answer
    
    def chat(self):
        print("\n" + "=" * 60)
        print("DevOps Chatbot is ready!")
        print("=" * 60)
        print("Ask me anything about DevOps (or 'quit' to exit)\n")
        
        while True:
            question = input("You: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not question:
                continue
            
            result = self.predict(question)
            print(f"\nBot: {result['answer']}")
            print(f"Intent: {result['intent']} (Confidence: {result['confidence']:.2%})\n")

if __name__ == "__main__":
    chatbot = DevOpsChatbot()
    chatbot.chat()

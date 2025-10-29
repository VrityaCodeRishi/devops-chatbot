import torch
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback
)
from torch.utils.data import Dataset
import pandas as pd
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, classification_report

class DevOpsDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            padding='max_length',
            truncation=True,
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class DevOpsChatbotTrainer:
    def __init__(self, model_name='distilbert-base-uncased', data_dir='data/processed'):
        self.model_name = model_name
        self.data_dir = data_dir
        self.tokenizer = DistilBertTokenizer.from_pretrained(model_name)
        
        with open(f'{data_dir}/label_map.json', 'r') as f:
            self.label_map = json.load(f)
        
        with open(f'{data_dir}/id_to_label.json', 'r') as f:
            self.id_to_label = {int(k): v for k, v in json.load(f).items()}
        
        self.num_labels = len(self.label_map)
        
        print(f"Initializing model: {model_name}")
        print(f"Number of intents: {self.num_labels}")
        print(f"Intents: {list(self.label_map.keys())}")
        
        self.model = DistilBertForSequenceClassification.from_pretrained(
            model_name,
            num_labels=self.num_labels
        )
    
    def load_data(self):
        print("\nLoading datasets...")
    
        train_df = pd.read_json(f'{self.data_dir}/train.json', lines=True)
        val_df = pd.read_json(f'{self.data_dir}/val.json', lines=True)
        test_df = pd.read_json(f'{self.data_dir}/test.json', lines=True)
        
        print(f"Train samples: {len(train_df)}")
        print(f"Validation samples: {len(val_df)}")
        print(f"Test samples: {len(test_df)}")
        
        print("\nCreating torch datasets...")
        train_dataset = DevOpsDataset(
            train_df['text'].tolist(),
            train_df['label_id'].tolist(),
            self.tokenizer
        )
        
        val_dataset = DevOpsDataset(
            val_df['text'].tolist(),
            val_df['label_id'].tolist(),
            self.tokenizer
        )
        
        test_dataset = DevOpsDataset(
            test_df['text'].tolist(),
            test_df['label_id'].tolist(),
            self.tokenizer
        )
        
        return {
            'train': train_dataset,
            'validation': val_dataset,
            'test': test_dataset
        }
    
    def compute_metrics(self, eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        
        accuracy = accuracy_score(labels, predictions)
        f1 = f1_score(labels, predictions, average='weighted')
        
        return {
            'accuracy': accuracy,
            'f1': f1
        }
    
    def train(self, 
              output_dir='models/distilbert-devops-faq', 
              epochs=10,
              batch_size=8,
              learning_rate=2e-5):
        

        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"\n Device: {device}")
        if device == "cuda":
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
        
        datasets = self.load_data()
        
        training_args = TrainingArguments(
            output_dir=output_dir,
            eval_strategy='epoch',
            save_strategy='epoch',
            learning_rate=learning_rate,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            num_train_epochs=epochs,
            weight_decay=0.01,
            load_best_model_at_end=True,
            metric_for_best_model='f1',
            greater_is_better=True,
            push_to_hub=False,
            logging_dir=f'{output_dir}/logs',
            logging_steps=5,
            fp16=torch.cuda.is_available(),
            report_to='none',
            save_total_limit=2,
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=datasets['train'],
            eval_dataset=datasets['validation'],
            compute_metrics=self.compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
        )
        
        print("\nStarting training...")
        print("=" * 60)
        train_result = trainer.train()
        
        print("\n" + "=" * 60)
        print("Evaluating on test set...")
        test_results = trainer.evaluate(datasets['test'])
        
        predictions = trainer.predict(datasets['test'])
        pred_labels = np.argmax(predictions.predictions, axis=-1)
        true_labels = predictions.label_ids

        pred_intents = [self.id_to_label[i] for i in pred_labels]
        true_intents = [self.id_to_label[i] for i in true_labels]
        
        print("\nDetailed Classification Report:")
        print("=" * 60)
        print(classification_report(true_intents, pred_intents))
        

        print(f"\nSaving model to {output_dir}...")
        trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        config = {
            'model_name': self.model_name,
            'num_labels': self.num_labels,
            'test_accuracy': float(test_results['eval_accuracy']),
            'test_f1': float(test_results['eval_f1']),
            'epochs': epochs,
            'batch_size': batch_size,
            'learning_rate': learning_rate
        }
        
        with open(f'{output_dir}/training_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("\n" + "=" * 60)
        print("Training complete!")
        print(f"Test Accuracy: {test_results['eval_accuracy']:.4f}")
        print(f"Test F1 Score: {test_results['eval_f1']:.4f}")
        print("=" * 60)
        
        return trainer, test_results

if __name__ == "__main__":
    trainer = DevOpsChatbotTrainer()
    trainer.train(epochs=5, batch_size=8)

import yaml
import json
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from collections import Counter

def load_faqs(yaml_path='data/raw/devops_faqs.yaml'):
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    return data['faqs']

def prepare_training_data(faqs):
    training_data = []
    
    for faq in faqs:
        intent = faq['intent']
        for question in faq['questions']:
            training_data.append({
                'text': question,
                'label': intent,
                'answer': faq['answer']
            })
    
    return training_data

def create_dataset(output_dir='data/processed', test_size=0.3, val_size=0.5, random_state=42):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print("Loading FAQ data...")
    faqs = load_faqs()
    data = prepare_training_data(faqs)
    
    df = pd.DataFrame(data)
    
    print(f"\nTotal samples: {len(df)}")
    print(f"Unique intents: {df['label'].nunique()}")
    print(f"\nIntent distribution:")
    print(df['label'].value_counts())
    

    unique_labels = sorted(df['label'].unique())
    label_map = {label: idx for idx, label in enumerate(unique_labels)}
    id_to_label = {idx: label for label, idx in label_map.items()}
    
    df['label_id'] = df['label'].map(label_map)
    
    train_df, temp_df = train_test_split(
        df, 
        test_size=test_size, 
        stratify=df['label_id'], 
        random_state=random_state
    )
    
    val_df, test_df = train_test_split(
        temp_df, 
        test_size=val_size, 
        stratify=temp_df['label_id'], 
        random_state=random_state
    )
    
    train_df.to_json(f'{output_dir}/train.json', orient='records', lines=True)
    val_df.to_json(f'{output_dir}/val.json', orient='records', lines=True)
    test_df.to_json(f'{output_dir}/test.json', orient='records', lines=True)
    
    with open(f'{output_dir}/label_map.json', 'w') as f:
        json.dump(label_map, f, indent=2)
    
    with open(f'{output_dir}/id_to_label.json', 'w') as f:
        json.dump(id_to_label, f, indent=2)
    
    answer_map = {intent: faqs_item['answer'] 
                  for faqs_item in faqs 
                  for intent in [faqs_item['intent']]}
    
    with open(f'{output_dir}/answer_map.json', 'w') as f:
        json.dump(answer_map, f, indent=2)
    
    print(f"\nDataset created successfully!")
    print(f"Train: {len(train_df)} samples")
    print(f"Validation: {len(val_df)} samples")
    print(f"Test: {len(test_df)} samples")
    print(f"\nFiles saved to: {output_dir}/")
    
    return train_df, val_df, test_df, label_map

if __name__ == "__main__":
    create_dataset()

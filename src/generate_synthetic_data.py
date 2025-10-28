import os
import json
import yaml
from pathlib import Path

GENERATION_PROMPT = """Generate 20 diverse questions that a DevOps engineer might ask about {intent_topic}.

Intent: {intent_name}
Topic: {intent_topic}
Example questions:
{example_questions}

Requirements:
- Questions should be natural and varied
- Include different phrasings (what, how, why, explain, tell me, etc.)
- Mix beginner and advanced questions
- Include comparisons and troubleshooting questions
- Make them realistic for a DevOps context

Generate 20 NEW questions (different from examples):"""

def generate_with_openai(intent_name, intent_topic, example_questions, num_questions=20):
    try:
        import openai
        
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        prompt = GENERATION_PROMPT.format(
            intent_name=intent_name,
            intent_topic=intent_topic,
            example_questions="\n".join(f"- {q}" for q in example_questions[:5])
        )
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a DevOps training data generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=500
        )
        
        generated_text = response.choices[0].message.content
        questions = [q.strip('- ').strip() for q in generated_text.split('\n') if q.strip()]
        return questions
        
        return []
        
    except ImportError:
        print("Install OpenAI: pip install openai")
        return []

def generate_with_paraphrasing(base_questions):
    from collections import defaultdict
    
    augmented = []
    
    # Paraphrasing templates
    templates = {
        'what_is': [
            "What is {}?",
            "Can you explain {}?",
            "Tell me about {}",
            "What do you mean by {}?",
            "Define {}",
            "Explain {} to me",
            "I want to understand {}",
            "Help me learn about {}",
        ],
        'how_to': [
            "How to {}?",
            "How do I {}?",
            "What's the way to {}?",
            "Can you show me how to {}?",
            "Steps to {}",
            "Guide me through {}",
            "Tutorial for {}",
        ],
        'why': [
            "Why {}?",
            "Why should I {}?",
            "What's the reason for {}?",
            "Benefits of {}",
            "Why is {} important?",
        ],
        'compare': [
            "{} vs {}",
            "Difference between {} and {}",
            "Compare {} with {}",
            "{} or {}?",
            "Which is better: {} or {}?",
        ]
    }
    
    return augmented

def generate_large_dataset(target_samples=10000):
    print(f"Target: {target_samples} training samples")
    

    with open('data/raw/devops_faqs.yaml', 'r') as f:
        faqs = yaml.safe_load(f)['faqs']
    
    num_intents = len(faqs)
    samples_per_intent = target_samples // num_intents
    
    print(f"\nDataset composition:")
    print(f"   Intents: {num_intents}")
    print(f"   Target samples per intent: {samples_per_intent}")
    print(f"   Total: {samples_per_intent * num_intents} samples")
    
    augmentation_templates = [
        "What is {topic}?",
        "Explain {topic}",
        "Tell me about {topic}",
        "How does {topic} work?",
        "{topic} explained",
        "Understanding {topic}",
        "{topic} basics",
        "{topic} fundamentals",
        "{topic} overview",
        "Introduction to {topic}",
        
        "How to use {topic}?",
        "{topic} tutorial",
        "Getting started with {topic}",
        "{topic} guide",
        "Learn {topic}",
        "{topic} for beginners",
        "{topic} best practices",
        
        "Why use {topic}?",
        "Benefits of {topic}",
        "Advantages of {topic}",
        "Use cases for {topic}",
        "When to use {topic}?",
        "Should I use {topic}?",
        
        "{topic} vs alternatives",
        "Compare {topic}",
        "{topic} alternatives",
        "Is {topic} better?",
        
        "How to debug {topic}?",
        "{topic} troubleshooting",
        "Common {topic} issues",
        "{topic} problems",
        "Fix {topic} errors",
        
        "{topic} architecture",
        "{topic} internals",
        "Advanced {topic}",
        "{topic} deep dive",
        "{topic} configuration",
        "{topic} optimization",
    ]
    
    intent_keywords = {
        'kubernetes_basics': ['Kubernetes', 'K8s', 'container orchestration', 'pods', 'clusters'],
        'docker_basics': ['Docker', 'containers', 'containerization', 'images', 'Docker Compose'],
        'cicd_pipeline': ['CI/CD', 'continuous integration', 'continuous deployment', 'pipelines', 'automation'],
        'terraform_basics': ['Terraform', 'IaC', 'Infrastructure as Code', 'HCL', 'provisioning'],
        'monitoring_logging': ['monitoring', 'observability', 'logs', 'metrics', 'alerts'],
        'container_orchestration': ['orchestration', 'container management', 'scheduling', 'scaling'],
        'git_version_control': ['Git', 'version control', 'GitHub', 'GitLab', 'repositories'],
        'linux_commands': ['Linux', 'Unix', 'shell', 'bash', 'command line'],
        'cloud_platforms': ['cloud', 'AWS', 'Azure', 'GCP', 'cloud computing'],
        'ansible_configuration': ['Ansible', 'configuration management', 'playbooks', 'automation'],
    }
    
    expanded_faqs = []
    
    for faq in faqs:
        intent = faq['intent']
        answer = faq['answer']
        keywords = intent_keywords.get(intent, [intent.replace('_', ' ')])
        
        generated_questions = set(faq['questions'])
        
        for template in augmentation_templates:
            for keyword in keywords:
                question = template.format(topic=keyword)
                generated_questions.add(question)
                
                if len(generated_questions) >= samples_per_intent:
                    break
            if len(generated_questions) >= samples_per_intent:
                break
        
        expanded_faqs.append({
            'intent': intent,
            'questions': list(generated_questions)[:samples_per_intent],
            'answer': answer
        })
    
    # Save expanded dataset
    output_data = {'faqs': expanded_faqs}
    
    with open('data/raw/devops_faqs.yaml', 'w') as f:
        yaml.dump(output_data, f, default_flow_style=False, allow_unicode=True)
    
    total_questions = sum(len(faq['questions']) for faq in expanded_faqs)
    print(f"\nGenerated {total_questions} questions!")
    print(f"   Saved to: data/raw/devops_faqs.yaml")

if __name__ == "__main__":
    # Generate 1000 samples per intent = 10,000 total
    generate_large_dataset(target_samples=10000)

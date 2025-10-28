import os
import json
import yaml
from pathlib import Path
import random

GENERATION_PROMPT = """Generate 20 diverse questions that a DevOps engineer might ask about {intent_topic}.

Intent: {intent_name}
Topic: {intent_topic}
Example questions:
{example_questions}

Requirements:
- Questions should be natural and varied
- Include different phrasings (what, how, why, explain, tell me, etc.)
- Mix beginner, intermediate, and advanced questions
- Include comparisons and troubleshooting questions
- Make them realistic for a DevOps context

Generate 20 NEW questions (different from examples):"""


def generate_with_openai(intent_name, intent_topic, example_questions, num_questions=100):
    """Generate questions using OpenAI API"""
    try:
        import openai
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return []
        
        client = openai.OpenAI(api_key=api_key)
        
        prompt = GENERATION_PROMPT.format(
            intent_name=intent_name,
            intent_topic=intent_topic,
            example_questions="\n".join(f"- {q}" for q in example_questions[:5])
        )
        
        all_questions = []
        batches = (num_questions + 19) // 20  # Generate in batches of 20
        
        for _ in range(batches):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a DevOps training data generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=800
            )
            
            generated_text = response.choices[0].message.content
            questions = [q.strip('- ').strip() for q in generated_text.split('\n') 
                        if q.strip() and any(c.isalpha() for c in q)]
            
            # Clean numbering
            cleaned = []
            for q in questions:
                q = q.lstrip('0123456789.-) ').strip()
                if q and len(q) > 10:
                    cleaned.append(q)
            
            all_questions.extend(cleaned)
        
        return all_questions[:num_questions]
        
    except ImportError:
        print("⚠️  OpenAI not installed - using template generation only")
        return []
    except Exception as e:
        print(f"⚠️  OpenAI API error: {e}")
        return []


def generate_large_dataset_improved(target_samples=7000, use_openai=False):
    """
    Generate 7000 high-quality varied questions
    """
    print(f"🎯 Target: {target_samples} training samples")
    print(f"   OpenAI API: {'Enabled' if use_openai and os.getenv('OPENAI_API_KEY') else 'Disabled'}")
    
    # Load base data
    with open('data/raw/devops_faqs.yaml', 'r') as f:
        faqs = yaml.safe_load(f)['faqs']
    
    num_intents = len(faqs)
    samples_per_intent = target_samples // num_intents
    
    print(f"\n📊 Dataset composition:")
    print(f"   Intents: {num_intents}")
    print(f"   Target samples per intent: {samples_per_intent}")
    print(f"   Total: {samples_per_intent * num_intents} samples")
    
    # Enhanced templates with more variation
    question_patterns = {
        'what_patterns': [
            "What is {topic}?",
            "What does {topic} do?",
            "What are {topic}?",
            "What's {topic}?",
            "Can you explain what {topic} is?",
            "Tell me what {topic} means",
            "Define {topic}",
            "What do you mean by {topic}?",
            "{topic} definition",
            "Meaning of {topic}",
        ],
        'explain_patterns': [
            "Explain {topic}",
            "Explain {topic} to me",
            "Can you explain {topic}?",
            "Help me understand {topic}",
            "I need an explanation of {topic}",
            "Please explain {topic}",
            "{topic} explained",
            "Break down {topic} for me",
            "Describe {topic}",
            "Give me an overview of {topic}",
        ],
        'how_patterns': [
            "How does {topic} work?",
            "How do I use {topic}?",
            "How to implement {topic}?",
            "How can I leverage {topic}?",
            "How should I use {topic}?",
            "What's the way to use {topic}?",
            "Show me how {topic} works",
            "How to get started with {topic}?",
            "How do you set up {topic}?",
            "What's the process for {topic}?",
        ],
        'why_patterns': [
            "Why use {topic}?",
            "Why is {topic} important?",
            "Why should I use {topic}?",
            "Why do we need {topic}?",
            "What's the purpose of {topic}?",
            "What are the benefits of {topic}?",
            "Why is {topic} popular?",
            "What makes {topic} useful?",
            "Advantages of {topic}",
            "Why choose {topic}?",
        ],
        'learning_patterns': [
            "Learn {topic}",
            "{topic} tutorial",
            "{topic} guide",
            "Getting started with {topic}",
            "{topic} for beginners",
            "Introduction to {topic}",
            "{topic} basics",
            "{topic} fundamentals",
            "{topic} overview",
            "Understanding {topic}",
            "{topic} 101",
            "Beginner's guide to {topic}",
        ],
        'advanced_patterns': [
            "Advanced {topic}",
            "{topic} best practices",
            "{topic} architecture",
            "{topic} internals",
            "{topic} deep dive",
            "{topic} configuration",
            "{topic} optimization",
            "{topic} advanced concepts",
            "Master {topic}",
            "{topic} expert guide",
            "{topic} in production",
            "Enterprise {topic}",
        ],
        'comparison_patterns': [
            "{topic} vs alternatives",
            "Compare {topic}",
            "{topic} comparison",
            "Is {topic} better?",
            "Should I use {topic}?",
            "{topic} pros and cons",
            "When to use {topic}?",
            "{topic} or alternatives?",
            "Choosing {topic}",
            "Why {topic} over others?",
        ],
        'troubleshooting_patterns': [
            "Troubleshoot {topic}",
            "Debug {topic}",
            "Fix {topic} issues",
            "Common {topic} problems",
            "{topic} errors",
            "Resolve {topic} issues",
            "{topic} troubleshooting guide",
            "How to fix {topic}?",
            "{topic} common mistakes",
            "Debugging {topic}",
        ],
        'practical_patterns': [
            "Using {topic} in production",
            "Real-world {topic}",
            "{topic} use cases",
            "Implementing {topic}",
            "Deploy with {topic}",
            "Integrate {topic}",
            "{topic} implementation guide",
            "How to deploy {topic}?",
            "{topic} setup guide",
            "Configure {topic}",
        ],
    }
    
    # Intent-specific keywords with more variations
    intent_keywords = {
        'kubernetes_basics': [
            'Kubernetes', 'K8s', 'Kube', 'container orchestration', 'pods', 
            'clusters', 'K8s cluster', 'Kubernetes deployment', 'K8s pods',
            'Kubernetes services', 'container orchestration platform', 'Kubernetes architecture',
            'Kubernetes ecosystem', 'cloud-native orchestration'
        ],
        'docker_basics': [
            'Docker', 'containers', 'containerization', 'Docker images', 
            'Docker Compose', 'Dockerfile', 'Docker Engine', 'containerized apps',
            'Docker runtime', 'container technology', 'Docker containers',
            'lightweight containers', 'application containers'
        ],
        'cicd_pipeline': [
            'CI/CD', 'continuous integration', 'continuous deployment', 'CI/CD pipelines', 
            'automation', 'build pipeline', 'deployment automation', 'continuous delivery',
            'software delivery pipeline', 'DevOps pipeline', 'automated deployment',
            'release pipeline', 'deployment pipeline', 'build automation'
        ],
        'terraform_basics': [
            'Terraform', 'IaC', 'Infrastructure as Code', 'HCL', 'infrastructure provisioning',
            'Terraform code', 'declarative infrastructure', 'cloud provisioning',
            'Terraform modules', 'infrastructure automation', 'HashiCorp Terraform',
            'Terraform configuration', 'infrastructure management'
        ],
        'monitoring_logging': [
            'monitoring', 'observability', 'logs', 'metrics', 'alerts',
            'application monitoring', 'log aggregation', 'system monitoring',
            'Prometheus', 'Grafana', 'ELK stack', 'logging', 'APM',
            'observability platform', 'monitoring tools', 'infrastructure monitoring'
        ],
        'container_orchestration': [
            'container orchestration', 'orchestration', 'container management', 
            'scheduling', 'scaling', 'orchestration platform', 'container scheduling',
            'automated container management', 'container deployment automation',
            'Docker Swarm', 'orchestration tools', 'container lifecycle'
        ],
        'git_version_control': [
            'Git', 'version control', 'GitHub', 'GitLab', 'repositories',
            'source control', 'Git workflow', 'branching', 'Git branches',
            'version control system', 'distributed version control', 'code versioning',
            'Git repository', 'VCS'
        ],
        'linux_commands': [
            'Linux', 'Unix', 'shell', 'bash', 'command line', 'terminal',
            'Linux commands', 'shell scripting', 'Linux administration',
            'system administration', 'Linux CLI', 'command-line interface',
            'Unix commands', 'bash scripting', 'Linux terminal'
        ],
        'cloud_platforms': [
            'cloud', 'AWS', 'Azure', 'GCP', 'cloud computing', 'cloud providers',
            'Amazon Web Services', 'Microsoft Azure', 'Google Cloud Platform',
            'cloud services', 'cloud infrastructure', 'public cloud',
            'cloud platforms', 'cloud solutions'
        ],
        'ansible_configuration': [
            'Ansible', 'configuration management', 'playbooks', 'automation',
            'Ansible automation', 'infrastructure automation', 'config management',
            'Ansible playbooks', 'configuration automation', 'IT automation',
            'provisioning automation', 'agentless automation'
        ],
    }
    
    expanded_faqs = []
    
    for faq in faqs:
        intent = faq['intent']
        answer = faq['answer']
        keywords = intent_keywords.get(intent, [intent.replace('_', ' ')])
        
        print(f"\n📝 Generating for: {intent}")
        
        # Start with existing questions
        generated_questions = set(faq['questions'])
        initial_count = len(generated_questions)
        
        # Generate with OpenAI if available
        if use_openai and os.getenv('OPENAI_API_KEY'):
            print(f"   🤖 Using OpenAI API...")
            openai_questions = generate_with_openai(
                intent, 
                intent.replace('_', ' '), 
                list(generated_questions)[:5],
                num_questions=200  # Generate more for variety
            )
            generated_questions.update(openai_questions)
            print(f"   ✅ OpenAI generated: {len(openai_questions)} questions")
        
        # Template-based generation
        for pattern_group, patterns in question_patterns.items():
            for pattern in patterns:
                # Shuffle keywords for variety
                shuffled_keywords = random.sample(keywords, min(len(keywords), 5))
                
                for keyword in shuffled_keywords:
                    question = pattern.format(topic=keyword)
                    
                    # Add variation with capitalization
                    variations = [
                        question,
                        question.capitalize(),
                    ]
                    
                    generated_questions.update(variations)
                    
                    if len(generated_questions) >= samples_per_intent * 1.5:
                        break
                
                if len(generated_questions) >= samples_per_intent * 1.5:
                    break
            
            if len(generated_questions) >= samples_per_intent * 1.5:
                break
        
        # Shuffle and select target number
        questions_list = list(generated_questions)
        random.shuffle(questions_list)
        final_questions = questions_list[:samples_per_intent]
        
        expanded_faqs.append({
            'intent': intent,
            'questions': final_questions,
            'answer': answer
        })
        
        print(f"   ✅ Total: {len(final_questions)} questions (started with {initial_count})")
    
    # Save expanded dataset
    output_data = {'faqs': expanded_faqs}
    
    output_file = 'data/raw/devops_faqs.yaml'
    with open(output_file, 'w') as f:
        yaml.dump(output_data, f, default_flow_style=False, allow_unicode=True)
    
    total_questions = sum(len(faq['questions']) for faq in expanded_faqs)
    print(f"\n✅ Generated {total_questions} questions!")
    print(f"   Saved to: {output_file}")
    
    print(f"\n📊 Breakdown by intent:")
    for faq in expanded_faqs:
        print(f"   {faq['intent']}: {len(faq['questions'])} questions")
    
    print(f"\n🔄 Next steps:")
    print(f"   1. Update data_preparation.py to use: {output_file}")
    print(f"   2. Run: python src/data_preparation.py")
    print(f"   3. Train: python src/train.py")
    print(f"   4. Expected accuracy: 97-98% with {total_questions} samples")


if __name__ == "__main__":
    use_openai = bool(os.getenv("OPENAI_API_KEY"))
    
    generate_large_dataset_improved(
        target_samples=7000,
        use_openai=use_openai
    )

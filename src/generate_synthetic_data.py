import os
import json
import yaml
import random
import requests
import time
import re
from pathlib import Path

GENERATION_PROMPT = """Generate 25 diverse, high-quality questions that a DevOps engineer might ask about {intent_topic}.

Intent: {intent_name}
Topic: {intent_topic}

Example questions:
{example_questions}

Requirements:
- Questions should be natural and varied (how people actually talk)
- Include different phrasings (what, how, why, explain, tell me, etc.)
- Mix beginner, intermediate, and advanced questions
- Include comparisons, troubleshooting, and best practices
- Make them realistic for real DevOps scenarios
- Include practical "how-to" questions
- Each question must end with "?"

Generate 25 NEW questions (different from examples):"""

def generate_with_openai(intent_name, intent_topic, example_questions, num_questions=100):
    try:
        import openai
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("No OpenAI API key found")
            return []
        
        client = openai.OpenAI(api_key=api_key)
        
        prompt = GENERATION_PROMPT.format(
            intent_name=intent_name,
            intent_topic=intent_topic,
            example_questions="\n".join(f"- {q}" for q in example_questions[:5])
        )
        
        all_questions = []
        batches = (num_questions + 24) // 25
        
        for batch_num in range(batches):
            print(f"Batch {batch_num + 1}/{batches} (GPT-4o)...", end='', flush=True)
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a senior DevOps architect with 15+ years of experience. Generate realistic, high-quality training questions that DevOps engineers would actually ask. Focus on practical scenarios."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    temperature=0.85,
                    max_tokens=1500,
                    top_p=0.9,
                )
                
                generated_text = response.choices[0].message.content
                questions = [q.strip('- ').strip() for q in generated_text.split('\n') 
                            if q.strip() and any(c.isalpha() for c in q)]
                
                cleaned = []
                for q in questions:
                    q = q.lstrip('0123456789.-) ').strip()
                    if (q and 
                        len(q) > 15 and 
                        '?' in q and
                        not q.startswith(('Question', 'Note', 'Example'))):
                        cleaned.append(q)
                
                all_questions.extend(cleaned)
                print(f" +{len(cleaned)}")
                
                time.sleep(1)
                
            except Exception as e:
                print(f" Error: {e}")
                continue
        
        unique_questions = list(set(all_questions))
        print(f"Total unique from GPT-4o: {len(unique_questions)}")
        return unique_questions[:num_questions]
        
    except ImportError:
        print("\nOpenAI not installed. Run: pip install openai")
        return []
    except Exception as e:
        print(f"\nOpenAI API error: {e}")
        return []

def scrape_stackoverflow_data(keywords, max_questions=300):
    BASE_URL = "https://api.stackexchange.com/2.3/search/advanced"
    all_questions = []
    
    for tag in keywords[:3]:
        tag_clean = tag.lower().replace(' ', '-')
        print(f"      Fetching: {tag_clean}", end='')
        
        params = {
            "order": "desc",
            "sort": "votes",
            "tagged": tag_clean,
            "site": "stackoverflow",
            "pagesize": 100,
        }
        
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            data = response.json()
            
            for item in data.get("items", [])[:100]:
                title = item.get("title", "").strip()
                if len(title) > 15 and '?' in title:
                    all_questions.append(title)
            
            print(f" +{len([t for t in all_questions[-100:] if t])}")
            time.sleep(0.5)
        except Exception as e:
            print(f" Error: {e}")
    
    return list(set(all_questions))[:max_questions]

def paraphrase_question(question, variations=2):
    paraphrases = [question]
    
    transforms = [
        (r'^What is ', 'Can you explain '),
        (r'^What is ', 'Tell me about '),
        (r'^How do I ', 'How can I '),
        (r'^How does (.+) work\?', r'Explain how \1 works'),
        (r'\?$', ' please?'),
    ]
    
    for old, new in transforms:
        if len(paraphrases) >= variations + 1:
            break
        modified = re.sub(old, new, question, flags=re.IGNORECASE)
        if modified != question:
            paraphrases.append(modified)
    
    return paraphrases

def score_question_quality(question):
    score = 50
    
    if '?' in question:
        score += 10
    if any(w in question.lower() for w in ['what', 'how', 'why']):
        score += 10
    if 10 < len(question.split()) < 25:
        score += 10
    if '{' in question or '}' in question:
        score -= 50
    if len(question) < 10:
        score -= 30
    
    return max(0, min(100, score))

def augment_with_variations(questions, rate=0.3):
    augmented = list(questions)
    
    abbrevs = {
        'kubernetes': 'k8s',
        'continuous integration': 'CI',
        'continuous deployment': 'CD',
        'infrastructure as code': 'IaC',
    }
    
    for question in list(questions)[:int(len(questions) * rate)]:
        for full, abbrev in abbrevs.items():
            if full in question.lower():
                aug_q = re.sub(full, abbrev, question, flags=re.IGNORECASE)
                if aug_q != question:
                    augmented.append(aug_q)
    
    return augmented

def validate_dataset(expanded_faqs):
    issues = []
    
    for faq in expanded_faqs:
        intent = faq['intent']
        questions = faq['questions']
        
        if len(questions) != len(set(questions)):
            issues.append(f"{intent}: Has duplicate questions")
        
        template_errors = [q for q in questions if '{' in q or '}' in q]
        if template_errors:
            issues.append(f"{intent}: {len(template_errors)} unfilled templates")
        
        short_questions = [q for q in questions if len(q) < 10]
        if short_questions:
            issues.append(f"{intent}: {len(short_questions)} questions too short")
        
        if not faq.get('answer'):
            issues.append(f"{intent}: Missing answer")
    
    if issues:
        print("\n  Dataset Issues Found:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("\n Dataset validation passed!")
    
    return len(issues) == 0

def generate_large_dataset_improved(
    target_samples=15000,
    use_openai=True,
    use_stackoverflow=True
):
    
    print(f"Target: {target_samples} samples")
    print(f"   OpenAI GPT-4o: {'OpenAI model used' if use_openai and os.getenv('OPENAI_API_KEY') else ''}")
    print(f"   Stack Overflow: {'Stackoverflow used' if use_stackoverflow else ''}")
    
    if use_openai and os.getenv('OPENAI_API_KEY'):
        print(f"Estimated cost: $2-3 (one-time investment for best quality)")
    
    with open('data/raw/devops_faqs.yaml', 'r') as f:
        faqs = yaml.safe_load(f)['faqs']
    
    samples_per_intent = target_samples // len(faqs)
    
    print(f"\n Configuration:")
    print(f"   Intents: {len(faqs)}")
    print(f"   Samples per intent: {samples_per_intent}")
    
    intent_keywords = {
        'kubernetes_basics': [
            'kubernetes', 'k8s', 'container-orchestration', 'pods', 'kubectl'
        ],
        'docker_basics': [
            'docker', 'containers', 'dockerfile', 'docker-compose'
        ],
        'cicd_pipeline': [
            'ci-cd', 'continuous-integration', 'jenkins', 'gitlab-ci', 'github-actions'
        ],
        'terraform_basics': [
            'terraform', 'infrastructure-as-code', 'iac', 'hashicorp'
        ],
        'monitoring_logging': [
            'monitoring', 'prometheus', 'grafana', 'logging', 'observability'
        ],
        'container_orchestration': [
            'container-orchestration', 'kubernetes', 'docker-swarm', 'orchestration'
        ],
        'git_version_control': [
            'git', 'github', 'version-control', 'gitlab'
        ],
        'linux_commands': [
            'linux', 'bash', 'shell', 'unix', 'command-line'
        ],
        'cloud_platforms': [
            'aws', 'azure', 'gcp', 'cloud-computing', 'amazon-web-services'
        ],
        'ansible_configuration': [
            'ansible', 'configuration-management', 'automation', 'ansible-playbook'
        ],
    }
    
    question_patterns = {
        'what_patterns': [
            "What is {topic}?",
            "What does {topic} do?",
            "What are {topic}?",
            "Can you explain what {topic} is?",
            "Tell me what {topic} means",
            "Define {topic}",
            "What exactly is {topic}?",
        ],
        'explain_patterns': [
            "Explain {topic}",
            "Can you explain {topic}?",
            "Help me understand {topic}",
            "Describe {topic}",
            "Break down {topic}",
            "Give me an overview of {topic}",
        ],
        'how_patterns': [
            "How does {topic} work?",
            "How do I use {topic}?",
            "How to implement {topic}?",
            "How to get started with {topic}?",
            "How to configure {topic}?",
            "How should I use {topic}?",
        ],
        'why_patterns': [
            "Why use {topic}?",
            "Why is {topic} important?",
            "What are the benefits of {topic}?",
            "Why choose {topic}?",
            "What makes {topic} useful?",
        ],
        'learning_patterns': [
            "Learn {topic}",
            "{topic} tutorial",
            "{topic} guide",
            "Getting started with {topic}",
            "{topic} for beginners",
        ],
        'comparison_patterns': [
            "{topic} vs alternatives",
            "Compare {topic}",
            "Should I use {topic}?",
        ],
    }
    
    expanded_faqs = []
    
    for faq in faqs:
        intent = faq['intent']
        answer = faq['answer']
        keywords = intent_keywords.get(intent, [intent.replace('_', ' ')])
        
        print(f"\n {intent} (target: {samples_per_intent})")
        
        generated_questions = set(faq['questions'])
        initial = len(generated_questions)
        
        if use_stackoverflow:
            print(f"Stack Overflow:")
            so_qs = scrape_stackoverflow_data(keywords, max_questions=400)
            generated_questions.update(so_qs)
            print(f"Total SO: {len(so_qs)} questions")
        

        if use_openai and os.getenv('OPENAI_API_KEY'):
            print(f"GPT-4o generation:")
            try:
                openai_qs = generate_with_openai(
                    intent, 
                    intent.replace('_', ' '), 
                    list(generated_questions)[:5], 
                    400
                )
                generated_questions.update(openai_qs)
                print(f"Total GPT-4o: {len(openai_qs)} questions")
            except Exception as e:
                print(f"Error: {e}")
        
        print(f"    Templates: ", end='')
        template_count = 0
        for pattern_group, patterns in question_patterns.items():
            for pattern in patterns:
                for keyword in keywords:
                    keyword_readable = keyword.replace('-', ' ')
                    question = pattern.format(topic=keyword_readable)
                    generated_questions.add(question)
                    generated_questions.add(question.capitalize())
                    template_count += 2
        print(f"+{template_count}")
        
        print(f"Paraphrasing: ", end='')
        base_questions = list(generated_questions)[:200]
        para_count = 0
        for q in base_questions:
            paraphrases = paraphrase_question(q, variations=3)
            para_count += len(paraphrases) - 1
            generated_questions.update(paraphrases)
        print(f"+{para_count}")
        
        generated_questions = set(augment_with_variations(list(generated_questions), rate=0.3))
        

        high_quality = [q for q in generated_questions 
                       if score_question_quality(q) >= 50]
        
        random.shuffle(high_quality)
        final_questions = high_quality[:samples_per_intent]
        
        expanded_faqs.append({
            'intent': intent,
            'questions': final_questions,
            'answer': answer
        })
        
        print(f"Final: {len(final_questions)} questions")
    
    output_data = {'faqs': expanded_faqs}
    output_file = 'data/raw/devops_faqs.yaml'
    
    Path('data/raw').mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        yaml.dump(output_data, f, default_flow_style=False, allow_unicode=True)
    
    total = sum(len(faq['questions']) for faq in expanded_faqs)
    print(f"\n Generated {total} high-quality questions with GPT-4o!")
    print(f"   Saved to: {output_file}")
    
    validate_dataset(expanded_faqs)
    
    print(f"\n Breakdown by intent:")
    for faq in expanded_faqs:
        print(f"   {faq['intent']}: {len(faq['questions'])} questions")
    
    return expanded_faqs

if __name__ == "__main__":
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    
    if not has_openai:
        print("\n To use GPT-4o generation (recommended for best quality):")
        print("   export OPENAI_API_KEY='sk-your-key-here'")
        print("\n   Proceeding with Stack Overflow + Templates only...\n")
    else:
        print("\n OpenAI API key detected - using GPT-4o (latest model)")
        print("   This will generate the highest quality training data\n")
    
    generate_large_dataset_improved(
        target_samples=15000,
        use_openai=has_openai,
        use_stackoverflow=True
    )

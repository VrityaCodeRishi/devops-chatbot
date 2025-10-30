import yaml

# Read current data
with open('data/raw/devops_faqs.yaml', 'r') as f:
    data = yaml.safe_load(f)

faqs = data['faqs']

# Find the two intents
k8s_idx = next(i for i, f in enumerate(faqs) if f['intent'] == 'kubernetes_basics')
orch_idx = next(i for i, f in enumerate(faqs) if f['intent'] == 'container_orchestration')

k8s = faqs[k8s_idx]
orch = faqs[orch_idx]

# Move K8s-specific questions from orchestration to k8s
k8s_keywords = ['kubernetes', 'k8s', 'kubectl', 'pod', 'deployment', 'service', 'namespace', 'cluster', 'operator']

# Clean orchestration questions
clean_orch = []
moved_to_k8s = []

for q in orch['questions']:
    q_lower = q.lower()
    # If question mentions K8s, move it
    if any(keyword in q_lower for keyword in k8s_keywords):
        moved_to_k8s.append(q)
    else:
        clean_orch.append(q)

print(f"🔄 Moving {len(moved_to_k8s)} K8s-specific questions from orchestration to kubernetes_basics")
print(f"✅ Keeping {len(clean_orch)} generic orchestration questions")

# Update
faqs[k8s_idx]['questions'].extend(moved_to_k8s)
faqs[orch_idx]['questions'] = clean_orch

# Clean kubernetes questions (remove generic orchestration)
clean_k8s = []
generic_orch = ['orchestration', 'orchestrate', 'orchestrating']

for q in k8s['questions']:
    q_lower = q.lower()
    # If it's purely generic orchestration (no K8s mention), skip it
    has_k8s = any(kw in q_lower for kw in k8s_keywords)
    has_generic = any(kw in q_lower for kw in generic_orch)
    
    if has_generic and not has_k8s:
        print(f"❌ Removing generic from K8s: {q}")
    else:
        clean_k8s.append(q)

faqs[k8s_idx]['questions'] = clean_k8s

# Save
with open('data/raw/devops_faqs_clean.yaml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

print(f"\n✅ Saved to data/raw/devops_faqs_clean.yaml")
print(f"📊 Final counts:")
print(f"   kubernetes_basics: {len(faqs[k8s_idx]['questions'])}")
print(f"   container_orchestration: {len(faqs[orch_idx]['questions'])}")
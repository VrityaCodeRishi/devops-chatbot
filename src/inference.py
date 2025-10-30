import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import json
from pathlib import Path

class DevOpsChatbot:
    def __init__(self, model_path='models/distilbert-devops-faq'):
        print(f" Loading model from {model_path}...")
        
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
        
        self.context_answers = self._load_context_answers()
    
    def _load_context_answers(self):
        return {
            'kubernetes_basics': {
                'default': "Kubernetes is an open-source container orchestration platform that automates deployment, scaling, and management of containerized applications. It uses a master-worker architecture with pods as the smallest deployable units.",
                'manage': "Kubernetes manages containerized applications through a control plane that handles scheduling, scaling, and monitoring. It automatically distributes containers across nodes, restarts failed containers, and scales applications based on demand.",
                'orchestrate': "Kubernetes orchestrates containers by scheduling them on worker nodes, managing their lifecycle, handling networking between containers, and ensuring desired state is maintained through controllers like Deployments and ReplicaSets.",
                'pods': "Kubernetes pods are the smallest deployable units that can contain one or more containers. Pods share networking and storage, and Kubernetes manages pod placement, replication, and lifecycle automatically.",
                'work': "Kubernetes works by using a declarative approach where you define desired state in YAML files. The control plane continuously monitors actual state and makes changes to match desired state, handling container scheduling, health checks, and auto-scaling.",
                'difference': "Kubernetes is a container orchestration platform, while Docker is a containerization platform. Docker creates and runs containers, whereas Kubernetes manages multiple Docker containers at scale across clusters, handling deployment, scaling, networking, and high availability.",
                'deploy': "Kubernetes deploys containerized applications using Deployments, which define the desired number of pod replicas. It handles rolling updates, rollbacks, scaling, and ensures pods are distributed across nodes for high availability.",
            },
            'docker_basics': {
                'default': "Docker is a containerization platform that packages applications and their dependencies into lightweight, portable containers. Unlike VMs, containers share the host OS kernel, making them more efficient and faster to start.",
                'work': "Docker works by packaging application code with all dependencies into container images. The Docker Engine runs these images as isolated containers that share the host kernel but maintain separate filesystems, processes, and networking.",
                'containerize': "Docker containerizes applications by creating layers of filesystem changes in a Dockerfile. Each instruction creates a new layer, and the final image contains everything needed to run the application in any environment.",
                'images': "Docker images are read-only templates containing application code, runtime, libraries, and dependencies. Images are built from Dockerfiles and can be stored in registries like Docker Hub. Containers are running instances of images.",
                'vs': "Docker containers share the host OS kernel and are more lightweight than VMs. VMs include a full OS copy, making them heavier. Containers start in seconds vs minutes for VMs, and use significantly less resources.",
            },
            'cicd_pipeline': {
                'default': "CI/CD (Continuous Integration/Continuous Deployment) automates the software delivery process from code commit to production deployment. CI merges code changes frequently with automated testing, while CD automatically deploys validated changes to production.",
                'pipeline': "A CI/CD pipeline automates stages from code commit through build, test, and deployment. It typically includes source control integration, automated builds, unit and integration tests, security scans, and automated deployment to staging and production.",
                'delivery': "The DevOps delivery pipeline automates software delivery through stages: source → build → test → deploy. It includes version control, automated testing, artifact creation, deployment automation, and monitoring, ensuring fast and reliable releases.",
                'automation': "CI/CD automation eliminates manual steps in software delivery. Automated testing runs on every commit, builds are triggered automatically, deployments happen without human intervention, and rollbacks are automated if issues are detected.",
            },
            'terraform_basics': {
                'default': "Terraform is an Infrastructure as Code (IaC) tool that allows you to define and provision cloud resources using declarative configuration files (HCL). It supports multiple cloud providers and maintains state for infrastructure management.",
                'provision': "Terraform provisions infrastructure by reading configuration files (HCL), creating an execution plan showing what will be created/modified, and then applying changes to cloud providers through their APIs. It tracks state to manage infrastructure lifecycle.",
                'state': "Terraform state tracks resource metadata and relationships. It's stored in a state file (local or remote) and used to map real resources to configuration. State enables Terraform to know what exists and what changes are needed.",
                'modules': "Terraform modules are reusable packages of Terraform configurations. They encapsulate resources and enable infrastructure reuse. Modules can be shared across projects and versioned independently.",
            },
            'monitoring_logging': {
                'default': "Application monitoring involves collecting metrics, logs, and traces for observability. Popular tools include Prometheus for metrics, Grafana for visualization, and ELK/EFK stack (Elasticsearch, Logstash/Fluentd, Kibana) for log aggregation and analysis.",
                'metrics': "Metrics are numerical measurements collected over time (CPU usage, request latency, error rates). Logs are event records with timestamps. Metrics provide quantitative data for alerting and trends, while logs provide detailed context for debugging.",
                'prometheus': "Prometheus collects metrics by scraping HTTP endpoints at regular intervals. Applications expose metrics in Prometheus format, and Prometheus stores time-series data. It includes a query language (PromQL) for analysis and alerting.",
                'observability': "The three pillars of observability are metrics (quantitative data), logs (event records), and traces (request flows). Together they provide complete visibility into system behavior, performance, and issues.",
            },
            'git_version_control': {
                'default': "Git is a distributed version control system that tracks code changes. GitHub/GitLab are platforms hosting Git repositories. Common branching strategies include GitFlow, trunk-based development, and feature branching for team collaboration.",
                'branching': "GitFlow uses main/develop branches with feature, release, and hotfix branches. Trunk-based development commits directly to main with short-lived feature branches. Feature branching creates branches for each feature that merge via pull requests.",
                'workflow': "Git workflow typically includes: clone repository → create feature branch → make changes → commit → push → create pull request → code review → merge. Teams choose workflows based on size and release cadence.",
            },
            'linux_commands': {
                'default': "Essential Linux commands include: ls (list), cd (change directory), grep (search), ps (processes), top (monitoring), tail (logs), chmod (permissions), and systemctl (services). Understanding these is crucial for DevOps work.",
                'troubleshoot': "For Linux troubleshooting: check logs with tail/journalctl, monitor processes with top/htop, check disk with df/du, analyze network with netstat/ss, check services with systemctl, and use grep to search logs for errors.",
                'monitor': "Monitor Linux processes with: top (real-time view), htop (interactive), ps aux (snapshot), systemctl status (services), journalctl (logs), and tools like vmstat (memory), iostat (I/O), and sar (system activity).",
            },
            'cloud_platforms': {
                'default': "Major cloud platforms include AWS (largest market share, most services), Azure (best for Microsoft ecosystem), and GCP (strong in ML/data analytics). Choose based on existing expertise, regional availability, pricing, and specific service requirements.",
                'choose': "Choose cloud providers based on: existing team expertise, specific service needs (e.g., ML on GCP), enterprise agreements, regional compliance requirements, pricing models, and ecosystem integration. Consider multi-cloud for vendor independence.",
                'comparison': "AWS offers the most services and largest ecosystem. Azure integrates best with Microsoft tools and enterprise systems. GCP excels in data analytics, ML, and Kubernetes. All three provide global infrastructure, similar core services, and competitive pricing.",
            },
            'ansible_configuration': {
                'default': "Ansible is an agentless configuration management and automation tool using YAML playbooks. It's simpler than Puppet/Chef (which require agents), making it popular for infrastructure provisioning, application deployment, and configuration management.",
                'automate': "Ansible automates infrastructure through playbooks (YAML files) that define desired state. It connects via SSH, executes tasks idempotently, and can manage thousands of servers. Tasks are organized in roles for reusability.",
                'playbooks': "Ansible playbooks are YAML files containing plays (groups of tasks). Each task uses modules to perform actions like installing packages, copying files, or managing services. Playbooks are idempotent, so they can run multiple times safely.",
            },
            'container_orchestration': {
                'default': "Container orchestration automates deployment, scaling, and management of containerized applications. Kubernetes is the industry standard, offering advanced features like auto-scaling, self-healing, and rolling updates. Docker Swarm is simpler but less feature-rich.",
                'scale': "Container orchestration manages containers at scale by automating deployment across clusters, handling load balancing, scaling replicas based on demand, monitoring health, and replacing failed containers automatically.",
            },
        }
    
    def _get_contextual_answer(self, intent, question):
        question_lower = question.lower()
        
        if intent not in self.context_answers:
            return self.answer_map.get(intent, "I'm not sure how to answer that.")
        
        intent_answers = self.context_answers[intent]
        
        keywords = {
            'manage': ['manage', 'managing', 'management'],
            'orchestrate': ['orchestrate', 'orchestration', 'orchestrating'],
            'pods': ['pod', 'pods'],
            'work': ['work', 'works', 'working', 'does'],
            'difference': ['difference', 'different', 'vs', 'versus', 'compare', 'comparison'],
            'deploy': ['deploy', 'deployment', 'deploying'],
            'containerize': ['containerize', 'containerization', 'containerizing'],
            'images': ['image', 'images'],
            'pipeline': ['pipeline', 'pipelines'],
            'delivery': ['delivery', 'deliver'],
            'automation': ['automate', 'automation', 'automated'],
            'provision': ['provision', 'provisioning'],
            'state': ['state', 'states'],
            'modules': ['module', 'modules'],
            'metrics': ['metric', 'metrics', 'logs', 'difference between'],
            'prometheus': ['prometheus'],
            'observability': ['observability', 'pillars', 'three'],
            'branching': ['branch', 'branching', 'strategy', 'strategies'],
            'workflow': ['workflow', 'process'],
            'troubleshoot': ['troubleshoot', 'debug', 'issue', 'problem'],
            'monitor': ['monitor', 'monitoring', 'processes'],
            'choose': ['choose', 'choosing', 'select', 'which'],
            'comparison': ['comparison', 'compare', 'vs'],
            'automate': ['automate', 'automation'],
            'playbooks': ['playbook', 'playbooks'],
            'scale': ['scale', 'scaling', 'at scale'],
        }
        
        for context, context_keywords in keywords.items():
            if any(kw in question_lower for kw in context_keywords):
                if context in intent_answers:
                    return intent_answers[context]
        
        return intent_answers.get('default', self.answer_map.get(intent))
    
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
        
        answer = self._get_contextual_answer(intent, question)
        
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
                print("\n Goodbye!")
                break
            
            if not question:
                continue
            
            result = self.predict(question)
            print(f"\n Bot: {result['answer']}")
            print(f"   Intent: {result['intent']} (Confidence: {result['confidence']:.2%})\n")

if __name__ == "__main__":
    chatbot = DevOpsChatbot()
    chatbot.chat()

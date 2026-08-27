import subprocess
import json

# 1. Criar Milestones
milestones = [
    {"title": "v0.1 - Fundação e Core Multi-Tenant", "description": "Setup de infraestrutura, autenticação JWT com 2FA TOTP e isolamento de workspaces."},
    {"title": "v0.2 - Gestão de Contas e Lançamentos 4D (MVP)", "description": "Contas, cartões, taxonomia em 4 dimensões e equalização do casal."},
    {"title": "v0.3 - Módulo Sair do Vermelho e Diagnóstico", "description": "Gestão de dívidas, motor Avalanche vs. Bola de Neve e termômetro DTI."},
    {"title": "v0.4 - Radar de Gastos e Reserva de Emergência", "description": "Tetos orçamentários, detecção de desperdício e cofre da reserva."},
    {"title": "v0.5 - Projeções e Importação de Dados", "description": "Fluxo de caixa preditivo 12 meses e importação bancária OFX/CSV."}
]

for m in milestones:
    subprocess.run(["gh", "api", "repos/anselmo-nonato/kivo/milestones", "-f", f"title={m['title']}", "-f", f"description={m['description']}"], capture_output=True)

# 2. Criar Labels personalizadas
labels = [
    {"name": "epic", "color": "3E4B9B", "description": "Épicos e módulos principais"},
    {"name": "backend", "color": "0052CC", "description": "Tarefas de API FastAPI e PostgreSQL"},
    {"name": "frontend", "color": "1D76DB", "description": "Tarefas de interface Next.js / React"},
    {"name": "security", "color": "B60205", "description": "Autenticação, 2FA e RLS"},
    {"name": "finance-engine", "color": "008672", "description": "Motores de cálculo financeiro e matemático"}
]

for l in labels:
    subprocess.run(["gh", "label", "create", l["name"], "--color", l["color"], "--description", l["description"], "--repo", "anselmo-nonato/kivo", "--force"], capture_output=True)

print("Milestones e Labels criadas com sucesso no GitHub!")

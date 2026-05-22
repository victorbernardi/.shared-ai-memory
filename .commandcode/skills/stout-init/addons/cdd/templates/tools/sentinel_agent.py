import os
import sys
import io
import json
import yaml
from pathlib import Path

# Garante que o diretório raiz esteja no path para as importações de 'src'
root_dir = Path(__file__).parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from src.tools.gcc_analytics import GCCAnalytics
from src.config import config

# Reconfigura o output para UTF-8 (Corta o mal pela raiz no Windows)
if sys.platform == "win32" and not isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class SentinelAgent:
    """
    Agente Sentinela para Otimização Autônoma (Self-Healing).
    Analisa falhas e lacunas de intenção para propor melhorias no rules.yaml.
    """
    def __init__(self):
        self.analytics = GCCAnalytics()
        self.failure_log_path = Path("notes/failure-log.md")

    def run_audit(self):
        """Executa a auditoria completa do ecossistema."""
        print("\n" + "🛡️ " * 5 + " INICIANDO AUDITORIA DO AGENTE SENTINELA " + "🛡️ " * 5)
        
        self.analytics.parse_all()
        unmapped = self._find_unmapped_intents()
        failures = self._parse_failure_log()
        
        proposals = []
        
        if unmapped:
            proposals.append(self._propose_rule_for_unmapped(unmapped))
        
        if failures:
            proposals.append(self._propose_fix_for_failures(failures))

        self._display_audit_results(unmapped, failures, proposals)

    def _find_unmapped_intents(self):
        """Identifica interações onde a intenção não foi mapeada pelo motor de regras."""
        unmapped_checkpoints = [cp for cp in self.analytics.checkpoints if cp.get('intent') in ['N/A', 'PARSE_ERROR']]
        return unmapped_checkpoints

    def _parse_failure_log(self) -> list:
        """Lê o log de falhas e extrai eventos recentes."""
        if not self.failure_log_path.exists():
            return []
        
        # Tenta UTF-8 primeiro, depois UTF-16 (comum em arquivos criados pelo PowerShell/Windows)
        try:
            with open(self.failure_log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            try:
                with open(self.failure_log_path, 'r', encoding='utf-16') as f:
                    lines = f.readlines()
            except Exception as e:
                print(f"[-] Erro fatal ao ler log de falhas: {e}")
                return []
        
        # Filtra apenas linhas que parecem ser registros de erro (ex: contendo timestamp)
        return [line.strip() for line in lines if line.startswith('- [')]

    def _propose_rule_for_unmapped(self, unmapped):
        """Cria uma proposta de nova regra baseada em intenções órfãs."""
        count = len(unmapped)
        return {
            "type": "NEW_RULE",
            "reason": f"Detectadas {count} interações com intenção não mapeada.",
            "suggestion": {
                "id": f"auto_rule_{datetime.now().strftime('%Y%m%d')}",
                "priority": 1,
                "enabled": True,
                "filter": {"operator": "eq", "field": "intent", "value": "PENDENTE_DEFINIR"},
                "action": {"type": "activate_skill", "target": "PENDENTE_DEFINIR"}
            }
        }

    def _propose_fix_for_failures(self, failures):
        """Propõe uma revisão de sistema baseada em falhas registradas."""
        return {
            "type": "SYSTEM_CHECK",
            "reason": f"Existem {len(failures)} registros de falha no failure-log.md.",
            "suggestion": "Verificar se as regras ativadas durante as falhas possuem dependências quebradas ou schemas inválidos."
        }

    def _display_audit_results(self, unmapped, failures, proposals):
        """Exibe o diagnóstico e as propostas de melhoria."""
        print(f"\n[DIAGNÓSTICO]")
        print(f"-> Intenções Órfãs: {len(unmapped)}")
        print(f"-> Falhas Críticas: {len(failures)}")
        
        if not proposals:
            print("\n✅ O sistema está operando com 100% de cobertura e estabilidade.")
            return

        print("\n" + "💡 PROPOSTAS DE AUTO-OTIMIZAÇÃO:")
        for i, prop in enumerate(proposals, 1):
            print(f"\n{i}. [{prop['type']}] - {prop['reason']}")
            if isinstance(prop['suggestion'], dict):
                print("Sugestão de YAML:")
                print(yaml.dump([prop['suggestion']], sort_keys=False))
            else:
                print(f"Sugestão: {prop['suggestion']}")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    from datetime import datetime
    sentinel = SentinelAgent()
    sentinel.run_audit()

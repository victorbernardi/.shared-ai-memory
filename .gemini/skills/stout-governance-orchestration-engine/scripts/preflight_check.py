import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Configuração de Logging para a Skill
logging.basicConfig(level=logging.INFO, format="%(asctime)s [GOVERNANCE] %(message)s")
logger = logging.getLogger("GovernanceEngine")

def check_utf8_hygiene():
    """Garante que o ambiente suporte UTF-8 para evitar erros de encoding no Windows."""
    try:
        if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")
        logger.info("🟢 Higiene de Encoding: UTF-8 configurado.")
        return True
    except Exception as e:
        logger.warning(f"🟡 Falha ao reconfigurar encoding: {e}")
        return False

def check_fabric_connector(shared_dir: Path):
    """Verifica se o conector do Fabric e as dependências Java estão presentes."""
    connector_path = shared_dir / "fabric_db.py"
    config_path = shared_dir / "config.py"
    
    missing = []
    if not connector_path.exists(): missing.append("fabric_db.py")
    if not config_path.exists(): missing.append("config.py")
    
    if missing:
        logger.error(f"🔴 Erro de Ambiente: Arquivos críticos ausentes em /shared: {', '.join(missing)}")
        return False
    
    logger.info("🟢 Ambiente: Conectores e configurações de infraestrutura localizados.")
    return True

def parse_recency_report(shared_dir: Path, fail_fast: bool = False):
    """Lê o recency_status.md e emite alertas sobre fontes obsoletas."""
    recency_file = shared_dir / "recency_status.md"
    
    if not recency_file.exists():
        logger.warning(f"🟡 Governança: Relatório de recência não encontrado em {recency_file}.")
        return True # Não bloqueia se o relatório estiver ausente
        
    outdated = []
    try:
        with open(recency_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        for line in lines:
            if "|" in line and ("🔴" in line or "🟡" in line):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 4:
                    fonte = parts[1]
                    status = parts[3]
                    outdated.append(f"{fonte} ({status})")
        
        if outdated:
            logger.warning("⚠️  ALERTA DE RECÊNCIA: Fontes desatualizadas detectadas!")
            for item in outdated:
                logger.warning(f"   - {item}")
            if fail_fast:
                logger.error("🔴 Fail-Fast Ativado: Interrompendo execução por obsolescência de dados.")
                return False
        else:
            logger.info("🟢 Recência: Todas as fontes estão atualizadas conforme relatório.")
            
    except Exception as e:
        logger.error(f"🔴 Erro ao processar relatório de recência: {e}")
        return False
        
    return True

def run_preflight(shared_path: str, fail_fast: bool = False):
    """Orquestrador do Checklist de Decolagem."""
    logger.info("=== Iniciando Pre-flight Check (Stout Governance) ===")
    
    shared_dir = Path(shared_path)
    
    checks = [
        check_utf8_hygiene(),
        check_fabric_connector(shared_dir),
        parse_recency_report(shared_dir, fail_fast)
    ]
    
    if all(checks):
        logger.info("✅ Pre-flight concluído: Motor pronto para processamento.")
        return True
    else:
        logger.error("❌ Pre-flight falhou ou emitiu alertas críticos.")
        return False

if __name__ == "__main__":
    # Exemplo de uso via CLI para teste isolado
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--shared", required=True, help="Caminho para a pasta /shared")
    parser.add_argument("--fail-fast", action="store_true", help="Interromper em caso de erro")
    args = parser.parse_args()
    
    success = run_preflight(args.shared, args.fail_fast)
    sys.exit(0 if success else 1)

import os
import json
import shutil
import argparse
from datetime import datetime, timedelta, timezone
from filelock import FileLock
from sync_wire_client import ARCHIVE_MAX_MSG, ARCHIVE_MAX_DAYS, LOCK_TIMEOUT

def archive_protocol_files(base_path=".", max_msg=ARCHIVE_MAX_MSG, max_days=ARCHIVE_MAX_DAYS, dry_run=False):
    jsonl_path = os.path.join(base_path, "SYNC_WIRE.jsonl")
    idx_path = os.path.join(base_path, "SYNC_WIRE.idx")
    lock_path = jsonl_path + ".lock"
    
    if not os.path.exists(jsonl_path):
        print("[!] Arquivo JSONL não encontrado.")
        return

    # 1. Verifica se precisa de rotação
    should_rotate = False
    
    # Contagem de mensagens (linhas)
    line_count = 0
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f: line_count += 1
    
    if line_count >= max_msg:
        print(f"[*] Limite de mensagens atingido ({line_count}/{max_msg}).")
        should_rotate = True
        
    # Idade do arquivo (simplificado pela data de modificação)
    mtime = datetime.fromtimestamp(os.path.getmtime(jsonl_path), tz=timezone.utc)
    if datetime.now(timezone.utc) - mtime > timedelta(days=max_days):
        print(f"[*] Limite de tempo atingido ({max_days} dias).")
        should_rotate = True

    if not should_rotate:
        print("[*] Nenhuma rotação necessária no momento.")
        return

    if dry_run:
        print("[DRY RUN] Rotação seria executada agora.")
        return

    # 2. Executa rotação com Lock
    lock = FileLock(lock_path, timeout=LOCK_TIMEOUT)
    with lock:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"SYNC_WIRE_{timestamp}.jsonl"
        archive_path = os.path.join(base_path, "docs/decisions/", archive_name) # Movendo para decisions como histórico
        
        print(f"[*] Arquivando mensagens antigas em: {archive_path}")
        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        shutil.copy2(jsonl_path, archive_path)
        
        # Truncar mantendo as últimas 50 mensagens (hot window)
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        keep_lines = lines[-50:]
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            f.writelines(keep_lines)
            
        # Resetar índice para reconstrução pelo monitor
        with open(idx_path, 'w', encoding='utf-8') as f:
            json.dump({"last_offset": 0}, f)
            
        print("[*] Rotação concluída com sucesso.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arquivador/Rotacionador SYNC_WIRE v2.0")
    parser.add_argument("--max-msg", type=int, default=ARCHIVE_MAX_MSG)
    parser.add_argument("--max-days", type=int, default=ARCHIVE_MAX_DAYS)
    parser.add_argument("--dry-run", action="store_true")
    
    args = parser.parse_args()
    archive_protocol_files(max_msg=args.max_msg, max_days=args.max_days, dry_run=args.dry_run)

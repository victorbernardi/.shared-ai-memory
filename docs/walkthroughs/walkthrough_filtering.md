# Walkthrough: Filtragem de Entidades Internas (John Deere & Inova)

Implementação concluída com sucesso. Os faturamentos e potenciais de mercado associados à própria Inova e à fábrica (John Deere Brasil) foram removidos dos datasets principais.

## ✅ O que foi feito
1. **Configuração Centralizada:** Adição da `BLACKLIST_ROOTS` em `config_inova_identity.py`.
2. **Motor M2 (Faturamento):** Implementação de filtro para remover John Deere Brasil e Inova.
3. **Motor M3 (Potencial):** 
    - Remoção de entidades internas (JD/Inova).
    - **Filtro de Território:** Remoção de máquinas com `AOR Indicator` = "Outside dealer AOR".
4. **Impacto Mensurado:**
    - **Faturamento:** Redução de ~R$ 7,9M.
    - **Potencial (Interno):** Redução de ~R$ 954k.
    - **Potencial (Território/AOR):** Redução de **R$ 82,2M**.

## 📊 Resultados da Validação Final

### Motor M3 - Log (Resumo)
```json
"Estatisticas": {
    "Grupos_Mapeados": 1249,
    "Potencial_Total_Anual": 443744108.72,
    "Potencial_Excluido_Interno": 954540.28,
    "Potencial_Excluido_Fora_AOR": 82267185.26,
    "Chassis_Com_Dono": 2883
}
```

### Motor M5 - BI Output
- **Faturamento Bruto Total:** R$ 179.450.169,44
- **Potencial Total Geral:** R$ 443.744.108,72
- **SOW Global:** **23,09%**

## 📂 Arquivos Modificados
- [config_inova_identity.py](file:///C:/Projetos/Inova/Potencial%20Clientes/config_inova_identity.py)
- [motor_de_faturamento_v1.py](file:///C:/Projetos/Inova/Potencial%20Clientes/02_Faturamento/motor_de_faturamento_v1.py)
- [motor_de_potencial_v1_run.py](file:///C:/Projetos/Inova/Potencial%20Clientes/03_Potencial/motor_de_potencial_v1_run.py)

---
*Assinado: Antigravity*

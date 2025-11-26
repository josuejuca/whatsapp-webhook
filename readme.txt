Versão: 0.1.0 (Webhook Whatsapp)

$25/11/2025 

Criação da lógica do sistema: 
[ ] Webhook
[ ] Filter 
[ ] BOT
[ ] AI 
[ ] Flow

Essa API está sendo desenvolvida para uso nos sistemas da META (WhatsApp) usando fluxos e bots de autoatendimento. 

Banco de dados do MySQL 

[whatsapp_db_webhook]

- webhook
    - id 
    - date 
    - json 
- contacts
    - id 
    - wa_id 
    - profile (bot, ia, human)
    - name 
    - create_in
    - last_message

$26/11/2025 
Lógica do sistema:
[ ] Webhook
[ ] Filter 
[ ] BOT
[ ] AI 
[ ] Flow

Ajustes / Melhorias: 
- Melhoria no banco de dados e no webhook. 
- Foi adicionado logs mais claros para debug.
- Salvamento no banco de dados.
- Possibilidade de trabalhar com vários números. 
- Filter
- Ajuste no init asynccontextmanager()

Banco de dados atualizado: 

Banco de dados do MySQL 

[whatsapp_db_webhook]

- webhook
    - id 
    - date 
    - json 
- contacts
    - id 
    - wa_id 
    - profile # (human, bot, ia) 
    - name 
    - create_in
    - activate_bot # true or false
    - activate_automatic_message # true or false
    - create_for_phone_number 
    - last_message_timestamp
- settings
    - id
    - default_bot
    - default_profile # human
    - wa_id
    - phone_number_id 
    - webhook_verify_token 
    - meta_token

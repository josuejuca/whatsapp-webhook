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


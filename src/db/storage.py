import os
import mysql.connector
from mysql.connector import Error
from typing import Optional, Dict, Any
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()

class DatabaseStorage:
    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME")
        self.port = int(os.getenv("DB_PORT") or 3306)
        self.connection = None
        
    def _get_connection(self, include_db: bool = True):
        """Cria conexão com o MySQL"""
        try:
            if include_db:
                conn = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    port=self.port
                )
            else:
                conn = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    port=self.port
                )
            return conn
        except Error as e:
            print(f"Erro ao conectar ao MySQL: {e}")
            return None

    def check_connection(self) -> bool:
        """Verifica se consegue conectar ao banco"""
        conn = self._get_connection(include_db=False)
        if conn and conn.is_connected():
            conn.close()
            return True
        return False

    def create_database(self) -> bool:
        """Cria o banco de dados se não existir"""
        try:
            conn = self._get_connection(include_db=False)
            if not conn:
                return False
            
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            print(f"✓ Banco de dados '{self.database}' verificado/criado")
            cursor.close()
            conn.close()
            return True
        except Error as e:
            print(f"Erro ao criar banco de dados: {e}")
            return False

    def create_tables(self) -> bool:
        """Cria as tabelas se não existirem"""
        try:
            conn = self._get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            # Tabela webhook
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS webhook (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    json JSON NOT NULL
                )
            """)
            print("✓ Tabela 'webhook' verificada/criada")
            
            # Tabela contacts - CHAVE COMPOSTA (wa_id + create_for_phone_number)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    wa_id VARCHAR(50) NOT NULL,
                    profile VARCHAR(50) DEFAULT 'human',
                    name VARCHAR(255),
                    create_in DATETIME DEFAULT CURRENT_TIMESTAMP,
                    activate_bot BOOLEAN DEFAULT FALSE,
                    activate_automatic_message BOOLEAN DEFAULT FALSE,
                    create_for_phone_number VARCHAR(50) NOT NULL,
                    last_message_timestamp BIGINT,
                    UNIQUE KEY unique_conversation (wa_id, create_for_phone_number)
                )
            """)
            print("✓ Tabela 'contacts' verificada/criada")
            
            # Tabela settings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    default_bot VARCHAR(50),
                    default_profile VARCHAR(50) DEFAULT 'human',
                    wa_id VARCHAR(50),
                    phone_number_id VARCHAR(50),
                    webhook_verify_token VARCHAR(255),
                    meta_token TEXT
                )
            """)
            print("✓ Tabela 'settings' verificada/criada")
            
            # Insere configuração padrão se não existir
            cursor.execute("SELECT COUNT(*) FROM settings")
            count = cursor.fetchone()[0]
            if count == 0:
                meta_token = os.getenv("META_TOKEN", None)
                cursor.execute("""
                    INSERT INTO settings (default_bot, default_profile, wa_id, phone_number_id, webhook_verify_token, meta_token) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (None, 'human', '556181412286', '524386454098961', '7b5a67574d8b1d77d2803b24946950f0', meta_token))
                print("✓ Configuração padrão inserida")
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Error as e:
            print(f"Erro ao criar tabelas: {e}")
            return False

    def initialize(self) -> bool:
        """Inicializa o banco de dados completo"""
        print("Inicializando banco de dados...")
        
        if not self.check_connection():
            print("✗ Não foi possível conectar ao MySQL")
            return False
        print("✓ Conexão com MySQL estabelecida")
        
        if not self.create_database():
            print("✗ Erro ao criar/verificar banco de dados")
            return False
        
        if not self.create_tables():
            print("✗ Erro ao criar/verificar tabelas")
            return False
        
        print("✓ Banco de dados inicializado com sucesso!")
        return True

    def save_webhook(self, webhook_data: Dict[str, Any]) -> Optional[int]:
        """Salva o payload do webhook completo"""
        try:
            conn = self._get_connection()
            if not conn:
                return None
            
            cursor = conn.cursor()
            query = "INSERT INTO webhook (json) VALUES (%s)"
            cursor.execute(query, (json.dumps(webhook_data),))
            conn.commit()
            
            webhook_id = cursor.lastrowid
            cursor.close()
            conn.close()
            
            print(f"✓ Webhook salvo com ID: {webhook_id}")
            return webhook_id
        except Error as e:
            print(f"Erro ao salvar webhook: {e}")
            return None

    def save_or_update_contact(
        self, 
        wa_id: str, 
        name: str,
        phone_number_id: str,
        timestamp: int
    ) -> bool:
        """Salva ou atualiza um contato com base nas configurações"""
        try:
            conn = self._get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor(dictionary=True)
            
            # Busca configurações do número
            cursor.execute(
                "SELECT default_profile FROM settings WHERE phone_number_id = %s", 
                (phone_number_id,)
            )
            settings = cursor.fetchone()
            
            # Define profile e activate_bot baseado nas settings
            if settings:
                profile = settings.get('default_profile', 'human')
                activate_bot = False if profile == 'human' else True
            else:
                profile = 'human'
                activate_bot = False
            
            # Verifica se ESTA CONVERSA ESPECÍFICA existe (wa_id + phone_number_id)
            cursor.execute(
                "SELECT id, create_in FROM contacts WHERE wa_id = %s AND create_for_phone_number = %s", 
                (wa_id, phone_number_id)
            )
            contact = cursor.fetchone()
            
            if contact:
                # Conversa já existe - atualiza
                query = """
                    UPDATE contacts 
                    SET name = %s, last_message_timestamp = %s 
                    WHERE wa_id = %s AND create_for_phone_number = %s
                """
                cursor.execute(query, (name, timestamp, wa_id, phone_number_id))
                
                first_message_date = contact['create_in'].strftime('%d/%m/%Y %H:%M:%S')
                print(f"✓ Contato {wa_id} ({name}) atualizado")
                print(f"  └─ Conversa com número: {phone_number_id}")
                print(f"  └─ Primeira mensagem desta conversa foi em: {first_message_date}")
                print(f"  └─ Esta é mais uma mensagem nesta conversa")
            else:
                # Nova conversa - insere
                query = """
                    INSERT INTO contacts 
                    (wa_id, name, profile, create_for_phone_number, last_message_timestamp, activate_bot, activate_automatic_message) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    wa_id, 
                    name, 
                    profile, 
                    phone_number_id, 
                    timestamp, 
                    activate_bot, 
                    False
                ))
                
                now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                print(f"✓ Nova conversa criada: {wa_id} ({name}) → {phone_number_id}")
                print(f"  └─ Esta é a PRIMEIRA mensagem desta conversa")
                print(f"  └─ Criado em: {now}")
                print(f"  └─ Profile: {profile}")
                print(f"  └─ Bot ativado: {activate_bot}")
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Error as e:
            print(f"Erro ao salvar/atualizar contato: {e}")
            return False

    def get_settings(self) -> Optional[Dict[str, Any]]:
        """Busca as configurações do sistema"""
        try:
            conn = self._get_connection()
            if not conn:
                return None
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM settings WHERE id = 1")
            settings = cursor.fetchone()
            
            cursor.close()
            conn.close()
            return settings
        except Error as e:
            print(f"Erro ao buscar configurações: {e}")
            return None

# Instância global
db = DatabaseStorage()
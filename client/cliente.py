import pika
import json
import uuid
import datetime
import random
from datetime import datetime, timedelta
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sys
import customtkinter
from tkinter import PhotoImage
import pytz
import logging
import os
from database import connect_to_db, get_mutuals

class PhysicalClock:
    def __init__(self):
        self.offset = timedelta(0)

    def now(self):
        # 30% de chance de drift ±1 s
        if random.random() < 0.3:
            delta = timedelta(seconds=random.choice([-1, 1]))
            self.offset += delta
            print(f"[Drift] aplicando {delta.total_seconds()}s, offset={self.offset.total_seconds()}s")
            logging.info(f"[Drift] aplicando {delta.total_seconds()}s, offset={self.offset.total_seconds()}s")
        return datetime.now(pytz.timezone("America/Sao_Paulo")) + self.offset

class LogicalClock:
    def __init__(self):
        self.counter = 0

    def tick(self):
        self.counter += 1
        return self.counter

    def update(self, remote_ts):
        self.counter = max(self.counter, remote_ts) + 1
        return self.counter

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/client-python.log",
    level=logging.INFO,
    format="%(asctime)sZ [client-python] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)

# instâncias globais
phy_clock = PhysicalClock()
lamport   = LogicalClock()

# Variáveis globais para armazenar credenciais
config = {
    'dbname':'NOME DA DATABASE',
    'user':'NOME DO USER',
    'password':'SENHA',
    'host':'HOST',
    'port':'26257'
}

print(get_mutuals("a"))
print(get_mutuals("b"))
print(get_mutuals("c"))

# Função para criar conta
def create_account():
    username = entry_username.get().strip()
    password = entry_password.get().strip()
    confirm_password = entry_confirm_password.get().strip()

    if not username or not password:
        messagebox.showerror("Erro", "Usuário e senha são obrigatórios.")
        return

    if password != confirm_password:
        messagebox.showerror("Erro", "As senhas não coincidem.")
        return

    conn = connect_to_db()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            # Verificar se o usuário já existe no banco de dados
            cur.execute("SELECT COUNT(*) FROM usuario WHERE usuario_nome = %s", (username,))
            if cur.fetchone()[0] > 0:
                messagebox.showerror("Erro", "Usuário já existe.")
                return

            # Inserir o novo usuário no banco de dados
            cur.execute(
            "INSERT INTO usuario (usuario_nome, senha) VALUES (%s, %s)",
            (username, password)
            )
            conn.commit()
            messagebox.showinfo("Sucesso", "Conta criada com sucesso!")
            logging.info(f"CREATE_ACCOUNT usuário={username}")
            switch_to_login()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao criar conta: {e}")
        logging.error(f"CREATE_ACCOUNT-ERROR usuário={username} erro={e}")
    finally:
        conn.close()

# Função para realizar login
def login():
    username = entry_login_username.get().strip()
    password = entry_login_password.get().strip()

    if not username or not password:
        messagebox.showerror("Erro", "Usuário e senha são obrigatórios.")
        logging.warning(f"LOGIN_FAILED usuário={username}")
        return

    conn = connect_to_db()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            # Verificar se o usuário e senha estão corretos no banco de dados
            cur.execute("SELECT senha FROM usuario WHERE usuario_nome = %s ", (username,))
            result = cur.fetchone()
            if not result or result[0] != password:
                messagebox.showerror("Erro", "Usuário ou senha inválidos.")
                logging.warning(f"LOGIN_FAILED usuário={username}")
                return

            messagebox.showinfo("Sucesso", f"Bem-vindo, {username}!")
            logging.info(f"LOGIN_SUCCESS usuário={username}")
            root.withdraw()  # Oculta a janela principal
            threading.Thread(target=start_rabbitmq_listener, args=(username,), daemon=True).start()
            open_menu(username)  # Abre o menu principal
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao realizar login: {e}")
        logging.error(f"LOGIN-ERROR usuário={username} erro={e}")
    finally:
        conn.close()

# Função para alternar para a tela de login
def switch_to_login():
    frame_create_account.pack_forget()
    frame_login.pack()

# Função para alternar para a tela de criação de conta
def switch_to_create_account():
    frame_login.pack_forget()
    frame_create_account.pack()

# Função principal do cliente
def start_client(user_id):
    # 1) publica um follow de exemplo (igual ao seu)
    ts_phys = phy_clock.now().isoformat()
    ts_lamp = lamport.tick()
    props   = pika.BasicProperties(delivery_mode=2,
                                   headers={'logicalTimestamp': ts_lamp})
    follow_msg = {
        "type":       "follow",
        "followerId": user_id,
        "followedId": "outro_usuario",
        "timestamp":  ts_phys
    }
    conn = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    ch   = conn.channel()
    ch.exchange_declare(exchange='follows', exchange_type='fanout', durable=True)
    ch.basic_publish(exchange='follows', routing_key='', body=json.dumps(follow_msg), properties=props)
    print(f"[Você → Follow] fis={ts_phys} lamp={ts_lamp}")
    logging.info(f"ENVIAR_FOLLOW follower={user_id} followed=outro_usuario fis={ts_phys} lamp={ts_lamp}")

    # 2) listener de follows
    def on_follow(ch, method, props, body):
        remote = props.headers.get('logicalTimestamp', 0)
        local  = lamport.update(remote)
        msg    = json.loads(body)
        print(f"[Lamport Cliente] Follow remoto={remote} → local={local}")
        print(f"[Notificação] {msg['followerId']} seguiu {msg['followedId']}")
        logging.info(f"RECEBER_FOLLOW from={msg['followerId']} to={msg['followedId']} lamport_remote={remote} lamport_local={local}")

    def follow_listener():
        fconn = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        fch   = fconn.channel()
        fch.exchange_declare(exchange='follows', exchange_type='fanout', durable=True)
        qf = fch.queue_declare('', exclusive=True).method.queue
        fch.queue_bind(exchange='follows', queue=qf)
        fch.basic_consume(queue=qf, on_message_callback=on_follow, auto_ack=True)
        fch.start_consuming()

    threading.Thread(target=follow_listener, daemon=True).start()

    # 3) listener de posts
    def on_post(ch, method, props, body):
        remote = props.headers.get('logicalTimestamp', 0)
        local  = lamport.update(remote)
        msg    = json.loads(body)
        print(f"[Lamport Cliente] Post remoto={remote} → local={local}")
        print(f"[Notificação] {msg['userId']} postou: {msg['content']}")
        logging.info(f"RECEBER_POST from={msg['userId']} content=\"{msg['content']}\" lamport_remote={remote} lamport_local={local}")

    def post_listener():
        pconn = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        pch   = pconn.channel()
        pch.exchange_declare(exchange='posts', exchange_type='fanout', durable=True)
        qp = pch.queue_declare('', exclusive=True).method.queue
        pch.queue_bind(exchange='posts', queue=qp)
        pch.basic_consume(queue=qp, on_message_callback=on_post, auto_ack=True)
        pch.start_consuming()

    threading.Thread(target=post_listener, daemon=True).start()

    # 4) loop de envio de posts (igual ao seu):
    while True:
        content = input("> ")
        if content.lower()=="sair": break

        ts_phys = phy_clock.now().isoformat()
        ts_lamp = lamport.tick()
        props   = pika.BasicProperties(delivery_mode=2, headers={'logicalTimestamp': ts_lamp})
        post_msg = {
            "type":    "post",
            "postId":  str(uuid.uuid4()),
            "userId":  user_id,
            "content": content,
            "timestamp": ts_phys
        }
        ch.basic_publish(exchange='posts', routing_key='', body=json.dumps(post_msg), properties=props)
        print(f"[Você → Post] fis={ts_phys} lamp={ts_lamp}")
        logging.info(f"ENVIAR_POST user={user_id} postId={post_msg['postId']} fis={ts_phys} lamp={ts_lamp}")

    conn.close()

def start_rabbitmq_listener(username):
    try:
        # 1) Conectar ao RabbitMQ e criar canal
        conn = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        ch   = conn.channel()

        # —————————————————————————————
        # POSTS
        ch.exchange_declare(exchange='posts', exchange_type='fanout', durable=True)
        queue_posts = ch.queue_declare('', exclusive=True).method.queue
        ch.queue_bind(exchange='posts', queue=queue_posts)

        def on_post(ch, method, properties, body):
            remote_ts = properties.headers.get('logicalTimestamp', 0)
            local_ts  = lamport.update(remote_ts)
            print(f"[Lamport {username}] Post remoto={remote_ts} → local={local_ts}")
            msg = json.loads(body)
            print(f"[Notificação {username}] {msg['userId']} postou: {msg['content']}")

        ch.basic_consume(queue=queue_posts, on_message_callback=on_post, auto_ack=True)


        # —————————————————————————————
        # FOLLOWS
        ch.exchange_declare(exchange='follows', exchange_type='fanout', durable=True)
        queue_follows = ch.queue_declare('', exclusive=True).method.queue
        ch.queue_bind(exchange='follows', queue=queue_follows)

        def on_follow(ch, method, properties, body):
            remote_ts = properties.headers.get('logicalTimestamp', 0)
            local_ts  = lamport.update(remote_ts)
            print(f"[Lamport {username}] Follow remoto={remote_ts} → local={local_ts}")
            msg = json.loads(body)
            print(f"[Notificação {username}] {msg['followerId']} seguiu {msg['followedId']}")

        ch.basic_consume(queue=queue_follows, on_message_callback=on_follow, auto_ack=True)


        # —————————————————————————————
        # PRIVATE MESSAGES (caso queira)
        ch.exchange_declare(exchange='private_messages', exchange_type='fanout', durable=True)
        queue_pm = ch.queue_declare('', exclusive=True).method.queue
        ch.queue_bind(exchange='private_messages', queue=queue_pm)

        def on_private(ch, method, properties, body):
            remote_ts = properties.headers.get('logicalTimestamp', 0)
            local_ts  = lamport.update(remote_ts)
            print(f"[Lamport {username}] Privado remoto={remote_ts} → local={local_ts}")
            msg = json.loads(body)
            print(f"[Mensagem Privada {username}] {msg['sender']}: {msg['content']}")

        ch.basic_consume(queue=queue_pm, on_message_callback=on_private, auto_ack=True)


        print(f"[RabbitMQ] {username} escutando posts, follows e mensagens privadas…")
        ch.start_consuming()

    except Exception as e:
        print(f"[Erro RabbitMQ] {e}")



def open_menu(username):

    # 1) Criar janela principal
    menu_window = customtkinter.CTkToplevel(root)
    menu_window.title(f"Bem-vindo, {username}")
    menu_window.geometry(f"{900}x{600}")
    menu_window.minsize(900,600)
    menu_window.maxsize(900,600)


    customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
    customtkinter.set_default_color_theme("pink.json")  # Themes: "blue" (standard), "green", "dark-blue"

    # 2) Configurar grid (sidebar coluna 0, content_area coluna 1)
    menu_window.grid_rowconfigure(0, weight=1)
    menu_window.grid_columnconfigure(0, weight=0)
    menu_window.grid_columnconfigure(1, weight=1)

    # 3) Sidebar
    sidebar = customtkinter.CTkFrame(menu_window, width=140, corner_radius=0)
    sidebar.grid(row=0, column=0, sticky="nsew")  
    sidebar.grid_rowconfigure(4, weight=1)

    # 4) Área de conteúdo
    content_area = customtkinter.CTkFrame(menu_window, corner_radius=10)
    content_area.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    # Funções internas para gerenciar conteúdo
    def limpar_conteudo():
        for w in content_area.winfo_children():
            w.destroy()

    def follow_user():
        limpar_conteudo()
        # Container para exibir os posts
        follow_frame = customtkinter.CTkFrame(content_area)
        follow_frame.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        # Título
        customtkinter.CTkLabel(follow_frame, text="   Seguindo   ", font=("Arial", 16)).pack(
            anchor="w", pady=(0, 10)
        )

        # Obter a lista de usuários do banco de dados
        conn = connect_to_db()
        if not conn:
            messagebox.showerror("Erro", "Erro ao conectar ao banco de dados.")
            return

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT usuario_nome FROM usuario WHERE usuario_nome != %s", (username,)
                )
                users = [row[0] for row in cur.fetchall()]
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar usuários: {e}")
            # follow_window.destroy()
            return
        finally:
            conn.close()

        # Verificar se há usuários disponíveis para seguir
        if not users:
            messagebox.showinfo(
                "Informação", "Não há outros usuários disponíveis para seguir."
            )
            # follow_window.destroy()
            return

        # Campo de seleção para o nome do usuário a ser seguido
        customtkinter.CTkLabel(follow_frame, text="   Selecione o usuário que deseja seguir:   ").pack()
        user_combobox = ttk.Combobox(
            follow_frame, values=users, state="readonly", width=30
        )
        user_combobox.pack(pady=5)

        def submit_follow():
            follow = user_combobox.get().strip()
            if not follow:
                messagebox.showerror("Erro", "Selecione um usuário para seguir.")
                return

            conn = connect_to_db()
            if conn:
                try:
                    with conn.cursor() as cur:
                        # Atualizar a lista de "seguindo" do usuário
                        cur.execute(
                            "SELECT seguindo FROM usuario WHERE usuario_nome = %s",
                            (username,),
                        )
                        result = cur.fetchone()
                        seguindo = (
                            json.loads(result[0])
                            if result and isinstance(result[0], str)
                            else []
                        )

                        if follow not in seguindo:
                            seguindo.append(follow)
                            cur.execute(
                                """
                                UPDATE usuario
                                SET seguindo = seguindo || %s::jsonb
                                WHERE usuario_nome = %s
                                AND NOT EXISTS (
                                    SELECT 1
                                    FROM jsonb_array_elements_text(seguindo) AS elem(value)
                                    WHERE elem.value = %s
                                )
                                """,
                                (json.dumps([follow]), username, follow),
                            )

                        # Atualizar a lista de "seguido_por" do usuário seguido
                        cur.execute(
                            "SELECT seguido_por FROM usuario WHERE usuario_nome = %s",
                            (follow,),
                        )
                        result = cur.fetchone()
                        seguido_por = (
                            json.loads(result[0])
                            if result and isinstance(result[0], str)
                            else []
                        )

                        if username not in seguido_por:
                            seguido_por.append(username)
                            cur.execute(
                                """
                                UPDATE usuario
                                SET seguido_por = seguido_por || %s::jsonb
                                WHERE usuario_nome = %s
                                AND NOT EXISTS (
                                    SELECT 1
                                    FROM jsonb_array_elements_text(seguido_por) AS elem(value)
                                    WHERE elem.value = %s
                                )
                                """,
                                (json.dumps([username]), follow, username),
                            )

                        conn.commit()

                        # Conectar ao RabbitMQ e publicar o evento de follow
                        rabbit_conn = pika.BlockingConnection(
                            pika.ConnectionParameters(host="rabbitmq")
                        )
                        ch = rabbit_conn.channel()
                        ch.exchange_declare(
                            exchange="follows", exchange_type="fanout", durable=True
                        )

                        # Publicar o follow COM DRIFT e LAMPORT
                        ts_phys = phy_clock.now().isoformat()
                        ts_lamp = lamport.tick()
                        props   = pika.BasicProperties(
                            delivery_mode=2,
                            headers={'logicalTimestamp': ts_lamp}
                        )
                        follow_msg = {
                            "type": "follow",
                            "followerId": username,
                            "followedId": follow,
                            "timestamp": ts_phys
                        }
                        ch.basic_publish(
                            exchange="follows",
                            routing_key="",
                            body=json.dumps(follow_msg),
                            properties=props
                        )

                        
                        messagebox.showinfo(
                            "Sucesso", f"Agora você está seguindo {follow}!"
                        )
                        logging.info(f"FOLLOW_DB_UPDATE user={username} follow={follow}")
                        logging.info(f"ENVIAR_FOLLOW via UI follower={username} followed={follow} fis={ts_phys} lamp={ts_lamp}")
                        rabbit_conn.close()
                        
                        # follow_window.destroy()
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao seguir usuário: {e}")
                    logging.error(f"FOLLOW_ERROR user={username} follow={follow} erro={e}")
                    
                finally:
                    conn.close()
                    
                    


        # Botão para confirmar o follow
        customtkinter.CTkButton(
            follow_frame, text="Seguir", command=submit_follow
        ).pack(pady=10)

    def private_message():
        limpar_conteudo()

        # Container principal
        pm_frame = customtkinter.CTkFrame(content_area)
        pm_frame.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        # Título
        customtkinter.CTkLabel(
            pm_frame, text="   Mensagens Privadas   ", font=("Arial", 16)
        ).pack(anchor="w", pady=(0, 10))

        customtkinter.CTkLabel(pm_frame, text="   Selecione o usuário que deseja conversar:   ").pack()

        # 1) Combobox de mutuals
        mutuals = get_mutuals(username)
        combobox = ttk.Combobox(pm_frame, values=mutuals, state="readonly", width=30)
        combobox.pack(pady=5)

        # 2) Área de chat (scrollable)
        chat_frame = customtkinter.CTkScrollableFrame(pm_frame, height=300)
        chat_frame.pack(fill="both", expand=True, pady=(10, 0))

        def load_chat(event=None):
            # limpa histórico
            for w in chat_frame.winfo_children():
                w.destroy()

            other = combobox.get().strip()
            if not other:
                return

            conn = connect_to_db()
            try:
                with conn.cursor() as cur:
                    # 1) Puxa seu JSONB de private_messages
                    cur.execute(
                        "SELECT mensagens_privadas FROM usuario WHERE usuario_nome = %s",
                        (username,)
                    )
                    row = cur.fetchone()
                    my_pm = row[0] or {}
                    if isinstance(my_pm, str):
                        my_pm = json.loads(my_pm)

                    # 2) Puxa o JSONB dele
                    cur.execute(
                        "SELECT mensagens_privadas FROM usuario WHERE usuario_nome = %s",
                        (other,)
                    )
                    row2 = cur.fetchone()
                    their_pm = row2[0] or {}
                    if isinstance(their_pm, str):
                        their_pm = json.loads(their_pm)

                    # 3) Extrai as duas conversas
                    my_convo    = my_pm.get(other, {})    # mensagens que você enviou
                    their_convo = their_pm.get(username, {})  # mensagens que ele enviou

                    # 4) Une tudo num único dicionário
                    combined = {}
                    combined.update(my_convo)
                    combined.update(their_convo)

                    # 5) Exibe em ordem cronológica
                    for ts in sorted(combined):
                        msg = combined[ts]
                        tag = "Você" if msg["sender"] == username else msg["sender"]
                        texto = f"{tag} ({ts[:19]}): {msg['content']}"
                        customtkinter.CTkLabel(
                            chat_frame,
                            text=texto,
                            wraplength=600,
                            justify="left"
                        ).pack(anchor="w", padx=5, pady=2)

            finally:
                conn.close()


        # 3) Campo de entrada + botão Enviar
        entry = customtkinter.CTkEntry(pm_frame, placeholder_text="Digite sua mensagem...")
        entry.pack(fill="x", pady=(10, 0), padx=5)

        def send_private():
            other = combobox.get().strip()
            text  = entry.get().strip()
            if not other or not text:
                messagebox.showerror("Erro", "Selecione um usuário e digite algo.")
                return

            # 1) Gere UM SÓ ts_phys (com drift)
            ts_phys = phy_clock.now().isoformat()
            new_msg = { ts_phys: {"sender": username, "content": text} }

            conn = connect_to_db()
            if not conn:
                messagebox.showerror("Erro", "Não foi possível conectar ao banco.")
                return

            try:
                # 2) Atualiza o JSONB no banco com ts_phys
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE usuario
                        SET mensagens_privadas = jsonb_set(
                                mensagens_privadas,
                                %s,
                                COALESCE(mensagens_privadas #> %s, '{}'::jsonb) || %s::jsonb,
                                true
                            )
                        WHERE usuario_nome = %s
                        """,
                        (
                            [other],             # caminho no JSON
                            [other],             # idem para #>
                            json.dumps(new_msg), # nosso novo par {ts_phys: {...}}
                            username
                        )
                    )
                    conn.commit()

                # 3) Publique no RabbitMQ COM Lamport no header
                ts_lamp = lamport.tick()
                props   = pika.BasicProperties(
                    delivery_mode=2,
                    headers={'logicalTimestamp': ts_lamp}
                )
                private_msg = {
                    "type":      "private",
                    "sender":    username,
                    "recipient": other,
                    "content":   text,
                    "timestamp": ts_phys
                }

                rabbit_conn = pika.BlockingConnection(
                    pika.ConnectionParameters(host="rabbitmq")
                )
                ch = rabbit_conn.channel()
                ch.exchange_declare(
                    exchange="private_messages",
                    exchange_type="fanout",
                    durable=True
                )
                ch.basic_publish(
                    exchange="private_messages",
                    routing_key="",
                    body=json.dumps(private_msg),
                    properties=props
                )
                logging.info(f"ENVIAR_PRIVATE sender={username} recipient={other} content=\"{text}\" fis={ts_phys} lamp={ts_lamp}")
                rabbit_conn.close()

                # 4) Atualize a UI recarregando o chat com ts_phys já salvo
                entry.delete(0, "end")
                load_chat()

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao enviar mensagem privada: {e}")
                logging.error(f"PRIVATE_ERROR sender={username} recipient={other} erro={e}")
            finally:
                conn.close()


            # 4) Atualize a UI recarregando o chat (com o ts_phys já no banco)
            entry.delete(0, "end")
            load_chat()


        combobox.bind("<<ComboboxSelected>>", load_chat) # vai aparecer as mensagens logo quando eu selecionar alguma pessoa

        customtkinter.CTkButton(pm_frame, text="Enviar", command=send_private)\
                       .pack(pady=5)


    def mostrar_post_feed():
        limpar_conteudo()

        # Container para exibir os posts
        posts_frame = customtkinter.CTkFrame(content_area)
        posts_frame.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        # Título
        customtkinter.CTkLabel(posts_frame, text="   Posts    ", font=("Arial", 16)).pack(anchor="w", pady=(0, 10))

        post_frame = customtkinter.CTkScrollableFrame(posts_frame, height=300)
        post_frame.pack(fill="both", expand=True, pady=(10, 0))

        # Conectar ao banco e buscar posts
        conn = connect_to_db()
        if conn:
            try:
                with conn.cursor() as cur:
                    # Obter os posts do usuário e das pessoas que ele segue
                    cur.execute("""
                        SELECT usuario_nome, posts_enviados 
                        FROM usuario
                        WHERE usuario_nome = %s OR usuario_nome = ANY(
                            SELECT jsonb_array_elements_text(seguindo)
                            FROM usuario
                            WHERE usuario_nome = %s       
                        )
                    """, (username, username))
                    rows = cur.fetchall()

                    # Lista para armazenar todos os posts com timestamps
                    all_posts = []

                    for row in rows:
                        user, posts = row
                        if posts:
                            # Verificar se o valor é uma string antes de carregar como JSON
                            if isinstance(posts, str):
                                posts = json.loads(posts)

                            for timestamp, post_data in posts.items():
                                all_posts.append((timestamp, user, post_data['conteudo']))

                    # Ordenar todos os posts por timestamp
                    all_posts.sort(key=lambda x: x[0])

                    # Exibir os posts em ordem cronológica
                    for timestamp, user, content in all_posts:
                        customtkinter.CTkLabel(
                            post_frame,
                            text=f"{user} ({timestamp}): {content}",
                            anchor="w",
                            justify="left",
                            wraplength=600
                        ).pack(anchor="w")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar posts: {e}")
            finally:
                conn.close()

        # Container para criar um novo post
        new_post_frame = customtkinter.CTkFrame(content_area)
        new_post_frame.pack(fill="x", padx=10, pady=10)

        new_post_entry = customtkinter.CTkEntry(
            new_post_frame, width=400, placeholder_text="Digite seu post aqui"
        )
        new_post_entry.pack(fill="x", pady=(10, 0), padx=5)

        def submit_post():
            content = new_post_entry.get().strip()
            if not content:
                messagebox.showerror("Erro", "O conteúdo do post não pode estar vazio.")
                return

            # 1) Gere UM SÓ ts_phys (com drift) que usaremos em tudo
            ts_phys = phy_clock.now().isoformat()
            post_id = str(uuid.uuid4())

            conn = connect_to_db()
            if not conn:
                messagebox.showerror("Erro", "Não foi possível conectar ao banco.")
                return

            try:
                # 2) Atualiza o JSONB no banco com ts_phys
                novo_post = { ts_phys: {"id_post": post_id, "conteudo": content} }
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE usuario
                    SET posts_enviados = posts_enviados || %s::jsonb
                    WHERE usuario_nome = %s
                    AND NOT EXISTS (
                        SELECT 1 FROM jsonb_object_keys(posts_enviados) AS key
                        WHERE key = %s
                    )
                    """,
                    ( json.dumps(novo_post), username, ts_phys )
                )
                conn.commit()
                cur.close()

                # 3) Publique no RabbitMQ COM IMPOSTAÇÃO Lamport no header
                ts_lamp = lamport.tick()
                props   = pika.BasicProperties(
                    delivery_mode=2,
                    headers={'logicalTimestamp': ts_lamp}
                )
                post_msg = {
                    "type":      "post",
                    "postId":    post_id,
                    "userId":    username,
                    "content":   content,
                    "timestamp": ts_phys
                }

                rabbit_conn = pika.BlockingConnection(
                    pika.ConnectionParameters(host="rabbitmq")
                )
                ch = rabbit_conn.channel()
                ch.exchange_declare(exchange="posts", exchange_type="fanout", durable=True)
                ch.basic_publish(
                    exchange='posts',
                    routing_key='',
                    body=json.dumps(post_msg),
                    properties=props
                )
                rabbit_conn.close()

                # 4) Atualize a UI usando o mesmo ts_phys
                customtkinter.CTkLabel(
                    post_frame,
                    text=f"{username} ({ts_phys}): {content}",
                    anchor="w",
                    justify="left",
                    wraplength=600,
                ).pack(fill="x")
                new_post_entry.delete(0, "end")
                messagebox.showinfo("Sucesso", "Post enviado com sucesso!")
                logging.info(f"ENVIAR_POST_UI user={username} postId={post_id} content=\"{content}\" fis={ts_phys} lamp={ts_lamp}")

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao enviar post: {e}")
                logging.error(f"POST_UI_ERROR user={username} erro={e}")
            finally:
                conn.close()



        customtkinter.CTkButton(
            new_post_frame, text="Postar", command=submit_post
        ).pack(pady=5)

    # Botões da sidebar
    customtkinter.CTkButton(
        sidebar, text="Postar", command=mostrar_post_feed).grid(
        row=0, column=0, padx=20, pady=10, sticky="ew")

    customtkinter.CTkButton(
        sidebar, text="Seguir", command=follow_user).grid(
        row=1, column=0, padx=20, pady=10, sticky="ew")

    customtkinter.CTkButton(
        sidebar, text="Mensagens Privadas", command=private_message).grid(
        row=2, column=0, padx=20, pady=10, sticky="ew")

    customtkinter.CTkButton(
        sidebar,
        text="Sair",
        fg_color="transparent",
        text_color="#a31545",
        command=menu_window.destroy,
    ).grid(row=6, column=0, padx=20, pady=10, sticky="s")

    # Exibir o feed ao abrir
    mostrar_post_feed()

    menu_window.mainloop()

    # # Criar a janela principal do menu
    # menu_window = tk.Toplevel(root)
    # menu_window.title(f"Bem-vindo, {username}")

    # # Criar o menu em cascata
    # menu_bar = tk.Menu(menu_window)
    # menu_window.config(menu=menu_bar)

    # # Menu "Opções"
    # options_menu = tk.Menu(menu_bar, tearoff=0)
    # menu_bar.add_cascade(label="Opções", menu=options_menu)
    # options_menu.add_command(label="Postar", command=lambda: open_post_window(username))
    # options_menu.add_command(label="Seguir", command=lambda: follow_user(username))
    # options_menu.add_command(label="Mensagens Privadas", command=lambda: private_messages(username))
    # options_menu.add_separator()
    # options_menu.add_command(label="Sair", command=menu_window.destroy)


def encerrar_execucao():
    root.destroy()
    sys.exit()

def change_appearance_mode_event(new_appearance_mode: str):
    customtkinter.set_appearance_mode(new_appearance_mode)

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("pink.json")  # Themes: "blue" (standard), "green", "dark-blue"

# Interface gráfica

root = customtkinter.CTk()
root.title("FEICEBOOK")
root.geometry(f"{400}x{300}")
root.minsize(400, 300)
root.maxsize(400, 300)


# Frame para criar conta
frame_create_account = customtkinter.CTkFrame(root)
customtkinter.CTkLabel(frame_create_account, text="Criar Conta", font=("Arial", 16)).pack(pady=10)
customtkinter.CTkLabel(frame_create_account, text="Usuário:").pack()
entry_username = customtkinter.CTkEntry(frame_create_account)
entry_username.pack()
customtkinter.CTkLabel(frame_create_account, text="Senha:").pack()
entry_password = customtkinter.CTkEntry(frame_create_account, show="*")
entry_password.pack()
customtkinter.CTkLabel(frame_create_account, text="Confirmar Senha:").pack()
entry_confirm_password = customtkinter.CTkEntry(frame_create_account, show="*")
entry_confirm_password.pack()
customtkinter.CTkButton(frame_create_account, text="Criar Conta", command=create_account).pack(pady=10)
customtkinter.CTkButton(frame_create_account, text="Já tem uma conta? Login", command=switch_to_login).pack()
frame_create_account.pack()




# Frame para login
frame_login = customtkinter.CTkFrame(root)
customtkinter.CTkLabel(frame_login, text="Login", font=("Arial", 16)).pack(pady=10)
customtkinter.CTkLabel(frame_login, text="Usuário:").pack()
entry_login_username = customtkinter.CTkEntry(frame_login)
entry_login_username.pack()
customtkinter.CTkLabel(frame_login, text="Senha:").pack()
entry_login_password = customtkinter.CTkEntry(frame_login, show="*")
entry_login_password.pack()
customtkinter.CTkLabel(frame_login, text=" ").pack()
customtkinter.CTkLabel(frame_login, text=" ").pack()


customtkinter.CTkButton(frame_login, text="Login", command=login).pack(pady=10)
customtkinter.CTkButton(frame_login, text="Criar Conta", command=switch_to_create_account).pack()





root.mainloop()
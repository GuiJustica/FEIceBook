import pika
import json
import uuid
import datetime
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from database import connect_to_db 

# Variáveis globais para armazenar credenciais
config = {
    'dbname':'NOME DA DATABASE',
    'user':'NOME DO USER',
    'password':'SENHA',
    'host':'HOST',
    'port':'26257'
}

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
            switch_to_login()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao criar conta: {e}")
    finally:
        conn.close()

# Função para realizar login
def login():
    username = entry_login_username.get().strip()
    password = entry_login_password.get().strip()

    if not username or not password:
        messagebox.showerror("Erro", "Usuário e senha são obrigatórios.")
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
                return

            messagebox.showinfo("Sucesso", f"Bem-vindo, {username}!")
            root.withdraw()  # Oculta a janela principal
            threading.Thread(target=start_rabbitmq_listener, args=(username,), daemon=True).start()
            open_menu(username)  # Abre o menu principal
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao realizar login: {e}")
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
    follow = input(f"Digite o userId de quem {user_id} quer seguir: ").strip()
    print(f"\nVocê ({user_id}) vai seguir: {follow}\n")

    # Conectar ao RabbitMQ
    conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    ch = conn.channel()

    # Declarar ambas as exchanges
    ch.exchange_declare(exchange='follows', exchange_type='fanout', durable=True)
    ch.exchange_declare(exchange='posts', exchange_type='fanout', durable=True)

    # Publicar o evento de follow
    follow_msg = {
        "type": "follow",
        "followerId": user_id,
        "followedId": follow
    }
    ch.basic_publish(
        exchange='follows',
        routing_key='',
        body=json.dumps(follow_msg),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    print(f"[Você] Agora segue: {follow}")

    # Função que trata cada post recebido
    def on_post(ch, method, props, body):
        msg = json.loads(body)
        if msg.get("userId") == follow:
            print(f"\n[Notificação] {follow} postou: {msg['content']}\n> ", end="")

    # Thread para escutar a exchange 'posts'
    def start_listener():
        lconn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        lch = lconn.channel()
        lch.exchange_declare(exchange='posts', exchange_type='fanout', durable=True)
        q = lch.queue_declare('', exclusive=True).method.queue
        lch.queue_bind(exchange='posts', queue=q)
        lch.basic_consume(queue=q, on_message_callback=on_post, auto_ack=True)
        lch.start_consuming()

    threading.Thread(target=start_listener, daemon=True).start()

    print("Digite suas mensagens. Escreva 'sair' para encerrar.\n")

    # Loop de postagem
    while True:
        content = input("> ").strip()
        if content.lower() == "sair":
            print("Encerrando client.")
            break

        post_msg = {
            "type": "post",
            "postId": str(uuid.uuid4()),
            "userId": user_id,
            "content": content,
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
        }
        ch.basic_publish(
            exchange='posts',
            routing_key='',
            body=json.dumps(post_msg),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"[Você] Post enviado: “{content}”")

    # Fechar conexão de publicação
    conn.close()

def start_rabbitmq_listener(username):
    try:
        # Conectar ao RabbitMQ
        conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        ch = conn.channel()

        # Declarar a exchange de posts
        ch.exchange_declare(exchange='posts', exchange_type='fanout', durable=True)

        # Criar uma fila exclusiva para o usuário
        queue = ch.queue_declare('', exclusive=True).method.queue
        ch.queue_bind(exchange='posts', queue=queue)

        # Função para processar mensagens recebidas
        def on_post(ch, method, properties, body):
            msg = json.loads(body)
            user_id = msg.get("userId")
            content = msg.get("content")
            timestamp = msg.get("timestamp")
            print(f"[Notificação] {user_id} postou: {content} ({timestamp})")

        # Consumir mensagens da fila
        ch.basic_consume(queue=queue, on_message_callback=on_post, auto_ack=True)
        print(f"[RabbitMQ] Conexão ativa para o usuário {username}.")
        ch.start_consuming()
    except Exception as e:
        print(f"[Erro RabbitMQ] {e}")

def open_menu(username):
    # Criar a janela principal do menu
    menu_window = tk.Toplevel(root)
    menu_window.title(f"Bem-vindo, {username}")

    # Criar o menu em cascata
    menu_bar = tk.Menu(menu_window)
    menu_window.config(menu=menu_bar)

    # Menu "Opções"
    options_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Opções", menu=options_menu)
    options_menu.add_command(label="Postar", command=lambda: open_post_window(username))
    options_menu.add_command(label="Seguir", command=lambda: follow_user(username))
    options_menu.add_command(label="Mensagens Privadas", command=lambda: private_messages(username))
    options_menu.add_separator()
    options_menu.add_command(label="Sair", command=menu_window.destroy)

def open_post_window(username):
    # Criar a janela de postagem
    post_window = tk.Toplevel(root)
    post_window.title("Postar")

    # Container para exibir os posts
    posts_frame = tk.Frame(post_window)
    posts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Título
    tk.Label(posts_frame, text="Posts", font=("Arial", 16)).pack()

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

                for row in rows:
                    user, posts = row
                    if posts:
                        # Verificar se o valor é uma string antes de carregar como JSON
                        if isinstance(posts, str):
                            posts = json.loads(posts)
                        for timestamp, post_data in posts.items():
                            tk.Label(posts_frame, text=f"{user} ({timestamp}): {post_data['conteudo']}").pack(anchor="w")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar posts: {e}")
        finally:
            conn.close()

    # Container para criar um novo post
    new_post_frame = tk.Frame(post_window)
    new_post_frame.pack(fill=tk.X, padx=10, pady=10)

    tk.Label(new_post_frame, text="Novo Post:").pack(anchor="w")
    new_post_entry = tk.Entry(new_post_frame, width=50)
    new_post_entry.pack(side=tk.LEFT, padx=5)

    def submit_post():
        content = new_post_entry.get().strip()
        if not content:
            messagebox.showerror("Erro", "O conteúdo do post não pode estar vazio.")
            return

        conn = connect_to_db()
        if not conn:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco.")
            return

        try:
            with conn.cursor() as cur:
                # 1) Gere o timestamp e o ID do post
                timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
                post_id   = str(uuid.uuid4())

                # 2) Monte o JSONB minimalista do novo post
                novo_post = {
                    timestamp: {
                        "id_post": post_id,
                        "conteudo": content
                    }
                }

                # 3) Atualize atomically, adicionando só se a chave (timestamp) ainda não existir
                cur.execute("""
                    UPDATE usuario
                    SET posts_enviados = posts_enviados || %s::jsonb
                    WHERE usuario_nome = %s
                    AND NOT EXISTS (
                        SELECT 1
                            FROM jsonb_object_keys(posts_enviados) AS key
                            WHERE key = %s
                    )
                """, (json.dumps(novo_post), username, timestamp))
                conn.commit()

                # 4) Publica no RabbitMQ
                rabbit_conn = pika.BlockingConnection(
                    pika.ConnectionParameters(host="localhost")
                )
                ch = rabbit_conn.channel()
                ch.exchange_declare(exchange="posts", exchange_type="fanout", durable=True)

                post_msg = {
                    "type":     "post",
                    "postId":   post_id,
                    "userId":   username,
                    "content":  content,
                    "timestamp": timestamp,
                }
                ch.basic_publish(
                    exchange="posts",
                    routing_key="",
                    body=json.dumps(post_msg),
                    properties=pika.BasicProperties(delivery_mode=2),
                )
                rabbit_conn.close()

                # 5) Atualiza UI e limpa input
                tk.Label(posts_frame, text=f"{username} ({timestamp}): {content}") \
                .pack(anchor="w")
                new_post_entry.delete(0, tk.END)
                messagebox.showinfo("Sucesso", "Post enviado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar post: {e}")
        finally:
            conn.close()

    tk.Button(new_post_frame, text="Postar", command=submit_post).pack(side=tk.LEFT, padx=5)

def follow_user(username):
    # Criar a janela para seguir outro usuário
    follow_window = tk.Toplevel(root)
    follow_window.title("Seguir Usuário")

    # Título
    tk.Label(follow_window, text="Seguir Usuário", font=("Arial", 16)).pack(pady=10)

    # Obter a lista de usuários do banco de dados
    conn = connect_to_db()
    if not conn:
        messagebox.showerror("Erro", "Erro ao conectar ao banco de dados.")
        return

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT usuario_nome FROM usuario WHERE usuario_nome != %s", (username,))
            users = [row[0] for row in cur.fetchall()]
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar usuários: {e}")
        follow_window.destroy()
        return
    finally:
        conn.close()

    # Verificar se há usuários disponíveis para seguir
    if not users:
        messagebox.showinfo("Informação", "Não há outros usuários disponíveis para seguir.")
        follow_window.destroy()
        return

    # Campo de seleção para o nome do usuário a ser seguido
    tk.Label(follow_window, text="Selecione o usuário que deseja seguir:").pack()
    user_combobox = ttk.Combobox(follow_window, values=users, state="readonly", width=30)
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
                        "SELECT seguindo FROM usuario WHERE usuario_nome = %s", (username,)
                    )
                    result = cur.fetchone()
                    seguindo = json.loads(result[0]) if result and isinstance(result[0], str) else []

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
                        "SELECT seguido_por FROM usuario WHERE usuario_nome = %s", (follow,)
                    )
                    result = cur.fetchone()
                    seguido_por = json.loads(result[0]) if result and isinstance(result[0], str) else []

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
                    rabbit_conn = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
                    ch = rabbit_conn.channel()
                    ch.exchange_declare(exchange="follows", exchange_type="fanout", durable=True)

                    follow_msg = {
                        "type": "follow",
                        "followerId": username,
                        "followedId": follow,
                    }
                    ch.basic_publish(
                        exchange="follows",
                        routing_key="",
                        body=json.dumps(follow_msg),
                        properties=pika.BasicProperties(delivery_mode=2),
                    )
                    rabbit_conn.close()

                    messagebox.showinfo("Sucesso", f"Agora você está seguindo {follow}!")
                    follow_window.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao seguir usuário: {e}")
            finally:
                conn.close()

    # Botão para confirmar o follow
    tk.Button(follow_window, text="Seguir", command=submit_follow).pack(pady=10)

    # Botão para fechar a janela
    tk.Button(follow_window, text="Cancelar", command=follow_window.destroy).pack(pady=5)

def private_messages(username):
    # Função para mensagens privadas (a ser implementada)
    messagebox.showinfo("Mensagens Privadas", "Funcionalidade de mensagens privadas ainda não implementada.")

# Interface gráfica
root = tk.Tk()
root.title("Rede Social")

# Frame para criar conta
frame_create_account = tk.Frame(root)
tk.Label(frame_create_account, text="Criar Conta", font=("Arial", 16)).pack(pady=10)
tk.Label(frame_create_account, text="Usuário:").pack()
entry_username = tk.Entry(frame_create_account)
entry_username.pack()
tk.Label(frame_create_account, text="Senha:").pack()
entry_password = tk.Entry(frame_create_account, show="*")
entry_password.pack()
tk.Label(frame_create_account, text="Confirmar Senha:").pack()
entry_confirm_password = tk.Entry(frame_create_account, show="*")
entry_confirm_password.pack()
tk.Button(frame_create_account, text="Criar Conta", command=create_account).pack(pady=10)
tk.Button(frame_create_account, text="Já tem uma conta? Login", command=switch_to_login).pack()
frame_create_account.pack()

# Frame para login
frame_login = tk.Frame(root)
tk.Label(frame_login, text="Login", font=("Arial", 16)).pack(pady=10)
tk.Label(frame_login, text="Usuário:").pack()
entry_login_username = tk.Entry(frame_login)
entry_login_username.pack()
tk.Label(frame_login, text="Senha:").pack()
entry_login_password = tk.Entry(frame_login, show="*")
entry_login_password.pack()
tk.Button(frame_login, text="Login", command=login).pack(pady=10)
tk.Button(frame_login, text="Criar Conta", command=switch_to_create_account).pack()

root.mainloop()
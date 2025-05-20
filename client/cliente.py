import pika
import json
import uuid
import datetime
import threading

# 1) Ler seu userId e quem quer seguir
user_id = input("Digite seu userId: ").strip()
follow = input("Digite o userId de quem você quer seguir: ").strip()
print(f"\nVocê ({user_id}) vai seguir: {follow}\n")

# 2) Função que trata cada post recebido
def on_post(ch, method, props, body):
    msg = json.loads(body)
    if msg.get("userId") == follow:
        print(f"\n[Notificação] {follow} postou: {msg['content']}\n> ", end="")

# 3) Thread para escutar a exchange 'posts'
def start_listener():
    conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    ch = conn.channel()
    ch.exchange_declare(exchange='posts', exchange_type='fanout', durable=True)
    q = ch.queue_declare('', exclusive=True).method.queue
    ch.queue_bind(exchange='posts', queue=q)
    ch.basic_consume(queue=q, on_message_callback=on_post, auto_ack=True)
    ch.start_consuming()

threading.Thread(target=start_listener, daemon=True).start()

# 4) Conexão para publicar
pub_conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
pub_ch = pub_conn.channel()
pub_ch.exchange_declare(exchange='posts', exchange_type='fanout', durable=True)

print("Digite suas mensagens. Escreva 'sair' para encerrar.\n")

# 5) Loop de postagem
while True:
    content = input("> ").strip()
    if content.lower() == "sair":
        print("Encerrando client.")
        break

    message = {
        "type": "post",
        "postId": str(uuid.uuid4()),
        "userId": user_id,
        "content": content,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }
    pub_ch.basic_publish(
        exchange='posts',
        routing_key='',
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    print(f"[Você] Post enviado: “{content}”")

pub_conn.close()
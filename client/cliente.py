import pika
import json
import uuid
import datetime
import threading

# 1) Ler seu userId e quem quer seguir
user_id = input("Digite seu userId: ").strip()
follow = input("Digite o userId de quem você quer seguir: ").strip()
print(f"\nVocê ({user_id}) vai seguir: {follow}\n")

# 2) Conectar ao RabbitMQ (para posts e follows)
conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
ch = conn.channel()

# Declarar ambas as exchanges
ch.exchange_declare(exchange='follows', exchange_type='fanout', durable=True)
ch.exchange_declare(exchange='posts',   exchange_type='fanout', durable=True)

# 3) Publicar o evento de follow **antes** de tudo
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

# 4) Função que trata cada post recebido
def on_post(ch, method, props, body):
    msg = json.loads(body)
    if msg.get("userId") == follow:
        print(f"\n[Notificação] {follow} postou: {msg['content']}\n> ", end="")

# 5) Thread para escutar a exchange 'posts'
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

# 6) Loop de postagem
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
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }
    ch.basic_publish(
        exchange='posts',
        routing_key='',
        body=json.dumps(post_msg),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    print(f"[Você] Post enviado: “{content}”")

# 7) Fechar conexão de publicação
conn.close()
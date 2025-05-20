import pika

# 1) Conecta ao RabbitMQ na máquina local
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost')
)
channel = connection.channel()

# 2) Garante que a exchange 'posts' existe (tipo fanout)
channel.exchange_declare(
    exchange='posts',
    exchange_type='fanout',
    durable=True
)

# 3) Envia "Hello, World!" para essa exchange
channel.basic_publish(
    exchange='posts',
    routing_key='',
    body='Hello, World!',
    properties=pika.BasicProperties(delivery_mode=2)  # mensagem persistente
)

print("[Cliente Python] Enviado: Hello, World!")
connection.close()

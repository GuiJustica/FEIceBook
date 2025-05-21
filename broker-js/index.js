// broker-js/index.js
const amqp = require('amqplib');

async function main() {
  // 1) Conectar ao RabbitMQ
  const conn = await amqp.connect('amqp://guest:guest@rabbitmq:5672/');
  const ch = await conn.createChannel();

  // 2) Declarar as exchanges
  await ch.assertExchange('follows', 'fanout', { durable: true });
  await ch.assertExchange('posts',   'fanout', { durable: true });
  await ch.assertExchange('notifications', 'direct', { durable: true });

  // 3) Map de seguidores: seguido → Set de seguidores
  const followersMap = new Map();

  // 4) Consumir mensagens de follow
  const { queue: followQueue } = await ch.assertQueue('', { exclusive: true });
  await ch.bindQueue(followQueue, 'follows', '');
  ch.consume(followQueue, msg => {
    const { followerId, followedId } = JSON.parse(msg.content.toString());
    if (!followersMap.has(followedId)) {
      followersMap.set(followedId, new Set());
    }
    followersMap.get(followedId).add(followerId);
    console.log(`${followerId} agora segue ${followedId}`);
  }, { noAck: true });

  // 5) Consumir mensagens de post e reenviar notificações
  const { queue: postQueue } = await ch.assertQueue('', { exclusive: true });
  await ch.bindQueue(postQueue, 'posts', '');
  ch.consume(postQueue, msg => {
    const post = JSON.parse(msg.content.toString());
    const subs = followersMap.get(post.userId) || [];
    for (const follower of subs) {
      // publicar em notifications com routingKey = follower
      ch.publish(
        'notifications',
        follower,
        Buffer.from(JSON.stringify(post)),
        { persistent: true }
      );
      console.log(`Notificação para ${follower}: ${post.userId} postou “${post.content}”`);
    }
  }, { noAck: true });

  console.log('broker-js rodando e aguardando eventos…');
}

main().catch(err => {
  console.error('Erro no broker-js:', err);
  process.exit(1);
});

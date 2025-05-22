// broker-js/index.js
require('dotenv').config();
const amqp = require('amqplib');
const { Pool } = require('pg');

async function loadInitialFollowers(followersMap) {
  // Configura a conexão ao CockroachDB via variáveis de ambiente
  const pool = new Pool({
    host:     process.env.DB_HOST,
    port:     parseInt(process.env.DB_PORT, 10),
    user:     process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME,
    ssl:      { rejectUnauthorized: false }
  });

  try {
    const res = await pool.query(`
      SELECT usuario_nome, seguido_por
        FROM usuario
    `);
    res.rows.forEach(row => {
      const followedId = row.usuario_nome;
      // seguido_por já chega como array do JSONB
      const followers  = Array.isArray(row.seguido_por)
        ? row.seguido_por
        : JSON.parse(row.seguido_por || '[]');
      followersMap.set(followedId, new Set(followers));
    });
    console.log('[broker-js] followersMap inicializado a partir do banco');
  } finally {
    await pool.end();
  }
}

async function main() {
  // 1) Conectar ao RabbitMQ
  const conn = await amqp.connect('amqp://guest:guest@rabbitmq:5672/');
  const ch   = await conn.createChannel();

  // 2) Declarar as exchanges
  await ch.assertExchange('follows',           'fanout', { durable: true });
  await ch.assertExchange('posts',             'fanout', { durable: true });
  await ch.assertExchange('private_messages',  'fanout', { durable: true });
  await ch.assertExchange('notifications',     'direct', { durable: true });

  // 3) Map de seguidores: seguido → Set de seguidores
  const followersMap = new Map();
  // Carrega estado inicial do CockroachDB
  await loadInitialFollowers(followersMap);

  // 4) Consumir mensagens de follow em fila durável e nomeada
  const followQueue = 'broker.followers';
  await ch.assertQueue(followQueue, { durable: true });
  await ch.bindQueue  (followQueue, 'follows', '');
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
    const subs = followersMap.get(post.userId) || new Set();
    for (const follower of subs) {
      ch.publish(
        'notifications',
        follower,
        Buffer.from(JSON.stringify(post)),
        { persistent: true }
      );
      console.log(`Notificação para ${follower}: ${post.userId} postou “${post.content}”`);
    }
  }, { noAck: true });

  // 6) Consumir mensagens privadas e reenviar para o destinatário
  const { queue: pmQueue } = await ch.assertQueue('', { exclusive: true });
  await ch.bindQueue(pmQueue, 'private_messages', '');
  ch.consume(pmQueue, msg => {
    const pm = JSON.parse(msg.content.toString());
    const { sender, recipient, content } = pm;
    ch.publish(
      'notifications',
      recipient,
      Buffer.from(JSON.stringify(pm)),
      { persistent: true }
    );
    console.log(`Mensagem privada de ${sender} para ${recipient}: ${content}`);
  }, { noAck: true });

  console.log('broker-js rodando e aguardando eventos…');
}

main().catch(err => {
  console.error('Erro no broker-js:', err);
  process.exit(1);
});
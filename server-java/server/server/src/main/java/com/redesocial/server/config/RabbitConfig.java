package com.redesocial.server.config;

import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.FanoutExchange;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitConfig {

    // Injeta o serviço de relógio lógico
    @Autowired
    private LogicalClockService logicalClockService;

    @Bean
    public FanoutExchange postsExchange() {
        return new FanoutExchange("posts");
    }

    @Bean
    public Queue postsQueue() {
        return new Queue("posts.queue", true);
    }

    @Bean
    public Binding postsBinding(FanoutExchange postsExchange, Queue postsQueue) {
        return BindingBuilder.bind(postsQueue).to(postsExchange);
    }

    @Bean
    public FanoutExchange followsExchange() {
        return new FanoutExchange("follows");
    }

    @Bean
    public Queue followsQueue() {
        return new Queue("follows.queue", true);
    }

    @Bean
    public Binding followsBinding(FanoutExchange followsExchange, Queue followsQueue) {
        return BindingBuilder.bind(followsQueue).to(followsExchange);
    }

    @Bean
    public FanoutExchange privateMessagesExchange() { // exchange para mensagens privadas
        return new FanoutExchange("private_messages");
    }

    @Bean
    public Queue privateMessagesQueue() { // fila que o servidor vai consumir
        return new Queue("private_messages.queue", true);
    }

    @Bean
    public Binding privateMessagesBinding(FanoutExchange privateMessagesExchange, Queue privateMessagesQueue) { // binding entre exchange e fila
        return BindingBuilder.bind(privateMessagesQueue).to(privateMessagesExchange);
    }

    @Bean // Bean que aplica o relógio lógico antes de cada publicação
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory) {
        RabbitTemplate template = new RabbitTemplate(connectionFactory);
        template.setBeforePublishPostProcessors(message -> {
            int ts = logicalClockService.onSend();
            message.getMessageProperties().setHeader("logicalTimestamp", ts);
            return message;
        });
        return template;
    }
}

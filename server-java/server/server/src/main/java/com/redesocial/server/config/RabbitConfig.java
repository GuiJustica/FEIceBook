package com.redesocial.server.config;

import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.FanoutExchange;
import org.springframework.amqp.core.Queue;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitConfig {

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
}

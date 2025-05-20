package com.redesocial.server.listener;

import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Component
public class PostListener {

    @RabbitListener(queues = "posts.queue")
    public void onPostReceived(String message) {
        System.out.println("[Servidor] Post recebido: " + message);
    }

    @RabbitListener(queues = "follows.queue")
    public void onFollowReceived(String message) {
        System.out.println("[Servidor] Follow recebido: " + message);
    }
}

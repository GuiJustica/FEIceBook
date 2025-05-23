package com.redesocial.server.listener;

import org.springframework.amqp.core.Message;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import com.redesocial.server.config.LogicalClockService;

@Component
public class PostListener {

    @Autowired
    private LogicalClockService logicalClockService;

    @RabbitListener(queues = "posts.queue")
    public void onPostReceived(Message message) {
        Object header = message.getMessageProperties().getHeaders().get("logicalTimestamp"); // le o timestamp lógico do header
        int receivedTs = (header instanceof Integer) ? (Integer) header : 0;
        int localTs = logicalClockService.onReceive(receivedTs); // atualize o relógio lógico local
        String payload = new String(message.getBody()); // converta o body em String
        System.out.printf("[Servidor] Post recebido: '%s' (TS remoto=%d → clock local=%d)%n", payload, receivedTs, localTs); // log de conferência
    }

    @RabbitListener(queues = "follows.queue")
    public void onFollowReceived(Message message) {
        Object header = message.getMessageProperties().getHeaders().get("logicalTimestamp");
        int receivedTs = (header instanceof Integer) ? (Integer) header : 0;
        int localTs = logicalClockService.onReceive(receivedTs);
        String payload = new String(message.getBody());
        System.out.printf("[Servidor] Follow recebido: '%s' (TS remoto=%d → clock local=%d)%n", payload, receivedTs, localTs);
    }

    @RabbitListener(queues = "private_messages.queue")
    public void onPrivateMessageReceived(Message message) {
        Object header = message.getMessageProperties().getHeaders().get("logicalTimestamp");
        int receivedTs = (header instanceof Integer) ? (Integer) header : 0;
        int localTs = logicalClockService.onReceive(receivedTs);
        String payload = new String(message.getBody());
        System.out.printf("[Servidor] Mensagem privada recebida: '%s' (TS remoto=%d → clock local=%d)%n", payload, receivedTs, localTs);
    }
    
}

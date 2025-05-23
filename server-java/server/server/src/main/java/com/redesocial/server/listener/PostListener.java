package com.redesocial.server.listener;

import org.springframework.amqp.core.Message;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import com.redesocial.server.config.LogicalClockService;
import com.redesocial.server.config.PhysicalTimestampService;
import java.util.Map;

@Component
public class PostListener {

    @Autowired
    private LogicalClockService logicalClockService;

    @Autowired
    private PhysicalTimestampService physicalTimestampService;

    @RabbitListener(queues = "posts.queue")
    public void onPostReceived(Message message) {
        // injeta drift físico em 30% dos casos
        physicalTimestampService.applyRandomDrift();

        // lê timestamp lógico remoto e atualiza local
        Map<String,Object> headers = message.getMessageProperties().getHeaders();
        Object header = headers.get("logicalTimestamp");
        int receivedTs = (header instanceof Integer) ? (Integer) header : 0;
        int localTs    = logicalClockService.onReceive(receivedTs);

        // processa payload
        String payload = new String(message.getBody());
        System.out.printf("[Servidor] Post recebido: '%s' (TS remoto=%d → clock local=%d)%n",
                          payload, receivedTs, localTs);
    }

    @RabbitListener(queues = "follows.queue")
    public void onFollowReceived(Message message) {
        physicalTimestampService.applyRandomDrift();

        Map<String,Object> headers = message.getMessageProperties().getHeaders();
        Object header = headers.get("logicalTimestamp");
        int receivedTs = (header instanceof Integer) ? (Integer) header : 0;
        int localTs    = logicalClockService.onReceive(receivedTs);

        String payload = new String(message.getBody());
        System.out.printf("[Servidor] Follow recebido: '%s' (TS remoto=%d → clock local=%d)%n",
                          payload, receivedTs, localTs);
    }

    @RabbitListener(queues = "private_messages.queue")
    public void onPrivateMessageReceived(Message message) {
        physicalTimestampService.applyRandomDrift();

        Map<String,Object> headers = message.getMessageProperties().getHeaders();
        Object header = headers.get("logicalTimestamp");
        int receivedTs = (header instanceof Integer) ? (Integer) header : 0;
        int localTs    = logicalClockService.onReceive(receivedTs);

        String payload = new String(message.getBody());
        System.out.printf("[Servidor] Mensagem privada recebida: '%s' (TS remoto=%d → clock local=%d)%n",
                          payload, receivedTs, localTs);
    }
}
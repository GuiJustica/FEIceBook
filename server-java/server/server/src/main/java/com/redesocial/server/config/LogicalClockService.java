package com.redesocial.server.config;

import org.springframework.stereotype.Component;
import java.util.concurrent.atomic.AtomicInteger;


@Component
public class LogicalClockService {
    private final AtomicInteger clock = new AtomicInteger(0);

    /** Chame antes de enviar qualquer mensagem: */
    public synchronized int onSend() {
        return clock.incrementAndGet();
    }

    /** Chame ao receber uma mensagem com timestamp ‘receivedTs’: */
    public synchronized int onReceive(int receivedTs) {
        clock.set(Math.max(clock.get(), receivedTs));
        return clock.incrementAndGet();
    }

    /** Para inspecionar o valor atual (opcional): */
    public int getCurrent() {
        return clock.get();
    }
}


package com.redesocial.server.config;

import org.springframework.stereotype.Component;
import java.time.Instant;
import java.util.Random;

@Component
public class PhysicalTimestampService {
    private final Random rnd = new Random();
    private long offsetMs = 0; // campo que acumula o drift aplicado (ms)

    // Retorna o timestamp atual, aplicando em 30% dos casos um drift de ±1 min que acumula em offsetMs 
    public Instant getTimestamp() {
        if (rnd.nextDouble() < 0.3) {
            long delta = (rnd.nextBoolean() ? 1 : -1) * 60_000L; // atrasa 1 minuto
            offsetMs += delta;
            System.out.println("Simulando erro físico de " + (delta/1000) + " s (offset atual = " + (offsetMs/1000) + " s)");
        }
        return Instant.ofEpochMilli(System.currentTimeMillis() + offsetMs);
    }

    // zera o drift acumulado (chamado pelo BerkeleySyncService)
    public void resetOffset() {
        offsetMs = 0;
    }
}

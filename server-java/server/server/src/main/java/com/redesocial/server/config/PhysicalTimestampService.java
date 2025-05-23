package com.redesocial.server.config;

import org.springframework.stereotype.Component;
import java.time.Instant;
import java.util.Random;

@Component
public class PhysicalTimestampService {
    private final Random rnd = new Random();
    private long offsetMs = 0;

    /** Retorna o timestamp corrente **sem** aplicar novo drift */
    public Instant getTimestamp() {
        return Instant.ofEpochMilli(System.currentTimeMillis() + offsetMs);
    }

    /** Chame **só** quando quiser injetar um erro físico de 30% ±1min */
    public void applyRandomDrift() {
        if (rnd.nextDouble() < 0.3) {
            long delta = (rnd.nextBoolean() ? 60_000L : -60_000L);
            offsetMs += delta;
            System.out.printf("[Drift] aplicando %d s (offset atual = %d s)%n",
                              delta/1000, offsetMs/1000);
        }
    }

    /** Zera o erro acumulado — use após Berkeley sync */
    public void resetOffset() {
        offsetMs = 0;
    }
}

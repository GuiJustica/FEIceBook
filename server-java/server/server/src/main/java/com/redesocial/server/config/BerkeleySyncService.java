package com.redesocial.server.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import java.time.Instant;

@Service
public class BerkeleySyncService {

    @Autowired
    private PhysicalTimestampService physicalTimestampService;

    /** roda a cada 10 segundos */
    @Scheduled(fixedRate = 10_000)
    public void sincroniza() {
        System.out.println("Iniciando sincronização de Berkeley");

        // 1) Leia o timestamp atual (já com drift aplicado pelo PhysicalTimestampService)
        Instant servidorTs = physicalTimestampService.getTimestamp();

        // 2) Calcule o offset em ms em relação ao tempo do sistema
        long offsetMs = servidorTs.toEpochMilli() - System.currentTimeMillis();
        System.out.println("Offset detectado = " + offsetMs + " ms");

        // 3) Corrija o relógio físico (zerar offset)
        physicalTimestampService.resetOffset();
        System.out.println("Relógio físico corrigido (offset zerado)");
    }
}

package com.redesocial.server.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import java.time.Instant;

@Service
public class BerkeleySyncService {

    @Autowired
    private PhysicalTimestampService physicalTimestampService;

    /**
     * Roda a cada 10 segundos, sem aplicar drift aqui
     */
    @Scheduled(fixedRate = 10_000)
    public void sincroniza() {
        System.out.println("[Berkeley] Iniciando sincronização de relógios");

        // 1) Leia o timestamp sem novo drift
        Instant servidorTs = physicalTimestampService.getTimestamp();

        // 2) Calcule offset em relação ao tempo do sistema
        long offsetMs = servidorTs.toEpochMilli() - System.currentTimeMillis();
        System.out.println("[Berkeley] Timestamp do servidor = " + servidorTs);
        System.out.println("[Berkeley] Offset detectado = " + offsetMs + " ms");

        // 3) Zere o drift acumulado
        physicalTimestampService.resetOffset();
        System.out.println("[Berkeley] offset zerado, sincronização concluída\n");
    }
}
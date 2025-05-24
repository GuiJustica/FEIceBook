package com.redesocial.server.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.time.ZoneId;
import java.time.ZonedDateTime;

@Service
public class BerkeleySyncService {

    @Autowired
    private PhysicalTimestampService physicalTimestampService;

    private static final ZoneId SAO_PAULO = ZoneId.of("America/Sao_Paulo");

    /**
     * Roda a cada 10 segundos, sem aplicar drift aqui
     */
    @Scheduled(fixedRate = 10_000)
    public void sincroniza() {
        System.out.println("[Berkeley] Iniciando sincronização de relógios");

        // 1) Leia o timestamp sem novo drift
        Instant servidorTs = physicalTimestampService.getTimestamp();

        // 2) Converta para horário de São Paulo (-03:00)
        ZonedDateTime spTs = servidorTs.atZone(SAO_PAULO);

        // 3) Exiba o timestamp no fuso de São Paulo
        System.out.println("[Berkeley] Timestamp do servidor (São Paulo) = " + spTs);

        // 4) Calcule offset em relação ao tempo do sistema
        long offsetMs = servidorTs.toEpochMilli() - System.currentTimeMillis();
        System.out.println("[Berkeley] Offset detectado = " + offsetMs + " ms");

        // 5) Zere o drift acumulado
        physicalTimestampService.resetOffset();
        System.out.println("[Berkeley] offset zerado, sincronização concluída\n");
    }
}

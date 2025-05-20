import java.io.*;

public class Servidor {
    public static void main(String[] args) {
        try {
            // 1. Executar script Python
            System.out.println("Executando Python:");
            ProcessBuilder pb1 = new ProcessBuilder("python", "teste.py");
            Process p1 = pb1.start();
            BufferedReader br1 = new BufferedReader(new InputStreamReader(p1.getInputStream()));
            br1.lines().forEach(System.out::println);


            // 2. Compilar C++
            System.out.println("\nCompilando C++:");
            String execName = "teste2.exe";
            ProcessBuilder pb2 = new ProcessBuilder("g++", "teste.cpp", "-o", execName);
            Process p2 = pb2.start();
            p2.waitFor(); // Espera a compilação

            // 3. Executar C++
            System.out.println("\nExecutando C++:");
            ProcessBuilder pb3 = new ProcessBuilder(execName);
            Process p3 = pb3.start();
            BufferedReader br3 = new BufferedReader(new InputStreamReader(p3.getInputStream()));
            br3.lines().forEach(System.out::println);

            // 4. Mensagem final Java
            System.out.println("\nJava: Hello World!");

        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }
}
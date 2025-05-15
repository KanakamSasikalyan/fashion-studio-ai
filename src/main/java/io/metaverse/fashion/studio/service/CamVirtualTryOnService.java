package io.metaverse.fashion.studio.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.nio.file.*;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@Service
public class CamVirtualTryOnService {

    @Value("${python.camscript.path}")
    private String pythonScriptPath;

    @Value("${upload.directory}")
    private String uploadDirectory;

    private Process pythonProcess;
    private final ExecutorService outputReaderExecutor = Executors.newSingleThreadExecutor();
    private final ObjectMapper objectMapper = new ObjectMapper();

    public String saveClothImage(MultipartFile file) throws IOException {
        Path uploadPath = Paths.get(uploadDirectory);
        if (!Files.exists(uploadPath)) {
            Files.createDirectories(uploadPath);
        }

        String fileName = System.currentTimeMillis() + "_" + file.getOriginalFilename();
        Path filePath = uploadPath.resolve(fileName);
        Files.copy(file.getInputStream(), filePath, StandardCopyOption.REPLACE_EXISTING);

        return filePath.toString();
    }

    public void startVirtualTryOn(String clothImagePath, SimpMessagingTemplate messagingTemplate)
            throws IOException, InterruptedException {
        stopVirtualTryOn();

        ProcessBuilder processBuilder = new ProcessBuilder(
                "python",
                pythonScriptPath,
                "--cloth-image",
                clothImagePath
        );

        processBuilder.redirectErrorStream(true);
        pythonProcess = processBuilder.start();

        streamProcessOutput(pythonProcess, messagingTemplate);
    }

    private void streamProcessOutput(Process process, SimpMessagingTemplate messagingTemplate) {
        outputReaderExecutor.execute(() -> {
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    try {
                        JsonNode jsonNode = objectMapper.readTree(line);
                        if (jsonNode.has("type") && "frame".equals(jsonNode.get("type").asText())) {
                            String frameData = jsonNode.get("data").asText();
                            messagingTemplate.convertAndSend("/topic/video-feed",
                                    Map.of("frame", frameData));
                        }
                    } catch (Exception e) {
                        System.err.println("Error processing Python output: " + e.getMessage());
                    }
                }
            } catch (IOException e) {
                System.err.println("Error reading Python output: " + e.getMessage());
            } finally {
                System.out.println("Python process output stream closed");
            }
        });
    }

    public void stopVirtualTryOn() {
        if (pythonProcess != null && pythonProcess.isAlive()) {
            pythonProcess.destroy();
            try {
                pythonProcess.waitFor();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
}
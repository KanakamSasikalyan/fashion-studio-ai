package io.metaverse.fashion.studio.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.nio.file.*;
import java.util.Base64;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

@Service
public class CamVirtualTryOnService {

    @Value("${python.camscript.path}")
    private String pythonScriptPath;

    @Value("${upload.directory}")
    private String uploadDirectory;

    private Process pythonProcess;
    private Future<?> outputReaderFuture;
    private final ExecutorService executorService = Executors.newCachedThreadPool(); // Use a pool for managing tasks
    private final ObjectMapper objectMapper = new ObjectMapper();

    private String currentClothImagePath; // Store the path of the uploaded cloth

    public String getCurrentClothImagePath() {
        return currentClothImagePath;
    }

    public void setCurrentClothImagePath(String currentClothImagePath) {
        this.currentClothImagePath = currentClothImagePath;
    }

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

    public void processAndStreamFrame(String base64Frame, String clothImagePath, SimpMessagingTemplate messagingTemplate)
            throws IOException, InterruptedException {

        // If Python process is not running, start it
        if (pythonProcess == null || !pythonProcess.isAlive()) {
            startPythonProcess(clothImagePath, messagingTemplate);
        }

        // Write the base64 frame to Python's stdin
        try (BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(pythonProcess.getOutputStream()))) {
            // Send as a JSON object to match Python's expected input
            writer.write(objectMapper.writeValueAsString(Map.of("type", "frame_input", "data", base64Frame)));
            writer.newLine();
            writer.flush();
        } catch (IOException e) {
            System.err.println("Error writing frame to Python stdin: " + e.getMessage());
            messagingTemplate.convertAndSend("/topic/errors", Map.of("message", "Error communicating with virtual try-on engine."));
            stopVirtualTryOn(); // Stop the process on write error
        }
    }

    private void startPythonProcess(String clothImagePath, SimpMessagingTemplate messagingTemplate) throws IOException, InterruptedException {
        stopVirtualTryOn(); // Ensure any old process is stopped

        ProcessBuilder processBuilder = new ProcessBuilder(
                "python",
                pythonScriptPath,
                "--cloth-image",
                clothImagePath
        );

        processBuilder.redirectErrorStream(true); // Redirects stderr to stdout
        pythonProcess = processBuilder.start();

        // Start reading output in a separate thread
        outputReaderFuture = executorService.submit(() -> streamProcessOutput(pythonProcess, messagingTemplate));
    }

    private void streamProcessOutput(Process process, SimpMessagingTemplate messagingTemplate) {
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.trim().startsWith("{") && line.trim().endsWith("}")) {
                    try {
                        JsonNode jsonNode = objectMapper.readTree(line);
                        if (jsonNode.has("type")) {
                            String type = jsonNode.get("type").asText();
                            if ("frame".equals(type) && jsonNode.has("data")) {
                                String frameData = jsonNode.get("data").asText();
                                messagingTemplate.convertAndSend("/topic/video-feed",
                                        Map.of("frame", frameData));
                            } else if ("error".equals(type) && jsonNode.has("message")) {
                                String errorMessage = jsonNode.get("message").asText();
                                System.err.println("Python error: " + errorMessage);
                                messagingTemplate.convertAndSend("/topic/errors", Map.of("message", "Python error: " + errorMessage));
                                stopVirtualTryOn(); // Stop on Python error
                            } else if ("status".equals(type)) {
                                System.out.println("Python status: " + jsonNode.get("message").asText());
                            } else {
                                System.out.println("Received unknown JSON from Python: " + line);
                            }
                        }
                    } catch (Exception e) {
                        System.err.println("Error parsing JSON from Python output: " + line + " - " + e.getMessage());
                        messagingTemplate.convertAndSend("/topic/errors", Map.of("message", "Backend parsing error."));
                    }
                } else {
                    System.err.println("Non-JSON Python output: " + line);
                }
            }
        } catch (IOException e) {
            System.err.println("Error reading Python output stream: " + e.getMessage());
            messagingTemplate.convertAndSend("/topic/errors", Map.of("message", "Backend stream read error."));
        } finally {
            System.out.println("Python process output stream closed.");
            if (process.isAlive()) {
                process.destroy(); // Ensure process is terminated if stream closes unexpectedly
            }
        }
    }

    public void stopVirtualTryOn() {
        if (outputReaderFuture != null) {
            outputReaderFuture.cancel(true); // Interrupt the output reader thread
            outputReaderFuture = null;
        }

        if (pythonProcess != null) {
            if (pythonProcess.isAlive()) {
                System.out.println("Attempting to stop Python process...");
                try {
                    // Send a signal to Python script if it listens for it, or just destroy
                    try (BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(pythonProcess.getOutputStream()))) {
                        writer.write(objectMapper.writeValueAsString(Map.of("type", "command", "action", "stop")));
                        writer.newLine();
                        writer.flush();
                    } catch (IOException e) {
                        System.err.println("Could not send stop command to Python process (might be already closed or broken pipe): " + e.getMessage());
                    }

                    boolean terminated = pythonProcess.waitFor(5, java.util.concurrent.TimeUnit.SECONDS);
                    if (!terminated) {
                        pythonProcess.destroyForcibly();
                        System.out.println("Python process forcibly destroyed.");
                    } else {
                        System.out.println("Python process terminated gracefully.");
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    System.err.println("Interrupted while waiting for Python process to stop: " + e.getMessage());
                    pythonProcess.destroyForcibly();
                }
            }
            pythonProcess = null; // Clear the reference
        }
    }
}

/*package io.metaverse.fashion.studio.service;

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

        processBuilder.redirectErrorStream(true); // Redirects stderr to stdout
        pythonProcess = processBuilder.start();

        streamProcessOutput(pythonProcess, messagingTemplate);
    }

    private void streamProcessOutput(Process process, SimpMessagingTemplate messagingTemplate) {
        outputReaderExecutor.execute(() -> {
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    // Attempt to parse only if the line looks like a JSON object
                    // This is a simple check; a more robust check might involve
                    // trying to parse and catching JsonParseException
                    if (line.trim().startsWith("{") && line.trim().endsWith("}")) {
                        try {
                            JsonNode jsonNode = objectMapper.readTree(line);
                            if (jsonNode.has("type") && "frame".equals(jsonNode.get("type").asText())) {
                                String frameData = jsonNode.get("data").asText();
                                messagingTemplate.convertAndSend("/topic/video-feed",
                                        Map.of("frame", frameData));
                            } else {
                                // Log other JSON types if necessary
                                System.out.println("Received non-frame JSON: " + line);
                            }
                        } catch (Exception e) {
                            // This catch block will now primarily catch parsing errors
                            // for lines that *look* like JSON but are malformed.
                            System.err.println("Error parsing JSON from Python output: " + line + " - " + e.getMessage());
                        }
                    } else {
                        // Log non-JSON output, which might be warnings or errors from Python/OpenCV
                        System.err.println("Non-JSON Python output: " + line);
                    }
                }
            } catch (IOException e) {
                System.err.println("Error reading Python output stream: " + e.getMessage());
            } finally {
                System.out.println("Python process output stream closed");
            }
        });
    }

    public void stopVirtualTryOn() {
        if (pythonProcess != null && pythonProcess.isAlive()) {
            pythonProcess.destroy();
            try {
                // Give some time for the process to terminate
                boolean terminated = pythonProcess.waitFor(5, java.util.concurrent.TimeUnit.SECONDS);
                if (!terminated) {
                    pythonProcess.destroyForcibly(); // Forcefully destroy if not terminated
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                System.err.println("Interrupted while waiting for Python process to stop: " + e.getMessage());
            }
        }
    }
}*/
package io.metaverse.fashion.studio.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.concurrent.Executors;

@Service
public class CamVirtualTryOnService {
    private Process pythonProcess;
    @Value("${python.camvirtualtryon.script}")
    private String pythonScriptPath;
    private String pythonExecutable = "python";
    private Path currentClothImagePath;

    public void startPythonProcess(MultipartFile clothImage, int port) throws IOException {
        // Add logging to confirm Python process execution
        System.out.println("Starting Python process for virtual try-on...");

        if (isProcessRunning()) {
            System.out.println("Python process is already running.");
            throw new IllegalStateException("Python process is already running");
        }

        // Save the uploaded image to a temporary file
        currentClothImagePath = Files.createTempFile("tryon-cloth-", ".png");
        try (InputStream inputStream = clothImage.getInputStream()) {
            Files.copy(inputStream, currentClothImagePath, StandardCopyOption.REPLACE_EXISTING);
        }

        // Build the process command
        ProcessBuilder processBuilder = new ProcessBuilder(
                pythonExecutable,
                pythonScriptPath,
                "--cloth", currentClothImagePath.toString(),
                "--port", String.valueOf(port)
        );

        // Log the command being executed
        System.out.println("Executing command: " + String.join(" ", processBuilder.command()));

        // Set up environment and redirects
        processBuilder.redirectErrorStream(true);

        // Start the process
        pythonProcess = processBuilder.start();

        // Log process output in a separate thread
        Executors.newSingleThreadExecutor().submit(() -> {
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(pythonProcess.getInputStream()))) {

                String line;
                while ((line = reader.readLine()) != null) {
                    System.out.println("[Python Process] " + line);
                }
            } catch (IOException e) {
                System.err.println("Error reading Python process output: " + e.getMessage());
            } finally {
                cleanupTempFile();
            }
        });

        // Add shutdown hook
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            stopPythonProcess();
            cleanupTempFile();
        }));
    }

    public void stopPythonProcess() {
        if (pythonProcess != null && pythonProcess.isAlive()) {
            pythonProcess.destroy();
            try {
                if (!pythonProcess.waitFor(3, java.util.concurrent.TimeUnit.SECONDS)) {
                    pythonProcess.destroyForcibly();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                pythonProcess.destroyForcibly();
            }
        }
        pythonProcess = null;
        cleanupTempFile();
    }

    public boolean isProcessRunning() {
        return pythonProcess != null && pythonProcess.isAlive();
    }

    private void cleanupTempFile() {
        try {
            if (currentClothImagePath != null && Files.exists(currentClothImagePath)) {
                Files.deleteIfExists(currentClothImagePath);
            }
        } catch (IOException e) {
            System.err.println("Failed to delete temporary cloth image: " + e.getMessage());
        }
    }

    // Configuration setters
    public void setPythonScriptPath(String path) {
        this.pythonScriptPath = path;
    }

    public void setPythonExecutable(String executable) {
        this.pythonExecutable = executable;
    }

    public String saveClothImage(MultipartFile clothImage) throws IOException {
        Path tempFile = Files.createTempFile("cloth-image-", ".png");
        try (InputStream inputStream = clothImage.getInputStream()) {
            Files.copy(inputStream, tempFile, StandardCopyOption.REPLACE_EXISTING);
        }
        return tempFile.toAbsolutePath().toString();
    }

    public void startVirtualTryOn(String clothImagePath, SimpMessagingTemplate messagingTemplate) {
        // Logic to start the virtual try-on process using the cloth image
        System.out.println("Starting virtual try-on with image: " + clothImagePath);
        // Add WebSocket or messaging logic here if needed
    }

    public void stopVirtualTryOn() {
        // Logic to stop the virtual try-on process
        System.out.println("Stopping virtual try-on process.");
    }
}
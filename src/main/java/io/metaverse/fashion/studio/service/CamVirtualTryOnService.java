//package io.metaverse.fashion.studio.service;
//
//import com.fasterxml.jackson.databind.JsonNode;
//import com.fasterxml.jackson.databind.ObjectMapper;
//import org.springframework.beans.factory.annotation.Value;
//import org.springframework.messaging.simp.SimpMessagingTemplate;
//import org.springframework.stereotype.Service;
//import org.springframework.web.multipart.MultipartFile;
//
//import java.io.*;
//import java.nio.file.*;
//import java.util.Map;
//import java.util.concurrent.*;
//
//@Service
//public class CamVirtualTryOnService {
//
//    @Value("${python.camscript.path}")
//    private String pythonScriptPath;
//
//    @Value("${upload.directory}")
//    private String uploadDirectory;
//
//    private Process pythonProcess;
//    private Future<?> outputReaderFuture;
//    private final ExecutorService executorService = Executors.newCachedThreadPool();
//    private final ObjectMapper objectMapper = new ObjectMapper();
//    private final BlockingQueue<String> frameQueue = new LinkedBlockingQueue<>(5); // Limit queue size
//
//    private String currentClothImagePath;
//
//    public String getCurrentClothImagePath() {
//        return currentClothImagePath;
//    }
//
//    public void setCurrentClothImagePath(String currentClothImagePath) {
//        this.currentClothImagePath = currentClothImagePath;
//    }
//
//    public String saveClothImage(MultipartFile file) throws IOException {
//        Path uploadPath = Paths.get(uploadDirectory);
//        if (!Files.exists(uploadPath)) {
//            Files.createDirectories(uploadPath);
//        }
//
//        String fileName = System.currentTimeMillis() + "_" + file.getOriginalFilename();
//        Path filePath = uploadPath.resolve(fileName);
//        Files.copy(file.getInputStream(), filePath, StandardCopyOption.REPLACE_EXISTING);
//
//        return filePath.toString();
//    }
//
//    public void processFrameAsync(String base64Frame, String clothImagePath,
//                                  SimpMessagingTemplate messagingTemplate) {
//        // Non-blocking add to queue
//        if (!frameQueue.offer(base64Frame)) {
//            System.out.println("Frame dropped - processing too slow");
//            return;
//        }
//
//        executorService.execute(() -> {
//            try {
//                processFrame(frameQueue.take(), clothImagePath, messagingTemplate);
//            } catch (Exception e) {
//                messagingTemplate.convertAndSend("/topic/errors",
//                        Map.of("message", "Frame processing error: " + e.getMessage()));
//            }
//        });
//    }
//
//    private void processFrame(String base64Frame, String clothImagePath,
//                              SimpMessagingTemplate messagingTemplate)
//            throws IOException, InterruptedException {
//
//        if (pythonProcess == null || !pythonProcess.isAlive()) {
//            startPythonProcess(clothImagePath, messagingTemplate);
//            // Give Python process time to initialize
//            Thread.sleep(500);
//        }
//
//        try (BufferedWriter writer = new BufferedWriter(
//                new OutputStreamWriter(pythonProcess.getOutputStream()))) {
//            writer.write(objectMapper.writeValueAsString(
//                    Map.of("type", "frame_input", "data", base64Frame)));
//            writer.newLine();
//            writer.flush();
//        } catch (IOException e) {
//            System.err.println("Error writing frame to Python: " + e.getMessage());
//            stopVirtualTryOn();
//            throw e;
//        }
//    }
//
//    private void startPythonProcess(String clothImagePath,
//                                    SimpMessagingTemplate messagingTemplate)
//            throws IOException, InterruptedException {
//
//        stopVirtualTryOn(); // Clean up any existing process
//
//        ProcessBuilder processBuilder = new ProcessBuilder(
//                "python3",
//                pythonScriptPath,
//                "--cloth-image",
//                clothImagePath
//        );
//
//        processBuilder.redirectErrorStream(true);
//        pythonProcess = processBuilder.start();
//
//        outputReaderFuture = executorService.submit(() ->
//                streamProcessOutput(pythonProcess, messagingTemplate));
//    }
//
//    private void streamProcessOutput(Process process, SimpMessagingTemplate messagingTemplate) {
//        try (BufferedReader reader = new BufferedReader(
//                new InputStreamReader(process.getInputStream()))) {
//
//            String line;
//            while ((line = reader.readLine()) != null && !Thread.currentThread().isInterrupted()) {
//                if (line.trim().startsWith("{") && line.trim().endsWith("}")) {
//                    try {
//                        JsonNode jsonNode = objectMapper.readTree(line);
//                        String type = jsonNode.path("type").asText();
//
//                        switch (type) {
//                            case "frame":
//                                String frameData = jsonNode.path("data").asText();
//                                messagingTemplate.convertAndSend("/topic/video-feed",
//                                        Map.of("frame", frameData));
//                                break;
//                            case "error":
//                                String errorMessage = jsonNode.path("message").asText();
//                                messagingTemplate.convertAndSend("/topic/errors",
//                                        Map.of("message", "Python error: " + errorMessage));
//                                stopVirtualTryOn();
//                                break;
//                            case "status":
//                                System.out.println("Python status: " + jsonNode.path("message").asText());
//                                break;
//                            default:
//                                System.out.println("Unknown message type: " + type);
//                        }
//                    } catch (Exception e) {
//                        System.err.println("Error parsing Python output: " + e.getMessage());
//                    }
//                }
//            }
//        } catch (IOException e) {
//            System.err.println("Error reading Python output: " + e.getMessage());
//        } finally {
//            System.out.println("Python process output stream closed");
//        }
//    }
//
//    public void stopVirtualTryOn() {
//        if (outputReaderFuture != null) {
//            outputReaderFuture.cancel(true);
//            outputReaderFuture = null;
//        }
//
//        if (pythonProcess != null) {
//            if (pythonProcess.isAlive()) {
//                try {
//                    // Send graceful shutdown command
//                    try (BufferedWriter writer = new BufferedWriter(
//                            new OutputStreamWriter(pythonProcess.getOutputStream()))) {
//                        writer.write(objectMapper.writeValueAsString(
//                                Map.of("type", "command", "action", "stop")));
//                        writer.newLine();
//                        writer.flush();
//                    } catch (IOException e) {
//                        System.err.println("Error sending stop command: " + e.getMessage());
//                    }
//
//                    // Wait for process to terminate
//                    if (!pythonProcess.waitFor(3, TimeUnit.SECONDS)) {
//                        pythonProcess.destroyForcibly();
//                    }
//                } catch (Exception e) {
//                    pythonProcess.destroyForcibly();
//                }
//            }
//            pythonProcess = null;
//        }
//
//        frameQueue.clear();
//    }
//}
//
///*package io.metaverse.fashion.studio.service;
//
//import com.fasterxml.jackson.databind.JsonNode;
//import com.fasterxml.jackson.databind.ObjectMapper;
//import org.springframework.beans.factory.annotation.Value;
//import org.springframework.messaging.simp.SimpMessagingTemplate;
//import org.springframework.stereotype.Service;
//import org.springframework.web.multipart.MultipartFile;
//
//import java.io.*;
//import java.nio.file.*;
//import java.util.Map;
//import java.util.concurrent.ExecutorService;
//import java.util.concurrent.Executors;
//
//@Service
//public class CamVirtualTryOnService {
//
//    @Value("${python.camscript.path}")
//    private String pythonScriptPath;
//
//    @Value("${upload.directory}")
//    private String uploadDirectory;
//
//    private Process pythonProcess;
//    private final ExecutorService outputReaderExecutor = Executors.newSingleThreadExecutor();
//    private final ObjectMapper objectMapper = new ObjectMapper();
//
//    public String saveClothImage(MultipartFile file) throws IOException {
//        Path uploadPath = Paths.get(uploadDirectory);
//        if (!Files.exists(uploadPath)) {
//            Files.createDirectories(uploadPath);
//        }
//
//        String fileName = System.currentTimeMillis() + "_" + file.getOriginalFilename();
//        Path filePath = uploadPath.resolve(fileName);
//        Files.copy(file.getInputStream(), filePath, StandardCopyOption.REPLACE_EXISTING);
//
//        return filePath.toString();
//    }
//
//    public void startVirtualTryOn(String clothImagePath, SimpMessagingTemplate messagingTemplate)
//            throws IOException, InterruptedException {
//        stopVirtualTryOn();
//
//        ProcessBuilder processBuilder = new ProcessBuilder(
//                "python",
//                pythonScriptPath,
//                "--cloth-image",
//                clothImagePath
//        );
//
//        processBuilder.redirectErrorStream(true); // Redirects stderr to stdout
//        pythonProcess = processBuilder.start();
//
//        streamProcessOutput(pythonProcess, messagingTemplate);
//    }
//
//    private void streamProcessOutput(Process process, SimpMessagingTemplate messagingTemplate) {
//        outputReaderExecutor.execute(() -> {
//            try (BufferedReader reader = new BufferedReader(
//                    new InputStreamReader(process.getInputStream()))) {
//                String line;
//                while ((line = reader.readLine()) != null) {
//                    // Attempt to parse only if the line looks like a JSON object
//                    // This is a simple check; a more robust check might involve
//                    // trying to parse and catching JsonParseException
//                    if (line.trim().startsWith("{") && line.trim().endsWith("}")) {
//                        try {
//                            JsonNode jsonNode = objectMapper.readTree(line);
//                            if (jsonNode.has("type") && "frame".equals(jsonNode.get("type").asText())) {
//                                String frameData = jsonNode.get("data").asText();
//                                messagingTemplate.convertAndSend("/topic/video-feed",
//                                        Map.of("frame", frameData));
//                            } else {
//                                // Log other JSON types if necessary
//                                System.out.println("Received non-frame JSON: " + line);
//                            }
//                        } catch (Exception e) {
//                            // This catch block will now primarily catch parsing errors
//                            // for lines that *look* like JSON but are malformed.
//                            System.err.println("Error parsing JSON from Python output: " + line + " - " + e.getMessage());
//                        }
//                    } else {
//                        // Log non-JSON output, which might be warnings or errors from Python/OpenCV
//                        System.err.println("Non-JSON Python output: " + line);
//                    }
//                }
//            } catch (IOException e) {
//                System.err.println("Error reading Python output stream: " + e.getMessage());
//            } finally {
//                System.out.println("Python process output stream closed");
//            }
//        });
//    }
//
//    public void stopVirtualTryOn() {
//        if (pythonProcess != null && pythonProcess.isAlive()) {
//            pythonProcess.destroy();
//            try {
//                // Give some time for the process to terminate
//                boolean terminated = pythonProcess.waitFor(5, java.util.concurrent.TimeUnit.SECONDS);
//                if (!terminated) {
//                    pythonProcess.destroyForcibly(); // Forcefully destroy if not terminated
//                }
//            } catch (InterruptedException e) {
//                Thread.currentThread().interrupt();
//                System.err.println("Interrupted while waiting for Python process to stop: " + e.getMessage());
//            }
//        }
//    }
//}*/
// VirtualTryOnService.java
package io.metaverse.fashion.studio.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

@Service
public class VirtualTryOnService {

    private static final Logger logger = LoggerFactory.getLogger(VirtualTryOnService.class);

    @Value("${python.vtonscript.path}")
    private String pythonScriptPath;

    @Value("${ai.vtonoutput.dir}")
    private String outputDir;

    public String processImages(MultipartFile userImage, MultipartFile clothImage) throws IOException, InterruptedException {
        logger.info("Starting processImages method");

        String imageUrl = null;

        // Create output directory if it doesn't exist
        Path outputPath = getOutputPath();
        if (!Files.exists(outputPath)) {
            Files.createDirectories(outputPath);
        }

        // Save uploaded files temporarily
        String userImagePath = saveFile(userImage, "user");
        String clothImagePath = saveFile(clothImage, "cloth");

        logger.info("User image saved at: {}", userImagePath);
        logger.info("Cloth image saved at: {}", clothImagePath);

        // Run the Python script
        ProcessBuilder pb = new ProcessBuilder(
                "python",
                pythonScriptPath,
                userImagePath,
                clothImagePath,
                outputDir
        );

        pb.redirectErrorStream(true);
        Process process = pb.start();

        // Capture Python script output
        StringBuilder output = new StringBuilder();
        try (var reader = new java.io.BufferedReader(new java.io.InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
                logger.info("Python script output: {}", line);

                // Check for error patterns in output
                if (line.startsWith("ERROR:") || line.contains("Exception") || line.contains("Error")) {
                    logger.error("Python script error detected: {}", line);
                    process.destroy();
                    throw new RuntimeException("Python script error: " + line);
                }

                if (line.startsWith("http")) {
                    imageUrl = line.trim();
                }
            }
        }

        int exitCode = process.waitFor();
        if (exitCode != 0) {
            throw new RuntimeException("Python script failed with exit code " + exitCode);
        }

        // Validate the output is a URL
//        String result = output.toString().trim();
//        if (!result.startsWith("http")) {
//            throw new RuntimeException("Invalid output from Python script: " + result);
//        }

        // Clean up temporary files
        try {
            Files.deleteIfExists(Paths.get(userImagePath));
            Files.deleteIfExists(Paths.get(clothImagePath));
        } catch (IOException e) {
            logger.warn("Failed to delete temporary files: {}", e.getMessage());
        }

        return imageUrl;
    }

    private Path getOutputPath() {
        Path path = Paths.get(outputDir);
        if (!path.isAbsolute()) {
            // If relative path, make it relative to project root
            path = Paths.get("").toAbsolutePath().resolve(outputDir);
        }
        return path;
    }

    private String saveFile(MultipartFile file, String prefix) throws IOException {
        Path outputPath = getOutputPath();
        Files.createDirectories(outputPath);

        String fileName = prefix + "_" + UUID.randomUUID() + "_" + file.getOriginalFilename();
        Path filePath = outputPath.resolve(fileName);
        file.transferTo(filePath);
        logger.info("File saved: {}", filePath);
        return filePath.toAbsolutePath().toString();
    }
}
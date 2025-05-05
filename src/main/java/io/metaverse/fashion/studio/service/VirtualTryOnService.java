// VirtualTryOnService.java
package io.metaverse.fashion.studio.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

@Service
public class VirtualTryOnService {

    @Value("${python.vtonscript.path}")
    private String pythonScriptPath;

    @Value("${ai.vtonoutput.dir}")
    private String outputDir;

    public String processImages(MultipartFile userImage, MultipartFile clothImage) throws IOException, InterruptedException {
        // Create output directory if it doesn't exist
        Path outputPath = Paths.get(outputDir);
        if (!Files.exists(outputPath)) {
            Files.createDirectories(outputPath);
        }

        // Save uploaded files temporarily
        String userImagePath = saveFile(userImage, "user");
        String clothImagePath = saveFile(clothImage, "cloth");

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
            }
        }

        int exitCode = process.waitFor();
        if (exitCode != 0) {
            throw new RuntimeException("Error running Python script: " + output);
        }

        // Clean up temporary files
        Files.deleteIfExists(Paths.get(userImagePath));
        Files.deleteIfExists(Paths.get(clothImagePath));

        // Return the result URL (last line of the output)
        return output.toString().trim();
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
        return filePath.toAbsolutePath().toString();
    }
}
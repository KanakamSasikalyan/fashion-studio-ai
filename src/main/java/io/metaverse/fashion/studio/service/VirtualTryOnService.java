package io.metaverse.fashion.studio.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.util.UUID;

@Service
public class VirtualTryOnService {

    @Value("${python.script.path}")
    private String pythonScriptPath;

    @Value("${ai.output.dir}")
    private String outputDir;

    public String processImages(MultipartFile userImage, MultipartFile clothImage) throws IOException, InterruptedException {
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

        // Return the result URL (last line of the output)
        return output.toString().trim();
    }

    private String saveFile(MultipartFile file, String prefix) throws IOException {
        String fileName = prefix + "_" + UUID.randomUUID() + "_" + file.getOriginalFilename();
        File tempFile = new File(outputDir, fileName);
        file.transferTo(tempFile);
        return tempFile.getAbsolutePath();
    }
}
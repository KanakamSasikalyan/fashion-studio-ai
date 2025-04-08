package io.metaverse.fashion.studio.service;

import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Paths;

@Service
public class VirtualTryOnService {

    @Value("${python.virtual_try_on_script}")
    private String virtualTryOnScriptPath;

    public String processVirtualTryOn(String clothingImagePath,
                                      String userImagePath,
                                      boolean isCameraInput) {
        try {
            ProcessBuilder pb = new ProcessBuilder(
                    "python",
                    virtualTryOnScriptPath,
                    clothingImagePath,
                    userImagePath,
                    String.valueOf(isCameraInput)
            );

            pb.redirectErrorStream(true);

            Process process = pb.start();
            StringBuilder output = new StringBuilder();

            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    output.append(line);
                }
            }

            int exitCode = process.waitFor();
            if (exitCode != 0) {
                throw new RuntimeException("Python script failed: " + output);
            }

            return output.toString();
        } catch (IOException | InterruptedException e) {
            throw new RuntimeException("Virtual try-on processing failed", e);
        }
    }
}
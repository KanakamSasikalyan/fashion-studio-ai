package io.metaverse.fashion.studio.service;

import io.metaverse.fashion.studio.entity.ClothingDesign;
import io.metaverse.fashion.studio.repository.ClothingDesignRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Base64;
import java.util.stream.Collectors;

@Service
public class AIClothingService {

    Logger log = LoggerFactory.getLogger(AIClothingService.class);

    @Value("${ai.output.dir}")
    private String outputDir;

    private final String pythonScriptPath;
    private final ClothingDesignRepository clothingDesignRepository;

    @Autowired
    public AIClothingService(@Value("${python.script.path}") String pythonScriptPath, ClothingDesignRepository clothingDesignRepository) {
        this.pythonScriptPath = pythonScriptPath;
        this.clothingDesignRepository = clothingDesignRepository;
    }

    public byte[] generateClothingDesign(String prompt, String style) throws IOException {
        // Ensure output directory exists
        Files.createDirectories(Paths.get(outputDir));

        ProcessBuilder pb = new ProcessBuilder(
                "python",
                pythonScriptPath,
                "\"" + prompt + "\"",
                style,
                outputDir
        );

        // Redirect error stream to standard output
        pb.redirectErrorStream(true);

        Process process = pb.start();

        // Capture and log Python output in real-time
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream()))) {

            String line;
            while ((line = reader.readLine()) != null) {
                if (line.startsWith("ERROR")) {
                    log.error("Python: " + line);
                } else {
                    log.info("Python: " + line);
                }
            }
        }

        try {

            String base64Image = new BufferedReader(
                    new InputStreamReader(process.getInputStream())
            ).readLine();

            if (process.waitFor() != 0) {
                String error = new BufferedReader(
                        new InputStreamReader(process.getErrorStream())
                ).lines().collect(Collectors.joining("\n"));
                throw new RuntimeException("AI generation failed:\n" + error);
            }

            byte[] imageBytes = Base64.getDecoder().decode(base64Image);

            // Store image in database using JPA repository
            ClothingDesign design = new ClothingDesign();
            design.setPrompt(prompt);
            design.setStyle(style);
            design.setImageData(imageBytes);
            clothingDesignRepository.save(design);

            return imageBytes;

        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Generation interrupted", e);
        }
    }
}

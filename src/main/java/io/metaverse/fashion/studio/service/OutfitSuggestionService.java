package io.metaverse.fashion.studio.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.concurrent.TimeUnit;

@Service
public class OutfitSuggestionService {
    private static final Logger logger = LoggerFactory.getLogger(OutfitSuggestionService.class);

    @Value("${python.outfitscript.path}")
    private String pythonScriptPath;

    private final ObjectMapper objectMapper = new ObjectMapper();

    public String getOutfitSuggestion(String occasion, String gender) throws IOException {
        try {
            logger.info("Executing Python script for occasion: {} and gender: {}", occasion, gender);

            ProcessBuilder pb = new ProcessBuilder(
                    "python",
                    pythonScriptPath,
                    occasion,
                    gender
            );

            pb.redirectErrorStream(true);
            Process process = pb.start();

            String processOutput = readStream(process.getInputStream());
            logger.debug("Python script output:\n{}", processOutput);

            if (!process.waitFor(1, TimeUnit.MINUTES)) {
                process.destroy();
                throw new RuntimeException("Python script timed out");
            }

            if (process.exitValue() != 0) {
                throw new RuntimeException("Python script failed: " + processOutput);
            }

            JsonNode response = objectMapper.readTree(processOutput);
            if (!response.path("status").asText().equals("success")) {
                throw new RuntimeException(
                        "Prediction failed: " + response.path("message").asText()
                );
            }

            return response.path("outfitSuggestion").asText();

        } catch (IOException | InterruptedException e) {
            logger.error("Error executing Python script: {}", e.getMessage(), e);
            throw new RuntimeException("Python script execution failed", e);
        }
    }

    private String readStream(InputStream inputStream) throws IOException {
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream))) {
            StringBuilder builder = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                builder.append(line);
            }
            return builder.toString();
        }
    }
}
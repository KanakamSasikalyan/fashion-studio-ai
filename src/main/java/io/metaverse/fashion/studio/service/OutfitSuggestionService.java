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

    public String getOutfitSuggestion(String occasion) throws IOException {
        try {
            logger.info("Executing Python script for occasion: {}", occasion);

            ProcessBuilder pb = new ProcessBuilder(
                    "python",
                    pythonScriptPath,
                    occasion
            );

            // Redirect error stream to output stream to capture all logs
            pb.redirectErrorStream(true);

            Process process = pb.start();

            // Read the combined output stream (stdout + stderr)
            String processOutput = readStream(process.getInputStream());

            // Log the Python output
            logger.debug("Python script output:\n{}", processOutput);

            // Wait for the process to complete with timeout
            boolean finished = process.waitFor(30, TimeUnit.SECONDS);
            if (!finished) {
                process.destroy();
                throw new RuntimeException("Python script execution timed out");
            }

            if (processOutput == null || processOutput.isEmpty()) {
                throw new RuntimeException("Python script returned no output");
            }

            // Parse JSON
            JsonNode rootNode;
            try {
                rootNode = objectMapper.readTree(processOutput);
            } catch (Exception e) {
                logger.error("Failed to parse Python script output: {}", processOutput);
                throw new RuntimeException("Invalid JSON output from Python script", e);
            }

            if ("error".equals(rootNode.path("status").asText())) {
                String errorMessage = rootNode.path("message").asText();
                logger.error("Python script reported error: {}", errorMessage);
                throw new RuntimeException("Python error: " + errorMessage);
            }

            String suggestion = rootNode.path("outfitSuggestion").asText();
            logger.info("Outfit suggestion received: {}", suggestion);
            return suggestion;

        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            logger.error("Python script execution interrupted", e);
            throw new RuntimeException("Script execution interrupted", e);
        }
    }

    private String readStream(InputStream inputStream) throws IOException {
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream))) {
            StringBuilder builder = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                builder.append(line).append("\n");
            }
            return builder.toString().trim();
        }
    }
}
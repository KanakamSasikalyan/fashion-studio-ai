package io.metaverse.fashion.studio.service;

import com.fasterxml.jackson.core.JsonProcessingException;
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

    public String callGetOutfitSuggestion(String occasion, String gender, String season) throws IOException {
        return getOutfitSuggestion(occasion, gender, season);
    }

    public String getOutfitSuggestion(String occasion, String gender, String season) throws IOException {
        try {
            logger.info("Executing enhanced Python script for occasion: {}, gender: {}, season: {}",
                    occasion, gender, season);

            ProcessBuilder pb = new ProcessBuilder(
                    "python",
                    pythonScriptPath,
                    occasion,
                    gender,
                    season
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

            // Parse JSON response to validate status, but return the original JSON string
            JsonNode response;
            try {
                response = objectMapper.readTree(processOutput);
            } catch (JsonProcessingException e) {
                throw new RuntimeException("Failed to parse Python script output: " + processOutput, e);
            }

            if (!response.path("status").asText().equals("success")) {
                throw new RuntimeException(
                        "Prediction failed: " + response.path("message").asText()
                );
            }

            // Return the raw JSON string to the frontend for both cases
            return processOutput;

        } catch (IOException | InterruptedException e) {
            logger.error("Error executing Python script: {}", e.getMessage(), e);
            throw new RuntimeException("Python script execution failed", e);
        }
    }

    public String callGetOutfitSuggestionByPrompt(String prompt) throws IOException {
        try {
            logger.info("Executing enhanced Python script for prompt: {}", prompt);
            ProcessBuilder pb = new ProcessBuilder(
                    "python",
                    pythonScriptPath,
                    prompt
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
            // Parse JSON response
            JsonNode response;
            try {
                response = objectMapper.readTree(processOutput);
            } catch (JsonProcessingException e) {
                throw new RuntimeException("Failed to parse Python script output: " + processOutput, e);
            }
            if (!response.path("status").asText().equals("success")) {
                throw new RuntimeException(
                        "Prediction failed: " + response.path("message").asText()
                );
            }
            // Return the raw JSON string to the frontend
            return processOutput;
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
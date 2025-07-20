package io.metaverse.fashion.studio.service;

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

    public String callGetOutfitSuggestion(String occasion, String gender, String season) throws IOException {
        return getOutfitSuggestion(occasion, gender, season);
    }

    public String callGetOutfitSuggestionByPrompt(String prompt) throws IOException {
        return getOutfitSuggestion(prompt, "unisex", "all");
    }

    private String getOutfitSuggestion(String input, String gender, String season) throws IOException {
        try {
            logger.info("Executing Python script with OpenAI integration for input: {}, gender: {}, season: {}",
                    input, gender, season);

            ProcessBuilder pb = new ProcessBuilder(
                    "python",
                    pythonScriptPath,
                    input,
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

            return processOutput;

        } catch (InterruptedException e) {
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
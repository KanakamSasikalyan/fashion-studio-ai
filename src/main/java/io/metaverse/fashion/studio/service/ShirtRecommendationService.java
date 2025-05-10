package io.metaverse.fashion.studio.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.nio.file.*;
import java.util.*;

@Service
public class ShirtRecommendationService {

    @Value("${python.shirtrecommend.script}")
    private String pythonScriptPath;

    private final String tempImageDir = "temp_images";
    private final String pythonExecutable = "python";

    public ShirtRecommendationService() {
        try {
            Files.createDirectories(Paths.get(tempImageDir));
        } catch (IOException e) {
            throw new RuntimeException("Failed to create temp image directory", e);
        }
    }

    public Map<String, Object> recommendShirts(
            MultipartFile image1, String platform1, Double price1, String description1,
            MultipartFile image2, String platform2, Double price2, String description2) throws IOException, InterruptedException {

        // Validate at least one image is provided
        if (image1 == null && image2 == null) {
            throw new IllegalArgumentException("At least one shirt image must be provided");
        }

        // Save images and build command
        List<String> command = new ArrayList<>();
        command.add(pythonExecutable);
        command.add(pythonScriptPath);

        if (image1 != null) {
            String image1Path = saveImage("shirt1", image1);
            command.addAll(List.of(
                    "--image1", image1Path,
                    "--platform1", platform1 != null ? platform1 : "Unknown",
                    "--price1", price1 != null ? String.valueOf(price1) : "1000.0",
                    "--description1", description1 != null ? description1 : ""
            ));
        }

        if (image2 != null) {
            String image2Path = saveImage("shirt2", image2);
            command.addAll(List.of(
                    "--image2", image2Path,
                    "--platform2", platform2 != null ? platform2 : "Unknown",
                    "--price2", price2 != null ? String.valueOf(price2) : "1000.0",
                    "--description2", description2 != null ? description2 : ""
            ));
        }

        // Add default weights
        command.addAll(List.of(
                "--platform_weight", "0.2",
                "--price_weight", "0.3",
                "--color_weight", "0.2",
                "--material_weight", "0.2",
                "--description_weight", "0.1"
        ));

        ProcessBuilder processBuilder = new ProcessBuilder(command);
        processBuilder.redirectErrorStream(true);

        Process process = processBuilder.start();

        StringBuilder output = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }
        }

        int exitCode = process.waitFor();
        if (exitCode != 0) {
            throw new RuntimeException("Python script failed with exit code: " + exitCode + "\nOutput: " + output.toString());
        }

        return new ObjectMapper().readValue(output.toString(), Map.class);
    }

    private String saveImage(String id, MultipartFile image) throws IOException {
        String filename = id + "_" + System.currentTimeMillis() + ".jpg";
        Path path = Paths.get(tempImageDir, filename);
        image.transferTo(path);
        path.toFile().deleteOnExit();
        return path.toAbsolutePath().toString();
    }
}

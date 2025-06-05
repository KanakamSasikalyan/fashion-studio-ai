package io.metaverse.fashion.studio.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;
import java.util.logging.Logger;

@Service
public class ImageProcessingService {

    Logger logger = Logger.getLogger(String.valueOf(ImageProcessingService.class));

    @Value("${python.scripts.remove-background}")
    private String removeBackgroundScript;

    @Value("${file.upload.temp-dir}")
    private String tempDir;

    public String removeBackground(String imageUrl) throws IOException, InterruptedException {
        // Create temp directory if not exists
        Path tempPath = Paths.get(tempDir);
        if (!Files.exists(tempPath)) {
            Files.createDirectories(tempPath);
        }

        // Generate unique filenames
        String inputFilename = UUID.randomUUID() + ".jpg";
        String outputFilename = "processed_" + UUID.randomUUID() + ".png";

        Path inputPath = tempPath.resolve(inputFilename);
        Path outputPath = tempPath.resolve(outputFilename);

        try {
            // Download image from URL
            byte[] imageBytes = downloadImage(imageUrl);
            Files.write(inputPath, imageBytes);

            // Build and execute Python process
            ProcessBuilder pb = new ProcessBuilder(
                    "python",
                    removeBackgroundScript,
                    inputPath.toString(),
                    outputPath.toString()
            );

            pb.redirectErrorStream(true);
            Process process = pb.start();

            // Read output
            StringBuilder pythonOutput = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    pythonOutput.append(line).append("\n");
                }
            }

            int exitCode = process.waitFor();
            logger.info("Python remove_background.py output: " + pythonOutput.toString());

            if (exitCode != 0 || !pythonOutput.toString().contains("SUCCESS:")) {
                throw new IOException("Python script failed: " + pythonOutput.toString());
            }

            // Parse output to get the processed image path
            if (pythonOutput.toString().startsWith("SUCCESS:")) {
                String processedPath = pythonOutput.toString().substring(8).trim();

                // Verify the processed image exists
                if (!Files.exists(Paths.get(processedPath))) {
                    throw new IOException("Processed image not found at: " + processedPath);
                }

                return processedPath;
            } else {
                throw new IOException(pythonOutput.toString());
            }
        } finally {
            // Clean up input file (output file will be served and then deleted by controller)
            Files.deleteIfExists(inputPath);
        }
    }

    private byte[] downloadImage(String imageUrl) throws IOException {
        // Validate URL
        if (imageUrl == null || imageUrl.trim().isEmpty()) {
            throw new IOException("Image URL cannot be null or empty");
        }

        HttpURLConnection connection = null;
        InputStream inputStream = null;
        ByteArrayOutputStream outputStream = null;

        try {
            URL url = new URL(imageUrl);
            connection = (HttpURLConnection) url.openConnection();

            // Set timeout and headers
            connection.setConnectTimeout(5000); // 5 seconds
            connection.setReadTimeout(15000);   // 15 seconds
            connection.setRequestProperty("User-Agent", "FashionStudioAI/1.0");

            // Verify response code
            int responseCode = connection.getResponseCode();
            if (responseCode != HttpURLConnection.HTTP_OK) {
                throw new IOException("Server returned HTTP " + responseCode + " for URL: " + imageUrl);
            }

            // Check content type
            String contentType = connection.getContentType();
            if (contentType == null || !contentType.startsWith("image/")) {
                throw new IOException("Invalid content type: " + contentType);
            }

            // Get content length for progress/validation
            int contentLength = connection.getContentLength();
            if (contentLength > 10_000_000) { // 10MB max
                throw new IOException("Image too large (max 10MB)");
            }

            // Read image data
            inputStream = connection.getInputStream();
            outputStream = new ByteArrayOutputStream(contentLength > 0 ? contentLength : 8192);

            byte[] buffer = new byte[8192];
            int bytesRead;
            while ((bytesRead = inputStream.read(buffer)) != -1) {
                outputStream.write(buffer, 0, bytesRead);
            }

            return outputStream.toByteArray();

        } catch (MalformedURLException e) {
            throw new IOException("Invalid URL format: " + imageUrl, e);
        } finally {
            // Clean up resources
            if (inputStream != null) {
                try {
                    inputStream.close();
                } catch (IOException e) {
                    // Log but don't throw
                    logger.info("Error closing input stream");
                }
            }
            if (connection != null) {
                connection.disconnect();
            }
            if (outputStream != null) {
                try {
                    outputStream.close();
                } catch (IOException e) {
                    logger.info("Error closing output stream");
                }
            }
        }
    }
}





/*
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;
import java.util.logging.Logger;

@Service
public class ImageProcessingService {

    Logger logger = Logger.getLogger(String.valueOf(ImageProcessingService.class));

    @Value("${python.scripts.remove-background}")
    private String removeBackgroundScript;

    @Value("${file.upload.temp-dir}")
    private String tempDir;

    public String removeBackground(String imageUrl) throws IOException, InterruptedException {
        // Create temp directory if not exists
        Path tempPath = Paths.get(tempDir);
        if (!Files.exists(tempPath)) {
            Files.createDirectories(tempPath);
        }

        // Generate unique filenames
        String inputFilename = UUID.randomUUID() + ".jpg";
        String outputFilename = "processed_" + UUID.randomUUID() + ".png";

        Path inputPath = tempPath.resolve(inputFilename);
        Path outputPath = tempPath.resolve(outputFilename);

        try {
            // Download image from URL (simplified example)
            byte[] imageBytes = downloadImage(imageUrl);
            Files.write(inputPath, imageBytes);

            // Build and execute Python process
            ProcessBuilder pb = new ProcessBuilder(
                    "python",
                    removeBackgroundScript,
                    inputPath.toString(),
                    outputPath.toString()
            );

            pb.redirectErrorStream(true);
            Process process = pb.start();

            // Read output
            StringBuilder pythonOutput = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    pythonOutput.append(line).append("\n");
                }
            }

            int exitCode = process.waitFor();
            logger.info("Python remove_background.py output: " + pythonOutput.toString());
            if (exitCode != 0 || !pythonOutput.toString().contains("SUCCESS:")) {
                throw new IOException("Python script failed: " + pythonOutput.toString());
            }

            // Parse output
            if (pythonOutput.toString().startsWith("SUCCESS:")) {
                String processedPath = pythonOutput.toString().substring(8);
                return processedPath;
            } else {
                throw new IOException(pythonOutput.toString());
            }
        } finally {
            // Clean up input file (output file will be served)
            Files.deleteIfExists(inputPath);
        }
    }

    private byte[] downloadImage(String imageUrl) throws IOException {
        // Validate URL
        if (imageUrl == null || imageUrl.trim().isEmpty()) {
            throw new IOException("Image URL cannot be null or empty");
        }

        HttpURLConnection connection = null;
        InputStream inputStream = null;
        ByteArrayOutputStream outputStream = null;

        try {
            URL url = new URL(imageUrl);
            connection = (HttpURLConnection) url.openConnection();

            // Set timeout and headers
            connection.setConnectTimeout(5000); // 5 seconds
            connection.setReadTimeout(15000);   // 15 seconds
            connection.setRequestProperty("User-Agent", "FashionStudioAI/1.0");

            // Verify response code
            int responseCode = connection.getResponseCode();
            if (responseCode != HttpURLConnection.HTTP_OK) {
                throw new IOException("Server returned HTTP " + responseCode + " for URL: " + imageUrl);
            }

            // Check content type
            String contentType = connection.getContentType();
            if (contentType == null || !contentType.startsWith("image/")) {
                throw new IOException("Invalid content type: " + contentType);
            }

            // Get content length for progress/validation
            int contentLength = connection.getContentLength();
            if (contentLength > 10_000_000) { // 10MB max
                throw new IOException("Image too large (max 10MB)");
            }

            // Read image data
            inputStream = connection.getInputStream();
            outputStream = new ByteArrayOutputStream(contentLength > 0 ? contentLength : 8192);

            byte[] buffer = new byte[8192];
            int bytesRead;
            while ((bytesRead = inputStream.read(buffer)) != -1) {
                outputStream.write(buffer, 0, bytesRead);
            }

            return outputStream.toByteArray();

        } catch (MalformedURLException e) {
            throw new IOException("Invalid URL format: " + imageUrl, e);
        } finally {
            // Clean up resources
            if (inputStream != null) {
                try {
                    inputStream.close();
                } catch (IOException e) {
                    // Log but don't throw
                    logger.info("Error closing input stream");
                }
            }
            if (connection != null) {
                connection.disconnect();
            }
            if (outputStream != null) {
                try {
                    outputStream.close();
                } catch (IOException e) {
                    logger.info("Error closing output stream");
                }
            }
        }
    }
}*/

/*package io.metaverse.fashion.studio.service;

import io.metaverse.fashion.studio.entity.ProcessedImage;
import io.metaverse.fashion.studio.repository.ProcessedImageRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;
import java.util.logging.Logger;

@Service
public class ImageProcessingService {

    private final ProcessedImageRepository processedImageRepository;

    Logger logger = Logger.getLogger(String.valueOf(ImageProcessingService.class));

    @Value("${python.scripts.remove-background}")
    private String removeBackgroundScript;

    @Value("${file.upload.temp-dir}")
    private String tempDir;

    public ImageProcessingService(ProcessedImageRepository processedImageRepository) {
        this.processedImageRepository = processedImageRepository;
    }

    public String removeBackground(MultipartFile file) throws IOException, InterruptedException {
        // Create temp directory if not exists
        Path tempPath = Paths.get(tempDir);
        if (!Files.exists(tempPath)) {
            Files.createDirectories(tempPath);
        }

        // Generate unique filename
        String inputFilename = UUID.randomUUID() + ".jpg";
        Path inputPath = tempPath.resolve(inputFilename);

        try {
            // Save uploaded file to temp location
            file.transferTo(inputPath);

            // Build and execute Python process
            ProcessBuilder pb = new ProcessBuilder(
                    "python",
                    removeBackgroundScript,
                    inputPath.toString()
            );

            pb.redirectErrorStream(true);
            Process process = pb.start();

            // Read output
            StringBuilder pythonOutput = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    pythonOutput.append(line).append("\n");
                }
            }

            int exitCode = process.waitFor();
            if (exitCode != 0 || !pythonOutput.toString().contains("SUCCESS:")) {
                throw new IOException("Python script failed: " + pythonOutput.toString());
            }

            // Parse output to get the image URL
            if (pythonOutput.toString().startsWith("SUCCESS:")) {
                String imageUrl = pythonOutput.toString().substring(8).trim();

                // Save to database
                ProcessedImage processedImage = new ProcessedImage();
                processedImage.setOriginalFilename(file.getOriginalFilename());
                processedImage.setImageUrl(imageUrl);
                processedImageRepository.save(processedImage);

                return imageUrl;
            } else {
                throw new IOException(pythonOutput.toString());
            }
        } finally {
            // Clean up input file
            Files.deleteIfExists(inputPath);
        }
    }

    private byte[] downloadImage(String imageUrl) throws IOException {
        // Validate URL
        if (imageUrl == null || imageUrl.trim().isEmpty()) {
            throw new IOException("Image URL cannot be null or empty");
        }

        HttpURLConnection connection = null;
        InputStream inputStream = null;
        ByteArrayOutputStream outputStream = null;

        try {
            URL url = new URL(imageUrl);
            connection = (HttpURLConnection) url.openConnection();

            // Set timeout and headers
            connection.setConnectTimeout(5000); // 5 seconds
            connection.setReadTimeout(15000);   // 15 seconds
            connection.setRequestProperty("User-Agent", "FashionStudioAI/1.0");

            // Verify response code
            int responseCode = connection.getResponseCode();
            if (responseCode != HttpURLConnection.HTTP_OK) {
                throw new IOException("Server returned HTTP " + responseCode + " for URL: " + imageUrl);
            }

            // Check content type
            String contentType = connection.getContentType();
            if (contentType == null || !contentType.startsWith("image/")) {
                throw new IOException("Invalid content type: " + contentType);
            }

            // Get content length for progress/validation
            int contentLength = connection.getContentLength();
            if (contentLength > 10_000_000) { // 10MB max
                throw new IOException("Image too large (max 10MB)");
            }

            // Read image data
            inputStream = connection.getInputStream();
            outputStream = new ByteArrayOutputStream(contentLength > 0 ? contentLength : 8192);

            byte[] buffer = new byte[8192];
            int bytesRead;
            while ((bytesRead = inputStream.read(buffer)) != -1) {
                outputStream.write(buffer, 0, bytesRead);
            }

            return outputStream.toByteArray();

        } catch (MalformedURLException e) {
            throw new IOException("Invalid URL format: " + imageUrl, e);
        } finally {
            // Clean up resources
            if (inputStream != null) {
                try {
                    inputStream.close();
                } catch (IOException e) {
                    // Log but don't throw
                    logger.info("Error closing input stream");
                }
            }
            if (connection != null) {
                connection.disconnect();
            }
            if (outputStream != null) {
                try {
                    outputStream.close();
                } catch (IOException e) {
                    logger.info("Error closing output stream");
                }
            }
        }
    }
}*/

/*
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;
import java.util.logging.Logger;

@Service
public class ImageProcessingService {

    Logger logger = Logger.getLogger(String.valueOf(ImageProcessingService.class));

    @Value("${python.scripts.remove-background}")
    private String removeBackgroundScript;

    @Value("${file.upload.temp-dir}")
    private String tempDir;

    public String removeBackground(String imageUrl) throws IOException, InterruptedException {
        // Create temp directory if not exists
        Path tempPath = Paths.get(tempDir);
        if (!Files.exists(tempPath)) {
            Files.createDirectories(tempPath);
        }

        // Generate unique filenames
        String inputFilename = UUID.randomUUID() + ".jpg";
        String outputFilename = "processed_" + UUID.randomUUID() + ".png";

        Path inputPath = tempPath.resolve(inputFilename);
        Path outputPath = tempPath.resolve(outputFilename);

        try {
            // Download image from URL (simplified example)
            byte[] imageBytes = downloadImage(imageUrl);
            Files.write(inputPath, imageBytes);

            // Build and execute Python process
            ProcessBuilder pb = new ProcessBuilder(
                    "python",
                    removeBackgroundScript,
                    inputPath.toString(),
                    outputPath.toString()
            );

            pb.redirectErrorStream(true);
            Process process = pb.start();

            // Read output
            StringBuilder pythonOutput = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    pythonOutput.append(line).append("\n");
                }
            }

            int exitCode = process.waitFor();
            logger.info("Python remove_background.py output: " + pythonOutput.toString());
            if (exitCode != 0 || !pythonOutput.toString().contains("SUCCESS:")) {
                throw new IOException("Python script failed: " + pythonOutput.toString());
            }

            // Parse output
            if (pythonOutput.toString().startsWith("SUCCESS:")) {
                String processedPath = pythonOutput.toString().substring(8);
                return processedPath;
            } else {
                throw new IOException(pythonOutput.toString());
            }
        } finally {
            // Clean up input file (output file will be served)
            Files.deleteIfExists(inputPath);
        }
    }

    private byte[] downloadImage(String imageUrl) throws IOException {
        // Validate URL
        if (imageUrl == null || imageUrl.trim().isEmpty()) {
            throw new IOException("Image URL cannot be null or empty");
        }

        HttpURLConnection connection = null;
        InputStream inputStream = null;
        ByteArrayOutputStream outputStream = null;

        try {
            URL url = new URL(imageUrl);
            connection = (HttpURLConnection) url.openConnection();

            // Set timeout and headers
            connection.setConnectTimeout(5000); // 5 seconds
            connection.setReadTimeout(15000);   // 15 seconds
            connection.setRequestProperty("User-Agent", "FashionStudioAI/1.0");

            // Verify response code
            int responseCode = connection.getResponseCode();
            if (responseCode != HttpURLConnection.HTTP_OK) {
                throw new IOException("Server returned HTTP " + responseCode + " for URL: " + imageUrl);
            }

            // Check content type
            String contentType = connection.getContentType();
            if (contentType == null || !contentType.startsWith("image/")) {
                throw new IOException("Invalid content type: " + contentType);
            }

            // Get content length for progress/validation
            int contentLength = connection.getContentLength();
            if (contentLength > 10_000_000) { // 10MB max
                throw new IOException("Image too large (max 10MB)");
            }

            // Read image data
            inputStream = connection.getInputStream();
            outputStream = new ByteArrayOutputStream(contentLength > 0 ? contentLength : 8192);

            byte[] buffer = new byte[8192];
            int bytesRead;
            while ((bytesRead = inputStream.read(buffer)) != -1) {
                outputStream.write(buffer, 0, bytesRead);
            }

            return outputStream.toByteArray();

        } catch (MalformedURLException e) {
            throw new IOException("Invalid URL format: " + imageUrl, e);
        } finally {
            // Clean up resources
            if (inputStream != null) {
                try {
                    inputStream.close();
                } catch (IOException e) {
                    // Log but don't throw
                    logger.info("Error closing input stream");
                }
            }
            if (connection != null) {
                connection.disconnect();
            }
            if (outputStream != null) {
                try {
                    outputStream.close();
                } catch (IOException e) {
                    logger.info("Error closing output stream");
                }
            }
        }
    }
}*/
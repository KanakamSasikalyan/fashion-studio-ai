package io.metaverse.fashion.studio.controller;

import io.metaverse.fashion.studio.service.ImageProcessingService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Map;

@RestController
public class ImageProcessingController {

    @Autowired
    private ImageProcessingService imageProcessingService;

    // ImageProcessingController.java (updated removeBackground method)
    @PostMapping("/api/image/remove-background")
    public ResponseEntity<?> removeBackground(@RequestBody Map<String, String> payload) {
        try {
            String imageUrl = payload.get("imageUrl");
            String processedImagePath = imageProcessingService.removeBackground(imageUrl);

            // Read the processed image file
            Path path = Paths.get(processedImagePath);
            byte[] imageBytes = Files.readAllBytes(path);

            // Clean up the file after reading
            Files.deleteIfExists(path);

            return ResponseEntity.ok()
                    .contentType(MediaType.IMAGE_PNG)
                    .body(imageBytes);
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body("{\"error\":\"" + e.getMessage() + "\"}");
        }
    }
}
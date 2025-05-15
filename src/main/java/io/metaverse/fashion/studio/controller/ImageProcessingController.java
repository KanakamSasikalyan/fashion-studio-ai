package io.metaverse.fashion.studio.controller;

import io.metaverse.fashion.studio.service.ImageProcessingService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ImageProcessingController {

    @Autowired
    private ImageProcessingService imageProcessingService;

    @PostMapping("/api/image/remove-background")
    public ResponseEntity<?> removeBackground(@RequestParam String imageUrl) {
        try {
            String processedImagePath = imageProcessingService.removeBackground(imageUrl);
            return ResponseEntity.ok()
                    .body("{\"processedImageUrl\":\"" + processedImagePath + "\"}");
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body("{\"error\":\"" + e.getMessage() + "\"}");
        }
    }
}
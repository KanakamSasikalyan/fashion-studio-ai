package io.metaverse.fashion.studio.controller;

import io.metaverse.fashion.studio.service.VirtualTryOnService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

@RestController
@RequestMapping("/api/try-on")
public class TryOnController {

    @Autowired
    private VirtualTryOnService virtualTryOnService;

    @Value("${file.upload-dir}")
    private String uploadDir;

    @Value("${file.generated-dir}")
    private String generatedDir;

    @PostMapping("/from-camera")
    public ResponseEntity<?> tryOnFromCamera(@RequestParam("clothingImage") String clothingImagePath) {
        try {
            // In production, you would capture the camera frame here
            // For demo purposes, we'll use a sample image
            String sampleUserImage = generatedDir + "sample_user.jpg";

            String resultPath = virtualTryOnService.processVirtualTryOn(
                    generatedDir + clothingImagePath,
                    sampleUserImage,
                    true
            );
            return ResponseEntity.ok().body(new TryOnResponse(resultPath));
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(new ErrorResponse("Camera try-on failed: " + e.getMessage()));
        }
    }

    @PostMapping("/from-upload")
    public ResponseEntity<?> tryOnFromUpload(
            @RequestParam("clothingImage") String clothingImagePath,
            @RequestParam("userImage") MultipartFile userImage) {

        if (userImage.isEmpty()) {
            return ResponseEntity.badRequest()
                    .body(new ErrorResponse("Please select an image to upload"));
        }

        try {
            String userImagePath = saveUploadedFile(userImage);
            String resultPath = virtualTryOnService.processVirtualTryOn(
                    generatedDir + clothingImagePath,
                    userImagePath,
                    false
            );
            return ResponseEntity.ok().body(new TryOnResponse(resultPath));
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                    .body(new ErrorResponse("Upload try-on failed: " + e.getMessage()));
        }
    }

    private String saveUploadedFile(MultipartFile file) throws IOException {
        String fileName = UUID.randomUUID() + "_" + file.getOriginalFilename();
        Path filePath = Paths.get(uploadDir, fileName);
        Files.copy(file.getInputStream(), filePath);
        return filePath.toString();
    }

    // Response DTOs
    private record TryOnResponse(String resultImagePath) {}
    private record ErrorResponse(String message) {}
}
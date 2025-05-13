package io.metaverse.fashion.studio.controller;

import io.metaverse.fashion.studio.service.CamVirtualTryOnService;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@RestController
@RequestMapping("/api/virtual-try-on")
public class CamVirtualTryOnController {
    private final CamVirtualTryOnService virtualTryOnService;

    public CamVirtualTryOnController(CamVirtualTryOnService virtualTryOnService) {
        this.virtualTryOnService = virtualTryOnService;
    }

    @PostMapping(value = "/start", consumes = MediaType.MULTIPART_FORM_DATA_VALUE, produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<?> startVirtualTryOn(
            @RequestParam("clothImage") MultipartFile clothImage,
            @RequestParam(value = "port", defaultValue = "8765") int port) {

        try {
            // Validate input
            if (clothImage.isEmpty()) {
                return ResponseEntity.badRequest().body("{\"error\": \"Cloth image is required\"}");
            }
            if (!clothImage.getContentType().startsWith("image/")) {
                return ResponseEntity.badRequest().body("{\"error\": \"Only image files are allowed\"}");
            }

            // Add logging to debug the parameters passed to the Python process
            System.out.println("Starting virtual try-on with cloth image: " + clothImage.getOriginalFilename() + ", Port: " + port);

            // Start the Python process
            virtualTryOnService.startPythonProcess(clothImage, port);

            // Ensure the response from the Python process is logged
            System.out.println("Python process started successfully. Listening on port: " + port);

            return ResponseEntity.ok()
                    .contentType(MediaType.APPLICATION_JSON)
                    .body("{\"message\": \"Virtual try-on started successfully\", \"port\": " + port + "}");
        } catch (IllegalStateException e) {
            return ResponseEntity.badRequest()
                    .contentType(MediaType.APPLICATION_JSON)
                    .body("{\"error\": \"" + e.getMessage() + "\"}");
        } catch (IOException e) {
            return ResponseEntity.internalServerError()
                    .contentType(MediaType.APPLICATION_JSON)
                    .body("{\"error\": \"Failed to start virtual try-on: " + e.getMessage() + "\"}");
        }
    }

    @PostMapping(value = "/stop", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<String> stopVirtualTryOn() {
        virtualTryOnService.stopPythonProcess();
        return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_JSON)
                .body("{\"message\": \"Virtual try-on stopped\"}");
    }

    @GetMapping(value = "/status", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<String> getStatus() {
        boolean isRunning = virtualTryOnService.isProcessRunning();
        return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_JSON)
                .body("{\"isRunning\": " + isRunning + "}");
    }
}
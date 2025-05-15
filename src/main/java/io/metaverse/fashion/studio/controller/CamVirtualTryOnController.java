package io.metaverse.fashion.studio.controller;

import io.metaverse.fashion.studio.service.CamVirtualTryOnService;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@RestController
@RequestMapping("/api/virtual-try-on")
public class CamVirtualTryOnController {

    private final CamVirtualTryOnService virtualTryOnService;
    private final SimpMessagingTemplate messagingTemplate;

    public CamVirtualTryOnController(CamVirtualTryOnService virtualTryOnService,
                                     SimpMessagingTemplate messagingTemplate) {
        this.virtualTryOnService = virtualTryOnService;
        this.messagingTemplate = messagingTemplate;
    }

    @PostMapping(value = "/upload-cloth", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<String> uploadClothImage(@RequestParam("file") MultipartFile file) {
        try {
            String imagePath = virtualTryOnService.saveClothImage(file);
            virtualTryOnService.startVirtualTryOn(imagePath, messagingTemplate);
            return ResponseEntity.ok("Virtual try-on started successfully");
        } catch (IOException e) {
            return ResponseEntity.badRequest().body("Error processing image: " + e.getMessage());
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return ResponseEntity.internalServerError().body("Processing interrupted");
        }
    }

    @PostMapping("/stop")
    public ResponseEntity<String> stopVirtualTryOn() {
        virtualTryOnService.stopVirtualTryOn();
        return ResponseEntity.ok("Virtual try-on stopped");
    }
}
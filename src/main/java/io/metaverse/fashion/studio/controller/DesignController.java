package io.metaverse.fashion.studio.controller;

import io.metaverse.fashion.studio.entity.ClothingDesign;
import io.metaverse.fashion.studio.service.AIClothingService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;

@RestController
@RequestMapping("/api/designs")
@CrossOrigin(origins = "*")
public class DesignController {

    private final AIClothingService aiService;

    @Autowired
    public DesignController(AIClothingService aiService) {
        this.aiService = aiService;
    }

    @PostMapping("/generate")
    public ResponseEntity<?> generateDesign(
            @RequestParam String prompt,
            @RequestParam(defaultValue = "casual") String style
    ) {
        try {
            String decodedPrompt = URLDecoder.decode(prompt, StandardCharsets.UTF_8);
            ClothingDesign design = aiService.generateClothingDesign(decodedPrompt, style);
            return ResponseEntity.ok(design);
        } catch (IOException e) {
            return ResponseEntity.internalServerError().body("Error generating design: " + e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body("Unexpected error: " + e.getMessage());
        }
    }
}
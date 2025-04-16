package io.metaverse.fashion.studio.controller;

import io.metaverse.fashion.studio.entity.ClothingDesign;
import io.metaverse.fashion.studio.repository.ClothingDesignRepository;
import io.metaverse.fashion.studio.service.AIClothingService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;

@RestController
@RequestMapping("/api/designs")
public class DesignController {

    private final AIClothingService aiService;

    @Autowired
    private ClothingDesignRepository clothingDesignRepository;

    public DesignController(AIClothingService aiService) {
        this.aiService = aiService;
    }

    @PostMapping(value = "/{prompt}", produces = MediaType.IMAGE_PNG_VALUE)
    public ResponseEntity<byte[]> generateDesign(
            @PathVariable String prompt,
            @RequestParam(defaultValue = "casual") String style
    ) {
        try {
            String decodedPrompt = URLDecoder.decode(prompt, StandardCharsets.UTF_8);
            byte[] imageBytes = aiService.generateClothingDesign(decodedPrompt, style);
            return ResponseEntity.ok().contentType(MediaType.IMAGE_PNG).body(imageBytes);
        } catch (IOException e) {
            return ResponseEntity.status(500).body(("Error: " + e.getMessage()).getBytes());
        } catch (Exception e) {
            return ResponseEntity.status(500).body(("Unexpected Error: " + e.getMessage()).getBytes());
        }
    }

    // @GetMapping(value = "/{id}", produces = MediaType.IMAGE_PNG_VALUE)
    // public ResponseEntity<byte[]> getDesign(@PathVariable Long id) {
    //     try {
    //         ClothingDesign design = clothingDesignRepository.findById(id)
    //                 .orElseThrow(() -> new RuntimeException("Design not found"));
    //         return ResponseEntity.ok().body(design.getImageData());
    //     } catch (Exception e) {
    //         return ResponseEntity.status(500).body(("Error: " + e.getMessage()).getBytes());
    //     }
    // }
}

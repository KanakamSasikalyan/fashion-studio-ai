package io.metaverse.fashion.studio.controller;

import io.metaverse.fashion.studio.entity.ClothingDesign;
import io.metaverse.fashion.studio.service.AIClothingService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;

import java.io.IOException;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.List;

@RestController
@RequestMapping("/api/designs")
public class DesignController {

    private final AIClothingService aiService;

    @Autowired
    public DesignController(AIClothingService aiService) {
        this.aiService = aiService;
    }

    @GetMapping("/generate")
    public ResponseEntity<?> generateDesign(
            @RequestParam String prompt,
            @RequestParam(defaultValue = "casual") String style,
            @RequestParam(defaultValue = "male") String gender
    ) {
        try {
            String decodedPrompt = URLDecoder.decode(prompt, StandardCharsets.UTF_8);
            ClothingDesign design = aiService.generateClothingDesign(decodedPrompt, style, gender);
            return ResponseEntity.ok(design);
        } catch (IOException e) {
            return ResponseEntity.internalServerError().body("Error generating design: " + e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body("Unexpected error: " + e.getMessage());
        }
    }

    @GetMapping(value = "/generate/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<ServerSentEvent<String>> generateDesignStream(
            @RequestParam String prompt,
            @RequestParam(defaultValue = "casual") String style,
            @RequestParam(defaultValue = "man") String gender
    ) {
        return aiService.generateClothingDesignStream(prompt, style, gender);
    }

    @GetMapping("/image-urls")
    public List<String> getAllImageUrls() {
        return aiService.getAllImageUrls();
    }

    @GetMapping("/all")
    public List<ClothingDesign> getAllDesigns() {
        return aiService.getAllDesigns();
    }
}
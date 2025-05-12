package io.metaverse.fashion.studio.controller;

import io.metaverse.fashion.studio.service.ShirtRecommendationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.Parameter;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;

@RestController
@RequestMapping("/api/shirts")
public class ShirtRecommendationController {

    private final ShirtRecommendationService recommendationService;

    public ShirtRecommendationController(ShirtRecommendationService recommendationService) {
        this.recommendationService = recommendationService;
    }

    @Operation(summary = "Compare two shirts", description = "Upload images and details of two shirts to get a recommendation")
    @PostMapping(value = "/compare", consumes = MediaType.MULTIPART_FORM_DATA_VALUE, produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<?> compareShirts(
            @RequestPart(value = "image1", required = false) MultipartFile image1,
            @RequestParam(value = "platform1", required = false) String platform1,
            @RequestParam(value = "price1", required = false) Double price1,
            @RequestParam(value = "description1", required = false) String description1,
            @RequestPart(value = "image2", required = false) MultipartFile image2,
            @RequestParam(value = "platform2", required = false) String platform2,
            @RequestParam(value = "price2", required = false) Double price2,
            @RequestParam(value = "description2", required = false) String description2) {

        try {
            Map<String, Object> response = recommendationService.recommendShirts(
                    image1, platform1, price1, description1,
                    image2, platform2, price2, description2
            );

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(
                    Map.of("status", "error", "message", e.getMessage()));
        }
    }
}
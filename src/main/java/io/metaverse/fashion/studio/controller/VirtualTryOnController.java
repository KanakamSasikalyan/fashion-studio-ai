package io.metaverse.fashion.studio.controller;

import io.metaverse.fashion.studio.service.VirtualTryOnService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Schema;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@RestController
@RequestMapping("/api/virtual-tryon")
public class VirtualTryOnController {

    @Autowired
    private VirtualTryOnService virtualTryOnService;

    @Operation(summary = "Try on clothing using images")
    @PostMapping(value = "/try-on", consumes = "multipart/form-data")
    public ResponseEntity<?> tryOnClothing(
            @Parameter(description = "User image file", schema = @Schema(type = "string", format = "binary"))
            @RequestParam("userImage") MultipartFile userImage,

            @Parameter(description = "Cloth image file", schema = @Schema(type = "string", format = "binary"))
            @RequestParam("clothImage") MultipartFile clothImage
    ) {
        try {
            String resultUrl = virtualTryOnService.processImages(userImage, clothImage);
            return ResponseEntity.ok(resultUrl);
        } catch (IOException | InterruptedException e) {
            return ResponseEntity.internalServerError().body("Error processing request: " + e.getMessage());
        }
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<String> handleException(Exception e) {
        return ResponseEntity.internalServerError().body("An unexpected error occurred: " + e.getMessage());
    }
}
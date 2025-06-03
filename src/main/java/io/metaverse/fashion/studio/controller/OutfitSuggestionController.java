package io.metaverse.fashion.studio.controller;

import io.metaverse.fashion.studio.service.OutfitSuggestionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.io.IOException;

@RestController
@RequestMapping("/api/outfit")
public class OutfitSuggestionController {
    private final OutfitSuggestionService outfitSuggestionService;

    @Autowired
    public OutfitSuggestionController(OutfitSuggestionService outfitSuggestionService) {
        this.outfitSuggestionService = outfitSuggestionService;
    }

    @GetMapping("/suggest")
    public ResponseEntity<String> suggestOutfit(
            @RequestParam String occasion,
            @RequestParam String gender,
            @RequestParam(required = false, defaultValue = "all") String season) throws IOException {
        String json = outfitSuggestionService.callGetOutfitSuggestion(occasion, gender, season);
        return ResponseEntity.ok().contentType(MediaType.APPLICATION_JSON).body(json);
    }
}
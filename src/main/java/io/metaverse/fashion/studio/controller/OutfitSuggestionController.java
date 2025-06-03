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
            @RequestParam(required = false) String occasion,
            @RequestParam(required = false) String gender,
            @RequestParam(required = false, defaultValue = "all") String season,
            @RequestParam(required = false) String prompt) throws IOException {
        String json;
        if (prompt != null && !prompt.isEmpty()) {
            json = outfitSuggestionService.callGetOutfitSuggestionByPrompt(prompt);
        } else if (occasion != null && gender != null) {
            json = outfitSuggestionService.callGetOutfitSuggestion(occasion, gender, season);
        } else {
            return ResponseEntity.badRequest().body("{\"status\":\"error\",\"message\":\"Missing required parameters.\"}");
        }
        return ResponseEntity.ok().contentType(MediaType.APPLICATION_JSON).body(json);
    }
}
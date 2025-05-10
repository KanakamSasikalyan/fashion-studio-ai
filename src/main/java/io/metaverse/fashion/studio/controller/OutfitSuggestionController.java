package io.metaverse.fashion.studio.controller;

import io.metaverse.fashion.studio.service.OutfitSuggestionService;
import org.springframework.beans.factory.annotation.Autowired;
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
    public String suggestOutfit(@RequestParam String occasion) throws IOException {
        return outfitSuggestionService.getOutfitSuggestion(occasion);
    }
}

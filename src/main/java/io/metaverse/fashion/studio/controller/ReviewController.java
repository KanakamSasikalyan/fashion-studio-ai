package io.metaverse.fashion.studio.controller;

import io.metaverse.fashion.studio.entity.Review;
import io.metaverse.fashion.studio.service.ReviewService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/reviews")
public class ReviewController {
    @Autowired
    private ReviewService reviewService;

    @PostMapping
    public ResponseEntity<Review> createReview(@RequestBody Review review) {
        return ResponseEntity.ok(reviewService.saveReview(review));
    }

    @GetMapping
    public ResponseEntity<List<Review>> getAllReviews() {
        return ResponseEntity.ok(reviewService.getAllReviews());
    }

    @PostMapping("/{id}/like")
    public ResponseEntity<Review> likeReview(@PathVariable Long id) {
        return ResponseEntity.ok(reviewService.likeReview(id));
    }
}

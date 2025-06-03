package io.metaverse.fashion.studio.service;

import io.metaverse.fashion.studio.entity.Review;
import io.metaverse.fashion.studio.repository.ReviewRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class ReviewService {
    @Autowired
    private ReviewRepository reviewRepository;

    public Review saveReview(Review review) {
        return reviewRepository.save(review);
    }

    public List<Review> getAllReviews() {
        return reviewRepository.findAll();
    }

    public Optional<Review> getReviewById(Long id) {
        return reviewRepository.findById(id);
    }

    public Review likeReview(Long id) {
        Review review = reviewRepository.findById(id).orElseThrow();
        review.setLikes(review.getLikes() + 1);
        return reviewRepository.save(review);
    }
}

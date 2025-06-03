package io.metaverse.fashion.studio.repository;

import io.metaverse.fashion.studio.entity.Review;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ReviewRepository extends JpaRepository<Review, Long> {
}

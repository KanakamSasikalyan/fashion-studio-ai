package io.metaverse.fashion.studio.repository;

import io.metaverse.fashion.studio.entity.ClothingDesign;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ClothingDesignRepository extends JpaRepository<ClothingDesign, Long> {
    @Query("SELECT d.imageUrl FROM ClothingDesign d")
    List<String> findAllImageUrls();
}
package io.metaverse.fashion.studio.repository;

import io.metaverse.fashion.studio.entity.ClothingDesign;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ClothingDesignRepository extends JpaRepository<ClothingDesign, Long> {
}
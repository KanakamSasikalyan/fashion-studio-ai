package io.metaverse.fashion.studio.repository;

import io.metaverse.fashion.studio.entity.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    List<Product> findByDescriptionContainingOrDisplayNameContainingOrCategoryContaining(String desc, String name, String category);
}

//package io.metaverse.fashion.studio.entity;
//// ProcessedImage.java - the functionality is not begin used in the application #removed - no more required
//
//import jakarta.persistence.*;
//import org.hibernate.annotations.CreationTimestamp;
//
//import java.time.LocalDateTime;
//
//@Entity
//@Table(name = "processed_images")
//public class ProcessedImage {
//    @Id
//    @GeneratedValue(strategy = GenerationType.IDENTITY)
//    private Long id;
//
//    @Column(nullable = false)
//    private String originalFilename;
//
//    @Column(nullable = false)
//    private String imageUrl;
//
//    @CreationTimestamp
//    private LocalDateTime createdAt;
//
//    public Long getId() {
//        return id;
//    }
//
//    public void setId(Long id) {
//        this.id = id;
//    }
//
//    public String getOriginalFilename() {
//        return originalFilename;
//    }
//
//    public void setOriginalFilename(String originalFilename) {
//        this.originalFilename = originalFilename;
//    }
//
//    public String getImageUrl() {
//        return imageUrl;
//    }
//
//    public void setImageUrl(String imageUrl) {
//        this.imageUrl = imageUrl;
//    }
//
//    public LocalDateTime getCreatedAt() {
//        return createdAt;
//    }
//
//    public void setCreatedAt(LocalDateTime createdAt) {
//        this.createdAt = createdAt;
//    }
//}
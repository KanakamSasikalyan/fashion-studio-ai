package io.metaverse.fashion.studio.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "clothing_designs")
public class ClothingDesign {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String prompt;
    private String style;
    private String gender; // Added gender field

    @Column(length = 2048) // Increased length for URL
    private String imageUrl; // Changed from byte[] to String

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getPrompt() { return prompt; }
    public void setPrompt(String prompt) { this.prompt = prompt; }
    public String getStyle() { return style; }
    public void setStyle(String style) { this.style = style; }
    public String getGender() { return gender; }
    public void setGender(String gender) { this.gender = gender; }
    public String getImageUrl() { return imageUrl; }
    public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }
}
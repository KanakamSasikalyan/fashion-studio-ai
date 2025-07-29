package io.metaverse.fashion.studio.controller;

import io.metaverse.fashion.studio.entity.Product;
import io.metaverse.fashion.studio.service.ProductService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/products")
@CrossOrigin(origins = "http://localhost:3000")
public class ProductController {

    @Autowired
    private ProductService productService;

    @GetMapping("/search")
    public List<Product> searchProducts(@RequestParam String query,
                                        @RequestParam(required = false) String gender) {
        return productService.searchProducts(query, gender);
    }
}
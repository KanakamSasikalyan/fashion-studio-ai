package io.metaverse.fashion.studio.service;

import io.metaverse.fashion.studio.entity.Product;
import io.metaverse.fashion.studio.repository.ClothingDesignRepository;
import io.metaverse.fashion.studio.repository.ProductRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class ProductService {

    private static final Logger logger = LoggerFactory.getLogger(ProductService.class);

    @Autowired
    private ProductRepository productRepository;

    private final String pythonScriptMatchProducts;

    ProductService(@Value("${python.script.matchPro}") String pythonScriptMatchProducts, ProductRepository productRepository){
        this.pythonScriptMatchProducts = pythonScriptMatchProducts;
        this.productRepository = productRepository;
    }

    public List<Product> searchProducts(String query, String gender) {
        logger.info("Starting product search with query: '{}' and gender: '{}'", query, gender);

        try {
            // Execute Python script
            //String pythonScriptPath = new ClassPathResource("python/match_products.py").getFile().getAbsolutePath();
            logger.debug("Python script path: {}", pythonScriptMatchProducts);

            ProcessBuilder pb = new ProcessBuilder(
                    "python",
                    pythonScriptMatchProducts,
                    query,
                    gender != null ? gender : ""
            );
            pb.redirectErrorStream(true);

            logger.debug("Starting Python process...");
            Process process = pb.start();

            // Read output from Python script
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            List<Product> results = new ArrayList<>();

            logger.debug("Reading Python script output...");
            while ((line = reader.readLine()) != null) {
                logger.debug("Python output: {}", line);

                if (line.startsWith("[LOG]")) {
                    // This is a log message from Python
                    logger.info("Python Log: {}", line.substring(5));
                } else {
                    // This is a product result
                    String[] parts = line.split("\\|\\|\\|");
                    System.out.println("Part 1: "+parts[0]);
                    System.out.println("Part 2: "+parts[1]);
                    System.out.println("Part 3: "+parts[2]);
                    System.out.println("Part 4: "+parts[3]);
                    if (parts.length >= 4) {
                        Product product = new Product();
                        product.setDisplayName(parts[0]);
                        product.setCategory(parts[1]);
                        product.setDescription(parts[2]);
                        product.setImageUrl("https://ik.imagekit.io/sp7ub8zm6/fashion_outfits/"+parts[3]);
                        results.add(product);
                    }
                }
            }

            int exitCode = process.waitFor();
            logger.debug("Python process exited with code: {}", exitCode);

            if (exitCode != 0) {
                logger.error("Python script execution failed with exit code: {}", exitCode);
                throw new RuntimeException("Python script execution failed");
            }

            logger.info("Product search completed. Found {} results.", results.size());
            return results;
        } catch (Exception e) {
            logger.error("Error during product search: ", e);
            return Collections.emptyList();
        }
    }
}
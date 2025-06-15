package io.metaverse.fashion.studio.service;

import io.metaverse.fashion.studio.entity.ClothingDesign;
import io.metaverse.fashion.studio.repository.ClothingDesignRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.http.codec.ServerSentEvent;
import reactor.core.publisher.Flux;
import reactor.core.publisher.FluxSink;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;

@Service
public class AIClothingService {

    Logger log = LoggerFactory.getLogger(AIClothingService.class);

    @Value("${ai.output.dir}")
    private String outputDir;

    private final String pythonScriptPath;
    private final ClothingDesignRepository clothingDesignRepository;

    @Autowired
    public AIClothingService(@Value("${python.script.path}") String pythonScriptPath, ClothingDesignRepository clothingDesignRepository) {
        this.pythonScriptPath = pythonScriptPath;
        this.clothingDesignRepository = clothingDesignRepository;
    }

    public List<String> getAllImageUrls() {
        return clothingDesignRepository.findAllImageUrls();
    }

    public List<ClothingDesign> getAllDesigns() {
        return clothingDesignRepository.findAll();
    }

    public ClothingDesign generateClothingDesign(String prompt, String style, String gender) throws IOException {
        Files.createDirectories(Paths.get(outputDir));

        ProcessBuilder pb = new ProcessBuilder(
                "python",
                pythonScriptPath,
                "\"" + prompt + "\"",
                style,
                gender,
                outputDir
        );

        pb.redirectErrorStream(true);
        Process process = pb.start();

        String imageUrl = null;

        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream()))) {

            String line;
            while ((line = reader.readLine()) != null) {
                if (line.startsWith("ERROR")) {
                    log.error("Python Error Output: {}", line);
                } else {
                    log.info("Python Output: {}", line);

                    if (line.startsWith("http")) {
                        imageUrl = line.trim();
                    }
                }
            }
        }

        ClothingDesign design = new ClothingDesign();
        design.setPrompt(prompt);
        design.setStyle(style);
        design.setGender(gender);
        design.setImageUrl(imageUrl);

        ClothingDesign savedDesign = clothingDesignRepository.save(design);
        log.info("Design successfully saved to database with ID: {}", savedDesign.getId());

        return design;
    }

    public Flux<ServerSentEvent<String>> generateClothingDesignStream(String prompt, String style, String gender) {
        return Flux.create(emitter -> {
            ExecutorService executor = Executors.newSingleThreadExecutor();
            executor.submit(() -> {
                try {
                    Files.createDirectories(Paths.get(outputDir));
                    ProcessBuilder pb = new ProcessBuilder(
                            "python",
                            pythonScriptPath,
                            "\"" + prompt + "\"",
                            style,
                            gender,
                            outputDir
                    );
                    pb.redirectErrorStream(true);
                    Process process = pb.start();
                    try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
                        String line;
                        String imageUrl = null;
                        while ((line = reader.readLine()) != null) {
                            log.info("Python Output Line: {}", line);
                            if (line.startsWith("PROGRESS:")) {
                                String percent = line.replace("PROGRESS:", "").trim();
                                emitter.next(ServerSentEvent.builder(percent).build());
                            } else if (line.startsWith("http")) {
                                imageUrl = line.trim();

                                log.info("Image generation completed...");
                                log.info("Trying to save the imageUrl into database...");

                                ClothingDesign design = new ClothingDesign();
                                int hashCode = prompt.hashCode();
                                String head = "ClothingDesign#"+String.valueOf(hashCode);
                                design.setPrompt(head);
                                design.setStyle(style);
                                design.setGender(gender);
                                design.setImageUrl(imageUrl);

                                log.debug("Attempting to save design to database");
                                ClothingDesign savedDesign = clothingDesignRepository.save(design);
                                log.info("Design successfully saved to database with ID: {}", savedDesign.getId());

                                emitter.next(ServerSentEvent.builder("COMPLETE:" + imageUrl).build());
                            } else if (line.startsWith("ERROR")) {
                                emitter.next(ServerSentEvent.builder("ERROR:" + line).build());
                            }
                        }
                        process.waitFor();
                    }
                    emitter.complete();
                } catch (Exception e) {
                    log.error("Error in generateClothingDesignStream", e);
                    emitter.next(ServerSentEvent.builder("ERROR:" + e.getMessage()).build());
                    emitter.complete();
                } finally {
                    executor.shutdown();
                    try {
                        if (!executor.awaitTermination(5, TimeUnit.SECONDS)) {
                            executor.shutdownNow();
                        }
                    } catch (InterruptedException e) {
                        executor.shutdownNow();
                    }
                }
            });
        }, FluxSink.OverflowStrategy.BUFFER);
    }
}
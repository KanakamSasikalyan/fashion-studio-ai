//package io.metaverse.fashion.studio.controller;
//
//import io.metaverse.fashion.studio.service.CamVirtualTryOnService;
//import org.springframework.http.MediaType;
//import org.springframework.http.ResponseEntity;
//import org.springframework.messaging.handler.annotation.MessageMapping;
//import org.springframework.messaging.simp.SimpMessagingTemplate;
//import org.springframework.stereotype.Controller;
//import org.springframework.web.bind.annotation.*;
//import org.springframework.web.multipart.MultipartFile;
//
//import java.io.IOException;
//import java.util.Map;
//
//@Controller
//@RequestMapping("/api/virtual-try-on")
//public class CamVirtualTryOnController {
//
//    private final CamVirtualTryOnService virtualTryOnService;
//    private final SimpMessagingTemplate messagingTemplate;
//
//    public CamVirtualTryOnController(CamVirtualTryOnService virtualTryOnService,
//                                     SimpMessagingTemplate messagingTemplate) {
//        this.virtualTryOnService = virtualTryOnService;
//        this.messagingTemplate = messagingTemplate;
//    }
//
//    @PostMapping(value = "/upload-cloth", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
//    @ResponseBody
//    public ResponseEntity<String> uploadClothImage(@RequestParam("file") MultipartFile file) {
//        try {
//            String imagePath = virtualTryOnService.saveClothImage(file);
//            virtualTryOnService.setCurrentClothImagePath(imagePath);
//            return ResponseEntity.ok("Cloth image uploaded successfully. Ready to start try-on.");
//        } catch (IOException e) {
//            return ResponseEntity.badRequest().body("Error processing cloth image: " + e.getMessage());
//        }
//    }
//
//    @PostMapping("/stop")
//    @ResponseBody
//    public ResponseEntity<String> stopVirtualTryOn() {
//        virtualTryOnService.stopVirtualTryOn();
//        virtualTryOnService.setCurrentClothImagePath(null);
//        return ResponseEntity.ok("Virtual try-on stopped.");
//    }
//
//    @MessageMapping("/process-frame")
//    public void processFrame(Map<String, String> payload) {
//        String base64Frame = payload.get("frame");
//        if (base64Frame == null || base64Frame.isEmpty()) {
//            messagingTemplate.convertAndSend("/topic/errors",
//                    Map.of("message", "Received empty frame data."));
//            return;
//        }
//
//        try {
//            String clothImagePath = virtualTryOnService.getCurrentClothImagePath();
//            if (clothImagePath == null) {
//                messagingTemplate.convertAndSend("/topic/errors",
//                        Map.of("message", "No cloth image uploaded. Please upload a cloth first."));
//                return;
//            }
//
//            // Process frame asynchronously
//            virtualTryOnService.processFrameAsync(base64Frame, clothImagePath, messagingTemplate);
//        } catch (Exception e) {
//            messagingTemplate.convertAndSend("/topic/errors",
//                    Map.of("message", "Error processing frame: " + e.getMessage()));
//            virtualTryOnService.stopVirtualTryOn();
//        }
//    }
//}
//
//
///*package io.metaverse.fashion.studio.controller;
//
//import io.metaverse.fashion.studio.service.CamVirtualTryOnService;
//import org.springframework.http.MediaType;
//import org.springframework.http.ResponseEntity;
//import org.springframework.messaging.simp.SimpMessagingTemplate;
//import org.springframework.web.bind.annotation.*;
//import org.springframework.web.multipart.MultipartFile;
//
//import java.io.IOException;
//
//@RestController
//@RequestMapping("/api/virtual-try-on")
//public class CamVirtualTryOnController {
//
//    private final CamVirtualTryOnService virtualTryOnService;
//    private final SimpMessagingTemplate messagingTemplate;
//
//    public CamVirtualTryOnController(CamVirtualTryOnService virtualTryOnService,
//                                     SimpMessagingTemplate messagingTemplate) {
//        this.virtualTryOnService = virtualTryOnService;
//        this.messagingTemplate = messagingTemplate;
//    }
//
//    @PostMapping(value = "/upload-cloth", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
//    public ResponseEntity<String> uploadClothImage(@RequestParam("file") MultipartFile file) {
//        try {
//            String imagePath = virtualTryOnService.saveClothImage(file);
//            virtualTryOnService.startVirtualTryOn(imagePath, messagingTemplate);
//            return ResponseEntity.ok("Virtual try-on started successfully");
//        } catch (IOException e) {
//            return ResponseEntity.badRequest().body("Error processing image: " + e.getMessage());
//        } catch (InterruptedException e) {
//            throw new RuntimeException(e);
//        }
//    }
//
//    @PostMapping("/stop")
//    public ResponseEntity<String> stopVirtualTryOn() {
//        virtualTryOnService.stopVirtualTryOn();
//        return ResponseEntity.ok("Virtual try-on stopped");
//    }
//}*/

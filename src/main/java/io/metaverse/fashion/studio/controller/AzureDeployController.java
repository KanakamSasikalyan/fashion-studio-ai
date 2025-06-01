package io.metaverse.fashion.studio.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AzureDeployController {

    @GetMapping("/azure-deploy")
    public String azureDeployTest(){
        return "Welcome, Fashion Studio Backend Deployed Successfully!";
    }
}

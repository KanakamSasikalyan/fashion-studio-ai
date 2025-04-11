package io.metaverse.fashion.studio.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.ClassPathResource;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.File;
import java.io.FileOutputStream;

@Configuration
public class PythonConfig {

    @Bean
    public String pythonScriptPath() throws IOException {
        ClassPathResource resource = new ClassPathResource("python/generate_clothing.py");
        File tempFile = File.createTempFile("generate_clothing", ".py");
        try (InputStream in = resource.getInputStream();
             OutputStream out = new FileOutputStream(tempFile)) {
            byte[] buffer = new byte[1024];
            int bytesRead;
            while ((bytesRead = in.read(buffer)) != -1) {
                out.write(buffer, 0, bytesRead);
            }
        }
        return tempFile.getAbsolutePath();
    }
}
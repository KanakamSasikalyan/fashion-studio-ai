package io.metaverse.fashion.studio.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.List;

@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .cors(Customizer.withDefaults()) // ✅ Enable CORS using the config below
                .csrf(csrf -> csrf.disable())    // Optional: Disable CSRF for APIs
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/api/**", "/virtual-try-on-websocket/**").permitAll() // Allow open access
                        .anyRequest().authenticated()
                );

        return http.build();
    }

    //allow the mentioned origin requests
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOriginPatterns(List.of(
                "http://localhost:3000",
                "http://localhost:8080",
                "https://ubc-fashion-studio-ai-frontend-container-efadeqfwfkfgg4dm.canadacentral-01.azurewebsites.net" // Add this line
        ));
        configuration.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(List.of("*"));
        configuration.setAllowCredentials(true); // ✅ Allows cookies and credentials

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        // ✅ Register CORS for both REST and WebSocket paths
        source.registerCorsConfiguration("/api/**", configuration);
        source.registerCorsConfiguration("/virtual-try-on-websocket/**", configuration);
        source.registerCorsConfiguration("/**", configuration); // Optional fallback

        return source;
    }
}

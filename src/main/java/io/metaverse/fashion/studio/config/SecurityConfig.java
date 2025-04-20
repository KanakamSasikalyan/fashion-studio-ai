//package io.metaverse.fashion.studio.config;
//
//import org.springframework.context.annotation.Bean;
//import org.springframework.context.annotation.Configuration;
//import org.springframework.security.config.annotation.web.builders.HttpSecurity;
//import org.springframework.security.web.SecurityFilterChain;
//import org.springframework.security.config.Customizer;
//
//@Configuration
//public class SecurityConfig {
//
//    @Bean
//    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
//        return http
//                .authorizeHttpRequests(auth -> auth
//                        .anyRequest().permitAll() // 👈 Allow all endpoints
//                )
//                .csrf(csrf -> csrf.disable()) // Disable CSRF (okay for APIs, but careful in prod)
//                .httpBasic(Customizer.withDefaults()) // Optional: enable basic auth if needed
//                .build();
//    }
//}

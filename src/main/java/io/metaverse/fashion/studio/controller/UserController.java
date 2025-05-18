package io.metaverse.fashion.studio.controller;

import io.metaverse.fashion.studio.entity.User;
import io.metaverse.fashion.studio.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/users")
public class UserController {

    @Autowired
    private UserService userService;

    @PostMapping("/signup")
    public ResponseEntity<User> signup(@RequestBody User user) {
        try {
            User newUser = userService.signupUser(user.getUsername(), user.getEmail(), user.getPassword());
            return ResponseEntity.ok(newUser);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(null);
        }
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestParam String username, @RequestParam String password) {
        boolean isAuthenticated = userService.loginUser(username, password);
        if (isAuthenticated) {
            return ResponseEntity.ok(Map.of("message", "Login successful", "user", username));
        } else {
            return ResponseEntity.status(401).body(Map.of("message", "Invalid username or password"));
        }
    }
}
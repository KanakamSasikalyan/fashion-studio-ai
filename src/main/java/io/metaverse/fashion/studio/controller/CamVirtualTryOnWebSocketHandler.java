package io.metaverse.fashion.studio.controller;

import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import java.io.IOException;

public class CamVirtualTryOnWebSocketHandler extends TextWebSocketHandler {

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws IOException {
        // Handle messages from frontend (like stop commands)
        String payload = message.getPayload();
        if ("stop".equalsIgnoreCase(payload)) {
            // Implement stop logic if needed
            session.sendMessage(new TextMessage("Stopping virtual try-on"));
        }
    }

    @Override
    public void afterConnectionEstablished(WebSocketSession session) throws Exception {
        // Send initial message when connection is established
        session.sendMessage(new TextMessage("Connected to virtual try-on service"));
    }
}

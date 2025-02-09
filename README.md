# Modern Chat App

## Description

The Modern Chat App is a real-time messaging application built using Python. It features a sleek, modern design with a simple user interface created with **Tkinter**. The app allows users to join a chat room, send and receive messages, and interact with others in real-time.

This project demonstrates the integration of **client-server architecture** using **WebSockets** for real-time communication. It also includes the option for users to add emojis to their messages and provides a layout similar to modern chat apps.

**Please note: This is a demo version, and the application is still under development.**

## Features

- **User Login**: Users can choose their username to join the chat room.
- **Real-time Messaging**: Messages are sent and received in real-time via WebSockets.
- **Emoji Picker**: Users can add emojis to their messages with an easy-to-use emoji picker.
- **User List**: Displays a list of users currently online in the chat room.
- **Modern UI**: The user interface is designed with a modern, minimalist aesthetic using the `ttkthemes` library.
- **Message History**: Chat messages are displayed with a timestamp and username, with custom styling for better readability.
- **Message System Notifications**: Displays system notifications like when a user joins or leaves the chat.

## Demo

### Client
- Built using **Tkinter** for the GUI and **asyncio** with **websockets** for asynchronous network communication.
- Users can join the chat by entering a username, which is then displayed in the chat room.
- Messages are exchanged in real-time between clients and the server.
- Users can see a list of online users and send messages with or without emojis.

### Server
- The server handles incoming WebSocket connections from clients.
- The server sends updates to clients when messages are sent or when users join/leave the chat room.

## Installation

To run the application locally, follow these steps:

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt

import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import asyncio
import websockets
import threading
import json
from datetime import datetime
from PIL import Image, ImageTk
import emoji
import ttkthemes

class ModernChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Chat App")
        
        # Apply modern theme with custom styles
        self.style = ttkthemes.ThemedStyle(root)
        self.style.set_theme("arc")
        
        # Custom styles
        self.style.configure("Card.TFrame", background="#ffffff", relief="raised", borderwidth=1)
        self.style.configure("Sidebar.TFrame", background="#f5f6f7")
        self.style.configure("Header.TLabel", font=("Helvetica", 14, "bold"), padding=10)
        self.style.configure("UserList.Treeview", rowheight=30, font=("Helvetica", 11))
        self.style.configure("ChatEntry.TEntry", padding=5)
        self.style.configure("SendButton.TButton", padding=5)
        
        # Window configuration
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Set background color
        self.root.configure(bg="#f0f2f5")
        
        # Create main container with padding and background
        self.main_container = ttk.Frame(root, style="Card.TFrame", padding=10)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create and configure the main layout
        self.create_layout()
        
        # Initialize variables
        self.username = None
        self.websocket = None
        self.users_online = set()
        self.message_history = []
        
        # Start connection
        self.login_dialog()
    
    def create_layout(self):
        # Create left sidebar
        self.create_sidebar()
        
        # Create right content area
        self.create_content_area()
    
    def create_sidebar(self):
        sidebar = ttk.Frame(self.main_container, style="Sidebar.TFrame", width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # App logo/header
        header_frame = ttk.Frame(sidebar)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        logo_label = ttk.Label(header_frame, text="💬", font=("Helvetica", 24))
        logo_label.pack(side=tk.LEFT, padx=10)
        
        app_name = ttk.Label(header_frame, text="ModernChat", style="Header.TLabel")
        app_name.pack(side=tk.LEFT)
        
        # Search box
        search_frame = ttk.Frame(sidebar)
        search_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.search_entry = ttk.Entry(search_frame, style="ChatEntry.TEntry")
        self.search_entry.pack(fill=tk.X)
        self.search_entry.insert(0, "🔍 Search users...")
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.delete(0, tk.END) if self.search_entry.get() == "🔍 Search users..." else None)
        self.search_entry.bind("<FocusOut>", lambda e: self.search_entry.insert(0, "🔍 Search users...") if not self.search_entry.get() else None)
        
        # Online users section
        users_header = ttk.Label(sidebar, text="Online Users", font=("Helvetica", 12, "bold"))
        users_header.pack(pady=10, padx=10, anchor="w")
        
        self.users_tree = ttk.Treeview(sidebar, show="tree", selectmode="browse", style="UserList.Treeview", height=20)
        self.users_tree.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Add scrollbar to users list
        users_scroll = ttk.Scrollbar(sidebar, orient="vertical", command=self.users_tree.yview)
        users_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.users_tree.configure(yscrollcommand=users_scroll.set)
    
    def create_content_area(self):
        content = ttk.Frame(self.main_container)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Chat header
        header = ttk.Frame(content, style="Card.TFrame")
        header.pack(fill=tk.X, pady=(0, 10))
        
        self.chat_header = ttk.Label(header, text="Chat Room", style="Header.TLabel")
        self.chat_header.pack(side=tk.LEFT, padx=10)
        
        # Chat area with custom styling
        chat_frame = ttk.Frame(content, style="Card.TFrame")
        chat_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chat_area = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Helvetica", 11),
            bg="#ffffff",
            fg="#000000",
            padx=10,
            pady=10
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure message styling
        self.chat_area.tag_configure("timestamp", foreground="#666666", font=("Helvetica", 9))
        self.chat_area.tag_configure("username", foreground="#2980b9", font=("Helvetica", 11, "bold"))
        self.chat_area.tag_configure("message", font=("Helvetica", 11))
        self.chat_area.tag_configure("system", foreground="#27ae60", font=("Helvetica", 11, "italic"))
        
        # Input area
        input_frame = ttk.Frame(content, style="Card.TFrame")
        input_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Message composition area
        compose_frame = ttk.Frame(input_frame)
        compose_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.msg_entry = ttk.Entry(
            compose_frame,
            style="ChatEntry.TEntry",
            font=("Helvetica", 11)
        )
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.msg_entry.bind("<Return>", self.send_message)
        
        # Buttons
        button_frame = ttk.Frame(compose_frame)
        button_frame.pack(side=tk.RIGHT)
        
        # Emoji button
        self.emoji_btn = ttk.Button(
            button_frame,
            text="😊",
            width=3,
            style="SendButton.TButton",
            command=self.show_emoji_picker
        )
        self.emoji_btn.pack(side=tk.LEFT, padx=5)
        
        # Attachment button
        self.attach_btn = ttk.Button(
            button_frame,
            text="📎",
            width=3,
            style="SendButton.TButton",
            command=self.show_attachment_dialog
        )
        self.attach_btn.pack(side=tk.LEFT, padx=5)
        
        # Send button
        self.send_btn = ttk.Button(
            button_frame,
            text="Send",
            style="SendButton.TButton",
            command=self.send_message
        )
        self.send_btn.pack(side=tk.LEFT)
    
    def login_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Welcome to ModernChat")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Style the dialog
        dialog.configure(bg="#ffffff")
        
        # Welcome message
        ttk.Label(
            dialog,
            text="💬",
            font=("Helvetica", 48)
        ).pack(pady=(20, 0))
        
        ttk.Label(
            dialog,
            text="Welcome to ModernChat",
            font=("Helvetica", 16, "bold")
        ).pack(pady=(10, 20))
        
        # Username entry
        entry_frame = ttk.Frame(dialog)
        entry_frame.pack(fill=tk.X, padx=50)
        
        ttk.Label(
            entry_frame,
            text="Choose your username:",
            font=("Helvetica", 11)
        ).pack(anchor="w")
        
        entry = ttk.Entry(entry_frame, font=("Helvetica", 11), style="ChatEntry.TEntry")
        entry.pack(fill=tk.X, pady=(5, 20))
        entry.focus()
        
        def submit():
            username = entry.get().strip()
            if username:
                self.username = username
                dialog.destroy()
                self.connect_to_server()
            else:
                messagebox.showerror("Error", "Username cannot be empty")
        
        # Join button
        ttk.Button(
            dialog,
            text="Join Chat",
            style="SendButton.TButton",
            command=submit
        ).pack(pady=10)
        
        entry.bind("<Return>", lambda e: submit())
    
    def show_emoji_picker(self):
        picker = tk.Toplevel(self.root)
        picker.title("Emoji Picker")
        picker.geometry("300x200")
        
        # Common emojis
        emojis = ["😊", "😂", "👍", "❤️", "😎", "🎉", "👋", "🔥", "✨", "🙌", 
                  "😄", "🎈", "🌟", "💡", "🚀", "💪", "👏", "🌈", "💫", "🎨"]
        
        def add_emoji(emoji_char):
            current = self.msg_entry.get()
            self.msg_entry.delete(0, tk.END)
            self.msg_entry.insert(0, current + emoji_char)
            picker.destroy()
        
        # Create scrollable frame for emojis
        canvas = tk.Canvas(picker)
        scrollbar = ttk.Scrollbar(picker, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add emojis to grid
        for i, emoji_char in enumerate(emojis):
            btn = ttk.Button(
                scrollable_frame,
                text=emoji_char,
                command=lambda e=emoji_char: add_emoji(e),
                width=3
            )
            btn.grid(row=i//5, column=i%5, padx=5, pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def show_attachment_dialog(self):
        messagebox.showinfo("Attachments", "File attachment feature coming soon!")
    
    def connect_to_server(self):
        threading.Thread(target=lambda: asyncio.run(self.start_client()), daemon=True).start()
    
    async def start_client(self):
        try:
            self.websocket = await websockets.connect(f"ws://localhost:8000/ws?username={self.username}")
            self.chat_header.config(text=f"Chat Room - Connected as {self.username}")
            
            # Display welcome message
            self.display_system_message(f"Welcome to the chat, {self.username}!")
            
            while True:
                try:
                    message = await self.websocket.recv()
                    data = json.loads(message)
                    
                    if data["type"] == "message":
                        self.display_message(data)
                    elif data["type"] == "user_list":
                        self.update_user_list(data["users"])
                    elif data["type"] == "user_joined":
                        self.display_system_message(f"{data['username']} joined the chat")
                    elif data["type"] == "user_left":
                        self.display_system_message(f"{data['username']} left the chat")
                        
                except websockets.ConnectionClosed:
                    break
                    
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
    
    def send_message(self, event=None):
        message = self.msg_entry.get().strip()
        if message and self.websocket:
            data = {
                "type": "message",
                "username": self.username,
                "content": message,
                "timestamp": datetime.now().strftime("%H:%M")
            }
            
            asyncio.run(self.websocket.send(json.dumps(data)))
            self.msg_entry.delete(0, tk.END)
    
    def display_message(self, data):
        self.chat_area.configure(state=tk.NORMAL)
        
        # Add timestamp
        self.chat_area.insert(tk.END, f"[{data['timestamp']}] ", "timestamp")
        
        # Add username
        self.chat_area.insert(tk.END, f"{data['username']}: ", "username")
        
        # Add message content
        self.chat_area.insert(tk.END, f"{data['content']}\n", "message")
        
        self.chat_area.configure(state=tk.DISABLED)
        self.chat_area.see(tk.END)
    
    def display_system_message(self, message):
        self.chat_area.configure(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"System: {message}\n", "system")
        self.chat_area.configure(state=tk.DISABLED)
        self.chat_area.see(tk.END)
    
    def update_user_list(self, users):
        self.users_tree.delete(*self.users_tree.get_children())
        for user in sorted(users):
            status = "🟢" if user == self.username else "⭐"
            status_icon = status + " " if user == self.username else "🟢 "
            self.users_tree.insert("", tk.END, text=f"{status_icon}{user}", tags=("current_user" if user == self.username else "other_user",))
            
        # Style the user list items
        self.users_tree.tag_configure("current_user", foreground="#2980b9")
        self.users_tree.tag_configure("other_user", foreground="#2c3e50")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernChatClient(root)
    root.mainloop()
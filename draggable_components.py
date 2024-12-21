import tkinter as tk
from tkinter import ttk

class ThumbnailFrame(ttk.Frame):
    def __init__(self, container, screenshot_app, index, **kwargs):
        super().__init__(container, **kwargs)
        self.screenshot_app = screenshot_app
        self.index = index
        self.selected = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.original_position = None
        
        # Configure styles for selection and drag feedback
        self.style = ttk.Style()
        self.style.configure("Selected.TFrame", background="lightblue")
        self.style.configure("Normal.TFrame", background="white")
        self.style.configure("Dragging.TFrame", background="lightgrey")
        
        # Apply initial style
        self.configure(style="Normal.TFrame")
        
        # Bind mouse events
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_drop)
        
        # Create placeholder for drag indication
        self.placeholder = None
        
    def on_click(self, event):
        """Handle mouse click event"""
        self.screenshot_app.select_thumbnail(self.index)
        # Store initial mouse position
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        # Store original grid position
        self.original_position = (self.grid_info()['row'], self.grid_info()['column'])
        
    def on_drag(self, event):
        """Handle drag event"""
        if not self.selected:
            return
            
        # Calculate distance moved
        dx = event.x_root - self.drag_start_x
        dy = event.y_root - self.drag_start_y
        
        # Only start drag if moved more than 5 pixels
        if abs(dx) < 5 and abs(dy) < 5:
            return
            
        # If first time dragging, create drag visual
        if not self.placeholder:
            self.start_drag()
            
        # Update position
        new_x = self.winfo_x() + dx
        new_y = self.winfo_y() + dy
        
        # Move the widget
        self.place(x=new_x, y=new_y)
        
        # Update start position for next drag
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        
        # Show drop location
        self.update_drop_indicator(event)
        
    def start_drag(self):
        """Initialize drag operation"""
        # Create placeholder where the widget was
        self.placeholder = ttk.Frame(self.master, style="Normal.TFrame")
        self.placeholder.grid(row=self.original_position[0], 
                            column=self.original_position[1],
                            padx=5, pady=5)
        
        # Lift dragged widget above others
        self.lift()
        self.configure(style="Dragging.TFrame")
        
    def update_drop_indicator(self, event):
        """Update visual indication of where item will be dropped"""
        # Get mouse position relative to thumbnail frame
        x = event.x_root - self.master.winfo_rootx()
        y = event.y_root - self.master.winfo_rooty()
        
        # Calculate grid position
        row = y // (self.winfo_height() + 10)
        col = x // (self.winfo_width() + 10)
        
        # Move placeholder to new position
        if self.placeholder:
            try:
                max_row = len(self.screenshot_app.screenshot_manager.screenshots) // self.screenshot_app.columns
                if 0 <= row <= max_row and 0 <= col < self.screenshot_app.columns:
                    self.placeholder.grid(row=row, column=col)
            except tk.TclError:
                pass  # Ignore errors from rapid movement
        
    def on_drop(self, event):
        """Handle drop event"""
        if not self.selected or not self.placeholder:
            return
            
        # Get drop coordinates relative to thumbnail frame
        x = event.x_root - self.master.winfo_rootx()
        y = event.y_root - self.master.winfo_rooty()
        
        # Calculate new position
        new_row = y // (self.winfo_height() + 10)
        new_col = x // (self.winfo_width() + 10)
        
        # Calculate new index
        new_index = new_row * self.screenshot_app.columns + new_col
        
        # Clean up drag visuals
        self.end_drag()
        
        # Reorder if position changed
        if new_index != self.index:
            # Ensure new_index is within bounds
            max_index = len(self.screenshot_app.screenshot_manager.screenshots)
            new_index = max(0, min(new_index, max_index))
            
            self.screenshot_app.screenshot_manager.reorder_screenshots(self.index, new_index)
            self.screenshot_app.selected_thumbnail = new_index
            self.screenshot_app.update_thumbnails()
            
    def end_drag(self):
        """Clean up after drag operation"""
        # Remove placeholder
        if self.placeholder:
            self.placeholder.destroy()
            self.placeholder = None
        
        # Reset widget state
        self.place_forget()
        self.grid(row=self.original_position[0], 
                 column=self.original_position[1],
                 padx=5, pady=5)
        self.configure(style="Selected.TFrame" if self.selected else "Normal.TFrame")
        
    def set_selected(self, selected):
        """Update selection state"""
        self.selected = selected
        self.configure(style="Selected.TFrame" if selected else "Normal.TFrame")
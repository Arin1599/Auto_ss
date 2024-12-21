import tkinter as tk
from tkinter import ttk, filedialog
import keyboard
import threading
from PIL import Image, ImageTk
from draggable_components import ThumbnailFrame
from settings_manager import SettingsManager
from screenshot_manager import ScreenshotManager

class ScreenshotToPDF:
    def __init__(self):
        self.is_running = True
        self.settings_manager = SettingsManager()
        self.screenshot_manager = ScreenshotManager()
        self.selected_thumbnail = None
        self.columns = 5
        self.dragged_widget = None
        
        self.init_gui()
        self.keyboard_thread = threading.Thread(target=self.keyboard_listener, daemon=True)
        self.keyboard_thread.start()

    def init_gui(self):
        self.root = tk.Tk()
        self.root.title("Screenshot to PDF")
        self.root.geometry("800x600")

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self._init_shortcuts_frame(main_frame)
        self._init_options_frame(main_frame)
        self._init_screenshots_frame(main_frame)
        self._init_button_frame(main_frame)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Bind keyboard shortcuts
        self.root.bind("<Left>", self.move_thumbnail_left)
        self.root.bind("<Right>", self.move_thumbnail_right)
        self.root.bind("<Up>", self.move_thumbnail_up)
        self.root.bind("<Down>", self.move_thumbnail_down)
        self.root.bind("<Delete>", self.delete_selected)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _init_shortcuts_frame(self, parent):
        shortcuts_frame = ttk.LabelFrame(parent, text="Keyboard Shortcuts", padding="5")
        shortcuts_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        shortcuts = self.settings_manager.get_setting('shortcuts')
        ttk.Label(shortcuts_frame, text=f"Take Screenshot: {shortcuts['take_screenshot']}").grid(row=0, column=0, padx=5)
        ttk.Label(shortcuts_frame, text=f"Save PDF: {shortcuts['save_pdf']}").grid(row=0, column=1, padx=5)
        ttk.Label(shortcuts_frame, text=f"Exit: {shortcuts['exit']}").grid(row=0, column=2, padx=5)

    def _init_options_frame(self, parent):
        self.compress_var = tk.BooleanVar(value=self.settings_manager.get_setting('compress', False))
        compression_frame = ttk.LabelFrame(parent, text="Options", padding="5")
        compression_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Checkbutton(
            compression_frame,
            text="Compress Screenshots",
            variable=self.compress_var,
            command=lambda: self.settings_manager.update_setting('compress', self.compress_var.get())
        ).grid(row=0, column=0, padx=5)

    def _init_screenshots_frame(self, parent):
        list_frame = ttk.LabelFrame(parent, text="Screenshots", padding="5")
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        self.canvas = tk.Canvas(list_frame)
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=v_scrollbar.set)

        self.thumbnail_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.thumbnail_frame, anchor=tk.NW)

        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Bind events for drag and drop
        self.thumbnail_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)

    def _init_button_frame(self, parent):
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, columnspan=2, pady=5)

        ttk.Button(button_frame, text="Take Screenshot", command=self.take_screenshot).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Save PDF", command=self.save_pdf).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Clear All", command=self.clear_screenshots).grid(row=0, column=2, padx=5)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        # Update canvas width when window is resized
        width = event.width
        self.canvas.itemconfig(self.canvas_window, width=width)
        self.columns = max(1, (width - 20) // 170)  # 170 = thumbnail width (150) + padding
        self.update_thumbnails()

    def select_thumbnail(self, index):
        if self.selected_thumbnail == index:
            return

        # Deselect previous
        if self.selected_thumbnail is not None:
            old_frame = self.get_thumbnail_frame(self.selected_thumbnail)
            if old_frame:
                old_frame.set_selected(False)

        # Select new
        self.selected_thumbnail = index
        new_frame = self.get_thumbnail_frame(index)
        if new_frame:
            new_frame.set_selected(True)

    def get_thumbnail_frame(self, index):
        for widget in self.thumbnail_frame.winfo_children():
            if isinstance(widget, ThumbnailFrame) and widget.index == index:
                return widget
        return None

    def move_thumbnail_left(self, event):
        if self.selected_thumbnail is not None and self.selected_thumbnail > 0:
            self.screenshot_manager.reorder_screenshots(self.selected_thumbnail, self.selected_thumbnail - 1)
            self.selected_thumbnail -= 1
            self.update_thumbnails()

    def move_thumbnail_right(self, event):
        if (self.selected_thumbnail is not None and 
            self.selected_thumbnail < len(self.screenshot_manager.screenshots) - 1):
            self.screenshot_manager.reorder_screenshots(self.selected_thumbnail, self.selected_thumbnail + 1)
            self.selected_thumbnail += 1
            self.update_thumbnails()

    def move_thumbnail_up(self, event):
        if self.selected_thumbnail is not None and self.selected_thumbnail >= self.columns:
            new_index = self.selected_thumbnail - self.columns
            self.screenshot_manager.reorder_screenshots(self.selected_thumbnail, new_index)
            self.selected_thumbnail = new_index
            self.update_thumbnails()

    def move_thumbnail_down(self, event):
        if (self.selected_thumbnail is not None and 
            self.selected_thumbnail + self.columns < len(self.screenshot_manager.screenshots)):
            new_index = self.selected_thumbnail + self.columns
            self.screenshot_manager.reorder_screenshots(self.selected_thumbnail, new_index)
            self.selected_thumbnail = new_index
            self.update_thumbnails()

    def delete_selected(self, event):
        if self.selected_thumbnail is not None:
            self.remove_screenshot(self.selected_thumbnail)
            self.selected_thumbnail = None

    def take_screenshot(self):
        try:
            self.screenshot_manager.take_screenshot(
                compress=self.compress_var.get(),
                quality=self.settings_manager.get_setting('quality', 95)
            )
            self.update_thumbnails()
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to take screenshot: {str(e)}")

    def save_pdf(self):
        if not self.screenshot_manager.screenshots:
            tk.messagebox.showwarning("Warning", "No screenshots to save!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if file_path:
            try:
                self.screenshot_manager.create_pdf(file_path)
                tk.messagebox.showinfo("Success", "PDF saved successfully!")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to save PDF: {str(e)}")

    def update_thumbnails(self):
        if hasattr(self, '_updating'):
            return
        self._updating = True
        
        try:
            for widget in self.thumbnail_frame.winfo_children():
                widget.destroy()

            for i, screenshot in enumerate(self.screenshot_manager.screenshots):
                frame = ThumbnailFrame(self.thumbnail_frame, self, i)
                row = i // self.columns
                col = i % self.columns
                frame.grid(row=row, column=col, padx=5, pady=5)

                if i == self.selected_thumbnail:
                    frame.set_selected(True)

                serial_num = self.screenshot_manager.serial_numbers[i]
                serial_label = ttk.Label(frame, text=f"#{serial_num}")
                serial_label.grid(row=0, column=0, sticky="nw", padx=2, pady=2)

                label = ttk.Label(frame)
                label.configure(image=screenshot['thumbnail'])
                label.image = screenshot['thumbnail']
                label.grid(row=1, column=0, padx=2, pady=2)

                remove_btn = ttk.Button(frame, text="Remove",
                                      command=lambda idx=i: self.remove_screenshot(idx))
                remove_btn.grid(row=2, column=0, pady=2)

            self.thumbnail_frame.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        finally:
            delattr(self, '_updating')

    def remove_screenshot(self, index):
        if hasattr(self, '_updating'):
            return
        
        self.screenshot_manager.remove_screenshot(index)
        if self.selected_thumbnail is not None:
            if index < self.selected_thumbnail:
                self.selected_thumbnail -= 1
            elif index == self.selected_thumbnail:
                self.selected_thumbnail = None
        self.update_thumbnails()

    def clear_screenshots(self):
        if tk.messagebox.askyesno("Confirm", "Are you sure you want to clear all screenshots?"):
            self.screenshot_manager.clear_screenshots()
            self.selected_thumbnail = None
            self.update_thumbnails()

    def keyboard_listener(self):
        shortcuts = self.settings_manager.get_setting('shortcuts')
        
        keyboard.add_hotkey(shortcuts['take_screenshot'], 
                          lambda: self.root.after(0, self.take_screenshot))
        keyboard.add_hotkey(shortcuts['save_pdf'], 
                          lambda: self.root.after(0, self.save_pdf))
        keyboard.add_hotkey(shortcuts['exit'], 
                          lambda: self.root.after(0, self.on_closing))

    def on_closing(self):
        if tk.messagebox.askyesno("Quit", "Do you want to quit?"):
            self.is_running = False
            self.clear_screenshots()
            self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ScreenshotToPDF()
    app.run()
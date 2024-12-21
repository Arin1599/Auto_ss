# Auto_ss

Auto_ss is a GUI-based Python application that allows users to capture screenshots, manage them via a thumbnail interface, and save them as a single PDF file. The project is designed to be user-friendly and highly customizable, making it suitable for personal and professional use. This is very handy for students who need to take screenshots of their work and save them as a PDF.

---

## Features

### 1. **Take Screenshots**
- Capture screenshots using customizable keyboard shortcuts.
- Option to compress screenshots for optimized file size.

### 2. **Manage Screenshots**
- View screenshots in a grid layout with draggable thumbnails.
- Reorder thumbnails using arrow keys or drag-and-drop.
- Select, delete, or clear all screenshots.

### 3. **Save as PDF**
- Combine selected screenshots into a single PDF file.
- Customizable quality settings for PDF creation.

### 4. **Keyboard Shortcuts**
- Quickly take screenshots, save PDFs, or exit the application using hotkeys.

---

## Dependencies

### Required Python Libraries
- **Tkinter**: For creating the graphical user interface.
- **Pillow**: For handling image processing and thumbnails.
- **Keyboard**: For capturing global keyboard shortcuts.
- **Draggable Components**: For drag-and-drop functionality (custom module).
- **Settings Manager**: For managing user preferences (custom module).
- **Screenshot Manager**: For screenshot handling and PDF creation (custom module).

Install dependencies using `pip`:
```bash
pip install pillow keyboard
```

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Arin1599/Auto_ss.git
   cd Auto_ss
   ```

2. Install required libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

---

## Usage

### **Launching the Application**
Run the script `app.py` to launch the GUI.

### **Keyboard Shortcuts**
Customize the shortcuts in `settings_manager.py`:
- **Take Screenshot**: `Ctrl+Shift+S`
- **Save PDF**: `Ctrl+Shift+P`
- **Exit Application**: `Ctrl+Shift+Q`

### **Taking Screenshots**
- Press the `Take Screenshot` button or use the assigned keyboard shortcut.
- Screenshots appear as thumbnails in the "Screenshots" section.

### **Reordering Thumbnails**
- Use arrow keys or drag and drop the thumbnails to reorder them.

### **Saving as PDF**
- Click the `Save PDF` button or use the assigned shortcut.
- Choose a destination and filename to save the PDF.

### **Clearing Screenshots**
- Click the `Clear All` button to remove all screenshots.

---

## Project Structure

```
ScreenshotToPDF/
├── draggable_components.py  # Handles drag-and-drop functionality for thumbnails.
├── settings_manager.py      # Manages application settings like shortcuts and compression.
├── screenshot_manager.py    # Handles screenshot capturing and PDF creation.
├── app.py                   # Main application logic.
├── README.md                # Project documentation.
└── requirements.txt         # Python dependencies.
```

---

## Customization

### **Settings**
Update `settings_manager.py` for:
- Keyboard shortcuts
- Compression preferences
- Screenshot quality settings

### **UI Layout**
Modify `app.py` for customizing the GUI layout or adding new features.

---

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Submit a pull request.

---



## Acknowledgments

- Inspired by the need for a simple screenshot-to-PDF tool.
- Special thanks to the Python community for the amazing libraries.
- Used Gen AI to get around the coding and limitations of the project.

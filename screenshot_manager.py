import os
from datetime import datetime
import pyautogui
from PIL import Image, ImageTk
from fpdf import FPDF
import tkinter as tk

class ScreenshotManager:
    def __init__(self, temp_dir="temp_screenshots"):
        self.temp_dir = temp_dir
        self.screenshots = []
        self.serial_numbers = []
        self.next_serial = 1
        
        # Create temp directory if it doesn't exist
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        else:
            # Clean up any existing files
            self.cleanup_temp_files()

    def cleanup_temp_files(self):
        """Clean up any leftover temporary files"""
        try:
            for filename in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
        except Exception as e:
            print(f"Error cleaning temp directory: {e}")

    def take_screenshot(self, compress=False, quality=95):
        """
        Take a screenshot and save it to temp directory
        
        Args:
            compress (bool): Whether to compress the image
            quality (int): JPEG quality if compressing (1-100)
            
        Returns:
            int: Index of the new screenshot
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.temp_dir}/screenshot_{timestamp}.png"

            # Take screenshot
            screenshot = pyautogui.screenshot()
            
            # Process image based on settings
            if compress:
                screenshot = screenshot.convert('RGB')
                filename = filename.replace('.png', '.jpg')
                
            # Save screenshot
            screenshot.save(filename, quality=quality if compress else 95)

            # Create thumbnail
            thumbnail = screenshot.copy()
            thumbnail.thumbnail((150, 150))  # Fixed thumbnail size
            photo = ImageTk.PhotoImage(thumbnail)

            # Store screenshot info
            self.screenshots.append({
                'path': filename,
                'thumbnail': photo,
                'photo_ref': photo,
                'timestamp': timestamp
            })
            
            # Assign serial number
            self.serial_numbers.append(self.next_serial)
            self.next_serial += 1

            return len(self.screenshots) - 1

        except Exception as e:
            raise Exception(f"Failed to take screenshot: {str(e)}")

    def remove_screenshot(self, index):
        """
        Remove a screenshot at the specified index
        
        Args:
            index (int): Index of screenshot to remove
        """
        if 0 <= index < len(self.screenshots):
            try:
                # Delete file
                if os.path.exists(self.screenshots[index]['path']):
                    os.remove(self.screenshots[index]['path'])
                
                # Remove from lists
                del self.screenshots[index]
                del self.serial_numbers[index]
                
            except Exception as e:
                raise Exception(f"Failed to remove screenshot: {str(e)}")

    def clear_screenshots(self):
        """Remove all screenshots"""
        try:
            # Delete all files
            for screenshot in self.screenshots:
                try:
                    if os.path.exists(screenshot['path']):
                        os.remove(screenshot['path'])
                except OSError as e:
                    print(f"Error deleting file {screenshot['path']}: {e}")
            
            # Clear lists
            self.screenshots.clear()
            self.serial_numbers.clear()
            self.next_serial = 1
            
        except Exception as e:
            raise Exception(f"Failed to clear screenshots: {str(e)}")

    def create_pdf(self, file_path):
        """
        Create a PDF from screenshots with two images per page
        
        Args:
            file_path (str): Path where to save the PDF
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.screenshots:
            return False

        try:
            pdf = FPDF()
            
            # A4 dimensions in mm
            page_width = 210
            page_height = 297
            margin = 10
            
            # Calculate usable width and spacing
            usable_width = page_width - (2 * margin)
            image_width = usable_width
            spacing = 10  # Space between images
            
            # Process screenshots two at a time
            for i in range(0, len(self.screenshots), 2):
                pdf.add_page()
                
                # First image
                img1_path = self.screenshots[i]['path']
                img1 = Image.open(img1_path)
                aspect1 = img1.size[1] / img1.size[0]
                
                # Calculate height for first image (using 40% of page height)
                img1_height = min(image_width * aspect1, page_height * 0.4)
                
                # Add first image
                pdf.image(
                    img1_path,
                    x=margin,
                    y=margin,
                    w=image_width,
                    h=img1_height
                )
                
                # Add timestamp for first image
                pdf.set_font('Arial', 'I', 8)
                timestamp1 = datetime.strptime(self.screenshots[i]['timestamp'], "%Y%m%d_%H%M%S")
                formatted_time1 = timestamp1.strftime("%Y-%m-%d %H:%M:%S")
                pdf.text(margin, margin + img1_height + 5, f"Taken: {formatted_time1}")
                
                # Second image if available
                if i + 1 < len(self.screenshots):
                    img2_path = self.screenshots[i + 1]['path']
                    img2 = Image.open(img2_path)
                    aspect2 = img2.size[1] / img2.size[0]
                    
                    # Calculate height for second image (using 40% of page height)
                    img2_height = min(image_width * aspect2, page_height * 0.4)
                    
                    # Calculate Y position for second image
                    y2 = margin + img1_height + spacing + 10  # Add extra 10mm for timestamp
                    
                    # Add second image
                    pdf.image(
                        img2_path,
                        x=margin,
                        y=y2,
                        w=image_width,
                        h=img2_height
                    )
                    
                    # Add timestamp for second image
                    timestamp2 = datetime.strptime(self.screenshots[i + 1]['timestamp'], "%Y%m%d_%H%M%S")
                    formatted_time2 = timestamp2.strftime("%Y-%m-%d %H:%M:%S")
                    pdf.text(margin, y2 + img2_height + 5, f"Taken: {formatted_time2}")
                
                # Add page number
                pdf.set_font('Arial', 'I', 8)
                pdf.text(page_width - margin - 20, page_height - margin, 
                        f'Page {pdf.page_no()}')

            pdf.output(file_path)
            return True
            
        except Exception as e:
            raise Exception(f"Failed to create PDF: {str(e)}")

    def reorder_screenshots(self, old_index, new_index):
        """
        Reorder screenshots by moving one from old_index to new_index
        
        Args:
            old_index (int): Current index of screenshot
            new_index (int): New index for screenshot
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not (0 <= old_index < len(self.screenshots) and 
                0 <= new_index <= len(self.screenshots)):
            return False
            
        try:
            # Adjust new_index if moving forward
            if new_index > old_index:
                new_index -= 1
                
            # Move items
            screenshot = self.screenshots.pop(old_index)
            serial_num = self.serial_numbers.pop(old_index)
            
            self.screenshots.insert(new_index, screenshot)
            self.serial_numbers.insert(new_index, serial_num)
            
            return True
            
        except Exception as e:
            print(f"Error reordering screenshots: {e}")
            return False

    def get_screenshot_info(self, index):
        """
        Get information about a screenshot
        
        Args:
            index (int): Index of screenshot
            
        Returns:
            dict: Screenshot information or None if invalid index
        """
        if 0 <= index < len(self.screenshots):
            screenshot = self.screenshots[index]
            return {
                'path': screenshot['path'],
                'timestamp': screenshot['timestamp'],
                'serial_number': self.serial_numbers[index]
            }
        return None

    def __len__(self):
        """Return number of screenshots"""
        return len(self.screenshots)

    def __del__(self):
        """Cleanup on deletion"""
        self.cleanup_temp_files()
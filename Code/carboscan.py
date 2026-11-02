import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import cv2
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
import requests
import time
from datetime import datetime
import json
import os
import threading


class CarboScanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CarboScan Vision - Diabetes Management")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f0f0f0")
        
        
        self.cap = None
        self.is_scanning = False
        self.detection_in_progress = False
        self.carb_target = 45  
        self.camera_index = 0
        self.daily_carbs = 0
        self.scan_history = []
        self.load_data()
        

        self.create_widgets()
        
        self.start_camera()
        
    def create_widgets(self):
   
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_panel = tk.Frame(main_frame, bg="white", relief=tk.RIDGE, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        camera_title = tk.Label(left_panel, text="📷 Live Camera Feed", 
                               font=("Arial", 16, "bold"), bg="white", fg="#2c3e50")
        camera_title.pack(pady=10)
        
        self.canvas = tk.Canvas(left_panel, width=800, height=600, bg="black")
        self.canvas.pack(padx=10, pady=5)
        
        button_frame = tk.Frame(left_panel, bg="white")
        button_frame.pack(pady=10)
        
        self.scan_button = tk.Button(button_frame, text="🔍 Start Scanning", 
                                     command=self.toggle_scanning,
                                     font=("Arial", 12, "bold"),
                                     bg="#27ae60", fg="white",
                                     width=15, height=2,
                                     cursor="hand2")
        self.scan_button.pack(side=tk.LEFT, padx=5)
        
        settings_button = tk.Button(button_frame, text="⚙️ Settings", 
                                   command=self.open_settings,
                                   font=("Arial", 12),
                                   bg="#3498db", fg="white",
                                   width=12, height=2,
                                   cursor="hand2")
        settings_button.pack(side=tk.LEFT, padx=5)
        
        right_panel = tk.Frame(main_frame, bg="white", relief=tk.RIDGE, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.create_carb_counter(right_panel)
        
        self.create_scan_info_panel(right_panel)
        
        self.create_history_panel(right_panel)
        
    def create_carb_counter(self, parent):
        counter_frame = tk.LabelFrame(parent, text="📊 Daily Carb Tracker", 
                                     font=("Arial", 14, "bold"),
                                     bg="white", fg="#2c3e50", relief=tk.RIDGE, bd=2)
        counter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.carb_label = tk.Label(counter_frame, text=f"{self.daily_carbs}g", 
                                   font=("Arial", 36, "bold"),
                                   bg="white", fg="#e74c3c")
        self.carb_label.pack(pady=10)
        
        subtitle = tk.Label(counter_frame, text="Total Carbs Today", 
                           font=("Arial", 10),
                           bg="white", fg="#7f8c8d")
        subtitle.pack()
        
        reset_button = tk.Button(counter_frame, text="🔄 Reset Daily Counter", 
                                command=self.reset_daily_carbs,
                                font=("Arial", 9),
                                bg="#95a5a6", fg="white",
                                cursor="hand2")
        reset_button.pack(pady=5)
        
    def create_scan_info_panel(self, parent):
        info_frame = tk.LabelFrame(parent, text="📦 Last Scanned Product", 
                                  font=("Arial", 14, "bold"),
                                  bg="white", fg="#2c3e50", relief=tk.RIDGE, bd=2)
        info_frame.pack(fill=tk.BOTH, padx=10, pady=10)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=12, 
                                                   font=("Courier", 10),
                                                   bg="#ecf0f1", fg="#2c3e50",
                                                   wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.info_text.insert("1.0", "No product scanned yet.\n\nPlace a barcode in front of the camera and click 'Start Scanning'.")
        self.info_text.config(state=tk.DISABLED)
        
    def create_history_panel(self, parent):
        history_frame = tk.LabelFrame(parent, text="📋 Scan History (Today)", 
                                     font=("Arial", 14, "bold"),
                                     bg="white", fg="#2c3e50", relief=tk.RIDGE, bd=2)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview for history
        columns = ("Time", "Product", "Carbs", "Level")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, 
                                        show="headings", height=10)
        
        self.history_tree.heading("Time", text="Time")
        self.history_tree.heading("Product", text="Product")
        self.history_tree.heading("Carbs", text="Carbs/100g")
        self.history_tree.heading("Level", text="Level")
        
        self.history_tree.column("Time", width=80)
        self.history_tree.column("Product", width=200)
        self.history_tree.column("Carbs", width=80)
        self.history_tree.column("Level", width=80)
        
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, 
                                 command=self.history_tree.yview)
        self.history_tree.configure(yscroll=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.refresh_history()
        
    def start_camera(self):
        """Initialize camera"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.update_camera_feed()
        except Exception as e:
            messagebox.showerror("Camera Error", f"Failed to open camera: {str(e)}")
            
    def update_camera_feed(self):
        """Update camera feed continuously"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                
                if self.is_scanning and not self.detection_in_progress:
                    x1, y1 = w // 4, h // 4
                    x2, y2 = 3 * w // 4, 3 * h // 4
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    cv2.putText(frame, "Place barcode here", (x1 + 20, y1 - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    if not self.detection_in_progress:
                        roi = frame[y1:y2, x1:x2]
                        threading.Thread(target=self.scan_barcode, 
                                       args=(roi.copy(),), daemon=True).start()
                
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_resized = cv2.resize(frame_rgb, (800, 600))
                img = Image.fromarray(frame_resized)
                imgtk = ImageTk.PhotoImage(image=img)
                
                self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
                self.canvas.imgtk = imgtk
                
        self.root.after(30, self.update_camera_feed)
        
    def scan_barcode(self, roi):
        """Scan barcode in ROI (runs in thread)"""
        if self.detection_in_progress:
            return
            
        self.detection_in_progress = True
        
        try:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY, 11, 2)
            
            barcodes = decode(gray)
            
            for b in barcodes:
                code = b.data.decode("utf-8")
                self.process_barcode(code)
                break 
                
        except Exception as e:
            print(f"Scan error: {e}")
        finally:
            self.detection_in_progress = False
            
    def process_barcode(self, code):
        """Process detected barcode"""
        
        try:
            import winsound
            winsound.Beep(1200, 200)
        except:
            print("\a") 
            
        info = self.get_food_info(code)
        
        if not info:
            self.root.after(0, lambda: messagebox.showwarning(
                "Product Not Found", 
                f"Barcode {code} not found in OpenFoodFacts database."))
            return
            
        level, max_qty, color = self.classify_food(info["carbs"])
        
        self.root.after(0, lambda: self.display_product_info(info, level, max_qty, color))
        
        self.add_to_history(info, level)

        self.root.after(0, self.toggle_scanning)
        
    def get_food_info(self, barcode):
        """Get product info from OpenFoodFacts"""
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                return None
            data = r.json()
            if data.get("status") != 1:
                return None
            p = data["product"]
            return {
                "barcode": barcode,
                "name": p.get("product_name", "N/A"),
                "brand": p.get("brands", "N/A"),
                "carbs": p.get("nutriments", {}).get("carbohydrates_100g", "N/A"),
                "sugars": p.get("nutriments", {}).get("sugars_100g", "N/A"),
            }
        except:
            return None
            
    def classify_food(self, carbs_per_100g):
        """Classify food based on carb content"""
        if carbs_per_100g == "N/A":
            return "UNKNOWN", None, "#95a5a6"
        
        carbs = float(carbs_per_100g)
        
        if carbs <= 10:
            return "LOW", round((self.carb_target / carbs) * 100, 1), "#27ae60"
        elif carbs <= 20:
            return "MEDIUM", round((self.carb_target / carbs) * 100, 1), "#f39c12"
        else:
            return "HIGH", round((self.carb_target / carbs) * 100, 1), "#e74c3c"
            
    def display_product_info(self, info, level, max_qty, color):
        """Display product info in the panel"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete("1.0", tk.END)
        
        text = f"""
✅ PRODUCT DETECTED
{'─' * 40}

📦 Name:     {info['name']}
🏷️  Brand:    {info['brand']}
🍞 Carbs:    {info['carbs']} g / 100g
🍬 Sugars:   {info['sugars']} g / 100g

{'─' * 40}
📊 CLASSIFICATION
{'─' * 40}

Level:  {level}
Target: {self.carb_target}g carbs per meal

{'─' * 40}
💡 RECOMMENDATION
{'─' * 40}

Maximum portion size for {self.carb_target}g carbs:
➜ {max_qty} g

{'─' * 40}
        """
        
        self.info_text.insert("1.0", text)
        self.info_text.config(state=tk.DISABLED)
        
        messagebox.showinfo("Product Scanned", 
                          f"✅ {info['name']}\n\n"
                          f"Level: {level}\n"
                          f"Max portion: {max_qty}g for {self.carb_target}g carbs")
        
    def add_to_history(self, info, level):
        """Add scan to history"""
        now = datetime.now()
        
        entry = {
            "timestamp": now.strftime("%H:%M:%S"),
            "date": now.strftime("%Y-%m-%d"),
            "product": info["name"],
            "brand": info["brand"],
            "carbs": info["carbs"],
            "level": level
        }
        
        self.scan_history.append(entry)
        self.save_data()
        self.refresh_history()
        
    def refresh_history(self):
        """Refresh history treeview"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            

        today = datetime.now().strftime("%Y-%m-%d")
        for entry in reversed(self.scan_history):
            if entry["date"] == today:
                self.history_tree.insert("", 0, values=(
                    entry["timestamp"],
                    entry["product"][:30],  # Truncate long names
                    f"{entry['carbs']}g",
                    entry["level"]
                ))
                
    def toggle_scanning(self):
        """Toggle scanning mode"""
        self.is_scanning = not self.is_scanning
        
        if self.is_scanning:
            self.scan_button.config(text="⏹️ Stop Scanning", bg="#e74c3c")
        else:
            self.scan_button.config(text="🔍 Start Scanning", bg="#27ae60")
            
    def reset_daily_carbs(self):
        """Reset daily carb counter"""
        if messagebox.askyesno("Reset Counter", 
                              "Are you sure you want to reset the daily carb counter?"):
            self.daily_carbs = 0
            self.carb_label.config(text=f"{self.daily_carbs}g")
            self.save_data()
            
    def open_settings(self):
        """Open settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg="white")
        
        tk.Label(settings_window, text="Carb Target per Meal (g):", 
                font=("Arial", 12), bg="white").pack(pady=20)
        
        carb_var = tk.IntVar(value=self.carb_target)
        carb_spinbox = tk.Spinbox(settings_window, from_=10, to=100, 
                                  textvariable=carb_var,
                                  font=("Arial", 14), width=10)
        carb_spinbox.pack()
        

        tk.Label(settings_window, text="Camera Index:", 
                font=("Arial", 12), bg="white").pack(pady=20)
        
        camera_var = tk.IntVar(value=self.camera_index)
        camera_spinbox = tk.Spinbox(settings_window, from_=0, to=5, 
                                    textvariable=camera_var,
                                    font=("Arial", 14), width=10)
        camera_spinbox.pack()
        
        def save_settings():
            self.carb_target = carb_var.get()
            new_camera = camera_var.get()
            
            if new_camera != self.camera_index:
                self.camera_index = new_camera
                if self.cap:
                    self.cap.release()
                self.start_camera()
                
            self.save_data()
            messagebox.showinfo("Settings", "Settings saved successfully!")
            settings_window.destroy()
            
        tk.Button(settings_window, text="💾 Save Settings", 
                 command=save_settings,
                 font=("Arial", 12, "bold"),
                 bg="#27ae60", fg="white",
                 width=15, height=2,
                 cursor="hand2").pack(pady=20)
        
    def save_data(self):
        """Save data to JSON file"""
        data = {
            "carb_target": self.carb_target,
            "camera_index": self.camera_index,
            "daily_carbs": self.daily_carbs,
            "scan_history": self.scan_history
        }
        
        try:
            with open("carboscan_data.json", "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
            
    def load_data(self):
        """Load data from JSON file"""
        try:
            if os.path.exists("carboscan_data.json"):
                with open("carboscan_data.json", "r") as f:
                    data = json.load(f)
                    self.carb_target = data.get("carb_target", 45)
                    self.camera_index = data.get("camera_index", 0)
                    self.daily_carbs = data.get("daily_carbs", 0)
                    self.scan_history = data.get("scan_history", [])
        except Exception as e:
            print(f"Error loading data: {e}")
            
    def on_closing(self):
        """Clean up on window close"""
        self.save_data()
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = CarboScanApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
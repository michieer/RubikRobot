#
# Calibration GUI for Rubik's Cube Robot - Python conversion of calibrate.php and adjustServo.php
#

import tkinter as tk
from tkinter import ttk
import json
import os
import threading
from pathlib import Path
from moveCube.servo import moveServo
import serial.tools.list_ports

# -----------------------
# SETTINGS (edit here)
# -----------------------
MAIN_H = 850
MAIN_W = 1000

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class AdjustServoFrame:
    # Embedded frame for adjusting individual servo positions#
    
    def __init__(self, parent, config, direction, position, servo_number, serial_device, on_save_callback=None):
        self.config = config
        self.direction = direction
        self.position = position
        self.servo_number = servo_number
        self.serial_device = serial_device
        self.on_save_callback = on_save_callback
        self.current_value = config[direction][str(position)]
        self.min_value = self.current_value - 500
        self.max_value = self.current_value + 500
        
        # Create frame
        self.frame = ttk.LabelFrame(parent, text=f"Calibrate {direction.upper()} - Position {position}", padding="15")
        
        # Info labels
        ttk.Label(self.frame, text=f"Location: {direction.upper()}", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Label(self.frame, text=f"Position: {position}").grid(row=1, column=0, columnspan=2, sticky="w")
        ttk.Label(self.frame, text=f"Servo: {self.servo_number}").grid(row=2, column=0, columnspan=2, sticky="w")
        ttk.Label(self.frame, text=f"Current Value: {self.current_value}").grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 20))
        
        # Slider
        ttk.Label(self.frame, text="Adjust Value:", font=("Segoe UI", 10, "bold")).grid(row=4, column=0, columnspan=2, sticky="w")
        
        # Value display - CREATE BEFORE SLIDER to avoid callback issues
        #self.value_label = ttk.Label(self.frame, text=f"Value: {self.current_value}", font=("Segoe UI", 12, "bold"))
        #self.value_label.grid(row=6, column=0, columnspan=2, sticky="ew", pady=10)
        
        slider_frame = ttk.Frame(self.frame)
        slider_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Zorg dat value_var een IntVar is (of DoubleVar als je floats wilt)
        self.value_var = tk.IntVar(value=self.current_value)
        self.scale_var  = tk.DoubleVar(value=float(self.current_value))
        
        self.slider = ttk.Scale(
            slider_frame,
            from_=self.min_value,
            to=self.max_value,
            orient="horizontal",
            command=lambda v: self.value_var.set(int(float(v)))
        )
        self.slider.pack(fill="x", expand=True)
        self.slider.set(self.current_value)

        self.spinbox = ttk.Spinbox(
            slider_frame,
            from_=self.min_value,
            to=self.max_value,
            increment=1,
            textvariable=self.value_var,
            font=("Segoe UI", 12),
            width=6
        )
        self.spinbox.pack(pady=(6, 0))

        self.value_var.trace_add("write", self.on_value_change)
        self.value_var.set(self.current_value)

        # Buttons frame
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=self.save_value).pack(side="left", padx=5)

    def on_value_change(self, *args):
        try:
            value = int(float(self.value_var.get()))
        except (tk.TclError, ValueError):
            return

        if self.value_var.get() != value:
            self.value_var.set(value)
            return 

        # Voorkom thread-spam: start alleen als waarde echt veranderd is
        if getattr(self, "_last_value", None) == value:
            return
        self._last_value = value

        # Servo aansturen in background thread
        thread = threading.Thread(
            target=self._move_servo_safe,
            args=(value,),
            daemon=True
        )
        thread.start()

    def _move_servo_safe(self, value):
        #Safely move servo with error handling#
        try:
            moveServo('single', self.serial_device, self.servo_number, value)
        except Exception as e:
            print(f"Error moving servo: {e}")
    
    def save_value(self):
        #Save new servo position to config#
        new_value = int(float(self.slider.get()))
        self.config[self.direction][str(self.position)] = new_value
        
        # Save to JSON file
        config_path = Path('config/config.json')
        try:
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"Saved: {self.direction} {self.position} = {new_value}")
        except Exception as e:
            print(f"Error saving config: {e}")
        
        # Call the save callback
        if self.on_save_callback:
            self.on_save_callback()
    
    def get_frame(self):
        #Return the frame widget#
        return self.frame

class CalibrationWindow:
    #Main calibration window with image background and position controls#
    
    def __init__(self, parent_root):
        self.parent_root = parent_root
        self.config = self._load_config()
        self.serial_device = self._find_serial_device()
        self.current_direction = 'up'  # Default direction
        self.current_adjust_frame = None
        self.photo = None
        
        # Create main window
        self.window = tk.Toplevel(parent_root)
        self.window.title("Rubik's Cube Robot - Calibration")
        self.window.configure(bg='#f0f0f0')
        self.window.grab_set()  # Make it modal
        self.window.focus_set()
        self.window.attributes('-topmost', True)
        
        # Create main container with two columns
        main_container = ttk.Frame(self.window)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # LEFT COLUMN: Image with overlaid buttons
        left_frame = ttk.Frame(main_container, relief="sunken", borderwidth=2)
        left_frame.pack(side="left", fill="both", padx=(0, 5), expand=True)
        
        # Create frame for background image and buttons
        self.image_frame = tk.Frame(left_frame, bg="white")
        self.image_frame.pack(fill="both", expand=True)
        
        # Load and display the cube image
        self._load_cube_image()
        
        # RIGHT COLUMN: Position selections and adjustment
        right_frame = tk.Frame(main_container, bg='#f0f0f0', relief="sunken", borderwidth=2, width=310, height=1000)
        right_frame.pack(side="right", padx=(5, 0))
        right_frame.pack_propagate(False)  # Fixed width and height
        
        # Close button at bottom right (pack first so it stays at bottom)
        bottom_button_frame = ttk.Frame(right_frame)
        bottom_button_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        
        ttk.Button(bottom_button_frame, text="Close", command=self.window.destroy).pack(side="right", padx=5)
        
        # Top section: Direction/Delays content (positions list) - fixed height and width
        self.content_frame = ttk.Frame(right_frame, height=430, width=300)
        self.content_frame.pack(padx=5, pady=5)
        self.content_frame.pack_propagate(False)  # Fixed height and width
        
        self.direction_content = {}
        for direction in ['up', 'right', 'left', 'down']:
            frame = ttk.Frame(self.content_frame, borderwidth=1)
            self.direction_content[direction] = frame
            self._create_direction_content(frame, direction)
        
        # Create delays content with same scrollable structure
        self.delays_content = ttk.Frame(self.content_frame, borderwidth=1)
        self._create_delays_content_frame()
        
        # Bottom section: Adjustment window - fixed height and width
        self.adjust_container = ttk.Frame(right_frame, height=370, width=280)
        self.adjust_container.pack(padx=5, pady=5)
        self.adjust_container.pack_propagate(False)  # Fixed height and width
        
        # Initially show UP direction content
        self._show_direction_content('up')
        
        # Set window size and center on screen
        self._center(MAIN_W, MAIN_H)
    
    def _center(self, w, h):
        #Center window on screen#
        self.window.update_idletasks()
        sw, sh = self.window.winfo_screenwidth(), self.window.winfo_screenheight()
        x, y = (sw - w) // 2, (sh - h) // 2
        self.window.geometry(f"{w}x{h}+{x}+{y}")
  
    def _load_cube_image(self):
        #Load and display the cube image as background with overlaid buttons#
        try:
            if HAS_PIL:
                image_path = Path('config/Otvinta-rubik.png')
                if image_path.exists():
                    img = Image.open(image_path)
                    # Make image larger for better visibility
                    img.thumbnail((600, 600), Image.Resampling.LANCZOS)
                    self.photo = ImageTk.PhotoImage(img)
                    
                    # Store image dimensions
                    self.img_width = self.photo.width()
                    self.img_height = self.photo.height()
                    
                    # Create background label with image centered
                    self.image_label = tk.Label(self.image_frame, image=self.photo, bg="white")
                    self.image_label.place(relx=0.5, rely=0.5, anchor="center", 
                                          width=self.img_width, height=self.img_height)
                    
                    # Create overlay buttons
                    self._create_overlay_buttons()
                    return
        except Exception as e:
            print(f"Could not load image: {e}")
        
        # Fallback
        fallback_label = tk.Label(self.image_frame, text="Otvinta-rubik.png not found", 
                                   font=("Segoe UI", 10), bg="white", fg="gray")
        fallback_label.place(relwidth=1, relheight=1)
    
    def _create_overlay_buttons(self):
        #Create clickable buttons overlaid on image center using x,y pixel offsets#
        if not self.photo:
            return
        
        # Button positions as offsets from center (center_x = 0, center_y = 0)
        # x positive = right, x negative = left
        # y positive = down, y negative = up
        buttons_config = [
            ('UP', 20, -265, 'up'),
            ('DOWN', 20, 205, 'down'),
            ('LEFT', -180, 60, 'left'),
            ('RIGHT', 200, 60, 'right'),
            ('DELAYS', -180, 260, 'delays'),
        ]
        
        for text, offset_x, offset_y, direction in buttons_config:
            self._add_overlay_button(text, offset_x, offset_y, direction)
    
    def _add_overlay_button(self, text, offset_x, offset_y, direction):
        #Add a single button using x,y pixel offsets from image center#
        btn = tk.Button(
            self.image_frame,
            text=text,
            width=8,
            height=2,
            command=lambda d=direction: self._select_direction(d),
            bg='lightblue',
            activebackground='yellow',
            font=("Segoe UI", 9, "bold"),
            relief="raised",
            bd=2
        )
        # Position relative to center with pixel offsets
        btn.place(relx=0.5, rely=0.5, anchor="center", x=offset_x, y=offset_y)
        
        # Store button for later reference
        if not hasattr(self, 'overlay_buttons'):
            self.overlay_buttons = {}
        self.overlay_buttons[direction] = btn
    
    def _select_direction(self, direction):
        #Handle direction button click#
        self.current_direction = direction
        
        # Update overlay button appearance
        if hasattr(self, 'overlay_buttons'):
            for d, btn in self.overlay_buttons.items():
                if d == direction:
                    btn.config(bg='yellow')
                else:
                    btn.config(bg='lightblue')
        
        # Handle delays button separately
        if direction == 'delays':
            self._select_delays()
        else:
            # Show direction content (bottom section will be empty until a position is selected)
            self._show_direction_content(direction)
    
    def _select_delays(self):
        #Handle delays button click#
        # Hide all direction content
        for frame in self.direction_content.values():
            frame.pack_forget()
        self.delays_content.pack_forget()
        
        # Update header
        if not hasattr(self, 'content_header'):
            self.content_header = ttk.Label(self.content_frame, text="", font=("Segoe UI", 11, "bold"), foreground="blue")
            self.content_header.pack(side="top", fill="x", padx=10, pady=5)
        
        self.content_header.config(text="Movement Delays")
        
        # Show delays content
        if not self.delays_scrollable_frame.winfo_children():
            self._create_delays_content()
        self.delays_content.pack(fill="both", expand=True)
        
        # Clear adjustment window
        self._clear_adjustment_window()
    
    def _show_direction_content(self, direction):
        #Show content for the selected direction#
        # Hide all direction content and delays
        for frame in self.direction_content.values():
            frame.pack_forget()
        self.delays_content.pack_forget()
        
        # Add header showing selected direction
        if not hasattr(self, 'content_header'):
            self.content_header = ttk.Label(self.content_frame, text="", font=("Segoe UI", 11, "bold"), foreground="blue")
            self.content_header.pack(side="top", fill="x", padx=10, pady=5)
        
        self.content_header.config(text=f"Selected Side: {direction.upper()}")
        
        # Show selected direction content
        self.direction_content[direction].pack(fill="both", expand=True)
        
        # Clear the adjustment window when switching direction
        self._clear_adjustment_window()
    
    def _show_adjustment_window(self, direction, position):
        #Display adjustment window for selected direction and position#
        self._clear_adjustment_window()
        
        # Get servo ID
        servo_id = self.config[direction]['turnId'] if position in ['0', '90', '180', '270'] else self.config[direction]['moveId']
        
        # Create new adjustment frame
        self.current_adjust_frame = AdjustServoFrame(
            self.adjust_container,
            self.config,
            direction,
            position,
            servo_id,
            self.serial_device,
            on_save_callback=self._refresh_content
        )
        
        frame = self.current_adjust_frame.get_frame()
        frame.pack(fill="both", expand=True)
    
    def _clear_adjustment_window(self):
        #Clear the adjustment window#
        if hasattr(self, 'adjust_container'):
            for widget in self.adjust_container.winfo_children():
                widget.destroy()
        self.current_adjust_frame = None
    
    def _load_config(self):
        #Load configuration from config.json#
        config_path = Path('config/config.json')
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def _find_serial_device(self):
        #Find the Pololu serial device#
        try:
            if os.name == 'nt':  # Windows
                for port in serial.tools.list_ports.comports():
                    if "Pololu" in port.description and "Command" in port.description:
                        return port.device
            else:  # Linux/macOS
                return '/dev/ttyACM0'
        except Exception as e:
            print(f"Error finding serial device: {e}")
        return None
    
    def _create_direction_content(self, parent, direction):
        #Create content frame for a direction with scrollable positions#
        # Create scrollbar
        canvas = tk.Canvas(parent, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding="10")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Positions table
        positions_frame = ttk.LabelFrame(scrollable_frame, text="Rotation Positions", padding="10")
        positions_frame.pack(fill="x", pady=5)
        
        ttk.Label(positions_frame, text="Position", font=("Segoe UI", 9, "bold"), width=12).grid(row=0, column=0, sticky="w")
        ttk.Label(positions_frame, text="Value", font=("Segoe UI", 9, "bold"), width=12).grid(row=0, column=1, sticky="w")
        ttk.Label(positions_frame, text="Select", font=("Segoe UI", 9, "bold")).grid(row=0, column=2)
        
        row = 1
        for pos in ['0', '90', '180', '270']:
            value = self.config[direction][pos]
            ttk.Label(positions_frame, text=f"{pos}°").grid(row=row, column=0, sticky="w", pady=5)
            ttk.Label(positions_frame, text=str(value)).grid(row=row, column=1, sticky="w", pady=5)
            ttk.Button(
                positions_frame,
                text="Select",
                width=10,
                command=lambda d=direction, p=pos: self._show_adjustment_window(d, p)
            ).grid(row=row, column=2, pady=5)
            row += 1
        
        # Movement positions
        move_frame = ttk.LabelFrame(scrollable_frame, text="Movement Positions", padding="10")
        move_frame.pack(fill="x", pady=5)
        
        ttk.Label(move_frame, text="Position", font=("Segoe UI", 9, "bold"), width=12).grid(row=0, column=0, sticky="w")
        ttk.Label(move_frame, text="Value", font=("Segoe UI", 9, "bold"), width=12).grid(row=0, column=1, sticky="w")
        ttk.Label(move_frame, text="Select", font=("Segoe UI", 9, "bold")).grid(row=0, column=2)
        
        row = 1
        for pos, label in [('in', 'In'), ('out', 'Out'), ('park', 'Park')]:
            value = self.config[direction].get(pos, 'N/A')
            ttk.Label(move_frame, text=label).grid(row=row, column=0, sticky="w", pady=5)
            ttk.Label(move_frame, text=str(value)).grid(row=row, column=1, sticky="w", pady=5)
            if value != 'N/A':
                ttk.Button(
                    move_frame,
                    text="Select",
                    width=10,
                    command=lambda d=direction, p=pos: self._show_adjustment_window(d, p)
                ).grid(row=row, column=2, pady=5)
            row += 1
    def _create_delays_content_frame(self):
        #Create scrollable content frame for delays#
        canvas = tk.Canvas(self.delays_content, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.delays_content, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding="10")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store reference for later use
        self.delays_scrollable_frame = scrollable_frame
    
    def _create_delays_content(self):
        #Create delays configuration content#
        frame = ttk.LabelFrame(self.delays_scrollable_frame, text="Movement Delays (milliseconds)", padding="20")
        frame.pack(fill="x", pady=5)
        
        self.delay_entries = {}
        delays = self.config.get('delay', {})
        
        row = 0
        for delay_key, label in [('90', '90° Turn'), ('180', '180° Turn'), ('move', 'Move'), ('photo', 'Photo')]:
            ttk.Label(frame, text=f"{label}:").grid(row=row, column=0, sticky="w", pady=10)
            entry = ttk.Entry(frame, width=10)
            entry.insert(0, str(delays.get(delay_key, 0)))
            entry.grid(row=row, column=1, sticky="w", pady=10)
            self.delay_entries[delay_key] = entry
            row += 1
        
        # Save button for delays
        def save_delays():
            for key, entry in self.delay_entries.items():
                try:
                    self.config['delay'][key] = int(entry.get())
                except ValueError:
                    pass
            
            config_path = Path('config/config.json')
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            print("Delays saved")
        
        ttk.Button(frame, text="Save Delays", command=save_delays).grid(row=row, column=0, columnspan=2, pady=20)
    
    def _refresh_content(self):
        #Refresh config after changes#
        self.config = self._load_config()
        
        # Recreate all direction content frames
        for direction in self.direction_content.keys():
            frame = self.direction_content[direction]
            # Clear the frame
            for widget in frame.winfo_children():
                widget.destroy()
            # Recreate content
            self._create_direction_content(frame, direction)
    
    def _refresh_content(self):
        #Refresh config after changes#
        self.config = self._load_config()
        
        # Recreate all direction content frames
        for direction in self.direction_content.keys():
            frame = self.direction_content[direction]
            # Clear the frame
            for widget in frame.winfo_children():
                widget.destroy()
            # Recreate content
            self._create_direction_content(frame, direction)



def open_calibration_window(root):
    #Open the calibration window from main app#
    CalibrationWindow(root)




def open_calibration_window(root):
    #Open the calibration window from main app#
    CalibrationWindow(root)

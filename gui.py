import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from material import get_material_list
from tkinter import StringVar
import os  # Add this at the top with other imports

class AutocompleteComboBox(ctk.CTkComboBox):
    def __init__(self, *args, placeholder="Select Material", **kwargs):
        super().__init__(*args, **kwargs)
        self.placeholder = placeholder
        self._entry.bind("<FocusIn>", self._focus_in)
        self._entry.bind("<FocusOut>", self._focus_out)
        self._show_placeholder()
        
        self.all_values = self._values
        self._entry.bind('<KeyRelease>', self._on_keyrelease)

    def _focus_in(self, event):
        if self._entry.get() == self.placeholder:
            self._entry.delete(0, "end")

    def _focus_out(self, event):
        if not self._entry.get():
            self._show_placeholder()

    def _show_placeholder(self):
        self._entry.delete(0, "end")
        self._entry.insert(0, self.placeholder)
        
    def _on_keyrelease(self, event):
        # Get current text
        value = event.widget.get().lower()
        
        # Filter values based on current input
        if value:
            filtered_values = [
                item for item in self.all_values 
                if value in item.lower()
            ]
            
            # Update dropdown list with filtered values
            if (filtered_values):
                self.configure(values=filtered_values)
                # Force dropdown to open
                self._entry.focus_force()
                self._entry.event_generate("<Down>")
            else:
                self.configure(values=self.all_values)
        else:
            # If no input, show all values
            self.configure(values=self.all_values)

class RossFilterGUI:
    def __init__(self, calculator):
        self.window = ctk.CTk()
        self.window.title("Ross Filter Calculator")
        self.window.geometry("1400x950")
        
        # Store calculator instance
        self.calculator = calculator
        
        # Configure grid layout (2x2)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        # Create left frame for controls
        self.left_frame = ctk.CTkFrame(self.window, width=400)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Create right frame for plot
        self.right_frame = ctk.CTkFrame(self.window)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Initialize UI components
        self._setup_left_frame()
        self._setup_right_frame()
        
        # Set default appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

    def _setup_left_frame(self):
        # Configure grid layout for left frame
        self.left_frame.grid_columnconfigure(0, weight=1)
        
        # Add title label
        title_label = ctk.CTkLabel(
            self.left_frame, 
            text="Ross Filter Calculator",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Create Materials frame
        self.materials_frame = ctk.CTkFrame(self.left_frame)
        self.materials_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self._setup_materials_frame()
        
        # Create Energy Range frame
        self.energy_frame = ctk.CTkFrame(self.left_frame)
        self.energy_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self._setup_energy_frame()
        
        # Create Transmission frame (moved to row 3)
        self.transmission_frame = ctk.CTkFrame(self.left_frame)
        self.transmission_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self._setup_transmission_frame()
        
        # Create Output Console frame (moved to row 4)
        self.output_frame = ctk.CTkFrame(self.left_frame)
        self.output_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        self._setup_output_frame()

    def _setup_materials_frame(self):
        # Configure materials frame
        self.materials_frame.grid_columnconfigure(1, weight=1)
        
        # Add Materials frame title
        materials_title = ctk.CTkLabel(
            self.materials_frame,
            text="Materials",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        materials_title.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # Add Show Materials button
        show_materials_button = ctk.CTkButton(
            self.materials_frame,
            text="Show Available Materials",
            width=200,
            command=self._show_materials_list
        )
        show_materials_button.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
        
        # Filter 1 label
        filter1_label = ctk.CTkLabel(
            self.materials_frame,
            text="Filter 1:",
            font=ctk.CTkFont(size=14)
        )
        filter1_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        # Get material list
        materials = get_material_list()
        
        # Material dropdown
        self.material1_var = ctk.StringVar(value="Select Material")
        self.material1_dropdown = AutocompleteComboBox(
            self.materials_frame,
            values=materials,
            variable=self.material1_var,
            width=200,
            placeholder="Select Material"
        )
        self.material1_dropdown.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        # Thickness label and entry
        thickness1_label = ctk.CTkLabel(
            self.materials_frame,
            text="Thickness (µm):",  # Changed to µm
            font=ctk.CTkFont(size=14)
        )
        thickness1_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        # Create frame for thickness1 input
        thickness1_frame = ctk.CTkFrame(self.materials_frame)
        thickness1_frame.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        thickness1_frame.grid_columnconfigure(0, weight=1)

        self.thickness1_var = StringVar(value="0.0")
        self.thickness1_entry = ctk.CTkEntry(
            thickness1_frame,
            textvariable=self.thickness1_var,
            width=160
        )
        self.thickness1_entry.grid(row=0, column=0, sticky="ew")

        # Up/Down buttons for thickness1
        buttons_frame1 = ctk.CTkFrame(thickness1_frame)
        buttons_frame1.grid(row=0, column=1, padx=(5,0))
        
        up_button1 = ctk.CTkButton(
            buttons_frame1, text="↑", width=10, height=5,
            command=lambda: self._adjust_thickness(self.thickness1_var, 0.1)
        )
        up_button1.grid(row=0, column=0)
        
        down_button1 = ctk.CTkButton(
            buttons_frame1, text="↓", width=10, height=5,
            command=lambda: self._adjust_thickness(self.thickness1_var, -0.1)
        )
        down_button1.grid(row=1, column=0)

        # Create button frame for Filter 1 buttons
        filter1_buttons_frame = ctk.CTkFrame(self.materials_frame)
        filter1_buttons_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # Add Filter 1 button
        add_filter1_button = ctk.CTkButton(
            filter1_buttons_frame,
            text="Add Filter 1",
            width=120,
            command=lambda: self._add_filter(
                1,
                self.material1_var.get(),
                self.thickness1_var.get(),
                "Filter 1"
            )
        )
        add_filter1_button.grid(row=0, column=0, padx=5)

        # Modify Filter 1 button
        modify_filter1_button = ctk.CTkButton(
            filter1_buttons_frame,
            text="Modify Filter 1",
            width=120,
            command=lambda: self._modify_filter(1)
        )
        modify_filter1_button.grid(row=0, column=1, padx=5)
        
        # Filter 2 label
        filter2_label = ctk.CTkLabel(
            self.materials_frame,
            text="Filter 2:",
            font=ctk.CTkFont(size=14)
        )
        filter2_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
        
        # Material dropdown for Filter 2
        self.material2_var = ctk.StringVar(value="Select Material")
        self.material2_dropdown = AutocompleteComboBox(
            self.materials_frame,
            values=materials,
            variable=self.material2_var,
            width=200,
            placeholder="Select Material"
        )
        self.material2_dropdown.grid(row=5, column=1, padx=10, pady=5, sticky="ew")
        
        # Thickness label and entry for Filter 2
        thickness2_label = ctk.CTkLabel(
            self.materials_frame,
            text="Thickness (µm):",  # Changed to µm
            font=ctk.CTkFont(size=14)
        )
        thickness2_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
        
        # Create frame for thickness2 input
        thickness2_frame = ctk.CTkFrame(self.materials_frame)
        thickness2_frame.grid(row=6, column=1, padx=10, pady=5, sticky="ew")
        thickness2_frame.grid_columnconfigure(0, weight=1)

        self.thickness2_var = StringVar(value="0.0")
        self.thickness2_entry = ctk.CTkEntry(
            thickness2_frame,
            textvariable=self.thickness2_var,
            width=160
        )
        self.thickness2_entry.grid(row=0, column=0, sticky="ew")

        # Up/Down buttons for thickness2
        buttons_frame2 = ctk.CTkFrame(thickness2_frame)
        buttons_frame2.grid(row=0, column=1, padx=(5,0))
        
        up_button2 = ctk.CTkButton(
            buttons_frame2, text="↑", width=10, height=5,
            command=lambda: self._adjust_thickness(self.thickness2_var, 0.1)
        )
        up_button2.grid(row=0, column=0)
        
        down_button2 = ctk.CTkButton(
            buttons_frame2, text="↓", width=10, height=5,
            command=lambda: self._adjust_thickness(self.thickness2_var, -0.1)
        )
        down_button2.grid(row=1, column=0)

        # Create button frame for Filter 2 buttons
        filter2_buttons_frame = ctk.CTkFrame(self.materials_frame)
        filter2_buttons_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

        # Add Filter 2 button
        add_filter2_button = ctk.CTkButton(
            filter2_buttons_frame,
            text="Add Filter 2",
            width=120,
            command=lambda: self._add_filter(
                2,
                self.material2_var.get(),
                self.thickness2_var.get(),
                "Filter 2"
            )
        )
        add_filter2_button.grid(row=0, column=0, padx=5)

        # Modify Filter 2 button
        modify_filter2_button = ctk.CTkButton(
            filter2_buttons_frame,
            text="Modify Filter 2",
            width=120,
            command=lambda: self._modify_filter(2)
        )
        modify_filter2_button.grid(row=0, column=1, padx=5)

    def _modify_filter(self, filter_num):
        """Modify existing filter material thickness"""
        filter_instance = self.calculator.filter1 if filter_num == 1 else self.calculator.filter2
        material_var = self.material1_var if filter_num == 1 else self.material2_var
        thickness_var = self.thickness1_var if filter_num == 1 else self.thickness2_var
        
        # Check if materials exist in filter
        if not filter_instance.materials:
            self.print_to_console(f"Filter {filter_num} is empty. Nothing to modify.")
            return
            
        current_material = material_var.get()
        
        # Check if selected material exists in filter
        if current_material not in filter_instance.materials:
            self.print_to_console(f"Material '{current_material}' not found in Filter {filter_num}")
            return
            
        try:
            # Get material index
            material_index = filter_instance.materials.index(current_material)
            
            # Update thickness
            new_thickness = float(thickness_var.get()) * 1e-4  # Convert µm to cm
            filter_instance.thicknesses[material_index] = new_thickness
            
            self.print_to_console(
                f"Filter {filter_num}: Modified {current_material} thickness to {thickness_var.get()} µm"
            )
        except ValueError as e:
            self.print_to_console(f"Error modifying Filter {filter_num}: {str(e)}")

    def _add_filter(self, filter_num, material, thickness_str, filter_name):
        """Add material to filter through calculator"""
        success, message = self.calculator.add_material_to_filter(
            filter_num,
            material,
            float(thickness_str)
        )
        
        if success:
            self.print_to_console(
                f"{filter_name}: Added {material} with thickness {thickness_str} µm"
            )
        else:
            self.print_to_console(f"{filter_name} Error: {message}")

    def _show_materials_list(self):
        """Display all available materials in a new window"""
        materials_window = ctk.CTkToplevel(self.window)
        materials_window.title("Available Materials")
        materials_window.geometry("400x510")
        
        # Make window modal and stay on top
        materials_window.transient(self.window)  # Set parent window
        materials_window.grab_set()  # Make window modal
        materials_window.lift()  # Lift window to top
        
        # Center the window relative to main window
        x = self.window.winfo_x() + (self.window.winfo_width() - 400) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - 500) // 2
        materials_window.geometry(f"+{x}+{y}")
        
        # Add title label
        title = ctk.CTkLabel(
            materials_window,
            text="Available Materials",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=10)
        
        # Create scrollable textbox
        textbox = ctk.CTkTextbox(materials_window, width=350, height=400)
        textbox.pack(padx=20, pady=10)
        
        # Get and display materials
        materials = get_material_list()
        materials_text = "\n".join(sorted(materials))
        textbox.insert("1.0", materials_text)
        textbox.configure(state="disabled")  # Make read-only

        # Close button
        close_button = ctk.CTkButton(
            materials_window,
            text="Close",
            width=100,
            command=materials_window.destroy
        )
        close_button.pack(pady=10)

    def _adjust_thickness(self, var: StringVar, delta: float):
        """Adjust thickness value by delta amount"""
        try:
            current = float(var.get())
            new_value = max(0, min(100, current + delta))  # Clamp between 0 and 10
            var.set(f"{new_value:.1f}")
        except ValueError:
            var.set("0.0")

    def _setup_energy_frame(self):
        # Remove the column weight configuration as it affects the entry width
        # self.energy_frame.grid_columnconfigure(1, weight=1)  # Remove this line
        
        # Add Energy Range frame title
        energy_title = ctk.CTkLabel(
            self.energy_frame,
            text="Energy Range (keV)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        energy_title.grid(row=0, column=0, columnspan=6, padx=10, pady=5, sticky="w")
        
        # Start Energy
        start_label = ctk.CTkLabel(
            self.energy_frame,
            text="Start:",
            font=ctk.CTkFont(size=14)
        )
        start_label.grid(row=1, column=0, padx=3, pady=5)
        
        self.energy_start_var = StringVar(value="0.001")
        self.energy_start_entry = ctk.CTkEntry(
            self.energy_frame,
            textvariable=self.energy_start_var,
            width=90
        )
        self.energy_start_entry.grid(row=1, column=1, padx=3, pady=5)
        
        # Stop Energy
        stop_label = ctk.CTkLabel(
            self.energy_frame,
            text="Stop:",
            font=ctk.CTkFont(size=14)
        )
        stop_label.grid(row=1, column=2, padx=3, pady=5)
        
        self.energy_stop_var = StringVar(value="50.0")
        self.energy_stop_entry = ctk.CTkEntry(
            self.energy_frame,
            textvariable=self.energy_stop_var,
            width=90
        )
        self.energy_stop_entry.grid(row=1, column=3, padx=3, pady=5)
        
        # Step Size
        step_label = ctk.CTkLabel(
            self.energy_frame,
            text="Step:",
            font=ctk.CTkFont(size=14)
        )
        step_label.grid(row=1, column=4, padx=3, pady=5)
        
        self.energy_step_var = StringVar(value="0.5")
        self.energy_step_entry = ctk.CTkEntry(
            self.energy_frame,
            textvariable=self.energy_step_var,
            width=90
        )
        self.energy_step_entry.grid(row=1, column=5, padx=3, pady=5)

    def _setup_transmission_frame(self):
        # Configure transmission frame
        self.transmission_frame.grid_columnconfigure((0,1), weight=1)
        
        # Add Transmission frame title
        transmission_title = ctk.CTkLabel(
            self.transmission_frame,
            text="Transmission Calculation",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        transmission_title.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # Create button frame for aligned buttons
        button_frame = ctk.CTkFrame(self.transmission_frame)
        button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        
        # Add Calculate button
        calculate_button = ctk.CTkButton(
            button_frame,
            text="Calculate Transmission",
            width=200,
            command=self._calculate_transmission
        )
        calculate_button.grid(row=0, column=0, padx=5, pady=10)
        
        # Add Reset button
        reset_button = ctk.CTkButton(
            button_frame,
            text="Reset",
            width=100,
            command=self._reset_all,
            fg_color="darkred",
            hover_color="red"
        )
        reset_button.grid(row=0, column=1, padx=5, pady=10)
        
        # Add Save Figure button
        save_button = ctk.CTkButton(
            button_frame,
            text="Save Figure",
            width=100,
            command=self._save_figure,
            fg_color="darkgreen",
            hover_color="green"
        )
        save_button.grid(row=0, column=2, padx=5, pady=10)

    def _save_figure(self):
        """Save the current figure to a file"""
        try:
            # Get current working directory and default filename
            initialdir = os.getcwd()
            initialfile = "figure"
            
            # Create file dialog
            file_path = ctk.filedialog.asksaveasfilename(
                defaultextension=".png",
                initialdir=initialdir,
                initialfile=initialfile,
                filetypes=[
                    ("PNG files", "*.png"),
                    ("PDF files", "*.pdf"),
                    ("SVG files", "*.svg")
                ],
                title="Save Figure As"
            )
            
            if file_path:
                # Save figure
                self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                self.print_to_console(f"Figure saved successfully to: {file_path}")
        except Exception as e:
            self.print_to_console(f"Error saving figure: {str(e)}")

    def _reset_all(self):
        """Reset everything to initial state"""
        try:
            # Reset calculator
            success, message = self.calculator.reset()
            
            if success:
                # Reset material dropdowns
                self.material1_var.set("Select Material")
                self.material2_var.set("Select Material")
                
                # Reset thickness values
                self.thickness1_var.set("0.0")
                self.thickness2_var.set("0.0")
                
                # Reset plot
                self._initialize_plot()
                
                self.print_to_console("Reset successful - All filters cleared")
            else:
                self.print_to_console(f"Reset failed: {message}")
                
        except Exception as e:
            self.print_to_console(f"Reset error: {str(e)}")

    def _calculate_transmission(self):
        """Calculate and plot transmission using calculator"""
        try:
            success, result = self.calculator.calculate_transmission(
                self.energy_start_var.get(),
                self.energy_stop_var.get(),
                self.energy_step_var.get()
            )
            
            if success:
                # Clear previous plot
                self.plot.clear()
                
                # Plot available data
                energies = result['energies']
                
                if 'transmission1' in result:
                    self.plot.plot(energies/1E3, result['transmission1'], 
                                 label='Filter 1', color='blue')
                
                if 'transmission2' in result:
                    self.plot.plot(energies/1E3, result['transmission2'], 
                                 label='Filter 2', color='red')
                
                if 'difference' in result:
                    self.plot.plot(energies/1E3, result['difference'], 
                                 label='Difference', linestyle='--', color='green')
                
                self.plot.set_xlabel('Energy (keV)')
                self.plot.set_ylabel('Transmission')
                self.plot.set_title('Ross Filter Transmission')
                self.plot.grid(True)
                self.plot.legend()
                
                self.canvas.draw()
                
                # Print calculation results
                self.print_to_console("Transmission calculation completed successfully")
            else:
                self.print_to_console(f"Calculation Error: {result}")
                
        except Exception as e:
            self.print_to_console(f"Error: {str(e)}")

    def _setup_output_frame(self):
        """Setup the output console frame"""
        # Configure output frame
        self.output_frame.grid_columnconfigure(0, weight=1)
        
        # Add Output Console frame title
        output_title = ctk.CTkLabel(
            self.output_frame,
            text="Output Console",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        output_title.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Create output console textbox
        self.output_console = ctk.CTkTextbox(
            self.output_frame,
            width=380,
            height=150,
            font=ctk.CTkFont(size=12)
        )
        self.output_console.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Add Clear button
        clear_button = ctk.CTkButton(
            self.output_frame,
            text="Clear Console",
            width=120,
            command=self._clear_console
        )
        clear_button.grid(row=2, column=0, padx=10, pady=10)
        
    def _clear_console(self):
        """Clear the output console"""
        self.output_console.delete("1.0", "end")
        
    def print_to_console(self, message):
        """Print a message to the output console"""
        self.output_console.insert("end", f"{message}\n")
        self.output_console.see("end")  # Auto-scroll to bottom

    def _setup_right_frame(self):
        # Create matplotlib figure
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.right_frame)
        self.canvas.draw()
        
        # Place canvas in right frame
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initialize empty plot
        self._initialize_plot()

    def _initialize_plot(self):
        """Initialize empty plot with labels"""
        self.plot.clear()
        self.plot.set_xlabel('Energy (keV)')
        self.plot.set_ylabel('Transmission')
        self.plot.set_title('Ross Filter Transmission')
        self.plot.grid(True)
        self.canvas.draw()

    def _sample_plot(self):
        """Remove sample plot, start with empty plot"""
        self._initialize_plot()

    def run(self):
        """Start the GUI application"""
        self.window.mainloop()

if __name__ == "__main__":
    app = RossFilterGUI()
    app.run()

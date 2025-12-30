import os
from tkinter import StringVar

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .material import get_material_list
from .units import um_to_cm


class AutocompleteComboBox(ctk.CTkComboBox):
    def __init__(self, *args, placeholder="Select Material", **kwargs):
        super().__init__(*args, **kwargs)
        self.placeholder = placeholder
        self._entry.bind("<FocusIn>", self._focus_in)
        self._entry.bind("<FocusOut>", self._focus_out)
        self._show_placeholder()

        self.all_values = self._values
        self._entry.bind("<KeyRelease>", self._on_keyrelease)

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
        value = event.widget.get().lower()

        if value:
            filtered_values = [item for item in self.all_values if value in item.lower()]
            if filtered_values:
                self.configure(values=filtered_values)
                self._entry.focus_force()
                self._entry.event_generate("<Down>")
            else:
                self.configure(values=self.all_values)
        else:
            self.configure(values=self.all_values)


class RossFilterGUI:
    def __init__(self, calculator):
        self.window = ctk.CTk()
        self.window.title("Ross Filter Calculator")
        self.window.geometry("1400x950")

        self.calculator = calculator

        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.left_frame = ctk.CTkFrame(self.window, width=400)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.right_frame = ctk.CTkFrame(self.window)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self._setup_left_frame()
        self._setup_right_frame()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

    def _setup_left_frame(self):
        self.left_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            self.left_frame,
            text="Ross Filter Calculator",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.materials_frame = ctk.CTkFrame(self.left_frame)
        self.materials_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self._setup_materials_frame()

        self.energy_frame = ctk.CTkFrame(self.left_frame)
        self.energy_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self._setup_energy_frame()

        self.transmission_frame = ctk.CTkFrame(self.left_frame)
        self.transmission_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self._setup_transmission_frame()

        self.output_frame = ctk.CTkFrame(self.left_frame)
        self.output_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        self._setup_output_frame()

    def _setup_materials_frame(self):
        self.materials_frame.grid_columnconfigure(1, weight=1)

        materials_title = ctk.CTkLabel(
            self.materials_frame,
            text="Materials",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        materials_title.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        show_materials_button = ctk.CTkButton(
            self.materials_frame,
            text="Show Available Materials",
            width=200,
            command=self._show_materials_list,
        )
        show_materials_button.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        materials = get_material_list()

        filter1_label = ctk.CTkLabel(self.materials_frame, text="Filter 1:", font=ctk.CTkFont(size=14))
        filter1_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.material1_var = ctk.StringVar(value="Select Material")
        self.material1_dropdown = AutocompleteComboBox(
            self.materials_frame,
            values=materials,
            variable=self.material1_var,
            width=200,
            placeholder="Select Material",
        )
        self.material1_dropdown.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        thickness1_label = ctk.CTkLabel(
            self.materials_frame,
            text="Thickness (µm):",
            font=ctk.CTkFont(size=14),
        )
        thickness1_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        thickness1_frame = ctk.CTkFrame(self.materials_frame)
        thickness1_frame.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        thickness1_frame.grid_columnconfigure(0, weight=1)

        self.thickness1_var = StringVar(value="0.0")
        self.thickness1_entry = ctk.CTkEntry(thickness1_frame, textvariable=self.thickness1_var, width=160)
        self.thickness1_entry.grid(row=0, column=0, sticky="ew")

        buttons_frame1 = ctk.CTkFrame(thickness1_frame)
        buttons_frame1.grid(row=0, column=1, padx=(5, 0))

        up_button1 = ctk.CTkButton(
            buttons_frame1,
            text="↑",
            width=10,
            height=5,
            command=lambda: self._adjust_thickness(self.thickness1_var, 0.1),
        )
        up_button1.grid(row=0, column=0)

        down_button1 = ctk.CTkButton(
            buttons_frame1,
            text="↓",
            width=10,
            height=5,
            command=lambda: self._adjust_thickness(self.thickness1_var, -0.1),
        )
        down_button1.grid(row=1, column=0)

        filter1_buttons_frame = ctk.CTkFrame(self.materials_frame)
        filter1_buttons_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        add_filter1_button = ctk.CTkButton(
            filter1_buttons_frame,
            text="Add Filter 1",
            width=120,
            command=lambda: self._add_filter(1, self.material1_var.get(), self.thickness1_var.get(), "Filter 1"),
        )
        add_filter1_button.grid(row=0, column=0, padx=5)

        modify_filter1_button = ctk.CTkButton(
            filter1_buttons_frame,
            text="Modify Filter 1",
            width=120,
            command=lambda: self._modify_filter(1),
        )
        modify_filter1_button.grid(row=0, column=1, padx=5)

        filter2_label = ctk.CTkLabel(self.materials_frame, text="Filter 2:", font=ctk.CTkFont(size=14))
        filter2_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")

        self.material2_var = ctk.StringVar(value="Select Material")
        self.material2_dropdown = AutocompleteComboBox(
            self.materials_frame,
            values=materials,
            variable=self.material2_var,
            width=200,
            placeholder="Select Material",
        )
        self.material2_dropdown.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        thickness2_label = ctk.CTkLabel(
            self.materials_frame,
            text="Thickness (µm):",
            font=ctk.CTkFont(size=14),
        )
        thickness2_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")

        thickness2_frame = ctk.CTkFrame(self.materials_frame)
        thickness2_frame.grid(row=6, column=1, padx=10, pady=5, sticky="ew")
        thickness2_frame.grid_columnconfigure(0, weight=1)

        self.thickness2_var = StringVar(value="0.0")
        self.thickness2_entry = ctk.CTkEntry(thickness2_frame, textvariable=self.thickness2_var, width=160)
        self.thickness2_entry.grid(row=0, column=0, sticky="ew")

        buttons_frame2 = ctk.CTkFrame(thickness2_frame)
        buttons_frame2.grid(row=0, column=1, padx=(5, 0))

        up_button2 = ctk.CTkButton(
            buttons_frame2,
            text="↑",
            width=10,
            height=5,
            command=lambda: self._adjust_thickness(self.thickness2_var, 0.1),
        )
        up_button2.grid(row=0, column=0)

        down_button2 = ctk.CTkButton(
            buttons_frame2,
            text="↓",
            width=10,
            height=5,
            command=lambda: self._adjust_thickness(self.thickness2_var, -0.1),
        )
        down_button2.grid(row=1, column=0)

        filter2_buttons_frame = ctk.CTkFrame(self.materials_frame)
        filter2_buttons_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

        add_filter2_button = ctk.CTkButton(
            filter2_buttons_frame,
            text="Add Filter 2",
            width=120,
            command=lambda: self._add_filter(2, self.material2_var.get(), self.thickness2_var.get(), "Filter 2"),
        )
        add_filter2_button.grid(row=0, column=0, padx=5)

        modify_filter2_button = ctk.CTkButton(
            filter2_buttons_frame,
            text="Modify Filter 2",
            width=120,
            command=lambda: self._modify_filter(2),
        )
        modify_filter2_button.grid(row=0, column=1, padx=5)

    def _modify_filter(self, filter_num):
        filter_instance = self.calculator.filter1 if filter_num == 1 else self.calculator.filter2
        material_var = self.material1_var if filter_num == 1 else self.material2_var
        thickness_var = self.thickness1_var if filter_num == 1 else self.thickness2_var

        if not filter_instance.materials:
            self.print_to_console(f"Filter {filter_num} is empty. Nothing to modify.")
            return

        current_material = material_var.get()
        if current_material not in filter_instance.materials:
            self.print_to_console(f"Material '{current_material}' not found in Filter {filter_num}")
            return

        try:
            material_index = filter_instance.materials.index(current_material)
            filter_instance.thicknesses[material_index] = um_to_cm(float(thickness_var.get()))
            self.print_to_console(
                f"Filter {filter_num}: Modified {current_material} thickness to {thickness_var.get()} µm"
            )
        except ValueError as e:
            self.print_to_console(f"Error modifying Filter {filter_num}: {str(e)}")

    def _add_filter(self, filter_num, material, thickness_str, filter_name):
        success, message = self.calculator.add_material_to_filter(filter_num, material, float(thickness_str))
        if success:
            self.print_to_console(f"{filter_name}: Added {material} with thickness {thickness_str} µm")
        else:
            self.print_to_console(f"{filter_name} Error: {message}")

    def _show_materials_list(self):
        materials_window = ctk.CTkToplevel(self.window)
        materials_window.title("Available Materials")
        materials_window.geometry("400x510")

        materials_window.transient(self.window)
        materials_window.grab_set()
        materials_window.lift()

        x = self.window.winfo_x() + (self.window.winfo_width() - 400) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - 500) // 2
        materials_window.geometry(f"+{x}+{y}")

        title = ctk.CTkLabel(
            materials_window,
            text="Available Materials",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        title.pack(pady=10)

        textbox = ctk.CTkTextbox(materials_window, width=350, height=400)
        textbox.pack(padx=20, pady=10)

        materials_text = "\n".join(sorted(get_material_list()))
        textbox.insert("1.0", materials_text)
        textbox.configure(state="disabled")

        close_button = ctk.CTkButton(materials_window, text="Close", width=100, command=materials_window.destroy)
        close_button.pack(pady=10)

    def _adjust_thickness(self, var: StringVar, delta: float):
        try:
            current = float(var.get())
            new_value = max(0, min(100, current + delta))
            var.set(f"{new_value:.1f}")
        except ValueError:
            var.set("0.0")

    def _setup_energy_frame(self):
        energy_title = ctk.CTkLabel(
            self.energy_frame,
            text="Energy Range (keV)",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        energy_title.grid(row=0, column=0, columnspan=6, padx=10, pady=5, sticky="w")

        start_label = ctk.CTkLabel(self.energy_frame, text="Start:", font=ctk.CTkFont(size=14))
        start_label.grid(row=1, column=0, padx=3, pady=5)
        self.energy_start_var = StringVar(value="0.001")
        self.energy_start_entry = ctk.CTkEntry(self.energy_frame, textvariable=self.energy_start_var, width=90)
        self.energy_start_entry.grid(row=1, column=1, padx=3, pady=5)

        stop_label = ctk.CTkLabel(self.energy_frame, text="Stop:", font=ctk.CTkFont(size=14))
        stop_label.grid(row=1, column=2, padx=3, pady=5)
        self.energy_stop_var = StringVar(value="50.0")
        self.energy_stop_entry = ctk.CTkEntry(self.energy_frame, textvariable=self.energy_stop_var, width=90)
        self.energy_stop_entry.grid(row=1, column=3, padx=3, pady=5)

        step_label = ctk.CTkLabel(self.energy_frame, text="Step:", font=ctk.CTkFont(size=14))
        step_label.grid(row=1, column=4, padx=3, pady=5)
        self.energy_step_var = StringVar(value="0.5")
        self.energy_step_entry = ctk.CTkEntry(self.energy_frame, textvariable=self.energy_step_var, width=90)
        self.energy_step_entry.grid(row=1, column=5, padx=3, pady=5)

    def _setup_transmission_frame(self):
        self.transmission_frame.grid_columnconfigure((0, 1), weight=1)

        transmission_title = ctk.CTkLabel(
            self.transmission_frame,
            text="Transmission Calculation",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        transmission_title.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        button_frame = ctk.CTkFrame(self.transmission_frame)
        button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        calculate_button = ctk.CTkButton(
            button_frame,
            text="Calculate Transmission",
            width=200,
            command=self._calculate_transmission,
        )
        calculate_button.grid(row=0, column=0, padx=5, pady=10)

        reset_button = ctk.CTkButton(
            button_frame,
            text="Reset",
            width=100,
            command=self._reset_all,
            fg_color="darkred",
            hover_color="red",
        )
        reset_button.grid(row=0, column=1, padx=5, pady=10)

        save_button = ctk.CTkButton(
            button_frame,
            text="Save Figure",
            width=100,
            command=self._save_figure,
            fg_color="darkgreen",
            hover_color="green",
        )
        save_button.grid(row=0, column=2, padx=5, pady=10)

    def _save_figure(self):
        try:
            initialdir = os.getcwd()
            initialfile = "figure"

            file_path = ctk.filedialog.asksaveasfilename(
                defaultextension=".png",
                initialdir=initialdir,
                initialfile=initialfile,
                filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("SVG files", "*.svg")],
                title="Save Figure As",
            )

            if file_path:
                self.figure.savefig(file_path, dpi=300, bbox_inches="tight")
                self.print_to_console(f"Figure saved successfully to: {file_path}")
        except Exception as e:
            self.print_to_console(f"Error saving figure: {str(e)}")

    def _reset_all(self):
        try:
            success, message = self.calculator.reset()
            if success:
                self.material1_var.set("Select Material")
                self.material2_var.set("Select Material")
                self.thickness1_var.set("0.0")
                self.thickness2_var.set("0.0")
                self._initialize_plot()
                self.print_to_console("Reset successful - All filters cleared")
            else:
                self.print_to_console(f"Reset failed: {message}")
        except Exception as e:
            self.print_to_console(f"Reset error: {str(e)}")

    def _calculate_transmission(self):
        try:
            success, result = self.calculator.calculate_transmission(
                self.energy_start_var.get(),
                self.energy_stop_var.get(),
                self.energy_step_var.get(),
            )

            if success:
                self.plot.clear()
                energies = result["energies"]

                if "transmission1" in result:
                    self.plot.plot(energies / 1e3, result["transmission1"], label="Filter 1", color="blue")
                if "transmission2" in result:
                    self.plot.plot(energies / 1e3, result["transmission2"], label="Filter 2", color="red")
                if "difference" in result:
                    self.plot.plot(
                        energies / 1e3,
                        result["difference"],
                        label="Difference",
                        linestyle="--",
                        color="green",
                    )

                self.plot.set_xlabel("Energy (keV)")
                self.plot.set_ylabel("Transmission")
                self.plot.set_title("Ross Filter Transmission")
                self.plot.grid(True)
                self.plot.legend()
                self.canvas.draw()
                self.print_to_console("Transmission calculation completed successfully")
            else:
                self.print_to_console(f"Calculation Error: {result}")
        except Exception as e:
            self.print_to_console(f"Error: {str(e)}")

    def _setup_output_frame(self):
        self.output_frame.grid_columnconfigure(0, weight=1)

        output_title = ctk.CTkLabel(
            self.output_frame,
            text="Output Console",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        output_title.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.output_console = ctk.CTkTextbox(
            self.output_frame,
            width=380,
            height=150,
            font=ctk.CTkFont(size=12),
        )
        self.output_console.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        clear_button = ctk.CTkButton(self.output_frame, text="Clear Console", width=120, command=self._clear_console)
        clear_button.grid(row=2, column=0, padx=10, pady=10)

    def _clear_console(self):
        self.output_console.delete("1.0", "end")

    def print_to_console(self, message):
        self.output_console.insert("end", f"{message}\n")
        self.output_console.see("end")

    def _setup_right_frame(self):
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.right_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        self._initialize_plot()

    def _initialize_plot(self):
        self.plot.clear()
        self.plot.set_xlabel("Energy (keV)")
        self.plot.set_ylabel("Transmission")
        self.plot.set_title("Ross Filter Transmission")
        self.plot.grid(True)
        self.canvas.draw()

    def run(self):
        self.window.mainloop()

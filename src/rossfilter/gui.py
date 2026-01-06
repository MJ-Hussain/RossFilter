import tkinter as tk
import customtkinter as ctk
import numpy as np
import xraydb

from .calculator import RossFilterCalculator
from .material import get_material_list
from .plot_manager import PlotManager
from .plot_selection import PlotSelectionPanel
from .units import um_to_cm, kev_to_ev


class AutocompleteComboBox(ctk.CTkComboBox):
    def __init__(self, *args, placeholder="Select Material", **kwargs):
        super().__init__(*args, **kwargs)
        self.placeholder = placeholder
        self.all_values = self._values
        
        self.set(placeholder)
        self.configure(text_color="gray")
        
        self._entry.bind("<FocusIn>", self._on_focus_in)
        self._entry.bind("<FocusOut>", self._on_focus_out)
        self._entry.bind("<KeyRelease>", self._on_key_release)

    def _on_focus_in(self, event):
        if self.get() == self.placeholder:
            self.set("")
            self.configure(text_color=("black", "white"))

    def _on_focus_out(self, event):
        if not self.get():
            self.set(self.placeholder)
            self.configure(text_color="gray")

    def _on_key_release(self, event):
        if event.keysym in ["Up", "Down", "Return", "Escape", "Tab"]:
            return

        current_text = self.get()
        value = current_text.lower()
        
        if value:
            filtered_values = [item for item in self.all_values if value in item.lower()]
            self.configure(values=filtered_values if filtered_values else self.all_values)
            
            if filtered_values:
                try:
                    # Directly try to open the dropdown menu (CustomTkinter internal)
                    self._open_dropdown_menu()
                except AttributeError:
                    # Fallback for older versions or if method name changes
                    self._entry.event_generate("<Down>")
                
                # Ensure focus remains on the entry widget so typing can continue
                self._entry.focus_set()
        else:
            self.configure(values=self.all_values)


class ChannelWidget(ctk.CTkFrame):
    """Widget representing a single channel in the list (CRUD only)."""

    def __init__(self, master, channel_idx, channel, 
                 on_select_callback, 
                 on_delete_channel_callback,
                 on_edit_filter_callback,
                 on_delete_filter_callback,
                 is_selected=False, **kwargs):
        super().__init__(master, **kwargs)
        self.channel_idx = channel_idx
        self.channel = channel
        self.on_select_callback = on_select_callback
        self.on_delete_channel_callback = on_delete_channel_callback
        self.on_edit_filter_callback = on_edit_filter_callback
        self.on_delete_filter_callback = on_delete_filter_callback
        
        self.selected_color = ("#3B8ED0", "#1F6AA5")  # ctk theme color
        self.default_color = ("#EBEBEB", "#2B2B2B")   # ctk frame color
        
        self.configure(fg_color=self.selected_color if is_selected else self.default_color)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Button-3>", self._show_header_menu)
        
        self.grid_columnconfigure(0, weight=1)
        
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 2))
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.bind("<Button-1>", self._on_click, add=True)
        header_frame.bind("<Button-3>", self._show_header_menu, add=True)

        chan_label = ctk.CTkLabel(header_frame, text=f"Channel {channel_idx + 1}", font=ctk.CTkFont(weight="bold"))
        chan_label.grid(row=0, column=0, sticky="w")
        chan_label.bind("<Button-1>", self._on_click, add="+")
        chan_label.bind("<Button-3>", self._show_header_menu, add="+")
        
        # Header Context Menu
        self.header_menu = tk.Menu(self, tearoff=0)
        self.header_menu.add_command(label="Delete Channel", command=lambda: self.on_delete_channel_callback(self.channel_idx))

        # Filters list (display only; CRUD via context menu)
        self.filters_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filters_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        self.filters_frame.bind("<Button-1>", self._on_click, add=True)
        self.filters_frame.bind("<Button-3>", self._show_header_menu, add=True)
        
        if not channel.filters:
            lbl = ctk.CTkLabel(self.filters_frame, text="(Empty)", text_color="gray", font=ctk.CTkFont(size=11))
            lbl.grid(row=0, column=0, sticky="w")
            lbl.bind("<Button-1>", self._on_click, add="+")
            lbl.bind("<Button-3>", self._show_header_menu, add="+")
        else:
            for i, flt in enumerate(channel.filters):
                text = f"• {flt.material} ({flt.thickness*1e4:.1f} µm)"
                if flt.density:
                    text += f" [{flt.density} g/cm³]"

                lbl = ctk.CTkLabel(self.filters_frame, text=text, anchor="w")
                lbl.grid(row=i, column=0, sticky="w")
                lbl.bind("<Button-1>", self._on_click, add="+")
                lbl.bind("<Button-3>", lambda e, f_idx=i: self._show_filter_menu(e, f_idx), add="+")

    def _on_click(self, event):
        self.on_select_callback(self.channel_idx)

    def _show_header_menu(self, event):
        try:
            self.header_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.header_menu.grab_release()

    def _show_filter_menu(self, event, filter_idx):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Edit Filter", command=lambda: self.on_edit_filter_callback(self.channel_idx, filter_idx))
        menu.add_command(label="Delete Filter", command=lambda: self.on_delete_filter_callback(self.channel_idx, filter_idx))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()


class RossFilterGUI:
    def __init__(self, calculator: RossFilterCalculator):
        self.calculator = calculator
        self.window = ctk.CTk()
        self.window.title("Ross Filter Calculator")
        self.window.geometry("1400x900")
        self.difference_count = 0
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.selected_channel_idx = -1
        self.editing_filter_idx = None # (channel_idx, filter_idx) or None
        self.selection_panel = None
        self._channel_refresh_job = None
        self._channel_refresh_preserve = True

        # Main Layout
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.left_panel = ctk.CTkFrame(self.window, width=400, corner_radius=0)
        self.left_panel.grid(row=0, column=0, sticky="nsew")
        self.left_panel.grid_propagate(False)

        self.right_panel = ctk.CTkFrame(self.window, corner_radius=0)
        self.right_panel.grid(row=0, column=1, sticky="nsew")

        self._setup_left_panel()
        self._setup_right_panel()
        
        # Initial state
        self._refresh_channel_list()
        self._update_filter_creator_state()

    def _setup_left_panel(self):
        self.left_panel.grid_columnconfigure(0, weight=1)
        self.left_panel.grid_rowconfigure(2, weight=1) # Channel list expands

        # 1. Energy Settings
        self.energy_frame = ctk.CTkFrame(self.left_panel)
        self.energy_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self._setup_energy_controls()

        # 2. Channel Management Header
        self.channel_header_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.channel_header_frame.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="ew")
        
        lbl = ctk.CTkLabel(self.channel_header_frame, text="Channels", font=ctk.CTkFont(size=16, weight="bold"))
        lbl.pack(side="left")
        
        add_btn = ctk.CTkButton(self.channel_header_frame, text="+ Add Channel", width=100, command=self._add_channel)
        add_btn.pack(side="right")

        # 3. Channel List
        self.channel_list_frame = ctk.CTkScrollableFrame(self.left_panel)
        self.channel_list_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        # 4. Filter Creator
        self.filter_creator_frame = ctk.CTkFrame(self.left_panel)
        self.filter_creator_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self._setup_filter_creator()

        # 5. Actions
        self.action_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.action_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        
        self.calc_btn = ctk.CTkButton(self.action_frame, text="Calculate Filter Bands", height=40, command=self._calculate)
        self.calc_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        self.reset_btn = ctk.CTkButton(self.action_frame, text="Reset", width=80, height=40, fg_color="darkred", hover_color="red", command=self._reset)
        self.reset_btn.pack(side="right", padx=(5, 0))

        # 6. Console
        self.console = ctk.CTkTextbox(self.left_panel, height=120, font=ctk.CTkFont(size=12))
        self.console.grid(row=5, column=0, padx=10, pady=10, sticky="ew")
        self.console.insert("1.0", "Welcome to Ross Filter Calculator.\nAdd channels and filters to begin.\n")

    def _setup_energy_controls(self):
        self.energy_frame.grid_columnconfigure((1, 3, 5), weight=1)
        
        ctk.CTkLabel(self.energy_frame, text="Energy (keV)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=6, pady=5)
        
        ctk.CTkLabel(self.energy_frame, text="Start:").grid(row=1, column=0, padx=5)
        self.energy_start = ctk.CTkEntry(self.energy_frame, width=60)
        self.energy_start.insert(0, "0.1")
        self.energy_start.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(self.energy_frame, text="Stop:").grid(row=1, column=2, padx=5)
        self.energy_stop = ctk.CTkEntry(self.energy_frame, width=60)
        self.energy_stop.insert(0, "20.0")
        self.energy_stop.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(self.energy_frame, text="Step:").grid(row=1, column=4, padx=5)
        self.energy_step = ctk.CTkEntry(self.energy_frame, width=60)
        self.energy_step.insert(0, "0.5")
        self.energy_step.grid(row=1, column=5, padx=5, pady=5, sticky="ew")

    def _setup_filter_creator(self):
        self.filter_creator_frame.grid_columnconfigure(1, weight=1)
        
        self.creator_label = ctk.CTkLabel(self.filter_creator_frame, text="Add Filter", font=ctk.CTkFont(weight="bold"))
        self.creator_label.grid(row=0, column=0, columnspan=2, pady=5)
        
        ctk.CTkLabel(self.filter_creator_frame, text="Material:").grid(row=1, column=0, padx=10, sticky="w")
        self.material_combo = AutocompleteComboBox(self.filter_creator_frame, values=get_material_list())
        self.material_combo.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(self.filter_creator_frame, text="Thickness (µm):").grid(row=2, column=0, padx=10, sticky="w")
        self.thickness_var = ctk.StringVar(value="0.0")
        self.thickness_entry = ctk.CTkEntry(self.filter_creator_frame, textvariable=self.thickness_var)
        self.thickness_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.filter_creator_frame, text="Density (g/cm³):").grid(row=3, column=0, padx=10, sticky="w")
        self.density_var = ctk.StringVar(value="")
        self.density_entry = ctk.CTkEntry(self.filter_creator_frame, textvariable=self.density_var, placeholder_text="Optional")
        self.density_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.filter_creator_frame, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.preview_btn = ctk.CTkButton(btn_frame, text="Preview", command=self._preview_filter, fg_color="gray")
        self.preview_btn.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.add_filter_btn = ctk.CTkButton(btn_frame, text="Add Filter", command=self._add_filter)
        self.add_filter_btn.grid(row=0, column=1, padx=5, sticky="ew")

    def _setup_right_panel(self):
        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=3)
        self.right_panel.grid_columnconfigure(1, weight=1)

        self.plot_manager = PlotManager(self.right_panel)
        self.plot_manager.widget.grid(row=0, column=0, sticky="nsew")

        self.selection_panel = PlotSelectionPanel(self.right_panel, on_change=self._on_selection_changed)
        self.selection_panel.grid(row=0, column=1, sticky="ns", padx=8, pady=8)

    def _log(self, msg):
        self.console.insert("end", f"{msg}\n")
        self.console.see("end")

    def _add_channel(self):
        idx = self.calculator.add_channel()
        self._log(f"Added Channel {idx + 1}")
        self.selected_channel_idx = idx
        self.difference_count = 0
        self._request_channel_refresh()
        self._update_filter_creator_state()

    def _select_channel(self, idx):
        self.selected_channel_idx = idx
        self.editing_filter_idx = None
        self._request_channel_refresh() # To update selection visuals
        self._update_filter_creator_state()

    def _refresh_channel_list(self, preserve_selection=True):
        for widget in self.channel_list_frame.winfo_children():
            widget.destroy()

        for i, channel in enumerate(self.calculator.channels):
            cw = ChannelWidget(
                self.channel_list_frame, 
                channel_idx=i, 
                channel=channel, 
                on_select_callback=self._select_channel,
                on_delete_channel_callback=self._delete_channel,
                on_edit_filter_callback=self._edit_filter,
                on_delete_filter_callback=self._delete_filter,
                is_selected=(i == self.selected_channel_idx)
            )
            cw.pack(fill="x", pady=2)

        self._refresh_selection_panel(preserve_selection=preserve_selection)

    def _refresh_selection_panel(self, preserve_selection=True):
        if not self.selection_panel:
            return

        differences = []
        for i in range(self.difference_count):
            label = f"Diff {i + 1}-{i + 2}"
            key = ("diff", i)
            differences.append((label, key))

        self.selection_panel.refresh(
            self.calculator.channels,
            differences=differences,
            preserve_selection=preserve_selection
        )

    def _request_channel_refresh(self, preserve_selection=True):
        self._channel_refresh_preserve = self._channel_refresh_preserve and preserve_selection
        if self._channel_refresh_job is None:
            self._channel_refresh_job = self.window.after_idle(self._perform_channel_refresh)

    def _perform_channel_refresh(self):
        self._channel_refresh_job = None
        preserve = self._channel_refresh_preserve
        self._channel_refresh_preserve = True
        self._refresh_channel_list(preserve_selection=preserve)

    def _update_filter_creator_state(self):
        if self.selected_channel_idx >= 0 and self.selected_channel_idx < len(self.calculator.channels):
            if self.editing_filter_idx:
                self.creator_label.configure(text=f"Edit Filter (Ch {self.editing_filter_idx[0]+1}, Flt {self.editing_filter_idx[1]+1})")
                self.add_filter_btn.configure(text="Update Filter", state="normal")
            else:
                self.creator_label.configure(text=f"Add Filter to Channel {self.selected_channel_idx + 1}")
                self.add_filter_btn.configure(text="Add Filter", state="normal")
                
            self.material_combo.configure(state="normal")
            self.thickness_entry.configure(state="normal")
            self.density_entry.configure(state="normal")
            self.preview_btn.configure(state="normal")
        else:
            self.creator_label.configure(text="Select a Channel to Add Filter")
            self.material_combo.configure(state="disabled")
            self.thickness_entry.configure(state="disabled")
            self.density_entry.configure(state="disabled")
            self.preview_btn.configure(state="disabled")
            self.add_filter_btn.configure(state="disabled")

    def _add_filter(self):
        if self.selected_channel_idx < 0:
            return
            
        material = self.material_combo.get()
        try:
            thickness = float(self.thickness_var.get())
        except ValueError:
            self._log("Error: Invalid thickness")
            return
        
        density_str = self.density_var.get().strip()
        try:
            density = float(density_str) if density_str else None
        except ValueError:
            self._log("Error: Invalid density")
            return

        if self.editing_filter_idx:
            # Update existing
            c_idx, f_idx = self.editing_filter_idx
            success, msg = self.calculator.update_filter_in_channel(c_idx, f_idx, material, thickness, density)
            if success:
                self._log(f"Updated Filter in Channel {c_idx + 1}")
                self.editing_filter_idx = None # Exit edit mode
            else:
                self._log(f"Error: {msg}")
        else:
            # Add new
            success, msg = self.calculator.add_filter_to_channel(self.selected_channel_idx, material, thickness, density)
            if success:
                self._log(f"Added {material} ({thickness} µm) to Channel {self.selected_channel_idx + 1}")
            else:
                self._log(f"Error: {msg}")

        if success:
            self.difference_count = 0
            self._request_channel_refresh()
            self._update_filter_creator_state()
            self._plot_selected_series()

    def _get_energy_range(self):
        try:
            start = float(self.energy_start.get())
            stop = float(self.energy_stop.get())
            step = float(self.energy_step.get())
            return start, stop, step
        except ValueError:
            return None

    def _delete_channel(self, channel_idx):
        success, msg = self.calculator.remove_channel(channel_idx)
        if success:
            self._log(msg)
            if self.selected_channel_idx == channel_idx:
                self.selected_channel_idx = -1
            elif self.selected_channel_idx > channel_idx:
                self.selected_channel_idx -= 1
            self.difference_count = 0
            self._request_channel_refresh()
            self._update_filter_creator_state()
        else:
            self._log(f"Error: {msg}")

    def _delete_filter(self, channel_idx, filter_idx):
        success, msg = self.calculator.remove_filter_from_channel(channel_idx, filter_idx)
        if success:
            self._log(msg)
            self.difference_count = 0
            self._request_channel_refresh()
            self._plot_selected_series()
        else:
            self._log(f"Error: {msg}")

    def _edit_filter(self, channel_idx, filter_idx):
        self.selected_channel_idx = channel_idx
        self.editing_filter_idx = (channel_idx, filter_idx)
        
        channel = self.calculator.channels[channel_idx]
        flt = channel.filters[filter_idx]
        
        self.material_combo.set(flt.material)
        self.thickness_var.set(str(flt.thickness * 1e4)) # cm to um
        self.density_var.set(str(flt.density) if flt.density else "")
        
        self._request_channel_refresh()
        self._update_filter_creator_state()
        self._log(f"Editing Filter {filter_idx + 1} in Channel {channel_idx + 1}")

    def _preview_filter(self):
        # Calculate transmission for just this filter
        material = self.material_combo.get()
        try:
            thickness_um = float(self.thickness_var.get())
            thickness_cm = um_to_cm(thickness_um)
        except ValueError:
            self._log("Error: Invalid thickness")
            return

        density_str = self.density_var.get().strip()
        try:
            density = float(density_str) if density_str else None
        except ValueError:
            self._log("Error: Invalid density")
            return

        erange = self._get_energy_range()
        if not erange:
            self._log("Error: Invalid energy range")
            return
        
        start, stop, step = erange
        energies_kev = np.arange(start, stop + step, step)
        energies_ev = kev_to_ev(energies_kev)
        
        try:
            # Create a temporary filter to calc transmission
            # We can use the Channel logic or direct calculation
            energies_ev = np.asarray(energies_ev)  # Ensure it's always an array
            mu = np.array([xraydb.material_mu(material, e, density=density) for e in energies_ev])
            transmission = np.exp(-mu * thickness_cm)
            
            self.plot_manager.clear(title="Preview")
            self.plot_manager.plot_series(energies_kev, transmission, label='Preview', style='--', color='gray', alpha=0.7)
            self.plot_manager.draw()
            self._log(f"Previewing {material} ({thickness_um} µm)")
            
        except Exception as e:
            self._log(f"Preview Error: {str(e)}")

    def _calculate(self):
        erange = self._get_energy_range()
        if not erange:
            self._log("Error: Invalid energy range")
            return
            
        success, result = self.calculator.calculate_transmission(*erange)
        
        if success:
            self.difference_count = len(result.differences)
            self._refresh_selection_panel(preserve_selection=False)
            if self.selection_panel:
                self.selection_panel.set_selected_keys([], exclusive=True)

            self.plot_manager.clear(title="Ross Filter Transmission")
            self.plot_manager.draw()
            self._log("Filter bands calculated. Select items to plot from Plot Selection.")
        else:
            self.difference_count = 0
            self._refresh_selection_panel(preserve_selection=True)
            self._log(f"Error: {result}")

    def _reset(self):
        self.calculator.reset()
        self.selected_channel_idx = -1
        self.editing_filter_idx = None
        self.difference_count = 0
        self._request_channel_refresh(preserve_selection=False)
        self._update_filter_creator_state()
        self._refresh_selection_panel(preserve_selection=False)
        if self.selection_panel:
            self.selection_panel.set_selected_keys([], exclusive=True)
        self.plot_manager.clear(title="Ross Filter Transmission")
        self.plot_manager.draw()
        self._log("Reset all channels.")

    def _on_selection_changed(self, keys):
        self._plot_selected_series(keys)

    def _plot_selected_series(self, selected_keys=None):
        erange = self._get_energy_range()
        if not erange:
            self._log("Error: Invalid energy range")
            return

        start, stop, step = erange
        energies_kev = np.arange(start, stop + step, step)
        energies_ev = kev_to_ev(energies_kev)

        try:
            selected = selected_keys if selected_keys is not None else (
                self.selection_panel.get_selected_keys() if self.selection_panel else []
            )

            self.plot_manager.clear(title="Selected Transmissions")

            if not selected:
                self.plot_manager.draw()
                return

            for key in selected:
                if key[0] == "channel":
                    c_idx = key[1]
                    channel = self.calculator.channels[c_idx]
                    transmission = channel.calculate_transmission(energies_ev)
                    label = f"Channel {c_idx + 1}"
                    self.plot_manager.plot_series(energies_kev, transmission, label=label)
                elif key[0] == "filter":
                    c_idx, f_idx = key[1], key[2]
                    channel = self.calculator.channels[c_idx]
                    transmission = channel.calculate_single_filter(f_idx, energies_ev)
                    flt = channel.filters[f_idx]
                    label = f"Ch {c_idx + 1}: {flt.material}"
                    self.plot_manager.plot_series(energies_kev, transmission, label=label)
                elif key[0] == "diff":
                    d_idx = key[1]
                    if d_idx + 1 < len(self.calculator.channels):
                        ch1 = self.calculator.channels[d_idx]
                        ch2 = self.calculator.channels[d_idx + 1]
                        t1 = ch1.calculate_transmission(energies_ev)
                        t2 = ch2.calculate_transmission(energies_ev)
                        diff = np.abs(t1 - t2)
                        label = f"Diff {d_idx + 1}-{d_idx + 2}"
                        self.plot_manager.plot_series(energies_kev, diff, label=label, style="--")
                        self.plot_manager.fill_between(energies_kev, diff, alpha=0.2)

            self.plot_manager.draw()
        except Exception as e:
            self._log(f"Plot Error: {str(e)}")

    def run(self):
        self.window.mainloop()

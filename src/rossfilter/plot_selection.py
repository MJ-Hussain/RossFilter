import customtkinter as ctk


class PlotSelectionPanel(ctk.CTkFrame):
    """Checkbox-based series selector for channels, filters, and differences."""

    def __init__(self, master, on_change):
        super().__init__(master, fg_color="transparent")
        self.on_change = on_change
        self._variables: dict[tuple, ctk.BooleanVar] = {}

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 4))

        title = ctk.CTkLabel(header, text="Plot Selection", font=ctk.CTkFont(size=14, weight="bold"))
        title.pack(side="left")

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")

        self.select_all_btn = ctk.CTkButton(btn_frame, text="All", width=40, command=self._select_all)
        self.select_all_btn.pack(side="left", padx=2)

        self.clear_btn = ctk.CTkButton(btn_frame, text="Clear", width=60, command=self._clear_selection)
        self.clear_btn.pack(side="left", padx=2)

        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", height=220)
        self.list_frame.pack(fill="both", expand=True)

    def refresh(self, channels, differences=None, preserve_selection=True):
        differences = differences or []
        existing_selected = set(self.get_selected_keys()) if preserve_selection else set()

        for child in self.list_frame.winfo_children():
            child.destroy()
        self._variables.clear()

        for c_idx, channel in enumerate(channels):
            chan_key = ("channel", c_idx)
            chan_label = f"Channel {c_idx + 1}"
            self._add_checkbox(chan_label, chan_key, padx=4, pady=2)
            for f_idx, flt in enumerate(channel.filters):
                flt_key = ("filter", c_idx, f_idx)
                flt_label = f"   • {flt.material} ({flt.thickness * 1e4:.1f} µm)"
                self._add_checkbox(flt_label, flt_key, padx=10, pady=1)

        if differences:
            divider = ctk.CTkLabel(self.list_frame, text="Differences", anchor="w", font=ctk.CTkFont(weight="bold"))
            divider.pack(fill="x", padx=4, pady=(6, 2))
            for label, key in differences:
                self._add_checkbox(f"   • {label}", key, padx=10, pady=1)

        if existing_selected:
            self.set_selected_keys([k for k in existing_selected if k in self._variables], exclusive=True)
        else:
            self.list_frame.update_idletasks()

    def _add_checkbox(self, label, key, padx=4, pady=2):
        var = ctk.BooleanVar(value=False)
        cb = ctk.CTkCheckBox(self.list_frame, text=label, variable=var, command=self._notify)
        cb.pack(anchor="w", padx=padx, pady=pady)
        self._variables[key] = var

    def _notify(self):
        if self.on_change:
            self.on_change(self.get_selected_keys())

    def get_selected_keys(self):
        return [key for key, var in self._variables.items() if var.get()]

    def set_selected_keys(self, keys, exclusive=True):
        if exclusive:
            for var in self._variables.values():
                var.set(False)
        for key in keys:
            if key in self._variables:
                self._variables[key].set(True)
        self._notify()

    def _select_all(self):
        for var in self._variables.values():
            var.set(True)
        self._notify()

    def _clear_selection(self):
        for var in self._variables.values():
            var.set(False)
        self._notify()

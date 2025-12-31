import customtkinter as ctk
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class PlotManager:
    """Wrap Matplotlib figure + toolbar for the RossFilter GUI."""

    def __init__(self, master):
        self.container = ctk.CTkFrame(master, corner_radius=0)

        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self._configure_axes(title="Ross Filter Transmission")

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.container)
        self.toolbar.update()

    @property
    def widget(self):
        return self.container

    def clear(self, title: str | None = None):
        self.ax.clear()
        self._configure_axes(title=title)

    def _configure_axes(self, title: str | None = None):
        self.ax.set_xlabel("Energy (keV)")
        self.ax.set_ylabel("Transmission")
        if title:
            self.ax.set_title(title)
        self.ax.grid(True)

    def plot_series(self, energies_kev, transmission, *, label=None, style="-", color=None, alpha=1.0):
        self.ax.plot(energies_kev, transmission, linestyle=style, label=label, color=color, alpha=alpha)

    def fill_between(self, energies_kev, lower, upper=None, *, alpha=0.2, color=None, label=None):
        upper = upper if upper is not None else 0
        self.ax.fill_between(energies_kev, lower, upper, alpha=alpha, color=color, label=label)

    def draw(self):
        if self.ax.get_legend_handles_labels()[1]:
            self.ax.legend()
        self.canvas.draw()

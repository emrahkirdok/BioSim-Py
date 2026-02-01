import matplotlib.pyplot as plt
import threading

class Analytics:
    def __init__(self):
        self.history = {
            "generation": [],
            "survivors": [],
            "kills": [],
            "avg_len": []
        }
        self.fig = None
        self.axes = None
        self.is_open = False

    def add_data(self, gen, survivors, kills, avg_len):
        self.history["generation"].append(gen)
        self.history["survivors"].append(survivors)
        self.history["kills"].append(kills)
        self.history["avg_len"].append(avg_len)
        
        if self.is_open:
            self.update_plot()

    def open_window(self):
        if self.is_open: return
        
        # We must run matplotlib in the main thread or a dedicated UI thread.
        # However, plt.show() can be non-blocking with plt.ion()
        plt.ion() 
        self.fig, self.axes = plt.subplots(3, 1, figsize=(6, 8), constrained_layout=True)
        self.fig.canvas.manager.set_window_title('BioSim-Py Analytics')
        self.is_open = True
        self.update_plot()

    def update_plot(self):
        if not self.is_open: return
        
        ax1, ax2, ax3 = self.axes
        gens = self.history["generation"]
        
        # 1. Population Graph
        ax1.clear()
        ax1.plot(gens, self.history["survivors"], color='green', label='Survivors')
        ax1.set_title("Population Survival")
        ax1.set_ylabel("Count")
        ax1.grid(True, alpha=0.3)
        
        # 2. Kill Count
        ax2.clear()
        ax2.plot(gens, self.history["kills"], color='red', label='Kills')
        ax2.set_title("Predation Events")
        ax2.set_ylabel("Count")
        ax2.grid(True, alpha=0.3)
        
        # 3. Genome Length
        ax3.clear()
        ax3.plot(gens, self.history["avg_len"], color='blue', label='Avg Genes')
        ax3.set_title("Evolutionary Complexity")
        ax3.set_xlabel("Generation")
        ax3.set_ylabel("Genes")
        ax3.grid(True, alpha=0.3)

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def close_window(self):
        if self.is_open:
            plt.close(self.fig)
            self.is_open = False

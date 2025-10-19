import tkinter as tk
import asyncio
import threading
import logging
from tkinter import ttk
from utils.decorators import log_block, log_block_async

from controller.simulation_controller import SimulationController

class SimulationGUI(tk.Tk):
    def __init__(self, controller: SimulationController = None):
        super().__init__()
        self.title("Simulation Controller")
        self.minsize(500, 400)
        self.maxsize(800, 600)
        self.loop = None
        self.thread = None
        self.controller = SimulationController(config_path="config/settings.ini") if controller is None else controller

        self.setup_widgets()
        # self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_widgets(self):
        frame = ttk.Frame(self, width=400, height=300, padding=10, relief="ridge")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.start_button = ttk.Button(frame, text="Start Simulation", command=self.start_simulation)
        self.start_button.grid(row=0, column=0, padx=5, pady=5)

        self.stop_button = ttk.Button(frame, text="Stop Simulation", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)

    @log_block
    def start_simulation(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Create a new event loop and a thread, because tkinter is not async-aware
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_async_loop)
        # Set the thread as a daemon to allow the program to exit without waiting for this thread to finish
        self.thread.daemon = True
        self.thread.start()

    @log_block
    def stop_simulation(self):
        self.stop_button.config(state=tk.DISABLED)

        # Safely stop the event loop from the main thread
        if self.loop and self.loop.is_running():
            future = asyncio.run_coroutine_threadsafe(self.controller.stop_simulation(), self.loop)
            # Wait for the stop operation to complete
            try:
                future.result(timeout=5)
            except Exception as e:
                logging.error(f"Error stopping simulation: {e}")

        self.start_button.config(state=tk.NORMAL)

    @log_block
    def _run_async_loop(self):
        asyncio.set_event_loop(self.loop)
        try:
            # Run the simulation until it's complete or stopped (equivalent to await)
            self.loop.run_until_complete(self.controller.start_simulation())
        except Exception as e:
            logging.error(f"Asyncio loop error: {e}")
        finally:
            # Clean up the loop
            if self.loop and not self.loop.is_closed():
                self.loop.close()
            # Update GUI state in the main thread after stopping the simulation
            self.after(0, self._on_simulation_stopped)

    @log_block
    def _on_simulation_stopped(self):
        """Called when simulation stops to update UI state"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    @log_block
    def on_closing(self):
        """Handle window closing"""
        if self.controller.is_running:
            self.stop_simulation()
        self.destroy()
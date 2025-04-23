import customtkinter as ctk

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")  # Options: "dark", "light", "system"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("CustomTkinter Basic Example")
        self.geometry("400x200")
        
        # Create a frame for better layout
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Create a label
        self.label = ctk.CTkLabel(self.frame, text="CustomTkinter Basic Example", 
                                font=ctk.CTkFont(size=20, weight="bold"))
        self.label.pack(pady=(0, 20))
        
        # Create a button tied to button_function
        self.button = ctk.CTkButton(self.frame, text="Click Me!", command=self.button_function)
        self.button.pack(pady=10)
        
    def button_function(self):
        """Function that runs when the button is clicked"""
        print("Button clicked!")
        # Update the label text when button is clicked
        self.label.configure(text="Button was clicked!")
        
# if __name__ == "__main__":
#     app = App()
#     app.mainloop()
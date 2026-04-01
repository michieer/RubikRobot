import tkinter as tk

_root = None
_results_text = None

def init_logger(root, text_widget):
    #Initialiseer de logger met de Tk root en de Text widget.
    global _root, _results_text
    _root = root
    _results_text = text_widget

def log(message):
    #Voeg een bericht toe aan de Text widget en scroll naar beneden.
    if _root is None or _results_text is None:
        print(message)
        return

    def append():
        _results_text.insert("end", str(message) + "\n")
        _results_text.see("end")

    _root.after(0, append)
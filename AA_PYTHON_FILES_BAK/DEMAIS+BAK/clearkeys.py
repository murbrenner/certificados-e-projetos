import keyboard
import pyautogui
def clear_all_keys_pressed():
    # Define the list of keys to check
    keys_to_check = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
                     "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                     "u", "v", "w", "x", "y", "z", "enter", "esc",
                     "space", "shift", "ctrl", "alt"]

    # Release each key if it is pressed
    for key in keys_to_check:
        if keyboard.is_pressed(key):
            pyautogui.keyUp(key)
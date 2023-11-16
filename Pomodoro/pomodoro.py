from tkinter import *
from tkinter.font import BOLD
import math

# ---------------------------- CONSTANTS ------------------------------- #
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"
WORK_MIN = 30*60
SHORT_BREAK_MIN = 5*60
LONG_BREAK_MIN = 20*60
repetitions = 0
timer = None


window = Tk()
window.title("pomodoro")
window.config(padx=100, pady=50, bg=PINK)


def count_down(count):
    global timer
    count_min = math.floor(count / 60)
    count_sec = count % 60
    if count_sec < 10:
        count_sec = f"0{count_sec}"
    
    canvas.itemconfig(timer_text, text=f"{count_min}:{count_sec}")
    if count > 0:
        timer = window.after(1000, count_down, count-1)
    else:
        start_timer()
        mark = ""
        sessions = math.floor(repetitions/2)
        for _ in range(sessions):
            mark += "✓"
        check_button.config(text=mark)


def start_timer():
    global repetitions
    repetitions += 1

    work_sec = WORK_MIN
    short_break_sec = SHORT_BREAK_MIN
    long_break_sec = LONG_BREAK_MIN

    if repetitions % 8 == 0:
        count_down(long_break_sec)
        timer_label.config(text="Break", fg=RED)      
    elif repetitions % 2 == 0:
        count_down(short_break_sec)
        timer_label.config(text="Break", fg=RED)      
    else:
        count_down(work_sec)
        timer_label.config(text="Work", fg=GREEN)
        

def reset_timer():
    global repetitions
    window.after_cancel(timer)
    canvas.itemconfig(timer_text, text="00:00")
    timer_label.config(text="Timer")
    check_button.config(text="")
    repetitions = 0


canvas = Canvas(width=200, height=224, bg=PINK, highlightthickness=0)
tomato_image = PhotoImage(file="tomato.png")
canvas.create_image(100, 112, image=tomato_image)
timer_text = canvas.create_text(100, 130, text="00:00", fill="white", font=(FONT_NAME, 32, BOLD))
canvas.grid(column=1, row=1)

timer_label = Label(text="Timer", font=(FONT_NAME, 50, BOLD), fg=YELLOW, bg=PINK, highlightthickness=0)
timer_label.grid(column=1, row=0)

start_button = Button(text="Start", highlightthickness=0, command=start_timer)
start_button.grid(column=0, row=2)

reset_button = Button(text="Reset", highlightthickness=0, command=reset_timer)
reset_button.grid(column=2, row=2)

check_button = Label(fg=GREEN, bg=PINK, font=30)
check_button.grid(column=1, row=3)


window.mainloop()

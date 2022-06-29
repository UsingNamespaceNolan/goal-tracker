import tkinter as tk
import os
from tkinter import messagebox
import json

LOGFILE = '/Users/nolanjohnston/PyCharmProjects/OnTrack/goals.json'

class MainWindow:
    def __init__(self, parent):
        # set title and window size
        self.parent = parent
        self.parent.title("On Track")

        # configure grid on main window
        self.parent.rowconfigure(0, weight=1)
        self.parent.rowconfigure(1, weight=1)
        self.parent.rowconfigure(2, weight=1)

        self.parent.columnconfigure(0, weight=1)

        # create main window frames
        self.top_frame = tk.Frame(parent)
        self.middle_frame = tk.Frame(parent)
        self.bottom_frame = tk.Frame(parent)
        self.top_frame.grid(row=0, column=0, sticky='nsew')
        self.top_frame.columnconfigure((0, 1, 2), weight=1)
        self.middle_frame.grid(row=1, column=0, sticky='nsew')
        self.middle_frame.columnconfigure((0, 1, 2), weight=1)
        self.bottom_frame.grid(row=2, column=0, sticky='nsew')
        self.bottom_frame.columnconfigure((0, 1, 2), weight=1)

        # create main window widgets
        self.goal_list = tk.Listbox(self.middle_frame, bg="white")
        self.goal_list.bind('<Double-Button>', lambda event: ShowGoal(self, event))
        self.goal_list.grid(column=1)

        initialize_goal_list(self.goal_list)

        self.goal_label = tk.Label(self.middle_frame, text="Current Goals  ")
        self.goal_label.grid(row = 0, column=0, sticky='n')

        self.create_button = tk.Button(self.top_frame, text="Create New Goal", command=lambda: NewGoalWindow(self))
        self.create_button.grid(column=2)

        self.bottom_frame_spacer = tk.Label(self.bottom_frame, text='\t  ')
        self.bottom_frame_spacer.grid(column=0, row=0)

        self.complete_goal_button = tk.Button(self.bottom_frame, text="Complete Goal", command=lambda: self.complete_goal())
        self.complete_goal_button.grid(column=1, row=0)

        self.delete_goal_button = tk.Button(self.bottom_frame, text="Delete Goal", command=lambda: delete_goal(self.goal_list))
        self.delete_goal_button.grid(column=2, row=0)


    def complete_goal(self):
        selection = self.goal_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a goal to complete!")


class ShowGoal:
    def __init__(self, root_window, event):
        goal_name = root_window.goal_list.get(root_window.goal_list.curselection())

        show_goal_window = tk.Toplevel(root_window.parent)
        show_goal_window.title(goal_name)

        goal_descr, goal_steps = get_goal_data(goal_name)

        tk.Label(show_goal_window, text=goal_descr).grid(row=0, column=0)
        tk.Label(show_goal_window, text=goal_steps).grid(row=1, column=0)


class NewGoalWindow:
    def __init__(self, root_window):
        self.goal_window = tk.Toplevel(root_window.parent)
        self.goal_window.title("Create Goal")

        # add labels indicating where to input stuff
        tk.Label(self.goal_window, text="Goal Name: ").grid(row=0, column=0)
        tk.Label(self.goal_window, text="Goal description: ").grid(row=1, column=0)
        tk.Label(self.goal_window, text="Goal steps (optional): ").grid(row=5, column=0)

        # add entry boxes for user input
        self.name_entry = tk.Text(self.goal_window, height=1)
        self.descr_entry = tk.Text(self.goal_window, height=4)
        self.step_entry = tk.Text(self.goal_window, height=2)
        step_add = tk.Button(self.goal_window, text="Add Step")

        self.name_entry.grid(row=0, column=1)
        self.descr_entry.grid(row=1, column=1, rowspan=4)
        self.step_entry.grid(row=5, column=1, rowspan=2)
        step_add.grid(row=5, column=2, rowspan=2)

        tk.Button(self.goal_window, text="Done Creating Goal",
                  command=lambda: update_goals(self, root_window.goal_list)).grid(row=7, column=1)


def delete_goal(goal_list) -> int:
    """If a goal in the main listbox is selected, delete_goal removes it from the log file and the listbox.
    Returns the length of the new list.

    :param goal_list: an instance of listbox widget
    """
    selection = goal_list.curselection()
    goal_key = goal_list.get(selection[0])

    if not selection:
        messagebox.showwarning("Warning", "Select a goal to delete")

    goal_list.delete(selection)

    with open(LOGFILE, 'r+') as log_file:
        goals = json.loads(''.join(log_file.readlines()))
        goals.pop(goal_key)
        open(LOGFILE, 'w').close()
        json.dump(goals, log_file)

    return goal_list.size()


def get_goal_data(goal_name):
    with open(LOGFILE, 'r') as goal_file:
        goals = goal_file.readlines()

        return 'No description found', 'No steps found'


def update_goals(window_object, goal_list):
    goal_name = window_object.name_entry.get("1.0", "end-1c")
    goal_description = window_object.descr_entry.get("1.0", "end-1c")
    goal_steps = window_object.step_entry.get("1.0", "end-1c")

    goal_list.insert(goal_list.size(), goal_name)

    json_goal = {goal_name: (goal_description, goal_steps)}
    curr_goals = ''

    with open(LOGFILE, 'r') as log_file:
        goals = log_file.readlines()
        if goals:
            curr_goals = ''.join(goals)

    with open(LOGFILE, 'w') as log_file:
        if not curr_goals or curr_goals.isspace():
            json.dump(json_goal, log_file)
        else:
            goals = json.loads(curr_goals[curr_goals.index('{'):])
            goals.update(json_goal)
            print(type(goals))
            json.dump(goals, log_file)

    window_object.goal_window.destroy()


def initialize_goal_list(goal_list):
    """initialize_goal_list reads a log file for goals that the user previously inputted and displays
    them in the main application listbox.
    """
    if not os.stat(LOGFILE).st_size:
        return None

    with open(LOGFILE, 'r') as goal_file:
        goals = ''.join(goal_file.readlines())

        if not goals or goals.isspace():
            return None

        goal_data = json.loads(goals[goals.index('{'):])

        for ind, goal_name in enumerate(goal_data):
            goal_list.insert(ind, goal_name)

def main():
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()

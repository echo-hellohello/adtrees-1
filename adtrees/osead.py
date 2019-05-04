'''
https://www.tutorialspoint.com/python/python_gui_programming.htm

https://likegeeks.com/python-gui-examples-tkinter-tutorial
https://www.python-course.eu/tkinter_layout_management.php

https://www.tutorialspoint.com/python/tk_relief.htm
'''
# from adtrees.adnode import ADNode
from adtrees.adtree import ADTree
from adtrees.attribute_domain import AttrDomain
from adtrees.basic_assignment import BasicAssignment
from adtrees.pareto_domain import ParetoDomain
from adtrees.default_domains import minCost, minDiff, maxProb
from adtrees.optimizers import optimal_attacks
try:
    from adtrees.linear_programming import ADTilp
    ILP_POSSIBLE = 1
    from adtrees.optimizers import optimal_countermeasures
except:
    ILP_POSSIBLE = 0

from tkinter import *
from adtrees.utils import read_val_from_grid, get_widget_from_grid
from time import ctime
# from tkinter.ttk import Combobox

# #global variables


class osead_gui():
    # global variables :)

    def __init__(self):
        self.window = Tk()  # the main window :(
        self.root = Toplevel(self.window)
        # self.root = Tk()  # the basic assignment window :(
        self.root.withdraw()
        self.col_width = 30
        self.TREE = ADTree()
        self.BASIC_ASSIGNMENT = BasicAssignment()
        self.TREE_LOADED = 0
        self.FILE_SELECTED = StringVar()
        self.FILE_SELECTED.set('no file selected')
        self.TREE_LOADED_MSG = "Path to currently loaded tree:"
        self.TASK_SELECTED = IntVar()
        self.TASK_SELECTED.set(0)
        self.ASSIGNMENTS_WINDOW_OPEN = False
        self.ASSIGNMENTS_WINDOW_OPENED_BEFORE = False
        self.ATTACKERS_BAS = []
        self.DEFENDERS_BAS = []
        self.ATTACKERS_ACTIONS_NUMBER = 0
        self.DEFENDERS_ACTIONS_NUMBER = 0
        self.DOMAIN = None
        self.DEF_CHECKBOXES_VARIABLES = []
        self.LAST_SELECTED_TASK = None
        self.PATH = StringVar()
        self.SET_SEM = []
        self.DEF_SEM = []
        self.SELECTED_DEFENCES = []
        self.RESULT = ""

        # optimal attacks variables
        self.NUMBER_ATTACKS = StringVar()
        self.NUMBER_ATTACKS.set("1")
        self.ATTRIBUTE = StringVar()
        self.ATTRIBUTE.set("cost")

        # pareto optimization variables
        self.PARETO_COSTS = StringVar()
        self.PARETO_COSTS.set("0")
        self.PARETO_SKILLS = StringVar()
        self.PARETO_SKILLS.set("0")
        self.PARETO_PROBS = StringVar()
        self.PARETO_PROBS.set("0")

        # ILP variables
        self.BUDGET = StringVar()
        self.BUDGET.set("0")
        self.OPT_PROBLEM = StringVar()
        self.OPT_PROBLEM.set("coverage")

        # assignment button
        self.ASSIGNMENT_ON = False
        self.assignment_button = None

        # oops
        self.window.title(
            "OSEAD: Optimal Strategies Extractor for Attack-Defense trees")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing_main_window)
        #window.resizable(0, 0)
        # width x height + x_offset + y_offset:
        width = 985
        height = 500
        self.window.geometry('{}x{}+20+20'.format(width, height))
        self.window.deiconify()
        # col_count, row_count = window.grid_size()
        #
        # for row in range(row_count):
        #     window.grid_rowconfigure(row, minsize=40)

        self.nbcols = 4
        self.col_width = 30  #

        # general stuff
        self.bg_colour = "#C5E3BF"  # "#A6D785"
        self.res_button = None

        self.radio_optimal = Radiobutton(self.window, text="Find optimal attacks",
                                         font=("helvetica", 10), relief=GROOVE, state=DISABLED, width=self.col_width - 4, variable=self.TASK_SELECTED, command=self.find_optimal_attacks_selected, value=1, padx=0, anchor='w')
        self.radio_optimal.grid(column=2, row=1, columnspan=2)
        self.radio_pareto = Radiobutton(self.window, text="Find Pareto optimal attacks",
                                        font=("helvetica", 10), relief=GROOVE, width=self.col_width - 4, state=DISABLED, command=self.find_pareto_selected, variable=self.TASK_SELECTED, value=2, padx=0, anchor='w')
        self.radio_pareto.grid(column=2, row=6, columnspan=2)
        self.radio_countermeasures = Radiobutton(self.window, text="Find optimal set of countermeasures",
                                                 font=("helvetica", 10), relief=GROOVE, width=self.col_width - 4, state=DISABLED, command=self.find_countermeasures_selected, variable=self.TASK_SELECTED, value=3, padx=0, anchor='w')
        self.radio_countermeasures.grid(column=2, row=11, columnspan=2)
        # optimal attacks spinboxes
        self.spin_attacks_number = Spinbox(
            self.window, from_=1, to=20, width=10, wrap=True, textvariable=self.NUMBER_ATTACKS, state=DISABLED)
        self.spin_attacks_number.grid(column=3, row=2)

        self.spin_attribute = Spinbox(self.window, values=('cost', 'skill',
                                                           'difficulty', 'probability'), width=10, wrap=True, textvariable=self.ATTRIBUTE, command=self.spinbox_attribute, state=DISABLED)
        self.spin_attribute.grid(column=3, row=3)
        # pareto spinboxes
        self.spin_pareto_costs = Spinbox(
            self.window, from_=0, to=20, width=10, wrap=True, command=self.spinbox_pareto_costs, textvariable=self.PARETO_COSTS, state=DISABLED)
        self.spin_pareto_costs.grid(column=3, row=7)
        self.spin_pareto_skills = Spinbox(
            self.window, from_=0, to=20, width=10, wrap=True, command=self.spinbox_pareto_skills, textvariable=self.PARETO_SKILLS, state=DISABLED)
        self.spin_pareto_skills.grid(column=3, row=8)
        self.spin_pareto_probs = Spinbox(
            self.window, from_=0, to=20, width=10, wrap=True, command=self.spinbox_pareto_probs, textvariable=self.PARETO_PROBS, state=DISABLED)
        self.spin_pareto_probs.grid(column=3, row=9)
        # countermeasures spinboxes
        self.entry_budget = Entry(self.window, width=10, state=DISABLED,
                                  exportselection=0, textvariable=self.BUDGET)
        self.entry_budget.grid(column=3, row=12)
        self.spin_counter = Spinbox(
            self.window, values=("coverage", "attacker's investment"), width=10, wrap=True, textvariable=self.OPT_PROBLEM, command=self.spinbox_ilp, state=DISABLED)
        self.spin_counter.grid(column=3, row=13)

        # required assignments
        self.lab32 = Label(self.window, text="No task selected.",
                           font=("helvetica", 10), relief=FLAT, width=(2 * self.col_width) // 3, anchor='w', justify=LEFT)
        self.lab32.grid(column=4, row=1)
        self.lab33 = Label(self.window, text="",
                           font=("helvetica", 10), relief=FLAT, width=(2 * self.col_width) // 3, anchor='w')
        self.lab33.grid(column=4, row=3)
        self.lab34 = Label(self.window, text="",
                           font=("helvetica", 10), relief=FLAT, width=(2 * self.col_width) // 3, anchor='w')
        self.lab34.grid(column=4, row=4)
        self.lab35 = Label(self.window, text="",
                           font=("helvetica", 10), relief=FLAT, width=(2 * self.col_width) // 3, anchor='w')
        self.lab35.grid(column=4, row=5)
        self.lab36 = Label(self.window, text="",
                           font=("helvetica", 10), relief=FLAT, width=self.col_width,
                           anchor='w', justify=LEFT, wraplength=7 * 32)
        self.lab36.grid(column=4, row=6)
        self.run_button = Button(self.window, text="Run", state=DISABLED,
                                 command=self.run_button_clicked, width=10)
        self.run_button.grid(column=6, row=3, columnspan=2)
        self.lab45 = Label(self.window, text="",
                           font=("helvetica", 10), relief=FLAT, width=self.col_width, anchor='w')  # , justify=LEFT)
        self.lab45.grid(column=6, row=5, columnspan=2)
        self.lab46 = Label(self.window, text="",
                           font=("helvetica", 10), relief=FLAT, width=self.col_width, anchor='w')  # , justify=LEFT)
        self.lab46.grid(column=6, row=6, columnspan=2)
        self.lab47 = Label(self.window, text="",
                           font=("helvetica", 10), relief=FLAT, width=self.col_width, anchor='w')  # , justify=LEFT)
        self.lab47.grid(column=6, row=7, columnspan=2)
        self.lab48 = Label(self.window, text="",
                           font=("helvetica", 10), relief=FLAT, width=self.col_width, anchor='w')  # , justify=LEFT)
        self.lab48.grid(column=6, row=8, columnspan=2)
        self.lab49 = Label(self.window, text="",
                           font=("helvetica", 10), relief=FLAT, width=self.col_width, anchor='w')  # , justify=LEFT)
        self.lab49.grid(column=6, row=9, columnspan=2)
        self.lab410 = Label(self.window, text="",
                            font=("helvetica", 10), relief=FLAT, width=self.col_width, anchor='w')  # , justify=LEFT)
        self.lab410.grid(column=6, row=11, columnspan=2)
        # lab37 = Label(window, text="",
        #               font=("helvetica", 10), relief=FLAT, width=(2 * col_width) // 3, anchor='w', justify=LEFT, wraplength=0)
        # lab37.grid(column=4, row=7, columnspan=2)

        self.lab1 = Label(self.window, text="TREE SELECTION",
                          font=("verdana", 10), relief=RIDGE, width=self.col_width, bg=self.bg_colour)
        self.lab1.grid(column=0, row=0, columnspan=2)

        self.lab12 = Label(self.window, text="Select ADTool .xml output file:",
                           font=("helvetica", 10), relief=FLAT, width=self.col_width, anchor='w')
        self.lab12.grid(column=0, row=2, columnspan=2)

        self.browse_button = Button(self.window, text="Browse",
                                    command=self.browse_clicked, anchor='e')
        self.browse_button.grid(column=0, row=3)

        self.lab13 = Label(self.window, text=self.TREE_LOADED_MSG,
                           font=("helvetica", 10), relief=FLAT, width=self.col_width, anchor='w')
        self.lab13.grid(column=0, row=5, columnspan=2)

        self.lab14 = Label(self.window, textvariable=self.FILE_SELECTED,
                           font=("helvetica", 10), relief=FLAT, anchor='w')
        self.lab14.grid(column=0, row=6)

        # 2.2 column 2 of 4
        self.lab2 = Label(self.window, text="TASK SELECTION",
                          font=("verdana", 10), relief=RIDGE, width=self.col_width, bg=self.bg_colour)  # "helvetica")
        self.lab2.grid(column=2, row=0, columnspan=2)

        # 2.2.1 find optimal attacks

        self.lab23 = Label(self.window, text="Number of attacks:",
                           font=("helvetica", 10), relief=FLAT, width=(2 * self.col_width) // 3, anchor='w')
        self.lab23.grid(column=2, row=2)

        self.lab24 = Label(self.window, text="Attribute to be optimized:",
                           font=("helvetica", 10), relief=FLAT, width=(2 * self.col_width) // 3, anchor='w')
        self.lab24.grid(column=2, row=3)  # , columnspan=2)

        # 2.2.2 find pareto optimal attacks

        self.lab26 = Label(self.window, text="Number of costs:",
                           font=("helvetica", 10), relief=FLAT, width=(2 * self.col_width) // 3, anchor='w')
        self.lab26.grid(column=2, row=7)

        self.lab26 = Label(self.window, text="Number of skills/difficulties:",
                           font=("helvetica", 10), relief=FLAT, width=(2 * self.col_width) // 3, anchor='w')
        self.lab26.grid(column=2, row=8)

        self.lab27 = Label(self.window, text="Number of probabilities:",
                           font=("helvetica", 10), relief=FLAT, width=(2 * self.col_width) // 3, anchor='w')
        self.lab27.grid(column=2, row=9)

        # 2.2.3 find optimal set of countermeasures

        self.lab28 = Label(self.window, text="Defender's budget:",
                           font=("helvetica", 10), relief=FLAT, width=(2 * self.col_width) // 3, anchor='w')
        self.lab28.grid(column=2, row=12)

        self.lab29 = Label(self.window, text="Optimization problem:",
                           font=("helvetica", 10), relief=FLAT, width=(2 * self.col_width) // 3, anchor='w')
        self.lab29.grid(column=2, row=13)

        # 2.3 column 3 of 4
        self.lab3 = Label(self.window, text="BASIC ASSIGNMENT",
                          font=("verdana", 10), relief=RIDGE, width=self.col_width, bg=self.bg_colour)  # "helvetica")
        self.lab3.grid(column=4, row=0, columnspan=2)

        # 2.4 column 4 of 4
        self.lab4 = Label(self.window, text="RUN ANALYSIS",
                          font=("verdana", 10), relief=RIDGE, width=self.col_width, bg=self.bg_colour)  # "helvetica")
        self.lab4.grid(column=6, row=0, columnspan=2)

    def on_closing_main_window(self):
        #global window, root
        self.root.quit()
        self.root.destroy()
        self.window.quit()
        self.window.destroy()

    def activate_optimal_attacks(self):
        if self.ASSIGNMENT_ON == False:
            self.create_assignment_button()
        self.spin_attacks_number.config(state=NORMAL)
        self.spin_attribute.config(state=NORMAL)

    def deactivate_optimal_attacks(self):
        self.spin_attacks_number.config(state=DISABLED)
        self.spin_attribute.config(state=DISABLED)

    def activate_pareto(self):
        if self.ASSIGNMENT_ON == False:
            self.create_assignment_button()
        self.spin_pareto_costs.config(state=NORMAL)
        self.spin_pareto_skills.config(state=NORMAL)
        self.spin_pareto_probs.config(state=NORMAL)

    def deactivate_pareto(self):
        self.spin_pareto_costs.config(state=DISABLED)
        self.spin_pareto_skills.config(state=DISABLED)
        self.spin_pareto_probs.config(state=DISABLED)

    def activate_countermeasures(self):
        if not ILP_POSSIBLE:
            return
        if self.ASSIGNMENT_ON == False:
            self.create_assignment_button()
        self.entry_budget.config(state=NORMAL)
        self.spin_counter.config(state=NORMAL)

    def deactivate_countermeasures(self):
        self.entry_budget.config(state=DISABLED)
        self.spin_counter.config(state=DISABLED)

    def deactivate_all(self):
        self.deactivate_optimal_attacks()
        self.deactivate_pareto()
        self.deactivate_countermeasures()

    def find_optimal_attacks_selected(self):
        # reset the basic assignment
        #global BASIC_ASSIGNMENT
        self.BASIC_ASSIGNMENT = BasicAssignment()
        self.activate_optimal_attacks()
        self.deactivate_pareto()
        self.deactivate_countermeasures()
        self.lab32.config(text="Selected task requires")
        self.lab33.config(text="1 assignment of " + self.ATTRIBUTE.get())
        self.lab34.config(text="")
        self.lab35.config(text="")
        self.lab36.config(
            text="for the attacker, and selection of actions executed by the defender.")

    def find_pareto_selected(self):
        # reset the basic assignment
        #global BASIC_ASSIGNMENT
        self.BASIC_ASSIGNMENT = BasicAssignment()
        self.deactivate_optimal_attacks()
        self.activate_pareto()
        self.deactivate_countermeasures()
        self.lab32.config(text="Selected task requires")
        if self.PARETO_COSTS.get() == 1:
            x = " assignment of cost and"
        else:
            x = " assignments of cost and"
        self.lab33.config(text=self.PARETO_COSTS.get() + x)
        if self.PARETO_SKILLS.get() == 1:
            x = " assignment of skill/diff."
        else:
            x = " assignments of skill/diff."
        self.lab34.config(text=self.PARETO_SKILLS.get() + x)
        if self.PARETO_PROBS.get() == 1:
            x = " assignment of prob."
        else:
            x = " assignments of prob."
        self.lab35.config(text=self.PARETO_PROBS.get() + x)
        self.lab36.config(
            text="for the attacker, and selection of actions executed by the defender.")

    def find_countermeasures_selected(self):
        # reset the basic assignment
        #global BASIC_ASSIGNMENT
        self.BASIC_ASSIGNMENT = BasicAssignment()
        self.deactivate_optimal_attacks()
        self.deactivate_pareto()
        self.activate_countermeasures()
        self.lab32.config(text="Selected task requires")
        if self.OPT_PROBLEM.get() == 'coverage':
            x = "0 assignments of cost"
        else:
            x = "1 assignment cost"
        self.lab33.config(text="1 assignment of cost")
        self.lab34.config(text="for the defender")
        self.lab35.config(text="")
        self.lab36.config(text="and " + x + " for the attacker.")

    def spinbox_attribute(self):
        self.lab33.config(text="1 assignment of " + self.ATTRIBUTE.get())

    def spinbox_pareto_costs(self):
        if int(self.PARETO_COSTS.get()) == 1:
            x = " assignment of cost and"
        else:
            x = " assignments of cost and"
        self.lab33.config(text=self.PARETO_COSTS.get() + x)

    def spinbox_pareto_skills(self):
        if int(self.PARETO_SKILLS.get()) == 1:
            x = " assignment of skill/diff."
        else:
            x = " assignments of skill/diff."
        self.lab34.config(text=str(self.PARETO_SKILLS.get()) + x)

    def spinbox_pareto_probs(self):
        if int(self.PARETO_SKILLS.get()) == 1:
            x = " assignment of probs."
        else:
            x = " assignments of probs."
        self.lab35.config(text=str(self.PARETO_PROBS.get()) + x)

    def spinbox_ilp(self):
        # if OPT_PROBLEM.get() == 'coverage':
        #     x = "the defender."
        # else:
        #     x = "both actors."
        if self.OPT_PROBLEM.get() == 'coverage':
            x = "0 assignments of cost"
        else:
            x = "1 assignment of cost"
        # lab34.config(text=x)
        self.lab36.config(text="and " + x + " for the attacker.")

    def create_assignment_button(self):
        #global ASSIGNMENT_ON
        self.ASSIGNMENT_ON = True
        self.assignment_button = Button(
            self.window, text="Preview/Modify assignments", command=self.assignment_button_clicked)
        self.assignment_button.grid(column=4, row=8)

    def run_button_clicked(self):
        # depending on the choice of the problem, do stuff
        # run_button: (column=6, row=3, columnspan=2)
        #global RESULT
        self.run_button.config(state=DISABLED)
        # 1. start time
        start = ctime()
        self.RESULT = "Tree: {}".format(self.PATH.get())
        self.RESULT += "\n\nOptimization goal: "
        self.lab45.config(text="Start: {}".format(start[4:19]))
        for lab in [self.lab46, self.lab47, self.lab48, self.lab49]:
            lab.config(text="")
        # 2. looking for optimal attacks
        if self.TASK_SELECTED.get() in [1, 2]:
            #global SET_SEM
            self.lab46.config(text="Extracting attacks...")
            self.SET_SEM = self.TREE.set_semantics()
            self.lab47.config(text="Done: {}".format(ctime()[4:19]))
            self.lab48.config(text="Extracting optimal attacks...")
            if self.TASK_SELECTED.get() == 1:
                nb_attacks = int(self.NUMBER_ATTACKS.get())
            else:
                nb_attacks = None
            result1 = optimal_attacks(
                self.TREE, self.BASIC_ASSIGNMENT, self.DOMAIN, nb_attacks, self.SET_SEM, True)
            self.lab49.config(text="Done: {}".format(ctime()[4:19]))
            # result1 lists the attacks; complete the final result with additional
            # info
            if self.TASK_SELECTED.get() == 1:
                attr = self.ATTRIBUTE.get()
                if attr in ['cost', 'difficulty', 'skill']:
                    # complete the optimization goal
                    self.RESULT += 'minimizing {} for the attacker'.format(
                        attr)
                else:
                    self.RESULT += 'maximizing {} for the attacker'.format(
                        attr)
            else:
                # pareto
                self.RESULT += 'determining Pareto optimal attacks wrt {} costs, {} skills/difficulties and {} probabilities'.format(
                    self.PARETO_COSTS.get(), self.PARETO_SKILLS.get(), self.PARETO_PROBS.get())
            self.RESULT += "\n\nCountermeasures implemented by the defender:\n"
            if len(self.SELECTED_DEFENCES) == 0:
                self.RESULT += '\tnone\n'
            for item in self.SELECTED_DEFENCES:
                self.RESULT += "\t{}\n".format(item.replace('\n', ' '))
            self.RESULT += '\n'
            self.RESULT += result1
            # add some additional info, no?
            self.RESULT += 'Analysis performed under the following basic assignment:\n'
            for b in self.ATTACKERS_BAS:
                self.RESULT += "\t{}, {}\n".format(b.replace('\n', ' '),
                                                   self.BASIC_ASSIGNMENT[b])
            # print(RESULT)
        else:
            # 3. looking for optimal countermeasures
            #global DEF_SEM
            if self.OPT_PROBLEM.get() == 'coverage':
                self.RESULT += "maximize the number of prevented attacks\n\n"
            else:
                self.RESULT += "maximize the necessary investment of the attacker\n\n"
            self.lab46.config(text="Extracting attacks and defences...")
            self.DEF_SEM = self.TREE.defense_semantics()
            self.lab47.config(text="Done: {}".format(ctime()[4:19]))
            self.lab48.config(text="Extracting optimal defences...")
            result1 = optimal_countermeasures(self.TREE, self.BASIC_ASSIGNMENT, float(
                self.BUDGET.get()), problem=self.OPT_PROBLEM.get(), defsem=self.DEF_SEM, output=True)
            self.lab49.config(text="Done: {}".format(ctime()[4:19]))
            self.RESULT += result1
            self.RESULT += 'Analysis performed under the following basic assignment:\n'
            for b in self.ATTACKERS_BAS:
                self.RESULT += "\t{}, {}\n".format(b.replace('\n', ' '),
                                                   self.BASIC_ASSIGNMENT[b])
            self.RESULT += "\n"
            for b in self.DEFENDERS_BAS:
                self.RESULT += "\t{}, {}\n".format(b.replace('\n', ' '),
                                                   self.BASIC_ASSIGNMENT[b])
            # print(RESULT)
        # SAVE/DISPLAY results buttons
        self.lab410.config(text="Analysis finished!")
        self.res_button = Button(self.window, text="Save results to .txt", state=NORMAL,
                                 command=self.res_button_clicked, width=14)
        self.res_button.grid(column=6, row=13, columnspan=2)
        return

    def res_button_clicked(self):
        from tkinter import filedialog
        file = filedialog.asksaveasfile()
        if file == '':
            # 'cancel' pressed
            return
        file.write(self.RESULT)
        file.close()

        # radio buttons

    def activate_goals_buttons(self):
        self.radio_optimal.config(state=NORMAL)
        self.radio_pareto.config(state=NORMAL)
        self.radio_countermeasures.config(state=NORMAL)

    def deactivate_goals_buttons(self):
        self.radio_optimal.config(state=DISABLED)
        self.radio_pareto.config(state=DISABLED)
        self.radio_countermeasures.config(state=DISABLED)

    def browse_clicked(self):
        #global TREE, TREE_LOADED, FILE_SELECTED, ATTACKERS_BAS, DEFENDERS_BAS, ATTACKERS_ACTIONS_NUMBER, DEFENDERS_ACTIONS_NUMBER, PATH
        from tkinter import filedialog
        file = filedialog.askopenfilename()
        if file[-4:] == '.xml':
            # tree should load successfully
            self.TREE = ADTree(path=file)
            self.TREE_LOADED = 1
            self.ATTACKERS_BAS = self.TREE.basic_actions('a')
            self.DEFENDERS_BAS = self.TREE.basic_actions('d')
            self.ATTACKERS_BAS.sort()
            self.DEFENDERS_BAS.sort()
            self.ATTACKERS_ACTIONS_NUMBER = len(self.ATTACKERS_BAS)
            self.DEFENDERS_ACTIONS_NUMBER = len(self.DEFENDERS_BAS)
            self.PATH.set(file)
            self.FILE_SELECTED.set(
                '...' + file[-min(len(self.TREE_LOADED_MSG), len(file)):])
            self.activate_goals_buttons()
            # print(TREE)
        elif file == '':
            # 'cancel' pressed
            return
        else:
            # failed to load a tree
            from tkinter import messagebox
            messagebox.showinfo(
                'Error!', 'Failed to load a tree from specified file. Be sure to select an .xml file produced by ADTool.')
            self.TREE = ADTree()
            self.TREE_LOADED = 0
            self.FILE_SELECTED.set('no file selected')
            self.deactivate_goals_buttons()

    def assignment_button_clicked(self):
        '''
        TODO
        '''
        #global root
        # global ASSIGNMENTS_WINDOW_OPEN  # , ATTACKERS_BAS, DEFENDERS_BAS
        #global DEF_CHECKBOXES_VARIABLES
        #global LAST_SELECTED_TASK
        if self.ASSIGNMENTS_WINDOW_OPEN:
            return
        else:
            self.ASSIGNMENTS_WINDOW_OPEN = True
        self.deactivate_goals_buttons()
        # we want to only refresh the window, if it was opened before and the
        # problem selected hasn't changed
        # SO, check the currently selected task
        task_is_the_same = self.get_current_task() == self.LAST_SELECTED_TASK
        if self.ASSIGNMENTS_WINDOW_OPENED_BEFORE and task_is_the_same:
            self.root.update()
            self.root.deiconify()
            return
        elif self.ASSIGNMENTS_WINDOW_OPENED_BEFORE:
            # if the task selected has changed, the root window is created
            # again
            self.root.destroy()
        # create new window
        self.LAST_SELECTED_TASK = self.get_current_task()
        # self.root = Tk()  # Tk()
        self.root = Toplevel(self.window)
        self.root.title("Basic assignment")
        #root.resizable(0, 0)
        # determine the behaviour on "root" being closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing_assignment)
        menubar = Menu(self.root)
        menubar.add_command(
            label="Import", command=self.import_assignment)
        menubar.add_command(
            label="Export", command=self.export_assignment)
        menubar.add_command(label="Save & Exit",
                            command=self.on_closing_assignment)
        # display the menu
        self.root.config(menu=menubar)
        # populate with table; depends on the problem selected and other parameters
        # 1. ROWS HEADERS
        ROWS_HEADERS = []
        attackers_actions_number = 0
        # gonna assign values to actions of the attacker
        # if determining optimal attacks or solving investment ILP
        if self.TASK_SELECTED.get() in [1, 2] or self.OPT_PROBLEM.get() == "attacker's investment":
            attackers_actions_number = len(self.ATTACKERS_BAS)
            ROWS_HEADERS = ['ATTACKER']
            ROWS_HEADERS.extend(self.ATTACKERS_BAS)
            ROWS_HEADERS.append('')
        elif self.TASK_SELECTED.get() == 3 and self.OPT_PROBLEM.get() == "coverage":
            attackers_actions_number = -2  # hacky hack
        # in either case, need to assign something to basic actions of the
        # defender
        ROWS_HEADERS.append('DEFENDER')
        ROWS_HEADERS.extend(self.DEFENDERS_BAS)
        ROWS_HEADERS = [x.replace('\n', ' ') for x in ROWS_HEADERS]
        # 2. COLUMNS HEADERS
        COLUMNS_HEADERS = [ROWS_HEADERS[0]]
        if self.TASK_SELECTED.get() == 1:
            COLUMNS_HEADERS.append(self.ATTRIBUTE.get())
        elif self.TASK_SELECTED.get() == 2:
            COLUMNS_HEADERS.extend(["cost_" + str(i + 1)
                                    for i in range(int(self.PARETO_COSTS.get()))])
            COLUMNS_HEADERS.extend(["skill/diff_" + str(i + 1)
                                    for i in range(int(self.PARETO_SKILLS.get()))])
            COLUMNS_HEADERS.extend(["prob_" + str(i + 1)
                                    for i in range(int(self.PARETO_PROBS.get()))])
        elif self.TASK_SELECTED.get() == 3 and self.OPT_PROBLEM.get() == "attacker's investment":
            COLUMNS_HEADERS.append('cost')
        #
        width = len(COLUMNS_HEADERS)
        height = len(ROWS_HEADERS)
        # 3. input of assignments for the attacker from xml buttons
        # buttons are placed iff attackers_actions_number != -2
        if attackers_actions_number != -2:
            # height = len(ROWS_HEADERS) + 1
            ATTACKER_XML_BUTTONS = []
            ATTACKER_BUTTONS_COMMANDS = []
            for i in range(width - 1):
                ATTACKER_XML_BUTTONS.append(
                    Button(self.root, text="load from .xml", anchor='e', command=self.load_assignment_from_xml(i + 1)))  # command =
        else:
            pass
            # height = len(ROWS_HEADERS)
        #
        for j in range(width):
            b = Label(self.root, text=COLUMNS_HEADERS[j])
            b.grid(row=0, column=j)
            if attackers_actions_number != -2 and j > 0:
                ATTACKER_XML_BUTTONS[
                    j - 1].grid(row=1, column=j)
        # rows for the attacker
        for i in range(attackers_actions_number + 2):
            # if the code inside the loop is executed, then there are buttons
            # , wraplength=20)
            b = Label(self.root, text=ROWS_HEADERS[i], justify=LEFT)
            if i == 0:
                b.grid(row=0, column=0)
            else:
                b.grid(row=i + 1, column=0)
            if i > 0 and i < attackers_actions_number + 1:
                for j in range(1, width):  # Columns
                    b = Entry(self.root, text='', textvariable=StringVar())
                    # the buttons are there, so i+1
                    # TODO: depending on whether opened for the first time or
                    # not
                    b.insert(0, "0")
                    b.grid(row=i + 1, column=j)
            elif i > 0:
                for j in range(1, width):
                    b = Label(self.root, text='')
                    b.grid(row=i + 1, column=j)
        # rows of the defender
        self.DEF_CHECKBOXES_VARIABLES = []
        for i in range(attackers_actions_number + 2, height):
            if attackers_actions_number != -2:
                # buttons are there!
                j = i + 1
            else:
                j = i
            # , wraplength=20)
            b = Label(self.root, text=ROWS_HEADERS[i], justify=LEFT)
            b.grid(row=j, column=0)
            if i == attackers_actions_number + 2:
                if self.TASK_SELECTED.get() == 3:
                    # optimization: need to provide costs for the defender
                    b = Label(self.root, text="cost")
                else:
                    b = Label(self.root, text="performed")
            else:
                if self.TASK_SELECTED.get() == 3:
                    # cost for the defender
                    b = Entry(self.root, text='')
                    b.insert(0, "0")
                else:
                    # checkbox for the defender
                    new_var = IntVar()
                    self.DEF_CHECKBOXES_VARIABLES.append(new_var)
                    b = Checkbutton(self.root, variable=new_var,
                                    onvalue=1, offvalue=0)
                    #variable=self.DEF_CHECKBOXES_VARIABLES[len(self.DEF_CHECKBOXES_VARIABLES) - 1]
            b.grid(row=j, column=1)
        # added on May 2
        # root.mainloop()

    def on_closing_assignment(self):
        #global ASSIGNMENTS_WINDOW_OPEN
        #global ASSIGNMENTS_WINDOW_OPENED_BEFORE
        self.ASSIGNMENTS_WINDOW_OPEN = False
        self.ASSIGNMENTS_WINDOW_OPENED_BEFORE = True
        self.update_basic_assignment()
        # print(BASIC_ASSIGNMENT)
        self.activate_goals_buttons()
        self.run_button.config(state=ACTIVE)
        self.root.withdraw()
        # root.destroy()

    def update_basic_assignment(self):
        self.SELECTED_DEFENCES = []
        # store the basic assignment
        # load from grid cells, depending on the problem selected
        # read_val_from_grid
        #print('task selected: {}'.format(TASK_SELECTED.get()))
        if self.TASK_SELECTED.get() == 1:
            # 1. load values for the attacker
            for i in range(self.ATTACKERS_ACTIONS_NUMBER):
                self.BASIC_ASSIGNMENT[self.ATTACKERS_BAS[i]
                                      ] = read_val_from_grid(self.root, i + 2, 1)
            # 2. interpret check boxes of the defender
            temp = ['cost', 'skill', 'difficulty',
                    'probability'].index(self.ATTRIBUTE.get())
            NEUTRAL = [0, 0, 0, 1][temp]
            ABSORBING = [2**20, 2**20, 2**20, 0][temp]  # 2**20 for infinity
            for i in range(self.DEFENDERS_ACTIONS_NUMBER):
                if self.DEF_CHECKBOXES_VARIABLES[i].get():
                    # checkbox selected
                    #print("uuu, checkbox SELECTED")
                    corresponding_ba = self.DEFENDERS_BAS[i]
                    self.BASIC_ASSIGNMENT[corresponding_ba] = ABSORBING
                    self.SELECTED_DEFENCES.append(corresponding_ba)
                else:
                    # print("NOPE")
                    self.BASIC_ASSIGNMENT[self.DEFENDERS_BAS[i]] = NEUTRAL
            # 3. select the domain
            self.DOMAIN = [minCost, minDiff, minDiff, maxProb][temp]
        elif self.TASK_SELECTED.get() == 2:
            nb_of_domains = int(self.PARETO_COSTS.get()) + \
                int(self.PARETO_SKILLS.get()) + int(self.PARETO_PROBS.get())
            # 1. load values for the attacker
            for i in range(self.ATTACKERS_ACTIONS_NUMBER):
                vals_assigned = [read_val_from_grid(
                    self.root, i + 2, j + 1) for j in range(nb_of_domains)]
                self.BASIC_ASSIGNMENT[self.ATTACKERS_BAS[i]] = [vals_assigned]
            # 2. interpret tick boxes of the defender
            NEUTRAL = [0 for i in range(
                int(self.PARETO_COSTS.get()) + int(self.PARETO_SKILLS.get()))]
            NEUTRAL.extend([1 for i in range(int(self.PARETO_PROBS.get()))])
            ABSORBING = [2**20 for i in range(
                int(self.PARETO_COSTS.get()) + int(self.PARETO_SKILLS.get()))]
            ABSORBING.extend([0 for i in range(int(self.PARETO_PROBS.get()))])
            for i in range(self.DEFENDERS_ACTIONS_NUMBER):
                if self.DEF_CHECKBOXES_VARIABLES[i].get():
                    # checkbox selected
                    corresponding_ba = self.DEFENDERS_BAS[i]
                    self.BASIC_ASSIGNMENT[corresponding_ba] = [ABSORBING]
                    self.SELECTED_DEFENCES.append(corresponding_ba)
                else:
                    self.BASIC_ASSIGNMENT[self.DEFENDERS_BAS[i]] = [NEUTRAL]
            # 3. create the domain
            self.DOMAIN = ParetoDomain(int(self.PARETO_COSTS.get()), int(
                self.PARETO_SKILLS.get()), int(self.PARETO_PROBS.get()))
        elif self.OPT_PROBLEM.get() == "attacker's investment":
            # 1. load values for the attacker
            for i in range(self.ATTACKERS_ACTIONS_NUMBER):
                self.BASIC_ASSIGNMENT[self.ATTACKERS_BAS[i]
                                      ] = read_val_from_grid(self.root, i + 2, 1)
            # 2. load values for the defender
            for i in range(self.DEFENDERS_ACTIONS_NUMBER):
                self.BASIC_ASSIGNMENT[self.DEFENDERS_BAS[i]] = read_val_from_grid(
                    self.root, i + self.ATTACKERS_ACTIONS_NUMBER + 4, 1)
        else:
            # coverage problem
            for i in range(self.DEFENDERS_ACTIONS_NUMBER):
                self.BASIC_ASSIGNMENT[self.DEFENDERS_BAS[i]] = read_val_from_grid(
                    self.root, i + 1, 1)

    def get_current_task(self):
        if self.TASK_SELECTED.get() == 1:
            return self.ATTRIBUTE.get()
        if self.TASK_SELECTED.get() == 2:
            return "pareto_{}_{}_{}".format(self.PARETO_COSTS.get(), self.PARETO_SKILLS.get(), self.PARETO_PROBS.get())
        return self.OPT_PROBLEM.get()

    def load_assignment_from_xml(self, index):
        def f():
            #global root
            from tkinter import filedialog
            file = filedialog.askopenfilename()
            if file == '':
                return
            if file[-4:] == '.xml':
                # ba should load successfully
                ba = BasicAssignment(path=file)
            else:
                # failed to load a tree
                from tkinter import messagebox
                messagebox.showinfo(
                    'Error!', 'Failed to load a basic assignment from specified file. Be sure to select an .xml file produced by ADTool.')
                return
            # display loaded values in appropriate Entry widgets
            for i in range(self.ATTACKERS_ACTIONS_NUMBER):
                # 1. fetch the value
                val = ba[self.ATTACKERS_BAS[i]]
                # 2. update&display in appropriate Entry widget, the one in
                # (i+2, index) grid cell
                entry = get_widget_from_grid(self.root, i + 2, index)
                # clear the widget
                entry.delete(0, len(entry.get()))
                # modify value
                entry.insert(0, str(val))
        return f

    def export_assignment(self):
        self.update_basic_assignment()
        from tkinter import filedialog
        file = filedialog.asksaveasfile()
        if file == '':
            return
        for label in self.BASIC_ASSIGNMENT:
            out_label = str(label).replace('\n', ' ')
            file.write(out_label + '\t' +
                       str(self.BASIC_ASSIGNMENT[label]) + '\n')
        file.close()

    def import_assignment(self):
        #global root
        from tkinter import filedialog
        file = filedialog.askopenfilename()
        if file == '':
            # 'cancel' pressed
            return
        if file[-4:] == '.txt':
            # ba should load successfully
            ba = BasicAssignment(path=file)
        else:
            # failed to load an assignment
            from tkinter import messagebox
            messagebox.showinfo(
                'Error!', 'Failed to load a basic assignment from specified file. Be sure to select a .txt file produced by OSEAD.')
            return
        # display loaded values in appropriate Entry widgets
        # but not if the problem selected is the coverage problem
        current_task = self.TASK_SELECTED.get()
        if current_task in [1, 2] or self.OPT_PROBLEM != 'coverage':
            if current_task == 2:
                columns_to_fill_in = int(
                    self.PARETO_COSTS.get()) + int(self.PARETO_PROBS.get()) + int(self.PARETO_SKILLS.get())
            else:
                columns_to_fill_in = 1
            for i in range(self.ATTACKERS_ACTIONS_NUMBER):
                for j in range(columns_to_fill_in):
                    # 1. fetch the value
                    if current_task == 2:
                        # try: :)
                        val = ba[self.ATTACKERS_BAS[i].replace('\n', ' ')][
                            0][j]
                    else:
                        val = ba[self.ATTACKERS_BAS[i].replace('\n', ' ')]
                    # 2. update&display in appropriate Entry widget, the one in
                    # (i+2, index) grid cell
                    entry = get_widget_from_grid(self.root, i + 2, j + 1)
                    # clear the widget
                    entry.delete(0, len(entry.get()))
                    # modify value
                    entry.insert(0, str(val))
        # TODO: import values for the defender

    # def main():
    # create the main window
    # global window, spin_attacks_number, spin_attribute
    # window.title(
    #     "OSEAD: Optimal Strategies Extractor for Attack-Defense trees")
    # #window.resizable(0, 0)
    # # width x height + x_offset + y_offset:
    # width = 985
    # height = 500
    # window.geometry('{}x{}+20+20'.format(width, height))
    # # col_count, row_count = window.grid_size()
    # #
    # # for row in range(row_count):
    # #     window.grid_rowconfigure(row, minsize=40)
    #
    # nbcols = 4
    # col_width = 30  #
    #
    # # general stuff
    # bg_colour = "#C5E3BF"  # "#A6D785"

    # 2. create & place labels
    # 2.1 column 1 of 4

    # display/run
    # window.mainloop()


def osead():
    gui = osead_gui()
    gui.window.mainloop()

if __name__ == '__main__':
    osead()

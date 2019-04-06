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

# global variables
window = Tk()  # the main window :(
root = None  # the basic assignment window :(
col_width = 30
TREE = ADTree()
BASIC_ASSIGNMENT = BasicAssignment()
TREE_LOADED = 0
FILE_SELECTED = StringVar()
FILE_SELECTED.set('no file selected')
TREE_LOADED_MSG = "Path to currently loaded tree:"
TASK_SELECTED = IntVar()
TASK_SELECTED.set(0)
ASSIGNMENTS_WINDOW_OPEN = False
ASSIGNMENTS_WINDOW_OPENED_BEFORE = False
ATTACKERS_BAS = []
DEFENDERS_BAS = []
ATTACKERS_ACTIONS_NUMBER = 0
DEFENDERS_ACTIONS_NUMBER = 0
DOMAIN = None
DEF_CHECKBOXES_VARIABLES = []
LAST_SELECTED_TASK = None
PATH = StringVar()
SET_SEM = []
DEF_SEM = []
SELECTED_DEFENCES = []
RESULT = ""

# optimal attacks variables
NUMBER_ATTACKS = StringVar()
NUMBER_ATTACKS.set("1")
ATTRIBUTE = StringVar()
ATTRIBUTE.set("cost")

# pareto optimization variables
PARETO_COSTS = StringVar()
PARETO_COSTS.set("0")
PARETO_SKILLS = StringVar()
PARETO_SKILLS.set("0")
PARETO_PROBS = StringVar()
PARETO_PROBS.set("0")

# ILP variables
BUDGET = StringVar()
BUDGET.set("0")
OPT_PROBLEM = StringVar()
OPT_PROBLEM.set("coverage")

# assignment button
ASSIGNMENT_ON = False


def osead():
    window.title(
        "OSEAD: Optimal Strategies Extractor for Attack-Defense trees")
    #window.resizable(0, 0)
    # width x height + x_offset + y_offset:
    width = 985
    height = 500
    window.geometry('{}x{}+20+20'.format(width, height))
    # col_count, row_count = window.grid_size()
    #
    # for row in range(row_count):
    #     window.grid_rowconfigure(row, minsize=40)

    nbcols = 4
    col_width = 30  #

    # general stuff
    bg_colour = "#C5E3BF"  # "#A6D785"

    def activate_optimal_attacks():
        if ASSIGNMENT_ON == False:
            create_assignment_button()
        spin_attacks_number.config(state=NORMAL)
        spin_attribute.config(state=NORMAL)

    def deactivate_optimal_attacks():
        spin_attacks_number.config(state=DISABLED)
        spin_attribute.config(state=DISABLED)

    def activate_pareto():
        if ASSIGNMENT_ON == False:
            create_assignment_button()
        spin_pareto_costs.config(state=NORMAL)
        spin_pareto_skills.config(state=NORMAL)
        spin_pareto_probs.config(state=NORMAL)

    def deactivate_pareto():
        spin_pareto_costs.config(state=DISABLED)
        spin_pareto_skills.config(state=DISABLED)
        spin_pareto_probs.config(state=DISABLED)

    def activate_countermeasures():
        if not ILP_POSSIBLE:
            return
        if ASSIGNMENT_ON == False:
            create_assignment_button()
        entry_budget.config(state=NORMAL)
        spin_counter.config(state=NORMAL)

    def deactivate_countermeasures():
        entry_budget.config(state=DISABLED)
        spin_counter.config(state=DISABLED)

    def deactivate_all():
        deactivate_optimal_attacks()
        deactivate_pareto()
        deactivate_countermeasures()

    def find_optimal_attacks_selected():
        # reset the basic assignment
        global BASIC_ASSIGNMENT
        BASIC_ASSIGNMENT = BasicAssignment()
        activate_optimal_attacks()
        deactivate_pareto()
        deactivate_countermeasures()
        lab32.config(text="Selected task requires")
        lab33.config(text="1 assignment of " + ATTRIBUTE.get())
        lab34.config(text="")
        lab35.config(text="")
        lab36.config(
            text="for the attacker, and selection of actions executed by the defender.")

    def find_pareto_selected():
        # reset the basic assignment
        global BASIC_ASSIGNMENT
        BASIC_ASSIGNMENT = BasicAssignment()
        deactivate_optimal_attacks()
        activate_pareto()
        deactivate_countermeasures()
        lab32.config(text="Selected task requires")
        if PARETO_COSTS.get() == 1:
            x = " assignment of cost and"
        else:
            x = " assignments of cost and"
        lab33.config(text=PARETO_COSTS.get() + x)
        if PARETO_SKILLS.get() == 1:
            x = " assignment of skill/diff."
        else:
            x = " assignments of skill/diff."
        lab34.config(text=PARETO_SKILLS.get() + x)
        if PARETO_PROBS.get() == 1:
            x = " assignment of prob."
        else:
            x = " assignments of prob."
        lab35.config(text=PARETO_PROBS.get() + x)
        lab36.config(
            text="for the attacker, and selection of actions executed by the defender.")

    def find_countermeasures_selected():
        # reset the basic assignment
        global BASIC_ASSIGNMENT
        BASIC_ASSIGNMENT = BasicAssignment()
        deactivate_optimal_attacks()
        deactivate_pareto()
        activate_countermeasures()
        lab32.config(text="Selected task requires")
        if OPT_PROBLEM.get() == 'coverage':
            x = "0 assignments of cost"
        else:
            x = "1 assignment cost"
        lab33.config(text="1 assignment of cost")
        lab34.config(text="for the defender")
        lab35.config(text="")
        lab36.config(text="and " + x + " for the attacker.")

    def spinbox_attribute():
        lab33.config(text="1 assignment of " + ATTRIBUTE.get())

    def spinbox_pareto_costs():
        if int(PARETO_COSTS.get()) == 1:
            x = " assignment of cost and"
        else:
            x = " assignments of cost and"
        lab33.config(text=PARETO_COSTS.get() + x)

    def spinbox_pareto_skills():
        if int(PARETO_SKILLS.get()) == 1:
            x = " assignment of skill/diff."
        else:
            x = " assignments of skill/diff."
        lab34.config(text=str(PARETO_SKILLS.get()) + x)

    def spinbox_pareto_probs():
        if int(PARETO_SKILLS.get()) == 1:
            x = " assignment of probs."
        else:
            x = " assignments of probs."
        lab35.config(text=str(PARETO_PROBS.get()) + x)

    def spinbox_ilp():
        # if OPT_PROBLEM.get() == 'coverage':
        #     x = "the defender."
        # else:
        #     x = "both actors."
        if OPT_PROBLEM.get() == 'coverage':
            x = "0 assignments of cost"
        else:
            x = "1 assignment of cost"
        # lab34.config(text=x)
        lab36.config(text="and " + x + " for the attacker.")

    def create_assignment_button():
        global ASSIGNMENT_ON
        ASSIGNMENT_ON = True
        assignment_button = Button(
            window, text="Preview/Modify assignments", command=assignment_button_clicked)
        assignment_button.grid(column=4, row=8)

    def run_button_clicked():
        # depending on the choice of the problem, do stuff
        # run_button: (column=6, row=3, columnspan=2)
        global RESULT
        run_button.config(state=DISABLED)
        # 1. start time
        start = ctime()
        RESULT = "Tree: {}".format(PATH.get())
        RESULT += "\n\nOptimization goal: "
        lab45.config(text="Start: {}".format(start[4:19]))
        for lab in [lab46, lab47, lab48, lab49]:
            lab.config(text="")
        # 2. looking for optimal attacks
        if TASK_SELECTED.get() in [1, 2]:
            global SET_SEM
            lab46.config(text="Extracting attacks...")
            SET_SEM = TREE.set_semantics()
            lab47.config(text="Done: {}".format(ctime()[4:19]))
            lab48.config(text="Extracting optimal attacks...")
            if TASK_SELECTED.get() == 1:
                nb_attacks = int(NUMBER_ATTACKS.get())
            else:
                nb_attacks = None
            result1 = optimal_attacks(
                TREE, BASIC_ASSIGNMENT, DOMAIN, nb_attacks, SET_SEM, True)
            lab49.config(text="Done: {}".format(ctime()[4:19]))
            # result1 lists the attacks; complete the final result with additional
            # info
            if TASK_SELECTED.get() == 1:
                attr = ATTRIBUTE.get()
                if attr in ['cost', 'difficulty', 'skill']:
                    # complete the optimization goal
                    RESULT += 'minimizing {} for the attacker'.format(attr)
                else:
                    RESULT += 'maximizing {} for the attacker'.format(attr)
            else:
                # pareto
                RESULT += 'determining Pareto optimal attacks wrt {} costs, {} skills/difficulties and {} probabilities'.format(
                    PARETO_COSTS.get(), PARETO_SKILLS.get(), PARETO_PROBS.get())
            RESULT += "\n\nCountermeasures implemented by the defender:\n"
            if len(SELECTED_DEFENCES) == 0:
                RESULT += '\tnone\n'
            for item in SELECTED_DEFENCES:
                RESULT += "\t{}\n".format(item.replace('\n', ' '))
            RESULT += '\n'
            RESULT += result1
            # add some additional info, no?
            RESULT += 'Analysis performed under the following basic assignment:\n'
            for b in ATTACKERS_BAS:
                RESULT += "\t{}, {}\n".format(b.replace('\n', ' '),
                                              BASIC_ASSIGNMENT[b])
            # print(RESULT)
        else:
            # 3. looking for optimal countermeasures
            global DEF_SEM
            if OPT_PROBLEM.get() == 'coverage':
                RESULT += "maximize the number of prevented attacks\n\n"
            else:
                RESULT += "maximize the necessary investment of the attacker\n\n"
            lab46.config(text="Extracting attacks and defences...")
            DEF_SEM = TREE.defense_semantics()
            lab47.config(text="Done: {}".format(ctime()[4:19]))
            lab48.config(text="Extracting optimal defences...")
            result1 = optimal_countermeasures(TREE, BASIC_ASSIGNMENT, float(
                BUDGET.get()), problem=OPT_PROBLEM.get(), defsem=DEF_SEM, output=True)
            lab49.config(text="Done: {}".format(ctime()[4:19]))
            RESULT += result1
            RESULT += 'Analysis performed under the following basic assignment:\n'
            for b in ATTACKERS_BAS:
                RESULT += "\t{}, {}\n".format(b.replace('\n', ' '),
                                              BASIC_ASSIGNMENT[b])
            RESULT += "\n"
            for b in DEFENDERS_BAS:
                RESULT += "\t{}, {}\n".format(b.replace('\n', ' '),
                                              BASIC_ASSIGNMENT[b])
            # print(RESULT)
        # SAVE/DISPLAY results buttons
        lab410.config(text="Analysis finished!")
        res_button = Button(window, text="Save results to .txt", state=NORMAL,
                            command=res_button_clicked, width=14)
        res_button.grid(column=6, row=13, columnspan=2)
        return

    def res_button_clicked():
        from tkinter import filedialog
        file = filedialog.asksaveasfile()
        if file == '':
            # 'cancel' pressed
            return
        file.write(RESULT)
        file.close()

        # radio buttons
    radio_optimal = Radiobutton(window, text="Find optimal attacks",
                                font=("helvetica", 10), relief=GROOVE, state=DISABLED, width=col_width - 4, variable=TASK_SELECTED, command=find_optimal_attacks_selected, value=1, padx=0, anchor='w')
    radio_optimal.grid(column=2, row=1, columnspan=2)
    radio_pareto = Radiobutton(window, text="Find Pareto optimal attacks",
                               font=("helvetica", 10), relief=GROOVE, width=col_width - 4, state=DISABLED, command=find_pareto_selected, variable=TASK_SELECTED, value=2, padx=0, anchor='w')
    radio_pareto.grid(column=2, row=6, columnspan=2)
    radio_countermeasures = Radiobutton(window, text="Find optimal set of countermeasures",
                                        font=("helvetica", 10), relief=GROOVE, width=col_width - 4, state=DISABLED, command=find_countermeasures_selected, variable=TASK_SELECTED, value=3, padx=0, anchor='w')
    radio_countermeasures.grid(column=2, row=11, columnspan=2)
    # optimal attacks spinboxes
    spin_attacks_number = Spinbox(
        window, from_=1, to=20, width=10, wrap=True, textvariable=NUMBER_ATTACKS, state=DISABLED)
    spin_attacks_number.grid(column=3, row=2)

    spin_attribute = Spinbox(window, values=('cost', 'skill',
                                             'difficulty', 'probability'), width=10, wrap=True, textvariable=ATTRIBUTE, command=spinbox_attribute, state=DISABLED)
    spin_attribute.grid(column=3, row=3)
    # pareto spinboxes
    spin_pareto_costs = Spinbox(
        window, from_=0, to=20, width=10, wrap=True, command=spinbox_pareto_costs, textvariable=PARETO_COSTS, state=DISABLED)
    spin_pareto_costs.grid(column=3, row=7)
    spin_pareto_skills = Spinbox(
        window, from_=0, to=20, width=10, wrap=True, command=spinbox_pareto_skills, textvariable=PARETO_SKILLS, state=DISABLED)
    spin_pareto_skills.grid(column=3, row=8)
    spin_pareto_probs = Spinbox(
        window, from_=0, to=20, width=10, wrap=True, command=spinbox_pareto_probs, textvariable=PARETO_PROBS, state=DISABLED)
    spin_pareto_probs.grid(column=3, row=9)
    # countermeasures spinboxes
    entry_budget = Entry(window, width=10, state=DISABLED,
                         exportselection=0, textvariable=BUDGET)
    entry_budget.grid(column=3, row=12)
    spin_counter = Spinbox(
        window, values=("coverage", "attacker's investment"), width=10, wrap=True, textvariable=OPT_PROBLEM, command=spinbox_ilp, state=DISABLED)
    spin_counter.grid(column=3, row=13)

    # required assignments
    lab32 = Label(window, text="No task selected.",
                  font=("helvetica", 10), relief=FLAT, width=(2 * col_width) // 3, anchor='w', justify=LEFT)
    lab32.grid(column=4, row=1)
    lab33 = Label(window, text="",
                  font=("helvetica", 10), relief=FLAT, width=(2 * col_width) // 3, anchor='w')
    lab33.grid(column=4, row=3)
    lab34 = Label(window, text="",
                  font=("helvetica", 10), relief=FLAT, width=(2 * col_width) // 3, anchor='w')
    lab34.grid(column=4, row=4)
    lab35 = Label(window, text="",
                  font=("helvetica", 10), relief=FLAT, width=(2 * col_width) // 3, anchor='w')
    lab35.grid(column=4, row=5)
    lab36 = Label(window, text="",
                  font=("helvetica", 10), relief=FLAT, width=col_width,
                  anchor='w', justify=LEFT, wraplength=7 * 32)
    lab36.grid(column=4, row=6)
    run_button = Button(window, text="Run", state=DISABLED,
                        command=run_button_clicked, width=10)
    run_button.grid(column=6, row=3, columnspan=2)
    lab45 = Label(window, text="",
                  font=("helvetica", 10), relief=FLAT, width=col_width, anchor='w')  # , justify=LEFT)
    lab45.grid(column=6, row=5, columnspan=2)
    lab46 = Label(window, text="",
                  font=("helvetica", 10), relief=FLAT, width=col_width, anchor='w')  # , justify=LEFT)
    lab46.grid(column=6, row=6, columnspan=2)
    lab47 = Label(window, text="",
                  font=("helvetica", 10), relief=FLAT, width=col_width, anchor='w')  # , justify=LEFT)
    lab47.grid(column=6, row=7, columnspan=2)
    lab48 = Label(window, text="",
                  font=("helvetica", 10), relief=FLAT, width=col_width, anchor='w')  # , justify=LEFT)
    lab48.grid(column=6, row=8, columnspan=2)
    lab49 = Label(window, text="",
                  font=("helvetica", 10), relief=FLAT, width=col_width, anchor='w')  # , justify=LEFT)
    lab49.grid(column=6, row=9, columnspan=2)
    lab410 = Label(window, text="",
                   font=("helvetica", 10), relief=FLAT, width=col_width, anchor='w')  # , justify=LEFT)
    lab410.grid(column=6, row=11, columnspan=2)
    # lab37 = Label(window, text="",
    #               font=("helvetica", 10), relief=FLAT, width=(2 * col_width) // 3, anchor='w', justify=LEFT, wraplength=0)
    # lab37.grid(column=4, row=7, columnspan=2)

    def activate_goals_buttons():
        radio_optimal.config(state=NORMAL)
        radio_pareto.config(state=NORMAL)
        radio_countermeasures.config(state=NORMAL)

    def deactivate_goals_buttons():
        radio_optimal.config(state=DISABLED)
        radio_pareto.config(state=DISABLED)
        radio_countermeasures.config(state=DISABLED)

    def browse_clicked():
        global TREE, TREE_LOADED, FILE_SELECTED, ATTACKERS_BAS, DEFENDERS_BAS, ATTACKERS_ACTIONS_NUMBER, DEFENDERS_ACTIONS_NUMBER, PATH
        from tkinter import filedialog
        file = filedialog.askopenfilename()
        if file[-4:] == '.xml':
            # tree should load successfully
            TREE = ADTree(path=file)
            TREE_LOADED = 1
            ATTACKERS_BAS = TREE.basic_actions('a')
            DEFENDERS_BAS = TREE.basic_actions('d')
            ATTACKERS_BAS.sort()
            DEFENDERS_BAS.sort()
            ATTACKERS_ACTIONS_NUMBER = len(ATTACKERS_BAS)
            DEFENDERS_ACTIONS_NUMBER = len(DEFENDERS_BAS)
            PATH.set(file)
            FILE_SELECTED.set(
                '...' + file[-min(len(TREE_LOADED_MSG), len(file)):])
            activate_goals_buttons()
            # print(TREE)
        elif file == '':
            # 'cancel' pressed
            return
        else:
            # failed to load a tree
            from tkinter import messagebox
            messagebox.showinfo(
                'Error!', 'Failed to load a tree from specified file. Be sure to select an .xml file produced by ADTool.')
            TREE = ADTree()
            TREE_LOADED = 0
            FILE_SELECTED.set('no file selected')
            deactivate_goals_buttons()

    def assignment_button_clicked():
        '''
        TODO
        '''
        global root
        global ASSIGNMENTS_WINDOW_OPEN  # , ATTACKERS_BAS, DEFENDERS_BAS
        global DEF_CHECKBOXES_VARIABLES
        global LAST_SELECTED_TASK
        if ASSIGNMENTS_WINDOW_OPEN:
            return
        else:
            ASSIGNMENTS_WINDOW_OPEN = True
        deactivate_goals_buttons()
        # we want to only refresh the window, if it was opened before and the
        # problem selected hasn't changed
        # SO, check the currently selected task
        task_is_the_same = get_current_task() == LAST_SELECTED_TASK
        if ASSIGNMENTS_WINDOW_OPENED_BEFORE and task_is_the_same:
            root.update()
            root.deiconify()
            return
        elif ASSIGNMENTS_WINDOW_OPENED_BEFORE:
            root.destroy()
        # create new window
        LAST_SELECTED_TASK = get_current_task()
        root = Toplevel()  # Tk()
        #root.resizable(0, 0)
        # determine the behaviour on "root" being closed
        root.protocol("WM_DELETE_WINDOW", on_closing_assignment)
        menubar = Menu(root)
        menubar.add_command(label="Import", command=import_assignment)
        menubar.add_command(label="Export", command=export_assignment)
        menubar.add_command(label="Save & Exit",
                            command=on_closing_assignment)
        # display the menu
        root.config(menu=menubar)
        # populate with table; depends on the problem selected and other parameters
        # 1. ROWS HEADERS
        ROWS_HEADERS = []
        attackers_actions_number = 0
        # gonna assign values to actions of the attacker
        # if determining optimal attacks or solving investment ILP
        if TASK_SELECTED.get() in [1, 2] or OPT_PROBLEM.get() == "attacker's investment":
            attackers_actions_number = len(ATTACKERS_BAS)
            ROWS_HEADERS = ['ATTACKER']
            ROWS_HEADERS.extend(ATTACKERS_BAS)
            ROWS_HEADERS.append('')
        elif TASK_SELECTED.get() == 3 and OPT_PROBLEM.get() == "coverage":
            attackers_actions_number = -2  # hacky hack
        # in either case, need to assign something to basic actions of the
        # defender
        ROWS_HEADERS.append('DEFENDER')
        ROWS_HEADERS.extend(DEFENDERS_BAS)
        ROWS_HEADERS = [x.replace('\n', ' ') for x in ROWS_HEADERS]
        # 2. COLUMNS HEADERS
        COLUMNS_HEADERS = [ROWS_HEADERS[0]]
        if TASK_SELECTED.get() == 1:
            COLUMNS_HEADERS.append(ATTRIBUTE.get())
        elif TASK_SELECTED.get() == 2:
            COLUMNS_HEADERS.extend(["cost_" + str(i + 1)
                                    for i in range(int(PARETO_COSTS.get()))])
            COLUMNS_HEADERS.extend(["skill/diff_" + str(i + 1)
                                    for i in range(int(PARETO_SKILLS.get()))])
            COLUMNS_HEADERS.extend(["prob_" + str(i + 1)
                                    for i in range(int(PARETO_PROBS.get()))])
        elif TASK_SELECTED.get() == 3 and OPT_PROBLEM.get() == "attacker's investment":
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
                    Button(root, text="load from .xml", anchor='e', command=load_assignment_from_xml(i + 1)))  # command =
        else:
            pass
            # height = len(ROWS_HEADERS)
        #
        for j in range(width):
            b = Label(root, text=COLUMNS_HEADERS[j])
            b.grid(row=0, column=j)
            if attackers_actions_number != -2 and j > 0:
                ATTACKER_XML_BUTTONS[
                    j - 1].grid(row=1, column=j)
        # rows for the attacker
        for i in range(attackers_actions_number + 2):
            # if the code inside the loop is executed, then there are buttons
            # , wraplength=20)
            b = Label(root, text=ROWS_HEADERS[i], justify=LEFT)
            if i == 0:
                b.grid(row=0, column=0)
            else:
                b.grid(row=i + 1, column=0)
            if i > 0 and i < attackers_actions_number + 1:
                for j in range(1, width):  # Columns
                    b = Entry(root, text='', textvariable=StringVar())
                    # the buttons are there, so i+1
                    # TODO: depending on whether opened for the first time or
                    # not
                    b.insert(0, "0")
                    b.grid(row=i + 1, column=j)
            elif i > 0:
                for j in range(1, width):
                    b = Label(root, text='')
                    b.grid(row=i + 1, column=j)
        # rows of the defender
        DEF_CHECKBOXES_VARIABLES = []
        for i in range(attackers_actions_number + 2, height):
            if attackers_actions_number != -2:
                # buttons are there!
                j = i + 1
            else:
                j = i
            # , wraplength=20)
            b = Label(root, text=ROWS_HEADERS[i], justify=LEFT)
            b.grid(row=j, column=0)
            if i == attackers_actions_number + 2:
                if TASK_SELECTED.get() == 3:
                    # optimization: need to provide costs for the defender
                    b = Label(root, text="cost")
                else:
                    b = Label(root, text="performed")
            else:
                if TASK_SELECTED.get() == 3:
                    # cost for the defender
                    b = Entry(root, text='')
                    b.insert(0, "0")
                else:
                    # checkbox for the defender
                    new_var = IntVar()
                    DEF_CHECKBOXES_VARIABLES.append(new_var)
                    b = Checkbutton(root, variable=new_var,
                                    onvalue=1, offvalue=0)
            b.grid(row=j, column=1)

    def on_closing_assignment():
        global ASSIGNMENTS_WINDOW_OPEN
        global ASSIGNMENTS_WINDOW_OPENED_BEFORE
        ASSIGNMENTS_WINDOW_OPEN = False
        ASSIGNMENTS_WINDOW_OPENED_BEFORE = True
        update_basic_assignment()
        # print(BASIC_ASSIGNMENT)
        activate_goals_buttons()
        run_button.config(state=ACTIVE)
        root.withdraw()
        # root.destroy()

    def update_basic_assignment():
        global BASIC_ASSIGNMENT
        global DOMAIN
        global SELECTED_DEFENCES
        SELECTED_DEFENCES = []
        # store the basic assignment
        # load from grid cells, depending on the problem selected
        # read_val_from_grid
        #print('task selected: {}'.format(TASK_SELECTED.get()))
        if TASK_SELECTED.get() == 1:
            # 1. load values for the attacker
            for i in range(ATTACKERS_ACTIONS_NUMBER):
                BASIC_ASSIGNMENT[ATTACKERS_BAS[i]
                                 ] = read_val_from_grid(root, i + 2, 1)
            # 2. interpret check boxes of the defender
            temp = ['cost', 'skill', 'difficulty',
                    'probability'].index(ATTRIBUTE.get())
            NEUTRAL = [0, 0, 0, 1][temp]
            ABSORBING = [2**20, 2**20, 2**20, 0][temp]  # 2**20 for infinity
            for i in range(DEFENDERS_ACTIONS_NUMBER):
                if DEF_CHECKBOXES_VARIABLES[i].get():
                    # checkbox selected
                    corresponding_ba = DEFENDERS_BAS[i]
                    BASIC_ASSIGNMENT[corresponding_ba] = ABSORBING
                    SELECTED_DEFENCES.append(corresponding_ba)
                else:
                    BASIC_ASSIGNMENT[DEFENDERS_BAS[i]] = NEUTRAL
            # 3. select the domain
            DOMAIN = [minCost, minDiff, minDiff, maxProb][temp]
        elif TASK_SELECTED.get() == 2:
            nb_of_domains = int(PARETO_COSTS.get()) + \
                int(PARETO_SKILLS.get()) + int(PARETO_PROBS.get())
            # 1. load values for the attacker
            for i in range(ATTACKERS_ACTIONS_NUMBER):
                vals_assigned = [read_val_from_grid(
                    root, i + 2, j + 1) for j in range(nb_of_domains)]
                BASIC_ASSIGNMENT[ATTACKERS_BAS[i]] = [vals_assigned]
            # 2. interpret tick boxes of the defender
            NEUTRAL = [0 for i in range(
                int(PARETO_COSTS.get()) + int(PARETO_SKILLS.get()))]
            NEUTRAL.extend([1 for i in range(int(PARETO_PROBS.get()))])
            ABSORBING = [2**20 for i in range(
                int(PARETO_COSTS.get()) + int(PARETO_SKILLS.get()))]
            ABSORBING.extend([0 for i in range(int(PARETO_PROBS.get()))])
            for i in range(DEFENDERS_ACTIONS_NUMBER):
                if DEF_CHECKBOXES_VARIABLES[i].get():
                    # checkbox selected
                    corresponding_ba = DEFENDERS_BAS[i]
                    BASIC_ASSIGNMENT[corresponding_ba] = [ABSORBING]
                    SELECTED_DEFENCES.append(corresponding_ba)
                else:
                    BASIC_ASSIGNMENT[DEFENDERS_BAS[i]] = [NEUTRAL]
            # 3. create the domain
            DOMAIN = ParetoDomain(int(PARETO_COSTS.get()), int(
                PARETO_SKILLS.get()), int(PARETO_PROBS.get()))
        elif OPT_PROBLEM.get() == "attacker's investment":
            # 1. load values for the attacker
            for i in range(ATTACKERS_ACTIONS_NUMBER):
                BASIC_ASSIGNMENT[ATTACKERS_BAS[i]
                                 ] = read_val_from_grid(root, i + 2, 1)
            # 2. load values for the defender
            for i in range(DEFENDERS_ACTIONS_NUMBER):
                BASIC_ASSIGNMENT[DEFENDERS_BAS[i]] = read_val_from_grid(
                    root, i + ATTACKERS_ACTIONS_NUMBER + 4, 1)
        else:
            # coverage problem
            for i in range(DEFENDERS_ACTIONS_NUMBER):
                BASIC_ASSIGNMENT[DEFENDERS_BAS[i]] = read_val_from_grid(
                    root, i + 1, 1)

    def get_current_task():
        if TASK_SELECTED.get() == 1:
            return ATTRIBUTE.get()
        if TASK_SELECTED.get() == 2:
            return "pareto_{}_{}_{}".format(PARETO_COSTS.get(), PARETO_SKILLS.get(), PARETO_PROBS.get())
        return OPT_PROBLEM.get()

    def load_assignment_from_xml(index):
        def f():
            global root
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
            for i in range(ATTACKERS_ACTIONS_NUMBER):
                # 1. fetch the value
                val = ba[ATTACKERS_BAS[i]]
                # 2. update&display in appropriate Entry widget, the one in
                # (i+2, index) grid cell
                entry = get_widget_from_grid(root, i + 2, index)
                # clear the widget
                entry.delete(0, len(entry.get()))
                # modify value
                entry.insert(0, str(val))
        return f

    def export_assignment():
        update_basic_assignment()
        from tkinter import filedialog
        file = filedialog.asksaveasfile()
        if file == '':
            return
        for label in BASIC_ASSIGNMENT:
            out_label = str(label).replace('\n', ' ')
            file.write(out_label + '\t' + str(BASIC_ASSIGNMENT[label]) + '\n')
        file.close()

    def import_assignment():
        global root
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
        current_task = TASK_SELECTED.get()
        if current_task in [1, 2] or OPT_PROBLEM != 'coverage':
            if current_task == 2:
                columns_to_fill_in = int(
                    PARETO_COSTS.get()) + int(PARETO_PROBS.get()) + int(PARETO_SKILLS.get())
            else:
                columns_to_fill_in = 1
            for i in range(ATTACKERS_ACTIONS_NUMBER):
                for j in range(columns_to_fill_in):
                    # 1. fetch the value
                    if current_task == 2:
                        # try: :)
                        val = ba[ATTACKERS_BAS[i].replace('\n', ' ')][
                            0][j]
                    else:
                        val = ba[ATTACKERS_BAS[i].replace('\n', ' ')]
                    # 2. update&display in appropriate Entry widget, the one in
                    # (i+2, index) grid cell
                    entry = get_widget_from_grid(root, i + 2, j + 1)
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
    lab1 = Label(window, text="TREE SELECTION",
                 font=("verdana", 10), relief=RIDGE, width=col_width, bg=bg_colour)
    lab1.grid(column=0, row=0, columnspan=2)

    lab12 = Label(window, text="Select ADTool .xml output file:",
                  font=("helvetica", 10), relief=FLAT, width=col_width, anchor='w')
    lab12.grid(column=0, row=2, columnspan=2)

    browse_button = Button(window, text="Browse",
                           command=browse_clicked, anchor='e')
    browse_button.grid(column=0, row=3)

    lab13 = Label(window, text=TREE_LOADED_MSG,
                  font=("helvetica", 10), relief=FLAT, width=col_width, anchor='w')
    lab13.grid(column=0, row=5, columnspan=2)

    lab14 = Label(window, textvariable=FILE_SELECTED,
                  font=("helvetica", 10), relief=FLAT, anchor='w')
    lab14.grid(column=0, row=6)

    # 2.2 column 2 of 4
    lab2 = Label(window, text="TASK SELECTION",
                 font=("verdana", 10), relief=RIDGE, width=col_width, bg=bg_colour)  # "helvetica")
    lab2.grid(column=2, row=0, columnspan=2)

    # 2.2.1 find optimal attacks

    lab23 = Label(window, text="Number of attacks:",
                  font=("helvetica", 10), relief=FLAT, width=(2 * col_width) // 3, anchor='w')
    lab23.grid(column=2, row=2)

    lab24 = Label(window, text="Attribute to be optimized:",
                  font=("helvetica", 10), relief=FLAT, width=(2 * col_width) // 3, anchor='w')
    lab24.grid(column=2, row=3)  # , columnspan=2)

    # 2.2.2 find pareto optimal attacks

    lab26 = Label(window, text="Number of costs:",
                  font=("helvetica", 10), relief=FLAT, width=(2 * col_width) // 3, anchor='w')
    lab26.grid(column=2, row=7)

    lab26 = Label(window, text="Number of skills/difficulties:",
                  font=("helvetica", 10), relief=FLAT, width=(2 * col_width) // 3, anchor='w')
    lab26.grid(column=2, row=8)

    lab27 = Label(window, text="Number of probabilities:",
                  font=("helvetica", 10), relief=FLAT, width=(2 * col_width) // 3, anchor='w')
    lab27.grid(column=2, row=9)

    # 2.2.3 find optimal set of countermeasures

    lab28 = Label(window, text="Defender's budget:",
                  font=("helvetica", 10), relief=FLAT, width=(2 * col_width) // 3, anchor='w')
    lab28.grid(column=2, row=12)

    lab29 = Label(window, text="Optimization problem:",
                  font=("helvetica", 10), relief=FLAT, width=(2 * col_width) // 3, anchor='w')
    lab29.grid(column=2, row=13)

    # 2.3 column 3 of 4
    lab3 = Label(window, text="BASIC ASSIGNMENT",
                 font=("verdana", 10), relief=RIDGE, width=col_width, bg=bg_colour)  # "helvetica")
    lab3.grid(column=4, row=0, columnspan=2)

    # 2.4 column 4 of 4
    lab4 = Label(window, text="RUN ANALYSIS",
                 font=("verdana", 10), relief=RIDGE, width=col_width, bg=bg_colour)  # "helvetica")
    lab4.grid(column=6, row=0, columnspan=2)

    # display/run
    window.mainloop()


if __name__ == '__main__':
    osead()

import numpy as np
from adtrees.lp_solve import lp_solve
from scipy.sparse import coo_matrix, vstack, hstack, eye, bmat, diags

"""
lpsolve citation data
----------------------
Description     : Open source (Mixed-Integer) Linear Programming system
Language        : Multi-platform, pure ANSI C / POSIX source code, Lex/Yacc based parsing
Official name   : lp_solve (alternatively lpsolve)
Release data    : Version 5.1.0.0 dated 1 May 2004
Co-developers   : Michel Berkelaar, Kjell Eikland, Peter Notebaert
Licence terms   : GNU LGPL (Lesser General Public Licence)
Citation policy : General references as per LGPL
                  Module specific references as specified therein

http://lpsolve.sourceforge.net/5.5/
"""


class ADTilp():
    """
    An instance of integer linear programming problem
                min/max f*x
                M*x <= y
    for ADTrees.
    """

    def __init__(self, T, costassignment, budget, problem='coverage', defsem=None):
        """
        Given an attack-defense tree T with no repeated basic actions,
        the assignment of cost to the basic actions of the actors
        and the budget of the defender, formulate a linear programming problem.

        If problem == 'coverage', then this is the coverage problem.
        In this case, 'costassignment' does not have to cover the actions of the
        attacker.

        If problem == 'investment', then the problem solved is the maximization
        of the necessary investment of the attacker.

        p - number of basic actions of the defender
        n - number of distinct attack strategies in the defense semantics = number of 'z' variables
        m - number of distinct defense strategies in the defense semantics


        p, n, m, matrix, rhs, goalcoeffs, ineq, upp_bounds, int_vars, T, budget, type
        (T = the tree wrt which the problem was constructed)
        """
        super(ADTilp, self).__init__()
        # initialization
        if defsem == None:
            defsem = T.defense_semantics()

        # construct the matrix for the coverage problem

        defenders_actions = T.basic_actions('d')
        defender_costs = np.array([costassignment[b]
                                   for b in defenders_actions])

        # cost[i] is the cost of performing the action
        # labeled with defenders_actions[i]
        if defsem == []:
            print('None of the possible attacks can be prevented.')
            return

        A_i = []    # list of attack strategies
        D_j = []    # list of defense strategies
        # 1. CREATE MATRIX P
        # P_{rows[k], cols[k]} = data[k]
        rows = []
        cols = []
        for scenario in defsem:
            if scenario[0] not in A_i:
                # add a new row to P
                A_i.append(scenario[0])
            if scenario[1] not in D_j:
                # add a new column to P
                D_j.append(scenario[1])
            # the value of P[A_i.index(scenario[0]][D_j.index(scenario[1]] will be
            # set to 1
            rows.append(A_i.index(scenario[0]))
            cols.append(D_j.index(scenario[1]))
        p = len(defenders_actions)
        n = len(A_i)
        m = len(D_j)

        # DEBUGGING
        # print('\nattack strategies:')
        # for item in A_i:
        #     print(item)
        # print('\ndefense strategies:')
        # for item in D_j:
        #     print(item)
        #
        # print('\nrows:')
        # print(rows)
        # print('\ncols:')
        # print(cols)

        rows = np.array(rows)
        cols = np.array(cols)
        data = np.array([1 for i in range(len(rows))])

        # print('\ndata:\n')
        # print(data)

        P = coo_matrix((data, (rows, cols)), shape=(n, m))

        # print('\nthe P matrix:')
        # print(P.toarray())

        # 2. CREATE MATRIX Y = (y_kj)
        rows = []
        cols = []
        for i in range(p):
            for j in range(m):
                if defenders_actions[i] in D_j[j]:
                    rows.append(i)
                    cols.append(j)
        data = np.array([1 for i in range(len(rows))])
        Y = coo_matrix((data, (rows, cols)), shape=(p, m))

        # print('\nthe Y matrix')
        # print(Y.toarray())
        # 3. CREATE the matrix of the linear programming problem
        t = np.squeeze(np.asarray(P.sum(1)))
        # t_i = sum of elements in i-th row of P
        s = np.squeeze(np.asarray(Y.sum(0)))
        # s_i = sum of the elements in i_th column of Y
        self.matrix = bmat([[defender_costs, None, None], [-Y.T, None, -p * eye(m)],
                            [Y.T, None, eye(m)], [None, -eye(n), P], [None, diags(t), -P]])
        # 4. CREATE the right hand side of the problem
        self.rhs = np.concatenate(
            (np.array([budget]), -s, s, t - 1, np.zeros(n)))
        # 5. info for the solver
        # indication whether the inequalities are <= or =>.
        # in this case they are <=, represented by -1.

        self.ineq = -np.ones(2 * m + 2 * n + 1)
        # upper bounds for the variables. the variables are binary, so 1.
        self.upp_bounds = np.ones(n + m + p)
        # which variables are integer? all of them.
        self.int_vars = [i for i in range(1, n + m + p + 1)]
        if problem == 'coverage':
            # coefficients of the linear goal function to be optimized.
            # multiplied by -1, since we want to minimize, while lp_solve function
            # maximizes.
            self.goalcoeffs = - \
                np.concatenate((np.zeros(p), np.ones(n), np.zeros(m)))
        else:
            # modify accordingly!
            costs_of_A_strats = [sum([costassignment[b]
                                      for b in A]) for A in A_i]
            # costs_of_A_strats[i] = cost of the i-th attacker's strategy
            max_of_attackers_costs = max(costs_of_A_strats)
            sumarray = np.array([max_of_attackers_costs])
            # diagonal of smth
            diag = diags([max_of_attackers_costs -
                          item for item in costs_of_A_strats])
            # matrix
            # add column of zeros
            # self.matrix.get_shape()[0] = 2*(n+m) + 1
            # print(self.matrix.get_shape())
            self.matrix = hstack([self.matrix, coo_matrix(
                [[0] for i in range(2 * (n + m) + 1)])])
            # to the result add a number of rows of specific format, namely
            # [0 diag 0 1]
            zeros_left = coo_matrix((n, p))
            zeros_right = coo_matrix((n, m))
            new_bottom = hstack(
                [zeros_left, diag, zeros_right,  [[1] for i in range(n)]])

            self.matrix = vstack([self.matrix, new_bottom])
            # rhs, etc.
            self.rhs = np.concatenate(
                [self.rhs, np.array(n * [max_of_attackers_costs])])
            self.ineq = np.concatenate([self.ineq, np.array(n * [-1])])
            self.upp_bounds = np.concatenate([self.upp_bounds, sumarray])
            self.int_vars.append(1)
            # goal function; maximize C
            self.goalcoeffs = np.concatenate((np.zeros(p + n + m), np.ones(1)))

            # print(self.goalcoeffs)

            # DEBUGGING
            # for item in [self.rhs, self.ineq, self.upp_bounds, self.int_vars, self.goalcoeffs]:
            #     print(len(item))
        self.p = p
        self.n = n
        self.m = m
        self.T = T
        self.budget = budget
        self.type = problem

        # DEBUGGING
        # print(self.matrix.toarray())
        # print(self.rhs)

    def solve(self, verbose=True):
        """
        Solve the problem represented by 'self', using lp_solve.

        If verbose==True, then display the results.
        """
        M = self.matrix.toarray()
        defenders_actions = self.T.basic_actions('d')
        # run the solver
        res = lp_solve(f=self.goalcoeffs, a=M, b=self.rhs, e=self.ineq,
                       vlb=None, vub=self.upp_bounds, xint=self.int_vars)

        defs_to_deploy = [defenders_actions[i]
                          for i in range(self.p) if res[1][i] > 0]

        if verbose:
            print('With your budget of {}, you should deploy the following defences:'.format(
                self.budget))
            for ba in defs_to_deploy:
                print(ba)
        # for i in range(self.p):
        #    if res[1][i] > 0:
        #        print(defenders_actions[i])

        number_of_prevented = int(
            self.n - np.sum(res[1][self.p: self.p + self.n]))
        number_of_preventable = int(self.n)

        if self.type == 'coverage':
            number_of_unprevented = -int(res[0])
            if verbose:
                print('Then {} attacks from total of {} preventable attacks are prevented.\n'.format(
                    number_of_prevented, number_of_preventable))
            return (defs_to_deploy, number_of_prevented, number_of_preventable)
        else:
            min_invest = float(res[0])
            if verbose:
                print('Then {} attacks from total of {} preventable attacks are prevented and the minimal necessary investment of the attacker is {}.\n'.format(
                    number_of_prevented, number_of_preventable, min_invest))
            return (defs_to_deploy, number_of_prevented, number_of_preventable, min_invest)

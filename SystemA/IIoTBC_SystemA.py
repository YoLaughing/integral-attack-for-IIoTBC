import os

import gurobipy as gp
import time

"""
    MILP bit division
    分组长度为64bit
    8分支广义feistel结构，每分枝8bit
"""


class SystemA:
    def __init__(self, round, input_DP, filename_model, filename_result):
        self.block_size = 64  # 64
        self.fi_num = 4
        self.state_size = 8  # 每分支bit数量
        # self.word_size = int(self.grp_block_size / 4)  # 4
        self.vars = []
        self.round_num = round
        self.input_dp = input_DP
        self.file_model = filename_model
        self.file_result = filename_result
        f_path, f_name = os.path.split(filename_model)
        if not os.path.exists(f_path):
            os.makedirs(f_path)

    sbox_ineq = [[1, 4, 1, 1, -2, -2, -2, -2, 1],
                 [0, 0, 3, 0, -1, -1, -1, -1, 1],
                 [-2, 0, -1, -1, 4, 2, 3, 3, 0],
                 [3, 0, 0, 0, -1, -1, -1, -1, 1],
                 [-6, -4, -3, -3, 2, -1, 2, 2, 11],
                 [0, 0, 0, 3, -1, -1, -1, -1, 1],
                 [-2, -2, -4, -4, 1, 1, 2, -1, 9],
                 [-1, -1, -2, -2, 5, 5, 5, 4, 0],
                 [-1, 0, 0, -1, 0, -1, 1, 0, 2],
                 [0, 1, 0, 0, -1, 0, -1, 0, 1]]

    def create_state_var(self, x, r):
        # return [x_r_0, x_r_1, x_r_2, ....]
        return ["{0}_{1}_{2}".format(x, r, p) for p in range(self.block_size)]

    def create_target_fn(self):
        """
        Create Objective function of the MILP model.
        Minimize
        """
        file_obj = open(self.file_model, "w+")
        file_obj.write("Minimize\n")
        output_var = self.create_state_var('x', self.round_num)
        file_obj.write(' + '.join(output_var) + '\n')
        file_obj.close()

    def input_init(self):
        """
        Generate constraints by the initial division property.
        """
        in_vars = []
        in_vars += self.create_state_var('x', 0)
        constraints = ["{0} = {1}".format(a, b) for a, b in zip(in_vars, self.input_dp)]
        file_obj = open(self.file_model, "a")
        file_obj.write('Subject To\n')
        for enq in constraints:
            file_obj.write(enq + '\n')
        file_obj.close()

    def constraint_and(self, u, v, t):
        """
        Generate constraints by and operation.
        u and v -----> t
        """
        file_obj = open(self.file_model, "a")
        for i in range(0, len(t)):
            file_obj.write((t[i] + " - " + u[i] + " >= " + str(0)))
            file_obj.write("\n")
            file_obj.write((t[i] + " - " + v[i] + " >= " + str(0)))
            file_obj.write("\n")
            file_obj.write((t[i] + " - " + u[i] + " - " + v[i] + " <= " + str(0)))
            file_obj.write("\n")
        file_obj.close()

    def constraint_xor3(self, s, t, w, x_out):
        """
        Generate the constraints by Xor operation.
        s xor t xor w = x_out
        xout - s - t - w = 0
        """
        file_obj = open(self.file_model, "a")
        for i in range(0, len(x_out)):
            eqn = []
            eqn.append(x_out[i])
            eqn.append(s[i])
            eqn.append(t[i])
            eqn.append(w[i])
            temp = " - ".join(eqn)
            temp = temp + " = " + str(0)
            file_obj.write(temp)
            file_obj.write("\n")
        file_obj.close()

    def constraint_xor2(self, s, t, x_out):
        """
        Generate the constraints by Xor operation.
        s xor t = x_out
        xout - s - t = 0
        """
        constraints = []
        for i in range(0, len(x_out)):
            eqn = []
            eqn.append(x_out[i])
            eqn.append(s[i])
            eqn.append(t[i])
            temp = " - ".join(eqn)
            temp = temp + " = " + str(0)
            constraints.append(temp)
        return constraints

    def constraint_copy(self, x, s, t):
        """
        Generate the constraints by Copy operation.
        x -- (s,t)
        """
        constraints = []
        for i in range(0, len(x)):
            eqn = []
            eqn.append(x[i])
            eqn.append(s[i])
            eqn.append(t[i])
            temp = " - ".join(eqn)
            temp = temp + " = " + str(0)
            constraints.append(temp)
        return constraints

    def sbox(self, in_vars, out_vars):
        """
        Generate the constraints by sbox layer.
        """
        constraints = []
        # An m-fold parallel application of the same 3-bit Sbox on the first 3m bits of the state.
        for coff in self.sbox_ineq:
            temp = ["{0} {1}".format(a, b) for a, b in zip(coff[:4], in_vars)]
            temp += ["{0} {1}".format(a, b) for a, b in zip(coff[4:8], out_vars)]
            temp_ineq = " + ".join(temp)
            temp_ineq = temp_ineq.replace("+ -", "- ")
            s = str(-coff[-1])
            s = s.replace("--", "")
            temp_ineq += " >= " + s
            constraints.append(temp_ineq)
        return constraints

    def PA1(self, in_vars, out_vars):
        constraints = []
        permutaion1 = [7, 2, 1, 4, 3, 6, 5, 0]
        for id1 in range(8):
            id2 = permutaion1[id1]
            constraints += ["{1} - {0} = 0".format(a, b) for a, b in zip(in_vars[id1*8:id1*8+8], out_vars[id2*8:id2*8+8])]
        return constraints

    def PA2(self, in_vars, out_vars):
        constraints = []
        permutaion1 = [3, 0, 1, 2, 7, 4, 5, 6]
        for id1 in range(8):
            id2 = permutaion1[id1]
            constraints += ["{1} - {0} = 0".format(a, b) for a, b in
                            zip(in_vars[id1 * 8:id1 * 8 + 8], out_vars[id2 * 8:id2 * 8 + 8])]
        return constraints


    def round_Function(self):
        MILP_eqn = []
        for rnd in range(self.round_num):
            in_vars = self.create_state_var('x', rnd)
            yi = self.create_state_var('y', rnd)
            zi = self.create_state_var('z', rnd)
            # wi = self.create_state_var('w', rnd)
            self.vars += in_vars + yi + zi
            for g in range(self.fi_num):
                # copy x --> (y,z)
                begin = g * 16
                MILP_eqn += self.constraint_copy(in_vars[begin:begin + 8], yi[begin:begin + 8], zi[begin:begin + 8])
                # two sbox
                MILP_eqn += self.sbox(zi[begin:begin + 4], zi[begin + 8:begin + 12])
                MILP_eqn += self.sbox(zi[begin + 4:begin + 8], zi[begin + 12:begin + 16])
                # xor (x, z) --> y
                begin = g*16+8
                zi_ll1 = zi[begin+1:begin+8]
                zi_ll1.append(zi[begin])
                MILP_eqn += self.constraint_xor2(in_vars[begin:begin + 8], zi_ll1, yi[begin:begin + 8])

            # linear
            out_vars = self.create_state_var('x', rnd+1)
            if rnd%2 == 0:
                # PA1
                MILP_eqn += self.PA1(yi, out_vars)
            else:
                MILP_eqn += self.PA2(yi, out_vars)

        self.vars += self.create_state_var('x', self.round_num)
        file_obj = open(self.file_model, "a")
        file_obj.write("\n")
        for temp in MILP_eqn:
            file_obj.write(temp)
            file_obj.write("\n")
        file_obj.close()

    def create_binary(self):
        """
        Specify variable type.
        """
        file_obj = open(self.file_model, "a")
        file_obj.write("\n")
        file_obj.write("binaries\n")
        for temp in self.vars:
            file_obj.write(temp)
            file_obj.write("\n")
        file_obj.write("END")
        file_obj.close()

    def create_model(self):
        self.create_target_fn()
        self.input_init()
        self.round_Function()
        # ANF_map, index_w = self.create_ANF_map_and_indexw()
        self.create_binary()

    def solve_model(self):
        """
        Solve the MILP model to search the integral distinguisher.
        """
        file_obj = open(self.file_result, "w+")
        file_obj.write("Result!\n")
        file_obj.close()
        time_start = time.time()
        m = gp.read(self.file_model)
        # 设置整数精度
        m.setParam("IntFeasTol", 1e-7)
        counter = 0
        set_zero = []
        MILP_trails = []
        global_flag = False
        while counter < self.block_size:
            m.optimize()
            # Gurobi syntax: m.Status == 2 represents the model is feasible.
            if m.Status == 2:
                all_vars = m.getVars()
                MILP_trial = []
                for v in all_vars:
                    name = v.getAttr('VarName')
                    valu = v.getAttr('x')
                    MILP_trial.append(name + ' = ' + str(valu))
                MILP_trails.append(MILP_trial)
                obj = m.getObjective()
                if round(obj.getValue()) > 1:
                    global_flag = True
                    break

                else:
                    file_obj = open(self.file_result, "a")
                    file_obj.write("************************************COUNTER = %d\n" % counter)
                    file_obj.close()
                    self.write_obj(obj)
                    for i in range(0, self.block_size):
                        u = obj.getVar(i)
                        temp = u.getAttr('x')
                        if round(temp) == 1:
                            set_zero.append(u.getAttr('VarName'))
                            u.ub = 0
                            m.update()
                            counter += 1
                            break
            # Gurobi syntax: m.Status == 3 represents the model is infeasible.
            elif m.Status == 3:
                global_flag = True
                break
            else:
                print("Unknown error!")

        file_obj = open(self.file_result, "a")
        if global_flag:
            file_obj.write("\nIntegral Distinguisher Found!\n\n")
            print("Integral Distinguisher Found!\n")
        else:
            file_obj.write("\nIntegral Distinguisher do NOT exist\n\n")
            print("Integral Distinguisher do NOT exist\n")

        file_obj.write("Those are the coordinates set to zero: \n")
        balanced = self.create_state_var('x', self.round_num)
        for u in set_zero:
            balanced.remove(u)
            file_obj.write(u)
            file_obj.write("\n")
        file_obj.write("The division trails is : \n")
        for index, Mi in enumerate(MILP_trails):
            file_obj.write("The division trails [%i] :\n" % index)
            for v in Mi:
                file_obj.write(v + '\n')
            # file_obj.write("\n")
        file_obj.write("\n")
        time_end = time.time()
        file_obj.write(("Time used = " + str(time_end - time_start)))
        file_obj.close()
        return (len(set_zero), balanced)

    def write_obj(self, obj):
        """
        Write the objective value into filename_result.
        """
        file_obj = open(self.file_result, "a")
        file_obj.write("The objective value = %d\n" % obj.getValue())
        eqn1 = []
        eqn2 = []
        for i in range(0, self.block_size):
            u = obj.getVar(i)
            if u.getAttr("x") != 0:
                eqn1.append(u.getAttr('VarName'))
                eqn2.append(u.getAttr('x'))
        length = len(eqn1)
        for i in range(0, length):
            s = eqn1[i] + "=" + str(eqn2[i])
            file_obj.write(s)
            file_obj.write("\n")
        file_obj.close()


def find_bit_integral_distinguisher(block_size, rounds, cipher_name):
    filepath = 'result/' + cipher_name + '_R%i/' % (rounds)

    len_zero = []
    for active_point in range(57, block_size):
        # for active_point in range(1):
        vector = ['1'] * block_size
        vector[active_point] = '0'
        input_DP = ''.join(vector)

        filename_model = filepath + cipher_name + '_R%i_A%i_model.lp' % (rounds, active_point)
        filename_result = filepath + cipher_name + '_R%i_A%i_result.txt' % (rounds, active_point)
        # file_r = open(filename_result, "w+")
        # file_r.close()
        fm = Feistel4Multi4Bit64(block_size, rounds, input_DP, filename_model, filename_result)
        # 最左边为最低位
        fm.create_model(input_DP)
        zero_ = fm.solve_model()
        len_zero.append('active_point = %i, len of zero = %i' % (active_point, zero_))

    filename_result = filepath + '---' + cipher_name + '----R%i_AllResult.txt' % (rounds)
    file_r = open(filename_result, "w+")
    for i in len_zero:
        file_r.write(i)
        file_r.write('\n')
    file_r.close()


if __name__ == "__main__":
    block_size = 64
    rounds = 13
    cipher_name = 'Feistel4_Multi4_Bit64'
    find_bit_integral_distinguisher(block_size, rounds, cipher_name)

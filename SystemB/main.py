import sys

sys.path.append("..")
from IIoTBC_SystemB import SystemB

if __name__ == "__main__":
    rounds = 60   # 输入division为input_DP
    filepath = 'SystemB_R%i/' % (rounds)
    filename_all = filepath + 'SystemB_R{0}_AllResult.txt'.format(rounds)

    for active_point in range(64):
        # active_point = 63
        vector = ['1'] * 64
        vector[active_point] = '0'
        input_DP = ''.join(vector)

        # 最左边为最低位
        filename_model = filepath + 'SystemB_R{0}_AP{1}_model.lp'.format(rounds, active_point)
        filename_result = filepath + 'SystemB_R{0}_AP{1}_result.txt'.format(rounds, active_point)
        fm = SystemB(round=rounds, input_DP=input_DP, filename_model=filename_model,
                     filename_result=filename_result)
        fm.create_model()
        (zero_, balanced) = fm.solve_model()
        # len_zero.append('active_point = %i, len of zero = %i' % (active_point, zero_))
        file_r = open(filename_all, "a")
        if zero_ < 64:
            file_r.write(
                "------------Integral Distinguisher Found!------------------------------------------------------- \n")
            file_r.write('------------Active_point = {0}, len of zero = {1}.\n'.format(active_point, zero_))
            file_r.write('------------Balanced position is:\n------------')
            for i, v in enumerate(balanced):
                file_r.write(str(v) + ", ")
                if (i + 1) % 16 == 0:
                    file_r.write("\n------------")
            file_r.write(
                '------------------------------------------------------------------------------------------------\n')
        else:
            file_r.write('Not Found!!!!! Find active_point = {0}, len of zero = {1}'.format(active_point, zero_))

        file_r.write('\n')
        file_r.close()

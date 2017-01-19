import math
import numpy
import os
import re
import sys
from collections import defaultdict


def get_files(folder):
    for f in os.listdir(folder):
        if (not f.startswith('.')) and f.endswith('.out'):
            yield f


def stddev(lst):
    sum_nu = 0
    mn = sum(lst) / float(len(lst))
    for ele in lst:
        sum_nu += (ele - mn) ** 2
    return math.sqrt(sum_nu / (len(lst) - 1))


def main():
    folder_name = sys.argv[1]

    mu_list = ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0', '2.0', '3.0', '4.0', '5.0', '6.0',
               '7.0', '8.0', '9.0']

    result_dict = dict()

    file_dict = dict()

    for file in get_files(folder_name):
        sequence_storage = list()

        number_storage = set()

        loop_storage = defaultdict(int)

        log_weight_flux = list()

        log_trj_flux = list()

        sum_log_weight_flux = 0

        sum_sq_log_weight_flux = 0

        sum_log_trj_flux = 0

        sum_sq_log_trj_flux = 0

        node_count = 0

        paras = re.search('trj.a7.0.b([0-9.]+).c0.60.1e([0-9]+).out', file)
        miu, opponents = paras.group(1), paras.group(2)
        print miu, opponents
        with open(folder_name + '/' + file, 'r') as f:

            for number in f:
                node_count += 1

                number = number.rstrip()

                # print "current number is: ", number

                if number in number_storage:

                    # print "this number repeats", "\n"

                    number_index = sequence_storage.index(number)

                    # print(sequence_storage[number_index:])

                    loop_set = frozenset(sequence_storage[number_index:])

                    if len(loop_set) >= 3:

                        loop_storage[loop_set] += 1

                        del sequence_storage[number_index:]

                        number_storage.difference_update(loop_set)

                    else:

                        sequence_storage.append(number)

                else:

                    sequence_storage.append(number)

                    number_storage.add(number)

                    # print "current sequence is: ", sequence_storage, "\n"

                    # print "current number in storage: ", number_storage, "\n"

        # for key in sorted(loop_storage, key=loop_storage.get, reverse=True):

        #     print "The loop is: ", " ".join(key), "\n"

        #     print "The loop has been repeated", loop_storage(key), "times\n"

        # steps = float(node_count - len(sequence_storage))

        totalsteps = float(node_count - len(sequence_storage))
        unique_loop_count = float(len(loop_storage))
        print 'unique_loop_count:', unique_loop_count

        for key, loop_count in sorted(loop_storage.items(), key=lambda x: x[1], reverse=True):
            trj_flux = loop_count / totalsteps

            current_log_trj_flux = -math.log(trj_flux)

            log_trj_flux.append(current_log_trj_flux)

            current_log_weight_flux = -math.log(loop_count)

            log_weight_flux.append(current_log_weight_flux)

            sum_log_weight_flux += current_log_weight_flux

            sum_sq_log_weight_flux += current_log_weight_flux ** 2

            sum_log_trj_flux += current_log_trj_flux

            sum_sq_log_trj_flux += current_log_trj_flux ** 2

            # print loop_count, ",  ",  str(log_weight_flux), ", ", str(trj_flux), ",  ",
            # str(current_log_trj_flux),  " ".join(key)

        av_log_weight_flux = sum_log_weight_flux / unique_loop_count

        av_log_trj_flux = sum_log_trj_flux / unique_loop_count

        sig_log_weight_flux = math.sqrt(
            (abs(sum_sq_log_weight_flux - (sum_log_weight_flux ** 2) / unique_loop_count) / unique_loop_count))

        # print (sum_sq_log_trj_flux - (sum_log_trj_flux ** 2) / unique_loop_count) / unique_loop_count

        sig_log_trj_flux = math.sqrt(
            abs((sum_sq_log_trj_flux - (sum_log_trj_flux ** 2) / unique_loop_count) / unique_loop_count))

        test_sig_log_flux = stddev(log_weight_flux)
        np_sig_weight = numpy.std(log_weight_flux)

        print 'std_weight:', sig_log_weight_flux, 'std_trj:', sig_log_trj_flux, 'std_func:', test_sig_log_flux, 'std_np:', np_sig_weight

        rrflux_weight = (av_log_weight_flux - min(log_weight_flux)) / sig_log_weight_flux

        rrflux_trj = (av_log_trj_flux - min(log_trj_flux)) / sig_log_trj_flux

        print "rrflux of weight: ", rrflux_weight

        print "rrflux of trj: ", rrflux_trj

        flux_result = (rrflux_weight, rrflux_trj)

        result_dict[miu] = flux_result

        file_dict[opponents] = result_dict

    for key in file_dict:
        with open('1e' + key + '.txt', 'w') as result_file:
            result_file.write("miu\trrflux_weight\trrfulx_flux\n")
            for mu in mu_list:
                result_file.write(
                    str(mu) + '\t' + str(file_dict[key][mu][0]) + '\t' + str(file_dict[key][mu][1]) + '\n')


if __name__ == "__main__":
    main()

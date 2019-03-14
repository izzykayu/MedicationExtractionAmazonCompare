from __future__ import print_function
import re
import os
import pprint
import sys
import glob
import pandas as pd

with open('results_example.txt') as fh:
    data = []
    for line in fh:
        data.append(eval(line))


def flatten_list(l):
    new = [item for sublist in l for item in sublist]
    return new


def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


entity_dict = {
    "MEDICATION": "Drug",
    "FREQUENCY": "Frequency",
    "ROUTE_OR_MODE": "Route",
    "DOSAGE": "Dosage",
    "STRENGTH": "Strength",
    "FORM": "Form",
    "DURATION": "Duration"
    }

entities_re = re.compile('(%s)' % '|'.join(entity_dict.keys()))


def replace_entities_n2c2(s):
    def replace(match):
        return entity_dict[match.group(0)]

    return entities_re.sub(replace, s)


import ujson


def amazon_convert_n2c2(example_path_prefix, data_line):
    f_out = open('/Users/isabelmetzger/PycharmProjects/MultiTaskLearningClinicalNLP/data/aws/' + str(
        example_path_prefix) + '.ann', 'w')

    counter = 0

    for x in flatten_list(data_line):
        counter += 1
        new_line = "T" + str(counter) + "\t" + replace_entities_n2c2(x['Category']) + " " + str(
            x['BeginOffset']) + " " + str(x['EndOffset']) + "\t" + x['Text']
        print(new_line)
        f_out.write(new_line + os.linesep)
        if x.get('Attributes') != None:
            attribute_list = x.get('Attributes')
            for a in attribute_list:
                counter += 1
                a_line = "T" + str(counter) + "\t" + replace_entities_n2c2(a['Type']) + " " + str(
                    a['BeginOffset']) + " " + str(a['EndOffset']) + "\t" + re.sub("\n", " ", a['Text'])
                print(a_line)
                f_out.write(a_line + os.linesep)
    print(counter)



def n2c2_convert_acm_concepts_only(infile_path_prefix):
    f_in = open('test/' + str(infile_path_prefix) + '.ann')
    f_out = open(
        '/Users/isabelmetzger/PycharmProjects/MultiTaskLearningClinicalNLP/data/ground_truths_concepts_only/' + str(
            infile_path_prefix) + 'c.ann', 'w')
    counter = 0
    incoming_list = f_in.readlines()
    pprint.pprint(incoming_list)
    new_list = []
    for line in incoming_list:
        if line.split('\t')[1].split(' ')[0].lower().strip() in ['drug', 'frequency', 'form',
                                                                 'duration', 'dosage',
                                                                 'strength', 'route']:
            print(line)
            counter += 1

            new_list.append(line)
            f_out.write(line)

#
if __name__ == '__main__':

    '''Convert acm output tag schemes among
    For example: if you want to convert the IOB tag scheme to BIO, then you run as following:
        python convert_acm_output.py ACM2N2C2 <input_prefix>
    '''
    # list_prefixes = [int(os.path.basename(f).split('.')[0]) for f in glob.glob('test/*.ann')]
    # for x in list_prefixes:
    #     n2c2_convert_acm_concepts_only(x)
    #     print('x mad
    if sys.argv[1].upper() == "ACM2N2C2":
        amazon_convert_n2c2(sys.argv[2])
    elif sys.argv[1].upper() == "N2C2CONCEPTS":
        n2c2_convert_acm_concepts_only(sys.argv[2])
    else:
        print("Argument error: sys.argv[1] should belongs to \"ACM2N2C2/N2C2CONCEPTS\"")

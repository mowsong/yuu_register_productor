#!/usr/bin/python
###################################################################################
# Copyright 2019 seabeam@yahoo.com - Licensed under the Apache License, Version 2.0
# For more information, see LICENCE in the main folder
###################################################################################
import os
import argparse

from openpyxl import load_workbook
from jinja2 import Environment, FileSystemLoader

from register_node import RegisterNode, walk
from xls_parser import XLSParser, get_bit_reset, format_hex


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description="Register generator argument process")
    arg_parser.add_argument('-n', '--name', required=True, dest='module_name')
    arg_parser.add_argument('-t', '--template', required=True, dest='template_name')
    arg_parser.add_argument('-i', '--input', required=True, dest='input_xlsx')
    arg_parser.add_argument('-o', '--output', required=False, dest='output_path', default='./')
    args = arg_parser.parse_args()
    script_dir = os.path.dirname(os.path.abspath(__file__))

    parser = XLSParser()
    parser.get_sheet('%s' %(args.input_xlsx))

    template_dir = '%s/template' %(script_dir)
    env = Environment(loader=FileSystemLoader(template_dir))
    env.trim_blocks = True
    env.lstrip_blocks = True
    env.filters['get_bit_reset'] = get_bit_reset
    env.filters['format_hex'] = format_hex
    template = env.get_template(args.template_name)

    root = parser.parse_data()
    root = parser.fill_reserved(root)
    root = parser.reorder_by_lsb(root)

    if not os.path.isdir('%s' %args.output_path):
        print("Output folder (%s) cannot be reached" %(args.output_path))
        exit(1)

    if args.template_name == 'html.j2':
        with open('%s/%s.htm' %(args.output_path, args.module_name), 'w', encoding='UTF-8') as f:
            f.write(template.render(module=args.module_name, root=root, width=32))
    elif args.template_name == 'uvm_reg_model.j2':
        with open('%s/%s_ral_model.sv' %(args.output_path, args.module_name), 'w', encoding='UTF-8') as f:
            f.write(template.render(module=args.module_name, root=root, width=32))
    
    print("Register productor generate done")
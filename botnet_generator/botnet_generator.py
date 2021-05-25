#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
##        Name: botnet_generator.py                                           #
##        Date: 19/05/2021                                                    #
## Description: Simple processor of kubernetes templates to create a          #
##              singularity botnet.                                           #
##----------------------------------------------------------------------------#
##      Editor: José Manuel Plana Santos                                      #
##     Contact: dev.josemanuelps@gmail.com                                    #
###############################################################################



# Imports.
import argparse
import os

# Definition of arguments.
parser = argparse.ArgumentParser(description = 'This script allows you to create a series of files that contain the information necessary to set up a botnet in a kubernetes cluster.')
parser.add_argument('path', type = str, help = 'Path where the files will be created.')
parser.add_argument('--name', type = str, help = 'Name of botnet. Default: Dirname of <(path)>')
parser.add_argument('--num', type = int, default = 10, help = 'Number of bots in botnet. Default: 10')
args = parser.parse_args()


class Main:

  def __init__(self):

    if args.num > 100:
      print('Error, num must be lower than 100.')
      exit(1)

    args.path = os.path.abspath(args.path)
    if not args.path.endswith('/'):
      args.path = args.path + '/'
    if not args.name:
      split_path = args.path.split('/')
      args.name = split_path[len(split_path) - 2]
    if not os.path.exists(args.path):
      os.mkdir(args.path)

    os.makedirs(args.path + 'inventory')
    os.makedirs(args.path + 'rules')

    inventory_file = open(args.path + 'inventory/hosts.yaml', 'w')
    inventory_file.write('---\n')
    inventory_file.write('all:\n')
    inventory_file.write('  hosts:\n')
    inventory_file.close()

    rules_file = open(args.path + 'rules/iptables.sh', 'w')
    rules_file.write('#!/bin/bash\n')
    rules_file.write('iptables -t nat -A POSTROUTING -j MASQUERADE -o enp39s0\n')
    rules_file.close()

    for x in range(args.num):
      if x < 10:
        self.create_deploy_file('0' + str(x))
        self.create_svc_file('0' + str(x))
        self.create_ansible_inventory_file('0' + str(x))
        self.iptables_rules('0' + str(x))
      else:
        self.create_deploy_file(str(x))
        self.create_svc_file(str(x))
        self.create_ansible_inventory_file(str(x))
        self.iptables_rules(str(x))

    print ('Done!')
    exit(0)

  def create_deploy_file(self, bot_number):

    src_file = open(os.path.dirname(os.path.abspath(__file__)) + '/templates/deploy.template.yaml', 'r')
    target_file = open(args.path + 'deploy.' + args.name + '.' + bot_number + '.yaml', 'w')
    
    for x in src_file.readlines():
      line = x
      if '$BOT_NUMBER$' in line:
        line = line.replace('$BOT_NUMBER$', bot_number)
      if '$BOTNET_NAME$' in line:
        line = line.replace('$BOTNET_NAME$', args.name)
      target_file.write(line)

    src_file.close()
    target_file.close()

  def create_svc_file(self, bot_number):

    src_file = open(os.path.dirname(os.path.abspath(__file__)) + '/templates/svc.template.yaml', 'r')
    target_file = open(args.path + 'svc.' + args.name + '.' + bot_number + '.yaml', 'w')
    
    for x in src_file.readlines():
      line = x
      if '$BOT_NUMBER$' in line:
        line = line.replace('$BOT_NUMBER$', bot_number)
      if '$BOTNET_NAME$' in line:
        line = line.replace('$BOTNET_NAME$', args.name)
      target_file.write(line)

    src_file.close()
    target_file.close()

  def create_ansible_inventory_file(self, bot_number):
    inventory_file = open(args.path + 'inventory/hosts.yaml', 'a')
    inventory_file.write('    deploy-' + args.name + '-'+ bot_number + ':\n')
    inventory_file.write('      ansible_host: svc-' + args.name + '-' + bot_number + '\n')
    inventory_file.write('      ansible_port: \'303' + bot_number + '\'\n')
    inventory_file.close()

  def iptables_rules(self, bot_number):
    
    rules_file = open(args.path + 'rules/iptables.sh', 'a')
    rules_file.write('iptables -A PREROUTING -t nat -p tcp --dport 303' + bot_number + ' -j DNAT --to 192.168.49.2:303' + bot_number + '\n')
    rules_file.write('iptables -A FORWARD -p tcp -m state --state NEW --dport 303' + bot_number + ' -j ACCEPT' + '\n')
    rules_file.close()


Main()

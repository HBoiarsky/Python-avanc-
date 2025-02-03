import sys

print(sys.argv)

commit_message =''

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-m', '--message')

args = parser.parse_args()

print('ArgumentParser a parsé le pramètre suivant: ', args.message)
commit_message = args.message

#!/usr/bin/python3
import pymongo
import getpass
import sys

from argument_parser import Argument, ArgumentParser, MissingArguments


class SubmitSystem:
    SUBMIT_DB_NAME = 'SUBMIT_SYSTEM'
    SUBMIT_PROMPT = 'Submit >>> '
    HELP = 'help'
    ADMIN = 'admin'

    def __init__(self):
        self.submit_db = None

        self.init_database()
        self.parser = self.init_parser()

    def init_database(self):
        total_mongo = pymongo.MongoClient('localhost', 27017)
        self.submit_db = total_mongo[self.SUBMIT_DB_NAME]

    def init_parser(self):
        parser = ArgumentParser()

        admin_branch, help_branch, course_branch = \
            parser.add_argument('branch', branching=[('admin', lambda x: x == 'admin'), ('help', lambda x: x == 'help'),
                                                     ('course', lambda x: True)],
                                help='select course, admin, or help')
        course_branch.help = 'Enter your course to submit files to it.'
        course_branch.add_argument('assignment', help='specify which assignment you are submitting')
        course_branch.add_argument('files', multiple=0, help='specify the files which you are submitting')

        admin_branch.add_argument('admin-select',
                                  help="choose one of: add-admin, remove-admin, create-course, delete-course, display-admins, display-courses")
        admin_branch.add_argument('names', optional=True, multiple=0)
        '''
        branching=[('add-admin', lambda x: x == 'add-admin'),
                                                             ('remove-admin', lambda x: x == 'remove-admin'),
                                                             ('create-course', lambda x: x == 'create-course'),
                                                             ('delete-course', lambda x: x == 'delete-course'),
                                                             ('display-admins', lambda x: x == 'display-admins'),
                                                             ('display-courses', lambda x: x == 'display-courses')],
        '''

        return parser

    def administrate(self, parsed_command):
        admin_collection = self.submit_db[self.ADMIN]
        course_collection = self.submit_db['courses']

        if parsed_command['admin-select'] == 'add-admin':
            for admin_name in parsed_command['names']:
                if not admin_collection.find_one({'uid': admin_name}):
                    admin_collection.insert_one({'uid': admin_name})
                    print('Admin {} inserted into database'.format(admin_name))
                else:
                    print('Admin {} duplicate detected'.format(admin_name))
        elif parsed_command['admin-select'] == 'remove-admin':
            for admin_name in parsed_command['names']:
                if admin_collection.find({'uid': admin_name}):
                    admin_collection.remove_one({'uid': admin_name})
                    print('Admin {} removed from database'.format(admin_name))
                else:
                    print('Admin {} not removed from database - not found'.format(admin_name))
        elif parsed_command['admin-select'] == 'create-course':
            pass
        elif parsed_command['admin-select'] == 'delete-course':
            pass
        elif parsed_command['admin-select'] == 'display-admins':
            for admin_record in admin_collection.find():
                print('Admin - {}'.format(admin_record['uid']))
        elif parsed_command['admin-select'] == 'display-courses':
            pass

    def run_system(self, command_arguments):
        command = input(self.SUBMIT_PROMPT)
        while command.strip().lower() not in ['quit', 'exit']:
            try:
                result = self.parser.parse_arguments(command.split())
                print(result)
                if self.ADMIN in result:
                    self.administrate(result)
                elif self.HELP in result:
                    print(self.parser.get_help())
                else:
                    print('you have entered course submission')
            except MissingArguments as ma:
                print('Missing Arguments')
                print(', '.join(ma.missing_arguments))
            command = input(self.SUBMIT_PROMPT)

        username = getpass.getuser()
        print(username)


if __name__ == '__main__':
    sub_sys = SubmitSystem()
    sub_sys.run_system(sys.argv)

class Argument:
    def __init__(self, name, optional=False, branching=None, multiple=1, terminate_multiple=None, help=None):
        self.name = name
        self.optional = optional
        if branching:
            self.branching = [(branch_name, branch_test, ArgumentParser()) for branch_name, branch_test in branching]
        else:
            self.branching = None
        self.multiple = multiple
        self.terminate_multiple = terminate_multiple
        self.help = help

    def __repr__(self):
        if self.branching:
            branch_help = '\tYou must choose one of the following:'
            for branch_name, branch_test, arg_parser in self.branching:
                branch_help += '\t\t' + branch_name + ':\n'
                branch_help += arg_parser.get_help()

            return branch_help

        return '\t'.join([self.name, self.help])


class MissingArguments(Exception):
    def __init__(self, missing_params):
        self.missing_arguments = missing_params


class ArgumentParser:

    def __init__(self, optional_tag='-', help=''):
        self.positional_arguments = []
        self.tag_arguments = {}
        self.optional_tag = optional_tag
        self.help = help

    def parse_arguments(self, split_string):
        """
            :param split_string: send a list of strings already split
            :return: parsed argument dictionary, containing the argument list required.
        """

        parsed_arugments = {}

        argument_index = 0
        command_index = 0
        multiple_counter = -1
        while command_index < len(self.positional_arguments) and argument_index < len(split_string):
            if self.positional_arguments[command_index].branching:
                for branch_name, branch_test, branch_parser in self.positional_arguments[command_index].branching:
                    print(branch_name)
                    if branch_test(split_string[argument_index]):
                        parsed_arugments[branch_name] = branch_name
                        parsed_arugments.update(branch_parser.parse_arguments(split_string[argument_index + 1:]))
                        return parsed_arugments
            else:
                if self.positional_arguments[command_index].multiple == 1:
                    parsed_arugments[self.positional_arguments[command_index].name] = split_string[argument_index]
                    command_index += 1
                    argument_index += 1
                elif not split_string[argument_index].startswith(self.optional_tag) and split_string[argument_index] != \
                        self.positional_arguments[command_index].terminate_multiple:

                    if multiple_counter == -1 and self.positional_arguments[command_index].multiple > 0:
                        parsed_arugments[self.positional_arguments[command_index].name] = [split_string[argument_index]]
                        multiple_counter = self.positional_arguments[command_index].multiple - 1
                    elif multiple_counter == -1:
                        parsed_arugments[self.positional_arguments[command_index].name] = [split_string[argument_index]]
                        multiple_counter = 0
                    elif multiple_counter == 0:
                        parsed_arugments[self.positional_arguments[command_index].name].append(
                            split_string[argument_index])
                    elif multiple_counter > 0:
                        parsed_arugments[self.positional_arguments[command_index].name].append(
                            split_string[argument_index])
                        multiple_counter -= 1
                        if multiple_counter == 0:
                            multiple_counter = -1
                            command_index += 1
                    argument_index += 1
                elif split_string[argument_index] == self.positional_arguments[command_index].terminate_multiple:
                    command_index += 1

        # TODO: implement optional arguments here

        missing_arguments = []
        for arg in self.positional_arguments:
            if not arg.optional and arg.name not in parsed_arugments:
                missing_arguments.append(arg.name)
        if missing_arguments:
            raise MissingArguments(missing_arguments)

        return parsed_arugments

    def add_argument(self, name, positional=True, optional=False, branching=None, multiple=1,
                     terminate_multiple=None, help='no help for this option'):
        if positional:
            if branching:
                self.positional_arguments.append(
                    Argument(name, optional, branching, multiple, terminate_multiple, help))
                return [t[2] for t in self.positional_arguments[-1].branching]
            self.positional_arguments.append(Argument(name, optional, branching, multiple, terminate_multiple, help))
        else:
            self.tag_arguments[name] = Argument(name, optional, branching, multiple, terminate_multiple, help)

    def get_help(self):
        help_string = ''
        help_string += '\t%s: \n\n' % self.help
        for argument in self.positional_arguments:
            help_string += '\t'*2 + repr(argument) + '\n'
        return help_string

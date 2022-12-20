from isa import *
import sys
import logging


class InvalidAsmException(Exception):
    def __init__(self, message="Parsing error"):
        self.message = "Invalid asm! " + message
        super().__init__(self.message)


def translate(text):
    data_flag = -1
    labels_searched = {}
    labels_present = {}
    variables_present = {}

    final_code = []

    line_number = 0
    # code_entry = -1

    for line in text.split("\n"):

        terms = line.strip().split(maxsplit=2)
        if len(terms) == 0:
            continue

        command_var_or_label = terms[0].strip()

        if command_var_or_label[-1] == ":":
            # label
            if len(terms) != 1:
                raise InvalidAsmException("Invalid label usage!")

            if command_var_or_label == ".text:":
                data_flag = 0
                # code_entry = line_number
            elif command_var_or_label == ".data:":
                data_flag = 1
            else:
                if data_flag == -1:
                    raise InvalidAsmException("Section is not set")
                elif data_flag == 1:
                    raise InvalidAsmException("Label in data section")
                else:
                    if command_var_or_label in labels_present:
                        raise InvalidAsmException("Label duplication")
                    else:
                        label_name = command_var_or_label[:-1]
                        labels_present[label_name] = line_number
                        if label_name in labels_searched:
                            # resolve missed dependencies
                            for resolved_line_num in labels_searched[label_name]:
                                ind = final_code[resolved_line_num]["args"].index(label_name)
                                final_code[resolved_line_num]["args"] = final_code[resolved_line_num]["args"][:ind] \
                                    + [line_number] \
                                    + final_code[resolved_line_num]["args"][ind+1:]
                            labels_searched.pop(label_name)
        else:
            if data_flag == 1:
                # data
                if len(terms) < 3:
                    raise InvalidAsmException("Invalid data section")
                variables_present[command_var_or_label] = line_number
                data_type = terms[1].strip()
                data = terms[2].strip()
                if data_type.upper() == "STRING":
                    data = data[1:-1]
                    for i in range(len(data)):
                        final_code.append(data[i])
                    final_code.append("\0")
                    line_number += len(data)+1
                elif data_type.upper() == "NUM":
                    final_code.append(int(data))
                    line_number += 1
                elif data_type.upper() == "CHAR":
                    if data[0] == "\"" or data[0] == "'":
                        data = data[1:-1]
                    else:
                        data = chr(int(data))
                    final_code.append(data)
                    line_number += 1
                else:
                    raise InvalidAsmException("Unknown data type!")

            elif data_flag == 0:

                found = -1
                opcodes = [item for item in AsmOpcode]
                for o in opcodes:

                    command_name = o.value

                    if command_var_or_label.upper() == command_name:
                        if len(terms) != opcode_args[command_name] + 1:
                            raise InvalidAsmException("Invalid arg num")
                        args = []
                        found = 1
                        braces = -1

                        if opcode_args[command_name] == 1:
                            # command with arg
                            arg = terms[1]
                            if arg[0] == "[":
                                arg = arg[1:-1]
                                braces = 1

                            if arg.lower() == "ac":
                                args.append(arg.upper())
                            elif arg in variables_present:
                                args.append(variables_present[arg])
                            elif arg in labels_present:
                                args.append(labels_present[arg])
                            else:
                                if arg in labels_searched:
                                    labels_searched[arg].append(line_number)
                                else:
                                    labels_searched[arg] = [line_number]
                                args.append(arg)

                        if command_name != "LD" and braces != -1:
                            raise InvalidAsmException("Wrong braces usage")

                        if command_name == "OUT":
                            command_name = "WR"
                            args = [-1]
                        elif command_name == "IN":
                            command_name = "LD_REL"
                            args = [-1]
                        elif command_name == "LD":
                            if braces == -1:
                                command_name = "LD_ABS"
                            else:
                                command_name = "LD_REL"

                        if command_name == "LD_ABS" and braces == -1 and args[0] == "AC":
                            raise InvalidAsmException("Wrong ac usage in ld command")
                        line_number += 1
                        command_binding = {"opcode": command_name, "args": args}
                        final_code.append(command_binding)
                        break
                if found == -1:
                    raise InvalidAsmException("Unknown command! {}".format(command_var_or_label))
            else:
                raise InvalidAsmException("Section is not set")

    print(final_code)
    print(labels_searched)
    print(labels_present)
    print(variables_present)
    # print(code_entry)

    return final_code


def main(args):
    assert len(args) == 2, \
        "Wrong arguments: translator.py <input_file> <target_file>"
    source, target = args

    with open(source, "rt", encoding="utf-8") as f:
        source = f.read()
    try:
        code = translate(source)
        print(code)
        # print("source LoC:", len(source.split()), "code instr:", len(code))
        write_code(target, code)
    except InvalidAsmException as e:
        logging.error(e.message)


if __name__ == '__main__':
    main(sys.argv[1:])

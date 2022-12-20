from enum import Enum
import json

# class AMode(Enum):
#     NO_ADDR = "NO_ADDR"
#     ABS = "ABS"
#     REL = "REL"


class AsmOpcode(Enum):
    CMP = "CMP"
    MOD = "MOD"
    JE = "JE"
    LD = "LD"
    WR = "WR"
    INC = "INC"
    DEC = "DEC"
    JMP = "JMP"
    SUB = "SUB"
    ADD = "ADD"
    HLT = "HLT"
    IN = "IN"
    OUT = "OUT"


class Opcode(Enum):
    CMP = "CMP"
    JE = "JE"
    MOD = "MOD"
    LD_ABS = "LD_ABS"
    LD_REL = "LD_REL"
    WR = "WR"
    INC = "INC"
    DEC = "DEC"
    JMP = "JMP"
    ADD = "ADD"
    SUB = "SUB"
    HLT = "HLT"


opcode_args = {
    AsmOpcode.CMP.name: 1,
    AsmOpcode.JE.name: 1,
    AsmOpcode.LD.name: 1,
    AsmOpcode.WR.name: 1,
    AsmOpcode.INC.name: 0,
    AsmOpcode.DEC.name: 0,
    AsmOpcode.JMP.name: 1,
    AsmOpcode.ADD.name: 1,
    AsmOpcode.HLT.name: 0,
    AsmOpcode.IN.name: 0,
    AsmOpcode.OUT.name: 0,
    AsmOpcode.MOD.name: 1,
    AsmOpcode.SUB.name: 1
}


def write_code(filename, code):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(json.dumps(code, indent=4))


def read_code(filename):
    with open(filename, encoding="utf-8") as file:
        code = json.loads(file.read())

    # for instr in code:
    #     instr['opcode'] = Opcode(instr['opcode'])
    #     if 'term' in instr:
    #         instr['term'] = Term(instr['term'][0], instr['term'][1],
    #                              AddrMode(instr['term'][2]), instr['term'][3])

    return code


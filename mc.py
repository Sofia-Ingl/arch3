from enum import Enum
from isa import Opcode


class MC(Enum):

    INSTR_FETCH = "IN_FETCH"

    ALU_RIGHT_MUX_ZERO = "ALU_RIGHT_MUX_ZERO"
    ALU_RIGHT_MUX_MEM = "ALU_RIGHT_MUX_MEM"

    ALU_LEFT_MUX_ZERO = "ALU_LEFT_MUX_ZERO"
    ALU_LEFT_MUX_ACC = "ALU_LEFT_MUX_ACC"

    ALU_SUB = "ALU_SUB"
    ALU_ADD = "ALU_ADD"
    ALU_INC = "ALU_INC"
    ALU_DEC = "ALU_DEC"
    ALU_MOD = "ALU_MOD"

    ACC_MUX_ALU = "ACC_MUX_ALU"
    ACC_MUX_MEM = "ACC_MUX_MEM"
    ACC_MUX_INSTR_ADDR_PART = "ACC_MUX_INSTR_ADDR_PART"

    ACC_WRITE_INTO_MEM = "ACC_WRITE_INTO_MEM"

    IP_MUX_INC = "IP_MUX_INC"
    IP_MUX_INSTR_ADDR_PART = "IP_MUX_INSTR_ADDR_PART"

    ADDR_MUX_INSTR_ADDR_PART = "ADDR_MUX_INSTR_ADDR_PART"
    ADDR_MUX_ACC = "ADDR_MUX_ACC"

    ACC_LATCH = "ACC_LATCH"
    IP_LATCH = "IP_LATCH"
    ADDR_LATCH = "ADDR_LATCH"

    Z_SET_GOTO = "Z_SET_GOTO"
    GOTO = "GOTO"
    CMP_INSTR_NOT_EQ_GOTO = "CMP_INSTR_NOT_EQ_GOTO"
    CMP_INSTR_ARG_NOT_EQ_GOTO = "CMP_INSTR_ARG_NOT_EQ_GOTO"

    STOP = "STOP"
    DECODING_ERR = "DECODING_ERR"


default_mc_memory = [
    {"opcode": MC.INSTR_FETCH, "args": [], "tick_num": 0},

    {"opcode": MC.CMP_INSTR_NOT_EQ_GOTO, "args": [Opcode.CMP, 8], "tick_num": 1},

    {"opcode": MC.ADDR_MUX_INSTR_ADDR_PART, "args": [], "tick_num": 1},
    {"opcode": MC.ADDR_LATCH, "args": [], "tick_num": 1},
    {"opcode": MC.ALU_RIGHT_MUX_MEM, "args": [], "tick_num": 2},
    {"opcode": MC.ALU_LEFT_MUX_ACC, "args": [], "tick_num": 2},
    {"opcode": MC.ALU_SUB, "args": [], "tick_num": 2},
    {"opcode": MC.GOTO, "args": [74], "tick_num": 2},  # ip++

    {"opcode": MC.CMP_INSTR_NOT_EQ_GOTO, "args": [Opcode.JE, 11], "tick_num": 1},   # 8

    {"opcode": MC.Z_SET_GOTO, "args": [77], "tick_num": 1},  # addr part of command to ip
    {"opcode": MC.GOTO, "args": [74], "tick_num": 1},  # ip ++

    {"opcode": MC.CMP_INSTR_NOT_EQ_GOTO, "args": [Opcode.LD_ABS, 15], "tick_num": 1},

    {"opcode": MC.ACC_MUX_INSTR_ADDR_PART, "args": [], "tick_num": 1},
    {"opcode": MC.ACC_LATCH, "args": [], "tick_num": 1},
    {"opcode": MC.GOTO, "args": [74], "tick_num": 1},  # ip++

    {"opcode": MC.CMP_INSTR_NOT_EQ_GOTO, "args": [Opcode.LD_REL, 24], "tick_num": 1},  # 15

    {"opcode": MC.CMP_INSTR_ARG_NOT_EQ_GOTO, "args": ["AC", 19], "tick_num": 1},  # go to fetch from mem
    {"opcode": MC.ADDR_MUX_ACC, "args": [], "tick_num": 1},
    {"opcode": MC.GOTO, "args": [20], "tick_num": 1},  # skip next micro command
    {"opcode": MC.ADDR_MUX_INSTR_ADDR_PART, "args": [], "tick_num": 1},  # 19
    {"opcode": MC.ADDR_LATCH, "args": [], "tick_num": 1},
    {"opcode": MC.ACC_MUX_MEM, "args": [], "tick_num": 2},
    {"opcode": MC.ACC_LATCH, "args": [], "tick_num": 2},
    {"opcode": MC.GOTO, "args": [74], "tick_num": 2},  # ip++

    {"opcode": MC.CMP_INSTR_NOT_EQ_GOTO, "args": [Opcode.WR, 29], "tick_num": 1},  # 24

    {"opcode": MC.ADDR_MUX_INSTR_ADDR_PART, "args": [], "tick_num": 1},
    {"opcode": MC.ADDR_LATCH, "args": [], "tick_num": 1},
    {"opcode": MC.ACC_WRITE_INTO_MEM, "args": [], "tick_num": 2},
    {"opcode": MC.GOTO, "args": [74], "tick_num": 2},  # ip++

    {"opcode": MC.CMP_INSTR_NOT_EQ_GOTO, "args": [Opcode.INC, 36], "tick_num": 1},  # 29

    {"opcode": MC.ALU_LEFT_MUX_ACC, "args": [], "tick_num": 1},
    {"opcode": MC.ALU_RIGHT_MUX_ZERO, "args": [], "tick_num": 1},
    {"opcode": MC.ALU_INC, "args": [], "tick_num": 1},
    # {"opcode": MC.ALU_WRITE_BUS, "args": [], "tick_num": 1},
    {"opcode": MC.ACC_MUX_ALU, "args": [], "tick_num": 1},
    {"opcode": MC.ACC_LATCH, "args": [], "tick_num": 1},
    {"opcode": MC.GOTO, "args": [74], "tick_num": 1},  # ip++

    {"opcode": MC.CMP_INSTR_NOT_EQ_GOTO, "args": [Opcode.DEC, 43], "tick_num": 1},  # 36

    {"opcode": MC.ALU_LEFT_MUX_ACC, "args": [], "tick_num": 1},
    {"opcode": MC.ALU_RIGHT_MUX_ZERO, "args": [], "tick_num": 1},
    {"opcode": MC.ALU_DEC, "args": [], "tick_num": 1},
    # {"opcode": MC.ALU_WRITE_BUS, "args": [], "tick_num": 1},
    {"opcode": MC.ACC_MUX_ALU, "args": [], "tick_num": 1},
    {"opcode": MC.ACC_LATCH, "args": [], "tick_num": 1},
    {"opcode": MC.GOTO, "args": [74], "tick_num": 1},  # ip++

    {"opcode": MC.CMP_INSTR_NOT_EQ_GOTO, "args": [Opcode.MOD, 52], "tick_num": 1},  # 43

    {"opcode": MC.ADDR_MUX_INSTR_ADDR_PART, "args": [], "tick_num": 1},
    {"opcode": MC.ADDR_LATCH, "args": [], "tick_num": 1},
    {"opcode": MC.ALU_LEFT_MUX_ACC, "args": [], "tick_num": 2},
    {"opcode": MC.ALU_RIGHT_MUX_MEM, "args": [], "tick_num": 2},
    {"opcode": MC.ALU_MOD, "args": [], "tick_num": 2},
    # {"opcode": MC.ALU_WRITE_BUS, "args": [], "tick_num": 2},
    {"opcode": MC.ACC_MUX_ALU, "args": [], "tick_num": 2},
    {"opcode": MC.ACC_LATCH, "args": [], "tick_num": 2},
    {"opcode": MC.GOTO, "args": [74], "tick_num": 2},  # ip++

    {"opcode": MC.CMP_INSTR_NOT_EQ_GOTO, "args": [Opcode.JMP, 54], "tick_num": 1},  # 52

    {"opcode": MC.GOTO, "args": [77], "tick_num": 1},  # addr part of command to ip

    {"opcode": MC.CMP_INSTR_NOT_EQ_GOTO, "args": [Opcode.ADD, 63], "tick_num": 1},  # 54

    {"opcode": MC.ADDR_MUX_INSTR_ADDR_PART, "args": [], "tick_num": 1},
    {"opcode": MC.ADDR_LATCH, "args": [], "tick_num": 1},
    {"opcode": MC.ALU_LEFT_MUX_ACC, "args": [], "tick_num": 2},
    {"opcode": MC.ALU_RIGHT_MUX_MEM, "args": [], "tick_num": 2},
    {"opcode": MC.ALU_ADD, "args": [], "tick_num": 2},
    # {"opcode": MC.ALU_WRITE_BUS, "args": [], "tick_num": 2},
    {"opcode": MC.ACC_MUX_ALU, "args": [], "tick_num": 2},
    {"opcode": MC.ACC_LATCH, "args": [], "tick_num": 2},
    {"opcode": MC.GOTO, "args": [74], "tick_num": 2},  # ip++

    {"opcode": MC.CMP_INSTR_NOT_EQ_GOTO, "args": [Opcode.SUB, 72], "tick_num": 1},  # 63

    {"opcode": MC.ADDR_MUX_INSTR_ADDR_PART, "args": [], "tick_num": 1},
    {"opcode": MC.ADDR_LATCH, "args": [], "tick_num": 1},
    {"opcode": MC.ALU_LEFT_MUX_ACC, "args": [], "tick_num": 2},
    {"opcode": MC.ALU_RIGHT_MUX_MEM, "args": [], "tick_num": 2},
    {"opcode": MC.ALU_SUB, "args": [], "tick_num": 2},
    # {"opcode": MC.ALU_WRITE_BUS, "args": [], "tick_num": 2},
    {"opcode": MC.ACC_MUX_ALU, "args": [], "tick_num": 2},
    {"opcode": MC.ACC_LATCH, "args": [], "tick_num": 2},
    {"opcode": MC.GOTO, "args": [74], "tick_num": 2},  # ip++

    {"opcode": MC.CMP_INSTR_NOT_EQ_GOTO, "args": [Opcode.HLT, 80], "tick_num": 1},  # 72

    {"opcode": MC.GOTO, "args": [81], "tick_num": 1},  # cpu stop

    {"opcode": MC.IP_MUX_INC, "args": [], "tick_num": 3},  # 74 <-ip++
    {"opcode": MC.IP_LATCH, "args": [], "tick_num": 3},

    {"opcode": MC.GOTO, "args": [0], "tick_num": 3},  # next instr fetch


    {"opcode": MC.IP_MUX_INSTR_ADDR_PART, "args": [], "tick_num": 3},  # 77
    {"opcode": MC.IP_LATCH, "args": [], "tick_num": 3},

    {"opcode": MC.GOTO, "args": [0], "tick_num": 3},  # next instr fetch

    {"opcode": MC.DECODING_ERR, "args": [], "tick_num": 3},  # err 80
    {"opcode": MC.STOP, "args": [], "tick_num": 3},  # stop 81


]

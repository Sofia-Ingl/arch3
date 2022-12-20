from mc import MC, default_mc_memory
import logging
import sys
from isa import read_code


class CommonMemory:

    def __init__(self, sz, input_buffer):
        assert sz > 0, "Memory size should be non-zero"
        self.mem = [0 for _ in range(sz)]
        self.size = sz
        self.input_buffer = input_buffer
        self.output_buffer = []
        self.input_mapping_addr = sz - 2
        self.output_mapping_addr = sz - 1
        self.available_memory_end_excluded = sz - 2

    def write(self, value, addr):
        assert (addr < self.size) and (addr >= 0), "Invalid address"
        assert addr != self.input_mapping_addr, "Mapped io memory illegal access"
        self.mem[addr] = value
        if addr == self.output_mapping_addr:
            self.output_buffer.append(value)

    def read(self, addr):
        assert (addr < self.size) and (addr >= 0), "Invalid address"
        if addr == self.input_mapping_addr:
            if len(self.input_buffer) == 0:
                raise EOFError()
            return self.input_buffer.pop(0)
        return self.mem[addr]


acc_mux_sigs = {
    MC.ACC_MUX_ALU: 0,
    MC.ACC_MUX_MEM: 1,
    MC.ACC_MUX_INSTR_ADDR_PART: 2
}

ip_mux_sigs = {
    MC.IP_MUX_INC: 0,
    MC.IP_MUX_INSTR_ADDR_PART: 1
}

addr_mux_sigs = {
    MC.ADDR_MUX_ACC: 0,
    MC.ADDR_MUX_INSTR_ADDR_PART: 1
}

alu_left_mux_sigs = {
    MC.ALU_LEFT_MUX_ZERO: 0,
    MC.ALU_LEFT_MUX_ACC: 1
}

alu_right_mux_sigs = {
    MC.ALU_RIGHT_MUX_ZERO: 0,
    MC.ALU_RIGHT_MUX_MEM: 1
}


class DataPath:

    def __init__(self, common_memory):
        self.allowed_max = 2 ** 31 - 1
        self.allowed_min = -2 ** 31

        self.common_memory = common_memory

        self.acc = 0
        self.addr = 0
        self.ip = 0
        self.instr = {"opcode": "NO_INSTR", "args": []}

        self.alu = 0
        self.z = 0
        # self.alu_out_bus = 0

        self.alu_right_mux = 0
        self.alu_left_mux = 0
        self.acc_mux = 0
        self.ip_mux = 0
        self.addr_mux = 0

    def fetch_instr(self):
        self.instr = self.common_memory.read(self.ip)

    def write_acc_into_mem(self):
        self.common_memory.write(self.acc, self.addr)

    def acc_mux_sig(self, mc):
        self.acc_mux = acc_mux_sigs[mc]

    def ip_mux_sig(self, mc):
        self.ip_mux = ip_mux_sigs[mc]

    def addr_mux_sig(self, mc):
        self.addr_mux = addr_mux_sigs[mc]

    def acc_latch(self):
        if self.acc_mux == acc_mux_sigs[MC.ACC_MUX_ALU]:
            self.acc = self.alu
        elif self.acc_mux == acc_mux_sigs[MC.ACC_MUX_MEM]:
            self.acc = self.common_memory.read(self.addr)
        elif self.acc_mux == acc_mux_sigs[MC.ACC_MUX_INSTR_ADDR_PART]:
            self.acc = self.instr["args"][0]

    def ip_latch(self):
        if self.ip_mux == ip_mux_sigs[MC.IP_MUX_INC]:
            self.ip = self.ip + 1
        elif self.ip_mux == ip_mux_sigs[MC.IP_MUX_INSTR_ADDR_PART]:
            self.ip = self.instr["args"][0]

    def addr_latch(self):
        if self.addr_mux == addr_mux_sigs[MC.ADDR_MUX_ACC]:
            self.addr = self.acc
        elif self.addr_mux == addr_mux_sigs[MC.ADDR_MUX_INSTR_ADDR_PART]:
            self.addr = self.instr["args"][0]

    def register_latch(self, mc):
        if mc == MC.ACC_LATCH:
            self.acc_latch()
        elif mc == MC.IP_LATCH:
            self.ip_latch()
        elif mc == MC.ADDR_LATCH:
            self.addr_latch()

    def alu_mux_sig(self, mc):
        if mc in {MC.ALU_RIGHT_MUX_ZERO, MC.ALU_RIGHT_MUX_MEM}:
            self.alu_right_mux = alu_right_mux_sigs[mc]
        elif mc in {MC.ALU_LEFT_MUX_ZERO, MC.ALU_LEFT_MUX_ACC}:
            self.alu_left_mux = alu_left_mux_sigs[mc]

    def alu_overflow_process(self, operand):
        if operand > self.allowed_max or operand < self.allowed_min:
            operand = self.allowed_max & operand
        return operand

        # while operand > allowed_max:
        #     operand = allowed_min + (operand - allowed_max)
        # while operand < allowed_min:
        #     operand = allowed_max + (operand - allowed_min)

    def alu_calc(self, mc):
        left_op = 0 if self.alu_left_mux == 0 else self.acc
        if type(left_op) is str:
            left_op = ord(left_op[0])
        right_op = 0 if self.alu_right_mux == 0 else self.common_memory.read(self.addr)
        if type(right_op) is str:
            right_op = ord(right_op[0])
        res = left_op | right_op
        if mc == MC.ALU_SUB:
            res = left_op - right_op
        elif mc == MC.ALU_ADD:
            res = left_op + right_op
        elif mc == MC.ALU_INC:
            # res = (left_op | right_op) + 1
            res = left_op + 1
        elif mc == MC.ALU_DEC:
            # res = (left_op | right_op) - 1
            res = left_op - 1
        elif mc == MC.ALU_MOD:
            res = left_op % right_op
        res = self.alu_overflow_process(res)
        self.alu = res
        self.z = 1 if (res == 0) else 0


# class StopIteration(Exception):
#     def __init__(self, message = "HLT command"):
#         self.message = message
#         super().__init__(self.message)


class ControlUnit:

    def __init__(self, mc_memory, data_path, code):
        assert len(code) < data_path.common_memory.available_memory_end_excluded, "Prog & data is too big"
        assert len(mc_memory) > 1, "Invalid mc mem initialization"
        self.data_path = data_path
        self.mc_memory = mc_memory
        self.mc_pointer = 0
        self.program_entry = self.load_module(code)  # load code & data
        self.data_path.ip = self.program_entry
        self._tick = 0

    def load_module(self, code):
        sz = len(code)
        assert sz <= self.data_path.common_memory.size - 2, "Not enough memory"
        program_entry = -1
        for i in range(len(code)):
            if program_entry == -1:
                if type(code[i]) is dict:
                    program_entry = i
            if program_entry != -1:
                # resolve io memory mappings
                if len(code[i]["args"]) > 0 and code[i]["args"][0] == -1:
                    if code[i]["opcode"] == "LD_ABS" or code[i]["opcode"] == "LD_REL":
                        code[i]["args"][0] = self.data_path.common_memory.input_mapping_addr
                    elif code[i]["opcode"] == "WR":
                        code[i]["args"][0] = self.data_path.common_memory.output_mapping_addr
            self.data_path.common_memory.mem[i] = code[i]
        return program_entry

    def inc_mc_pointer(self):
        self.mc_pointer += 1

    def try_set_mc_pointer(self, new_pos, cond):
        if cond:
            self.mc_pointer = new_pos
        else:
            self.inc_mc_pointer()

    def mc_process(self):
        mc = self.mc_memory[self.mc_pointer]
        # process

        if mc["opcode"] is MC.INSTR_FETCH:
            self.data_path.fetch_instr()
        elif mc["opcode"] in {MC.ALU_RIGHT_MUX_ZERO, MC.ALU_RIGHT_MUX_MEM, MC.ALU_LEFT_MUX_ZERO, MC.ALU_LEFT_MUX_ACC}:
            self.data_path.alu_mux_sig(mc["opcode"])
        elif mc["opcode"] in {MC.ALU_SUB, MC.ALU_ADD, MC.ALU_INC, MC.ALU_DEC, MC.ALU_MOD}:
            self.data_path.alu_calc(mc["opcode"])
        elif mc["opcode"] in {MC.ACC_MUX_ALU, MC.ACC_MUX_MEM, MC.ACC_MUX_INSTR_ADDR_PART}:
            self.data_path.acc_mux_sig(mc["opcode"])
        elif mc["opcode"] is MC.ACC_WRITE_INTO_MEM:
            self.data_path.write_acc_into_mem()
        elif mc["opcode"] in {MC.IP_MUX_INC, MC.IP_MUX_INSTR_ADDR_PART}:
            self.data_path.ip_mux_sig(mc["opcode"])
        elif mc["opcode"] in {MC.ADDR_MUX_ACC, MC.ADDR_MUX_INSTR_ADDR_PART}:
            self.data_path.addr_mux_sig(mc["opcode"])
        elif mc["opcode"] in {MC.ACC_LATCH, MC.IP_LATCH, MC.ADDR_LATCH}:
            self.data_path.register_latch(mc["opcode"])
        elif mc["opcode"] is MC.STOP:
            # raise StopIteration()
            return -1
        elif mc["opcode"] is MC.DECODING_ERR:
            # raise StopIteration("Decoding error occurred")
            return -2

        if mc["opcode"] in {MC.Z_SET_GOTO, MC.GOTO, MC.CMP_INSTR_NOT_EQ_GOTO, MC.CMP_INSTR_ARG_NOT_EQ_GOTO}:
            cond = False
            if mc["opcode"] is MC.Z_SET_GOTO:
                cond = self.data_path.z == 1
            elif mc["opcode"] is MC.GOTO:
                cond = True
            elif mc["opcode"] is MC.CMP_INSTR_NOT_EQ_GOTO:
                cond = mc["args"][0].name != self.data_path.instr["opcode"]
            elif mc["opcode"] is MC.CMP_INSTR_ARG_NOT_EQ_GOTO:
                cond = mc["args"][0] != self.data_path.instr["args"][0]
            self.try_set_mc_pointer(mc["args"][-1], cond)
        else:
            self.inc_mc_pointer()
        return mc["tick_num"]

    # fetch instr
    # decode instr
    # process microcode tick by tick

    def decode_and_execute_instruction(self):
        self.mc_pointer = 0
        tick_num = self.mc_process()
        ticks = [tick_num]
        self.tick()
        while tick_num >= 0 and self.mc_pointer > 0:  # tick < 0 if hlt or err (?); mc ptr == 0 after goto instr fetch
            tick_num = self.mc_process()
            # if (tick_num != ticks[-1]) and (tick_num > 0):
            if tick_num != ticks[-1]:
                logging.debug('%s', self)
                ticks.append(tick_num)
                self.tick()
        if tick_num == -1:
            raise StopIteration()
        elif tick_num == -2:
            raise StopIteration("Decoding error occurred")

    def tick(self):
        self._tick += 1

    def current_tick(self):
        return self._tick

    def __repr__(self):
        state = "{{TICK: {}, ADDR: {}, IP: {}, ACC: {}, Z: {}}}".format(
            self._tick,
            self.data_path.addr,
            self.data_path.ip,
            self.data_path.acc,
            self.data_path.z
        )

        instr = self.data_path.instr
        opcode = instr["opcode"]
        arg = instr["args"][0] if len(instr["args"]) > 0 else "no arg"
        action = "{} {}".format(opcode, arg)

        return "{} {}".format(state, action)


def simulation(code, input_tokens, data_memory_size, limit):
    common_memory = CommonMemory(data_memory_size, input_tokens)
    data_path = DataPath(common_memory)
    control_unit = ControlUnit(default_mc_memory, data_path, code)
    instr_counter = 0

    # logging.debug('%s', control_unit)
    try:
        while True:
            assert limit > instr_counter, "too long execution, increase limit!"
            control_unit.decode_and_execute_instruction()
            instr_counter += 1
            logging.debug('%s', control_unit)

    except EOFError:
        logging.debug('%s', control_unit)
        logging.warning('Input buffer is empty!')
    except StopIteration:
        instr_counter += 1
        logging.debug('%s', control_unit)
        logging.warning('Iteration stopped by HLT')
    # logging.info('output_buffer: %s', repr(''.join(data_path.output_buffer)))
    # return common_memory.output_buffer, instr_counter, control_unit.current_tick()
    common_memory.output_buffer = [str(i) for i in common_memory.output_buffer]
    return ''.join(common_memory.output_buffer), instr_counter, control_unit.current_tick()


def main(args):
    assert len(args) == 2, "Wrong arguments: machine.py <code_file> <input_file>"
    code_file, input_file = args

    code = read_code(code_file)
    # print(code)
    with open(input_file, encoding="utf-8") as file:
        input_text = file.read()
        input_token = []
        for char in input_text:
            input_token.append(char)
    input_token.append("\0")

    output, instr_counter, ticks = simulation(code, input_tokens=input_token, data_memory_size=100, limit=25000)
    print(output)
    print("instr_counter:", instr_counter, "ticks:", ticks)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    main(sys.argv[1:])

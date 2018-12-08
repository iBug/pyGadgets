#!/usr/bin/python3

import sys
import os
import math
import random
import subprocess as sp

import re


LC3SIM = os.path.dirname(os.path.realpath(__file__))+ "/lc3sim"
objfile = "test.obj"
PC_IR_PSR_REGEX = re.compile(r"^PC=x(?P<PC>[0-9A-F]{4}) IR=x(?P<IR>[0-9A-F]{4}) PSR=x[0-9A-F]{4} \((?P<PSR>\w+)\)")
REG_REGEX_S = "^" + " *".join([r"R{}=x([0-9A-F]{{4}})".format(n) for n in range(8)])
REG_REGEX = re.compile(REG_REGEX_S)


class LC3Controller:
    def __init__(self, objfile):
        self.p = None
        self.objfile = objfile
        self.PC = self.IR = self.PSR = None
        self.R0 = self.R1 = self.R2 = self.R3 = \
            self.R4 = self.R5 = self.R6 = self.R7 = None
        self.on_breakpoint = False

    def getline(self):
        line = self.p.stdout.readline().strip()
        return line

    def putline(self, line):
        line += "\n"
        self.p.stdin.write(line)
        self.p.stdin.flush()

    def open(self):
        global LC3SIM
        self.p = sp.Popen(["stdbuf", "-o0", LC3SIM, self.objfile], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT, universal_newlines=True, bufsize=0)

        # Process startup text
        while True:
            line = self.getline()
            if line.startswith("---") and line.endswith("---"):
                # Empty line
                self.getline()
                # PC, IR and PSR
                line = self.getline()
                self.parse_pc_ir_psr(line)
                # Registers
                line = self.getline()
                self.parse_registers(line)

                # Instruction line + "Loaded file" line
                self.getline()
                self.getline()
                break
        return self

    def parse_pc_ir_psr(self, line):
        match = PC_IR_PSR_REGEX.search(line)
        self.PC = match['PC']
        self.IR = match['IR']
        self.PSR = match['PSR']

    def parse_registers(self, line):
        match = REG_REGEX.search(line)
        for n in range(8):
            setattr(self, "R{}".format(n), match.group(n + 1))

    def set_register(self, r_num, value):
        if isinstance(value, int):
            value = "{:04X}".format(value)
        cmd = "register r{} {}".format(r_num, value)
        self.putline(cmd)
        assert self.getline().startswith("(lc3sim)")

    def set_breakpoint(self, value):
        if isinstance(value, int):
            value = "{:04X}".format(value)
        cmd = "break set {}".format(value)
        self.putline(cmd)
        assert self.getline().startswith("(lc3sim)")

    def step(self):
        self.putline("step")
        line = self.getline()
        assert line.startswith("(lc3sim)")
        line = line[len("(lc3sim)"):].strip()
        if line.startswith("The LC-3 hit a breakpoint"):
            self.on_breakpoint = True
            line = self.getline()
        else:
            self.on_breakpoint = False
        self.parse_pc_ir_psr(line)
        line = self.getline()
        self.parse_registers(line)
        self.getline()

    def quit(self):
        self.putline("quit")
        self.p.communicate()
        assert self.p.poll() is not None

    def __del__(self):
        try:
            self.quit()
        except Exception:
            pass

    def reset(self):
        self.on_breakpoint = False
        self.putline("reset")
        while True:
            line = self.getline()
            if line.startswith("---") and line.endswith("---"):
                # Empty line
                self.getline()
                # PC, IR and PSR
                line = self.getline()
                self.parse_pc_ir_psr(line)
                # Registers
                line = self.getline()
                self.parse_registers(line)

                # Instruction line + "Loaded file" line
                self.getline()
                self.getline()
                break


def find_halts(filename):
    with open(filename, "rb") as f:
        data = f.read()
    data = [(H << 8) | L for H, L in zip(data[::2], data[1::2])]
    orig = data[0]
    data = data[1:]
    halts = []
    for ind, obj in enumerate(data):
        if obj == 0xF025:  # HALT instruction
            halts.append(orig + ind)
    return halts


def lc3int(s):
    i = int(s, 16)
    if i >= 0x8000:
        i -= 0x10000
    return i


def run_single(lc3, a, b, count=False):
    global halts
    lc3.reset()
    for halt in halts:
        lc3.set_breakpoint(halt)

    lc3.set_register(0, a)
    lc3.set_register(1, b)
    step = 0
    while not lc3.on_breakpoint:
        step += 1
        if count:
            print("\rStep: {}".format(step), end="")
        lc3.step()
    step += 1  # HALT instruction
    if count:
        print("\rStep: {}".format(step))
    return step, lc3int(lc3.R0)


def main():
    global objfile, halts
    halts = find_halts(objfile)
    lc3 = LC3Controller(objfile).open()
    if len(sys.argv) == 2:
        count = int(sys.argv[1])
        steps = []
        inputs = []
        for i in range(count):
            a = random.randint(1, 0x7FFF)
            b = random.randint(1, 0x7FFF)
            answer = math.gcd(a, b)
            step, result = run_single(lc3, a, b)
            if answer != result:
                print("Wrong answer: A = {}, B = {}, expected {}, got {}".format(
                    a, b, answer, result))
                exit(1)
            steps.append(step)
            inputs.append((a, b))
        print("Ran {} times".format(count))
        print("Average steps = {:.3f}".format(sum(steps) / len(steps)))
        max_i = steps.index(max(steps))
        min_i = steps.index(min(steps))
        print("Min steps = {}, input = {}".format(steps[min_i], inputs[min_i]))
        print("Max steps = {}, input = {}".format(steps[max_i], inputs[max_i]))
        return

    if len(sys.argv) >= 3:
        r0 = int(sys.argv[1]) & 0xFFFF
        r1 = int(sys.argv[2]) & 0xFFFF
    else:
        r0 = random.randint(1, 0x7FFF)
        r1 = random.randint(1, 0x7FFF)
    answer = math.gcd(r0, r1)
    print("Input: A = {}, B = {}, expected = {}".format(r0, r1, answer))
    step, result = run_single(lc3, r0, r1, count=True)
    print("Result: {}".format(result))


if __name__ == "__main__":
    main()

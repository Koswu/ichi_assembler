import struct

import click
import sys
import os

TOTAL_MEMORY_SIZE = 1 << 16

TOKEN_BASE_CODE = {
    'loadn': 0x00000000,
    'loadp': 0x00010000,
    'storep': 0x00020000,
    'mov': 0x00030000,
    'add': 0x00100000,
    'or': 0x00110000,
    'and': 0x00120000,
    'not': 0x00130000,
    'xor': 0x00140000,
    'lshift': 0x00150000,
    'rshift': 0x00160000,
    'le': 0x00170000,
    'gt': 0x00180000,
    'eq': 0x00190000,
    'jmp': 0x00200000,
    'nop': 0x00210000,
    'halt': 0x00220000,
}
REG_CODES = {
    'ax': 0x00,
    'bx': 0x01,
    'cx': 0x02,
    'dx': 0x03,

    'pc': 0x10,
    'sp': 0x11,
    'bp': 0x12,
    'flag': 0x13,
}

PSEUDO_TOKENS = [
    'db', 'org'
]


def parse_line(line):
    if line[0] == '.':
        return b''
    parts = line.split()


def parse_number(number_str):
    if number_str[-1] == 'H':
        res = int(number_str[:-1], 16)
    else:
        res = int(number_str, 10)
    assert 0 <= res < (1 << 16)
    return res


def parse_bytes_value(value):
    # is str
    if value[0] in ('"', "'"):
        assert len(value) > 2
        assert value[-1] == value[0], value
        return bytes(value[1:-1], encoding='utf-8')
    # is number
    num = parse_number(value)
    assert 0 <= num <= 255
    return struct.pack('B', num)


@click.command()
@click.argument('input_file', type=click.File('r'))
def main(input_file):
    output_filename = os.path.splitext(input_file.name)[0] + '.bin'
    output_file = open(output_filename, 'wb')
    # init output file, let's use \00 to fill it
    output_file.write(b'\00' * TOTAL_MEMORY_SIZE)
    # seek to file head
    output_file.seek(0, 0)
    lines = input_file.read().split('\n')
    for line in lines:
        line = line.strip()
        if line[0] in ['.', ';']:
            continue
        tokens = line.split(' ', 1)
        tokens[0] = tokens[0].lower()
        if tokens[0] == 'org':
            address = parse_number(tokens[1])
            output_file.seek(address, 0)
            continue
        elif tokens[0] == 'db':
            output_file.write(parse_bytes_value(tokens[1]))
            continue
        assert tokens[0] in TOKEN_BASE_CODE, f'{tokens[0]} token invalid'
        write_data = TOKEN_BASE_CODE[tokens[0]]
        if tokens[0] == 'loadn':
            write_data += parse_number(tokens[1])
        elif tokens[0] == 'mov':
            regs = tokens[1].split(',')
            regs = [reg.lower().strip() for reg in regs]
            assert len(regs) == 2
            assert all([reg in REG_CODES for reg in regs]), f"{regs} not in REG_CODES"
            write_data += (REG_CODES[regs[0]]) << 8 + REG_CODES[regs[1]]
        output_file.write(struct.pack('I', write_data))
    output_file.seek(0, 2)
    assert output_file.tell() == TOTAL_MEMORY_SIZE
    output_file.close()


if __name__ == '__main__':
    main()

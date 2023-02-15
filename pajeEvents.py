#!/usr/bin/python3
import argparse
import random
import string

import random

def ordered_string_generator(n=0):
    yield "inst_%d" % n
    number = n + 1
    yield from ordered_string_generator(number)

# gerar um id numero em ordem
def random_string_generator(str_size=1):
    # allowed_chars = string.ascii_letters + string.punctuation
    allowed_chars = string.ascii_letters
    return ''.join(random.choice(allowed_chars) for x in range(str_size))

FETCH_IN = 0
FETCH_OUT = 1

def printEvent(eventId, instruction, cycle):
    if eventId == FETCH_IN:
        print(
            "FETCH_IN:",
            instruction["instruction_id"],
            "at cycle",
            cycle
        )

    elif eventId == FETCH_OUT:
        print(
            "FETCH_OUT:",
            instruction["instruction_id"],
            "at cycle",
            cycle
        )


# The definition of events contains the name of each event type and the names and types of each field. 
def event_definition():
    print("%%EventDef PajeDefineContainerType 0")
    print("%% Alias string")
    print("%% Type string")
    print("%% Name string")
    print("%%EndEventDef")

    # date: for fields that represent dates. It’s a double precision floating-point number, usually meaning
    # seconds since program start

    # int: for fields containing integer numeric values;

    # double: for fields containing floating-point values;

    # hex: for fields that represent addresses, in hexadecimal;

    # string: for strings of characters.

    # color: for fields that represent colors. A color is a sequence of three floating-point numbers be-
    # tween 0 and 1, inside double quotes ("). The three numbers are the values of red, green and
    # blue components.


    print("%%EventDef %s %d" % ("FetchIn", 0))
    print("%% cycle int")
    print("%%EndEventDef")

    print("%%EventDef %s %d" % ("FetchOut", 1)
    print("%% cycle int")
    print("%%EndEventDef")


def type_hierarchy():
    # Use paje events to define type hierarchy


def recorded_events():
    # The second part of the trace file contains one event per line, whose fields are separated by spaces
    # or tabs, the first field being the number that identifies the event type, followed by the other fields,
    # in the same order that they appear in the definition of the event. Fields of type string must be inside
    # double quotes (") if they contain space or tab characters, or if they are empty.
    # For example, the two events of figure 1 are shown below:

    # 21 3.233222 5 3 320
    # 17 5.123002 5 98 sync.c


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generates a sintetic PAJE trace file.')
    parser.add_argument('-n', '--number', help='Number of instructions to be processed.', required=True, type=int)
    parser.add_argument('-v', '--verbose', help='Level of verbose.', type=int, default=0)

    args = parser.parse_args()

    current_cycle = 0
    fetch_buffer = []
    instruction_id = ordered_string_generator()
    instructions_to_fetch = args.number
    instruction_template = {
        "instruction_id": None,
        "in_cycle": None,
        "out_cycle": None,
    }
    MIN_INST_LATENCY = 1
    MAX_INST_LATENCY = 30

    while instructions_to_fetch > 0 or len(fetch_buffer) > 0:
        if args.verbose > 0:
            print("---------- cycle:", current_cycle, "----------")
        
        if instructions_to_fetch > 0:
            fetched_instruction = instruction_template.copy()
            fetched_instruction.update({
                "instruction_id": next(instruction_id),
                "in_cycle": current_cycle,
                "out_cycle": current_cycle + random.randint(MIN_INST_LATENCY, MAX_INST_LATENCY),
            })

            printEvent(FETCH_IN, fetched_instruction, current_cycle)
            fetch_buffer.append(fetched_instruction)
            instructions_to_fetch = instructions_to_fetch - 1

        insts_to_pop = []
        for indx, instruction in enumerate(fetch_buffer):
            if current_cycle == instruction["out_cycle"]:
                printEvent(FETCH_OUT, instruction, current_cycle)
                insts_to_pop.append(indx)

        fetch_buffer = [instruction for indx, instruction in enumerate(fetch_buffer) if indx not in insts_to_pop]
        
        current_cycle = current_cycle + 1
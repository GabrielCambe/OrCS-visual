#!/usr/bin/python3
import argparse
import random
import string

import random

def random_string_generator(str_size=1):
    # allowed_chars = string.ascii_letters + string.punctuation
    allowed_chars = string.ascii_letters
    return ''.join(random.choice(allowed_chars) for x in range(str_size))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generates a sintetic PAJE trace file.')
    parser.add_argument('-n', '--number', help='Number of instructions to be processed.', required=True, type=int)
    parser.add_argument('-v', '--verbose', help='Level of verbose.', type=int, default=0)

    args = parser.parse_args()

    current_cycle = 0
    fetch_buffer = []
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
                "instruction_id": random_string_generator(str_size=12),
                "in_cycle": current_cycle,
                "out_cycle": current_cycle + random.randint(MIN_INST_LATENCY, MAX_INST_LATENCY),
            })
            print(
                "IN:",
                fetched_instruction["instruction_id"],
                "at cycle",
                current_cycle
            )
            fetch_buffer.append(fetched_instruction)
            instructions_to_fetch = instructions_to_fetch - 1

        insts_to_pop = []
        for indx, instruction in enumerate(fetch_buffer):
            if current_cycle == instruction["out_cycle"]:
                print(
                    "OUT:",
                    instruction["instruction_id"],
                    "at cycle",
                    current_cycle
                )
                insts_to_pop.append(indx)

        fetch_buffer = [instruction for indx, instruction in enumerate(fetch_buffer) if indx not in insts_to_pop]
        
        current_cycle = current_cycle + 1
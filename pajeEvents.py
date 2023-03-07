#!/usr/bin/python3
import argparse
import random
import string






# create trace generator

# create trace reader 







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

def id_generator(n=0):
    yield n
    number = n + 1
    yield from id_generator(number)

eventIdGenerator = id_generator()

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


# class PageEvent():
def printField(field_name, field_type):
    print("%% %s %s" % (field_name, field_type))


def printEvent(name, *fields, **kwargs):
    id = kwargs.get('id', next(eventIdGenerator))

    print("%%EventDef %s %d" % (name, id))

    for field_name, field_type in fields:
        printField(field_name, field_type)
    
    print("%EndEventDef")


def default_paje_events():
    # Defining PajeDefineContainerType to Define the FetchBuffer Container
    printEvent(
        'PajeDefineContainerType',
        # ('Alias','string'),
        ('Name','string'),
        ('Type','string')
    )

    printEvent(
        'PajeCreateContainer',
        ('Time','date'), # Time of creation of container
        ('Name','string'), # Name of new container
        ('Type','string'), #  Container type of new container
        ('Container','string') #  Parent of new container
    )

    printEvent(
        'PajeDestroyContainer',
        ('Time','date'), # Time of destruction of container
        ('Name','string'), # Name of new container
        ('Type','string'), #  Type of container
    )

    # Defining PajeDefineEventType to define the FetchIn and FetchOut events
    printEvent(
        'PajeDefineEventType',
        ('Type','string'),
        ('Name','string')
    )

    printEvent(
        'PajeNewEvent',
        ('Time','date'), # Time the event happened
        ('Type','string'), # Type of event
        ('Container','string'), # Container that produced event
        ('Value','string') # Value of new event
    )

# The definition of events contains the name of each event type and the names and types of each field. 
def event_definition(args):
    default_paje_events()

    printEvent(
        'FetchIn',
        ('Instruction','string'),
        ('Cycle', 'int')
    )

    printEvent(
        'FetchOut',     
        ('Instruction','string'),
        ('Cycle', 'int')
    )

def type_hierarchy(args):
    # Use paje events to define type hierarchy


# ---------------------------------------
# ---------- Defining Entities ----------
# ---------------------------------------
0 ROOT 0 "ROOT"
0 NODE ROOT "NODE"
0 VM NODE "VM"
1 MEM VM "Memory" "0 0 0"
1 CPU VM "CPU" "0 0 0"
4 LINK 0 VM VM "LINK


    pass


def recorded_events():
    # The second part of the trace file contains one event per line, whose fields are separated by spaces
    # or tabs, the first field being the number that identifies the event type, followed by the other fields,
    # in the same order that they appear in the definition of the event. Fields of type string must be inside
    # double quotes (") if they contain space or tab characters, or if they are empty.
    # For example, the two events of figure 1 are shown below:

    # 21 3.233222 5 3 320
    # 17 5.123002 5 98 sync.c
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generates a sintetic PAJE trace file.')
    parser.add_argument('-n', '--number', help='Number of instructions to be processed.', required=True, type=int)
    parser.add_argument('-v', '--verbose', help='Level of verbose.', type=int, default=0)

    args = parser.parse_args()

    event_definition(args)
    # type_hierarchy(args)
    # recorded_events(args)

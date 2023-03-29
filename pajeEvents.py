#!/usr/bin/python3
import argparse
import random
import string


# Instrução x entrou no fetch

# %EventDef FetchEnter 0
# %   Instruction string
# %   Timestamp date
# %EndEventDef

# Instrução x saiu do fetch depois de y milisegundos

# %EventDef FetchLeave 1
# %   Instruction string
# %   Timestamp date
# %EndEventDef

# Container Fetch Buffer





#TODO: create trace generator
    #TODO: Create Page Event Class
    #TODO: Create way to print event trace
    #TODO: Define type hierarchy
    #TODO: Define variable types
    #TODO: Define which sequence of events would represente a instruction entering and leaving the fetch buffer (create and destroy "instruction" container types?)

#TODO: create trace reader 




def ordered_string_generator(n=0):
    yield "inst_%d" % n
    number = n + 1
    yield from ordered_string_generator(number)

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


def printField(field_name, field_type):
    print("%% %s %s" % (field_name, field_type))


class PajeEvent():
    def __init__(self, name, *fields, **kwargs):
        self.id = kwargs.get('id', next(eventIdGenerator))
        self.name = name
        self.fields = dict(fields)


    # The definition of events contains the name of each event type and the names and types of each field. 
    def definition(self):
        print("%%EventDef %s %d" % (self.name, self.id))

        for field_name, field_type in self.fields.items():
            printField(field_name, field_type)
        
        print("%EndEventDef")


    def recordEvent(self, **kwargs):
        kwargsKeys = [key for key in kwargs]
        fieldKeys = [key for key in self.fields]
        if len(kwargsKeys) == len(fieldKeys):
            print("%d" % self.id, end='')    
            for kwargKey, fieldKey in zip(kwargsKeys, fieldKeys):
                if kwargKey == fieldKey:
                    print(" ", end='')    
                    if self.fields.get(fieldKey, None) == "string":
                        format = "\"%s\""
                    else:
                        format = "%s"
                    print(format % kwargs.get(kwargKey, None), end='')
            print()


# Defining PajeDefineContainerType to Define the FetchBuffer Container
PajeDefineContainerType = PajeEvent(
    'PajeDefineContainerType',
    ('Name','string'), # Name of new container type
    ('Type','string') # Parent container type
)

PajeCreateContainer = PajeEvent(
    'PajeCreateContainer',
    ('Time','date'), # Time of creation of container
    ('Name','string'), # Name of new container
    ('Type','string'), #  Container type of new container
    ('Container','string') #  Parent of new container
)

PajeDestroyContainer = PajeEvent(
    'PajeDestroyContainer',
    ('Time','date'), # Time of destruction of container
    ('Name','string'), # Name of new container
    ('Type','string'), #  Type of container
)

# Defining PajeDefineEventType to define the FetchIn and FetchOut events
PajeDefineEventType = PajeEvent(
    'PajeDefineEventType',
    ('Name','string'),
    ('Type','string')
)

PajeNewEvent = PajeEvent(
    'PajeNewEvent',
    ('Time','date'), # Time the event happened
    ('Type','string'), # Type of event
    ('Container','string'), # Container that produced event
    ('Value','string') # Value of new event
)

def print_default_paje_events_definitions():
    PajeDefineContainerType.definition()
    PajeCreateContainer.definition()
    # PajeDestroyContainer.definition()
    PajeDefineEventType.definition()
    # PajeNewEvent.definition()

FetchIn = PajeEvent(
    'FetchIn',
    ('Instruction','string'),
    ('Cycle', 'int')
)

FetchOut = PajeEvent(
    'FetchOut',     
    ('Instruction','string'),
    ('Cycle', 'int')
)
def print_event_definitions(args):
    print_default_paje_events_definitions()
    
    FetchIn.definition()
    FetchOut.definition()

# Use paje events to define type hierarchy
def print_type_hierarchy(args):

    PajeDefineContainerType.recordEvent(
        Name="SCREEN",
        Type="0"
    )

    PajeDefineContainerType.recordEvent(
        Name="FETCH_BUFFER",
        Type="SCREEN"
    )

    PajeDefineEventType.recordEvent(
        Name="FetchIn",
        Type="FETCH_BUFFER"
    )

    PajeDefineEventType.recordEvent(
        Name="FetchOut",
        Type="FETCH_BUFFER"
    )



def print_recorded_events(args):
    PajeCreateContainer.recordEvent(
        Time="0.0", # Time of creation of container
        Name="Simulador",  # Name of new container
        Type="SCREEN", #  Container type of new instruction["instruction_id"],container
        Container="0"  #  Parent of new container
    )

    PajeCreateContainer.recordEvent(
        Time="0.0", # Time of creation of container
        Name="Fetch_Buffer",  # Name of new container
        Type="FETCH_BUFFER", #  Container type of new container
        Container="Simulador"  #  Parent of new container
    )


#####################   
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

            # printEvent(FETCH_IN, fetched_instruction, current_cycle)
            FetchIn.recordEvent(
                Instruction=fetched_instruction.get("instruction_id", "UNKNOWN"),
                Cycle=current_cycle             
            )

            fetch_buffer.append(fetched_instruction)
            instructions_to_fetch = instructions_to_fetch - 1

        insts_to_pop = []
        for indx, instruction in enumerate(fetch_buffer):
            if current_cycle == instruction["out_cycle"]:
                # printEvent(FETCH_OUT, instruction, current_cycle)
                FetchOut.recordEvent(
                    Instruction=instruction.get("instruction_id", "UNKNOWN"),
                    Cycle=current_cycle             
                )
                insts_to_pop.append(indx)

        fetch_buffer = [instruction for indx, instruction in enumerate(fetch_buffer) if indx not in insts_to_pop]
        
        current_cycle = current_cycle + 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generates a sintetic PAJE trace file.')
    parser.add_argument('-n', '--number', help='Number of instructions to be processed.', required=True, type=int)
    parser.add_argument('-v', '--verbose', help='Level of verbose.', type=int, default=0)

    args = parser.parse_args()

    print_event_definitions(args)
    print_type_hierarchy(args)
    print_recorded_events(args)
    ('Instruction','string'),
    ('Cycle', 'int')

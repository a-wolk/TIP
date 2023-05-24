from parser.KatharaParser import KatharaParser

if __name__ == "__main__":
    machines = KatharaParser.parse("scenarios/kathara-lab_static-routing")
    for machine in machines:
        print(machine)
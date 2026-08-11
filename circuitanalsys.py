import numpy as np

class CircuitSolver:
    def __init__(self):
        self.resistors = []      
        self.current_sources = []  
        self.voltage_sources = []  

    def add_resistor(self, n1, n2, value):
        """Adds a resistor between node1 and node2 (Ohms)."""
        self.resistors.append((int(n1), int(n2), float(value)))

    def add_current_source(self, n_from, n_to, value):
        """Adds a current source flowing from n_from to n_to (Amperes)."""
        self.current_sources.append((int(n_from), int(n_to), float(value)))

    def add_voltage_source(self, pos, neg, value):
        """Adds a voltage source with (+) at pos and (-) at neg (Volts)."""
        self.voltage_sources.append((int(pos), int(neg), float(value)))

    def parse_netlist_line(self, line):
        """Parses a single line of netlist input."""
        parts = line.strip().split()
        if not parts or parts[0].startswith("#"):
            return  

        elem_type = parts[0][0].upper()
        
        if elem_type == 'R':
           
            _, n1, n2, val = parts[:4]
            self.add_resistor(n1, n2, val)
        elif elem_type == 'V':
           
            _, pos, neg, val = parts[:4]
            self.add_voltage_source(pos, neg, val)
        elif elem_type == 'I':
          
            _, n_from, n_to, val = parts[:4]
            self.add_current_source(n_from, n_to, val)
        else:
            print(f"Unknown element type skipped: {parts[0]}")

    def solve(self):
        """Solves node voltages and independent voltage source currents using MNA."""
        nodes = set()
        for n1, n2, _ in self.resistors:
            nodes.update([n1, n2])
        for n1, n2, _ in self.current_sources:
            nodes.update([n1, n2])
        for n1, n2, _ in self.voltage_sources:
            nodes.update([n1, n2])
        
        nodes.discard(0)  
        sorted_nodes = sorted(list(nodes))
        
        node_map = {node: i for i, node in enumerate(sorted_nodes)}
        N = len(sorted_nodes)
        M = len(self.voltage_sources)
       
        A = np.zeros((N + M, N + M))
        z = np.zeros(N + M)

        
        for n1, n2, R in self.resistors:
            g = 1.0 / R
            if n1 != 0:
                i = node_map[n1]
                A[i, i] += g
            if n2 != 0:
                j = node_map[n2]
                A[j, j] += g
            if n1 != 0 and n2 != 0:
                A[i, j] -= g
                A[j, i] -= g

        
        for n_from, n_to, I in self.current_sources:
            if n_from != 0:
                i = node_map[n_from]
                z[i] -= I 
            if n_to != 0:
                j = node_map[n_to]
                z[j] += I  

       
        for k, (pos, neg, V) in enumerate(self.voltage_sources):
            v_idx = N + k
            if pos != 0:
                i = node_map[pos]
                A[i, v_idx] += 1
                A[v_idx, i] += 1
            if neg != 0:
                j = node_map[neg]
                A[j, v_idx] -= 1
                A[v_idx, j] -= 1
            z[v_idx] = V

        try:
            x = np.linalg.solve(A, z)
        except np.linalg.LinAlgError:
            return None, None

        voltages = {0: 0.0}
        for node, idx in node_map.items():
            voltages[node] = x[idx]

        source_currents = {}
        for k, (pos, neg, V) in enumerate(self.voltage_sources):
            source_currents[f"V_source (Node {pos} -> Node {neg})"] = x[N + k]

        return voltages, source_currents

    def calculate_thevenin_norton(self, node_a, node_b):
        """
        Calculates Thévenin and Norton equivalents (Vth, Rth, In, Rn)
        between node_a and node_b.
        """
        # Step 1: Open-circuit voltage (Vth = Va - Vb)
        voltages, _ = self.solve()
        if voltages is None:
            return None
            
        v_a = voltages.get(node_a, 0.0)
        v_b = voltages.get(node_b, 0.0)
        v_th = v_a - v_b

        # Step 2: Equivalent resistance (Rth) via test current source on dead circuit
        dead_circuit = CircuitSolver()
        dead_circuit.resistors = self.resistors.copy()
        
        # Deactivate voltage sources (replace with short circuits / 0V)
        for pos, neg, _ in self.voltage_sources:
            dead_circuit.add_voltage_source(pos, neg, 0.0)
            
        
        
        # Inject 1A test current from node_b to node_a
        dead_circuit.add_current_source(n_from=node_b, n_to=node_a, value=1.0)

        test_voltages, _ = dead_circuit.solve()
        if test_voltages is None:
            return None

        v_a_test = test_voltages.get(node_a, 0.0)
        v_b_test = test_voltages.get(node_b, 0.0)
        r_th = v_a_test - v_b_test  # Rth = V_test / 1A
        
        # Step 3: Norton Current
        i_n = v_th / r_th if abs(r_th) > 1e-12 else float('inf')

        return {"V_th": v_th, "R_th": r_th, "I_n": i_n, "R_n": r_th}



def run_interactive():
    circuit = CircuitSolver()
    
    print("=" * 55)
    print(" CIRCUIT SOLVER INTERFACE")
    print(" Input Format Examples:")
    print("   R1 1 2 4     -> 4 Ohm resistor between nodes 1 & 2")
    print("   V1 1 0 12    -> 12V source with (+) at 1, (-) at GND (0)")
    print("   I1 0 3 3     -> 3A current source flowing from 0 to 3")
    print(" (Press Enter on an empty line to finish entering circuit)")
    print("=" * 55)

    while True:
        line = input("Enter Component: ").strip()
        if not line:
            break
        circuit.parse_netlist_line(line)

    
    voltages, currents = circuit.solve()
    if voltages is None:
        print("\nError: Could not solve circuit. Check connections or short circuits.")
        return

    print("\n" + "=" * 35)
    print("--- NODE VOLTAGES ---")
    for node, v in sorted(voltages.items()):
        print(f"V_{node}: {v:.2f} V")

    if currents:
        print("\n--- VOLTAGE SOURCE CURRENTS ---")
        for src, i in currents.items():
            print(f"{src}: {i:.2f} A")


   
    ans = input("\nCalculate Thévenin / Norton equivalent? (y/n): ").strip().lower()
    if ans == 'y':
        node_a = int(input("Node A (e.g., 2): "))
        node_b = int(input("Node B (e.g., 0 for GND): "))
        
        eq = circuit.calculate_thevenin_norton(node_a, node_b)
        if eq:
            print("\n" + "=" * 35)
            print(f"--- EQUIVALENT BETWEEN NODE {node_a} & NODE {node_b} ---")
            print(f"Thévenin Voltage    (V_th) : {eq['V_th']:.2f} V")
            print(f"Thévenin Resistance (R_th) : {eq['R_th']:.2f} Ω")
            print(f"Norton Current      (I_n)  : {eq['I_n']:.2f} A")
            print(f"Norton Resistance   (R_n)  : {eq['R_n']:.2f} Ω")

if __name__ == "__main__":
    run_interactive()

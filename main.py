import sys

class CacheLine:
    def __init__(self):
        self.valid = 0
        self.tag = None

def hex_to_tag(addr, line_size):
    return (addr // line_size) & 0xFFFFFFFF

def main():
    # Parse command-line arguments
    cache_size = int(sys.argv[1])
    line_size = int(sys.argv[2])
    group_size = int(sys.argv[3])
    access_file = sys.argv[4]

    num_lines = cache_size // line_size
    num_sets = num_lines // group_size

    # Initialize cache as a list of sets, each set containing cache lines
    cache = [[CacheLine() for _ in range(group_size)] for _ in range(num_sets)]

    fifo_counters = [0] * num_sets  # For tracking FIFO replacement
    hits, misses = 0, 0

    with open(access_file, 'r') as f:
        for line in f:
            # Skip empty lines
            line = line.strip()
            if not line:
                continue

            address = int(line, 16)
            tag = hex_to_tag(address, line_size)
            set_index = (address // line_size) % num_sets

            # Check if the tag is already in the set (hit or miss)
            hit = False
            for cache_line in cache[set_index]:
                if cache_line.valid and cache_line.tag == tag:
                    hits += 1
                    hit = True
                    break

            if not hit:
                misses += 1
                # Replace line according to FIFO policy
                fifo_index = fifo_counters[set_index]
                cache[set_index][fifo_index].valid = 1
                cache[set_index][fifo_index].tag = tag
                fifo_counters[set_index] = (fifo_index + 1) % group_size

            # Output cache state after each access
            print("================")
            for i, cache_line in enumerate(cache[set_index]):
                print(f"{i:03d} {cache_line.valid} ** {cache_line.tag:08X}" if cache_line.valid else f"{i:03d} 0")
        
    # Print hits and misses
    print(f"#hits: {hits}")
    print(f"#miss: {misses}")

if __name__ == "__main__":
    main()

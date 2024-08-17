import sys

class CacheLine:
    def __init__(self):
        self.valid = 0
        self.tag = None

def hex_to_tag_and_index(addr, line_size, num_lines):
    # Cálculo do tag removendo o offset e obtendo o índice da linha diretamente
    line_index = (addr // line_size) % num_lines
    tag = addr // line_size
    return line_index, tag

def main():
    # Parse command-line arguments
    cache_size = int(sys.argv[1])
    line_size = int(sys.argv[2])
    group_size = int(sys.argv[3])
    access_file = sys.argv[4]
    output_file = "output.txt"

    num_lines = cache_size // line_size  # Número total de linhas na cache

    # Inicializa a cache como uma lista de linhas
    cache = [CacheLine() for _ in range(num_lines)]

    fifo_counters = [0] * (num_lines // group_size)  # Para rastrear a substituição FIFO por conjunto
    hits, misses = 0, 0

    with open(access_file, 'r') as f, open(output_file, 'w') as out:
        for line in f:
            # Ignora linhas vazias
            line = line.strip()
            if not line:
                continue

            address = int(line, 16)
            line_index, tag = hex_to_tag_and_index(address, line_size, num_lines)

            # Identifica o conjunto ao qual essa linha pertence
            set_index = line_index // group_size
            
            hit = False
            # Verifica se o tag já está na linha (hit ou miss)
            if cache[line_index].valid and cache[line_index].tag == tag:
                hits += 1
                hit = True
            elif not hit:
                misses += 1
                if group_size > 1:
                    # Substituição FIFO dentro do conjunto
                    fifo_index = fifo_counters[set_index]
                    cache_line_to_replace = (set_index * group_size) + fifo_index
                    cache[cache_line_to_replace].valid = 1
                    cache[cache_line_to_replace].tag = tag
                    fifo_counters[set_index] = (fifo_index + 1) % group_size
                else:
                    # Substituição FIFO global
                    cache_line_to_replace = fifo_counters.index(min(fifo_counters))
                    cache[cache_line_to_replace].valid = 1
                    cache[cache_line_to_replace].tag = tag
                    fifo_counters[cache_line_to_replace] += 1
                    
                            
            # Saída do estado do cache após cada acesso
            out.write("================\n")
            out.write("IDX V ** ADDR **\n")
            for i, cache_line in enumerate(cache):
                if cache_line.valid:
                    out.write(f"{i:03d} {cache_line.valid} 0x{cache_line.tag:08X}\n")
                else:
                    out.write(f"{i:03d} 0\n")
        
    # Escreve hits e misses no arquivo
    with open(output_file, 'a') as out:
        out.write(f"#hits: {hits}\n")
        out.write(f"#miss: {misses}\n")

if __name__ == "__main__":
    main()

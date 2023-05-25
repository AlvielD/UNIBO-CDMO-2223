import os



def data_to_dzn():

    in_file_path = 'C:/Users/david/UNI/Combinatorial/Progetto/CDMO-Project/data'     # Data folder on the repository
    out_file_path = 'C:/Users\david/UNI/Combinatorial/Progetto/CDMO-Project/CP/data'       # Data folder on the CP folder

    n_instances = len(os.listdir(in_file_path))

    for i in range(1, n_instances):
        index = i if i>9 else f'0{i}'
        with open(f'{in_file_path}/inst{index}.dat', 'r') as f:
            lines = [e.split('\n')[0] for e in f.readlines()]
            m = int(lines[0])
            n = int(lines[1])
            l = [int(e) for e in lines[2].split(' ')[0]]
            s = [int(e) for e in lines[3].split(' ')[0]]
            D = []
            for line in lines[4:]:
                D.append([int(p) for p in line.split(' ')[0]])
            
            
        with open(f'{out_file_path}/inst{index}.dzn', 'w') as f:
            f.write(f'm = {m};\n')
            f.write(f'n = {n};\n')
            f.write(f'l = {l};\n')
            f.write(f's = {s};\n')

            f.write('D = [')
            for row in D:
                f.write(f'|')
                for e in row[:-1]:
                    f.write(f'{e},')
                f.write(f'{row[-1]}')
            f.write(f'|]')


if __name__ == '__main__':
    data_to_dzn()

import os

def data_to_dzn():

    in_file_path = '../../data'     # Data folder on the repository
    out_file_path = '../data'       # Data folder on the CP folder

    n_instances = len(os.listdir(in_file_path))

    for i in range(1, n_instances+1):
        with open(f'{in_file_path}/instance_{i}.txt', 'r') as f:
            lines = f.read().splitlines()

            m = lines[0]
            n = lines[1]
            
            l = [int(e) for e in lines[2].split(' ')]
            s = [int(e) for e in lines[3].split(' ')]

            D = []
            for line in lines[4:]:
                D.append([int(e) for e in line.split(' ')])
            
        with open(f'{out_file_path}/instance_{i}.dzn', 'w') as f:
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
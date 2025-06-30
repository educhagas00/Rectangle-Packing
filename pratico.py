import matplotlib.pyplot as plt
from matplotlib import animation
import random
import json

def visualize_packing_gif(rects, bin_width, bin_height, filename="packing.gif"):
    fig, ax = plt.subplots()
    ax.set_xlim(0, bin_width)
    ax.set_ylim(0, bin_height)
    ax.set_aspect('equal')
    plt.gca().invert_yaxis()
    plt.axis('off')

    # Gerar uma cor fixa por retângulo
    colors = {
        rect.id: (random.random(), random.random(), random.random())
        for rect in rects if rect.was_packed
    }

    def init():
        ax.clear()
        ax.set_xlim(0, bin_width)
        ax.set_ylim(0, bin_height)
        ax.set_aspect('equal')
        plt.gca().invert_yaxis()
        plt.axis('off')
        return []

    def update(frame):
        ax.clear()
        ax.set_xlim(0, bin_width)
        ax.set_ylim(0, bin_height)
        ax.set_aspect('equal')
        plt.gca().invert_yaxis()
        plt.axis('off')

        ax.set_xticks(range(0, bin_width + 1, bin_width * bin_height))
        ax.set_yticks(range(0, bin_height + 1, bin_width * bin_height))
        ax.grid(True, which='both', color='lightgray', linewidth=0.5)


        for i in range(frame + 1):
            rect = rects[i]
            if rect.was_packed:
                color = colors[rect.id]
                r = plt.Rectangle((rect.x, rect.y), rect.w, rect.h,
                                  facecolor=color, edgecolor='black', linewidth=1)
                ax.add_patch(r)
                ax.text(rect.x + rect.w / 2, rect.y + rect.h / 2, str(rect.id),
                        ha='center', va='center', fontsize=8, color='black')
        return []

    num_frames = sum(1 for r in rects if r.was_packed)
    ani = animation.FuncAnimation(fig, update, init_func=init,
                                  frames=num_frames, interval=500, blit=False)

    ani.save(filename, writer='pillow')
    print(f"GIF salvo como {filename}")



class Rect:
    def __init__(self, w, h, id_=0):
        self.id = id_
        self.w = w
        self.h = h
        self.was_packed = False

def read_instance_file(filename):
    """
    Lê um arquivo de instância no formato especificado.
    Assume que o arquivo sempre existe e é válido.
    """
    print(f"Lendo a instância do arquivo: {filename}...")
    with open(filename, 'r') as f:
        lines = f.readlines()

        # Linha 1: Número de itens
        num_items = int(lines[0].strip())

        # Linha 2: Dimensões do Bin
        bin_width, bin_height = map(int, lines[1].strip().split())

        rects = []
        # Próximas 'num_items' linhas: dados dos retângulos
        for i in range(num_items):
            # Lê os dados da linha e ignora os 3 últimos valores
            line_data = lines[i + 2].strip().split()
            rect_id = int(line_data[0])
            rect_w = int(line_data[1])
            rect_h = int(line_data[2])
            
            rects.append(Rect(w=rect_w, h=rect_h, id_=rect_id))
    
    print("Leitura concluída.")
    return rects, bin_width, bin_height        

def pack_rects_naive_rows(rects, bin_width, bin_height):
    rects.sort(key=lambda r: r.h, reverse=True)
    x_pos = 0
    y_pos = 0
    largest_h_this_row = 0

    for rect in rects:
        if (x_pos + rect.w) > bin_width:
            y_pos += largest_h_this_row
            x_pos = 0
            largest_h_this_row = 0

        if (y_pos + rect.h) > bin_height:
            break

        rect.x = x_pos
        rect.y = y_pos
        x_pos += rect.w

        if rect.h > largest_h_this_row:
            largest_h_this_row = rect.h

        rect.was_packed = True


def main():

    instance_filename = "instancias/c1-p1.ins2D"

    rects, W, H = read_instance_file(instance_filename)

    pack_rects_naive_rows(rects, bin_width=W, bin_height=H)

    print("\nPacked rectangles:")
    for r in rects:
        if r.was_packed:
            print(f"Item {r.id}: placed at ({r.x}, {r.y}), size ({r.w}x{r.h})")
        else:
            print(f"Item {r.id}: not packed")

    output_data = {
        'rectangles': [],
        'initial_bin_width': W,
        'initial_bin_height': H
    }
    
    for r in rects:
        rect_info = {
            'id': r.id,
            'w': r.w,
            'h': r.h,
            'was_packed': r.was_packed,
        }
        if r.was_packed:
            rect_info['x'] = r.x
            rect_info['y'] = r.y
        output_data['rectangles'].append(rect_info)

    with open('resultado_inicial.json', 'w') as f:
        json.dump(output_data, f, indent=4)
        
    print("\nSolução inicial salva em 'resultado_inicial.json'")


    

    total_area = W * H
    area_used = sum(r.w * r.h for r in rects if r.was_packed)
    area_wasted = total_area - area_used

     
    print(f"area total: {total_area}")
    print(f"area usada: {area_used}")
    print(f"area desperdiçada: {area_wasted}")
            

    visualize_packing_gif(rects, bin_width=W, bin_height=H, filename="resultado.gif")

if __name__ == "__main__":
    main()


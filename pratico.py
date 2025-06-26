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

    W, H = 50, 50  # dimensões 

    rects = [
        Rect(2, 12, id_=1),
        Rect(7, 12, id_=2),
        Rect(8, 6, id_=3),
        Rect(3, 6, id_=4),
        Rect(3, 5, id_=5),
        Rect(5, 5, id_=6),
        Rect(3, 12, id_=7),
        Rect(3, 7, id_=8),
        Rect(5, 7, id_=9),
        Rect(2, 6, id_=10),
        Rect(3, 2, id_=11),
        Rect(4, 2, id_=12),
        Rect(3, 4, id_=13),
        Rect(4, 4, id_=14),
        Rect(9, 2, id_=15),
        Rect(11, 2, id_=16),
    ]

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


import json
import random
import matplotlib.pyplot as plt
from matplotlib import animation
import time

def visualize_packing_image(rects, bin_width, bin_height, filename="packing.png"):

    fig, ax = plt.subplots(figsize=(8, 8)) # Ajuste o tamanho conforme necessário
    ax.set_xlim(0, bin_width)
    ax.set_ylim(0, bin_height)
    ax.set_aspect('equal')
    plt.gca().invert_yaxis()
    plt.axis('off')

    packed_rects = [r for r in rects if r.was_packed]
    if not packed_rects:
        print("Nenhum retângulo para visualizar.")
        return

    # Gera cores para cada retângulo
    colors = {
        rect.id: (random.random(), random.random(), random.random())
        for rect in packed_rects
    }

    # Desenha todos os retângulos na imagem
    for rect in packed_rects:
        color = colors[rect.id]
        r_patch = plt.Rectangle((rect.x, rect.y), rect.w, rect.h,
                              facecolor=color, edgecolor='black', linewidth=1)
        ax.add_patch(r_patch)
        ax.text(rect.x + rect.w / 2, rect.y + rect.h / 2, str(rect.id),
                ha='center', va='center', fontsize=8, color='white', weight='bold')

    # Salva a figura em um arquivo de imagem
    plt.savefig(filename, dpi=150, bbox_inches='tight', pad_inches=0.1)
    plt.close(fig) # Fecha a figura para liberar memória
    print(f"\nImagem do resultado final salva como {filename}")

# ==============================================================================
# 1. ESTRUTURAS DE DADOS E FUNÇÕES AUXILIARES
# ==============================================================================

class Rect:
    def __init__(self, w, h, id_):
        self.w = w
        self.h = h
        self.id = id_
        self.x = 0
        self.y = 0
        self.was_packed = False

class Solution:
    def __init__(self, sequence_pair):
        # A representação de uma solução é um par de permutações (sequence-pair).
        self.sequence_pair = sequence_pair
        self.area = float('inf')

def encode_to_sequence_pair(packed_rects):
    # Relações:
    # (A à esquerda de B) => A aparece antes de B em ambas as sequências.
    # (A acima de B) => A aparece antes de B em Γ+ e depois de B em Γ-.
    
    # Ordena os retângulos por suas coordenadas para estabelecer relações espaciais.
    rects = sorted(packed_rects, key=lambda r: (r.x + r.w/2, r.y + r.h/2))
    
    gamma_plus = []
    gamma_minus = []
    
    ids = [r.id for r in rects]
    
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            r_i = next(r for r in rects if r.id == ids[i])
            r_j = next(r for r in rects if r.id == ids[j])

            # Relação Esquerda/Direita
            if r_i.x + r_i.w <= r_j.x: # i está a esquerda de j
                if ids[i] not in gamma_plus: gamma_plus.append(ids[i])
                if ids[j] not in gamma_plus: gamma_plus.append(ids[j])
                if ids[i] not in gamma_minus: gamma_minus.append(ids[i])
                if ids[j] not in gamma_minus: gamma_minus.append(ids[j])
            
            # Relação Acima/Abaixo
            if r_i.y + r_i.h <= r_j.y: # i está acima de j
                if ids[i] not in gamma_plus: gamma_plus.append(ids[i])
                if ids[j] not in gamma_plus: gamma_plus.append(ids[j])
                if ids[j] not in gamma_minus: gamma_minus.append(ids[j])
                if ids[i] not in gamma_minus: gamma_minus.append(ids[i])

    # Garante que todos os retângulos estão presentes nas listas
    all_ids = {r.id for r in packed_rects}
    for r_id in all_ids:
        if r_id not in gamma_plus: gamma_plus.append(r_id)
        if r_id not in gamma_minus: gamma_minus.append(r_id)
            
    return (tuple(gamma_plus), tuple(gamma_minus))


def decode_sequence_pair(sequence_pair, rect_map):

    # Converte um sequence-pair em um empacotamento com coordenadas e retorna a área.
    
    gp, gm = sequence_pair[0], sequence_pair[1]
    pos_gp = {val: i for i, val in enumerate(gp)}
    pos_gm = {val: i for i, val in enumerate(gm)}
    
    for r_id in rect_map:
        rect_map[r_id].x = 0
        rect_map[r_id].y = 0

    for i in range(len(gp)):
        r_i_id = gp[i]
        r_i = rect_map[r_i_id]
        for j in range(i + 1, len(gp)):
            r_j_id = gp[j]
            r_j = rect_map[r_j_id]

            # Se r_i está "à esquerda" de r_j
            if pos_gm[r_i_id] < pos_gm[r_j_id]:
                r_j.x = max(r_j.x, r_i.x + r_i.w)
            # Se r_i está "acima" de r_j
            else:
                r_j.y = max(r_j.y, r_i.y + r_i.h)
    
    # Calcula a área do bounding box 
    max_x = max(r.x + r.w for r in rect_map.values())
    max_y = max(r.y + r.h for r in rect_map.values())
    return max_x * max_y


# ==============================================================================
# 2. IMPLEMENTAÇÃO DA BUSCA TABU
# ==============================================================================

class TabuSearchOptimizer:
    def __init__(self, rectangles, params):
        self.rectangles = rectangles
        self.rect_map = {r.id: r for r in rectangles}
        self.params = params
        # A lista tabu armazena atributos dos últimos 'TL' movimentos.
        self.tabu_list = []

    def _evaluate(self, solution):
        # Avalia uma solução decodificando e calculando sua area.
        area = decode_sequence_pair(solution.sequence_pair, self.rect_map)
        solution.area = area
        return area

    def _generate_neighbor(self, sequence_pair):
    
        # gera uma solução vizinha através de uma das três operações de troca, selecionada aleatoriamente.
        
        gp, gm = list(sequence_pair[0]), list(sequence_pair[1])
        
        if len(gp) < 2: return None, None
        
        # Seleciona dois retângulos distintos aleatoriamente.
        idx1, idx2 = random.sample(range(len(gp)), 2)

        op_type = random.choice(['G+', 'G-', 'Both'])
        
        # Troca os índices para obter os IDs
        r1_id, r2_id = gp[idx1], gp[idx2]

        # O atributo do movimento contém os retângulos trocados e o tipo da operação.
        move_attribute = {'rects': {r1_id, r2_id}, 'type': op_type}

        if op_type == 'G+':
            gp[idx1], gp[idx2] = gp[idx2], gp[idx1]
        elif op_type == 'G-':
            # Precisa encontrar os índices em gm
            gm_idx1, gm_idx2 = gm.index(r1_id), gm.index(r2_id)
            gm[gm_idx1], gm[gm_idx2] = gm[gm_idx2], gm[gm_idx1]
        else: # 'Both'
            gp[idx1], gp[idx2] = gp[idx2], gp[idx1]
            gm_idx1, gm_idx2 = gm.index(r1_id), gm.index(r2_id)
            gm[gm_idx1], gm[gm_idx2] = gm[gm_idx2], gm[gm_idx1]

        return move_attribute, (tuple(gp), tuple(gm))

    def _is_tabu(self, move_attr): # PRECISA DE MELHORIAS
        
        # Implementa a restrição tabu ESTOCÁSTICA
        
        tl = self.params['TL']
        for i, past_move in enumerate(self.tabu_list):
            # Condição (i): o tipo de movimento é o mesmo.
            if move_attr['type'] == past_move['type']:
                # Condição (ii): um dos retângulos do novo movimento participou do movimento antigo.
                if not move_attr['rects'].isdisjoint(past_move['rects']):
                    # Se ambas as condições são verdadeiras, rejeita com probabilidade p(i).
                    # A fórmula é (TL-i+1)/TL para um i 1-indexado. Para i 0-indexado, é (TL-i)/TL.
                    prob_reject = (tl - i) / tl
                    if random.random() < prob_reject:
                        return True  # O movimento é tabu.
        return False  # O movimento não é tabu.

    def _update_tabu_list(self, move_attr):
        # Adiciona um movimento à lista tabu 
        self.tabu_list.insert(0, move_attr)
        if len(self.tabu_list) > self.params['TL']: # remove o mais antigo se o tamanho exceder TL.
            self.tabu_list.pop()

    def search(self, initial_solution):

        # x é a solução atual, xb é a melhor encontrada.
        x = initial_solution
        self._evaluate(x)
        
        xb = Solution(x.sequence_pair)
        xb.area = x.area
        
        num_evaluations = 1

        print(f"Iniciando Busca Tabu. Solução inicial, Área: {x.area:.2f}")

        # O critério de parada é o número máximo de avaliações.
        while num_evaluations < self.params['MAXEVAL']:
            best_neighbor_not_tabu = None
            
            # O loop interno tenta encontrar um movimento admissível.
            for _ in range(self.params['MAXNEI']):
                move_attr, neighbor_sp = self._generate_neighbor(x.sequence_pair)
                if neighbor_sp is None: continue
                
                xa = Solution(neighbor_sp)
                self._evaluate(xa) # Avalia o vizinho.
                num_evaluations += 1

                if num_evaluations % 10000 == 0:
                    print(f"  Avaliações: {num_evaluations}, Melhor Área: {xb.area:.2f}")

                # Critério de Aspiração: se o vizinho é melhor que o melhor global, aceita-o.
                if xa.area < xb.area:
                    xb = xa
                    x = xa
                    self._update_tabu_list(move_attr)
                    break
                
                if not self._is_tabu(move_attr):
                    # Estratégia "First Admissible Move": se o vizinho não-tabu é melhor que o atual, aceita-o.
                    if xa.area < x.area:
                        x = xa
                        self._update_tabu_list(move_attr)
                        break
                    
                    # Guarda o melhor vizinho não-tabu encontrado para o caso de nenhum movimento ser aceito.
                    if best_neighbor_not_tabu is None or xa.area < best_neighbor_not_tabu.area:
                        best_neighbor_not_tabu = xa
            
            # Se o loop terminou sem um 'break', e um vizinho não-tabu foi encontrado, move para ele. evita ciclos.
            else: 
                if best_neighbor_not_tabu:
                    x = best_neighbor_not_tabu

        print(f"Busca Tabu concluída. Avaliações totais: {num_evaluations}")
        return xb

# 3. FUNÇÃO PRINCIPAL E EXECUÇÃO

def main():
    # 1. Ler a soluçao inicial do arquivo gerado pelo 'pratico.py'
    try:
        with open('resultado_inicial.json', 'r') as f:
            initial_data = json.load(f)
    except FileNotFoundError:
        print("Erro: O arquivo 'resultado_inicial.json' não foi encontrado.")
        print("Por favor, execute o script 'pratico.py' primeiro para gerar a solução inicial.")
        return

    rects_from_file = []
    for r_data in initial_data['rectangles']:
        r = Rect(r_data['w'], r_data['h'], id_ = r_data['id'])
        if r_data.get('was_packed', False):
            r.was_packed = True
            r.x = r_data['x']
            r.y = r_data['y']
        rects_from_file.append(r)
        
    packed_rects = [r for r in rects_from_file if r.was_packed]
    
    # 2. Converte a configuracao inicial para a representaçao sequence-pair
    initial_solution = encode_to_sequence_pair(packed_rects)
    initial_solution = Solution(initial_solution)

    # 3. Configurar e executar a Busca Tabu
    ts_params = {
        'MAXEVAL': 100000, # número máximo de avaliações
        'MAXNEI': 200, # número máximo de vizinhos a serem gerados por iteração
        'TL': 5 # tamanho da lista tabu
    }
    
    optimizer = TabuSearchOptimizer(packed_rects, ts_params)
    
    start_time = time.time()
    best_solution_found = optimizer.search(initial_solution)
    end_time = time.time()
    
    print("\n========================================")
    print("      RESULTADO FINAL DA BUSCA TABU")
    print("========================================")
    print(f"Melhor Área encontrada: {best_solution_found.area:.2f}")
    print(f"Tempo de execução: {end_time - start_time:.2f} segundos")
    print(f"Melhor Sequence-Pair: {best_solution_found.sequence_pair}")
    print("========================================")


    final_rect_map = {r.id: r for r in packed_rects}
    decode_sequence_pair(best_solution_found.sequence_pair, final_rect_map)
    final_rects = list(final_rect_map.values())
    final_W = max((r.x + r.w for r in final_rects), default=0)
    final_H = max((r.y + r.h for r in final_rects), default=0)

    visualize_packing_image(final_rects, final_W, final_H, filename="resultado_tabu_final.png")

if __name__ == "__main__":
    main()
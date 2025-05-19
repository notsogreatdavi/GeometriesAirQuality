import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, RadioButtons, Slider
import pickle
import os

# Parâmetros da simulação
grid_size = (50, 50)
D = 0.1
dt = 1
steps = 2000
update_interval = 50  # ms entre frames

# Elementos do grid
AIR, WALL, SOURCE, OBSTACLE, PERSON, FILTER = 0, 1, 2, 3, 4, 5

# Cores dos elementos (R, G, B)
colors = {
    AIR: [1, 1, 1],
    WALL: [0, 0, 0],
    SOURCE: [1, 0, 0],
    OBSTACLE: [0, 0, 1],
    FILTER: [0, 1, 0.3],
    PERSON: [1, 0.5, 0]  # Cor base para pessoas
}

# Dicionário de elementos
elementos = {
    "Parede": WALL,
    "Fonte": SOURCE,
    "Obstáculo": OBSTACLE,
    "Pessoa": PERSON,
    "Filtro": FILTER
}
elemento_selecionado = AIR

# Inicialização do grid
grid = np.zeros(grid_size, dtype=int)
grid[grid_size[0]//2, grid_size[1]//2] = SOURCE
C = np.zeros(grid_size)
C[grid == SOURCE] = 100.0
health = np.zeros(grid_size)  # Saúde das pessoas

# Variáveis de controle
ani = None
paused = False
filter_efficiency = 0.5
move_people_enabled = True
last_title_update = 0

# Configuração da figura
fig, ax = plt.subplots(figsize=(10, 8))
plt.subplots_adjust(left=0.05, right=0.7, bottom=0.1)
im = ax.imshow(np.zeros((*grid_size, 3)), interpolation='nearest', vmin=0, vmax=1)
plt.title("Simulação de Poluição - Pronto")
plt.axis('off')

def laplacian(C, grid, i, j):
    total = 0
    count = 0
    for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
        ni, nj = i + di, j + dj
        if 0 <= ni < grid_size[0] and 0 <= nj < grid_size[1]:
            if grid[ni, nj] in [AIR, SOURCE, PERSON]:
                total += C[ni, nj]
                count += 1
    return total - count * C[i, j] if count > 0 else 0

def move_people(grid, C, health):
    people_pos = np.argwhere(grid == PERSON)
    impassable = [WALL, OBSTACLE, SOURCE, FILTER]
    
    for i, j in people_pos:
        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        np.random.shuffle(directions)
        
        for di, dj in directions:
            ni, nj = i + di, j + dj
            if (0 <= ni < grid_size[0] and 0 <= nj < grid_size[1] and 
                grid[ni, nj] not in impassable):
                
                grid[i, j] = AIR
                grid[ni, nj] = PERSON
                C[ni, nj] = C[i, j]
                health[ni, nj] = health[i, j]
                C[i, j] = 0
                health[i, j] = 0
                break

def update_display():
    global last_title_update
    
    # Cria imagem baseada no grid
    img = np.zeros((*grid_size, 3))
    for element, color in colors.items():
        img[grid == element] = color
    
    # Aplica efeito de saúde nas pessoas (vetorizado)
    person_mask = (grid == PERSON)
    if np.any(person_mask):
        health_norm = np.clip(health[person_mask] / 100, 0, 1)
        img[person_mask, 1] = 0.5 * (1 - health_norm)
        img[person_mask, 2] = 0.5 * (1 - health_norm)
    
    # Aplica camada de concentração de poluentes
    max_C = np.max(C) if np.max(C) > 0 else 1
    concentration_layer = np.clip(C / max_C, 0, 0.7)
    img *= (1 - concentration_layer[..., np.newaxis])
    
    # Atualiza a imagem
    im.set_array(img)
    
    # Atualiza o título apenas ocasionalmente para melhor performance
    current_step = getattr(ani, '_step', 0)
    if current_step - last_title_update > 10 or current_step == 0:
        avg_health = np.mean(health[person_mask]) if np.any(person_mask) else 0
        ax.set_title(f"Simulação - Passo {current_step}/{steps}\nSaúde média: {avg_health:.1f}")
        last_title_update = current_step
    
    fig.canvas.draw_idle()

def onclick(event):
    global elemento_selecionado
    if event.xdata is None or event.ydata is None:
        return

    ix, iy = int(event.xdata), int(event.ydata)
    if 0 <= ix < grid_size[1] and 0 <= iy < grid_size[0]:
        if event.button == 1:  # Botão esquerdo
            grid[iy, ix] = elemento_selecionado
            if elemento_selecionado == SOURCE:
                C[iy, ix] = 100.0
            elif elemento_selecionado == PERSON:
                C[iy, ix] = 10.0
                health[iy, ix] = 100.0
            else:
                C[iy, ix] = 0
        elif event.button == 3:  # Botão direito
            grid[iy, ix] = AIR
            C[iy, ix] = 0
            health[iy, ix] = 0
        update_display()

fig.canvas.mpl_connect('button_press_event', onclick)

# Painel de controle
rax = plt.axes([0.75, 0.6, 0.2, 0.3])
radio = RadioButtons(rax, list(elementos.keys()), active=0)

def mudar_elemento(label):
    global elemento_selecionado
    elemento_selecionado = elementos[label]

radio.on_clicked(mudar_elemento)

# Slider para eficiência do filtro
ax_slider = plt.axes([0.75, 0.5, 0.2, 0.03])
slider = Slider(ax_slider, 'Eficiência Filtro', 0, 1, valinit=0.5)

def update_efficiency(val):
    global filter_efficiency
    filter_efficiency = val

slider.on_changed(update_efficiency)

# Botão para ligar/desligar movimento de pessoas
ax_move_toggle = plt.axes([0.75, 0.45, 0.2, 0.04])
btn_move_toggle = Button(ax_move_toggle, 'Movimento: ON')

def toggle_move(event):
    global move_people_enabled
    move_people_enabled = not move_people_enabled
    btn_move_toggle.label.set_text(f'Movimento: {"ON" if move_people_enabled else "OFF"}')

btn_move_toggle.on_clicked(toggle_move)

def save_map():
    """Salva o mapa atual em um arquivo"""
    map_data = {
        'grid': grid,
        'C': C,
        'health': health,
        'filter_efficiency': filter_efficiency
    }
    
    # Cria a pasta 'saved_maps' se não existir
    if not os.path.exists('saved_maps'):
        os.makedirs('saved_maps')
    
    # Encontra um nome de arquivo disponível
    i = 1
    while True:
        filename = f'saved_maps/map_{i}.pkl'
        if not os.path.exists(filename):
            break
        i += 1
    
    with open(filename, 'wb') as f:
        pickle.dump(map_data, f)
    
    ax.set_title(f"Mapa salvo como {filename}")
    update_display()

def load_map():
    """Carrega um mapa salvo"""
    global grid, C, health, filter_efficiency
    
    # Lista os mapas salvos
    if not os.path.exists('saved_maps'):
        ax.set_title("Nenhum mapa salvo encontrado")
        return
    
    map_files = [f for f in os.listdir('saved_maps') if f.endswith('.pkl')]
    if not map_files:
        ax.set_title("Nenhum mapa salvo encontrado")
        return
    
    # Carrega o último mapa salvo (poderia implementar uma seleção)
    filename = os.path.join('saved_maps', map_files[-1])
    
    try:
        with open(filename, 'rb') as f:
            map_data = pickle.load(f)
        
        grid = map_data['grid']
        C = map_data['C']
        health = map_data.get('health', np.zeros(grid_size))
        filter_efficiency = map_data.get('filter_efficiency', 0.5)
        
        ax.set_title(f"Mapa carregado: {filename}")
        update_display()
    except Exception as e:
        ax.set_title(f"Erro ao carregar mapa: {str(e)}")

def run_simulation(event):
    global ani, paused, grid, C, health, last_title_update
    paused = False
    last_title_update = 0
    
    # Salva estado inicial
    current_C = C.copy()
    current_grid = grid.copy()
    current_health = health.copy()
    
    def simulate():
        nonlocal current_C, current_grid, current_health
        for step in range(steps):
            if paused:
                yield current_grid, current_C, current_health
                continue
                
            new_C = current_C.copy()
            new_grid = current_grid.copy()
            new_health = current_health.copy()
            
            # Mover pessoas
            if move_people_enabled and step % 5 == 0:
                move_people(new_grid, new_C, new_health)
            
            # Difusão (vetorizada onde possível)
            for i in range(grid_size[0]):
                for j in range(grid_size[1]):
                    if new_grid[i, j] in [AIR, SOURCE, PERSON]:
                        lap = laplacian(new_C, new_grid, i, j)
                        new_C[i, j] += D * lap * dt
                        
                        if new_grid[i, j] == PERSON:
                            new_health[i, j] = max(0, new_health[i, j] - new_C[i, j] * 0.01)
            
            # Fontes e pessoas emitem poluentes
            new_C[new_grid == SOURCE] += 100.0
            new_C[new_grid == PERSON] += 10.0
            
            # Filtros
            filter_mask = (new_grid == FILTER)
            if np.any(filter_mask):
                for i, j in zip(*np.where(filter_mask)):
                    for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < grid_size[0] and 0 <= nj < grid_size[1]:
                            if new_grid[ni, nj] == AIR:
                                reduction = filter_efficiency * new_C[ni, nj]
                                new_C[ni, nj] -= reduction
                                new_C[i, j] += reduction
            
            # Condições de contorno e clipping
            new_C[0, :] = new_C[1, :]
            new_C[-1, :] = new_C[-2, :]
            new_C[:, 0] = new_C[:, 1]
            new_C[:, -1] = new_C[:, -2]
            new_C = np.clip(new_C, 0, None)
            
            current_C, current_grid, current_health = new_C, new_grid, new_health
            yield current_grid, current_C, current_health

    def update(frame_data):
        grid_frame, C_frame, health_frame = frame_data
        img = np.zeros((*grid_size, 3))
        
        # Renderização vetorizada
        for element, color in colors.items():
            img[grid_frame == element] = color
        
        # Saúde das pessoas
        person_mask = (grid_frame == PERSON)
        if np.any(person_mask):
            health_norm = np.clip(health_frame[person_mask] / 100, 0, 1)
            img[person_mask, 1] = 0.5 * (1 - health_norm)
            img[person_mask, 2] = 0.5 * (1 - health_norm)
        
        # Poluentes
        max_C = np.max(C_frame) if np.max(C_frame) > 0 else 1
        concentration_layer = np.clip(C_frame / max_C, 0, 0.7)
        img *= (1 - concentration_layer[..., np.newaxis])
        
        im.set_array(img)
        
        # Atualiza título a cada 10 frames
        current_step = getattr(ani, '_step', 0)
        if current_step % 10 == 0:
            avg_health = np.mean(health_frame[person_mask]) if np.any(person_mask) else 0
            ax.set_title(f"Simulação - Passo {current_step}/{steps}\nSaúde média: {avg_health:.1f}")
        
        return im,

    # Cria a animação
    ani = FuncAnimation(fig, update, frames=simulate(), 
                       interval=update_interval, blit=True, cache_frame_data=False)

# Botão de simulação
ax_button = plt.axes([0.75, 0.35, 0.2, 0.06])
btn = Button(ax_button, 'Iniciar Simulação')
btn.on_clicked(run_simulation)

# Botão de pausa
def toggle_pause(event):
    global paused, ani
    paused = not paused
    if paused and ani is not None:
        ani.event_source.stop()
    elif ani is not None:
        ani.event_source.start()

ax_pause = plt.axes([0.75, 0.28, 0.2, 0.06])
btn_pause = Button(ax_pause, 'Pausar/Continuar')
btn_pause.on_clicked(toggle_pause)

# Botão de salvar mapa
ax_save = plt.axes([0.75, 0.21, 0.2, 0.06])
btn_save = Button(ax_save, 'Salvar Mapa')
btn_save.on_clicked(lambda x: save_map())

# Botão de carregar mapa
ax_load = plt.axes([0.75, 0.14, 0.2, 0.06])
btn_load = Button(ax_load, 'Carregar Mapa')
btn_load.on_clicked(lambda x: load_map())

# Botão de limpar grade
def limpar_grade(event):
    global grid, C, health, ani, paused
    if ani is not None:
        ani.event_source.stop()
    paused = False
    grid = np.zeros(grid_size, dtype=int)
    grid[grid_size[0]//2, grid_size[1]//2] = SOURCE
    C = np.zeros(grid_size)
    C[grid == SOURCE] = 100.0
    health = np.zeros(grid_size)
    ax.set_title("Simulação de Poluição - Grade Limpa")
    update_display()

ax_clear = plt.axes([0.75, 0.07, 0.2, 0.06])
btn_clear = Button(ax_clear, 'Limpar Grade')
btn_clear.on_clicked(limpar_grade)

update_display()
plt.show()

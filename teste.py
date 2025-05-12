import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.colors as mcolors
from matplotlib.widgets import Button, RadioButtons

# Parâmetros da simulação
grid_size = (50, 50)
D = 0.1
dt = 1
steps = 200

# Tipos de células
AIR, WALL, SOURCE, OBSTACLE, PERSON, FILTER = 0, 1, 2, 3, 4, 5

# Dicionário de elementos e controle selecionado
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

# Variável global para manter a animação
ani = None

def laplacian(C, grid, i, j):
    total = 0
    count = 0
    for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
        ni, nj = i + di, j + dj
        if 0 <= ni < grid_size[0] and 0 <= nj < grid_size[1]:
            if grid[ni, nj] in [AIR, SOURCE]:
                total += C[ni, nj]
                count += 1
    return total - count * C[i, j]

# Configuração da figura interativa
fig, ax = plt.subplots(figsize=(8, 8))
plt.subplots_adjust(left=0.05, right=0.7)  # espaço para painel lateral
im = ax.imshow(np.zeros((*grid_size, 3)), interpolation='nearest')
plt.title("Clique para adicionar elemento selecionado\nBotão direito: limpa célula")
plt.axis('off')

def update_display():
    img = np.zeros((*grid_size, 3))
    img[grid == AIR] = [1, 1, 1]
    img[grid == WALL] = [0, 0, 0]
    img[grid == SOURCE] = [1, 0, 0]
    img[grid == OBSTACLE] = [0, 0, 1]
    img[grid == PERSON] = [1, 0.5, 0]     # laranja
    img[grid == FILTER] = [0, 1, 0.3]     # verde

    max_C = np.max(C) if np.max(C) > 0 else 1
    concentration_layer = np.clip(C / max_C, 0, 0.7)
    img = img * (1 - concentration_layer[..., np.newaxis])

    im.set_array(img)
    fig.canvas.draw()

update_display()

def onclick(event):
    global elemento_selecionado

    if event.xdata is None or event.ydata is None:
        return

    ix, iy = int(event.xdata), int(event.ydata)
    if 0 <= ix < grid_size[1] and 0 <= iy < grid_size[0]:
        if event.button == 1:  # Esquerdo: coloca elemento
            grid[iy, ix] = elemento_selecionado
            C[iy, ix] = 100.0 if elemento_selecionado == SOURCE else 0
        elif event.button == 3:  # Direito: limpa
            grid[iy, ix] = AIR
            C[iy, ix] = 0
        update_display()

fig.canvas.mpl_connect('button_press_event', onclick)

# Painel de seleção de elemento
rax = plt.axes([0.75, 0.4, 0.2, 0.4])
radio = RadioButtons(rax, list(elementos.keys()), active=0)

def mudar_elemento(label):
    global elemento_selecionado
    elemento_selecionado = elementos[label]

radio.on_clicked(mudar_elemento)

def run_simulation(event):
    global ani
    # Salva estado inicial
    current_C = C.copy()
    current_grid = grid.copy()
    history = []

    for step in range(steps):
        new_C = current_C.copy()
        for i in range(grid_size[0]):
            for j in range(grid_size[1]):
                if current_grid[i, j] in [AIR, SOURCE]:
                    lap = laplacian(current_C, current_grid, i, j)
                    new_C[i, j] = current_C[i, j] + D * lap * dt

        new_C[0, :] = new_C[1, :]
        new_C[-1, :] = new_C[-2, :]
        new_C[:, 0] = new_C[:, 1]
        new_C[:, -1] = new_C[:, -2]

        current_C = new_C
        history.append((current_grid.copy(), current_C.copy()))

    def create_frame_image(grid_frame, C_frame):
        img = np.zeros((*grid_size, 3))
        img[grid_frame == AIR] = [1, 1, 1]
        img[grid_frame == WALL] = [0, 0, 0]
        img[grid_frame == SOURCE] = [1, 0, 0]
        img[grid_frame == OBSTACLE] = [0, 0, 1]
        img[grid_frame == PERSON] = [1, 0.5, 0]
        img[grid_frame == FILTER] = [0, 1, 0.3]

        max_C = np.max(C_frame) if np.max(C_frame) > 0 else 1
        concentration_layer = np.clip(C_frame / max_C, 0, 0.7)
        img = img * (1 - concentration_layer[..., np.newaxis])
        return img

    def update(frame):
        grid_frame, C_frame = history[frame]
        im.set_array(create_frame_image(grid_frame, C_frame))
        ax.set_title(f"Simulação - Passo {frame + 1}/{steps}")
        return im,

    ani = FuncAnimation(fig, update, frames=len(history), interval=50, blit=True)

# Botão de simulação
ax_button = plt.axes([0.75, 0.2, 0.2, 0.08])
btn = Button(ax_button, 'Iniciar Simulação')
btn.on_clicked(run_simulation)

# Botão de limpar grade
def limpar_grade(event):
    global grid, C, ani
    if ani is not None:  # Verifica se a animação está em andamento
        ani.event_source.stop()  # Para a animação
    grid = np.zeros(grid_size, dtype=int)
    grid[grid_size[0]//2, grid_size[1]//2] = SOURCE
    C = np.zeros(grid_size)
    C[grid == SOURCE] = 100.0
    update_display()

ax_clear = plt.axes([0.75, 0.1, 0.2, 0.08])
btn_clear = Button(ax_clear, 'Limpar Grade')
btn_clear.on_clicked(limpar_grade)

plt.show()

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.colors as mcolors
from matplotlib.widgets import Button

# Parâmetros da simulação
grid_size = (50, 50)
D = 0.1
dt = 1
steps = 200

# Tipos de células
AIR, WALL, SOURCE, OBSTACLE = 0, 1, 2, 3

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
im = ax.imshow(np.zeros((*grid_size, 3)), interpolation='nearest')
plt.title("Clique para adicionar:\nBotão esquerdo: Parede | Botão direito: Obstáculo | Botão do meio: Fonte")
plt.axis('off')

def update_display():
    img = np.zeros((*grid_size, 3))
    img[grid == AIR] = [1, 1, 1]
    img[grid == WALL] = [0, 0, 0]
    img[grid == SOURCE] = [1, 0, 0]
    img[grid == OBSTACLE] = [0, 0, 1]
    
    max_C = np.max(C) if np.max(C) > 0 else 1
    concentration_layer = np.clip(C / max_C, 0, 0.7)
    img = img * (1 - concentration_layer[..., np.newaxis])
    
    im.set_array(img)
    fig.canvas.draw()

update_display()

def onclick(event):
    if event.xdata is None or event.ydata is None:
        return
    
    ix, iy = int(event.xdata), int(event.ydata)
    if 0 <= ix < grid_size[1] and 0 <= iy < grid_size[0]:
        if event.button == 1:
            grid[iy, ix] = WALL
            C[iy, ix] = 0
        elif event.button == 3:
            grid[iy, ix] = OBSTACLE
            C[iy, ix] = 0
        elif event.button == 2:
            grid[iy, ix] = SOURCE
            C[iy, ix] = 100.0
        update_display()

fig.canvas.mpl_connect('button_press_event', onclick)

def run_simulation(event):
    global ani  # Usamos a variável global para manter a animação
    
    plt.close(fig)  # Fecha a janela de configuração
    
    # Prepara os dados da simulação
    history = []
    current_C = C.copy()
    current_grid = grid.copy()
    
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
    
    # Configura a animação
    fig2, ax2 = plt.subplots(figsize=(8, 8))
    
    def create_frame_image(frame_data):
        grid_frame, C_frame = frame_data
        img = np.zeros((*grid_size, 3))
        img[grid_frame == AIR] = [1, 1, 1]
        img[grid_frame == WALL] = [0, 0, 0]
        img[grid_frame == SOURCE] = [1, 0, 0]
        img[grid_frame == OBSTACLE] = [0, 0, 1]
        
        max_C = np.max(C_frame) if np.max(C_frame) > 0 else 1
        concentration_layer = np.clip(C_frame / max_C, 0, 0.7)
        img = img * (1 - concentration_layer[..., np.newaxis])
        return img
    
    im2 = ax2.imshow(create_frame_image(history[0]), interpolation='nearest')
    ax2.axis('off')
    
    def update(frame):
        im2.set_array(create_frame_image(history[frame]))
        ax2.set_title(f"Passo {frame+1}/{steps}")
        return im2,
    
    # Cria e armazena a animação
    ani = FuncAnimation(fig2, update, frames=len(history), interval=50, blit=True)
    plt.show()

# Botão para iniciar simulação
ax_button = plt.axes([0.3, 0.05, 0.4, 0.075])
btn = Button(ax_button, 'Iniciar Simulação')
btn.on_clicked(run_simulation)

plt.show()
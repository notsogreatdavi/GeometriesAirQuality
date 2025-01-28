import streamlit as st
import numpy as np
import time

# Título e introdução
st.title("Fractal")
st.write("Exemplo de fractal, ajustando os parâmetros na barra lateral.")

# Parâmetros interativos
iterations = st.sidebar.slider("Nível de detalhe (iterações)", 2, 20, 10, 1)
separation = st.sidebar.slider("Separação", 0.7, 2.0, 0.7885)

# Barra de progresso e texto de status
progress_bar = st.sidebar.progress(0)
frame_text = st.sidebar.empty()
image = st.empty()

# Configurações do fractal
m, n, s = 960, 640, 400
x = np.linspace(-m / s, m / s, num=m).reshape((1, m))
y = np.linspace(-n / s, n / s, num=n).reshape((n, 1))

# Loop para gerar os frames
for frame_num, a in enumerate(np.linspace(0.0, 4 * np.pi, 100)):
    progress_bar.progress(frame_num / 100)
    frame_text.text(f"Frame {frame_num + 1}/100")

    # Cálculo do fractal
    c = separation * np.exp(1j * a)
    Z = np.tile(x, (n, 1)) + 1j * np.tile(y, (1, m))
    C = np.full((n, m), c)
    M = np.full((n, m), True, dtype=bool)
    N = np.zeros((n, m))

    for i in range(iterations):
        Z[M] = Z[M] * Z[M] + C[M]
        M[np.abs(Z) > 2] = False
        N[M] = i

    # Atualiza a imagem no Streamlit
    image.image(1.0 - (N / N.max()), use_container_width=True)
    time.sleep(0.1)


progress_bar.empty()
frame_text.empty()

st.button("Reiniciar")

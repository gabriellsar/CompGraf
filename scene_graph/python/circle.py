import numpy as np
from OpenGL.GL import *
from shape import Shape


class Circle(Shape):
    def __init__(self, segments=100):
        positions = [0.0, 0.0, 0.0]  # Ponto central
        tex_coords = [0.5, 0.5]  # Coordenada de textura do centro

        for i in range(segments + 1):
            angle = i * (2.0 * np.pi / segments)
            # Raio de 0.5 para um diâmetro de 1, facilitando a escala
            x = 0.5 * np.cos(angle)
            y = 0.5 * np.sin(angle)
            positions.extend([x, y, 0.0])
            # Mapeia as coordenadas do vértice para coordenadas de textura (0 a 1)
            tex_coords.extend([(x + 0.5), (y + 0.5)])

        self.vertex_count = len(positions) // 3

        b_positions = np.array(positions, dtype=np.float32)
        b_tex_coords = np.array(tex_coords, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # Buffer para posições (location = 0)
        id_pos = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, id_pos)
        glBufferData(GL_ARRAY_BUFFER, b_positions.nbytes, b_positions, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)

        # Buffer para coordenadas de textura (location = 3)
        id_tex = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, id_tex)
        glBufferData(GL_ARRAY_BUFFER, b_tex_coords.nbytes, b_tex_coords, GL_STATIC_DRAW)
        glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(3)

    def Draw(self, st):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.vertex_count)
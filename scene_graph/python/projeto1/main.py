import glfw
from OpenGL.GL import *
import glm

from scene_graph.python.camera2d import *
from scene_graph.python.node import *
from scene_graph.python.scene import *
from scene_graph.python.shader import *
from scene_graph.python.texture import *
from scene_graph.python.transform import *
from scene_graph.python.engine import *
from scene_graph.python.quad import *


# Engine para controlar a animação do sistema solar em 2D
class SolarSystemEngine(Engine):
    def __init__(self, earth_translation_trf, earth_rotation_trf, moon_trf, mercury_trf):
        self.earth_translation_trf = earth_translation_trf
        self.earth_rotation_trf = earth_rotation_trf
        self.moon_trf = moon_trf
        self.mercury_trf = mercury_trf

    def Update(self, dt):
        # Velocidades angulares
        earth_orbit_speed = 30.0
        earth_rotation_speed = 150.0
        moon_orbit_speed = 100.0
        mercury_orbit_speed = 50.0

        # Rotação da Terra em seu eixo (agora no eixo Z para ser visível em 2D)
        self.earth_rotation_trf.Rotate(earth_rotation_speed * dt, 0, 0, 1)

        # Translação da Terra ao redor do Sol
        self.earth_translation_trf.Rotate(earth_orbit_speed * dt, 0, 0, 1)

        # Translação da Lua ao redor da Terra
        self.moon_trf.Rotate(moon_orbit_speed * dt, 0, 0, 1)

        # Translação de Mercúrio ao redor do Sol
        self.mercury_trf.Rotate(mercury_orbit_speed * dt, 0, 0, 1)


def main():
    # Inicializa a biblioteca GLFW
    if not glfw.init():
        return
    # Configura a janela
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
    win = glfw.create_window(800, 800, "Mini Sistema Solar 2D", None, None)
    if not win:
        glfw.terminate()
        return
    glfw.set_key_callback(win, keyboard)

    # Define o contexto OpenGL atual
    glfw.make_context_current(win)
    print("OpenGL version:", glGetString(GL_VERSION))

    initialize()

    # Loop principal
    t0 = glfw.get_time()
    while not glfw.window_should_close(win):
        t = glfw.get_time()
        dt = t - t0
        t0 = t

        update(dt)
        display()

        glfw.swap_buffers(win)
        glfw.poll_events()

    glfw.terminate()


def initialize():
    # Configurações iniciais do OpenGL
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    # Habilitar blending para transparência nas texturas (caso as imagens tenham)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Criação da câmera 2D
    global camera
    camera = Camera2D(xmin=-15, xmax=15, ymin=-15, ymax=15)

    # Shader 2D para todos os objetos
    shader = Shader()
    shader.AttachVertexShader("../shaders/2d/vertex.glsl")
    shader.AttachFragmentShader("../shaders/2d/fragment.glsl")
    shader.Link()

    # Geometria
    quad = Quad()

    # Texturas
    sun_tex = Texture("color", "../images/sun.jpg")
    earth_tex = Texture("color", "../images/earth.jpg")
    moon_tex = Texture("color", "../images/moon.jpg")
    mercury_tex = Texture("color", "../images/mercury.jpg")
    space_tex = Texture("color", "../images/space.jpg")

    # Transformações
    sun_trf = Transform()
    sun_trf.Scale(3.0, 3.0, 1.0)  # Escala maior para o Sol

    earth_translation_trf = Transform()
    earth_translation_trf.Translate(7, 0, 0)  # Distância da Terra ao Sol

    earth_rotation_trf = Transform()
    earth_rotation_trf.Scale(1.0, 1.0, 1.0)  # Tamanho da Terra

    moon_trf = Transform()
    moon_trf.Translate(2.0, 0, 0)  # Distância da Lua à Terra
    moon_trf.Scale(0.3, 0.3, 1.0)  # Tamanho da Lua

    mercury_trf = Transform()
    mercury_trf.Translate(4, 0, 0)  # Distância de Mercúrio ao Sol
    mercury_trf.Scale(0.5, 0.5, 1.0)  # Tamanho de Mercúrio

    background_trf = Transform()
    background_trf.Scale(30, 30, 1)

    # Construção do Grafo de Cena
    sun_node = Node(trf=sun_trf, apps=[sun_tex], shps=[quad])
    earth_node = Node(trf=earth_rotation_trf, apps=[earth_tex], shps=[quad])
    moon_node = Node(trf=moon_trf, apps=[moon_tex], shps=[quad])
    mercury_node = Node(trf=mercury_trf, apps=[mercury_tex], shps=[quad])

    background_node = Node(trf=background_trf, apps=[space_tex], shps=[quad])

    # Hierarquia
    # A Lua é filha da Terra, que por sua vez é filha do Sol (indiretamente via transformação)
    earth_translation_node = Node(trf=earth_translation_trf, nodes=[earth_node, moon_node])

    # O nó raiz contém todos os elementos da cena
    root = Node(shader=shader, nodes=[background_node, sun_node, earth_translation_node, mercury_node])

    # Criação da cena e do engine de animação
    global scene
    scene = Scene(root)
    engine = SolarSystemEngine(earth_translation_trf, earth_rotation_trf, moon_trf, mercury_trf)
    scene.AddEngine(engine)


def update(dt):
    scene.Update(dt)


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    scene.Render(camera)


def keyboard(win, key, scancode, action, mods):
    if key == glfw.KEY_Q and action == glfw.PRESS:
        glfw.set_window_should_close(win, True)


if __name__ == "__main__":
    main()
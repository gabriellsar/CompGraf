import glfw

from camera2d import *
from circle import *
from engine import *
from node import *
from quad import *
from scene import *
from shader import *
from sphere import *
from texture import *
from transform import *

camera = None
scene = None


class SolarSystemEngine(Engine):
    def __init__(self, earth_orbit_trf, earth_rotation_trf, moon_orbit_trf, mercury_orbit_trf):
        self.earth_orbit_trf = earth_orbit_trf
        self.earth_rotation_trf = earth_rotation_trf
        self.moon_orbit_trf = moon_orbit_trf
        self.mercury_orbit_trf = mercury_orbit_trf

    def Update(self, dt):
        earth_orbit_speed = 30.0
        earth_rotation_speed = 60.0
        moon_orbit_speed = 100.0
        mercury_orbit_speed = 50.0

        # Rotação da Terra
        self.earth_rotation_trf.Rotate(earth_rotation_speed * dt, 0, 1, 0)

        # Movimento de translação
        self.earth_orbit_trf.Rotate(earth_orbit_speed * dt, 0, 0, 1)
        self.moon_orbit_trf.Rotate(moon_orbit_speed * dt, 0, 0, 1)
        self.mercury_orbit_trf.Rotate(mercury_orbit_speed * dt, 0, 0, 1)

# --- Função Principal ---
def main():
    if not glfw.init(): return
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
    win = glfw.create_window(1000, 720, "Mini Sistema Solar", None, None)
    if not win:
        glfw.terminate()
        return
    glfw.set_key_callback(win, keyboard)
    glfw.make_context_current(win)
    initialize()
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
    global camera, scene
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    camera = Camera2D(xmin=-8, xmax=8, ymin=-8, ymax=8)

    # Shader
    shader = Shader()
    shader.AttachVertexShader("../shaders/2d/vertex.glsl")
    shader.AttachFragmentShader("../shaders/2d/fragment.glsl")
    shader.Link()

    # Geometrias
    circle = Circle()
    quad = Quad()
    sphere = Sphere()

    # Texturas
    sun_tex = Texture("decal", "../images/sun.jpg")
    earth_tex = Texture("decal", "../images/earth.jpg")
    moon_tex = Texture("decal", "../images/moon.jpg")
    mercury_tex = Texture("decal", "../images/mercury.jpg")
    space_tex = Texture("decal", "../images/space.jpeg")

    # Transformações
    background_trf = Transform()
    background_trf.Scale(24, 24, 1)
    background_trf.Translate(-0.5, -0.5, -0.5)

    # Sol
    sun_trf = Transform()
    sun_trf.Scale(5.0, 5.0, 1.0)

    # Mercúrio
    mercury_local_trf = Transform()
    mercury_local_trf.Translate(3.5, 0, 0)
    mercury_local_trf.Scale(0.6, 0.6, 1.0)
    mercury_orbit_trf = Transform()

    # Terra
    earth_orbit_trf = Transform()

    earth_local_trf = Transform()
    earth_local_trf.Translate(6, 0, 0)
    earth_local_trf.Scale(.9, .9, 1.0)

    earth_rotation_trf = Transform()

    # Lua
    moon_orbit_trf = Transform()
    moon_local_trf = Transform()
    moon_local_trf.Translate(1.4, 0, 0)
    moon_local_trf.Scale(0.5, 0.5, 1.0)

    # Grafo de Cena
    background_node = Node(trf=background_trf, apps=[space_tex], shps=[quad])
    sun_node = Node(trf=sun_trf, apps=[sun_tex], shps=[circle])

    mercury_inner_node = Node(apps=[mercury_tex], shps=[circle])
    mercury_node = Node(trf=mercury_local_trf, nodes=[mercury_inner_node])

    moon_inner_node = Node(apps=[moon_tex], shps=[circle])
    moon_node = Node(trf=moon_local_trf, nodes=[moon_inner_node])

    earth_rotating_node = Node(trf=earth_rotation_trf, apps=[earth_tex], shps=[sphere])
    earth_node = Node(trf=earth_local_trf, nodes=[
        earth_rotating_node,
        Node(trf=moon_orbit_trf, nodes=[moon_node])
    ])

    root = Node(shader=shader, nodes=[
        background_node,
        sun_node,
        Node(trf=mercury_orbit_trf, nodes=[mercury_node]),
        Node(trf=earth_orbit_trf, nodes=[earth_node])
    ])

    scene = Scene(root)
    engine = SolarSystemEngine(earth_orbit_trf, earth_rotation_trf, moon_orbit_trf, mercury_orbit_trf)
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
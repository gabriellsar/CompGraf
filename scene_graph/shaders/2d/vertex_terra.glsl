#version 410

layout (location=0) in vec4 vertex;
layout (location=3) in vec2 tex_coord_in;

out vec2 tex_coord_out;

uniform mat4 Mvp;

void main (void)
{
  gl_Position = Mvp * vertex;
  tex_coord_out = tex_coord_in;
}
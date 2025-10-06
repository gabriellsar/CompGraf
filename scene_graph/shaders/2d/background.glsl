#version 410

in vec2 tex_coord_out;
out vec4 outcolor;
uniform sampler2D decal;

void main()
{
  outcolor = texture(decal, tex_coord_out);
}
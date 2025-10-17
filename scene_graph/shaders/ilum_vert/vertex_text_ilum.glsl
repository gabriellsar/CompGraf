#version 410

layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec3 aTangent;
layout (location = 3) in vec2 aTexCoord;

out vec3 FragPos;
out vec3 Normal;
out vec3 Tangent;
out vec2 TexCoord;

uniform mat4 Mvp;
uniform mat4 Mv;
uniform mat4 Mn;

void main()
{
    FragPos = vec3(Mv * vec4(aPos, 1.0));
    Normal = mat3(Mn) * aNormal;
    Tangent = mat3(Mn) * aTangent;

    TexCoord = aTexCoord;
    gl_Position = Mvp * vec4(aPos, 1.0);
}
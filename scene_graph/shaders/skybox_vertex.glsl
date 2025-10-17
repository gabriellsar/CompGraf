#version 410 core
layout (location = 0) in vec3 aPos;

out vec3 TexCoords;

uniform mat4 projection;
uniform mat4 view;

void main()
{
    TexCoords = aPos;
    // Remove o componente de translação da matriz de visão
    // para que o SkyBox siga a câmera sem se mover.
    mat4 viewNoTranslation = mat4(mat3(view));
    vec4 pos = projection * viewNoTranslation * vec4(aPos, 1.0);
    // Garante que o SkyBox seja sempre desenhado no fundo
    gl_Position = pos.xyww;
}
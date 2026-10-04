// ============================================================================
//  glow.fx — هالة ضوء (Billboard Glow) للمشاعل والفوانيس
//  يُستخدم مع dxDrawMaterialLine3D لعمل قرص/هالة ضوء دافئة حول كل مصدر
// ============================================================================

texture gTexture;
sampler sTexture = sampler_state
{
    Texture   = (gTexture);
    MinFilter = Linear;
    MagFilter = Linear;
};

float4 gColor;                 // rgba
float  gFalloff;               // شدة السقوط من المركز إلى الحافة

float4 GlowPS(float2 uv : TEXCOORD0) : COLOR
{
    float4 t = tex2D(sTexture, uv) * gColor;
    // سقوط شعاعي ناعم من المركز
    float2 c = uv - 0.5;
    float  r = length(c) * 2.0;
    float  fall = saturate(1.0 - pow(r, 1.6)) * gFalloff;
    return float4(t.rgb * fall, t.a * fall);
}

technique Glow
{
    pass P0 { PixelShader = compile ps_2_0 GlowPS(); }
}

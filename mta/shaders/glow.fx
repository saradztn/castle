// ============================================================================
//  glow.fx — هالة ضوء (مشعل/فانوس/منارة) تُرسم بـ dxDrawMaterialLine3D
//  نواة ساخنة بيضاء + تدرّج ناعم نحو الأطراف + ارتعاش لهب اختياري
// ============================================================================

texture gTexture;
sampler sTexture = sampler_state
{
    Texture   = (gTexture);
    MinFilter = Linear;
    MagFilter = Linear;
    MipFilter = Linear;
    AddressU  = Clamp;
    AddressV  = Clamp;
};

float4 gColor;         // rgba الهالة (تُعبَّأ من Lua)
float  gFalloff;       // قوة التدرّج (1.0 افتراضًا)
float  gTime;          // ثوانٍ — للارتعاش
float  gFlicker;       // 1 = ارتعاش لهب، 0 = ثابت

struct PS_IN
{
    float2 uv : TEXCOORD0;
};

float4 GlowPS(PS_IN i) : COLOR
{
    float2 p = i.uv * 2.0 - 1.0;
    float  d = length(p);
    if (d > 1.0)
        discard;

    float4 tex  = tex2D(sTexture, i.uv);
    float  core = pow(saturate(1.0 - d), (gFalloff + 1.0) * 2.2);
    float  mid  = pow(saturate(1.0 - d), 1.4) * 0.5;

    float flick = 1.0;
    if (gFlicker > 0.5)
        flick = 0.86 + 0.14 * sin(gTime * 11.0 + i.uv.x * 7.0);

    float  a   = (core + mid) * tex.a * gColor.a * flick;
    float3 col = gColor.rgb * (0.60 + 0.80 * core) + float3(0.55, 0.42, 0.22) * core * core;

    return float4(col * a, a);
}

technique Glow
{
    pass P0
    {
        PixelShader = compile ps_3_0 GlowPS();
    }
}

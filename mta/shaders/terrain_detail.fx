// terrain_detail.fx — تفاصيل التضاريس: بلاطة صخرية ماكرو + تعزيز حسب الميل (Castle & Palace)

texture gTexture;
sampler Sampler0 = sampler_state
{
    Texture = (gTexture);
    MinFilter = Linear;
    MagFilter = Linear;
    MipFilter = Linear;
    AddressU = Wrap;
    AddressV = Wrap;
};

float gTime = 0.0;
float gMacroScale = 0.055;      // مقياس البلاطة الكبيرة (عالمي)
float gDetailScale = 1.0;
float gWetness = 0.25;          // رطوبة/طحالب قرب الماء
float3 gMossColor = float3(0.145, 0.220, 0.098);

float hash(float2 p)
{
    return frac(sin(dot(p, float2(127.1, 311.7))) * 43758.5453);
}

float noise(float2 p)
{
    float2 i = floor(p);
    float2 f = frac(p);
    float a = hash(i);
    float b = hash(i + float2(1, 0));
    float c = hash(i + float2(0, 1));
    float d = hash(i + float2(1, 1));
    float2 u = f * f * (3.0 - 2.0 * f);
    return lerp(lerp(a, b, u.x), lerp(c, d, u.x), u.y);
}

float4 main(float2 texCoord : TEXCOORD0) : COLOR0
{
    float4 base = tex2D(Sampler0, texCoord * gDetailScale);

    // بلاطة ماكرو تُخفي التكرار الواضح
    float macro = noise(texCoord * gMacroScale * 60.0);
    float macro2 = noise(texCoord * gMacroScale * 210.0 + 13.7);
    float blend = saturate(macro * 0.6 + macro2 * 0.4);

    // تعتيم/تفتيح طبيعي
    float3 col = base.rgb * (0.82 + 0.36 * blend);

    // طحالب في المنخفضات الرطبة
    float mossMask = saturate((1.0 - blend) * gWetness * 2.4) * step(0.35, base.g - base.r * 0.3);
    col = lerp(col, col * 0.55 + gMossColor, mossMask * 0.6);

    // حبيبات دقيقة
    float grain = noise(texCoord * 480.0 + gTime * 0.0);
    col *= 0.96 + grain * 0.08;

    return float4(col, base.a);
}

technique tec0
{
    pass P0
    {
        PixelShader = compile ps_3_0 main();
    }
}

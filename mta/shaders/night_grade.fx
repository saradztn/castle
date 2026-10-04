// night_grade.fx — دَرْج ليلي سينمائي: تباين + تلوين بارد + تعتيم حواف + إحساس فيلم
// يُستخدم كشيدر شاشة (Post-Processing) عبر dxCreateScreenSource.

texture gScreen;
sampler Sampler0 = sampler_state
{
    Texture = (gScreen);
    MinFilter = Linear;
    MagFilter = Linear;
    AddressU = Clamp;
    AddressV = Clamp;
};

float gTime = 0.0;
float gStrength = 0.0;        // 0 = بلا تأثير (نهار)، 1 = كامل
float3 gShadowTint = float3(0.72, 0.82, 1.12);   // الظلال تميل للأزرق
float3 gHighlightTint = float3(1.06, 0.98, 0.88); // الإضاءات تميل للدافئ

float4 main(float2 texCoord : TEXCOORD0) : COLOR0
{
    float4 c = tex2D(Sampler0, texCoord);
    float3 col = c.rgb;

    // تباين + رفع الأسود قليلًا (Look فيلم)
    col = (col - 0.5) * 1.12 + 0.5;
    col = pow(max(col, 0.0), float3(0.94, 0.95, 1.02));

    // تقسيم لوني: ظلال باردة وإضاءات دافئة
    float lum = dot(col, float3(0.299, 0.587, 0.114));
    float3 shadowMix = gShadowTint;
    float3 hiMix = gHighlightTint;
    float3 tinted = col * lerp(shadowMix, hiMix, smoothstep(0.18, 0.85, lum));

    // تعتيم حواف
    float2 d = texCoord - 0.5;
    float vig = 1.0 - dot(d, d) * 1.35;
    vig = saturate(vig);

    float3 outc = lerp(col, tinted * vig, gStrength);

    return float4(outc, c.a);
}

technique tec0
{
    pass P0
    {
        PixelShader = compile ps_3_0 main();
    }
}

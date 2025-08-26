#!/usr/bin/env python3
"""
演示服务器 - 使用模拟转录演示AI总结功能
"""

import os
import sys
from typing import List

# 添加server目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server'))

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("server/.env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUMMARY_MODEL = os.getenv("SUMMARY_MODEL", "gpt-4o-mini")

print(f"🔑 OpenAI API Key: {'✅ 已配置' if OPENAI_API_KEY and OPENAI_API_KEY != 'your_openai_api_key_here' else '❌ 未配置'}")

# 初始化OpenAI客户端
try:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("✅ OpenAI 客户端初始化成功")
except Exception as e:
    print(f"❌ OpenAI 客户端初始化失败: {e}")
    client = None

# 导入提示词模板
try:
    from prompts import SYSTEM_SUMMARY, USER_TEMPLATE
    print("✅ 提示词模板加载成功")
except ImportError:
    SYSTEM_SUMMARY = "你是资深投研助手。请基于转录文本，提炼【3–5条】'结论/要点'，偏向可执行或判断性的观点。要求：1) 用目标语言输出（默认中文）；2) 不复述无关细节，不展开长论述；3) 若视频仅提供中性信息，则给出概要判断；4) 不编造数据，不给具体买卖建议或目标价；5) 仅返回要点列表，必要时可附一行'整体观点'。"
    USER_TEMPLATE = "目标语言: {lang}\n\n以下是转录文本（可能含中英文混合、口语化）：\n\n{transcript}\n\n请输出：\n- 3–5 条要点（列表，每条一行）。\n- 末尾可选'整体观点：…'。"

app = FastAPI(title="YouTube Video Summarizer - Demo Version", description="AI Demo with simulated transcripts")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SummaryResp(BaseModel):
    video_id: str
    conclusions: List[str]
    summary: str
    transcript_preview: str

# 模拟的股票分析转录文本
DEMO_TRANSCRIPTS = {
    "XusGw6dZlH0": """
大家好，欢迎来到阳光财经。今天我们来分析一下美股市场的五大族群的表现。

首先我们看科技股，特别是AI相关的公司。英伟达最近的财报表现不错，收入同比增长了百分之二百多，主要是因为数据中心和AI芯片的需求爆发。但是我们也要注意到，现在AI股票的估值已经比较高了，投资者需要谨慎一些。

第二个族群是新能源汽车。特斯拉的交付量虽然还在增长，但是增速已经放缓了。而且现在竞争越来越激烈，传统车企都在加速电动化转型。我个人认为，这个行业的洗牌期可能还没有结束。

第三是生物医药股。最近FDA批准了几个重要的新药，相关公司的股价都有不错的表现。但是药企的研发周期长，风险也比较大，适合长期持有的投资者。

第四个是消费类股票。由于通胀压力和消费者支出的变化，很多消费品公司的业绩都受到了影响。不过一些有品牌优势的公司还是能保持相对稳定的表现。

最后是金融股，特别是银行。随着利率的变化，银行的净息差受到了一些影响。但是如果经济保持稳定，银行股还是有投资价值的。

总的来说，现在美股市场分化比较明显，投资者需要精选个股，不能盲目追高。建议大家重点关注有实际业绩支撑的公司，避免纯粹的概念炒作。

好了，今天的分析就到这里，如果大家有什么问题，欢迎在评论区讨论。记得点赞订阅，我们下期再见！
    """,
    
    # Palantir (PLTR) 分析转录
    "pltr_demo": """
大家好，今天我们来深入分析Palantir Technologies，也就是PLTR这只股票。

Palantir是一家专门做大数据分析的公司，主要为政府部门和企业客户提供数据集成和分析平台。公司有两个主要产品：Gotham平台主要服务于政府和国防部门，Foundry平台则面向商业客户。

从最新的财报来看，Palantir的增长势头很强劲。公司的总收入同比增长了30%以上，其中商业客户的增长尤其亮眼，达到了54%的同比增长。这说明Palantir正在成功拓展商业市场，不再只依赖政府合同。

在AI人工智能领域，Palantir的优势非常明显。他们的AIP平台（Artificial Intelligence Platform）已经帮助很多企业客户实现了AI应用的快速部署。随着各行各业对AI应用需求的增长，这为Palantir创造了巨大的市场机会。

不过投资者也需要注意风险。PLTR的估值确实不便宜，市盈率仍然比较高。而且公司的盈利能力还有待提升，虽然收入增长很快，但要实现持续盈利还需要时间。

另外，Palantir对政府合同的依赖度虽然在下降，但仍然比较高。政府预算的变化可能会影响公司的业绩稳定性。

总体来说，我认为Palantir是一个有潜力的长期投资标的，特别是在AI和大数据分析领域的领先地位值得关注。但短期内股价可能会有波动，适合风险承受能力强的投资者。
    """,
    
    # 加密货币分析转录
    "crypto_demo": """
各位朋友大家好，今天我们来聊聊比特币和加密货币市场的最新动态。

比特币最近的走势可以说是跌宕起伏，从高点回调之后又出现了一些反弹。我们看到机构投资者对比特币的态度越来越积极，特别是一些传统的金融机构开始将比特币纳入他们的投资组合。

以太坊方面，随着以太坊2.0升级的推进，网络的能耗大大降低，这对环保投资者来说是一个积极信号。而且DeFi生态系统继续在以太坊上蓬勃发展，为ETH提供了强劲的基本面支撑。

不过我们也要看到，监管环境仍然是加密货币市场面临的最大不确定性。各国政府对加密货币的态度不一，一些严厉的监管措施可能会对市场造成短期冲击。

从技术分析角度来看，比特币需要突破关键阻力位才能确立新的上涨趋势。目前的成交量还不够理想，说明市场参与者仍然比较谨慎。

对于普通投资者来说，我建议大家理性对待加密货币投资。这个市场波动性很大，只用自己承受得起损失的资金来投资。同时要做好充分的研究，选择有实际应用价值的项目。

总的来说，加密货币作为一种新兴资产类别，长期来看还是有很大发展空间的，但投资者需要做好风险管理。
    """,
    
    # 科技股分析转录
    "tech_demo": """
欢迎收看今天的科技股分析。我们来重点关注一下最近表现活跃的几只科技股。

首先是苹果公司AAPL。虽然iPhone销量在某些市场有所下滑，但是苹果的服务业务继续保持强劲增长。App Store、iCloud、Apple Music等服务的收入已经占到公司总收入的相当比例，而且利润率更高。这为苹果提供了更加稳定的收入来源。

微软MSFT在云计算领域的表现依然亮眼。Azure平台的增长速度虽然有所放缓，但仍然保持在两位数增长。特别是在AI领域，微软与OpenAI的合作让他们在企业AI应用方面占据了领先地位。

谷歌的母公司Alphabet GOOGL最近发布的财报显示，广告业务有所恢复，YouTube的收入增长也很不错。不过投资者更关注的是谷歌在AI领域的进展，特别是Bard AI助手能否与ChatGPT形成有效竞争。

Meta META在VR和元宇宙领域的投入巨大，但短期内还看不到明显的回报。不过他们的广告业务正在从去年的低迷中恢复，用户增长也重新企稳。

总体来说，科技股的基本面依然相对健康，但估值已经不便宜了。投资者需要更加精选个股，关注那些有真正技术优势和商业模式创新的公司。

在当前的宏观环境下，建议大家关注那些现金流充裕、有定价权的科技龙头，避免那些纯概念性的投机股票。
    """,
    
    "default": """
各位投资者大家好！今天我们来分析当前市场的投资机会和风险。

当前全球经济面临多重挑战，通胀压力、地缘政治风险、以及央行政策的不确定性都对市场产生影响。在这种环境下，我们建议投资者保持谨慎乐观的态度。

从行业配置来看，我们看好以下几个方向：第一是科技创新领域，特别是人工智能、云计算等新兴技术；第二是新能源和环保产业，长期成长空间巨大；第三是医疗健康，人口老龄化带来持续需求。

同时，我们也要警惕一些风险因素：高估值股票的回调风险，流动性收紧对成长股的压制，以及宏观经济下行对周期股的冲击。

投资策略上，建议采用分散投资的方式，控制好仓位，做好风险管理。短期可以关注业绩确定性强的蓝筹股，长期布局具有核心竞争力的优质成长股。

总的来说，虽然市场存在不确定性，但只要我们做好研究，选择优质标的，保持理性投资，相信还是能够获得不错的收益的。
    """
}

def get_demo_transcript(video_id: str) -> str:
    """获取演示用的转录文本"""
    # 如果有特定的视频ID映射，直接返回
    if video_id in DEMO_TRANSCRIPTS:
        return DEMO_TRANSCRIPTS[video_id]
    
    # 基于视频ID的简单hash来选择不同的demo内容，提供更多样化的演示
    import hashlib
    hash_value = int(hashlib.md5(video_id.encode()).hexdigest(), 16)
    
    # 根据hash值选择不同的demo转录
    demo_keys = ["pltr_demo", "crypto_demo", "tech_demo", "default"]
    selected_key = demo_keys[hash_value % len(demo_keys)]
    
    return DEMO_TRANSCRIPTS[selected_key]

def summarize_conclusions(transcript: str, lang: str = "zh") -> tuple[List[str], str]:
    """使用GPT生成结论总结"""
    if not client:
        # 如果没有OpenAI客户端，返回基于规则的简单总结
        if lang == "zh":
            return [
                "🤖 演示模式：AI服务未配置",
                "📊 基于转录内容的基本分析",
                "💡 建议配置OpenAI API以获得完整AI分析",
                "📈 当前显示的是演示结果"
            ], "整体观点：演示模式下的模拟分析结果"
    
    print(f"🧠 开始AI总结，输入长度: {len(transcript)} 字符")
    
    sys_prompt = SYSTEM_SUMMARY
    user_prompt = USER_TEMPLATE.format(lang=lang, transcript=transcript[:18000])

    try:
        resp = client.chat.completions.create(
            model=SUMMARY_MODEL,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
        )
        text = resp.choices[0].message.content.strip()
        print(f"✅ AI总结完成")

        # 解析结论
        lines = [l.strip("- •\t ") for l in text.splitlines() if l.strip()]
        conclusions = []
        overall = []
        for l in lines:
            if l.startswith("整体观点") or l.lower().startswith("overall"):
                overall.append(l)
            else:
                conclusions.append(l)
        return conclusions[:6], "\n".join(overall)
    
    except Exception as e:
        print(f"❌ AI总结失败: {e}")
        # 返回基于关键词的简单分析
        if "科技" in transcript or "AI" in transcript or "英伟达" in transcript:
            conclusions = ["科技股表现活跃，AI概念受关注", "英伟达等芯片股财报亮眼", "但估值已达高位，需谨慎投资"]
        elif "新能源" in transcript or "特斯拉" in transcript:
            conclusions = ["新能源汽车行业竞争加剧", "特斯拉增速放缓但仍有优势", "行业洗牌期尚未结束"]
        elif "银行" in transcript or "金融" in transcript:
            conclusions = ["金融股受利率政策影响", "银行净息差面临压力", "经济稳定下仍有投资价值"]
        else:
            conclusions = ["市场分化明显，需精选个股", "建议关注业绩支撑的公司", "避免概念炒作，保持理性投资"]
        
        return conclusions, "整体观点：当前市场环境下建议谨慎乐观，做好风险控制"

@app.get("/")
async def root():
    return {
        "message": "YouTube Video Summarizer API - Demo Version",
        "status": "running",
        "openai_configured": bool(client),
        "note": "Using simulated transcripts for demo purposes",
        "endpoints": {
            "summarize": "/api/summarize?video_id=VIDEO_ID&lang=zh",
            "docs": "/docs"
        }
    }

@app.get("/api/summarize", response_model=SummaryResp)
async def api_summarize_demo(video_id: str = Query(...), lang: str = Query("zh")):
    """演示版总结API - 使用模拟转录"""
    
    print(f"📹 演示模式处理视频: {video_id}")
    
    # 获取演示转录
    transcript = get_demo_transcript(video_id)
    print(f"📝 使用演示转录，长度: {len(transcript)} 字符")
    
    try:
        # AI总结
        conclusions, overall = summarize_conclusions(transcript, lang=lang)
        
        # 生成预览
        preview = transcript[:800] + ("…" if len(transcript) > 800 else "")
        
        result = SummaryResp(
            video_id=video_id,
            conclusions=conclusions,
            summary=overall,
            transcript_preview=preview,
        )
        
        print(f"🎉 演示处理完成: {len(conclusions)} 条结论")
        return result
        
    except Exception as e:
        print(f"❌ 演示处理出错: {e}")
        raise HTTPException(status_code=500, detail=f"演示处理失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    print("🧪 启动演示版 YouTube 总结服务...")
    print("📡 服务将运行在: http://localhost:8000")
    print("📖 API 文档: http://localhost:8000/docs")
    print("🎭 使用模拟转录演示AI总结功能")
    print("⏹️  按 Ctrl+C 停止服务")
    print("-" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
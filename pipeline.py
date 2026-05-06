from agents import (
    build_search_agent,
    writer_chain,
    critic_chain,
    llm
)
from tools import scrape_url
import json


def rank_sources(results):
    ranked = []

    for item in results:
        score = 0
        url = item["url"].lower()

        # credibility boost
        if any(domain in url for domain in [
            "investopedia", "reuters", "bloomberg", "apnews"
        ]):
            score += 3

        # penalty
        if "youtube" in url:
            score -= 5

        # snippet quality
        score += len(item.get("snippet", "")) / 100

        ranked.append((score, item))

    ranked.sort(reverse=True, key=lambda x: x[0])
    return [item for _, item in ranked]



def summarize_content(text):
    prompt = f"""
Summarize the following content into 5 to 6 key bullet points.
Focus on facts, numbers, and insights.

Content:
{text[:2000]}

Return concise bullet points.
"""
    return llm.invoke(prompt)

# MAIN PIPELINE
def run_search_agent_pipeline(topic: str) -> dict:
    state = {}

    # =========================
    # Step 1 - Search Agent
    # =========================
    print("\n" + "="*50)
    print("step 1 - search agent is working ...")
    print("="*50)

    search_agent = build_search_agent()

    search_result = search_agent.invoke({
        "messages": [("user", f"find recent, reliable and detailed information about : {topic}")]
    })

    # Extract tool output safely
    tool_msg = next(
        (msg for msg in search_result["messages"] if msg.type == "tool"),
        None
    )

    if not tool_msg:
        raise ValueError("No tool response found")

    search_data = json.loads(tool_msg.content)

    # structured results
    state["search_results"] = [
        {
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": item.get("content", "")
        }
        for item in search_data
    ]

    # Rank sources
    state["search_results"] = rank_sources(state["search_results"])

    print("\nRanked Sources:\n")
    for i, item in enumerate(state["search_results"], 1):
        print(f"[{i}] {item['title']}")
        print(f"URL: {item['url']}\n")

    # Step 2 - Scrape + Summarize
    print("\n" + "="*50)
    print("step 2 - scraping + summarizing ...")
    print("="*50)

    summaries = []
    sources_map = {}

    for i, item in enumerate(state["search_results"], 1):
        url = item["url"]

        # skip bad sources
        if "youtube" in url.lower():
            continue

        print(f"\n Processing [{i}]: {url}")

        try:
            raw = scrape_url.invoke({"url": url})
            raw = str(raw)[:2000]

            summary = summarize_content(raw)

            # normalize summary
            if isinstance(summary, list):
                summary = " ".join(
                    x.get("text", "") if isinstance(x, dict) else str(x)
                    for x in summary
                )

            summaries.append(f"[{i}] {summary}")
            sources_map[i] = url

        except Exception as e:
            print(f"❌ Failed: {url} → {e}")

    if not summaries:
        raise ValueError("No summaries generated")

    # =========================
    # Step 3 - Writer
    # =========================
    print("\n" + "="*50)
    print("step 3 - writing report ...")
    print("="*50)

    research_combined = (
        f"TOPIC: {topic}\n\n"
        f"SOURCE SUMMARIES:\n\n" + "\n\n".join(summaries)
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    # =========================
    # Step 4 - Add Sources List
    # =========================
    sources_text = "\n".join([
        f"[{i}] {url}" for i, url in sources_map.items()
    ])

    state["report"] += f"\n\nSources:\n{sources_text}"

    print("\nFinal Report:\n", state["report"])

    # =========================
    # Step 5 - Critic
    # =========================
    print("\n" + "="*50)
    print("step 4 - critic review ...")
    print("="*50)

    state["feedback"] = critic_chain.invoke({
        "report": state["report"]
    })

    print("\nCritic Report:\n", state["feedback"])

    return state


if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    run_search_agent_pipeline(topic)
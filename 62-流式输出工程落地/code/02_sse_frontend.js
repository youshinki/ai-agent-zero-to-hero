// 前端 SSE 增量渲染：只追加 delta，不整段重渲染
async function streamAnswer(query) {
    const resp = await fetch("/chat/stream", {method: "POST", body: JSON.stringify({query})});
    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let answerEl = document.getElementById("answer");

    while (true) {
        const {done, value} = await reader.read();
        if (done) break;
        // 解析 SSE 格式：data: {...}\n\n
        const text = decoder.decode(value);
        for (const block of text.split("\n\n")) {
            if (!block.startsWith("data: ")) continue;
            const data = JSON.parse(block.slice(6));
            if (data.type === "answer") {
                answerEl.textContent += data.text;  // 只追加，不重渲染整段
            } else if (data.type === "done") {
                // 结束，隐藏 loading
            }
        }
    }
}

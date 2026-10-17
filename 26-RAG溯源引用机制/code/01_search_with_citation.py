# ===== kb_core.py：search 方法结构化溯源输出 =====

def search(self, query):
    """
    全新升级：带溯源引用的高精度检索
    返回结构化溯源数据 + 可直接喂给模型的引用文本
    """
    if not self.store["doc_list"]:
        return "知识库暂无任何私有文档内容"

    # 1. 多路扩召
    query_vec = self.get_embedding(query)
    raw_score_list = []

    for item in self.store["doc_list"]:
        sim_score = self.calc_similarity(query_vec, item["vector"])
        raw_score_list.append({
            "score": sim_score,
            "content": item["content"],
            "source": item["source"]
        })

    raw_top = sorted(raw_score_list, key=lambda x: x["score"], reverse=True)[:INIT_RECALL_TOPK]
    # 2. 重排序
    rerank_top = self.rerank_results(query, raw_top)
    # 3. 去重融合
    final_results = self.fuse_dup_content(rerank_top)

    if not final_results:
        return "未检索到相关私有文档内容"

    # ========== 新增：封装溯源引用信息 ==========
    ref_text = "【参考知识库片段（带溯源）】\n"
    ref_map = {}

    for idx, item in enumerate(final_results):
        ref_id = idx + 1
        ref_text += f"\n[引用{ref_id}] 来源文档：{item['source']}\n"
        ref_text += f"内容：{item['content']}\n"
        ref_map[ref_id] = {
            "source": item["source"],
            "score": item["total_score"],
            "content": item["content"]
        }

    # 4. 自适应压缩
    ref_text = compressor.compress(ref_text, MAX_CONTEXT_TOKEN)
    return ref_text

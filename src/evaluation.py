import json
from retrieval import RetrievalSystem
from generation import ScholarAI

# =========================
#     TEST QUESTIONS
# =========================
# Load test questions with paper mappings
with open("test_questions_mapped.json", "r", encoding="utf-8") as f:
    TEST_QUESTIONS = json.load(f)


# =========================
#   RETRIEVAL EVALUATION
# =========================
class RetrievalEvaluator:
    def __init__(self):
        self.retriever = RetrievalSystem()
    
    def evaluate_single_query(self, question, relevant_papers, k=5):
        """
        Evaluate retrieval for a single question
        Returns metrics: recall@k, precision@k, mrr
        """
        retrieved = self.retriever.retrieve(question, k=k)
        retrieved_paper_ids = [
            c.get("metadata", {}).get("paper_id", "") for c in retrieved
        ]
        
        # Calculate metrics
        relevant_retrieved = len(set(retrieved_paper_ids) & set(relevant_papers))
        
        recall = relevant_retrieved / len(relevant_papers) if relevant_papers else 0
        precision = relevant_retrieved / k if k > 0 else 0
        
        # Mean Reciprocal Rank
        mrr = 0
        for i, paper_id in enumerate(retrieved_paper_ids, 1):
            if paper_id in relevant_papers:
                mrr = 1 / i
                break
        
        return {
            "recall": recall,
            "precision": precision,
            "mrr": mrr,
            "retrieved_papers": retrieved_paper_ids
        }
    
    def evaluate_all(self, test_questions, k_values=[3, 5, 10]):
        """Evaluate retrieval across all test questions"""
        results = {}
        
        for k in k_values:
            recalls = []
            precisions = []
            mrrs = []
            
            for q in test_questions:
                if not q["relevant_papers"]:
                    continue  # Skip if no ground truth
                
                metrics = self.evaluate_single_query(
                    q["question"], 
                    q["relevant_papers"], 
                    k=k
                )
                
                recalls.append(metrics["recall"])
                precisions.append(metrics["precision"])
                mrrs.append(metrics["mrr"])
            
            results[f"k={k}"] = {
                "avg_recall": sum(recalls) / len(recalls) if recalls else 0,
                "avg_precision": sum(precisions) / len(precisions) if precisions else 0,
                "avg_mrr": sum(mrrs) / len(mrrs) if mrrs else 0,
                "num_queries": len(recalls)
            }
        
        return results


# =========================
#  GENERATION EVALUATION
# =========================
class GenerationEvaluator:
    def __init__(self):
        self.scholar = ScholarAI(top_k=5)
    
    def evaluate_answer(self, question, answer, expected_concepts):
        """
        Manual evaluation checklist for a single answer
        Returns dict with evaluation criteria
        """
        answer_lower = answer.lower()
        
        # Check concept coverage
        concepts_found = [
            concept for concept in expected_concepts 
            if concept.lower() in answer_lower
        ]
        concept_coverage = len(concepts_found) / len(expected_concepts) if expected_concepts else 0
        
        # Check for citations (simple heuristic)
        has_citations = "[1]" in answer or "[2]" in answer
        
        # Length check (answers should be substantial)
        word_count = len(answer.split())
        is_substantial = word_count > 100
        
        return {
            "question": question,
            "concept_coverage": concept_coverage,
            "concepts_found": concepts_found,
            "concepts_missing": [c for c in expected_concepts if c not in concepts_found],
            "has_citations": has_citations,
            "word_count": word_count,
            "is_substantial": is_substantial,
            "answer_preview": answer[:200] + "..." if len(answer) > 200 else answer
        }
    
    def evaluate_all(self, test_questions):
        """Generate and evaluate answers for all test questions"""
        results = []
        
        for q in test_questions:
            print(f"\nEvaluating: {q['question']}")
            answer, chunks = self.scholar.generate_expert_answer(q["question"])
            
            eval_result = self.evaluate_answer(
                q["question"],
                answer,
                q["expected_concepts"]
            )
            
            eval_result["question_id"] = q["id"]
            eval_result["category"] = q["category"]
            eval_result["num_sources"] = len(chunks)
            
            results.append(eval_result)
        
        return results


# =========================
#      MAIN EVALUATION
# =========================
if __name__ == "__main__":
    print("=" * 80)
    print("REGRESSION SCHOLAR - EVALUATION")
    print("=" * 80)
    
    # 1. RETRIEVAL EVALUATION
    print("\n1. RETRIEVAL EVALUATION")
    print("-" * 80)
    
    ret_eval = RetrievalEvaluator()
    retrieval_results = ret_eval.evaluate_all(TEST_QUESTIONS, k_values=[3, 5, 10])
    
    print("\nRetrieval Metrics:")
    for k, metrics in retrieval_results.items():
        print(f"\n{k}:")
        print(f"  Average Recall: {metrics['avg_recall']:.3f}")
        print(f"  Average Precision: {metrics['avg_precision']:.3f}")
        print(f"  Average MRR: {metrics['avg_mrr']:.3f}")
        print(f"  Queries evaluated: {metrics['num_queries']}")
    
    # 2. GENERATION EVALUATION
    print("\n\n2. GENERATION EVALUATION")
    print("-" * 80)
    
    gen_eval = GenerationEvaluator()
    generation_results = gen_eval.evaluate_all(TEST_QUESTIONS[:5])  # Start with first 5
    
    print("\nGeneration Metrics:")
    avg_coverage = sum(r["concept_coverage"] for r in generation_results) / len(generation_results)
    avg_word_count = sum(r["word_count"] for r in generation_results) / len(generation_results)
    citation_rate = sum(r["has_citations"] for r in generation_results) / len(generation_results)
    
    print(f"\nAverage concept coverage: {avg_coverage:.2%}")
    print(f"Average word count: {avg_word_count:.0f}")
    print(f"Citation rate: {citation_rate:.2%}")
    
    print("\n\nDetailed Results:")
    for r in generation_results:
        print(f"\n{r['question_id']}. {r['question']}")
        print(f"   Concept coverage: {r['concept_coverage']:.2%}")
        print(f"   Concepts found: {r['concepts_found']}")
        print(f"   Missing: {r['concepts_missing']}")
        print(f"   Has citations: {r['has_citations']}")
        print(f"   Word count: {r['word_count']}")
    
    # 3. SAVE RESULTS
    output = {
        "retrieval": retrieval_results,
        "generation": generation_results,
        "summary": {
            "avg_concept_coverage": avg_coverage,
            "avg_word_count": avg_word_count,
            "citation_rate": citation_rate
        }
    }
    
    with open("evaluation_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\n\n" + "=" * 80)
    print("Evaluation complete! Results saved to evaluation_results.json")
    print("=" * 80)

class RelevanceValidator:

    def __init__(
        self,
        min_top_score=0.15,
        min_average_score=0.15
    ):
        self.min_top_score = min_top_score
        self.min_average_score = min_average_score

    def validate(self, retrieval_results, query=""):

        if not retrieval_results:
            return False, "No clauses retrieved."

        # Retrieved results should be sorted by descending score.
        top_score = max(
            item["score"] for item in retrieval_results
        )

        avg_score = sum(
            item["score"]
            for item in retrieval_results
        ) / len(retrieval_results)

        print("\n==============================")
        print("Relevance Validator")
        print("==============================")
        print(f"Query         : {query}")
        print(f"Top Score     : {top_score:.4f}")
        print(f"Average Score : {avg_score:.4f}")
        print(f"Top Threshold : {self.min_top_score:.4f}")
        print(f"Avg Threshold : {self.min_average_score:.4f}")
        print("==============================\n")

        if top_score < self.min_top_score:
            return False, (
                f"Query not sufficiently related to uploaded "
                f"documents (Top Score = {top_score:.4f})"
            )

        if avg_score < self.min_average_score:
            return False, (
                f"Retrieved clauses are too weak "
                f"(Average Score = {avg_score:.4f})"
            )

        return True, "Relevant query"

PAPER_MAPPING = {
    # Ridge regression papers
    "ridge": [
        "1509.09169v8",  # Lecture notes on ridge regression
        "1507.03003v2",  # High-Dimensional Asymptotics: Ridge Regression
        "2009.08071v2",  # Ridge Regression Revisited
        "1409.2437v5",  # Fast Marginal Likelihood Estimation of Ridge
        "1608.00621v3",  # Kernel Ridge Regression
        "2408.13474v2",  # Ridge, lasso, and elastic-net estimations
    ],
    
    # LASSO papers
    "lasso": [
        "1108.4559v2",  # Optimal Algorithms for Ridge and Lasso
        "1010.3320v2",  # Exact block-wise optimization in group lasso
        "1910.01805v2",  # On the Duality between Network Flows and Network Lasso
        "2003.14118v1",  # A flexible adaptive lasso Cox frailty model
        "2512.10632v1",  # Lasso-Ridge Refitting
        "2408.13474v2",  # Ridge, lasso, and elastic-net estimations
    ],
    
    # Regularization general
    "regularization": [
        "2310.10807v1",  # Regularization properties of adversarially-trained
        "1311.2791v1",  # When Does More Regularization Imply Fewer Degrees of Freedom
        "2305.18496v2",  # Generalized equivalences between subsampling and ridge
    ],
    
    # Kernel methods
    "kernel": [
        "1608.00621v3",  # Kernel Ridge Regression
        "1907.02242v2",  # Fair Kernel Regression
        "2310.13966v3",  # Transfer Learning for Kernel-based Regression
        "1710.07004v2",  # Modal Regression using Kernel Density
        "1907.08592v2",  # Kernel Mode Decomposition
        "1411.0306v3",  # Fast Randomized Kernel Methods
    ],
    
    # Gaussian processes
    "gaussian_process": [
        "1302.4245v3",  # Gaussian Process Kernels
        "1912.06552v1",  # Active emulation with Gaussian processes
        "1911.00955v2",  # Gaussian process surrogate modeling
        "2002.02826v3",  # Conditional Deep Gaussian Processes
        "1911.09946v3",  # Actively Learning Gaussian Process Dynamics
        "1809.04967v3",  # Gaussian process classification
        "1110.4411v1",  # Gaussian Process Regression Networks
        "2310.19390v2",  # Implicit Manifold Gaussian Process Regression
        "2203.09179v3",  # Maximum Likelihood Estimation in GP Regression
        "2304.12923v1",  # Quantum Gaussian Process Regression
    ],
}

# Now map to specific questions
TEST_QUESTIONS_WITH_PAPERS = [
    {
        "id": 1,
        "question": "What is ridge regression?",
        "category": "definition",
        "expected_concepts": ["regularization", "L2 penalty", "shrinkage"],
        "relevant_papers": PAPER_MAPPING["ridge"]
    },
    {
        "id": 2,
        "question": "Compare ridge and LASSO",
        "category": "comparison",
        "expected_concepts": ["L1 vs L2", "variable selection", "sparsity"],
        "relevant_papers": PAPER_MAPPING["ridge"] + PAPER_MAPPING["lasso"]
    },
    {
        "id": 3,
        "question": "What is the bias-variance tradeoff?",
        "category": "concept",
        "expected_concepts": ["bias", "variance", "model complexity", "regularization"],
        "relevant_papers": [
            "1507.03003v2",  # High-Dimensional Asymptotics
            "1311.2791v1",  # Degrees of Freedom
            "1509.09169v8",  # Ridge lecture notes
        ]
    },
    {
        "id": 4,
        "question": "When should I use LASSO vs ridge regression?",
        "category": "application",
        "expected_concepts": ["sparsity assumption", "feature selection", "collinearity"],
        "relevant_papers": PAPER_MAPPING["ridge"] + PAPER_MAPPING["lasso"]
    },
    {
        "id": 5,
        "question": "What is elastic net regression?",
        "category": "definition",
        "expected_concepts": ["L1 and L2 penalty", "combination", "regularization"],
        "relevant_papers": [
            "2408.13474v2",  # Ridge, lasso, and elastic-net
            "2512.10632v1",  # Lasso-Ridge Refitting
        ]
    },
    {
        "id": 6,
        "question": "How does regularization affect overfitting?",
        "category": "concept",
        "expected_concepts": ["overfitting", "generalization", "penalty term"],
        "relevant_papers": PAPER_MAPPING["regularization"] + PAPER_MAPPING["ridge"][:3]
    },
    {
        "id": 7,
        "question": "What is cross-validation in the context of regression?",
        "category": "method",
        "expected_concepts": ["hyperparameter tuning", "validation", "model selection"],
        "relevant_papers": [
            "1409.2437v5",  # Fast Marginal Likelihood Estimation
            "1601.06722v2",  # Optimal designs for comparing regression
        ]
    },
    {
        "id": 8,
        "question": "Explain the LASSO solution path",
        "category": "technical",
        "expected_concepts": ["lambda", "coefficient trajectory", "shrinkage"],
        "relevant_papers": PAPER_MAPPING["lasso"][:4]
    },
    {
        "id": 9,
        "question": "What are the computational aspects of ridge regression?",
        "category": "technical",
        "expected_concepts": ["closed-form solution", "computational complexity"],
        "relevant_papers": [
            "1509.09169v8",  # Ridge lecture notes
            "1409.2437v5",  # Fast Marginal Likelihood
            "1608.00621v3",  # Efficient Multiple Incremental Computation
        ]
    },
    {
        "id": 10,
        "question": "How do you choose the regularization parameter?",
        "category": "application",
        "expected_concepts": ["cross-validation", "tuning", "lambda", "optimization"],
        "relevant_papers": [
            "1409.2437v5",  # Fast Marginal Likelihood Estimation
            "2009.08071v2",  # Ridge Regression Revisited
        ]
    },
    {
        "id": 11,
        "question": "What is kernel ridge regression?",
        "category": "definition",
        "expected_concepts": ["kernel trick", "non-linear", "ridge regression"],
        "relevant_papers": PAPER_MAPPING["kernel"][:4] + ["1509.09169v8"]
    },
    {
        "id": 12,
        "question": "How do Gaussian processes relate to regression?",
        "category": "concept",
        "expected_concepts": ["probabilistic", "uncertainty", "kernel methods"],
        "relevant_papers": PAPER_MAPPING["gaussian_process"][:5]
    },
    {
        "id": 13,
        "question": "What is the difference between group LASSO and standard LASSO?",
        "category": "technical",
        "expected_concepts": ["group structure", "variable selection", "penalty"],
        "relevant_papers": [
            "1010.3320v2",  # Exact block-wise optimization in group lasso
            "1108.4559v2",  # Optimal Algorithms
        ]
    },
    {
        "id": 14,
        "question": "Explain degrees of freedom in regularized regression",
        "category": "concept",
        "expected_concepts": ["degrees of freedom", "model complexity", "regularization"],
        "relevant_papers": [
            "1311.2791v1",  # When Does More Regularization Imply Fewer DoF
        ]
    },
    {
        "id": 15,
        "question": "What is ridge regression debiasing?",
        "category": "technical",
        "expected_concepts": ["bias correction", "estimation", "inference"],
        "relevant_papers": [
            "2009.08071v2",  # Ridge Regression Revisited: Debiasing
        ]
    },
]

# Save to JSON
import json
with open("test_questions_mapped.json", "w") as f:
    json.dump(TEST_QUESTIONS_WITH_PAPERS, f, indent=2)

print(f"Created {len(TEST_QUESTIONS_WITH_PAPERS)} test questions with paper mappings")
print("\nQuestion categories:")
from collections import Counter
categories = Counter(q["category"] for q in TEST_QUESTIONS_WITH_PAPERS)
for cat, count in categories.items():
    print(f"  {cat}: {count}")
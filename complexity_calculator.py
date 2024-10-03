from radon.complexity import cc_rank, cc_visit

def calculate_complexity(code: str):
    """
    Calculate the cyclomatic complexity of the code.
    """
    complexity = cc_visit(code)
    complexity_metrics = []
    for result in complexity:
        complexity_metrics.append({
            'name': result.name,
            'complexity': result.complexity,
            'rank': cc_rank(result.complexity)
        })
    
    return complexity_metrics

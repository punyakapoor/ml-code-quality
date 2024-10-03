import torch
from transformers import AutoTokenizer, AutoModel
from typing import List, Dict

class CodeBERTAnalyzer:
    def __init__(self):
        # Load the CodeBERT model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        self.model = AutoModel.from_pretrained("microsoft/codebert-base")
    
    def analyze_code(self, code: str) -> torch.Tensor:
        """
        Analyze code using CodeBERT and return its embedding.
        """
        # Tokenize the input code
        inputs = self.tokenizer(code, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        # Generate embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Return the embedding for the [CLS] token
        return outputs.last_hidden_state[:, 0, :]
    
    def get_code_quality_suggestions(self, code: str) -> List[Dict[str, str]]:
        """
        Get suggestions for code improvement based on embeddings.
        """
        # Get the embeddings for the code
        code_embedding = self.analyze_code(code)
        
        # Generate suggestions based on embeddings
        suggestions = []

        # Example rules based on embedding values (these are placeholders)
        if code_embedding[0, 0].item() > 0.5:
            suggestions.append({
                "type": "Review",
                "message": "This code might be complex; consider reviewing it."
            })

        if code_embedding[0, 1].item() < -0.5:
            suggestions.append({
                "type": "Documentation",
                "message": "Consider adding more comments or improving documentation."
            })

        return suggestions

import torch
from torch import nn


import torch
from torch import nn

class LoRA(nn.Module):
    """Low-Rank Adaptation module for fine-tuning neural networks."""

    def __init__(self, in_features: int, out_features: int, rank: int):
        """
        Initialize LoRA module with low-rank matrices.

        Args:
            in_features: Input dimension
            out_features: Output dimension
            rank: Rank of the low-rank approximation
        """
        super().__init__()
        
        # Define the low-rank matrices A and B
        self.A = nn.Parameter(torch.randn(in_features, rank) * 0.02)  # A is initialized with normal distribution
        self.B = nn.Parameter(torch.zeros(rank, out_features))        # B is initialized with zeros

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the LoRA module."""
        # Perform low-rank adaptation
        return torch.matmul(torch.matmul(x, self.A), self.B)



def apply_lora(model: nn.Module, rank: int = 16):
    """
    Apply LoRA to all square linear layers in the model.

    Args:
        model: The model to apply LoRA to
        rank: Rank for the LoRA modules
    """
    device = next(model.parameters()).device

    for name, module in model.named_modules():
        if not isinstance(module, nn.Linear):
            continue

        # Only apply to square matrices
        if module.weight.shape[0] != module.weight.shape[1]:
            continue

        in_features, out_features = module.weight.shape
        lora = LoRA(in_features, out_features, rank=rank).to(device)
        setattr(module, "lora", lora)

        # Store original forward method
        original_forward = module.forward

        # Create new forward method with closure to avoid late binding issues
        def make_forward_with_lora(orig_forward, lora_module):
            def forward_with_lora(x):
                return orig_forward(x) + lora_module(x)

            return forward_with_lora

        # Replace the forward method
        module.forward = make_forward_with_lora(original_forward, lora)

    return model

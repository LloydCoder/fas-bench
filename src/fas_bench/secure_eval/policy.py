from .models import ExecutionPolicy


def default_policy(image: str) -> ExecutionPolicy:
    return ExecutionPolicy(image=image)

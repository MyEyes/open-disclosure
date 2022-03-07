from cryptography.hazmat.primitives import hashes

class ContainerChallenge:

    def __init__(self, solution, difficulty) -> None:
        self.type = "sha256"

        digest = hashes.Hash(hashes.SHA256())
        digest.update(solution)

        self.target = digest.finalize()
        self.problem = solution
from typing import List, Dict

class ChatMemoryService:
    def __init__(self):
        self.memory = {}

    def get_memory(self, customer_email: str) -> List[Dict]:
        """
        Recupera el historial de mensajes de un cliente específico.
        """
        return self.memory.get(customer_email, [])

    def update_memory(self, customer_email: str, message: Dict):
        """
        Agrega un mensaje al historial del cliente.
        """
        if customer_email not in self.memory:
            self.memory[customer_email] = []
        self.memory[customer_email].append(message)

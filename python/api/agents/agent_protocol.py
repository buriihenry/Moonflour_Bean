from typing import Protocol, List, Dict, Any

class AgentProtoco(Protocol):
    def get_response(self,messages:List[Dict[str,Any]]) -> Dict[str,Any]:
        ...
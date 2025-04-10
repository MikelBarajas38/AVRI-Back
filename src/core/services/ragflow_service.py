import os
import requests
from typing import Dict, Any, List, Optional
import json


class RAGFlowService:
    """
    Class that provides an interface to interact with the RAGFlow API.
    """

    def __init__(
            self,
            base_url=None,
            api_key=None,
    ):
        self.base_url = base_url or os.environ.get('RAGFLOW_BASE_URL')
        self.api_key = api_key or os.environ.get('RAGFLOW_API_KEY')
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}' if self.api_key else None
        }
        print(f'Base URL: {self.base_url}')
        print(f'API Key: {self.api_key}')

    def main(self):
        """
        Main method to run the service.
        """
        ragflow_service = RAGFlowService()

        assistants = ragflow_service.list_assistants(name='AVRI')
        print(json.dumps(assistants, indent=2))

        name = assistants['data'][0]['name']
        id = assistants['data'][0]['id']
        print(f'Name: {name}, ID: {id}')

        sessions = ragflow_service.list_sessions(assistant_id=id)
        print(json.dumps(sessions, indent=2))
        session_id_1 = sessions['data'][0]['id']
        print(f'Session ID: {session_id_1}')

        session = ragflow_service.create_session(
            assistant_id=id,
            session_name='My session'
        )
        print(json.dumps(session, indent=2))
        session_id = session['data']['id']
        print(f'Session ID: {session_id}')

        response = ragflow_service.ask_question(
            assistant_id=id,
            question='Hello',
            session_id=session_id,
        )
        print(json.dumps(response, indent=2))

        response = ragflow_service.ask_question(
            assistant_id=id,
            question='Tell me about breast cancer',
            session_id=session_id_1,
        )
        print(json.dumps(response, indent=2))

        session = ragflow_service.delete_session(
            assistant_id=id,
            session_ids=[session_id]
        )
        print(json.dumps(session, indent=2))

    def list_assistants(
            self,
            name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all assistants or filter by name.
        """
        url = f'{self.base_url}/chats'
        params = {'name': name} if name else {}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def list_sessions(
            self,
            assistant_id: str,
            session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all sessions for a given assistant or filter by session ID.
        """
        url = f'{self.base_url}/chats/{assistant_id}/sessions'
        params = {'id': session_id} if session_id else {}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def create_session(
            self,
            assistant_id: str,
            session_name: str,
            session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new chat session for a given assistant.
        """
        url = f'{self.base_url}/chats/{assistant_id}/sessions'
        body = {'name': session_name}
        params = {'id': session_id} if session_id else {}
        response = requests.post(
            url,
            headers=self.headers,
            params=params,
            json=body
        )
        response.raise_for_status()
        return response.json()

    def delete_session(
            self,
            assistant_id: str,
            session_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Delete a chat session for a given assistant.
        """
        url = f'{self.base_url}/chats/{assistant_id}/sessions/'
        body = {'ids': session_ids}
        response = requests.delete(
            url,
            headers=self.headers,
            json=body
        )
        response.raise_for_status()
        return response.json()

    def ask_question(
        self,
        assistant_id: str,
        question: str,
        stream: bool = False,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a completion from a given assistant.
        """
        url = f'{self.base_url}/chats/{assistant_id}/completions'
        body = {'question': question, 'stream': stream}
        if user_id:
            body['user_id'] = user_id
        elif session_id:
            body['session_id'] = session_id
        response = requests.post(
            url,
            headers=self.headers,
            json=body
        )
        response.raise_for_status()
        return response.json()


if __name__ == '__main__':
    ragflow_service = RAGFlowService()
    ragflow_service.main()

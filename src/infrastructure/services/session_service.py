"""Service for managing problem-solving sessions and methodology flows."""
import uuid
import re
from typing import Any, Dict, List, Optional, Sequence

from src.core.methodology import MethodologyEngine, MethodologyType
from src.infrastructure.repositories.postgres_repository import PostgreSQLRepository
from src.infrastructure.services.llm_service import LLMService
from src.infrastructure.services.rag_engine import RAGEngine


class SessionService:
    def __init__(
        self, 
        repository: PostgreSQLRepository, 
        methodology_engine: MethodologyEngine,
        llm_service: LLMService,
        rag_engine: Optional[RAGEngine] = None
    ):
        self.repository = repository
        self.engine = methodology_engine
        self.llm = llm_service
        self.rag = rag_engine

    def detect_circular_logic(self, current_answer: str, previous_answers: List[str]) -> bool:
        """Requirement 11.3, 11.4: Detect if the answer repeats previous ones (70%+ word overlap)."""
        def get_words(text: str) -> set:
            words = set(re.findall(r'\w+', text.lower()))
            if not words and text.strip():
                return set(text.strip().lower())
            return words

        current_words = get_words(current_answer)
        if not current_words:
            return False

        for prev in previous_answers:
            prev_words = get_words(prev)
            if not prev_words:
                continue
            
            overlap = current_words.intersection(prev_words)
            ratio = len(overlap) / max(len(current_words), len(prev_words))
            if ratio >= 0.7:
                return True
        return False

    async def start_session(self, user_id: uuid.UUID, problem_description: str, methodology: str) -> Dict[str, Any]:
        """Start a new problem-solving session."""
        m_type = MethodologyType(methodology)
        
        db_session = await self.repository.create_session(
            user_id=user_id,
            problem_description=problem_description,
            methodology=methodology
        )
        
        template = self.engine.get_template(m_type)
        first_step = self.engine.get_step(m_type, 0)
        
        # Requirement 1.6: RAG search for similar records
        similar_records = []
        message = None
        if self.rag:
            try:
                similar_records = await self.rag.search_similar(problem_description, limit=5)
            except Exception as e:
                # Requirement 23.2: Degraded mode warning
                message = "Bilgi tabanına şu an erişilemiyor, oturum benzer kayıtlar olmadan devam edecek."
                print(f"RAG Error during session start: {str(e)}")
        
        return {
            "session_id": str(db_session.id),
            "methodology": methodology,
            "current_step": 0,
            "next_prompt": first_step.question if first_step else None,
            "total_steps": len(template.steps) if m_type != MethodologyType.FIVE_WHY else 7,
            "similar_problems": similar_records,
            "message": message
        }

    async def submit_step_response(self, session_id: uuid.UUID, response: str) -> Dict[str, Any]:
        """Submit response for the current step and get the next prompt."""
        db_session = await self.repository.get_session(session_id)
        if not db_session:
            raise ValueError("Session not found")
        
        m_type = MethodologyType(db_session.methodology)
        current_responses = db_session.step_responses or {}
        
        # 5 Why Dynamic Logic
        if m_type == MethodologyType.FIVE_WHY:
            prev_answers = list(current_responses.values())
            if self.detect_circular_logic(response, prev_answers):
                return {
                    "session_id": str(session_id),
                    "error": "Döngüsel mantık tespit edildi.",
                    "status": "active",
                    "current_step": db_session.current_step_index,
                    "next_prompt": "Neden? (Lütfen önceki yanıtlardan farklı bir açıklama yapın)"
                }

            current_responses[str(db_session.current_step_index)] = response
            next_step_index = db_session.current_step_index + 1
            
            if next_step_index >= 7:
                why_chain = {
                    "questions": [self.engine.get_step(m_type, i).question if i < 5 else "Neden?" for i in range(7)],
                    "answers": [current_responses.get(str(i)) for i in range(7)],
                    "root_cause": response
                }
                await self.repository.update_session(session_id, step_responses=why_chain, status="completed")
                return {
                    "session_id": str(session_id),
                    "status": "completed",
                    "message": "5 Why analizi tamamlandı."
                }
            
            prev_responses_list = [current_responses.get(str(i)) for i in range(next_step_index)]
            next_q = await self.llm.generate_next_why(db_session.problem_description, prev_responses_list)
            await self.repository.update_session(session_id, step_responses=current_responses, current_step_index=next_step_index)
            
            return {
                "session_id": str(session_id),
                "current_step": next_step_index,
                "next_prompt": next_q,
                "can_proceed": next_step_index >= 3,
                "status": "active"
            }

        # Ishikawa Logic (Requirement 10.4: Category Reassignment)
        suggestion = None
        if m_type == MethodologyType.ISHIKAWA:
            current_step = self.engine.get_step(m_type, db_session.current_step_index)
            if current_step:
                suggestion = await self.llm.suggest_category_reassignment(response, current_step.name)

        # Normal Methodology Flow
        current_responses[str(db_session.current_step_index)] = response
        
        is_vague = await self.llm.is_response_vague(response)
        if is_vague and db_session.followup_count < 3:
            new_count = db_session.followup_count + 1
            followup_q = await self.llm.generate_clarification(response)
            await self.repository.update_session(session_id, followup_count=new_count)
            return {
                "session_id": str(session_id),
                "current_step": db_session.current_step_index,
                "next_prompt": followup_q,
                "followup_count": new_count,
                "can_proceed": new_count >= 3,
                "status": "active"
            }

        next_step_index = db_session.current_step_index + 1
        is_complete = self.engine.is_complete(m_type, next_step_index)
        
        update_data = {
            "step_responses": current_responses,
            "current_step_index": next_step_index,
            "followup_count": 0
        }
        
        if is_complete:
            # 8D check
            if m_type == MethodologyType.EIGHT_D:
                missing = [f"D{i+1}" for i in range(8) if len(current_responses.get(str(i), "")) < 10]
                if missing:
                    return {
                        "session_id": str(session_id),
                        "error": f"Eksik veya yetersiz adımlar: {', '.join(missing)}",
                        "status": "active",
                        "current_step": db_session.current_step_index
                    }
                eight_d_report = {
                    "d1_team": current_responses.get("0"),
                    "d2_problem": current_responses.get("1"),
                    "d3_containment": current_responses.get("2"),
                    "d4_root_cause": current_responses.get("3"),
                    "d5_corrective": current_responses.get("4"),
                    "d6_implementation": current_responses.get("5"),
                    "d7_prevention": current_responses.get("6"),
                    "d8_closure": current_responses.get("7")
                }
                update_data["step_responses"] = eight_d_report

            # Ishikawa check
            elif m_type == MethodologyType.ISHIKAWA:
                categories = ["man", "machine", "method", "material", "measurement", "environment"]
                ishikawa_data = {cat: [current_responses.get(str(i))] for i, cat in enumerate(categories)}
                update_data["step_responses"] = ishikawa_data

            update_data["status"] = "completed"
        
        await self.repository.update_session(session_id, **update_data)
        
        if is_complete:
            return {
                "session_id": str(session_id),
                "status": "completed",
                "message": "Metodoloji başarıyla tamamlandı."
            }
        
        next_step = self.engine.get_step(m_type, next_step_index)
        response_data = {
            "session_id": str(session_id),
            "current_step": next_step_index,
            "next_prompt": next_step.question if next_step else None,
            "status": "active"
        }
        if suggestion:
            response_data["category_suggestion"] = suggestion
            
        return response_data

    async def step_back(self, session_id: uuid.UUID) -> Dict[str, Any]:
        """Requirement 2.5: Step back logic."""
        db_session = await self.repository.get_session(session_id)
        if not db_session:
            raise ValueError("Session not found")
        
        if db_session.current_step_index == 0:
            raise ValueError("Cannot step back from the first step")
        
        prev_step_index = db_session.current_step_index - 1
        await self.repository.update_session(session_id, current_step_index=prev_step_index)
        
        m_type = MethodologyType(db_session.methodology)
        step = self.engine.get_step(m_type, prev_step_index)
        
        return {
            "session_id": str(session_id),
            "current_step": prev_step_index,
            "next_prompt": step.question if step else "Soru bulunamadı.",
            "previous_response": (db_session.step_responses or {}).get(str(prev_step_index))
        }

    async def finalize_session(self, session_id: uuid.UUID) -> Dict[str, Any]:
        """Requirement 3: Finalize session, generate lessons learned, and store record."""
        db_session = await self.repository.get_session(session_id)
        if not db_session or db_session.status != "completed":
            raise ValueError("Session is not completed or not found")
        
        step_responses = db_session.step_responses or {}
        
        # Determine root cause based on methodology
        m_type = MethodologyType(db_session.methodology)
        root_cause = "Not determined"
        if m_type == MethodologyType.FIVE_WHY:
            root_cause = step_responses.get("root_cause", "")
        elif m_type == MethodologyType.EIGHT_D:
            root_cause = step_responses.get("d4_root_cause", "")
        else:
            # Fallback for PDCA / Ishikawa
            root_cause = str(step_responses)

        # Generate Lessons Learned
        lessons_learned = await self.llm.generate_lessons_learned(
            problem_description=db_session.problem_description,
            root_cause=root_cause,
            methodology=db_session.methodology
        )
        
        # Save to DB
        record = await self.repository.create_problem_record(
            title=f"Problem: {db_session.problem_description[:30]}...",
            problem_description=db_session.problem_description,
            methodology=db_session.methodology,
            step_responses=step_responses,
            root_cause=root_cause,
            corrective_actions=["Pending"],
            lessons_learned=lessons_learned
        )
        
        # Embed and store in Qdrant if available
        if self.rag:
            try:
                # Prepare content for embedding
                content = f"{record.title} {record.problem_description} {record.root_cause} {record.lessons_learned}"
                metadata = {
                    "title": record.title,
                    "methodology": record.methodology,
                    "root_cause": record.root_cause,
                    "resolution_status": "finalized"
                }
                await self.rag.upsert_record(record.id, content, metadata)
                await self.repository.update_problem_record_status(record.id, "embedded")
            except Exception as e:
                print(f"Failed to embed record {record.id}: {str(e)}")
                await self.repository.update_problem_record_status(record.id, "embedding_failed")
                
        return {
            "record_id": str(record.id),
            "title": record.title,
            "lessons_learned": lessons_learned,
            "status": "finalized"
        }

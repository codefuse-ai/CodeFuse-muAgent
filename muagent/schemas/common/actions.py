from pydantic import BaseModel
from enum import Enum



class ActionStatus(Enum):
    DEFAUILT = "default"

    FINISHED = "finished"
    STOPPED = "stopped"
    CONTINUED = "continued"

    TOOL_USING = "tool_using"
    CODING = "coding"
    CODE_EXECUTING = "code_executing"
    CODING2FILE = "coding2file"

    PLANNING = "planning"
    UNCHANGED = "unchanged"
    ADJUSTED = "adjusted"
    CODE_RETRIEVAL = "code_retrieval"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value.lower() == other.lower()
        return super().__eq__(other)
    

class Action(BaseModel):
    action_name: str
    description: str

class FinishedAction(Action):
    action_name: str = ActionStatus.FINISHED
    description: str = "provide the final answer to the original query to break the chain answer"

class StoppedAction(Action):
    action_name: str = ActionStatus.STOPPED
    description: str = "provide the final answer to the original query to break the agent answer"

class ContinuedAction(Action):
    action_name: str = ActionStatus.CONTINUED
    description: str = "cant't provide the final answer to the original query"

class ToolUsingAction(Action):
    action_name: str = ActionStatus.TOOL_USING
    description: str = "proceed with using the specified tool."

class CodingdAction(Action):
    action_name: str = ActionStatus.CODING
    description: str = "provide the answer by writing code"

class Coding2FileAction(Action):
    action_name: str = ActionStatus.CODING2FILE
    description: str = "provide the answer by writing code and filename"

class CodeExecutingAction(Action):
    action_name: str = ActionStatus.CODE_EXECUTING
    description: str = "provide the answer by writing executable code"

class PlanningAction(Action):
    action_name: str = ActionStatus.PLANNING
    description: str = "provide a sequence of tasks"

class UnchangedAction(Action):
    action_name: str = ActionStatus.UNCHANGED
    description: str = "this PLAN has no problem, just set PLAN_STEP to CURRENT_STEP+1."

class AdjustedAction(Action):
    action_name: str = ActionStatus.ADJUSTED
    description: str = "the PLAN is to provide an optimized version of the original plan."

# extended action exmaple
class CodeRetrievalAction(Action):
    action_name: str = ActionStatus.CODE_RETRIEVAL
    description: str = "execute the code retrieval to acquire more code information"

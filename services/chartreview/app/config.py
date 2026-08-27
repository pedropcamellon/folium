from folium.core.chart_review import CHARTREVIEW_TASK_QUEUE, CHARTREVIEW_WORKFLOW_NAME
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    temporal_address: str = "localhost:7233"
    temporal_namespace: str = "default"
    chartreview_task_queue: str = CHARTREVIEW_TASK_QUEUE
    chartreview_workflow_name: str = CHARTREVIEW_WORKFLOW_NAME
    ai_service_base_url: str
    ai_provider_name: str = "local"
    ai_model_name: str = "mediphi-clinical"
    request_timeout_seconds: float = 120.0
    activity_start_to_close_timeout_seconds: int = 120
    activity_max_attempts: int = 2

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

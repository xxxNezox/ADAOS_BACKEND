import httpx
from fastapi import HTTPException, status
from typing import Dict, Any, Optional

class ServerErrorHandler:
    @staticmethod
    async def handle_http_error(
        error: httpx.HTTPStatusError,
        default_detail: str = "Сервис не смог обработать ваш запрос",
        error_key: str = "error"
    ) -> HTTPException:
        """
        Обрабатывает ошибки HTTP от внешних сервисов
        
        Args:
            error: Исключение httpx.HTTPStatusError
            default_detail: Стандартное сообщение об ошибке
            error_key: Ключ в JSON ответе, содержащий сообщение об ошибке
            
        Returns:
            HTTPException с соответствующим статус-кодом и сообщением
        """
        detail = default_detail
        try:
            error_data = error.response.json()
            if error_key in error_data:
                detail = error_data[error_key]
        except Exception:
            pass
        
        return HTTPException(
            status_code=error.response.status_code,
            detail=detail
        )

    @staticmethod
    async def handle_request_error() -> HTTPException:
        """
        Обрабатывает ошибки соединения с внешними сервисами
        
        Returns:
            HTTPException с кодом 503 (Сервис недоступен)
        """
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис недоступен. Пожалуйста, попробуйте позже."
        )

    @staticmethod
    async def validate_service_response(
        response_data: Any,
        required_fields: list,
        service_name: str = "сервиса"
    ) -> None:
        """
        Проверяет корректность ответа от внешнего сервиса
        
        Args:
            response_data: Данные ответа от сервиса
            required_fields: Список обязательных полей
            service_name: Название сервиса для сообщения об ошибке
            
        Raises:
            HTTPException: Если ответ невалидный
        """
        if (not response_data or 
            not isinstance(response_data, dict) or 
            not all(field in response_data for field in required_fields)):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Неверный или неполный формат ответа от {service_name}."
            )

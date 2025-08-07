from logging.config import dictConfig
import logging
import json


class CustomJsonFormatter(logging.Formatter):
    def format(self, record):
        # Create the log record dict with renamed fields
        log_record = {
            'timestamp': self.formatTime(record, '%Y-%m-%dT%H:%M:%SZ'),
            'level': record.levelname,
            'correlation_id': getattr(record, 'correlation_id', '-'),
            'logger': f"{record.name}:{record.lineno}",
            'message': record.getMessage()
        }
        for attr in [
            'duration', 'method', 'path', 'status_code',
            'request_body', 'response_body', 'query_params',
            'client', 'user_agent', 'exception', 'traceback'
        ]:
            if hasattr(record, attr):
                log_record[attr] = getattr(record, attr)
        
        return json.dumps(log_record)
    

def configure_logging() -> None:
    dictConfig(
        {
            'version': 1,
            'disable_existing_loggers': False,
            'filters': {
                'correlation_id': {
                    '()': 'asgi_correlation_id.CorrelationIdFilter',
                    'uuid_length': 32,
                    'default_value': '-',
                },
            },
            'formatters': {
                'json': {
                    '()': CustomJsonFormatter,
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'filters': ['correlation_id'],
                    'formatter': 'json',
                },
                'file': {
                    'class': 'logging.FileHandler',
                    'filename': "app.log",
                    'filters': ['correlation_id'],
                    'formatter': 'json',
                },
            },
            'loggers': {
                'app': {'handlers': ['console', 'file'], 'level': 'INFO'},
                'sqlalchemy': {'handlers': ['console', 'file'], 'level': 'ERROR'},
                'httpx': {'handlers': ['console', 'file'], 'level': 'INFO'},
                'asgi_correlation_id': {'handlers': ['console', 'file'], 'level': 'WARNING'},
                'uvicorn': {'handlers': ['console', 'file'], 'level': 'INFO'},
            },
        }
    )
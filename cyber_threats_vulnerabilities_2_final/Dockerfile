FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app
COPY derexi-policy-pilot/backend/pulse/__init__.py derexi-policy-pilot/backend/pulse/service.py derexi-policy-pilot/backend/pulse/sources.py /app/pulse/
COPY cyber_threats_vulnerabilities_2_final/dashboard.py /app/dashboard.py
USER 65532:65532
EXPOSE 8080
ENTRYPOINT ["python", "/app/dashboard.py", "--bind", "0.0.0.0"]


@echo off
REM Customer cleanup script for Windows
REM Usage: clean_inactive_customers.bat

set TIMESTAMP=%date% %time%
set LOG_FILE=%TEMP%\customer_cleanup_log.txt

REM Navigate to project root
cd /d "%~dp0..\.."

REM Execute Django shell command
set "DELETED_COUNT="
for /f %%i in ('python manage.py shell -c "from django.utils import timezone; from datetime import timedelta; from customers.models import Customer; from django.db.models import Count; one_year_ago = timezone.now() - timedelta(days=365); inactive_customers = Customer.objects.annotate(order_count=Count('orders')).filter(order_count=0); count = inactive_customers.count(); inactive_customers.delete(); print(count)"') do (
    set DELETED_COUNT=%%i
)

REM Log the result
echo [%TIMESTAMP%] Deleted %DELETED_COUNT% inactive customers >> "%LOG_FILE%"
echo Customer cleanup completed. %DELETED_COUNT% customers deleted.